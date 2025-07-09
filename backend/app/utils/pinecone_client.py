#app/utils/pinecone_client.py
from pinecone import Pinecone, ServerlessSpec
from app.core.config import PINECONE_API_KEY, PINECONE_INDEX

def get_pinecone_index():
    print(f"[DEBUG] Connecting to Pinecone index: {PINECONE_INDEX}")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if not pc.has_index(PINECONE_INDEX):
        print(f"[INFO] Creating Pinecone index {PINECONE_INDEX}")
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=1536,  # set this to your embedding model's dimension
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ),
            metric="cosine"
        )
    index = pc.Index(PINECONE_INDEX)
    print(f"[DEBUG] Pinecone index connected: {index}")
    return index
