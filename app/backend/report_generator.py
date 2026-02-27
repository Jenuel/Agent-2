import google.generativeai as genai
import json
import os
import re

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def evaluate_readme(readme):
    if not readme:
        return 3.0

    prompt = f"""
    Evaluate this GitHub README quality. Respond with ONLY a single integer number from 1 to 10. No explanation, no other text.

    README:
    {readme[:3000]}
    """

    response = model.generate_content(prompt)

    score_text = response.text.strip()

    match = re.search(r'\d+(\.\d+)?', score_text)
    if match:
        return min(float(match.group()), 10.0)

    return 5.0  

REPORT_DIR = "reports"

def save_report(username, result):

    os.makedirs(REPORT_DIR, exist_ok=True)

    path = f"{REPORT_DIR}/{username}.json"

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    return path