import google.generativeai as genai
from AI.base import AIplatform

class Gemini(AIplatform):
    def __init__(self, api_key: str, system_prompt: str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        genai.configure(api_key=self.api_key)
        
        # Use gemini-1.5-flash - most widely available
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def chat(self, prompt: str) -> str:
        try:
            full_prompt = f"{self.system_prompt}\n\nUser: {prompt}" if self.system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"