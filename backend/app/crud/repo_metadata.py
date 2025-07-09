from sqlalchemy.orm import Session
from app.models.repo_metadata import RepoMetadata

def get_repo_metadata(db: Session, repo_url: str):
    return db.query(RepoMetadata).filter(RepoMetadata.repo_url == repo_url).first()

def upsert_repo_metadata(
    db: Session,
    repo_url: str,
    file_tree_json: str,
    analytics_json: str,
    dependency_graph_json: str,
):
    meta = db.query(RepoMetadata).filter(RepoMetadata.repo_url == repo_url).first()
    if meta:
        meta.file_tree_json = file_tree_json
        meta.analytics_json = analytics_json
        meta.dependency_graph_json = dependency_graph_json
    else:
        meta = RepoMetadata(
            repo_url=repo_url,
            file_tree_json=file_tree_json,
            analytics_json=analytics_json,
            dependency_graph_json=dependency_graph_json,
        )
        db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta
