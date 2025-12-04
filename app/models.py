from app import db  # Import db from __init__.py
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, 
                          default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    storage_path = db.Column(db.String(255), unique=True, nullable=False)
    
    def set_password(self, password):
        truncated_password = password.encode('utf-8')[:72]
        self.password_hash = pwd_context.hash(truncated_password)
    
    def check_password(self, password):
        if self.password_hash is None:
            return False
        truncated_password = password.encode('utf-8')[:72]
        return pwd_context.verify(truncated_password, self.password_hash)
