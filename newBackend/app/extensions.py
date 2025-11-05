from mongoengine import connect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()

def init_db(app):
    """
    Connect MongoEngine directly without Flask-MongoEngine.
    """
    connect(
        db="voice_door_unlock",
        host="mongodb://localhost:27017/voice_door_unlock"
    )
