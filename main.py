# main.py
import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from AI.livekit_ai import LiveKitAI

# Load environment variables - different approach for production
if os.path.exists(".env"):
    load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

# For Render deployment, these will be set in the dashboard
if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET or not LIVEKIT_URL:
    # Don't raise error in production, just log
    print("Warning: LiveKit environment variables not set. Token generation will fail.")

app = FastAPI(title="Aetheria AI Backend")

# CORS - allow all origins in production or specific ones
if os.getenv("RENDER"):  # Render sets this environment variable
    origins = [
        "https://aetheria-97jv.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ]
else:
    origins = ["*"]  # More restrictive in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LiveKit AI - initialize only if credentials are available
if LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
    livekit_ai = LiveKitAI(
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
        room_name="default-room"
    )
else:
    livekit_ai = None

@app.get("/")
async def health_check():
    return {"status": "running", "environment": "production" if os.getenv("RENDER") else "development"}

@app.post("/ai-response")
async def ai_response(prompt: str = Form(None), audio: UploadFile = File(None)):
    try:
        if prompt:
            text_prompt = prompt.strip()
            response_text = f"LiveKit AI received your prompt: {text_prompt}"  # Default response
            
            if livekit_ai:
                response_text = livekit_ai.chat(text_prompt)
            
            return {"response": response_text}
        else:
            raise HTTPException(status_code=400, detail="No prompt provided.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-token")
def get_livekit_token(identity: str):
    if not identity:
        raise HTTPException(status_code=400, detail="Identity required")
    
    if not livekit_ai:
        raise HTTPException(status_code=500, detail="LiveKit credentials not configured")

    token = livekit_ai.generate_token(identity)
    return {"token": token, "url": LIVEKIT_URL}

# ... rest of your endpoints