import os
import io
import tempfile
import numpy as np
from supabase import create_client, Client
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.spatial.distance import cosine
import librosa
import soundfile as sf
import os
from dotenv import load_dotenv

# ==========================
# CONFIGURATION
# ==========================

BUCKET_NAME = "voice_samples"
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
encoder = VoiceEncoder()


# ==========================
# STEP 1: UPLOAD TEST AUDIO
# ==========================
def upload_test_audio(file_path: str, user_id: str):
    """Uploads local test audio to Supabase inside users_samples/."""
    file_name = os.path.basename(file_path)
    remote_path = f"users_samples/{user_id}/{file_name}"
    print(f"⬆️ Uploading {remote_path} to Supabase...")

    with open(file_path, "rb") as f:
        res = supabase.storage.from_(BUCKET_NAME).upload(remote_path, f)

    print("✅ Uploaded successfully:", res)
    return remote_path


# ==========================
# STEP 2: DOWNLOAD & CONVERT
# ==========================
def download_and_convert(remote_path: str):
    """Downloads audio from Supabase, saves locally, converts to 16kHz WAV."""
    print(f"⬇️ Downloading {remote_path} from Supabase...")

    data = supabase.storage.from_(BUCKET_NAME).download(remote_path)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

    with open(temp_file.name, "wb") as f:
        f.write(data)

    print(f"✅ File downloaded to {temp_file.name}")

    # Convert audio for model
    wav, sr = librosa.load(temp_file.name, sr=16000)
    converted_file = temp_file.name.replace(".wav", "_converted.wav")
    sf.write(converted_file, wav, sr, subtype="PCM_16")

    print(f"🔄 Converted audio saved as {converted_file}")
    return converted_file


# ==========================
# STEP 3: GENERATE EMBEDDING
# ==========================
def generate_embedding(local_wav_path: str):
    """Generates a normalized embedding using Resemblyzer."""
    wav = preprocess_wav(local_wav_path)
    emb = encoder.embed_utterance(wav)
    emb = emb / np.linalg.norm(emb)
    print(f"🧠 Embedding generated: shape {emb.shape}")
    return emb


# ==========================
# STEP 4: SAVE EMBEDDING TO SUPABASE
# ==========================
def upload_embedding_to_supabase(embedding: np.ndarray, user_id: str):
    """Uploads generated voice embedding to Supabase (as .npy file)."""
    npy_bytes = io.BytesIO()
    np.save(npy_bytes, embedding)
    npy_bytes.seek(0)

    file_path = f"embeddings/{user_id}.npy"
    print(f"⬆️ Uploading embedding to Supabase as {file_path} ...")

    res = supabase.storage.from_(BUCKET_NAME).upload(file_path, npy_bytes)
    print("✅ Embedding uploaded successfully.")
    return file_path


# ==========================
# STEP 5: VERIFY WITH EXISTING EMBEDDINGS
# ==========================
def verify_with_cloud_embeddings(test_embedding: np.ndarray, threshold=0.75):
    """Downloads all embeddings from Supabase and compares similarity."""
    print("☁️ Fetching stored embeddings for verification...")

    files = supabase.storage.from_(BUCKET_NAME).list(path="embeddings")
    if not files:
        print("⚠️ No stored embeddings found in Supabase.")
        return False

    for f in files:
        if f["name"].endswith(".npy"):
            data = supabase.storage.from_(BUCKET_NAME).download(f"embeddings/{f['name']}")
            emb_ref = np.load(io.BytesIO(data))
            similarity = 1 - cosine(test_embedding, emb_ref)

            print(f"🔍 Compared with {f['name']}: Similarity = {similarity:.3f}")
            if similarity > threshold:
                print(f"✅ MATCH FOUND with {f['name']}")
                return True

    print("❌ No voice match found in Supabase.")
    return False


# ==========================
# STEP 6: MAIN TEST PIPELINE
# ==========================
def test_audio_pipeline(local_audio_path: str, user_id="user1"):
    """Full test pipeline: upload audio → process → verify voice."""
    print("\n🚀 Starting Cloud Voice Verification Test...\n")

    # Upload and process
    remote_path = upload_test_audio(local_audio_path, user_id)
    converted_audio = download_and_convert(remote_path)
    test_embedding = generate_embedding(converted_audio)

    # Save embedding in Supabase
    upload_embedding_to_supabase(test_embedding, user_id)

    # Verify with existing embeddings
    result = verify_with_cloud_embeddings(test_embedding)

    if result:
        print("\n🎉 FINAL RESULT: Voice matched successfully! Door can be opened.\n")
    else:
        print("\n🚫 FINAL RESULT: Voice mismatch. Access denied.\n")

    return result


# ==========================
# ENTRY POINT
# ==========================
if __name__ == "__main__":
    local_test_file = "Kavach/AI/Backend\models/references/user1.wav"
    test_audio_pipeline(local_test_file, user_id="test_user")
