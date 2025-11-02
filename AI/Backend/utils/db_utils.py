# backend/utils/db_utils.py
from supabase import create_client
from configs.settings import settings
import uuid
from datetime import datetime, timedelta

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# ---- User / profile operations ----
def create_profile_record(name: str, email: str, password: str):
    profile_id = str(uuid.uuid4())
    supabase_client.table("users").insert({
        "id": profile_id,
        "name": name,
        "email": email,
        "password": password,
        "open_count": 0,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return profile_id

def get_profile_by_id(profile_id: str):
    res = supabase_client.table("users").select("*").eq("id", profile_id).limit(1).execute()
    return res.data[0] if res.data else None

# ---- Voice sample metadata ----
def insert_voice_sample_record(profile_id: str, file_path: str, sample_type: str):
    supabase_client.table("voice_samples").insert({
        "id": str(uuid.uuid4()),
        "profile_id": profile_id,
        "file_path": file_path,
        "type": sample_type,
        "uploaded_at": datetime.utcnow().isoformat()
    }).execute()

# ---- Embeddings ----
def insert_embedding(profile_id: str, voice_sample_id: str, vector):
    supabase_client.table("embeddings").insert({
        "id": str(uuid.uuid4()),
        "profile_id": profile_id,
        "voice_sample_id": voice_sample_id,
        "vector": vector,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def get_embeddings_for_profile(profile_id: str, limit: int = 100):
    res = supabase_client.table("embeddings").select("vector,created_at").eq("profile_id", profile_id).order("created_at", desc=True).limit(limit).execute()
    return [r["vector"] for r in (res.data or [])]

# ---- Access logs & attempts ----
def insert_access_log(profile_id: str, intent: str, slot: str, similarity: float, success: bool, message: str):
    supabase_client.table("access_logs").insert({
        "id": str(uuid.uuid4()),
        "profile_id": profile_id,
        "intent_name": intent,
        "slot_name": slot,
        "cosine_similarity": similarity,
        "status": "success" if success else "failed",
        "message": message,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def record_failed_attempt(profile_id: str):
    # upsert into failed_attempts table
    res = supabase_client.table("failed_attempts").select("count, updated_at").eq("profile_id", profile_id).limit(1).execute()
    if not res.data:
        supabase_client.table("failed_attempts").insert({
            "profile_id": profile_id,
            "count": 1,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        return 1
    else:
        current = res.data[0].get("count", 0) + 1
        supabase_client.table("failed_attempts").update({
            "count": current,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("profile_id", profile_id).execute()
        return current

def reset_failed_attempts(profile_id: str):
    supabase_client.table("failed_attempts").update({"count": 0, "updated_at": datetime.utcnow().isoformat()}).eq("profile_id", profile_id).execute()

# ---- System state ----
def set_system_inactive():
    # assume a single row with id=1 exists
    res = supabase_client.table("system_state").select("*").limit(1).execute()
    if res.data:
        supabase_client.table("system_state").update({"active": False, "last_changed": datetime.utcnow().isoformat()}).eq("id", res.data[0]["id"]).execute()
    else:
        supabase_client.table("system_state").insert({"active": False, "last_changed": datetime.utcnow().isoformat()}).execute()

def set_system_active():
    res = supabase_client.table("system_state").select("*").limit(1).execute()
    if res.data:
        supabase_client.table("system_state").update({"active": True, "last_changed": datetime.utcnow().isoformat()}).eq("id", res.data[0]["id"]).execute()
    else:
        supabase_client.table("system_state").insert({"active": True, "last_changed": datetime.utcnow().isoformat()}).execute()

def is_system_active() -> bool:
    res = supabase_client.table("system_state").select("active").limit(1).execute()
    return res.data[0]["active"] if res.data else True

# ---- Email helpers ----
def get_user_email(profile_id: str):
    profile = get_profile_by_id(profile_id)
    return profile.get("email") if profile else None

def get_admin_email():
    return settings.ADMIN_EMAIL
