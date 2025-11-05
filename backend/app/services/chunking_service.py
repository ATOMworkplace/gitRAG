# app/services/chunking_service.py
import os
import hashlib
from typing import Iterable, Dict, List, Generator
from app.core.config import (
    CHUNK_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    MAX_CHUNKS_PER_FILE,
    REPO_WIDE_CHUNK_BUDGET,
)

EXCLUDE_FILENAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
EXCLUDE_EXTENSIONS = {}

def _should_skip_file(path: str) -> bool:
    base = os.path.basename(path)
    if base in EXCLUDE_FILENAMES:
        return True
    p = path.lower()
    return any(p.endswith(ext) for ext in EXCLUDE_EXTENSIONS)

def _try_get_tiktoken():
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None

_encoding = _try_get_tiktoken()

def _encode(text: str) -> List[int]:
    if _encoding:
        return _encoding.encode(text)
    return text.split()

def _decode(tokens: List[int]) -> str:
    if _encoding:
        return _encoding.decode(tokens)
    return " ".join(tokens)

def _stable_chunk_id(file_path: str, start_idx: int, chunk_text: str) -> str:
    h = hashlib.sha256()
    h.update(file_path.encode("utf-8"))
    h.update(str(start_idx).encode("utf-8"))
    h.update(chunk_text.encode("utf-8"))
    return h.hexdigest()

def _token_stream_chunks(text: str, target: int, overlap: int) -> Generator[str, None, None]:
    ids = _encode(text)
    n = len(ids)
    if n == 0:
        return
    start = 0
    step = max(1, target - overlap)
    while start < n:
        end = min(start + target, n)
        piece = ids[start:end]
        yield _decode(piece)
        if end == n:
            break
        start += step

def chunk_text_to_chunks(file_path: str, text: str) -> Generator[Dict, None, None]:
    if not text or not text.strip():
        return
    produced = 0
    start_token_idx = 0
    step = max(1, CHUNK_TOKENS - CHUNK_OVERLAP_TOKENS)
    for piece in _token_stream_chunks(text, CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS):
        if not piece.strip():
            continue
        cid = _stable_chunk_id(file_path, start_token_idx, piece)
        yield {
            "text": piece,
            "metadata": {
                "file": file_path,
                "chunk_id": cid
            }
        }
        produced += 1
        if produced >= MAX_CHUNKS_PER_FILE:
            break
        start_token_idx += step

def chunk_files_mem(files: Iterable[Dict]) -> List[Dict]:
    chunks: List[Dict] = []
    total_chunks = 0
    for f in files:
        fname = f["filename"]
        content = f["content"]
        if _should_skip_file(fname):
            continue
        if not content or not content.strip():
            continue
        produced = 0
        start_token_idx = 0
        step = max(1, CHUNK_TOKENS - CHUNK_OVERLAP_TOKENS)
        for piece in _token_stream_chunks(content, CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS):
            if not piece.strip():
                continue
            cid = _stable_chunk_id(fname, start_token_idx, piece)
            chunks.append({
                "text": piece,
                "metadata": {
                    "file": fname,
                    "chunk_id": cid
                }
            })
            produced += 1
            total_chunks += 1
            if produced >= MAX_CHUNKS_PER_FILE:
                break
            if total_chunks >= REPO_WIDE_CHUNK_BUDGET:
                break
            start_token_idx += step
        if total_chunks >= REPO_WIDE_CHUNK_BUDGET:
            break
    return chunks
