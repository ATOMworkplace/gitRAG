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
LLM_MODEL = config('LLM_MODEL', cast=str, default="llama3")
