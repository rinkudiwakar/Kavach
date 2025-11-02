import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_jwt_token(payload, expires_in_minutes=60):
    """Generate a JWT token with expiration."""
    payload['exp'] = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_jwt_token(token):
    """Decode JWT and return payload if valid."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
