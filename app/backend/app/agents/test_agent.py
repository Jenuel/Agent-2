import os
from .base_agent import Agent
from app.logger import get_logger

logger = get_logger(__name__)


def get_test_files(path: str) -> list[str]:
    """Returns a list of all file names that contain the word 'test' in their name within the given directory path."""
    test_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if "test" in file.lower():
                test_files.append(os.path.relpath(os.path.join(root, file), path))
    logger.debug("get_test_files | path=%s | test_file_count=%d", path, len(test_files))
    return test_files


def detect_tests(path: str) -> float:
    logger.info("detect_tests: starting for path=%s", path)
    agent = Agent(
        name="QA Expert",
        instructions=(
            "You are an expert QA automation engineer. "
            "Use the get_test_files tool to get a list of test files for the codebase. "
            "Evaluate the coverage and testing strategy based on the files available. "
            "Return ONLY a single float number between 0 to 10. No markdown, no other text. "
            "A large codebase without tests should be 0. Multiple test files in multiple domains is a 10."
        ),
        tools=[get_test_files],
    )
    result = agent.run(f"Evaluate the test strategy for the repository cloned at {path}")
    try:
        score = min(max(float(result.strip()), 0.0), 10.0)
        logger.info("detect_tests: score=%.2f for path=%s", score, path)
        return score
    except Exception as exc:
        logger.warning(
            "detect_tests: could not parse score %r (error=%s), defaulting to 5.0",
            result, exc,
        )
        return 5.0
