import os
import tempfile
import warnings
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai

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
# OpenAI client (v0.28.1) - OLD API
openai.api_key = OPENAI_API_KEY

# Gemini AI agent - BYPASS THE CORRUPTED FILE
SYSTEM_PROMPT_PATH = "src/prompts/system_prompt.md"
system_prompt = "You are Aetheria AI, a helpful and knowledgeable assistant. Provide clear, concise, and accurate responses to user queries."

# Skip file reading completely to avoid Unicode errors
print("Using default system prompt")

gemini_ai = Gemini(api_key=GEMINI_API_KEY, system_prompt=system_prompt)

# ---- FASTAPI INIT ----
app = FastAPI(title="Aetheria AI Backend")

origins = [
    "https://aetheria-97jv.vercel.app",
    "http://localhost:5173",
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

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                content = await audio.read()
                if not content:
                    raise HTTPException(status_code=400, detail="Empty audio file")
                tmp.write(content)
                tmp_path = tmp.name

            try:
                with open(tmp_path, "rb") as audio_file:
                    # OLD OPENAI API FOR WHISPER
                    transcription = openai.Audio.transcribe("whisper-1", audio_file)
                    user_text = transcription["text"]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

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