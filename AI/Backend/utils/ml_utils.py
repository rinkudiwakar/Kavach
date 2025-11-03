import numpy as np
import soundfile as sf
from pathlib import Path
from configs.settings import settings

# Optional: install librosa for resampling if not already
import librosa

# Picovoice SDKs (Porcupine + Rhino)
try:
    import pvporcupine
    from pvrhino import Rhino
    PICOVOICE_AVAILABLE = True
except Exception:
    pvporcupine = None
    Rhino = None
    PICOVOICE_AVAILABLE = False

# Resemblyzer (for speaker verification)
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    import torch
    RESEMBLYZER_AVAILABLE = True
except Exception:
    VoiceEncoder = None
    preprocess_wav = None
    torch = None
    RESEMBLYZER_AVAILABLE = False


# ===============================================
# 1️⃣ HELPER: LOAD & RESAMPLE AUDIO (16kHz mono PCM)
# ===============================================
def load_audio_16k(path):
    """Load audio file and resample to 16kHz mono 16-bit PCM."""
    audio, sr = sf.read(path)
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)  # convert stereo to mono
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = np.int16(audio * 32767)
    return audio


# ===============================================
# 2️⃣ PORCUPINE (Wake Word Detection)
# ===============================================
def init_porcupine_model(keyword_path: str = None):
    """Initialize Porcupine model."""
    if not PICOVOICE_AVAILABLE:
        print("⚠️ Porcupine not installed.")
        return None
    return pvporcupine.create(
        access_key=settings.PORCUPINE_ACCESS_KEY,
        keyword_paths=[keyword_path or settings.PORCUPINE_KEYWORD_PATH]
    )


def porcupine_detect(porcupine_handle, pcm_frame: np.ndarray):
    """Detect wake word in PCM16 audio."""
    if not porcupine_handle:
        energy = float((pcm_frame.astype(float)**2).mean())
        return energy > 1e-5

    frame_length = porcupine_handle.frame_length
    idx = 0
    while idx + frame_length <= len(pcm_frame):
        frame = pcm_frame[idx: idx + frame_length].astype('int16').tolist()
        if porcupine_handle.process(frame) >= 0:
            return True
        idx += frame_length
    return False


# ===============================================
# 3️⃣ RHINO (Intent Recognition)
# ===============================================
def init_rhino(context_path: str = None):
    """Initialize Rhino model."""
    if not PICOVOICE_AVAILABLE:
        print("⚠️ Rhino not installed.")
        return None
    return Rhino(
        access_key=settings.RHINO_ACCESS_KEY,
        context_path=context_path or settings.RHINO_CONTEXT_PATH
    )


def run_rhino_inference(rhino_handle, pcm_frame: np.ndarray):
    """Run Rhino on audio and extract intent."""
    if not rhino_handle:
        return None

    frame_length = rhino_handle.frame_length
    idx = 0
    while idx + frame_length <= len(pcm_frame):
        frame = pcm_frame[idx: idx + frame_length].astype('int16').tolist()
        is_finalized = rhino_handle.process(frame)
        if is_finalized:
            inference = rhino_handle.get_inference()
            if inference.is_understood:
                return {"intent": inference.intent, "slots": inference.slots}
            else:
                return None
        idx += frame_length
    return None


# ===============================================
# 4️⃣ RESEMBLYZER (Speaker Verification)
# ===============================================
encoder = VoiceEncoder() if RESEMBLYZER_AVAILABLE else None


def verify_speaker(sample_path: str, reference_path: str, threshold: float = 0.75) -> bool:
    """
    Compare two audio samples using Resemblyzer.
    Returns True if similarity > threshold.
    """
    if not RESEMBLYZER_AVAILABLE:
        print("⚠️ Resemblyzer not installed.")
        return False

    try:
        wav_sample = preprocess_wav(Path(sample_path))
        wav_ref = preprocess_wav(Path(reference_path))
    except Exception as e:
        print(f"⚠️ Error reading audio: {e}")
        return False

    emb_sample = encoder.embed_utterance(wav_sample)
    emb_ref = encoder.embed_utterance(wav_ref)

    sim = torch.nn.functional.cosine_similarity(
        torch.tensor(emb_sample), torch.tensor(emb_ref), dim=0
    ).item()
    print(f"🔊 Voice similarity: {sim:.3f}")
    return sim >= threshold


# ===============================================
# 5️⃣ CHAIN FUNCTION (Porcupine → Resemblyzer → Rhino)
# ===============================================
def run_full_voice_chain(pcm_audio_path: str, reference_voice_path: str):
    """
    Chain process:
    1. Porcupine detects wake word
    2. Resemblyzer verifies speaker
    3. Rhino extracts intent
    """
    print("🎧 Starting full voice verification chain...")

    # --- Load and preprocess ---
    pcm_data = load_audio_16k(pcm_audio_path)

    # --- Step 1: Wake word detection ---
    porcupine_handle = init_porcupine_model()
    wake_detected = porcupine_detect(porcupine_handle, pcm_data)

    if not wake_detected:
        print("❌ No wake word detected.")
        if porcupine_handle:
            porcupine_handle.delete()
        return {"status": "fail", "reason": "wake_word_not_detected"}

    print("✅ Wake word detected!")

    # --- Step 2: Speaker verification ---
    if not verify_speaker(pcm_audio_path, reference_voice_path, settings.VOICE_MATCH_THRESHOLD):
        print("🚫 Voice mismatch.")
        if porcupine_handle:
            porcupine_handle.delete()
        return {"status": "fail", "reason": "unauthorized_voice"}

    print("✅ Voice verified successfully!")

    # --- Step 3: Intent detection ---
    rhino_handle = init_rhino()
    intent_data = run_rhino_inference(rhino_handle, pcm_data)

    if rhino_handle:
        rhino_handle.delete()
    if porcupine_handle:
        porcupine_handle.delete()

    if intent_data:
        print(f"🧠 Intent recognized: {intent_data}")
        return {
            "status": "success",
            "wake_word": True,
            "voice_verified": True,
            "intent": intent_data.get("intent"),
            "slots": intent_data.get("slots"),
            "action": "door_opened"
        }
    else:
        print("❌ Intent not understood.")
        return {"status": "fail", "reason": "intent_not_understood"}
