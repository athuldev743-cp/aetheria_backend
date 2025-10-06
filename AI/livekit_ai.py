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
        Enhanced AI response without external API calls
        """
        prompt_lower = prompt.lower()
        
        # Enhanced responses for better user experience
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'hola']):
            return "Hello! I'm Aetheria AI, your intelligent assistant powered by LiveKit. How can I help you today? 🌟"
        
        elif 'how are you' in prompt_lower:
            return "I'm functioning perfectly! Ready to assist you with real-time communication, AI conversations, and LiveKit integration. What would you like to explore?"
        
        elif any(word in prompt_lower for word in ['livekit', 'video call', 'audio call']):
            return "LiveKit is an amazing open-source WebRTC platform for real-time audio and video experiences! I can help you generate access tokens, create rooms, and set up real-time communication. Would you like to try a LiveKit feature?"
        
        elif any(word in prompt_lower for word in ['token', 'access', 'auth']):
            return "I can generate LiveKit access tokens for secure room access. Use the token generation feature to get started with real-time communication!"
        
        elif any(word in prompt_lower for word in ['room', 'create room']):
            return f"I can help you create and manage LiveKit rooms! Your current default room is '{self.room_name}'. Want to create a new room or join an existing one?"
        
        elif any(word in prompt_lower for word in ['what can you do', 'help', 'features']):
            return "I can help you with: 🤖 AI conversations, 🎤 Voice interactions, 🎥 LiveKit real-time communication, 🔐 Token generation, 🏠 Room management, and 🔊 Text-to-speech! What would you like to try?"
        
        elif any(word in prompt_lower for word in ['thank', 'thanks']):
            return "You're welcome! I'm glad I could help. Is there anything else you'd like to know or try? 🚀"
        
        elif any(word in prompt_lower for word in ['bye', 'goodbye', 'exit']):
            return "Goodbye! Feel free to return anytime for more AI assistance and real-time communication features. Have a great day! 👋"
        
        elif any(word in prompt_lower for word in ['weather', 'time', 'date']):
            return f"I'm focused on AI communication and LiveKit features. For {prompt_lower.split()[0]} information, you might want to check a dedicated service. But I'd love to help with real-time communication!"
        
        elif any(word in prompt_lower for word in ['love', 'like you']):
            return "I'm here to assist you with AI conversations and real-time communication! Let me know how I can help with LiveKit features or anything else. 💫"
        
        else:
            # For unknown queries, provide helpful guidance
            responses = [
                f"Interesting question about '{prompt}'! I'm specialized in AI communication and LiveKit real-time features. Would you like to try voice chat or explore LiveKit capabilities?",
                f"I understand you're asking about '{prompt}'. My expertise is in real-time communication and AI assistance. I can help you with voice interactions, video calls, or general AI conversations!",
                f"Thanks for sharing that! I'm designed to assist with LiveKit integration and AI conversations. Want to explore real-time communication features or try a different question?",
                f"I'm constantly learning about '{prompt}'. Meanwhile, I can help you with: generating LiveKit tokens, setting up real-time rooms, or having AI-powered conversations!"
            ]
            import random
            return random.choice(responses)

    async def create_room(self):
        """
        Placeholder: real room creation is via LiveKit HTTP API.
        """
        return {
            "room_name": self.room_name, 
            "status": "created",
            "message": "Room created successfully! You can now generate tokens to access this room."
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