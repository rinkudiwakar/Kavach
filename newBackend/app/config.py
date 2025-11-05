import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    MONGODB_SETTINGS = {
        "db": "voice_door_unlock",
        "host": "mongodb://localhost:27017/voice_door_unlock"
    }
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
