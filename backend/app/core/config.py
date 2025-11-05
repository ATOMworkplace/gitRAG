from starlette.config import Config

config = Config('.env')



SESSION_SECRET_KEY = config('SESSION_SECRET_KEY', cast=str)
BASE_URL = config('BASE_URL', cast=str)
FRONT_END_URL = config('FRONT_END_URL', cast=str)
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', cast=str)
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', cast=str)
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID', cast=str)
GITHUB_CLIENT_SECRET = config('GITHUB_CLIENT_SECRET', cast=str)
DATABASE_URL = config('DATABASE_URL', cast=str)

# Pinecone
PINECONE_API_KEY = config('PINECONE_API_KEY', cast=str)
PINECONE_INDEX = config('PINECONE_INDEX', cast=str, default="gitrag-code")

# Ollama & Embedding models
OLLAMA_BASE_URL = config('OLLAMA_BASE_URL', cast=str, default="http://localhost:11434")
EMBED_MODEL = config('EMBED_MODEL', cast=str, default="nomic-embed-text")
LLM_MODEL = config('LLM_MODEL', cast=str, default="gpt-4o-mini")
GEMINI_EMBED_MODEL = config('GEMINI_EMBED_MODEL', cast=str, default="gemini-1.5-flash")
GEMINI_LLM_MODEL = config('GEMINI_LLM_MODEL', cast=str, default="models/text-embedding-004")

#Ingestion bounds
GITHUB_DENY_DIRS="node_modules,dist,build,.git,__pycache__,.venv,venv,target,.next,.vercel,out"
GITHUB_STREAMING_THRESHOLD_BYTES=256_000
GITHUB_MAX_BYTES_PER_FILE=2_000_000
GITHUB_REPO_INGEST_BYTE_BUDGET=250_000_000
GITHUB_MAX_FILES_PER_REPO=10_000
GITHUB_MAX_INGEST_SECONDS=600

#Token-aware chunking
CHUNK_TOKENS = 800
CHUNK_OVERLAP_TOKENS = 120
MAX_CHUNKS_PER_FILE = 2000
REPO_WIDE_CHUNK_BUDGET = 50000