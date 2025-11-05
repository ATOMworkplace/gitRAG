# app/services/github_service.py
import requests
import time
import io
import tarfile
from typing import List
from app.core.config import (
    GITHUB_DENY_DIRS,
    GITHUB_MAX_BYTES_PER_FILE,
    GITHUB_REPO_INGEST_BYTE_BUDGET,
    GITHUB_MAX_FILES_PER_REPO,
    GITHUB_MAX_INGEST_SECONDS
)

_DENY_DIRS = tuple(d.strip().rstrip("/") for d in GITHUB_DENY_DIRS.split(",") if d.strip())

_BINARY_SUFFIXES = (
    ".png",".jpg",".jpeg",".gif",".webp",".pdf",".zip",".tar",".gz",".tgz",".bz2",".xz",
    ".7z",".exe",".dll",".so",".dylib",".ico",".icns"
)

def _is_binary_path(path: str) -> bool:
    p = path.lower()
    return p.endswith(_BINARY_SUFFIXES)

def _deny_by_dir(path: str) -> bool:
    return any(path.startswith(d + "/") or ("/" + d + "/") in ("/" + path) for d in _DENY_DIRS)

def _should_fetch(path: str, legacy_exts=None) -> bool:
    if _deny_by_dir(path):
        return False
    if _is_binary_path(path):
        return False
    if legacy_exts is not None and not any(path.endswith(ext) for ext in legacy_exts):
        return False
    return True

def _rate_limited_get(session, url, max_attempts=5, headers=None, stream=False):
    for attempt in range(max_attempts):
        resp = session.get(url, headers=headers, stream=stream)
        if resp.status_code in (403, 429):
            reset = resp.headers.get("X-RateLimit-Reset")
            if reset:
                try:
                    wait_for = max(0, int(reset) - int(time.time()))
                    time.sleep(min(wait_for, 60))
                except Exception:
                    time.sleep(min(2 ** attempt, 32))
            else:
                time.sleep(min(2 ** attempt, 32))
            continue
        return resp
    return resp

def _get_default_branch(session, owner, repo, github_token=None) -> str:
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    r = _rate_limited_get(session, repo_url, headers=headers)
    r.raise_for_status()
    return r.json().get("default_branch", "main")

def iter_tar_entries(owner: str, repo: str, ref: str = "main", github_token: str | None = None):
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{ref}"
    with requests.Session() as s:
        with _rate_limited_get(s, url, headers=headers, stream=True) as r:
            r.raise_for_status()
            bio = io.BufferedReader(r.raw)
            with tarfile.open(fileobj=bio, mode="r|*") as tf:
                for m in tf:
                    if not m or not m.isfile():
                        continue
                    parts = m.name.split("/", 1)
                    relpath = parts[1] if len(parts) > 1 else m.name
                    fobj = tf.extractfile(m)
                    if not fobj:
                        continue
                    yield relpath, fobj

def stream_repo_texts(owner: str, repo: str, github_token: str | None, per_file_cap_bytes: int):
    with requests.Session() as session:
        ref = _get_default_branch(session, owner, repo, github_token)
    for relpath, fobj in iter_tar_entries(owner, repo, ref, github_token):
        if _deny_by_dir(relpath) or _is_binary_path(relpath):
            fobj.close()
            continue
        try:
            data = fobj.read(per_file_cap_bytes)
            if not data:
                continue
            text = data.decode("utf-8", errors="ignore")
            if text.strip():
                yield relpath, text
        finally:
            fobj.close()

def list_and_get_files(owner, repo, extensions=None, github_token=None):
    session = requests.Session()
    start_ts = time.time()
    total_bytes = 0
    files_out = []
    files_count = 0
    ref = _get_default_branch(session, owner, repo, github_token)
    for path, fobj in iter_tar_entries(owner, repo, ref, github_token):
        if not _should_fetch(path, legacy_exts=extensions):
            fobj.close()
            continue
        if time.time() - start_ts > GITHUB_MAX_INGEST_SECONDS:
            fobj.close()
            break
        if files_count >= GITHUB_MAX_FILES_PER_REPO:
            fobj.close()
            break
        if total_bytes >= GITHUB_REPO_INGEST_BYTE_BUDGET:
            fobj.close()
            break
        try:
            data = fobj.read(min(GITHUB_MAX_BYTES_PER_FILE, max(0, GITHUB_REPO_INGEST_BYTE_BUDGET - total_bytes)))
            if not data:
                continue
            content = data.decode("utf-8", errors="ignore")
            if content.strip():
                b = len(content.encode("utf-8"))
                remaining = max(0, GITHUB_REPO_INGEST_BYTE_BUDGET - total_bytes)
                if b > remaining:
                    if remaining == 0:
                        break
                    content = content.encode("utf-8")[:remaining].decode("utf-8", errors="ignore")
                    b = len(content.encode("utf-8"))
                files_out.append({"filename": path, "content": content})
                total_bytes += b
                files_count += 1
        finally:
            fobj.close()
    return files_out

def get_file_content_from_github(owner, repo, file_path, branch="main", github_token=None):
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    session.headers.update(headers)
    if branch is None:
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_resp = session.get(repo_url)
        repo_resp.raise_for_status()
        branch = repo_resp.json().get("default_branch", "main")
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    resp = session.get(raw_url)
    if not resp.ok:
        if resp.status_code == 403:
            _ = session.get("https://api.github.com/rate_limit")
        raise Exception(f"Failed to fetch file content for {file_path} (status {resp.status_code})")
    return resp.text

def list_repo_file_paths(owner: str, repo: str, github_token: str | None = None) -> List[str]:
    paths: List[str] = []
    with requests.Session() as session:
        ref = _get_default_branch(session, owner, repo, github_token)
    for relpath, fobj in iter_tar_entries(owner, repo, ref, github_token):
        paths.append(relpath)
        fobj.close()
    return paths
