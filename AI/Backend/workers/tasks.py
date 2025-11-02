# backend/workers/tasks.py
import os
import numpy as np
import time
from celery_worker import celery_app
from configs.settings import settings
from utils.db_utils import (
    insert_embedding,
    get_embeddings_for_profile,
    insert_access_log,
    record_failed_attempt,
    reset_failed_attempts,
    insert_voice_sample_record,
    supabase_client,
    get_profile_by_id,
    update_open_count
)
from utils.audio_utils import ensure_wav16_local, get_embedding_from_local_wav, cosine_similarity, download_from_storage
from utils.ml_utils import init_porcupine_model, porcupine_detect, init_rhino, run_rhino_inference
from utils.email_utils import alert_intrusion, alert_intent_mismatch, alert_user_failed_attempt

# -----------------------
# Enrollment task
# -----------------------
@celery_app.task(name="workers.tasks.process_enrollment")
def process_enrollment(profile_id: str, storage_path: str, sample_type: str):
    """
    - Downloads uploaded sample from Supabase storage
    - Converts to 16k WAV locally
    - Generates embedding (Resemblyzer)
    - Stores embedding in embeddings table
    """
    try:
        local_wav = ensure_wav16_local(storage_path)
        emb = get_embedding_from_local_wav(local_wav)
        # store embedding in DB
        insert_embedding(profile_id, None, emb.tolist())
    except Exception as e:
        print("Enrollment failed:", e)
    finally:
        try:
            if os.path.exists(local_wav):
                os.remove(local_wav)
        except:
            pass
    return True

# -----------------------
# Intent processing (live test)
# -----------------------
@celery_app.task(name="workers.tasks.process_intent_task")
def process_intent_task(profile_id: str, local_clip_path: str):
    """
    Called when a dashboard test clip is uploaded (contains wakeword + intent).
    Steps:
    1. Run Porcupine on audio to confirm wakeword
    2. Run Rhino to detect intent & slot
    3. Generate embedding and compare with stored embeddings (cosine)
    4. Log result, notify on failures, apply cooldown & escalation
    """
    try:
        # 1) convert local file to 16k WAV if needed (assume it's already .wav but ensure)
        # we can reuse ffmpeg conversion from audio_utils if needed. For now assume local_clip_path is 16k wav.
        audio, sr = None, None
        try:
            import soundfile as sf
            audio, sr = sf.read(local_clip_path, dtype='int16')
            pcm = np.array(audio).flatten()
        except Exception:
            # fallback: try to convert via ensure_wav16_local by uploading to storage then downloading
            # but for simplicity, raise
            raise

        # 2) Porcupine: check wakeword
        # TODO: set keyword_path per-profile if you created per-user keywords. For demo leave None.
        porcupine = init_porcupine_model()  # pass keyword_path if available
        wake_detected = porcupine_detect(porcupine, pcm)
        if not wake_detected:
            insert_access_log(profile_id, None, None, 0.0, False, "wakeword_not_detected")
            # record failure and alerts
            count = record_failed_attempt(profile_id)
            # send user email if needed
            user = get_profile_by_id(profile_id)
            if user and user.get("email"):
                alert_user_failed_attempt(user.get("email"), f"Wake word not detected. Attempt #{count}")
            return {"status": "failed", "reason": "wakeword_not_detected", "attempts": count}

        # 3) Rhino inference
        rhino = init_rhino()  # update if you want per-profile context
        rhino_res = run_rhino_inference(rhino, pcm)
        if not rhino_res:
            insert_access_log(profile_id, None, None, 0.0, False, "intent_not_understood")
            count = record_failed_attempt(profile_id)
            user = get_profile_by_id(profile_id)
            if user and user.get("email"):
                alert_user_failed_attempt(user.get("email"), f"Intent not understood. Attempt #{count}")
            return {"status": "failed", "reason": "intent_not_understood", "attempts": count}

        detected_intent = rhino_res.get("intent")
        detected_slot = rhino_res.get("slots")  # object/dict or string depending on context

        # 4) Embedding + similarity
        # create local wav for embedding if needed; here we already have local_clip_path
        emb = get_embedding_from_local_wav(local_clip_path)
        stored_vecs = get_embeddings_for_profile(profile_id)
        max_sim = 0.0
        if stored_vecs:
            sims = [cosine_similarity(emb, np.array(v)) for v in stored_vecs]
            max_sim = float(max(sims))
        else:
            max_sim = 0.0

        # 5) Decision logic
        threshold = settings.VOICE_MATCH_THRESHOLD
        speaker_ok = max_sim >= threshold

        # retrieve expected intent / slot from DB or profile metadata
        profile = get_profile_by_id(profile_id)
        expected_intent = None
        expected_slot = None
        # if you stored expected intent/slot in profile or intents table, fetch it here
        # TODO: adapt to how you store expected intent per profile
        # For now we will allow any intent if speaker matches

        if speaker_ok:
            # if the voice matches, check intent correctness
            # if expected_intent exists and doesn't equal detected_intent -> intent mismatch
            if expected_intent and detected_intent != expected_intent:
                insert_access_log(profile_id, detected_intent, str(detected_slot), max_sim, False, "intent_mismatch")
                # notify admin & user
                alert_intent_mismatch(profile.get("name", "user"), f"Detected intent: {detected_intent} - Expected: {expected_intent} - sim={max_sim:.3f}")
                count = record_failed_attempt(profile_id)
                return {"status": "failed", "reason": "intent_mismatch", "similarity": max_sim, "attempts": count}
            # success
            insert_access_log(profile_id, detected_intent, str(detected_slot), max_sim, True, "success")
            update_open_count(profile_id)
            reset_failed_attempts(profile_id)
            return {"status": "success", "intent": detected_intent, "slot": detected_slot, "similarity": max_sim}
        else:
            # speaker mismatch
            insert_access_log(profile_id, detected_intent, str(detected_slot), max_sim, False, "voice_mismatch")
            count = record_failed_attempt(profile_id)
            user = get_profile_by_id(profile_id)
            if user and user.get("email"):
                alert_user_failed_attempt(user.get("email"), f"Voice mismatch. Attempt #{count}. similarity={max_sim:.3f}")
            # escalate if too many attempts
            if count >= 5:
                # apply cooldown (sleep) — but don't block worker for long in production; instead store cooldown timestamp
                # For simplicity we will not sleep long here, but we will notify admin and optionally deactivate system
                alert_intrusion(profile.get("name", "user"), f"{profile.get('email')} had {count} failed attempts, last sim={max_sim:.3f}")
                if count >= 7:
                    # auto-deactivate system
                    from utils.db_utils import set_system_inactive
                    set_system_inactive()
            return {"status": "failed", "reason": "voice_mismatch", "similarity": max_sim, "attempts": count}

    except Exception as e:
        print("process_intent_task exception:", e)
        return {"status": "error", "error": str(e)}
    finally:
        # cleanup local file if exists
        try:
            if os.path.exists(local_clip_path):
                os.remove(local_clip_path)
        except:
            pass

# -----------------------
# manual password unlock record
# -----------------------
@celery_app.task(name="workers.tasks.record_manual_unlock")
def record_manual_unlock(profile_id: str, method: str = "password"):
    insert_access_log(profile_id, f"manual_{method}", None, 0.0, True, f"Manual unlock by {method}")
    update_open_count(profile_id)
    reset_failed_attempts(profile_id)
    return True
