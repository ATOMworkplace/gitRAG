# app/services/rag_service.py

import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from app.utils.pinecone_client import get_pinecone_index
from app.core.config import EMBED_MODEL, LLM_MODEL
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
import openai   

def batch_chunks(chunks, max_batch_bytes=2*1024*1024):  # Reduced to 2MB for safety
    """
    Batch chunks more conservatively to avoid Pinecone limits.
    The actual payload will be larger due to embeddings and serialization overhead.
    """
    batch = []
    total_bytes = 0
    max_chunks_per_batch = 100  # Additional safety limit
    
    for chunk in chunks:
        text_bytes = len(chunk["text"].encode("utf-8"))
        metadata_bytes = len(str(chunk["metadata"]).encode("utf-8"))
        # More conservative estimate including serialization overhead
        chunk_bytes = text_bytes + metadata_bytes + 500  # Increased padding
        
        if chunk_bytes > max_batch_bytes:
            print(f"[WARN] Skipping one too-large chunk ({chunk_bytes} bytes)")
            continue
            
        # Check if adding this chunk would exceed limits
        if (total_bytes + chunk_bytes > max_batch_bytes and batch) or len(batch) >= max_chunks_per_batch:
            yield batch
            batch = []
            total_bytes = 0
            
        batch.append(chunk)
        total_bytes += chunk_bytes
        
    if batch:
        yield batch

def upsert_chunks_to_pinecone(chunks, namespace, openai_api_key):
    print(f"[DEBUG] upsert_chunks_to_pinecone: {len(chunks)} chunks to {namespace}")
    embedder = OpenAIEmbeddings(openai_api_key=openai_api_key, model=EMBED_MODEL)
    pinecone_index = get_pinecone_index()
    print(f"[DEBUG] Pinecone index obtained: {pinecone_index}")
    
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedder,
        namespace=namespace
    )
    
    total_added = 0
    batch_num = 0
    total_batches = list(batch_chunks(chunks))
    
    print(f"[DEBUG] Will process {len(total_batches)} batches")
    
    for batch in total_batches:
        batch_num += 1
        texts = [c['text'] for c in batch]
        metadatas = [c['metadata'] for c in batch]
        batch_bytes = sum(len(t.encode('utf-8')) + len(str(m).encode('utf-8')) + 500 for t, m in zip(texts, metadatas))
        
        print(f"[DEBUG] Upserting batch {batch_num}/{len(total_batches)}: {len(texts)} texts, estimated {batch_bytes} bytes")
        
        try:
            vectorstore.add_texts(texts, metadatas=metadatas)
            total_added += len(texts)
            print(f"[DEBUG] Batch {batch_num} successful")
        except Exception as e:
            print(f"[ERROR] Failed to upsert batch {batch_num}: {e}")
            # Continue with other batches
            continue
    
    print(f"[DEBUG] Upsert to Pinecone complete: {total_added} chunks upserted")

def get_retriever(namespace, openai_api_key):
    print(f"[DEBUG] get_retriever for namespace={namespace}")
    embedder = OpenAIEmbeddings(openai_api_key=openai_api_key, model=EMBED_MODEL)
    pinecone_index = get_pinecone_index()
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedder,
        namespace=namespace,
    )
    return vectorstore.as_retriever()

def chat_with_rag(query, namespace, openai_api_key):
    print(f"[DEBUG] chat_with_rag: query={query}, namespace={namespace}")
    retriever = get_retriever(namespace, openai_api_key)
    llm = ChatOpenAI(openai_api_key=openai_api_key, model=LLM_MODEL, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )
    result = qa_chain(query)
    print(f"[DEBUG] LLM QA result: {result}")
    return result['result']

def validate_openai_key(openai_api_key):
    print(f"[DEBUG] Validating OpenAI API key")
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        models = client.models.list()
        print(f"[DEBUG] Models retrieved: {len(models.data)}")
        return True
    except Exception as e:
        print(f"[ERROR] OpenAI key validation failed: {e}")
        return False
    

def delete_pinecone_namespace(namespace):
    """
    Deletes all vectors for a namespace from Pinecone.
    """
    try:
        index = get_pinecone_index()
        index.delete(delete_all=True, namespace=namespace)
        print(f"[DEBUG] Deleted all vectors in namespace '{namespace}' from Pinecone.")
    except Exception as e:
        print(f"Error deleting namespace {namespace} from Pinecone: {e}")
