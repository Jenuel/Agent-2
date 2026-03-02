import os
import httpx
from git import Repo
from backend.logger import get_logger

logger = get_logger(__name__)

REPO_DIR = "repos"


async def get_user_repos(username: str) -> list:
    url = f"https://api.github.com/users/{username}/repos"
    logger.info("Fetching repositories for user '%s' from %s", username, url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    logger.debug(
        "GitHub API response | status=%d | user=%s", response.status_code, username
    )

    if response.status_code != 200:
        logger.error(
            "GitHub API error | status=%d | user=%s | body=%s",
            response.status_code,
            username,
            response.text[:300],
        )
        return []

    repos = response.json()
    logger.info("Fetched %d total repos for user '%s'", len(repos), username)

    filtered = []
    skipped_forks = 0

    for repo in repos:
        if repo["fork"]:
            skipped_forks += 1
            continue

        filtered.append({
            "name":        repo["name"],
            "stars":       repo["stargazers_count"],
            "commits_url": repo["commits_url"].replace("{/sha}", ""),
            "url":         repo["clone_url"],
            "size":        repo["size"],
            "language":    repo["language"],
        })

    logger.info(
        "Filtered repos | original=%d | forks_skipped=%d | non_forks=%d",
        len(repos),
        skipped_forks,
        len(filtered),
    )

    filtered.sort(key=lambda x: x["stars"] + x["size"], reverse=True)
    top = filtered[:3]

    logger.info(
        "Top %d repos selected for '%s': %s",
        len(top),
        username,
        [r["name"] for r in top],
    )

    return top


def clone_repo(username: str, repo: dict) -> str:
    path = f"{REPO_DIR}/{username}_{repo['name']}"

    if os.path.exists(path):
        logger.info("Repo already cloned, reusing: %s", path)
    else:
        logger.info("Cloning repo '%s' from %s → %s", repo["name"], repo["url"], path)
        Repo.clone_from(repo["url"], path, depth=1)
        logger.info("Clone complete: %s", path)

    return path


def analyze_structure(path: str) -> float:
    file_count = 0

    for root, dirs, files in os.walk(path):
        file_count += len(files)

    score = min(file_count / 5, 10.0)
    logger.debug(
        "Structure analysis | path=%s | file_count=%d | score=%.2f",
        path,
        file_count,
        score,
    )
    return round(score, 2)


def read_readme(path: str) -> str:
    for file in os.listdir(path):
        if file.lower().startswith("readme"):
            readme_path = f"{path}/{file}"
            logger.debug("README found: %s", readme_path)
            with open(readme_path, encoding="utf-8") as f:
                return f.read()

    logger.debug("No README found in: %s", path)
    return ""
