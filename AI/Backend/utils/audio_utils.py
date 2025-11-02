import io
import os
import numpy as np
import soundfile as sf
import subprocess
from pathlib import Path
from resemblyzer import VoiceEncoder, preprocess_wav
from configs.settings import settings
from .db_utils import supabase_client

# Initialize encoder once (heavy model)
encoder = VoiceEncoder()

# ===============================================
# 1️⃣ DOWNLOAD UTIL
# ===============================================
def download_from_storage(storage_path: str) -> bytes:
    """
    Download a file from Supabase storage and return raw bytes.
    Compatible with various client return types.
    """
    bucket = settings.VOICE_STORAGE_BUCKET
    try:
        res = supabase_client.storage.from_(bucket).download(storage_path)

        # Case 1: Supabase client returns dict
        if isinstance(res, dict) and "data" in res:
            return res["data"]

        # Case 2: Raw bytes (common for newer clients)
        if isinstance(res, (bytes, bytearray)):
            return res

        # Case 3: Object with 'data' attribute
        if hasattr(res, "data"):
            return res.data

        raise ValueError("Unexpected response format from Supabase download.")
    except Exception as e:
        print(f"❌ Error downloading {storage_path}: {e}")
        raise


# ===============================================
# 2️⃣ FFMPEG CONVERSION UTIL
# ===============================================
def _convert_to_wav16(input_path: str, output_path: str):
    """
    Convert input audio to 16kHz mono PCM WAV using ffmpeg.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-vn",
        "-f", "wav",
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ FFmpeg conversion failed for {input_path}: {e}")
        raise


# ===============================================
# 3️⃣ ENSURE LOCAL 16k WAV
# ===============================================
def ensure_wav16_local(storage_path: str) -> str:
    """
    Downloads from Supabase, converts to 16kHz mono WAV, and returns local path.
    Example return: /tmp/voice_samples/16k_username.wav
    """
    raw_bytes = download_from_storage(storage_path)

    tmp_dir = Path(settings.TEMP_DIR)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    tmp_raw = tmp_dir / f"raw_{Path(storage_path).name}"
    tmp_out = tmp_dir / f"16k_{Path(storage_path).stem}.wav"

    try:
        with open(tmp_raw, "wb") as f:
            f.write(raw_bytes)

        _convert_to_wav16(str(tmp_raw), str(tmp_out))
    finally:
        # Safely remove raw file if it exists
        if tmp_raw.exists():
            try:
                tmp_raw.unlink()
            except Exception as e:
                print(f"⚠️ Could not delete temp file {tmp_raw}: {e}")

    return str(tmp_out)


# ===============================================
# 4️⃣ RESEMBLYZER UTILITIES
# ===============================================
def extract_embedding(local_wav_path: str):
    """
    Extract and normalize Resemblyzer embedding.
    Returns: numpy array of shape (256,)
    """
    try:
        wav = preprocess_wav(local_wav_path)
        emb = encoder.embed_utterance(wav)
        emb = emb / np.linalg.norm(emb)
        return emb
    except Exception as e:
        print(f"❌ Error processing {local_wav_path}: {e}")
        raise


def cosine_similarity(a, b):
    """
    Compute cosine similarity between two embedding vectors.
    """
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
