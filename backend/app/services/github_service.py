import requests

def list_and_get_files(owner, repo, extensions=None, github_token=None):
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    session.headers.update(headers)

    # Get default branch
    repo_resp = session.get(f"https://api.github.com/repos/{owner}/{repo}")
    repo_resp.raise_for_status()
    branch = repo_resp.json().get("default_branch", "main")

    # Get the recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    tree_resp = session.get(tree_url)
    tree_resp.raise_for_status()
    tree = tree_resp.json()

    files = []
    for obj in tree.get("tree", []):
        if obj["type"] == "blob":
            path = obj["path"]

            # If extensions filter is provided, check it; otherwise include all files
            if extensions is None or any(path.endswith(ext) for ext in extensions):
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
                try:
                    file_resp = session.get(raw_url)
                    if file_resp.ok:
                        try:
                            content = file_resp.text
                            print(f"\n[DEBUG] File: {path}")
                            print(f"  [DEBUG] Length: {len(content)} chars")
                            print(f"  [DEBUG] First 100 chars: {repr(content[:100])}")
                            if content.strip():  # Only add non-empty files
                                files.append({"filename": path, "content": content})
                                print(f"  [DEBUG] Added to files (non-empty).")
                            else:
                                print(f"  [DEBUG] Not added (empty after strip).")
                        except UnicodeDecodeError:
                            print(f"[WARN] Skipping binary file: {path}")
                            continue
                    else:
                        print(f"[WARN] Failed to fetch {path}: {file_resp.status_code}")
                except Exception as e:
                    print(f"[WARN] Error fetching {path}: {e}")
                    continue

    print(f"\n[DEBUG] Returning {len(files)} files")
    return files

def get_file_content_from_github(owner, repo, file_path, branch="main", github_token=None):
    """
    Fetch the raw content of a file from a GitHub repository.
    """
    session = requests.Session()
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    session.headers.update(headers)

    # Optionally, you can make a call to get the default branch if you want it dynamic
    if branch is None:
        repo_resp = session.get(f"https://api.github.com/repos/{owner}/{repo}")
        repo_resp.raise_for_status()
        branch = repo_resp.json().get("default_branch", "main")

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    resp = session.get(raw_url)
    if not resp.ok:
        raise Exception(f"Failed to fetch file content for {file_path} (status {resp.status_code})")
    return resp.text