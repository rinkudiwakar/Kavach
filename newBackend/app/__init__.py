from flask import Flask
from .extensions import bcrypt, jwt, init_db
from .config import Config
from .routes import register_routes
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow the frontend origin and explicitly permit the Authorization header
    # so the browser will send the Authorization: Bearer <token> header on requests.
    CORS(app,
        origins=["http://localhost:5173"],
        supports_credentials=True,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        allow_headers=["Content-Type", "Authorization"]
    )
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    init_db(app)   # <-- direct mongoengine connect

    register_routes(app)
    return app


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MjMyNDMyNiwianRpIjoiOTVhMDljOWItY2VlZS00ZTBkLTk0ZmUtY2Y5NzhhNDUyNzYzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY5MGFlZTc5NGViYWRlMTIyMDU4ZjA4OSIsIm5iZiI6MTc2MjMyNDMyNiwiY3NyZiI6IjY2ODE3NzIzLTQyNDgtNGUyYi1hNDg1LTQzMzQxMTA4OTM4MyIsImV4cCI6MTc2MjQxMDcyNn0.k5DrFg-Vc9x-K1-z48nzlOoeNRIB_k0ZVbD0QaLV6eo