# app/services/chunking_service.py
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

MAX_FILE_SIZE = 2 * 1024 * 1024      # 2MB: skip files larger than this
MAX_CHUNK_SIZE = 3 * 1024 * 1024     # 3MB: skip any chunk larger than this
EXCLUDE_FILENAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
EXCLUDE_EXTENSIONS = {
    '.ico', '.png', '.jpg', '.jpeg', '.zip', '.tar', '.gz', '.rar', '.exe', '.dll'
}

def chunk_files_mem(files):
    # New: Use a *much larger* chunk size and overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2048,   # Use 2048 or 4096 for large context models
        chunk_overlap=256
    )
    chunks = []
    print(f"[DEBUG] chunk_files_mem called for {len(files)} files")
    for file in files:
        fname = file["filename"]
        content = file["content"]
        # Exclude files by name or extension
        if os.path.basename(fname) in EXCLUDE_FILENAMES or any(fname.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
            print(f"[WARN] Skipping {fname} (blocked by name or extension)")
            continue
        # Exclude files by size
        file_size = len(content.encode('utf-8'))
        if file_size > MAX_FILE_SIZE:
            print(f"[WARN] Skipping {fname} (file too large: {file_size} bytes > 2MB)")
            continue
        print(f"[DEBUG] Splitting file: {fname}")
        these_chunks = splitter.split_text(content)
        valid_chunks = 0
        for idx, chunk in enumerate(these_chunks):
            chunk_size = len(chunk.encode('utf-8'))
            if chunk_size > MAX_CHUNK_SIZE:
                print(f"[WARN] Skipping chunk {idx} of {fname}: chunk too large ({chunk_size} bytes > 3MB)")
                continue
            chunks.append({
                "text": chunk,
                "metadata": {"file": fname}
            })
            valid_chunks += 1
        print(f"[DEBUG] Created {len(these_chunks)} chunks for {fname}, kept {valid_chunks} (<=3MB)")
    print(f"[DEBUG] Finished chunking: {len(chunks)} chunks created")
    return chunks
