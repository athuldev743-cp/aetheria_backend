from pydantic import BaseModel

# Request model for chat
class ChatRequest(BaseModel):
    prompt: str

# Response model for chat
class ChatResponse(BaseModel):
    response: str
