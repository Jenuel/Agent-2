import os
from .base_agent import Agent
from backend.logger import get_logger

logger = get_logger(__name__)


def get_ci_workflows(path: str) -> list[str]:
    """Returns a list of CI/CD workflow files found in the repository (e.g., .github/workflows)."""
    workflows = []
    ci_path = os.path.join(path, ".github", "workflows")
    if os.path.exists(ci_path):
        for file in os.listdir(ci_path):
            workflows.append(file)
    logger.debug(
        "get_ci_workflows | path=%s | ci_path_exists=%s | workflow_count=%d",
        path,
        os.path.exists(ci_path),
        len(workflows),
    )
    return workflows


def detect_ci(path: str) -> float:
    logger.info("detect_ci: starting for path=%s", path)
    agent = Agent(
        name="DevOps Expert",
        instructions=(
            "You are an expert DevOps engineer evaluating CI/CD pipelines. "
            "Use the get_ci_workflows tool to check github actions or ci configurations. "
            "Based on the presence and number of CI workflow files, evaluate their devops maturity from 0 to 10. "
            "Return ONLY a single float number between 0 to 10. No markdown, no other text."
        ),
        tools=[get_ci_workflows],
    )
    result = agent.run(f"Evaluate the CI/CD strategy for the repository cloned at {path}")
    try:
        score = min(max(float(result.strip()), 0.0), 10.0)
        logger.info("detect_ci: score=%.2f for path=%s", score, path)
        return score
    except Exception as exc:
        logger.warning(
            "detect_ci: could not parse score %r (error=%s), defaulting to 5.0",
            result, exc,
        )
        return 5.0