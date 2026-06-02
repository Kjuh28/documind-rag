import sys
import os

# Adiciona a raiz do projeto (backend) ao caminho de busca do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models import ConceptReview
from atlas_provider_sqlalchemy.ddl import print_ddl

# O Atlas vai gerar o DDL baseado no dialeto do SQLite
print_ddl("sqlite", [ConceptReview])