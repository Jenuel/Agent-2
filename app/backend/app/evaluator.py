import os
from app.services.github_service import clone_repo, analyze_structure, read_readme
from app.agents.git_agent import analyze_git
from app.agents.architecture_agent import detect_architecture
from app.agents.test_agent import detect_tests
from app.agents.devops_agent import detect_ci
from app.report_generator import evaluate_readme, client
from app.logger import get_logger

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END

logger = get_logger(__name__)


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
    repo_name = state["repo"]["name"]
    logger.info("[clone] Starting clone + structure analysis for repo: %s", repo_name)

    path = clone_repo(state["username"], state["repo"])
    structure = analyze_structure(path)
    readme = read_readme(path)
    has_readme = bool(readme)

    logger.info(
        "[clone] Done | repo=%s | path=%s | structure_score=%.2f | has_readme=%s",
        repo_name, path, structure, has_readme,
    )
    return {"path": path, "structure": structure, "readme": readme}


def analyze_git_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    logger.info("[git] Analyzing git history for repo: %s", repo_name)
    score = analyze_git(state["path"])
    logger.info("[git] Score=%.2f for repo: %s", score, repo_name)
    return {"git": score}


def detect_arch_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    logger.info("[arch] Detecting architecture for repo: %s", repo_name)
    score = detect_architecture(state["path"])
    logger.info("[arch] Score=%.2f for repo: %s", score, repo_name)
    return {"architecture": score}


def detect_tests_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    logger.info("[test] Detecting test coverage for repo: %s", repo_name)
    score = detect_tests(state["path"])
    logger.info("[test] Score=%.2f for repo: %s", score, repo_name)
    return {"tests": score}


def detect_ci_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    logger.info("[ci] Detecting CI/CD config for repo: %s", repo_name)
    score = detect_ci(state["path"])
    logger.info("[ci] Score=%.2f for repo: %s", score, repo_name)
    return {"ci": score}


def evaluate_docs_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    readme_len = len(state.get("readme", ""))
    logger.info(
        "[docs] Evaluating README for repo: %s | readme_length=%d chars",
        repo_name, readme_len,
    )
    score = float(evaluate_readme(state.get("readme", "")))
    logger.info("[docs] Score=%.2f for repo: %s", score, repo_name)
    return {"docs": score}


def compile_score_node(state: RepoState) -> Dict[str, Any]:
    repo_name = state["repo"]["name"]
    scores = {
        "structure":    state.get("structure", 0),
        "git":          state.get("git", 0),
        "architecture": state.get("architecture", 0),
        "tests":        state.get("tests", 0),
        "ci":           state.get("ci", 0),
        "docs":         state.get("docs", 0),
    }

    repo_score = sum(scores.values()) / len(scores)

    logger.info(
        "[compile] Scores for '%s' | %s | overall=%.2f",
        repo_name,
        " | ".join(f"{k}={v:.2f}" for k, v in scores.items()),
        repo_score,
    )

    result = {
        "repo":  repo_name,
        "score": round(repo_score, 2),
        **{k: round(v, 2) for k, v in scores.items()},
    }

    return {"result": result, "repo_score": repo_score}


def generate_recommendation_node(state: RepoState) -> Dict[str, Any]:
    result = state.get("result", {})
    repo_name = result.get("repo", "Unknown")
    logger.info("[recommend] Generating LLM recommendation for repo: %s", repo_name)

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

Repository: {repo_name}

Should this candidate be hired? Provide a concise recommendation (2–3 sentences) with clear reasoning.
"""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL_ID"),
        contents=prompt,
    )
    recommendation = response.text.strip()
    logger.info("[recommend] Recommendation generated for repo: %s", repo_name)
    logger.debug("[recommend] Text: %s", recommendation[:200])

    return {"recommendation": recommendation}


# ── Graph assembly ─────────────────────────────────────────────────────────────

workflow = StateGraph(RepoState)

workflow.add_node("clone",     clone_and_structure_node)
workflow.add_node("git",       analyze_git_node)
workflow.add_node("arch",      detect_arch_node)
workflow.add_node("test",      detect_tests_node)
workflow.add_node("ci",        detect_ci_node)
workflow.add_node("docs",      evaluate_docs_node)
workflow.add_node("compile",   compile_score_node)
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


async def evaluate_repos(username: str, repos: list) -> dict:
    logger.info("Starting evaluation pipeline for user '%s' | repos=%d", username, len(repos))
    results = []
    scores = []

    for repo in repos:
        logger.info("--- Evaluating repo: %s ---", repo["name"])
        initial_state: RepoState = {"username": username, "repo": repo}

        final_state = await repo_eval_app.ainvoke(initial_state)

        scores.append(final_state["repo_score"])
        results.append({
            **final_state["result"],
            "recommendation": final_state.get("recommendation", ""),
        })

        logger.info(
            "Repo '%s' evaluation done | score=%.2f",
            repo["name"],
            final_state["repo_score"],
        )

    overall = sum(scores) / len(scores) if scores else 0.0
    logger.info(
        "All repos evaluated for '%s' | overall_score=%.2f", username, overall
    )

    return {
        "overall_score": round(overall, 2),
        "repos":         results,
    }
