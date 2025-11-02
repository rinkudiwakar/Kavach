from flask import Blueprint, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from bson import ObjectId
from models.family_admin_model import create_family_admin, find_family_by_admin_email
from utils.jwt_utils import create_jwt_token
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# 🟢 REGISTER FAMILY ADMIN
@auth_bp.route('/register', methods=['POST'])
def register_family():
    data = request.get_json()

    family_name = data.get('family_name')
    admin_name = data.get('admin_name')
    email = data.get('email')
    password = data.get('password')

    if not all([family_name, admin_name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    existing_family = find_family_by_admin_email(request.db, email)
    if existing_family:
        return jsonify({"error": "Admin with this email already exists"}), 409

    family_id = create_family_admin(
        request.db,
        family_name,
        admin_name,
        email,
        password
    )

    token = create_jwt_token({"family_id": str(family_id), "email": email})
    resp = make_response(jsonify({"message": "Family registered successfully"}))
    resp.set_cookie("jwt", token, httponly=True, samesite='Strict')

    return resp, 201


# 🟡 LOGIN
@auth_bp.route('/login', methods=['POST'])
def login_family():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing credentials"}), 400

    family = find_family_by_admin_email(request.db, email)
    if not family:
        return jsonify({"error": "Invalid credentials"}), 401

    stored_pw = family['admin']['password']
    if not bcrypt.check_password_hash(stored_pw, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_jwt_token({"family_id": str(family["_id"]), "email": email})
    resp = make_response(jsonify({"message": "Login successful"}))
    resp.set_cookie("jwt", token, httponly=True, samesite='Strict')

    return resp, 200
