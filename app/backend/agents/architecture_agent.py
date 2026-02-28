import os
from .base_agent import Agent

def get_file_tree(path: str) -> list[str]:
    """Returns a list of all files in the given directory path. Good for seeing the repository's structure."""
    tree = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".git" in root or ".venv" in root:
                continue
            tree.append(os.path.relpath(os.path.join(root, file), path))
    return tree

def detect_architecture(path: str) -> float:
    agent = Agent(
        name="Architecture Expert",
        instructions="You are an expert software architect analyzing code structure. Use the get_file_tree tool to inspect the repository. Evaluate the presence of design patterns, MVC models, microservices, containerization, and modern frameworks. Return ONLY a single float number between 0 to 10. No markdown, no other text.",
        tools=[get_file_tree]
    )
    result = agent.run(f"Evaluate the architecture for the repository cloned at {path}")
    try:
        return min(max(float(result.strip()), 0.0), 10.0)
    except Exception:
        return 5.0