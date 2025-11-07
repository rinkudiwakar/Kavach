from mongoengine import Document, EmbeddedDocument, StringField, ListField, FloatField, DateTimeField, EmbeddedDocumentField
from datetime import datetime

class Member(EmbeddedDocument):
    member_id = StringField(required=True)
    name = StringField(required=True)
    keyword = StringField()
    voice_samples = ListField(StringField())
    embedding = ListField(FloatField())
    created_at = DateTimeField(default=datetime.utcnow)
    last_access = DateTimeField()

class Admin(EmbeddedDocument):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class FamilyAdmin(Document):
    family_name = StringField(required=True, unique=True)
    admin = EmbeddedDocumentField(Admin, required=True)
    members = ListField(EmbeddedDocumentField(Member))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
