from flask import Blueprint
from .controllers.auth_controller import register_admin, login_admin
from .controllers.family_controller import add_member, verify

def register_routes(app):
    auth_bp = Blueprint("auth", __name__)
    family_bp = Blueprint("family", __name__)

    auth_bp.route("/register", methods=["POST"])(register_admin)
    auth_bp.route("/login", methods=["POST"])(login_admin)
    family_bp.route("/add-member", methods=["POST"])(add_member)
    # family_bp.route("/add-voice", methods=["POST"])(add_voice_sample)
    family_bp.route("/verify", methods=["POST"])(verify)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(family_bp, url_prefix="/api/family")
