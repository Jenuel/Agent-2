from git import Repo
import json
from .base_agent import Agent

def get_git_commits(path: str, limit: int = 50) -> list[str]:
    """Returns a list of the most recent git commit messages for the repository at the given path."""
    try:
        repo = Repo(path)
        commits = list(repo.iter_commits())[:limit]
        return [c.message.strip() for c in commits]
    except Exception:
        return []

def analyze_git(path: str) -> float:
    agent = Agent(
        name="Git Expert",
        instructions="You are an expert software engineer analyzing git commit history. Use the get_git_commits tool to get recent commit messages. Evaluate the readability, descriptiveness, and quality of the commits. Return ONLY a single float number between 0 to 10. No markdown, no other text.",
        tools=[get_git_commits]
    )
    result = agent.run(f"Evaluate the git commit history for the repo at {path}")
    try:
        return min(max(float(result.strip()), 0.0), 10.0)
    except Exception:
        return 5.0