# AI/base.py
from livekit.jwt import AccessToken

def generate_token(api_key: str, api_secret: str, identity: str):
    """
    Generate a LiveKit JWT access token
    """
    token = AccessToken(api_key=api_key, api_secret=api_secret).with_identity(identity).to_jwt()
    return token
