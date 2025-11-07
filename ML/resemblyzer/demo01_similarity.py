from resemblyzer import preprocess_wav, VoiceEncoder
from demo_utils import *
from itertools import groupby
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# ==========================================================
#  CONFIG
# ==========================================================
encoder = VoiceEncoder()
DATA_PATH = Path("..", "..", "dataset", "enrollment")
MIN_DURATION = 2.0  # seconds

# ==========================================================
#  LOAD & PREPROCESS
# ==========================================================
print("🔹 Loading dataset from:", DATA_PATH.resolve())

wav_fpaths = sorted(DATA_PATH.glob("**/*.wav"))  # sorted for correct grouping
if not wav_fpaths:
    raise ValueError("❌ No .wav files found in enrollment dataset path!")

speaker_wavs = {}
for speaker, wav_group in groupby(wav_fpaths, key=lambda f: f.parent.stem):
    wav_list = []
    for wav_path in wav_group:
        wav = preprocess_wav(wav_path)
        duration = len(wav) / 16000
        if duration < MIN_DURATION:
            print(f"⚠️ Skipping {wav_path.name} ({duration:.2f}s < {MIN_DURATION}s)")
            continue
        wav_list.append(wav)
    if wav_list:
        speaker_wavs[speaker] = wav_list
        print(f"✅ {speaker}: {len(wav_list)} utterances, avg length "
              f"{np.mean([len(w)/16000 for w in wav_list]):.2f}s")

if len(speaker_wavs) < 2:
    raise ValueError("❌ Need at least two speakers to compare!")

# ==========================================================
#  EMBEDDING CALCULATION (FIXED VERSION)
# ==========================================================
print("\n🎙️ Computing embeddings...")

# --- Utterance-level embeddings ---
embeds_a, embeds_b = [], []
for wavs in speaker_wavs.values():
    if len(wavs) == 1:
        # Duplicate if only one utterance
        embeds_a.append(encoder.embed_utterance(wavs[0]))
        embeds_b.append(encoder.embed_utterance(wavs[0]))
    else:
        embeds_a.append(encoder.embed_utterance(wavs[0]))
        embeds_b.append(encoder.embed_utterance(wavs[1]))

embeds_a, embeds_b = np.array(embeds_a), np.array(embeds_b)
print("Shape of utterance embeddings:", embeds_a.shape)

# --- Speaker-level embeddings (FIXED) ---
spk_embeds_a, spk_embeds_b = [], []
for wavs in speaker_wavs.values():
    num_wavs = len(wavs)
    
    if num_wavs == 1:
        # If only one utterance, use it for both embeddings
        embed = encoder.embed_speaker(wavs)
        spk_embeds_a.append(embed)
        spk_embeds_b.append(embed)
    elif num_wavs == 2:
        # Use one for each
        spk_embeds_a.append(encoder.embed_speaker([wavs[0]]))
        spk_embeds_b.append(encoder.embed_speaker([wavs[1]]))
    else:
        # Split normally for 3+ utterances
        half = num_wavs // 2
        spk_embeds_a.append(encoder.embed_speaker(wavs[:half]))
        spk_embeds_b.append(encoder.embed_speaker(wavs[half:]))

spk_embeds_a, spk_embeds_b = np.array(spk_embeds_a), np.array(spk_embeds_b)
print("Shape of speaker embeddings:", spk_embeds_a.shape)

# ==========================================================
#  SIMILARITY MATRICES
# ==========================================================
utt_sim_matrix = np.inner(embeds_a, embeds_b)
spk_sim_matrix = np.inner(spk_embeds_a, spk_embeds_b)

print("\n🔸 Utterance similarity matrix:\n", utt_sim_matrix)
print("\n🔸 Speaker similarity matrix:\n", spk_sim_matrix)

# ==========================================================
#  VISUALIZATION
# ==========================================================
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
labels_a = [f"{spk}-A" for spk in speaker_wavs.keys()]
labels_b = [f"{spk}-B" for spk in speaker_wavs.keys()]
mask = np.eye(len(utt_sim_matrix), dtype=bool)

# ---- Utterance-level similarity ----
plot_similarity_matrix(utt_sim_matrix, labels_a, labels_b, axs[0, 0],
                       "Cross-similarity between utterances\n(speaker_id-utterance_group)")

# ---- Speaker-level similarity ----
plot_similarity_matrix(spk_sim_matrix, labels_a, labels_b, axs[1, 0],
                       "Cross-similarity between speakers\n(speaker_id-utterances_group)")

# ---- Histogram: Utterance ----
same_utt = utt_sim_matrix[mask].flatten()
diff_utt = utt_sim_matrix[~mask].flatten()

axs[0, 1].hist(same_utt, bins=15, alpha=0.7, label="Same speaker", color="skyblue", edgecolor="black")
axs[0, 1].hist(diff_utt, bins=15, alpha=0.7, label="Different speakers", color="orange", edgecolor="black")
axs[0, 1].set_title("Histogram of similarity between utterances")
axs[0, 1].set_xlabel("Cosine similarity")
axs[0, 1].set_ylabel("Count")
axs[0, 1].legend()

# ---- Histogram: Speaker ----
same_spk = spk_sim_matrix[mask].flatten()
diff_spk = spk_sim_matrix[~mask].flatten()

axs[1, 1].hist(same_spk, bins=15, alpha=0.7, label="Same speaker", color="skyblue", edgecolor="black")
axs[1, 1].hist(diff_spk, bins=15, alpha=0.7, label="Different speakers", color="orange", edgecolor="black")
axs[1, 1].set_title("Histogram of similarity between speakers")
axs[1, 1].set_xlabel("Cosine similarity")
axs[1, 1].set_ylabel("Count")
axs[1, 1].legend()

plt.tight_layout()
plt.show()

# ==========================================================
#  THRESHOLD TESTING
# ==========================================================
def find_best_threshold(sim_matrix):
    """Finds the threshold that gives best accuracy."""
    labels = np.eye(sim_matrix.shape[0])  # 1 on diagonal, 0 elsewhere
    scores = sim_matrix.flatten()
    truth = labels.flatten()

    thresholds = np.linspace(0.4, 0.95, 56)  # test range
    best_acc, best_thr = 0, 0

    for t in thresholds:
        preds = (scores >= t).astype(int)
        acc = np.mean(preds == truth)
        if acc > best_acc:
            best_acc, best_thr = acc, t

    return best_thr, best_acc

# Apply to both matrices
utt_thr, utt_acc = find_best_threshold(utt_sim_matrix)
spk_thr, spk_acc = find_best_threshold(spk_sim_matrix)

# ==========================================================
#  RESULTS
# ==========================================================
print("\n🔸 Utterance similarity matrix:")
print(f"   ➤ Best threshold: {utt_thr:.2f}")
print(f"   ➤ Accuracy: {utt_acc:.3f}")

print("\n🔸 Speaker similarity matrix:")
print(f"   ➤ Best threshold: {spk_thr:.2f}")
print(f"   ➤ Accuracy: {spk_acc:.3f}")