from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Enable CORS for Android client
    CORS(app)

    # Load configuration
    from app.config import Config
    app.config.from_object(Config)

    # Initialize database with app
    db.init_app(app)

    # Register blueprints (NO URL PREFIXES to match Android expectations)
    from app.routes import auth_bp, files_bp
    #from app.routes.auth import auth_bp
    #from app.routes.files import files_bp

    app.register_blueprint(auth_bp)      # Auth routes at root level
    app.register_blueprint(files_bp)     # File routes at root level

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
