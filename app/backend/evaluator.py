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