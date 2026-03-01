from backend.services.github_service import clone_repo, analyze_structure, read_readme
from backend.agents.git_agent import analyze_git
from backend.agents.architecture_agent import detect_architecture
from backend.agents.test_agent import detect_tests
from backend.agents.devops_agent import detect_ci
from backend.report_generator import evaluate_readme, model

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END

class RepoState(TypedDict, total=False):
    username: str
    repo: dict
    path: str
    readme: str
    structure: float
    git: float
    architecture: float
    tests: float
    ci: float
    docs: float
    result: dict
    repo_score: float
    recommendation: str



def clone_and_structure_node(state: RepoState) -> Dict[str, Any]:
    path = clone_repo(state["username"], state["repo"])
    structure = analyze_structure(path)
    readme = read_readme(path)
    return {"path": path, "structure": structure, "readme": readme}


def analyze_git_node(state: RepoState) -> Dict[str, Any]:
    return {"git": analyze_git(state["path"])}


def detect_arch_node(state: RepoState) -> Dict[str, Any]:
    return {"architecture": detect_architecture(state["path"])}


def detect_tests_node(state: RepoState) -> Dict[str, Any]:
    return {"tests": detect_tests(state["path"])}


def detect_ci_node(state: RepoState) -> Dict[str, Any]:
    return {"ci": detect_ci(state["path"])}


def evaluate_docs_node(state: RepoState) -> Dict[str, Any]:
    return {"docs": float(evaluate_readme(state.get("readme", "")))}


def compile_score_node(state: RepoState) -> Dict[str, Any]:
    scores = {
        "structure": state.get("structure", 0),
        "git": state.get("git", 0),
        "architecture": state.get("architecture", 0),
        "tests": state.get("tests", 0),
        "ci": state.get("ci", 0),
        "docs": state.get("docs", 0),
    }

    repo_score = sum(scores.values()) / len(scores)

    result = {
        "repo":   state["repo"]["name"],
        "score":  round(repo_score, 2),
        **{k: round(v, 2) for k, v in scores.items()},
    }

    return {"result": result, "repo_score": repo_score}


def generate_recommendation_node(state: RepoState) -> Dict[str, Any]:
    result = state.get("result", {})

    prompt = f"""
You are a senior technical recruiter evaluating a software developer's GitHub profile.

The developer's repository scores are:
- Structure:     {result.get('structure', 'N/A')} / 10
- Git Quality:   {result.get('git', 'N/A')} / 10
- Architecture:  {result.get('architecture', 'N/A')} / 10
- Test Coverage: {result.get('tests', 'N/A')} / 10
- CI/CD Maturity:{result.get('ci', 'N/A')} / 10
- Documentation: {result.get('docs', 'N/A')} / 10
- Overall Score: {result.get('score', 'N/A')} / 10

Repository: {result.get('repo', 'Unknown')}

Should this candidate be hired? Provide a concise recommendation (2–3 sentences) with clear reasoning.
"""

    response = model.generate_content(prompt)
    return {"recommendation": response.text.strip()}





workflow = StateGraph(RepoState)

workflow.add_node("clone", clone_and_structure_node)
workflow.add_node("git", analyze_git_node)
workflow.add_node("arch", detect_arch_node)
workflow.add_node("test", detect_tests_node)
workflow.add_node("ci", detect_ci_node)
workflow.add_node("docs", evaluate_docs_node)
workflow.add_node("compile", compile_score_node)
workflow.add_node("recommend", generate_recommendation_node)

workflow.add_edge(START, "clone")
workflow.add_edge("clone", "git")
workflow.add_edge("clone", "arch")
workflow.add_edge("clone", "test")
workflow.add_edge("clone", "ci")
workflow.add_edge("clone", "docs")

workflow.add_edge(["git", "arch", "test", "ci", "docs"], "compile")
workflow.add_edge("compile", "recommend")
workflow.add_edge("recommend", END)

repo_eval_app = workflow.compile()

async def evaluate_repos(username, repos):
    results = []
    scores = []

    for repo in repos:
        initial_state = {"username": username, "repo": repo}
        
        # LangGraph runs individual sync agent nodes in its thread executors automatically!
        final_state = await repo_eval_app.ainvoke(initial_state)

        scores.append(final_state["repo_score"])
        results.append(final_state["result"])

    overall = sum(scores) / len(scores) if scores else 0

    return {
        "overall_score": round(overall, 2),
        "repos": results
    }
def generate_recommendation(result):

    prompt = f"""
        Candidate scores:

        {result}

        Should this candidate be hired?
        Respond with recommendation and reasoning.
    """

    response = model.generate_content(prompt)

    return response.text