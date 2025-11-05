from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta

def generate_jwt(identity: str, expires_hours: int = 24):
    """
    Generate a new JWT access token for a given user/family identity.
    
    Args:
        identity (str): Usually the MongoDB document ID (e.g., FamilyAdmin.id).
        expires_hours (int): Optional number of hours before token expires.

    Returns:
        str: Encoded JWT token.
    """
    expires_delta = timedelta(hours=expires_hours)
    token = create_access_token(identity=identity, expires_delta=expires_delta)
    return token


def decode_jwt(token: str):
    """
    Decode a JWT token (for debugging or internal verification).
    NOTE: Normally, Flask-JWT-Extended handles this automatically during requests.
    """
    try:
        decoded = decode_token(token)
        return decoded
    except Exception as e:
        return {"error": str(e)}
