# import sys
# sys.stdout.reconfigure(encoding='utf-8')

# from resemblyzer import preprocess_wav, VoiceEncoder
# from pathlib import Path
# import numpy as np
# import pickle
# import csv
# import os
# import tempfile
# import sounddevice as sd
# import wavio

# # Try to import noise reduction if available
# try:
#     import noisereduce as nr
#     USE_NR = True
# except ImportError:
#     USE_NR = False

# # =========================================================
# #  CONFIGURATION
# # =========================================================
# encoder = VoiceEncoder()
# DATA_PATH = Path("..", "..", "dataset", "enrollment")   # enrolled users
# TEST_PATH = Path("..", "..", "dataset", "test")         # test audios
# EMBED_SAVE_PATH = Path("saved_embeddings")
# EMBED_SAVE_PATH.mkdir(exist_ok=True)

# THRESHOLD = 0.65 # Single threshold for verification
# RESULT_CSV = Path("verification_resultsfinal1.csv")


# # =========================================================
# #  HELPER FUNCTIONS
# # =========================================================
# def load_or_create_embeddings():
#     """Load or compute average embedding per speaker"""
#     speaker_embeds = {}
#     for speaker_dir in DATA_PATH.glob("*"):
#         if not speaker_dir.is_dir():
#             continue

#         embed_file = EMBED_SAVE_PATH / f"{speaker_dir.stem}_embed.pkl"
#         if embed_file.exists():
#             with open(embed_file, "rb") as f:
#                 spk_embed = pickle.load(f)
#             print(f"📂 Loaded saved embedding for {speaker_dir.stem}")
#         else:
#             wavs = [preprocess_wav(f) for f in speaker_dir.glob("*.wav")]
#             if not wavs:
#                 continue
#             embeds = [encoder.embed_utterance(w) for w in wavs]
#             spk_embed = np.mean(embeds, axis=0)
#             with open(embed_file, "wb") as f:
#                 pickle.dump(spk_embed, f)
#             print(f"💾 Saved new embedding for {speaker_dir.stem}")

#         speaker_embeds[speaker_dir.stem] = spk_embed
#     return speaker_embeds


# if RESULT_CSV.exists():
#     os.remove(RESULT_CSV)
#     print(f"🧹 Old result file '{RESULT_CSV}' removed. New session started.")

# def log_result(filename, best_match, best_score, result):
#     """Append verification result to a new CSV file each run."""
#     try:
#         new_file = not RESULT_CSV.exists()
#         with open(RESULT_CSV, "a", newline="", encoding="utf-8") as csvfile:
#             writer = csv.writer(csvfile)
#             if new_file:
#                 writer.writerow(["Test File", "Predicted Speaker", "Similarity Score", "Result"])
#             writer.writerow([filename, best_match, f"{best_score:.3f}", result])
#         print(f"📁 Logged result → {filename}")
#     except Exception as e:
#         print(f"⚠️ Error while writing CSV: {e}")

# def preprocess_audio(file_path):
#     """Load and optionally denoise audio"""
#     wav = preprocess_wav(file_path)
#     if USE_NR:
#         wav = nr.reduce_noise(y=wav, sr=16000)
#     return wav


# def evaluate_similarity(test_wav, speaker_embeds):
#     """Compute cosine similarity and classify"""
#     test_embed = encoder.embed_utterance(test_wav)
#     scores = {spk: np.inner(test_embed, emb) for spk, emb in speaker_embeds.items()}
#     best_match, best_score = max(scores.items(), key=lambda x: x[1])

#     print("\n🔹 Similarity scores:")
#     for spk, sc in scores.items():
#         print(f"   {spk}: {sc:.3f}")

#     if best_score >= THRESHOLD:
#         result = f"✅ Access Granted → {best_match} ({best_score:.3f})"
#     else:
#         result = f"🚫 Access Denied → No match found (max={best_score:.3f})"

#     return result, best_match, best_score


# # =========================================================
# #  VERIFY TEST FILES
# # =========================================================
# def verify_dataset(speaker_embeds):
#     print("\n🎧 Running batch verification on all test files...\n")
#     for test_file in TEST_PATH.glob("*.wav"):
#         print(f"🎙️ Testing: {test_file.name}")
#         test_wav = preprocess_audio(test_file)
#         result, best_match, best_score = evaluate_similarity(test_wav, speaker_embeds)
#         print(result)
#         log_result(test_file.name, best_match, best_score, result)


# # =========================================================
# #  REAL-TIME RECORDING & VERIFY
# # =========================================================
# def record_and_verify(speaker_embeds, duration=7):
#     print(f"\n🎙️ Speak now for authentication ({duration} seconds)...")
#     recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
#     sd.wait()
#     recording = recording.flatten()

#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#         wavio.write(tmp.name, recording, 16000, sampwidth=2)
#         test_wav = preprocess_audio(tmp.name)

#     result, best_match, best_score = evaluate_similarity(test_wav, speaker_embeds)
#     print(f"\n{result}")
#     log_result("Live_Recording", best_match, best_score, result)

#     os.remove(tmp.name)


# # =========================================================
# #  MAIN ENTRY POINT
# # =========================================================
# if __name__ == "__main__":
#     print("🔹 Loading enrolled speaker embeddings...")
#     speaker_embeds = load_or_create_embeddings()
#     if not speaker_embeds:
#         raise ValueError("❌ No enrolled speakers found!")

#     print("\nChoose mode:")
#     print("1️⃣  Test all audios in dataset/test/")
#     print("2️⃣  Record live voice for authentication")

#     choice = input("\nEnter 1 or 2: ").strip()

#     if choice == "1":
#         verify_dataset(speaker_embeds)
#     elif choice == "2":
#         dur = input("Enter recording duration in seconds (default 7): ").strip()
#         duration = int(dur) if dur.isdigit() else 7
#         record_and_verify(speaker_embeds, duration)
#     else:
#         print("⚠️ Invalid choice. Please enter 1 or 2.")


import sys
sys.stdout.reconfigure(encoding='utf-8')

from resemblyzer import preprocess_wav, VoiceEncoder
from pathlib import Path
import numpy as np
import pickle
import csv
import os
import tempfile
import sounddevice as sd
import wavio

# Try to import optional noise reduction (if installed)
try:
    import noisereduce as nr
    USE_NR = True
except ImportError:
    USE_NR = False

# =========================================================
#  CONFIGURATION
# =========================================================
encoder = VoiceEncoder()  # Load Resemblyzer speaker encoder

DATA_PATH = Path("..", "..", "dataset", "enrollment")   # enrolled speakers
TEST_PATH = Path("..", "..", "dataset", "test")         # test audios
EMBED_SAVE_PATH = Path("saved_embeddings1")               # cache embeddings
EMBED_SAVE_PATH.mkdir(exist_ok=True)

THRESHOLD = 0.83 # 🔹 Revised: slightly higher, suitable for embed_speaker()
RESULT_CSV = Path("verification_results2csv")


# =========================================================
#  HELPER FUNCTIONS
# =========================================================
def load_or_create_embeddings():
    """
    Load saved speaker embeddings or create new ones using `encoder.embed_speaker()`
    This gives more robust speaker-level embeddings than averaging utterances.
    """
    speaker_embeds = {}

    for speaker_dir in DATA_PATH.glob("*"):
        if not speaker_dir.is_dir():
            continue

        embed_file = EMBED_SAVE_PATH / f"{speaker_dir.stem}_embed.pkl"

        if embed_file.exists():
            # 🔸 Load previously computed embedding to save time
            with open(embed_file, "rb") as f:
                spk_embed = pickle.load(f)
            print(f"📂 Loaded saved embedding for {speaker_dir.stem}")

        else:
            # 🔹 Compute fresh embedding using all available utterances
            wavs = [preprocess_wav(f) for f in speaker_dir.glob("*.wav")]
            if not wavs:
                continue

            # Optional noise reduction for each wav
            if USE_NR:
                wavs = [nr.reduce_noise(y=w, sr=16000) for w in wavs]

            # 🔸 Use embed_speaker for robust, normalized representation
            spk_embed = encoder.embed_speaker(wavs)

            # Save to disk for reuse
            with open(embed_file, "wb") as f:
                pickle.dump(spk_embed, f)
            print(f"💾 Saved new embedding for {speaker_dir.stem}")

        speaker_embeds[speaker_dir.stem] = spk_embed

    return speaker_embeds


# 🔹 Reset result CSV each session
if RESULT_CSV.exists():
    os.remove(RESULT_CSV)
    print(f"🧹 Old result file '{RESULT_CSV}' removed. New session started.")


def log_result(filename, best_match, best_score, result):
    """Append verification result into CSV."""
    try:
        new_file = not RESULT_CSV.exists()
        with open(RESULT_CSV, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if new_file:
                writer.writerow(["Test File", "Predicted Speaker", "Similarity Score", "Result"])
            writer.writerow([filename, best_match, f"{best_score:.3f}", result])
        print(f"📁 Logged result → {filename}")
    except Exception as e:
        print(f"⚠️ Error while writing CSV: {e}")


def preprocess_audio(file_path):
    """Load and optionally denoise audio."""
    wav = preprocess_wav(file_path)
    if USE_NR:
        wav = nr.reduce_noise(y=wav, sr=16000)
    return wav


# def evaluate_similarity(test_wav, speaker_embeds):
#     """
#     Compute cosine similarity between test embedding and enrolled speakers.
#     Classify using global THRESHOLD.
#     """
#     test_embed = encoder.embed_utterance(test_wav)

#     # 🔹 Compute cosine similarity with all enrolled speakers
#     scores = {spk: np.inner(test_embed, emb) for spk, emb in speaker_embeds.items()}

#     best_match, best_score = max(scores.items(), key=lambda x: x[1])

#     print("\n🔹 Similarity scores:")
#     for spk, sc in scores.items():
#         print(f"   {spk}: {sc:.3f}")

#     # ✅ Decision based on threshold
#     if best_score >= THRESHOLD:
#         result = f"✅ Access Granted → {best_match} ({best_score:.3f})"
#     else:
#         result = f"🚫 Access Denied → No match found (max={best_score:.3f})"

#     return result, best_match, best_score
def evaluate_similarity(test_wav, speaker_embeds):
    """
    Compute cosine similarity between test embedding and enrolled speakers.
    Classify using global THRESHOLD.
    """
    test_embed = encoder.embed_utterance(test_wav)

    # 🔹 Compute cosine similarity with all enrolled speakers
    scores = {spk: np.inner(test_embed, emb) for spk, emb in speaker_embeds.items()}

    best_match, best_score = max(scores.items(), key=lambda x: x[1])

    print("\n🔹 Similarity scores:")
    for spk, sc in scores.items():
        print(f"   {spk}: {sc:.3f}")

    # 🔸 Improved decision logic
    mean_score = np.mean(list(scores.values()))
    score_gap = best_score - mean_score

    if best_score >= THRESHOLD:
        if score_gap < 0.05:
            result = f"🚫 Access Denied (too close scores — possible imposter)"
        else:
            result = f"✅ Access Granted → {best_match} ({best_score:.3f})"
    else:
        result = f"🚫 Access Denied → No match found (max={best_score:.3f})"

    # ✅ Return values properly
    return result, best_match, best_score



# =========================================================
#  VERIFY TEST FILES
# =========================================================
def verify_dataset(speaker_embeds):
    """Run batch verification on all .wav files in dataset/test/"""
    print("\n🎧 Running batch verification on all test files...\n")
    for test_file in TEST_PATH.glob("*.wav"):
        print(f"🎙️ Testing: {test_file.name}")
        test_wav = preprocess_audio(test_file)
        result, best_match, best_score = evaluate_similarity(test_wav, speaker_embeds)
        print(result)
        log_result(test_file.name, best_match, best_score, result)


# =========================================================
#  REAL-TIME RECORDING & VERIFY
# =========================================================
def record_and_verify(speaker_embeds, duration=7):
    """Record voice from mic and verify against enrolled speakers."""
    print(f"\n🎙️ Speak now for authentication ({duration} seconds)...")
    recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
    sd.wait()
    recording = recording.flatten()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wavio.write(tmp.name, recording, 16000, sampwidth=2)
        test_wav = preprocess_audio(tmp.name)

    result, best_match, best_score = evaluate_similarity(test_wav, speaker_embeds)
    print(f"\n{result}")
    log_result("Live_Recording", best_match, best_score, result)

    os.remove(tmp.name)


# =========================================================
#  MAIN ENTRY POINT
# =========================================================
if __name__ == "__main__":
    print("🔹 Loading enrolled speaker embeddings...")
    speaker_embeds = load_or_create_embeddings()
    if not speaker_embeds:
        raise ValueError("❌ No enrolled speakers found!")

    print("\nChoose mode:")
    print("1️⃣  Test all audios in dataset/test/")
    print("2️⃣  Record live voice for authentication")

    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "1":
        verify_dataset(speaker_embeds)
    elif choice == "2":
        dur = input("Enter recording duration in seconds (default 7): ").strip()
        duration = int(dur) if dur.isdigit() else 7
        record_and_verify(speaker_embeds, duration)
    else:
        print("⚠️ Invalid choice. Please enter 1 or 2.")
