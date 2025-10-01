import os
from fastapi import FastAPI
from App.AI.gemini import Gemini       # if running uvicorn from AI_#1
from App.schemas import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.github.io"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load system prompt (optional)
def load_system_prompt():
    try:
        with open("src/prompts/system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Initialize AI
ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# Health check
@app.get("/")
async def root():
    return {"message": "API is running"}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response_text = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)
