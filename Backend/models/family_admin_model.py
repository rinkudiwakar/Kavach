from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
from bson import ObjectId
import uuid

bcrypt = Bcrypt()

def create_family_admin(db, family_name, admin_name, email, password):
    """Register a new family admin with an empty members list."""
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    family = {
        "family_name": family_name,
        "admin": {
            "name": admin_name,
            "email": email,
            "password": hashed_pw,
            "created_at": datetime.now(timezone.utc)
        },
        "members": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    result = db.families.insert_one(family)
    return result.inserted_id


def find_family_by_admin_email(db, email):
    """Find a family by admin email."""
    return db.families.find_one({"admin.email": email})


def add_member(db, family_id, name, keyword, embedding=None):
    """Add a member to the family's members array."""
    member = {
        "member_id": str(uuid.uuid4()),
        "name": name,
        "keyword": keyword,
        "voice_samples": [],
        "embedding": embedding,
        "created_at": datetime.now(timezone.utc)
    }

    db.families.update_one(
        {"_id": ObjectId(family_id)},
        {"$push": {"members": member}, "$set": {"updated_at": datetime.now(timezone.utc)}}
    )
    return member


def add_voice_sample(db, family_id, member_id, file_path, embedding):
    """Add a new voice sample and update embedding for a specific member."""
    db.families.update_one(
        {
            "_id": ObjectId(family_id),
            "members.member_id": member_id
        },
        {
            "$push": {"members.$.voice_samples": file_path},
            "$set": {
                "members.$.embedding": embedding,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )


def get_members(db, family_id):
    """Return all members of a family."""
    family = db.families.find_one({"_id": ObjectId(family_id)})
    return family.get("members", []) if family else []
