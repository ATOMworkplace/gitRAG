# app/services/repo_analysis.py

def build_file_tree(files):
    tree = {}
    for file in files:
        parts = file["filename"].split("/")
        current = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Leaf node = file
                current[part] = None
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    return tree

def analyze_repo(files):
    analytics = {
        "num_files": len(files),
        "file_extensions": {},
        "total_lines": 0,
        "total_bytes": 0,
        "largest_file": "",
        "largest_file_size": 0,
    }

    for f in files:
        filename = f["filename"]
        content = f["content"]
        ext = filename.split('.')[-1] if '.' in filename else ''
        analytics["file_extensions"].setdefault(ext, 0)
        analytics["file_extensions"][ext] += 1
        num_lines = content.count('\n') + 1 if content else 0
        analytics["total_lines"] += num_lines
        analytics["total_bytes"] += len(content.encode("utf-8"))
        if len(content.encode("utf-8")) > analytics["largest_file_size"]:
            analytics["largest_file"] = filename
            analytics["largest_file_size"] = len(content.encode("utf-8"))

    return analytics

def dummy_dependency_graph(files):
    nodes = [{"id": f["filename"]} for f in files if f["filename"].endswith(".py")]
    edges = []
    if len(nodes) >= 2:
        edges.append({"from": nodes[0]["id"], "to": nodes[1]["id"]})
    return {"nodes": nodes, "edges": edges}

def build_file_tree_from_paths(paths: list[str]):
    tree = {}
    for p in paths:
        parts = p.split("/")
        cur = tree
        for i, part in enumerate(parts):
            is_file = i == len(parts) - 1
            if is_file:
                cur[part] = None
            else:
                if part not in cur or not isinstance(cur[part], dict):
                    cur[part] = {}
                cur = cur[part]
    return tree
