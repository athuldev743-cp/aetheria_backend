import os
import tempfile
import warnings
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
import google.generativeai as genai

from AI.gemini import Gemini
from schemas import ChatResponse  # Make sure your schema is defined

# ---------------- ENV ----------------
load_dotenv()  # Load .env variables

# Optional: ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set environment variables for proxy if needed (optional)
# os.environ["HTTP_PROXY"] = "http://yourproxy:port"
# os.environ["HTTPS_PROXY"] = "http://yourproxy:port"

# Load API keys
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not gemini_api_key or not openai_api_key:
    raise ValueError("GEMINI_API_KEY or OPENAI_API_KEY not set.")

# ---------------- Initialize clients ----------------
# OpenAI client (v2)
openai_client = openai.OpenAI(api_key=openai_api_key)

# Gemini client
system_prompt_path = "src/prompts/system_prompt.md"
system_prompt = ""
if os.path.exists(system_prompt_path):
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
else:
    print(f"Warning: System prompt file not found at {system_prompt_path}")

gemini_client = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# ---------------- FastAPI setup ----------------
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

# ---------------- Health check ----------------
@app.get("/")
async def health_check():
    return {"status": "running", "message": "Aetheria AI Backend operational"}

# ---------------- AI Response ----------------
@app.post("/ai-response", response_model=ChatResponse)
async def ai_response(prompt: str = Form(None), audio: UploadFile = File(None)):
    try:
        user_text = ""

        # --- Audio transcription using OpenAI ---
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
                    transcription = openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                user_text = transcription.text
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        # --- Text prompt ---
        elif prompt:
            user_text = prompt.strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="No prompt or audio provided.")

        # --- Generate response using Gemini ---
        response_text = gemini_client.chat(user_text)

        return ChatResponse(response=response_text)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
