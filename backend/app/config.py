from functools import lru_cache

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _is_pytest() -> bool:
    """Check if code is running under pytest."""
    import sys

    return "pytest" in sys.modules


class Settings(BaseSettings):
    """
    Configurações globais da aplicação.
    """

    # Banco de dados
    DATABASE_URL: str = "sqlite:///../data/sqlite/vocabulary.db"
    CHROMA_DATA_PATH: str = "../data/chroma"

    # Modelo Ollama
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna uma instância de `Settings` com cache para otimizar o acesso às configurações.

    Esta função utiliza `functools.lru_cache` para armazenar em cache a instância de `Settings`,
    garantindo que as configurações sejam carregadas apenas uma vez durante a execução da aplicação.
    """
    return Settings()


# --- Inicialização dos Motores do Banco (Mantendo isolado e limpo) ---
settings = get_settings()


# Garante a crição do diretório para os dados do Chroma, se não existir
os.makedirs("../data/sqlite", exist_ok=True)
os.makedirs(settings.CHROMA_DATA_PATH, exist_ok=True)

# Configuração do SQLAlchemy para o banco de dados
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Injeção de dependência para as rotas do FastAPI
def get_db():
    """
    Fornece uma sessão de banco de dados para as rotas do FastAPI.

    Esta função é usada como dependência nas rotas do FastAPI para garantir que cada solicitação
    tenha acesso a uma sessão de banco de dados adequada, que é fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()