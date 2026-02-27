import google.generativeai as genai
import json
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

REPORT_DIR = "reports"

def save_report(username, result):

    os.makedirs(REPORT_DIR, exist_ok=True)

    path = f"{REPORT_DIR}/{username}.json"

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    return path