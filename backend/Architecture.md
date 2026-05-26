Guia de Arquitetura e Componentes — Documind-RAG
Este documento serve como um mapa técnico para entender a responsabilidade de cada arquivo e a engrenagem por trás do sistema de repetição espaçada e inteligência artificial local.

🏗️ Visão Geral da Stack Tecnológica
FastAPI: Framework backend assíncrono de alta performance responsável por expor as APIs e gerenciar as regras de negócio.

Ollama (Llama3): Provedor de LLM local que atua como o dicionário contextual inteligente (extração de conceitos em formato JSON puro).

ChromaDB: Banco de dados vetorial (Vector Store) encarregado de armazenar os embeddings dos conceitos para buscas semânticas por proximidade.

SQLite + SQLAlchemy: Banco de dados relacional e ORM responsáveis por gerenciar o ciclo de vida do aprendizado (cálculo de datas de revisão, estados do algoritmo de repetição espaçada e persistência estruturada).

🗂️ Responsabilidade dos Arquivos do Backend
1. backend/app/config.py — Central de Ambiente e Motores
O que faz: Gerencia as configurações globais, variáveis de ambiente e inicializa as conexões com os bancos de dados.

Pydantic Settings & .env: Mapeia e tipa as variáveis necessárias (como URLs de bancos e modelos da IA), usando fallbacks (valores padrão) caso não encontre o arquivo .env.

Otimização com @lru_cache: Implementa o padrão Singleton. O arquivo de configuração só é lido do disco rígido uma única vez; as leituras seguintes são feitas direto da memória RAM para garantir performance extrema.

Gerenciador de Ciclo de Vida (get_db): Uma função de injeção de dependência do FastAPI que abre uma nova sessão com o banco relacional a cada requisição e garante o fechamento automático (db.close()) assim que a resposta é enviada, evitando vazamentos de memória.

2. backend/app/models.py — Estrutura Relacional (SQLAlchemy)
O que faz: Define as tabelas do banco de dados relacional (SQLite), mapeando as colunas em classes Python.

Controle do Tempo: Guarda os metadados cruciais do aprendizado do usuário que o banco vetorial não gerencia bem: estagio_revisao (se você está na revisão de 1, 3 ou 7 dias) e proxima_revisao (a data/hora exata em que o sistema deve disparar a notificação).

Rastreabilidade: Armazena o termo original, a frase de contexto extraída do livro e as strings de tradução/sinônimos limpas geradas pela LLM.

3. backend/app/schemas.py — Contratos de Dados (Pydantic)
O que faz: Funciona como a "barreira de segurança" da API, validando rigorosamente os dados que entram do frontend e os dados que saem do backend.

Validação de Input: Garante que o frontend envie os campos obrigatórios e sanitizados (ex: termo e contexto).

Validação da IA (OllamaResponse): Força o Ollama a se comportar de forma previsível. O Pydantic valida se a string retornada pela LLM é realmente um JSON válido contendo as chaves exatas de tradução, sinônimos e explicação contextual antes de salvar no banco.

4. backend/app/brain.py — O Orquestrador da LLM
O que faz: Centraliza a inteligência do sistema, comunicando-se com a API local do Ollama.

Prompt Engineering de Extração: Injeta o termo e a frase do usuário dentro de um modelo de comando estruturado, ensinando a LLM a agir exclusivamente como um dicionário de tradução contextual.

Format Constraints: Força a LLM a responder em formato JSON estrito, coletando os dados brutos e repassando para o validador de esquemas.

5. backend/app/vector_store.py — Interface do Banco Vetorial
O que faz: Gerencia a comunicação direta com o container do ChromaDB.

Geração de Embeddings: Converte o significado do termo e do contexto em um vetor matemático de alta dimensão.

Busca Semântica: Permite que no futuro você pergunte ao chat por conceitos parecidos (ex: buscar "palavras sobre tristeza") e ele encontre termos guardados por proximidade matemática, mesmo que a palavra exata não seja igual.

6. backend/app/main.py — Porta de Entrada da Aplicação
O que faz: Inicializa a aplicação FastAPI e define as rotas/endpoints HTTP que o Frontend (Next.js) vai consumir.

Orquestrador de Fluxos: É quem recebe a requisição do front, aciona o brain.py para extrair os dados com a LLM, manda o vector_store.py salvar o vetor e registra as datas de revisão no banco relacional via models.py.

💾 Estrutura do Volume de Dados (/data)
data/sqlite/vocabulary.db: Arquivo físico contendo todos os seus registros de progresso e inteligência de tempo.

data/chroma/: Pasta contendo os índices vetoriais e arquivos de persistência binária dos embeddings gerados pelo ChromaDB.