
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
            "score": repo_score
        })

    overall = sum(scores) / len(scores)

    return {
        "overall_score": round(overall, 2),
        "repos": results
    }