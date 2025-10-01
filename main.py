import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

from AI.gemini import Gemini

# Gemini AI agent
system_prompt = "You are Aetheria AI, a helpful and knowledgeable assistant. Provide clear, concise, and accurate responses to user queries."
gemini_ai = Gemini(api_key=GEMINI_API_KEY, system_prompt=system_prompt)

app = FastAPI(title="Aetheria AI Backend")

origins = [
    "https://aetheria-97jv.vercel.app",
    "http://localhost:5173",
    "https://aetheria-backend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "running", "message": "Aetheria AI Backend operational"}

@app.post("/ai-response")
async def ai_response(prompt: str = Form(None), audio: UploadFile = File(None)):
    try:
        user_text = ""

        # ---- AUDIO HANDLING ----
        if audio:
            content = await audio.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty audio file")

            try:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                # Use speech_recognition for audio-to-text
                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    # Adjust for ambient noise and record
                    recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.record(source)
                    user_text = recognizer.recognize_google(audio_data)
                    
            except sr.UnknownValueError:
                raise HTTPException(status_code=400, detail="Could not understand audio")
            except sr.RequestError as e:
                raise HTTPException(status_code=400, detail=f"Speech recognition error: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        # ---- TEXT PROMPT ----
        elif prompt:
            user_text = prompt.strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="No prompt or audio provided.")

        # ---- GENERATE AI RESPONSE ----
        response_text = gemini_ai.chat(user_text)
        return {"response": response_text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))