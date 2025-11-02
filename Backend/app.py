from flask import Flask, g, request
from pymongo import MongoClient
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key_here"

# MongoDB setup
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['voice_auth']

@app.before_request
def before_request():
    """Attach db to every request context."""
    request.db = db

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
