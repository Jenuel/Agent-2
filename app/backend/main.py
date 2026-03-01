from fastapi import FastAPI, HTTPException
from backend.services.github_service import get_user_repos
from backend.evaluator import evaluate_repos
from backend.report_generator import save_report

app = FastAPI(title="GitHub Repo Evaluator API")


@app.get("/")
async def root():
    return {"message": "GitHub Repo Evaluator API is running."}


@app.post("/evaluate")
async def evaluate(github_url: str):
    username = github_url.rstrip("/").split("/")[-1]

    if not username:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL.")

    repos = await get_user_repos(username)

    if not repos:
        raise HTTPException(status_code=404, detail=f"No public repositories found for '{username}'.")

    result = await evaluate_repos(username, repos)

    report_path = save_report(username, result)

    return {
        "username":      username,
        "overall_score": result["overall_score"],
        "report":        report_path,
        "repos":         result["repos"],
    }