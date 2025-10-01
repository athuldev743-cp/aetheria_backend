import google.generativeai as genai
from AI.base import AIplatform

class Gemini(AIplatform):
    def __init__(self, api_key: str, system_prompt: str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        genai.configure(api_key=self.api_key)
        
        # Try different model names until we find one that works
        model_names = [
            'gemini-pro',  # Most widely available
            'models/gemini-pro',
            'gemini-1.0-pro',
            'models/gemini-1.0-pro'
        ]
        
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Successfully loaded model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Failed to load {model_name}: {e}")
                continue
        else:
            # If no model works, try to list available models
            try:
                available_models = genai.list_models()
                print("Available models:")
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        print(f"  - {model.name}")
                # Use the first available generative model
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        self.model = genai.GenerativeModel(model.name)
                        print(f"✅ Using available model: {model.name}")
                        break
                else:
                    raise Exception("No generative models available")
            except Exception as e:
                raise Exception(f"Could not load any Gemini model: {e}")
    
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