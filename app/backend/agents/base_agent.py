import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Agent:
    def __init__(self, name: str, instructions: str, tools: list = None):
        self.name = name
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=instructions,
            tools=tools or []
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=bool(tools))

    def run(self, message: str) -> str:
        response = self.chat.send_message(message)
        return response.text
