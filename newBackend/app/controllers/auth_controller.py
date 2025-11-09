# controllers/auth_controller.py

from flask import request, jsonify
from ..extensions import bcrypt
from ..models.family_admin import FamilyAdmin, Admin
from ..utils.jwt_utils import generate_jwt_response, clear_jwt_response


def register_admin():
    """
    Register a new family admin.
    Expected JSON payload:
    {
      "family_name": "<string>",
      "admin_name": "<string>",
      "email": "<string>",
      "password": "<string>"
    }
    """
    data = request.get_json() or {}

    # Basic validation
    required = ("family_name", "admin_name", "email", "password")
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Prevent duplicate family names or duplicate admin emails
    if FamilyAdmin.objects(family_name=data["family_name"]).first():
        return jsonify({"error": "Family already exists"}), 400

    if FamilyAdmin.objects(admin__email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    # Hash password and create documents
    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    admin = Admin(name=data["admin_name"], email=data["email"], password=hashed_pw)

    family = FamilyAdmin(family_name=data["family_name"], admin=admin, members=[])
    family.save()

    return jsonify({"message": "Admin registered successfully"}), 201


from flask import request, jsonify, make_response
from flask_bcrypt import check_password_hash
from ..models.family_admin import FamilyAdmin
from ..utils.jwt_utils import generate_jwt_response
from flask_jwt_extended import create_access_token
from datetime import timedelta

def login_admin():
    """
    Authenticate admin and set JWT in an HTTP-only cookie.
    Expected JSON payload:
    {
      "email": "<string>",
      "password": "<string>"
    }
    Returns a response with JWT in both JSON and HTTP-only cookie.
    """
    data = request.get_json() or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    family = FamilyAdmin.objects(admin__email=data["email"]).first()
    if not family:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(family.admin.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(
        identity=str(family.id),
        additional_claims={"family_name": family.family_name},
        expires_delta=timedelta(hours=2)
    )

    # Create response and set JWT in HTTP-only cookie
    response = make_response(jsonify({
        "message": "Login successful",
        "token": access_token,
        "family_name": family.family_name
    }), 200)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,       # Change to True in production (HTTPS)
        samesite="Lax",
        max_age=7200        # 2 hours in seconds
    )

    return response



def logout_admin():
    """
    Clear the JWT cookie to log out the user.
    Frontend should call this endpoint with credentials included.
    """
    return clear_jwt_response()
