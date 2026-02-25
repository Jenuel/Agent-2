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