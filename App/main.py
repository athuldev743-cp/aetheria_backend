from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from App.AI.gemini import Gemini
from App.schemas import ChatResponse
import os
import tempfile
import openai  # Whisper transcription

app = FastAPI(title="Aetheria AI Backend")

# ---- CORS ----
origins = [
    "https://aetheria-ten.vercel.app",  # frontend URL
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load system prompt ----
def load_system_prompt():
    try:
        with open("src/prompts/system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

system_prompt = load_system_prompt()

# ---- Initialize AI ----
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# ---- OpenAI Whisper API Key ----
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
openai.api_key = openai_api_key

# ---- Health check ----
@app.get("/")
async def health_check():
    return {"status": "running", "message": "Aetheria AI Backend is operational"}

# ---- AI Response with optional audio upload ----
@app.post("/ai-response", response_model=ChatResponse)
async def ai_response(prompt: str = Form(None), audio: UploadFile = File(None)):
    try:
        if audio:
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(await audio.read())
                tmp_path = tmp.name

            # Transcribe with Whisper
            transcription = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=open(tmp_path, "rb")
            )
            user_text = transcription["text"]
        elif prompt:
            user_text = prompt
        else:
            raise HTTPException(status_code=400, detail="No prompt or audio provided.")

        # Generate AI response
        response_text = ai_platform.chat(user_text)
        return ChatResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
