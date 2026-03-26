from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import urllib.parse
import logging
from dotenv import load_dotenv
load_dotenv()

from app.services.github_service import get_user_repos
from app.evaluator import evaluate_repos
from app.report_generator import save_report
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="GitHub Repo Evaluator API")

class EvaluateRequest(BaseModel):
    github_url: HttpUrl

class EvaluateResponse(BaseModel):
    username: str
    overall_score: float
    report: str
    repos: list

def extract_username(url: str) -> str:
    """Extracts username robustly from a GitHub URL."""
    parsed_url = urllib.parse.urlparse(str(url))
    path_parts = [part for part in parsed_url.path.split('/') if part]
    if not path_parts:
        return ""
    return path_parts[0]

@app.get("/")
async def root():
    logger.info("Health-check endpoint hit.")
    return {"message": "GitHub Repo Evaluator API is running."}

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest):
    logger.info("Received /evaluate request for URL: %s", request.github_url)

    username = extract_username(str(request.github_url))

    if not username:
        logger.warning("Invalid GitHub URL provided: %s", request.github_url)
        raise HTTPException(status_code=400, detail="Could not extract a valid GitHub username from the URL.")

    logger.info("Extracted username: %s", username)

    try:
        repos = await get_user_repos(username)
    except Exception as e:
        logger.error("Error fetching repos for %s: %s", username, str(e))
        raise HTTPException(status_code=502, detail="Failed to fetch repositories from GitHub.")

    if not repos:
        logger.warning("No public repositories found for user: %s", username)
        raise HTTPException(
            status_code=404,
            detail=f"No public repositories found for '{username}'.",
        )

    logger.info("Found %d repos to evaluate for user: %s", len(repos), username)

    try:
        result = await evaluate_repos(username, repos)
    except Exception as e:
        logger.error("Error evaluating repos for %s: %s", username, str(e))
        raise HTTPException(status_code=500, detail="Failed to evaluate repositories.")

    logger.info(
        "Evaluation complete for %s | overall_score=%.2f",
        username,
        result.get("overall_score", 0),
    )

    report_path = save_report(username, result)
    logger.info("Report saved at: %s", report_path)

    return EvaluateResponse(
        username=username,
        overall_score=result["overall_score"],
        report=report_path,
        repos=result.get("repos", [])
    )
