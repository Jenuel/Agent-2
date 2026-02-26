import os
from git import Repo

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

def analyze_git(path):

    repo = Repo(path)

    commits = list(repo.iter_commits())

    commit_count = len(commits)

    descriptive = 0

    for commit in commits[:50]:

        msg = commit.message.lower()

        if len(msg.split()) > 3:
            descriptive += 1

    quality_ratio = descriptive / max(len(commits[:50]), 1)

    commit_score = min(commit_count / 100, 10)

    message_score = quality_ratio * 10

    return round((commit_score + message_score) / 2, 2)