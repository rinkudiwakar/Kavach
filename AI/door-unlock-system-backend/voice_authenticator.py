import os
from pathlib import Path
import pickle
import numpy as np
import soundfile as sf
from resemblyzer import preprocess_wav, VoiceEncoder

try:
    import noisereduce as nr
    USE_NR = True
except ImportError:
    USE_NR = False

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))

class VoiceAuthenticator:
    def __init__(self, enrollment_path, embed_save_path, threshold=SIMILARITY_THRESHOLD):
        self.data_path = Path(enrollment_path)
        self.embed_save_path = Path(embed_save_path)
        self.embed_save_path.mkdir(exist_ok=True)
        self.threshold = threshold
        self.encoder = VoiceEncoder()
        self.speaker_embeds = self.load_or_create_embeddings()

    def load_or_create_embeddings(self):
        speaker_embeds = {}
        for speaker_dir in self.data_path.glob("*"):
            if not speaker_dir.is_dir():
                continue
            embed_file = self.embed_save_path / f"{speaker_dir.stem}_embed.pkl"
            if embed_file.exists():
                with open(embed_file, "rb") as f:
                    spk_embed = pickle.load(f)
            else:
                wavs = [preprocess_wav(f) for f in speaker_dir.glob("*.wav")]
                if USE_NR:
                    wavs = [nr.reduce_noise(y=w, sr=16000) for w in wavs]
                spk_embed = self.encoder.embed_speaker(wavs)
                with open(embed_file, "wb") as f:
                    pickle.dump(spk_embed, f)
            speaker_embeds[speaker_dir.stem] = spk_embed
        return speaker_embeds

    def preprocess_audio(self, audio_input):
        if isinstance(audio_input, str):
            wav, sr = sf.read(audio_input)
        elif isinstance(audio_input, np.ndarray):
            wav = audio_input
            sr = 16000
        else:
            raise ValueError("audio_input must be file path or numpy array")

        if len(wav.shape) > 1:
            wav = np.mean(wav, axis=1)
        if sr != 16000:
            import librosa
            wav = librosa.resample(wav, orig_sr=sr, target_sr=16000)
        if USE_NR:
            wav = nr.reduce_noise(y=wav, sr=16000)
        return wav

    def evaluate_similarity(self, test_wav):
        test_embed = self.encoder.embed_utterance(test_wav)
        scores = {spk: np.inner(test_embed, emb) for spk, emb in self.speaker_embeds.items()}

        # Log all scores for debugging
        # for spk, sc in scores.items():
        #     print(f"[VoiceAuth] {spk}: {sc:.3f}")

        best_match, best_score = max(scores.items(), key=lambda x: x[1])
        mean_score = np.mean(list(scores.values()))
        score_gap = best_score - mean_score

        if best_score >= self.threshold and score_gap >= 0.05:
            return {"result": "granted", "speaker": best_match, "score": best_score}
        else:
            # Mark unknown if below threshold
            return {"result": "denied", "speaker": "unknown", "score": best_score}

# ==============================
# Testing block
# ==============================
# if __name__ == "__main__":
#     import sounddevice as sd
#     import numpy as np

#     print("🔹 Voice Authenticator Test")
#     enrollment_path = "../../dataset/enrollment"
#     embed_save_path = "saved_embeddings"

#     # Initialize the authenticator
#     authenticator = VoiceAuthenticator(enrollment_path, embed_save_path)

#     # Ask user for recording duration
#     dur = input("Enter recording duration in seconds (default 7): ").strip()
#     duration = int(dur) if dur.isdigit() else 7

#     print(f"🎙️ Recording will start in 3 seconds. Get ready...")
#     import time
#     for i in range(3, 0, -1):
#         print(f"{i}...")
#         time.sleep(1)
#     print(f"Start speaking now! Recording for {duration} seconds...")

#     # Record audio
#     recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
#     sd.wait()
#     recording = recording.flatten()
#     print("✅ Recording complete.")

#     # Preprocess and evaluate
#     test_wav = authenticator.preprocess_audio(recording)
#     result = authenticator.evaluate_similarity(test_wav)

#     print("\n🔹 Voice Authentication Result:")
#     print(result)

#     # Optional: print all scores
#     print("\n🔹 Debug: Similarity scores with enrolled speakers:")
#     test_embed = authenticator.encoder.embed_utterance(test_wav)
#     scores = {spk: np.inner(test_embed, emb) for spk, emb in authenticator.speaker_embeds.items()}
#     for spk, sc in scores.items():
#         print(f"{spk}: {sc:.3f}")

