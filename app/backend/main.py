from fastapi import FastAPI
from backend.services.github_service import get_user_repos
from backend.evaluator import evaluate_repos
from backend.report_generator import save_report

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "GitHub Repo Evaluator API is running."}

@app.post("/evaluate")
async def evaluate(github_url: str):

    username = github_url.rstrip("/").split("/")[-1]

    repos = await get_user_repos(username)

    result = await evaluate_repos(username, repos)

    report_path = save_report(username, result)

    return {
        "username": username,
        "score": result["overall_score"],
        "report": report_path
    }