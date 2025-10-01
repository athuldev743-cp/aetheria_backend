import google.generativeai as genai
from AI.base import AIplatform

class Gemini(AIplatform):
    def __init__(self, api_key: str, system_prompt: str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        genai.configure(api_key=self.api_key)
        
        # Discover available models
        try:
            available_models = genai.list_models()
            print("🔍 Available models:")
            
            generative_models = []
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    generative_models.append(model.name)
                    print(f"   ✅ {model.name}")
            
            if not generative_models:
                raise Exception("No generative models available")
            
            # Try models in order of preference
            preferred_models = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-1.0-pro',
                'models/gemini-pro',
                generative_models[0]  # Use first available as fallback
            ]
            
            for model_name in preferred_models:
                if model_name in generative_models:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"🎯 Using model: {model_name}")
                    break
            else:
                # Use the first available generative model
                self.model = genai.GenerativeModel(generative_models[0])
                print(f"🔄 Using first available model: {generative_models[0]}")
                
        except Exception as e:
            print(f"❌ Model discovery failed: {e}")
            # Fallback to basic model
            self.model = genai.GenerativeModel('models/gemini-pro')
    
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