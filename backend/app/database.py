from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings  # <-- Importa as configurações globais
import re

class DocuMindbox:
    def __init__(self):
        # 1. Usamos as configurações do config.py dinamicamente
        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBEDDING_MODEL,  # Usa "nomic-embed-text"
            base_url=settings.OLLAMA_BASE_URL       # Usa "http://ollama:11434" dentro do Docker
        )
        
        # 2. Conectamos ao banco usando o caminho centralizado de dados
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_DATA_PATH, # Mantém salvo no volume correto
        )

    def clean_text(self, text: str) -> str:
        # Identifica se o texto está "espalhado" e junta
        cleaned = re.sub(r'(?<=[a-zA-Z])\s(?=[a-zA-Z]\s)', '', text)
        # Remove espaços múltiplos
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    def add_texts(self, texts: list[str]):
        # 1. Limpa espaços e remove strings vazias
        texts = [self.clean_text(t) for t in texts if t and self.clean_text(t)]
        
        if not texts:
            print("AVISO: Nenhum texto válido para processar.")
            return "Erro: O arquivo não contém texto extraível."
        
        # 2. Dividir o texto em pedaços (Chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text("\n".join(texts))
        
        # 3. Criar objetos de Documento do LangChain
        documents = [Document(page_content=t) for t in chunks if t.strip()]
        
        if not documents:
            return "Erro: Após o processamento, não restou texto útil."
        
        # 4. Adicionar ao banco (Aqui o ChromaDB chama o Ollama usando o Nomic)
        self.vector_store.add_documents(documents)
        return f"Sucesso: {len(chunks)} pedaços de texto adicionados."

    def search(self, query: str):
        # Busca os 3 pedaços de texto mais parecidos com a pergunta
        return self.vector_store.similarity_search(query, k=3)

# Instância global
db_manager = DocuMindbox()