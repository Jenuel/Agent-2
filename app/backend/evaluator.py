import os

REPO_DIR = "repos"

def clone_repo(username, repo):

    path = f"{REPO_DIR}/{username}_{repo['name']}"

    if not os.path.exists(path):

        Repo.clone_from(
            repo["url"],
            path,
            depth=1
        )

    return path

def analyze_structure(path):

    file_count = 0

    for root, dirs, files in os.walk(path):
        file_count += len(files)

    score = min(file_count / 50, 10)

    return round(score, 2)

def read_readme(path):

    for file in os.listdir(path):

        if file.lower().startswith("readme"):
            with open(f"{path}/{file}", encoding="utf-8") as f:
                return f.read()

    return ""
