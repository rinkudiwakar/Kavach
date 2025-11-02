from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Picovoice
    RHINO_ACCESS_KEY: str = os.getenv("RHINO_ACCESS_KEY")
    PORCUPINE_ACCESS_KEY: str = os.getenv("PORCUPINE_ACCESS_KEY")

    RHINO_CONTEXT_PATH: str = os.getenv("RHINO_CONTEXT_PATH")
    PORCUPINE_KEYWORD_PATH: str = os.getenv("PORCUPINE_KEYWORD_PATH")

    # Voice verification settings
    VOICE_MATCH_THRESHOLD: float = float(os.getenv("VOICE_MATCH_THRESHOLD", 0.75))
    VOICE_REFERENCE_DIR: str = os.getenv("VOICE_REFERENCE_DIR")

    # Storage paths
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/voice_samples")
    VOICE_STORAGE_BUCKET: str = os.getenv("VOICE_STORAGE_BUCKET", "voice_samples")

    # Email setup
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASS: str = os.getenv("SMTP_PASS")

    # Testing and fallback
    TEST_EMAIL: str = os.getenv("TEST_EMAIL", "test@example.com")

settings = Settings()
