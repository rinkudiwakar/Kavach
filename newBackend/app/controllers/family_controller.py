from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.verify_pipeline import verify_voice
from werkzeug.exceptions import BadRequest

from ..models.family_admin import FamilyAdmin, Member
from resemblyzer import VoiceEncoder, preprocess_wav
from datetime import datetime
from ..utils.compare_voice import cosine_similarity
import numpy as np
import uuid
import os
import traceback

VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", r"C:\Users\saksh\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")
MONGODB_URI     = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB      = os.getenv("MONGODB_DB", "voice_door_unlock")
MONGODB_COLL    = os.getenv("MONGODB_COLL", "family_admin")

encoder = VoiceEncoder()





from werkzeug.utils import secure_filename


ENROL_DIR = os.path.join("dataset", "enrolment")
ALLOWED_EXTS = {"wav", "mp3", "m4a", "flac", "ogg", "aac"}  # preprocess_wav can handle paths via librosa/soundfile
os.makedirs(ENROL_DIR, exist_ok=True)



def _ext_ok(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

def _collect_audio_files_from_request():
    """
    Accepts:
      - 'audios' / 'audios[]' as a list in form-data
      - or 'audio1', 'audio2', 'audio3' keys
    Returns a list of FileStorage objects (length must be 3) or ([], error_message)
    """
    files = request.files.getlist("audios")
    if not files:
        # Fallback to audio1..audio3
        possible = [request.files.get(f"audio{i}") for i in (1, 2, 3)]
        files = [f for f in possible if f]
    if len(files) != 3:
        return [], "Exactly three audio files are required (use 'audios[]' or 'audio1','audio2','audio3')."
    for f in files:
        if f.filename is None or f.filename.strip() == "":
            return [], "One of the audio files has an empty filename."
        if not _ext_ok(f.filename):
            return [], f"Unsupported file type for '{f.filename}'. Allowed: {', '.join(sorted(ALLOWED_EXTS))}."
    return files, None




@jwt_required()
def add_member():
    try:
        # Identity -> family
        family_id = get_jwt_identity()
        family = FamilyAdmin.objects(id=family_id).first()
        if not family:
            return jsonify({"error": "Family not found"}), 404

        # Validate fields
        name = request.form.get("name")
        if not name or not name.strip():
            return jsonify({"error": "Missing 'name' in form-data"}), 400
        name = name.strip()
        keyword = request.form.get("keyword", "").strip()

        # Enforce exactly 3 files
        files, err = _collect_audio_files_from_request()
        if err:
            return jsonify({"error": err}), 400

        # Create member_id early
        member_id = str(uuid.uuid4())

        # Build member folder: dataset/enrolment/<name_of_the_member>
        member_dir = os.path.join(ENROL_DIR, secure_filename(name))
        os.makedirs(member_dir, exist_ok=True)

        # Save locally and keep relative paths
        saved_paths = []
        for idx, f in enumerate(files, start=1):
            base = secure_filename(f.filename)
            # Make filename unique & ordered
            filename = f"{member_id}_{idx:02d}_{base}"
            full_path = os.path.join(member_dir, filename)
            f.save(full_path)
            saved_paths.append(os.path.relpath(full_path))  # store relative path

        # Compute embeddings for each file, then average
        emb_list = []
        for rel in saved_paths:
            # preprocess_wav can take a path; it handles loading & resampling
            wav = preprocess_wav(rel)
            emb = encoder.embed_utterance(wav)
            emb_list.append(emb)

        import numpy as np
        mean_emb = np.mean(np.vstack(emb_list), axis=0).astype(float).tolist()

        # Create Member object
        new_member = Member(
            member_id=member_id,
            name=name,
            keyword=keyword,
            voice_samples=saved_paths,  # relative file paths we saved
            embedding=mean_emb,
            created_at=datetime.utcnow(),
            last_access=datetime.utcnow(),
        )

        # Append and persist
        family.members.append(new_member)
        family.updated_at = datetime.utcnow()
        family.save()

        print(f"[INFO] Member added: {new_member.name} ({new_member.member_id})")
        print(f"[INFO] Saved 3 enrolment files under: {member_dir}")

        return jsonify({
            "message": "Member added",
            "member_id": new_member.member_id,
            "voice_samples": new_member.voice_samples
        }), 201

    except Exception as e:
        print("[ERROR] add_member failed:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# def verify():
    # """
    # POST /api/voice/verify
    # Content-Type: multipart/form-data
    # Form field: audio (file)
    # Optional JSON fields (as query params or form fields):
    #   - min_kws_conf (float)
    #   - speaker_threshold (float)
    # """
    # if "audio" not in request.files:
    #     raise BadRequest("Missing file field 'audio' (multipart/form-data).")

    # audio_file = request.files["audio"]
    # audio_bytes = audio_file.read()
    # if not audio_bytes:
    #     raise BadRequest("Empty 'audio' upload.")

    # # Optional overrides from query/form
    # try:
    #     min_kws_conf = float(request.values.get("min_kws_conf", 0.70))
    #     speaker_threshold = float(request.values.get("speaker_threshold", 0.80))
    # except ValueError:
    #     raise BadRequest("min_kws_conf and speaker_threshold must be numbers.")

    # # Optional: custom keywords as comma-separated string
    # # e.g. ?keywords=kawach,kavach
    # keywords_param = request.values.get("keywords")
    # keywords = [k.strip() for k in keywords_param.split(",")] if keywords_param else ["kawach", "kavach"]

    # try:
    #     result = verify_voice(
    #         audio=audio_bytes,
    #         vosk_model_path=VOSK_MODEL_PATH,
    #         # keywords=keywords,
    #         min_kws_conf=min_kws_conf,
    #         speaker_threshold=speaker_threshold,
    #         mongo_uri=MONGODB_URI,
    #         mongo_db=MONGODB_DB,
    #         mongo_coll=MONGODB_COLL,
    #         # you can also tune aggregation="mean_topk", top_k=3, etc.
    #     )
    #     return jsonify(result), 200
    # except FileNotFoundError as e:
    #     # Typically Vosk model path error
    #     return jsonify({"error": str(e)}), 500
    # except Exception as e:
    #     # Log in real apps; don’t leak internals in prod
    #     return jsonify({"error": f"Voice verification failed: {e}"}), 500
    
    # try:
    #     # family_id = get_jwt_identity()
    #     file = request.files.get("audio")

    #     if not file:
    #         return jsonify({"error": "Audio file missing"}), 400

    #     # Save temporarily for processing
    #     file_path = f"temp_verify_{datetime.now().timestamp()}.wav"
    #     file.save(file_path)

    #     wav = preprocess_wav(file_path)
    #     new_embedding = encoder.embed_utterance(wav)
    #     os.remove(file_path)

    #     family = FamilyAdmin.objects().first()
    #     if not family:
    #         return jsonify({"error": "Family not found"}), 404

    #     for member in family.members:
    #         if not member.embedding:
    #             continue

    #         sim = cosine_similarity(np.array(new_embedding), np.array(member.embedding))
    #         print(f"[DEBUG] Similarity with {member.name}: {sim}")

    #         if sim > 0.75:
    #             member.last_access = datetime.utcnow()
    #             family.save()
    #             print(f"[INFO] Access granted to {member.name} with similarity {sim}")
    #             return jsonify({
    #                 "status": "granted",
    #                 "member": member.name,
    #                 "similarity": sim
    #             }), 200

    #     print("[INFO] Access denied — no match found.")
    #     return jsonify({"status": "denied"}), 200

    # except Exception as e:
    #     print("[ERROR] verify_voice failed:", str(e))
    #     traceback.print_exc()
    #     return jsonify({"error": str(e)}), 500
def verify():
    """
    POST /api/voice/verify
    Body: multipart/form-data with field 'audio' (file)
    Optional: ?min_kws_conf=0.7&speaker_threshold=0.8
    """
    if "audio" not in request.files:
        raise BadRequest("Missing file field 'audio' (multipart/form-data).")

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    if not audio_bytes:
        raise BadRequest("Empty 'audio' upload.")

    try:
        min_kws_conf = float(request.values.get("min_kws_conf", 0.70))
        speaker_threshold = float(request.values.get("speaker_threshold", 0.80))
    except ValueError:
        raise BadRequest("min_kws_conf and speaker_threshold must be numbers.")

    try:
        result = verify_voice(
            audio=audio_bytes,
            vosk_model_path=VOSK_MODEL_PATH,
            min_kws_conf=min_kws_conf,
            speaker_threshold=speaker_threshold,
            # Do NOT pass keywords (your function reads per-member keywords from DB)
            # Do NOT pass mongo_* if verify_voice fetches the single family internally
        )
        return jsonify(result), 200

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Voice verification failed: {e}"}), 500
