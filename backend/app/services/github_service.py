# app/services/github_service.py
import requests

def list_and_get_files(owner, repo, extensions=None, github_token=None):
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        print(f"[DEBUG] Using GitHub token in list_and_get_files (starts with: {github_token[:6]})")
    else:
        print("[WARN] No GitHub token used in list_and_get_files (may be rate-limited)")
    session.headers.update(headers)

    # Get default branch
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"[DEBUG] GET {repo_url} to fetch default branch")
    repo_resp = session.get(repo_url)
    print(f"[DEBUG] repo_resp status: {repo_resp.status_code}")
    if repo_resp.status_code == 403:
        print("[ERROR] 403 on repo_resp:", repo_resp.json())
        # Check rate limit
        rl_resp = session.get("https://api.github.com/rate_limit")
        print("[DEBUG] Rate limit info:", rl_resp.json())
    repo_resp.raise_for_status()
    branch = repo_resp.json().get("default_branch", "main")
    print(f"[DEBUG] Default branch is: {branch}")

    # Get the recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    print(f"[DEBUG] GET {tree_url} to fetch tree")
    tree_resp = session.get(tree_url)
    print(f"[DEBUG] tree_resp status: {tree_resp.status_code}")
    if tree_resp.status_code == 403:
        print("[ERROR] 403 on tree_resp:", tree_resp.json())
        rl_resp = session.get("https://api.github.com/rate_limit")
        print("[DEBUG] Rate limit info:", rl_resp.json())
    tree_resp.raise_for_status()
    tree = tree_resp.json()

    files = []
    for obj in tree.get("tree", []):
        if obj["type"] == "blob":
            path = obj["path"]

            if extensions is None or any(path.endswith(ext) for ext in extensions):
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
                print(f"[DEBUG] GET {raw_url} to fetch file")
                try:
                    file_resp = session.get(raw_url)
                    print(f"[DEBUG] file_resp status: {file_resp.status_code} for {path}")
                    if file_resp.ok:
                        try:
                            content = file_resp.text
                            print(f"[DEBUG] File: {path} | Length: {len(content)} chars | First 100 chars: {repr(content[:100])}")
                            if content.strip():
                                files.append({"filename": path, "content": content})
                                print("[DEBUG] Added to files (non-empty).")
                            else:
                                print("[DEBUG] Not added (empty after strip).")
                        except UnicodeDecodeError:
                            print(f"[WARN] Skipping binary file: {path}")
                    else:
                        print(f"[WARN] Failed to fetch {path}: {file_resp.status_code}")
                        if file_resp.status_code == 403:
                            print("[ERROR] 403 on file fetch:", file_resp.text)
                            rl_resp = session.get("https://api.github.com/rate_limit")
                            print("[DEBUG] Rate limit info:", rl_resp.json())
                except Exception as e:
                    print(f"[WARN] Error fetching {path}: {e}")
    print(f"[DEBUG] Returning {len(files)} files")
    return files

def get_file_content_from_github(owner, repo, file_path, branch="main", github_token=None):
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        print(f"[DEBUG] Using GitHub token in get_file_content_from_github (starts with: {github_token[:6]})")
    session.headers.update(headers)

    if branch is None:
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        print(f"[DEBUG] GET {repo_url} to fetch default branch")
        repo_resp = session.get(repo_url)
        repo_resp.raise_for_status()
        branch = repo_resp.json().get("default_branch", "main")

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    print(f"[DEBUG] GET {raw_url} to fetch file content")
    resp = session.get(raw_url)
    if not resp.ok:
        print(f"[ERROR] Failed to fetch file content for {file_path} (status {resp.status_code})")
        if resp.status_code == 403:
            print("[ERROR] 403 on file content fetch:", resp.text)
            rl_resp = session.get("https://api.github.com/rate_limit")
            print("[DEBUG] Rate limit info:", rl_resp.json())
        raise Exception(f"Failed to fetch file content for {file_path} (status {resp.status_code})")
    return resp.text