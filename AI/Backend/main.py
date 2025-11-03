# backend/main.py
import os
import uuid
import tempfile
import numpy as np
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from configs.settings import settings
from utils.db_utils import (
    supabase_client,
    create_profile_record,
    insert_voice_sample_record,
    set_system_active,
    set_system_inactive,
    get_profile_by_id
)
from utils.ml_utils import (
    init_porcupine_model,
    porcupine_detect,
    init_rhino,
    run_rhino_inference
)
from utils.audio_utils import extract_embedding, cosine_similarity
from celery_worker import celery_app
from workers.tasks import process_intent_task

# -----------------------------------------------------
# FastAPI setup
# -----------------------------------------------------
app = FastAPI(title="Voice Unlock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.TEMP_DIR, exist_ok=True)

# -----------------------------------------------------
# PROFILE CREATION
# -----------------------------------------------------
@app.post("/profiles/create")
def create_profile(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    profile_id = create_profile_record(name=name, email=email, password=password)
    return {"profile_id": profile_id}

# -----------------------------------------------------
# UPLOAD VOICE SAMPLES
# -----------------------------------------------------
@app.post("/profiles/{profile_id}/upload_samples")
async def upload_samples(profile_id: str, sample_type: str = Form(...), files: list[UploadFile] = File(...)):
    profile = get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    stored_paths = []
    for file in files:
        suffix = os.path.splitext(file.filename)[1] or ".wav"
        tmp_name = f"{uuid.uuid4().hex}{suffix}"
        tmp_path = os.path.join(settings.TEMP_DIR, tmp_name)
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        storage_path = f"{profile_id}/{sample_type}/{tmp_name}"
        with open(tmp_path, "rb") as f:
            supabase_client.storage.from_(settings.VOICE_STORAGE_BUCKET).upload(storage_path, f)

        # get public URL
        public_url_res = supabase_client.storage.from_(settings.VOICE_STORAGE_BUCKET).get_public_url(storage_path)
        public_url = public_url_res.get("publicURL") or public_url_res.get("data", {}).get("publicUrl")

        insert_voice_sample_record(profile_id=profile_id, file_path=storage_path, sample_type=sample_type)
        stored_paths.append(storage_path)

        if sample_type in ("enrollment", "wake", "intent"):
            celery_app.send_task("workers.tasks.process_enrollment", args=[profile_id, storage_path, sample_type])

        try:
            os.remove(tmp_path)
        except:
            pass

    return {"uploaded": stored_paths}

# -----------------------------------------------------
# TEST UNLOCK — Porcupine → Resemblyzer → Rhino
# -----------------------------------------------------
@app.post("/test/unlock")
async def test_unlock(profile_id: str = Form(...), file: UploadFile = File(...)):
    """
    Simulate full unlock pipeline:
    1. Detect wake word (Porcupine)
    2. Verify speaker identity (Resemblyzer)
    3. Extract intent (Rhino)
    4. Return unlock decision
    """

    # Save uploaded file temporarily
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=settings.TEMP_DIR)
    tmp_path = tmp_file.name
    tmp_file.write(await file.read())
    tmp_file.flush()
    tmp_file.close()

    # 1️⃣ Load audio
    pcm_data, sr = sf.read(tmp_path)
    if pcm_data.ndim > 1:
        pcm_data = pcm_data[:, 0]
    pcm_data = (pcm_data * 32767).astype(np.int16)

    # 2️⃣ Initialize Porcupine
    porcupine = init_porcupine_model(keyword_path=settings.PORCUPINE_KEYWORD_PATH)
    wake_detected = porcupine_detect(porcupine, pcm_data)
    if not wake_detected:
        return JSONResponse(status_code=403, content={"message": "Wake word not detected"})

    # 3️⃣ Speaker Verification
    profile = get_profile_by_id(profile_id)
    if not profile or "embedding" not in profile:
        raise HTTPException(status_code=404, detail="Profile or embedding not found")

    user_embedding = np.array(profile["embedding"])
    test_embedding = extract_embedding(tmp_path)
    similarity = cosine_similarity(user_embedding, test_embedding)

    if similarity < settings.SPEAKER_SIMILARITY_THRESHOLD:
        return JSONResponse(status_code=403, content={"message": "Speaker not recognized"})

    # 4️⃣ Intent Detection
    rhino = init_rhino(context_path=settings.RHINO_CONTEXT_PATH)
    intent_result = run_rhino_inference(rhino, pcm_data)
    if not intent_result:
        return JSONResponse(status_code=403, content={"message": "Intent not understood"})

    intent = intent_result.get("intent")
    if intent.lower() in ("unlock_door", "open_door", "open"):
        celery_app.send_task("workers.tasks.handle_unlock_attempt_task", args=[profile_id, True])
        return {"status": "success", "message": "Door unlocked", "intent": intent}
    else:
        celery_app.send_task("workers.tasks.handle_unlock_attempt_task", args=[profile_id, False])
        return JSONResponse(status_code=403, content={"message": "Invalid intent"})

# -----------------------------------------------------
# FALLBACK UNLOCK WITH PASSWORD
# -----------------------------------------------------
@app.post("/test/unlock_with_password")
def unlock_with_password(profile_id: str = Form(...), password: str = Form(...)):
    profile = get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("password") == password:
        celery_app.send_task("workers.tasks.record_manual_unlock", args=[profile_id, "password"])
        return {"status": "success", "message": "Door unlocked with password"}
    return JSONResponse(status_code=403, content={"status": "error", "message": "Invalid password"})

# -----------------------------------------------------
# ADMIN CONTROLS
# -----------------------------------------------------
@app.post("/admin/deactivate")
def admin_deactivate():
    set_system_inactive()
    return {"status": "ok", "message": "System deactivated"}

@app.post("/admin/activate")
def admin_activate():
    set_system_active()
    return {"status": "ok", "message": "System activated"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test/task")
def test_task():
    celery_app.send_task("workers.tasks.dummy_task", args=[])
    return {"status": "queued", "message": "Dummy task sent to Celery."}

@app.get("/test/email")
def test_email():
    from utils.email_utils import send_email
    send_email(to_email=settings.TEST_EMAIL, subject="Test Email", body="This is a test.")
    return {"status": "success", "message": f"Email sent to {settings.TEST_EMAIL}"}
