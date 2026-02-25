import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def evaluate_readme(readme):
    if not readme:
        return 3

    prompt = f"""
    Evaluate this GitHub README quality from 1 to 10.

    README:
    {readme[:3000]}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)

    score = response.text.strip()
    return score

async def evaluate_repos(username, repos):

    results = []

    total = 0

    for repo in repos:

        path = clone_repo(username, repo)

        structure_score = analyze_structure(path)

        readme = read_readme(path)

        readme_score = evaluate_readme(readme)

        repo_score = (structure_score + float(readme_score)) / 2

        total += repo_score

        results.append({
            "repo": repo["name"],
            "score": repo_score
        })

    overall = total / len(results)

    return {
        "overall_score": round(overall, 2),
        "repos": results
    }