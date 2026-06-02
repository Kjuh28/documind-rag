from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
import shutil
import os
from dotenv import load_dotenv

from app.brain import brain
from app.vector_store import DocuLoader

from app.database import db_manager
from app.config import get_db, engine
from app.models import ConceptReview, Base
from app.schemas import ConceptCreate, ConceptResponse
from app.brain_spaced import extract_spaced_concept


load_dotenv() # Carrega as variáveis do .env para o ambiente

app = FastAPI(title="DocuMind RAG API & Spaced Repetition API")

# Cria as tabelas estruturadas no arquivo vocabulary.db se elas não existirem
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajuste para o endereço do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "project": "DocuMind", "timestamp": datetime.now(timezone.utc).isoformat()}

# ==============================================================================
# MÓDULO 1: RAG TRADICIONAL (Seus endpoints originais preservados)
# ==============================================================================

@app.post("/ask")
def ask_ai(question: str):
    response = brain.ask(question)
    return {"question": question, "answer": response}

# Rota para "ensinar" algo para a IA
@app.post("/train")
def train_ia(content: str):
    result = db_manager.add_texts([content])
    return {"message": result}

# Rota para ver o que o banco encontra (sem a IA responder ainda)
@app.get("/search")
def search_db(query: str):
    results = db_manager.search(query)
    return {"results": [doc.page_content for doc in results]}

# Rota para perguntar usando o contexto dos documentos
@app.post("/ask-doc")
def ask_with_context(question: str):
    # 1. Busca os textos relevantes no ChromaDB
    context_docs = db_manager.search(question)
    
    # 2. Une os textos em uma única string de contexto
    context_text = "\n".join([doc.page_content for doc in context_docs])
    
    # 3. Cria um "Prompt" reforçando que a IA deve usar o contexto
    prompt = f"""
    Você é o assistente do DocuMind. 
    Use APENAS o contexto abaixo para responder a pergunta do usuário.
    Se a resposta não estiver no contexto, diga que não sabe.
    
    CONTEXTO:
    {context_text}
    
    PERGUNTA:
    {question}
    """
    
    # 4. Envia para o cérebro (Ollama)
    response = brain.ask(prompt)
    
    return {
        "answer": response,
        "sources": [doc.page_content for doc in context_docs] # Bom para o usuário conferir
    }


# Rota para upload de arquivos
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 1. Salva o arquivo temporariamente no seu Windows
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Carrega o conteúdo do arquivo
        documents = DocuLoader.load_file(temp_path)
        
        # 3. Extrai o texto e envia para o nosso banco de dados
        texts = [doc.page_content for doc in documents]
        db_manager.add_texts(texts)
        
        return {"message": f"Arquivo {file.filename} processado e indexado com sucesso!"}
    
    finally:
        # 4. Remove o arquivo temporário para não entulhar seu PC
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ==============================================================================
# MÓDULO 2: SPACED REPETITION (Novos Endpoints Padronizados em Inglês)
# ==============================================================================

@app.post("/api/concepts", response_model=ConceptResponse)
async def create_concept(concept: ConceptCreate, db: Session = Depends(get_db)):
    
    try:
        # 1. Extrai o conceito usando a função de spaced repetition
        extracted_concept = extract_spaced_concept(term=concept.term, context=concept.context)
        
        # 2. Salva o conceito extraído no banco de dados
        db_concept = ConceptReview(
            term=concept.term,
            context=concept.context,
            translation=extracted_concept.translation,
            synonyms=extracted_concept.synonyms,
        )
        db.add(db_concept)
        db.commit()
        db.refresh(db_concept)
        

        # 3. Envia o conceito tratado para o ChromaDB através do seu db_manager original
        # Criamos uma string rica combinando o termo, tradução e a explicação de contexto da IA
        text_to_vector = (
            f"Term: {db_concept.term} | "
            f"Translation: {db_concept.translation} | "
            f"Explanation: {extracted_concept.context_explanation}"
        )
        db_manager.add_texts([text_to_vector])
        
        return db_concept

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and save the concept: {str(e)}"
        )
    

@app.get("/api/concepts/review", response_model=List[ConceptResponse])
def get_concepts_for_review(db: Session = Depends(get_db)):
    """
    Varre o banco relacional e retorna todas os cards cuja data de revisão expirou
    em relação ao momento atual (UTC).
    """
    now = datetime.now(timezone.utc)
    concepts_to_review = db.query(ConceptReview).filter(ConceptReview.next_review_date <= now).all()
    return concepts_to_review