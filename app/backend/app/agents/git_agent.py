from git import Repo
import json
from .base_agent import Agent
from app.logger import get_logger

logger = get_logger(__name__)


def get_git_commits(path: str, limit: int = 50) -> list[str]:
    """Returns a list of the most recent git commit messages for the repository at the given path."""
    try:
        repo = Repo(path)
        commits = list(repo.iter_commits())[:limit]
        messages = [c.message.strip() for c in commits]
        logger.debug("get_git_commits | path=%s | retrieved=%d commits", path, len(messages))
        return messages
    except Exception as exc:
        logger.warning("get_git_commits failed for path=%s | error=%s", path, exc)
        return []


def analyze_git(path: str) -> float:
    logger.info("analyze_git: starting for path=%s", path)
    agent = Agent(
        name="Git Expert",
        instructions=(
            "You are an expert software engineer analyzing git commit history. "
            "Use the get_git_commits tool to get recent commit messages. "
            "Evaluate the readability, descriptiveness, and quality of the commits. "
            "Return ONLY a single float number between 0 to 10. No markdown, no other text."
        ),
        tools=[get_git_commits],
    )
    result = agent.run(f"Evaluate the git commit history for the repo at {path}")
    try:
        score = min(max(float(result.strip()), 0.0), 10.0)
        logger.info("analyze_git: score=%.2f for path=%s", score, path)
        return score
    except Exception as exc:
        logger.warning(
            "analyze_git: could not parse score %r (error=%s), defaulting to 5.0",
            result, exc,
        )
        return 5.0
