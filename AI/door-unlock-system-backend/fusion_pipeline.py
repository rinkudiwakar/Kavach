import tempfile
import os
import soundfile as sf
import sounddevice as sd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time
import pickle
from pathlib import Path

from voice_authenticator import VoiceAuthenticator
from rhino import process_wav_for_intent  # Your Rhino utility

# ==========================
# Fusion Pipeline
# ==========================
class FusionPipeline:
    def __init__(self, embed_save_path="saved_embeddings"):
        """
        Initialize FusionPipeline by loading embeddings from local storage.
        """
        self.embed_save_path = Path(embed_save_path)
        self.authenticator = VoiceAuthenticator(enrollment_path=None, embed_save_path=embed_save_path)
        # Load embeddings for all users
        self.authenticator.speaker_embeds = self.load_embeddings_from_local()

    def load_embeddings_from_local(self):
        """
        Load all user embeddings from local saved_embeddings folder.
        Returns a dict: {username: embedding}
        """
        speaker_embeds = {}
        for file in self.embed_save_path.glob("*_embed.pkl"):
            username = file.stem.replace("_embed", "")
            with open(file, "rb") as f:
                speaker_embeds[username] = pickle.load(f)
        return speaker_embeds

    def run(self, audio_input):
        """
        Run fusion pipeline in parallel:
        1. Pass WAV to Rhino for intent recognition
        2. Pass same WAV to Resemblyzer for speaker authentication
        """
        # Preprocess audio to numpy array (16kHz, mono)
        test_wav = self.authenticator.preprocess_audio(audio_input)

        # Save to temporary WAV file for Rhino (16-bit PCM)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            # Convert float32 [-1,1] to int16 for Rhino
            int16_audio = np.int16(np.clip(test_wav, -1, 1) * 32767)
            sf.write(tmp_wav.name, int16_audio, 16000, subtype='PCM_16')
            wav_path_for_rhino = tmp_wav.name

        # Define the two tasks
        def run_rhino():
            return process_wav_for_intent(wav_path_for_rhino)

        def run_voice_auth():
            return self.authenticator.evaluate_similarity(test_wav)

        # Run both in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_rhino = executor.submit(run_rhino)
            future_voice = executor.submit(run_voice_auth)

            rhino_result = future_rhino.result()
            voice_result = future_voice.result()

        # Cleanup temp file
        os.remove(wav_path_for_rhino)

        # Return combined result
        return {"rhino": rhino_result, "voice_auth": voice_result}


# ==========================
# Record audio helper
# ==========================
def record_audio(duration=7, samplerate=16000):
    """
    Record live audio from mic with countdown
    """
    print(f"🎙️ Recording will start in 3 seconds. Get ready...")
    time.sleep(1)
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print(f"Start speaking now! Recording for {duration} seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    print("✅ Recording complete.")
    return recording.flatten()


# ==========================
# Get intent helper
# ==========================
def get_intent(duration=3):
    pipeline = FusionPipeline(embed_save_path="saved_embeddings")
    audio_input = record_audio(duration)
    result = pipeline.run(audio_input)
    return result


# ==========================
# Example usage
# ==========================
if __name__ == "__main__":
    result = get_intent(duration=5)
    print("\n🔹 Fusion Pipeline Result:")
    print(result)
