# app/services/rag_service.py

import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from app.utils.pinecone_client import get_pinecone_index
from app.core.config import EMBED_MODEL, LLM_MODEL, GEMINI_LLM_MODEL, GEMINI_EMBED_MODEL
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
import openai   

def batch_chunks(chunks, max_batch_bytes=2*1024*1024):  
    batch = []
    total_bytes = 0
    max_chunks_per_batch = 100  
    
    for chunk in chunks:
        text_bytes = len(chunk["text"].encode("utf-8"))
        metadata_bytes = len(str(chunk["metadata"]).encode("utf-8"))
        chunk_bytes = text_bytes + metadata_bytes + 500  
        
        if chunk_bytes > max_batch_bytes:
            continue
        
        if (total_bytes + chunk_bytes > max_batch_bytes and batch) or len(batch) >= max_chunks_per_batch:
            yield batch
            batch = []
            total_bytes = 0
            
        batch.append(chunk)
        total_bytes += chunk_bytes
        
    if batch:
        yield batch

def upsert_chunks_to_pinecone(chunks, namespace, openai_api_key):
    embedder = OpenAIEmbeddings(openai_api_key=openai_api_key, model=EMBED_MODEL)
    pinecone_index = get_pinecone_index()
    
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedder,
        namespace=namespace
    )
    
    total_added = 0
    batch_num = 0
    total_batches = list(batch_chunks(chunks))
    
    for batch in total_batches:
        batch_num += 1
        texts = [c['text'] for c in batch]
        metadatas = [c['metadata'] for c in batch]
        batch_bytes = sum(len(t.encode('utf-8')) + len(str(m).encode('utf-8')) + 500 for t, m in zip(texts, metadatas))
        
        try:
            vectorstore.add_texts(texts, metadatas=metadatas)
            total_added += len(texts)
        except Exception as e:
            continue

def get_retriever(namespace, openai_api_key):
    embedder = OpenAIEmbeddings(openai_api_key=openai_api_key, model=EMBED_MODEL)
    pinecone_index = get_pinecone_index()
    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embedder,
        namespace=namespace,
    )
    return vectorstore.as_retriever()

def chat_with_rag(query, namespace, openai_api_key):
    retriever = get_retriever(namespace, openai_api_key)
    llm = ChatOpenAI(openai_api_key=openai_api_key, model=LLM_MODEL, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )
    result = qa_chain(query)
    return result['result']

def validate_key(provider: str, api_key: str) -> bool:
    try:
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            _ = client.models.list()
            return True
        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            _ = [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            return True
        else:
            return False
    except Exception:
        return False


def validate_openai_key(openai_api_key):
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        models = client.models.list()
        return True
    except Exception as e:
        return False
    

def delete_pinecone_namespace(namespace):
    try:
        index = get_pinecone_index()
        index.delete(delete_all=True, namespace=namespace)
    except Exception as e:
        print(f"Error deleting namespace {namespace} from Pinecone: {e}")

def get_embedder(provider: str, api_key: str):
    if provider == "openai":
        return OpenAIEmbeddings(openai_api_key=api_key, model=EMBED_MODEL)   
    elif provider == "gemini":
        return GoogleGenerativeAIEmbeddings(google_api_key=api_key, model=GEMINI_EMBED_MODEL)
    else:
        raise ValueError("Unknown provider")

def get_llm(provider: str, api_key: str):
    if provider == "openai":
        return ChatOpenAI(openai_api_key=api_key, model=LLM_MODEL, temperature=0)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(api_key=api_key, model=GEMINI_LLM_MODEL, temperature=0)
    else:
        raise ValueError("Unknown provider")
    

def embed_dim_for_provider(provider: str) -> int:
    return 1536 if provider=="openai" else 768  

def upsert_chunks_to_pinecone(chunks, namespace, provider, api_key):
    embedder = get_embedder(provider, api_key)
    index = get_pinecone_index(provider, embed_dim_for_provider(provider))
    vectorstore = PineconeVectorStore(index=index, embedding=embedder, namespace=namespace)
    for batch in batch_chunks(chunks):
        texts = [c['text'] for c in batch]
        metadatas = [c['metadata'] for c in batch]
        vectorstore.add_texts(texts, metadatas=metadatas)

def get_retriever(namespace, provider, api_key):
    embedder = get_embedder(provider, api_key)
    index = get_pinecone_index(provider, embed_dim_for_provider(provider))
    vs = PineconeVectorStore(index=index, embedding=embedder, namespace=namespace)
    return vs.as_retriever()

def chat_with_rag(query, namespace, provider, api_key):
    retriever = get_retriever(namespace, provider, api_key)
    llm = get_llm(provider, api_key)
    
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type="stuff")
    return qa(query)['result']

def delete_pinecone_namespace(namespace, provider):
    try:
        index = get_pinecone_index(provider, embed_dim_for_provider(provider))
        index.delete(delete_all=True, namespace=namespace)
    except Exception as e:
        print(f"Error deleting namespace {namespace} ({provider}): {e}")
