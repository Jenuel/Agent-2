from google import genai
import json
import os
import re
from app.logger import get_logger

logger = get_logger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def evaluate_readme(readme: str) -> float:
    if not readme:
        logger.debug("evaluate_readme: no README content, returning default score 3.0")
        return 3.0

    logger.debug("evaluate_readme: sending README (%d chars) to LLM", len(readme))

    prompt = f"""
    Evaluate this GitHub README quality. Respond with ONLY a single integer number from 1 to 10. No explanation, no other text.

    README:
    {readme[:3000]}
    """

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL_ID"),
            contents=prompt
        )
        score_text = response.text.strip()
    except Exception as e:
        logger.error("Error during LLM generation: %s", e)
        return 5.0

    logger.debug("evaluate_readme: LLM raw response: %r", score_text)

    match = re.search(r'\d+(\.\d+)?', score_text)
    if match:
        score = min(float(match.group()), 10.0)
        logger.info("evaluate_readme: parsed score=%.2f", score)
        return score

    logger.warning(
        "evaluate_readme: could not parse score from LLM response %r, defaulting to 5.0",
        score_text,
    )
    return 5.0


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def save_report(username: str, result: dict) -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = f"{REPORT_DIR}/{username}.json"

    logger.info("Saving report for '%s' → %s", username, path)

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info("Report saved successfully: %s", path)
    return path
