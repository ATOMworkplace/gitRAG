# app/services/github_service.py
import requests

def list_and_get_files(owner, repo, extensions=None, github_token=None):
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    session.headers.update(headers)

    # Get default branch
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_resp = session.get(repo_url)
    if repo_resp.status_code == 403:
        # Check rate limit
        rl_resp = session.get("https://api.github.com/rate_limit")
    repo_resp.raise_for_status()
    branch = repo_resp.json().get("default_branch", "main")

    # Get the recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    tree_resp = session.get(tree_url)
    if tree_resp.status_code == 403:
        rl_resp = session.get("https://api.github.com/rate_limit")
    tree_resp.raise_for_status()
    tree = tree_resp.json()

    files = []
    for obj in tree.get("tree", []):
        if obj["type"] == "blob":
            path = obj["path"]

            if extensions is None or any(path.endswith(ext) for ext in extensions):
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
                try:
                    file_resp = session.get(raw_url)
                    if file_resp.ok:
                        try:
                            content = file_resp.text
                            if content.strip():
                                files.append({"filename": path, "content": content})
                        except UnicodeDecodeError:
                            print(f"[WARN] Skipping binary file: {path}")
                    else:
                        if file_resp.status_code == 403:
                            rl_resp = session.get("https://api.github.com/rate_limit")
                except Exception as e:
                    print(f"[WARN] Error fetching {path}: {e}")
    return files

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
            rl_resp = session.get("https://api.github.com/rate_limit")
        raise Exception(f"Failed to fetch file content for {file_path} (status {resp.status_code})")
    return resp.text