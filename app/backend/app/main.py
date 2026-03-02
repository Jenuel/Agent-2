from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from app.services.github_service import get_user_repos
from app.evaluator import evaluate_repos
from app.report_generator import save_report
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="GitHub Repo Evaluator API")


@app.get("/")
async def root():
    logger.info("Health-check endpoint hit.")
    return {"message": "GitHub Repo Evaluator API is running."}


@app.post("/evaluate")
async def evaluate(github_url: str):
    logger.info("Received /evaluate request for URL: %s", github_url)

    username = github_url.rstrip("/").split("/")[-1]

    if not username:
        logger.warning("Invalid GitHub URL provided: %s", github_url)
        raise HTTPException(status_code=400, detail="Invalid GitHub URL.")

    logger.info("Extracted username: %s", username)

    repos = await get_user_repos(username)

    if not repos:
        logger.warning("No public repositories found for user: %s", username)
        raise HTTPException(
            status_code=404,
            detail=f"No public repositories found for '{username}'.",
        )

    logger.info("Found %d repos to evaluate for user: %s", len(repos), username)

    result = await evaluate_repos(username, repos)

    logger.info(
        "Evaluation complete for %s | overall_score=%.2f",
        username,
        result["overall_score"],
    )

    report_path = save_report(username, result)

    logger.info("Report saved at: %s", report_path)

    return {
        "username":      username,
        "overall_score": result["overall_score"],
        "report":        report_path,
        "repos":         result["repos"],
    }
