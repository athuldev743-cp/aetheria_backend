import os
import tempfile
import warnings
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI  # New OpenAI API

from AI.gemini import Gemini
from schemas import ChatResponse

# ---- IGNORE WARNINGS ----
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---- LOAD ENV ----
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GEMINI_API_KEY or not OPENAI_API_KEY:
    raise ValueError("GEMINI_API_KEY or OPENAI_API_KEY environment variable not set.")

# ---- INIT CLIENTS ----
# OpenAI client (NEW API) with proxy workaround for Render
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except TypeError as e:
    if "proxies" in str(e):
        # Workaround for proxy issues
        import httpx
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(proxies=None)
        )
    else:
        raise

# Gemini AI agent - Use hardcoded prompt for Render
system_prompt = "You are Aetheria AI, a helpful and knowledgeable assistant. Provide clear, concise, and accurate responses to user queries."

gemini_ai = Gemini(api_key=GEMINI_API_KEY, system_prompt=system_prompt)

# ---- FASTAPI INIT ----
app = FastAPI(title="Aetheria AI Backend")

origins = [
    "https://aetheria-97jv.vercel.app",
    "http://localhost:5173",
    "https://your-render-app.onrender.com"  # Add your Render URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- HEALTH CHECK ----
@app.get("/")
async def health_check():
    return {"status": "running", "message": "Aetheria AI Backend operational"}

# ---- AI RESPONSE ----
@app.post("/ai-response", response_model=ChatResponse)
async def ai_response(prompt: str = Form(None), audio: UploadFile = File(None)):
    try:
        user_text = ""

        # ---- AUDIO HANDLING ----
        if audio:
            if not audio.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="Invalid audio file type")

            # For Render, use in-memory processing
            content = await audio.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty audio file")

            try:
                # Use in-memory file-like object
                from io import BytesIO
                audio_file = BytesIO(content)
                audio_file.name = "audio.wav"
                
                transcription = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                user_text = transcription.text
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")

        # ---- TEXT PROMPT ----
        elif prompt:
            user_text = prompt.strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="No prompt or audio provided.")

        # ---- GENERATE AI RESPONSE ----
        response_text = gemini_ai.chat(user_text)
        return ChatResponse(response=response_text)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))