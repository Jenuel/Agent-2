from backend.services.github_service import clone_repo, analyze_structure, read_readme
from backend.agents.git_agent import analyze_git
from backend.agents.architecture_agent import detect_architecture
from backend.agents.test_agent import detect_tests
from backend.agents.devops_agent import detect_ci
from backend.report_generator import evaluate_readme, model

async def evaluate_repos(username, repos):

    results = []

    scores = []

    for repo in repos:

        path = clone_repo(username, repo)

        structure = analyze_structure(path)

        git_score = analyze_git(path)

        arch = detect_architecture(path)

        tests = detect_tests(path)

        ci = detect_ci(path)

        readme = read_readme(path)

        docs = float(evaluate_readme(readme))

        repo_score = (
            structure +
            git_score +
            arch +
            tests +
            ci +
            docs
        ) / 6

        scores.append(repo_score)

        results.append({
            "repo": repo["name"],
            "structure": structure,
            "git": git_score,
            "architecture": arch,
            "tests": tests,
            "ci": ci,
            "docs": docs,
            "score": round(repo_score, 2)
        })

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