import os
from pathlib import Path
import pickle
from pymongo import MongoClient
import numpy as np
import soundfile as sf
from resemblyzer import preprocess_wav, VoiceEncoder
import time

try:
    import noisereduce as nr
    USE_NR = True
except ImportError:
    USE_NR = False

# -------------------------
# Config
# -------------------------
MONGO_URI = "mongodb://localhost:27017"  # Change to your MongoDB URI
DB_NAME = "voice_door_unlock"
COLLECTION_NAME = "users"
SAVE_PATH = "saved_embeddings"
SAMPLE_RATE = 16000
CHECK_INTERVAL = 10  # seconds

Path(SAVE_PATH).mkdir(exist_ok=True)
encoder = VoiceEncoder()

# -------------------------
# Connect to MongoDB
# -------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def process_user_audio(user):
    username = user.get("username")
    voice_files = user.get("voice_samples", [])

    if not username or not voice_files:
        return

    embed_file_path = os.path.join(SAVE_PATH, f"{username}_embed.pkl")
    # Skip if embedding already exists
    if os.path.exists(embed_file_path):
        return

    print(f"Processing embeddings for user: {username}")

    wavs = []

    for idx, voice_data in enumerate(voice_files):
        # Convert bytes to temp WAV
        temp_wav_path = f"temp_{username}_{idx}.wav"
        with open(temp_wav_path, "wb") as f:
            f.write(voice_data)

        # Preprocess WAV for Resemblyzer
        wav = preprocess_wav(temp_wav_path)
        if USE_NR:
            wav = nr.reduce_noise(y=wav, sr=SAMPLE_RATE)

        wavs.append(wav)
        os.remove(temp_wav_path)

    if wavs:
        speaker_embed = encoder.embed_speaker(wavs)
        with open(embed_file_path, "wb") as f:
            pickle.dump(speaker_embed, f)
        print(f"✅ Saved embedding for {username}")

def update_embeddings_loop():
    print("📌 Starting automatic embedding update service...")
    while True:
        users = collection.find({})
        for user in users:
            process_user_audio(user)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    update_embeddings_loop()
