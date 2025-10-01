from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from AI.gemini import Gemini
from schemas import ChatResponse

import os
import tempfile
import openai
from dotenv import load_dotenv





# ---- LOAD ENV ---
load_dotenv()  # MUST be called before using os.getenv

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not gemini_api_key or not openai_api_key:
    raise ValueError("GEMINI_API_KEY or OPENAI_API_KEY environment variable not set.")

openai.api_key = openai_api_key

# ---- INIT AI ----
system_prompt_path = "src/prompts/system_prompt.md"
system_prompt = ""
if os.path.exists(system_prompt_path):
    with open(system_prompt_path, "r") as f:
        system_prompt = f.read()

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# ---- FASTAPI ----
app = FastAPI(title="Aetheria AI Backend")

origins = [
    "https://aetheria-ten.vercel.app",
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

        if audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(await audio.read())
                tmp_path = tmp.name

            transcription = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=open(tmp_path, "rb")
            )
            user_text = transcription["text"]
            os.remove(tmp_path)

        elif prompt:
            user_text = prompt

        if not user_text:
            raise HTTPException(status_code=400, detail="No prompt or audio provided.")

        response_text = ai_platform.chat(user_text)
        return ChatResponse(response=response_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
