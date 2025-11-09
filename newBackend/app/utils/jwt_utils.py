from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    decode_token,
    set_access_cookies,
    unset_jwt_cookies
)
from datetime import timedelta
from flask import jsonify, make_response

# Initialize JWT manager
jwt = JWTManager()


def init_jwt(app):
    """
    Initialize JWT with secure cookie-based configuration.
    """
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # 🔒 Replace with an environment variable in production
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
    app.config["JWT_COOKIE_SECURE"] = False  # True in production (HTTPS)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # optional, enable later for CSRF safety
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    jwt.init_app(app)


def generate_jwt_response(identity: str, family_name: str):
    """
    Create a JWT token, set it in cookies, and return a JSON response.
    """
    token = create_access_token(identity=identity, expires_delta=timedelta(hours=24))

    response = make_response(jsonify({
        "message": "Login successful",
        "family_name": family_name
    }))
    set_access_cookies(response, token)
    return response, 200


def clear_jwt_response():
    """
    Clear the JWT cookie — useful for logout.
    """
    response = make_response(jsonify({"message": "Logout successful"}))
    unset_jwt_cookies(response)
    return response, 200


def decode_jwt(token: str):
    """
    Decode a JWT manually (for debugging or admin-level checks).
    Flask-JWT-Extended normally does this automatically.
    """
    try:
        decoded = decode_token(token)
        return decoded
    except Exception as e:
        return {"error": str(e)}
