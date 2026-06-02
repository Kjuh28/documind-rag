# 1. Usamos a imagem slim (estabilidade total para LangChain/ChromaDB)
FROM python:3.11-slim

# 2. Copia o binário oficial e ultra-rápido do UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Define variáveis de ambiente
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 4. Copia apenas os arquivos de travas para criar a camada de cache pesada
COPY pyproject.toml uv.lock ./

# 5. Instala as dependências de forma congelada (evita surpresas em produção)
# O --no-install-project garante que ele instale apenas as bibliotecas por enquanto
RUN uv sync --frozen --no-cache --no-install-project

# 6. Agora sim, copia o resto do código fonte do projeto
COPY . .

# 7. Expõe a porta do FastAPI
EXPOSE 8000

# 8. Executa o script que configuramos no seu toml (uv run start)
CMD ["uv", "run", "start"]