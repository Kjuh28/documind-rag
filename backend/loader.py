from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os

class DocuLoader:
    @staticmethod
    def load_file(file_path: str):
        # Verifica a extensão do arquivo
        ext = os.path.splitext(file_path)[-1].lower()
        
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError("Formato de arquivo não suportado!")
            
        return loader.load() # Retorna uma lista de objetos Document