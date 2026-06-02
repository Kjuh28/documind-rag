from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# 1. O que o Frontend envia ao capturar uma palavra nova do livro/PDF
class ConceptCreate(BaseModel):
    term: str
    context: str


# 2. O contrato estrito de como o Ollama DEVE devolver a resposta tratada
class OllamaResponse(BaseModel):
    translation: str 
    synonyms: str
    context_explanation: str


# 3. O que a API devolve limpo para o Frontend exibir na tela
class ConceptResponse(BaseModel):
    id: int
    term: str
    context: str
    translation: Optional[str] = None
    synonyms: Optional[str] = None
    review_stage: int
    next_review_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)