# main.py
import os
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

app = FastAPI(title="Aetheria AI Backend")

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://aetheria-97jv.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LiveKitAI only if credentials are available
try:
    from AI.livekit_ai import LiveKitAI
    if LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        livekit_ai = LiveKitAI(
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
            room_name="default-room"
        )
    else:
        livekit_ai = None
        print("Warning: LiveKit credentials not set")
except ImportError as e:
    print(f"Warning: Could not import LiveKitAI: {e}")
    livekit_ai = None

@app.get("/")
async def health_check():
    return {
        "status": "running", 
        "livekit_configured": livekit_ai is not None,
        "environment": "production" if os.getenv("RENDER") else "development"
    }

@app.post("/ai-response")
async def ai_response(
    prompt: str = Form(None), 
    audio: UploadFile = File(None)  # Fixed: Use = File(None) instead of = File(None))
):
    try:
        if audio:
            # Return a helpful message about audio being disabled
            return {"response": "🎤 Voice messages are currently being upgraded! Please use text input for now. I can still help you with LiveKit tokens, room creation, and AI conversations!"}
        
        elif prompt:
            text_prompt = prompt.strip()
            if livekit_ai:
                response_text = livekit_ai.chat(text_prompt)
            else:
                response_text = f"AI received: {text_prompt} (LiveKit not configured)"
            
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
        raise HTTPException(status_code=500, detail="LiveKit not configured. Check environment variables.")
    
    try:
        token = livekit_ai.generate_token(identity)
        return {"token": token, "url": LIVEKIT_URL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")

@app.get("/test-token")
def test_token(identity: str = "test-user"):
    """Test endpoint to verify token generation works"""
    if not livekit_ai:
        return {
            "success": False,
            "error": "LiveKit not configured",
            "message": "Check LIVEKIT_API_KEY and LIVEKIT_API_SECRET environment variables"
        }
    
    try:
        token = livekit_ai.generate_token(identity)
        return {
            "success": True,
            "token": token,
            "identity": identity,
            "message": "Token generated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Token generation failed"
        }

@app.post("/create-room")
async def create_room():
    if not livekit_ai:
        raise HTTPException(status_code=500, detail="LiveKit not configured")
    
    room = await livekit_ai.create_room()
    return {"room": room}