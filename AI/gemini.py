import google.generativeai as genai
from AI.base import AIplatform  # Your base class

class Gemini(AIplatform):
    def __init__(self, api_key: str, system_prompt: str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")  # Fixed model name

    def chat(self, prompt: str) -> str:
        try:
            if self.system_prompt:
                full_prompt = f"{self.system_prompt}\n\nUser: {prompt}"
            else:
                full_prompt = prompt
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"