# AI/livekit_ai.py
import jwt
import time
import uuid
from typing import Dict, Any

class LiveKitAI:
    def __init__(self, api_key: str, api_secret: str, room_name: str = "default-room"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.room_name = room_name

    def generate_token(self, participant_identity: str, name: str = None) -> str:
        """
        Generate JWT token manually for LiveKit access
        """
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        now = int(time.time())
        exp = now + 3600  # 1 hour expiration
        
        payload = {
            "iss": self.api_key,
            "sub": participant_identity,
            "exp": exp,
            "nbf": now,
            "iat": now,
            "jti": f"{participant_identity}-{now}-{uuid.uuid4().hex[:8]}",
            "video": {
                "room": self.room_name,
                "roomJoin": True,
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
                "hidden": False,
                "recorder": False
            }
        }
        
        if name:
            payload["name"] = name
        
        try:
            token = jwt.encode(
                payload, 
                self.api_secret, 
                algorithm="HS256", 
                headers=headers
            )
            return token
        except Exception as e:
            raise Exception(f"Failed to generate token: {str(e)}")

    def chat(self, prompt: str) -> str:
        """
        Enhanced AI response - you can integrate with real AI models here
        """
        # Simple rule-based responses for now
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm your LiveKit AI assistant. How can I help you today?"
        elif "how are you" in prompt_lower:
            return "I'm functioning well! Ready to help you with LiveKit integration and real-time communication."
        elif "livekit" in prompt_lower:
            return "LiveKit is an open-source WebRTC platform for real-time audio and video experiences. I can help you generate tokens and manage rooms!"
        elif "token" in prompt_lower:
            return "I can generate LiveKit access tokens for you. Use the /get-token endpoint with your identity."
        elif "room" in prompt_lower:
            return f"I can help you create and manage LiveKit rooms. Your current room is '{self.room_name}'."
        else:
            return f"Thanks for your message: '{prompt}'. I'm here to help with LiveKit integration and real-time communication features."

    async def create_room(self):
        """
        Placeholder: real room creation is via LiveKit HTTP API.
        In a real implementation, you would call LiveKit's REST API here.
        """
        return {
            "room_name": self.room_name, 
            "status": "created",
            "message": "Room created successfully (placeholder implementation)"
        }

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate and decode a JWT token (for verification)
        """
        try:
            decoded = jwt.decode(
                token, 
                self.api_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            return decoded
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError as e:
            raise Exception(f"Invalid token: {str(e)}")