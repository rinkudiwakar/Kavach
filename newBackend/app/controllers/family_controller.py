from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.family_admin import FamilyAdmin, Member
from resemblyzer import VoiceEncoder, preprocess_wav
from datetime import datetime
from ..utils.compare_voice import cosine_similarity
import numpy as np
import uuid
import os
import traceback

# Initialize the Resemblyzer voice encoder
encoder = VoiceEncoder()

# ----------------------------------------------------------
# ADD MEMBER (Protected Route)
# ----------------------------------------------------------
@jwt_required()  # JWT will now come from the HTTP-only cookie automatically
def add_member():
    try:
        # ✅ Debug: cookies instead of Authorization header
        print("[DEBUG] Cookies received:", request.cookies)

        data = request.get_json()
        family_id = get_jwt_identity()  # Automatically extracted from cookie

        family = FamilyAdmin.objects(id=family_id).first()
        if not family:
            return jsonify({"error": "Family not found"}), 404

        new_member = Member(
            member_id=str(uuid.uuid4()),
            name=data["name"],
            keyword=data.get("keyword", ""),
            voice_samples=[],
            embedding=[]
        )

        family.members.append(new_member)
        family.updated_at = datetime.utcnow()
        family.save()

        print(f"[INFO] Member added: {new_member.name} ({new_member.member_id})")

        return jsonify({
            "message": "Member added successfully",
            "member_id": new_member.member_id
        }), 201

    except Exception as e:
        print("[ERROR] add_member failed:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# ADD VOICE SAMPLE (Protected Route)
# ----------------------------------------------------------
@jwt_required()
def add_voice_sample():
    try:
        family_id = get_jwt_identity()
        member_id = request.form.get("member_id")
        file = request.files.get("audio")

        if not member_id or not file:
            return jsonify({"error": "member_id or audio file missing"}), 400

        family = FamilyAdmin.objects(id=family_id).first()
        if not family:
            return jsonify({"error": "Family not found"}), 404

        # Save uploaded file temporarily
        file_path = f"temp_{member_id}.wav"
        file.save(file_path)
        print(f"[INFO] File saved temporarily at: {file_path}")

        # Process voice embedding
        wav = preprocess_wav(file_path)
        embedding = encoder.embed_utterance(wav).tolist()
        print(f"[INFO] Embedding generated for member: {member_id}")

        # Update the member record
        for member in family.members:
            if member.member_id == member_id:
                member.voice_samples.append(file.filename)
                member.embedding = embedding
                member.last_access = datetime.utcnow()
                break
        else:
            return jsonify({"error": "Member not found"}), 404

        family.save()
        os.remove(file_path)
        print(f"[INFO] Voice sample added for {member_id}")

        return jsonify({"message": "Voice sample added successfully"}), 200

    except Exception as e:
        print("[ERROR] add_voice_sample failed:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------
# VERIFY VOICE (Protected Route)
# ----------------------------------------------------------
@jwt_required()
def verify_voice():
    try:
        family_id = get_jwt_identity()
        file = request.files.get("audio")

        if not file:
            return jsonify({"error": "Audio file missing"}), 400

        # Save temporarily for embedding computation
        file_path = f"temp_verify_{datetime.now().timestamp()}.wav"
        file.save(file_path)

        wav = preprocess_wav(file_path)
        new_embedding = encoder.embed_utterance(wav)
        os.remove(file_path)

        family = FamilyAdmin.objects(id=family_id).first()
        if not family:
            return jsonify({"error": "Family not found"}), 404

        # Compare voice embeddings
        for member in family.members:
            if not member.embedding:
                continue

            sim = cosine_similarity(np.array(new_embedding), np.array(member.embedding))
            print(f"[DEBUG] Similarity with {member.name}: {sim}")

            if sim > 0.75:
                member.last_access = datetime.utcnow()
                family.save()
                print(f"[INFO] Access granted to {member.name} (similarity={sim})")
                return jsonify({
                    "status": "granted",
                    "member": member.name,
                    "similarity": sim
                }), 200

        print("[INFO] Access denied — no match found.")
        return jsonify({"status": "denied"}), 200

    except Exception as e:
        print("[ERROR] verify_voice failed:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
