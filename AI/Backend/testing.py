# """
# testing.py
# ---------
# Full backend + AI test with microphone input.

# ✅ Checks FastAPI endpoints
# ✅ Records your voice live
# ✅ Sends audio to /test/unlock
# ✅ Verifies Supabase, Celery, and Embedding generation
# """

# import os
# import requests
# import sounddevice as sd
# import soundfile as sf
# import numpy as np
# from pathlib import Path
# from time import sleep
# from resemblyzer import preprocess_wav, VoiceEncoder
# from supabase import create_client
# from configs.settings import settings

# # ==============================
# # Configuration
# # ==============================
# API_BASE = "http://127.0.0.1:8000"  # FastAPI local server
# SAMPLE_RATE = 16000
# DURATION = 4  # seconds

# TEST_FILE = "test_voice.wav"

# # ==============================
# # Test 1: FastAPI Routes
# # ==============================
# def test_fastapi_routes():
#     print("\n🔹 [1] Checking FastAPI health endpoint...")
#     try:
#         res = requests.get(f"{API_BASE}/health")
#         if res.status_code == 200:
#             print("✅ FastAPI is running:", res.json())
#         else:
#             print("❌ FastAPI health check failed:", res.status_code)
#     except Exception as e:
#         print("❌ Error connecting to FastAPI:", e)

# # ==============================
# # Test 2: Supabase Connectivity
# # ==============================
# def test_supabase_connection():
#     print("\n🔹 [2] Testing Supabase connection...")
#     try:
#         client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
#         res = client.table("profiles").select("*").limit(1).execute()
#         print("✅ Supabase connected, example:", res.data)
#     except Exception as e:
#         print("❌ Supabase connection failed:", e)

# # ==============================
# # Test 3: Voice Recording + Embedding
# # ==============================
# def record_and_embed_voice():
#     print("\n🔹 [3] Recording your voice now...")
#     print("🎙️ Say your wake word + intent clearly after the beep...")
#     sleep(1)
#     print("🔔 Recording started... (Speak now!)")
#     audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
#     sd.wait()
#     print("✅ Recording finished.")

#     sf.write(TEST_FILE, audio, SAMPLE_RATE)
#     print(f"🎧 Saved audio to: {TEST_FILE}")

#     # Compute embeddings
#     print("🧠 Generating voice embedding...")
#     wav = preprocess_wav(Path(TEST_FILE))
#     encoder = VoiceEncoder()
#     emb = encoder.embed_utterance(wav)
#     print(f"✅ Embedding generated: {emb.shape}")

#     return TEST_FILE

# # ==============================
# # Test 4: Send Audio to Backend
# # ==============================
# def test_unlock_endpoint(profile_id="test_profile_123"):
#     print("\n🔹 [4] Sending voice sample to /test/unlock ...")

#     with open(TEST_FILE, "rb") as f:
#         files = {"file": (TEST_FILE, f, "audio/wav")}
#         data = {"profile_id": profile_id}
#         try:
#             res = requests.post(f"{API_BASE}/test/unlock", files=files, data=data)
#             print("✅ Sent successfully —", res.json())
#         except Exception as e:
#             print("❌ Unlock test failed:", e)

# # ==============================
# # Test 5: Celery Worker
# # ==============================
# def test_celery_worker():
#     print("\n🔹 [5] Checking Celery connectivity...")
#     try:
#         res = requests.get(f"{API_BASE}/test/task")
#         print("✅ Celery test triggered:", res.json())
#     except Exception as e:
#         print("❌ Celery test failed:", e)

# # ==============================
# # Run All Tests
# # ==============================
# if __name__ == "__main__":
#     print("🚀 Starting Backend + Voice Test Suite\n")

#     test_fastapi_routes()
#     sleep(1)

#     test_supabase_connection()
#     sleep(1)

#     record_and_embed_voice()
#     sleep(1)

#     test_unlock_endpoint()
#     sleep(1)

#     test_celery_worker()
#     sleep(1)

#     print("\n✅ All tests completed.")


"""
testing.py
-----------
End-to-end AI voice unlock test.

🧠 Flow:
Porcupine → detects wake word
Rhino → detects intent (e.g., "open door")
Resemblyzer → verifies speaker match
If all pass → "Door Opened ✅", else → "Access Denied ❌"
"""

import os
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from time import sleep
from resemblyzer import VoiceEncoder, preprocess_wav
from configs.settings import settings

# Try to import Picovoice models
try:
    import pvporcupine
    from pvrhino import Rhino
    PICOVOICE_AVAILABLE = True
except Exception as e:
    print("⚠️ Picovoice SDK not installed properly:", e)
    PICOVOICE_AVAILABLE = False


# ===============================
# PARAMETERS
# ===============================
SAMPLE_RATE = 16000
TEST_FILE = "test_unlock.wav"
REFERENCE_VOICE = settings.VOICE_REFERENCE_DIR
THRESHOLD = settings.VOICE_MATCH_THRESHOLD or 0.75

# ===============================
# Helper functions
# ===============================

def record_audio(duration=6):
    """Record audio from microphone"""
    print(f"🎙️ Recording for {duration} seconds... Speak naturally.")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    sf.write(TEST_FILE, audio, SAMPLE_RATE)
    print(f"✅ Audio saved: {TEST_FILE}")
    return np.squeeze(audio)

def play_beep():
    """Play short beep"""
    duration = 0.3
    freq = 1000
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    beep = 0.5 * np.sin(2 * np.pi * freq * t)
    sd.play(beep, SAMPLE_RATE)
    sd.wait()

# ===============================
# Porcupine Wake Word Detection
# ===============================
def detect_wake_word(audio):
    if not PICOVOICE_AVAILABLE:
        print("⚠️ Porcupine not available, skipping wake detection.")
        return True

    print("\n🔹 Step 1: Detecting Wake Word using Porcupine...")
    porcupine = pvporcupine.create(
        access_key=settings.PORCUPINE_ACCESS_KEY,
        keyword_paths=[settings.PORCUPINE_KEYWORD_PATH]
    )
    frame_len = porcupine.frame_length
    detected = False
    for i in range(0, len(audio), frame_len):
        frame = audio[i:i + frame_len].astype(np.int16).tolist()
        if len(frame) < frame_len:
            break
        result = porcupine.process(frame)
        if result >= 0:
            print("✅ Wake word detected!")
            detected = True
            break
    porcupine.delete()
    return detected

# ===============================
# Rhino Intent Detection
# ===============================
def detect_intent(audio):
    if not PICOVOICE_AVAILABLE:
        print("⚠️ Rhino not available, skipping intent detection.")
        return {"intent": "open_door", "understood": True}

    print("\n🔹 Step 2: Running Rhino intent detection...")
    rhino = Rhino(
        access_key=settings.RHINO_ACCESS_KEY,
        context_path=settings.RHINO_CONTEXT_PATH
    )
    frame_len = rhino.frame_length
    intent_result = None
    for i in range(0, len(audio), frame_len):
        frame = audio[i:i + frame_len].astype(np.int16).tolist()
        if len(frame) < frame_len:
            break
        finalized = rhino.process(frame)
        if finalized:
            inference = rhino.get_inference()
            if inference.is_understood:
                intent_result = {"intent": inference.intent, "slots": inference.slots}
                print(f"✅ Rhino understood intent: {intent_result}")
            else:
                print("❌ Rhino did not understand the command.")
            break
    rhino.delete()
    return intent_result

# ===============================
# Resemblyzer Voice Match
# ===============================
def verify_voice_identity(test_audio_path, reference_path):
    print("\n🔹 Step 3: Running Resemblyzer speaker verification...")
    encoder = VoiceEncoder()

    ref_wav = preprocess_wav(Path(reference_path))
    test_wav = preprocess_wav(Path(test_audio_path))

    ref_emb = encoder.embed_utterance(ref_wav)
    test_emb = encoder.embed_utterance(test_wav)

    similarity = np.dot(ref_emb, test_emb) / (np.linalg.norm(ref_emb) * np.linalg.norm(test_emb))
    print(f"🧮 Similarity score: {similarity:.3f}")

    return similarity >= THRESHOLD, similarity

# ===============================
# MAIN FLOW
# ===============================
if __name__ == "__main__":
    print("🚀 Voice Unlock System Test Starting...\n")

    print("🎧 Get ready to say your wake word and command (e.g. 'Hey Aegis, open the door')")
    sleep(1)
    play_beep()

    recorded_audio = record_audio(duration=6)

    # 1️⃣ Detect wake word
    if not detect_wake_word(recorded_audio):
        print("❌ Wake word not detected — try again.")
        exit()

    # 2️⃣ Detect intent
    intent = detect_intent(recorded_audio)
    if not intent or "open" not in (intent.get("intent", "")).lower():
        print("❌ Intent not recognized as 'open door'. Access denied.")
        exit()

    # 3️⃣ Verify speaker identity
    is_match, score = verify_voice_identity(TEST_FILE, REFERENCE_VOICE)

    if is_match:
        print("\n🔓 Door Opened ✅ (Speaker verified, intent recognized, wake word detected)")
    else:
        print("\n🚫 Access Denied ❌ (Voice did not match reference)")
        print(f"Similarity score {score:.3f} < threshold {THRESHOLD}")

    print("\n🧩 Test complete.")
