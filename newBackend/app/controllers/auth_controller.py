from flask import request, jsonify
from ..extensions import bcrypt
from ..models.family_admin import FamilyAdmin, Admin
from ..utils.jwt_utils import generate_jwt
from datetime import datetime

def register_admin():
    data = request.get_json()
    if FamilyAdmin.objects(family_name=data["family_name"]).first():
        return jsonify({"error": "Family already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    admin = Admin(name=data["admin_name"], email=data["email"], password=hashed_pw)

    family = FamilyAdmin(family_name=data["family_name"], admin=admin, members=[])
    family.save()
    return jsonify({"message": "Admin registered successfully"}), 201


def login_admin():
    data = request.get_json()
    family = FamilyAdmin.objects(admin__email=data["email"]).first()

    if not family or not bcrypt.check_password_hash(family.admin.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_jwt(identity=str(family.id))
    return jsonify({"token": token, "family_name": family.family_name})



# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MjY3MTI0MiwianRpIjoiY2UwMTM3NTQtODcyNy00MGQ3LWE5NGUtNmFjNWVkY2M4NTlhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY5MTAzOThiZDc1N2ZhZmUwM2QzMTJhNiIsIm5iZiI6MTc2MjY3MTI0MiwiY3NyZiI6IjU3NjJiMjE2LTY4NWYtNGEwMy05ZTc4LTgyMWY0NjZhZDFjMCIsImV4cCI6MTc2Mjc1NzY0Mn0.0l1-3akNvI0aaNZhmHCEAdtJuUFERYLJIEXB-mArmiU
