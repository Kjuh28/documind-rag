from fastapi import FastAPI
from brain import brain

from fastapi import UploadFile, File
import shutil
from loader import DocuLoader
from dotenv import load_dotenv
import os

from database import db_manager

load_dotenv() # Carrega as variáveis do .env para o ambiente

app = FastAPI(title="DocuMind RAG API")

@app.get("/")
def health_check():
    return {"status": "online", "project": "DocuMind"}

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