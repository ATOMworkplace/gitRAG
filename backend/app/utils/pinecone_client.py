# app/utils/pinecone_client.py
from pinecone import Pinecone, ServerlessSpec
from app.core.config import PINECONE_API_KEY, PINECONE_INDEX

def get_pinecone_index(provider: str, dim: int, metric="cosine"):
    base = PINECONE_INDEX  # e.g. "gitrag-code"
    name = f"{base}-{provider}-{dim}"
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if not pc.has_index(name):
        pc.create_index(
            name=name,
            dimension=dim,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            metric=metric
        )
    return pc.Index(name)
