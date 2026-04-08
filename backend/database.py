from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re

class DocuMindbox:
    def __init__(self):
        # Usamos o Ollama para gerar os "Embeddings" (transformar texto em vetores)
        self.embeddings = OllamaEmbeddings(model="llama3", base_url="http://localhost:11434")
        
        # Conectamos ao container do ChromaDB que configuramos no Docker
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db", # Onde ele salvará os dados localmente
        )

    def clean_text(self, text: str) -> str:
        # Tenta identificar se o texto está "espalhado" (ex: K e r l e y) e junta
        # Esta é uma regex simples, pode precisar de ajuste dependendo do PDF
        cleaned = re.sub(r'(?<=[a-zA-Z])\s(?=[a-zA-Z]\s)', '', text)
        # Remove espaços múltiplos
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    def add_texts(self, texts: list[str]):
        # 1. Limpa espaços e remove strings vazias da lista original
        texts = [self.clean_text(t) for t in texts if t and self.clean_text(t)]
        
        if not texts:
            print("AVISO: Nenhum texto válido para processar.")
            return "Erro: O arquivo não contém texto extraível."
        
        # 2. Dividir o texto em pedaços para a IA não se perder (Chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text("\n".join(texts))
        
        # 3. Criar objetos de Documento do LangChain
        documents = [Document(page_content=t) for t in chunks if t.strip()]
        
        if not documents:
            return "Erro: Após o processamento, não restou texto útil."
        
        # 4. Adicionar ao banco (Aqui o ChromaDB chama o Ollama para converter em vetores)
        self.vector_store.add_documents(documents)
        return f"Sucesso: {len(chunks)} pedaços de texto adicionados."

    def search(self, query: str):
        # Busca os 3 pedaços de texto mais parecidos com a pergunta
        return self.vector_store.similarity_search(query, k=3)

# Instância global
db_manager = DocuMindbox()