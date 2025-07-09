# app/routers/repo.py

from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import requests

from app.services.github_service import list_and_get_files, get_file_content_from_github
from app.services.chunking_service import chunk_files_mem
from app.services.rag_service import upsert_chunks_to_pinecone, delete_pinecone_namespace
from app.utils.db import get_db
from app.crud.api_key import get_api_key
from app.crud.repo_metadata import get_repo_metadata, upsert_repo_metadata
from app.crud.active_repo import (
    get_active_repo,
    set_active_repo,
    delete_active_repo,
)
from app.crud.chat import delete_chat_namespace

# Request models
class GetActiveRepoRequest(BaseModel):
    user_id: str

class SwitchRepoRequest(BaseModel):
    user_id: str

class GetFileContentRequest(BaseModel):
    user_id: str
    file_path: str

router = APIRouter(prefix="/repo", tags=["Repo"])

@router.post("/metadata")
async def get_repo_metadata_endpoint(
    body: GetActiveRepoRequest = Body(...),
    db: Session = Depends(get_db)
):
    repo_url = get_active_repo(db, body.user_id)
    if not repo_url:
        raise HTTPException(status_code=400, detail="No active repo for user.")

    meta = get_repo_metadata(db, repo_url)
    if not meta:
        raise HTTPException(status_code=404, detail="No metadata found for this repo. Please re-ingest.")

    return {
        "file_tree": json.loads(meta.file_tree_json),
        "analytics": json.loads(meta.analytics_json) if meta.analytics_json else {},
        "dependency_graph": json.loads(meta.dependency_graph_json) if meta.dependency_graph_json else {},
    }

@router.post("/ingest_repo")
async def ingest_repo(
    repo_url: str = Body(...),
    user_id: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Ingest a GitHub repo into Pinecone: fetch files, chunk, upsert.
    Also collects rich GitHub analytics.
    If another repo was previously active for this user, all previous repo data is deleted.
    """
    try:
        print("DEBUG: ingest_repo - user_id:", user_id, "repo_url:", repo_url)
        # Cleanup previous
        previous_repo_url = get_active_repo(db, user_id)
        if previous_repo_url:
            prev_repo = previous_repo_url.rstrip("/").split("/")[-1]
            prev_namespace = f"{user_id}_{prev_repo}"
            print("DEBUG: ingest_repo - cleaning up previous namespace:", prev_namespace)
            delete_pinecone_namespace(prev_namespace)
            delete_chat_namespace(db, prev_namespace)
            delete_active_repo(db, user_id)

        openai_api_key = get_api_key(db, user_id)
        if not openai_api_key:
            print("ERROR: No OpenAI API key set for this user.")
            raise HTTPException(status_code=401, detail="No OpenAI API key set for this user.")

        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        print("DEBUG: ingest_repo - owner:", owner, "repo:", repo)
        files = list_and_get_files(owner, repo)
        print("DEBUG: ingest_repo - files count:", len(files))
        chunks = chunk_files_mem(files)
        print("DEBUG: ingest_repo - chunks count:", len(chunks))
        namespace = f"{user_id}_{repo}"
        upsert_chunks_to_pinecone(chunks, namespace, openai_api_key)
        print("DEBUG: ingest_repo - upsert to pinecone done")

        # ===== Advanced: Gather all GitHub metadata =====
        GITHUB_API = "https://api.github.com"
        headers = {"Accept": "application/vnd.github.v3+json"}
        repo_info = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=headers).json()
        languages = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/languages", headers=headers).json()
        contributors = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/contributors", headers=headers).json()
        topics = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/topics", headers={"Accept": "application/vnd.github.mercy-preview+json"}).json()
        releases = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/releases", headers=headers).json()
        try:
            readme = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/readme", headers={"Accept": "application/vnd.github.v3.raw"}).text
        except Exception:
            readme = ""

        analytics = {
            "repo_name": repo_info.get("name"),
            "owner": repo_info.get("owner", {}).get("login"),
            "description": repo_info.get("description"),
            "stars": repo_info.get("stargazers_count"),
            "forks": repo_info.get("forks_count"),
            "open_issues": repo_info.get("open_issues_count"),
            "watchers": repo_info.get("subscribers_count"),
            "default_branch": repo_info.get("default_branch"),
            "license": repo_info.get("license", {}).get("name") if repo_info.get("license") else None,
            "created_at": repo_info.get("created_at"),
            "updated_at": repo_info.get("updated_at"),
            "pushed_at": repo_info.get("pushed_at"),
            "homepage": repo_info.get("homepage"),
            "size_kb": repo_info.get("size"),
            "language": repo_info.get("language"),
            "languages": languages,
            "topics": topics.get("names", []),
            "contributors": [
                {"login": c.get("login"), "contributions": c.get("contributions"), "avatar_url": c.get("avatar_url")}
                for c in contributors[:10]
            ] if contributors else [],
            "releases": [
                {"name": r.get("name"), "tag": r.get("tag_name"), "published_at": r.get("published_at")}
                for r in releases[:5]
            ] if releases else [],
            "readme": readme[:3000] + ("..." if len(readme) > 3000 else ""),
        }

        # Update repo metadata in database
        from app.services.repo_analysis import build_file_tree, analyze_repo  # For file tree + dependency analysis

        file_tree = build_file_tree(files)
        analytics_json = json.dumps(analytics)
        file_tree_json = json.dumps(file_tree)
        dependency_graph = analyze_repo(files)
        dependency_graph_json = json.dumps(dependency_graph)

        upsert_repo_metadata(
            db=db,
            repo_url=repo_url,
            file_tree_json=file_tree_json,
            analytics_json=analytics_json,
            dependency_graph_json=dependency_graph_json,
        )

        set_active_repo(db, user_id, repo_url)

        return {"ok": True, "namespace": namespace}
    except Exception as e:
        print("ERROR in ingest_repo:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch_repo")
async def switch_repo(
    body: SwitchRepoRequest = Body(...),
    db: Session = Depends(get_db)
):
    user_id = body.user_id
    try:
        repo_url = get_active_repo(db, user_id)
        if repo_url:
            repo = repo_url.rstrip("/").split("/")[-1]
            namespace = f"{user_id}_{repo}"
            print("DEBUG: switch_repo - deleting namespace:", namespace)
            delete_pinecone_namespace(namespace)
            delete_chat_namespace(db, namespace)
            delete_active_repo(db, user_id)
        return {"ok": True}
    except Exception as e:
        print("ERROR in switch_repo:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_active_repo")
async def get_active_repo_endpoint(
    body: GetActiveRepoRequest = Body(...),
    db: Session = Depends(get_db)
):
    repo_url = get_active_repo(db, body.user_id)
    return {"repo_url": repo_url}

@router.post("/get_file_content")
async def get_file_content(
    body: GetFileContentRequest,
    db: Session = Depends(get_db)
):
    """
    Return the content of a file in the active repo for this user.
    """
    repo_url = get_active_repo(db, body.user_id)
    if not repo_url:
        raise HTTPException(status_code=400, detail="No active repo for user.")
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    try:
        content = get_file_content_from_github(owner, repo, body.file_path)
        return {"content": content}
    except Exception as e:
        print("ERROR in get_file_content:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch file content.")
