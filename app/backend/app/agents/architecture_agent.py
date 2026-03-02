import os
from .base_agent import Agent
from backend.logger import get_logger

logger = get_logger(__name__)


def get_file_tree(path: str) -> list[str]:
    """Returns a list of all files in the given directory path. Good for seeing the repository's structure."""
    tree = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".git" in root or ".venv" in root:
                continue
            tree.append(os.path.relpath(os.path.join(root, file), path))
    logger.debug("get_file_tree | path=%s | file_count=%d", path, len(tree))
    return tree


def detect_architecture(path: str) -> float:
    logger.info("detect_architecture: starting for path=%s", path)
    agent = Agent(
        name="Architecture Expert",
        instructions=(
            "You are an expert software architect analyzing code structure. "
            "Use the get_file_tree tool to inspect the repository. "
            "Evaluate the presence of design patterns, MVC models, microservices, "
            "containerization, and modern frameworks. "
            "Return ONLY a single float number between 0 to 10. No markdown, no other text."
        ),
        tools=[get_file_tree],
    )
    result = agent.run(f"Evaluate the architecture for the repository cloned at {path}")
    try:
        score = min(max(float(result.strip()), 0.0), 10.0)
        logger.info("detect_architecture: score=%.2f for path=%s", score, path)
        return score
    except Exception as exc:
        logger.warning(
            "detect_architecture: could not parse score %r (error=%s), defaulting to 5.0",
            result, exc,
        )
        return 5.0