from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import or_
import jwt
import uuid
import os

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Check uniqueness
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "A user with this username already exists"}), 409
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "A user with this email already exists"}), 409
    
    try:
        user_public_id = str(uuid.uuid4())
        user_storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user_public_id)

        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            public_id=user_public_id,
            storage_path=user_storage_path
        )
        new_user.set_password(data.get('password'))
        
        os.makedirs(user_storage_path, exist_ok=True)
        
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not create user: {str(e)}"}), 500
        
    return jsonify({"message": f"User '{data.get('username')}' created successfully."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_identifier = data.get('login_identifier')
    password = data.get('password')
    
    if not login_identifier or not password:
        return jsonify({"error": "Login identifier and password are required"}), 400

    # Find user by email OR username
    user = User.query.filter(
        or_(User.email == login_identifier, User.username == login_identifier)
    ).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
        
    try:
        access_token = jwt.encode({
            'user_id': user.id, 
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['ACCESS_TOKEN_EXPIRY_HOURS'])
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        refresh_token = jwt.encode({
            'user_id': user.id, 
            'exp': datetime.utcnow() + timedelta(days=current_app.config['REFRESH_TOKEN_EXPIRY_DAYS'])
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
    except Exception as e:
        return jsonify({"error": f"Error generating tokens: {str(e)}"}), 500
        
    return jsonify({
        "message": "Login successful", 
        "access_token": access_token, 
        "refresh_token": refresh_token
    }), 200


@auth_bp.route('/login/google', methods=['POST'])
def login_google():
    data = request.get_json()
    if not data or 'google_token' not in data:
        return jsonify({"error": "Google ID token is required"}), 400
    
    token = data.get('google_token')
    
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            current_app.config['GOOGLE_CLIENT_ID']
        )
        google_user_id = idinfo['sub']
        email = idinfo['email']
    except ValueError as e:
        return jsonify({"error": f"Invalid Google token: {str(e)}"}), 401

    user = User.query.filter_by(google_id=google_user_id).first()

    if not user:
        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            return jsonify({
                "error": "account_exists_with_password",
                "message": "An account with this email already exists. Please sign in with your password to link your Google account."
            }), 409
        
        try:
            # Generate unique username from email
            base_username = email.split('@')[0].lower().replace('.', '').replace('_', '')
            username_candidate = base_username
            counter = 1
            while User.query.filter_by(username=username_candidate).first():
                username_candidate = f"{base_username}{counter}"
                counter += 1

            user_public_id = str(uuid.uuid4())
            user_storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user_public_id)

            user = User(
                username=username_candidate,
                email=email,
                google_id=google_user_id,
                public_id=user_public_id,
                storage_path=user_storage_path
            )
            
            os.makedirs(user_storage_path, exist_ok=True)
            
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Could not create user resources: {str(e)}"}), 500

    try:
        access_token = jwt.encode({
            'user_id': user.id, 
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['ACCESS_TOKEN_EXPIRY_HOURS'])
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        refresh_token = jwt.encode({
            'user_id': user.id, 
            'exp': datetime.utcnow() + timedelta(days=current_app.config['REFRESH_TOKEN_EXPIRY_DAYS'])
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
    except Exception as e:
        return jsonify({"error": f"Error generating tokens: {str(e)}"}), 500

    return jsonify({
        "message": "Google login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        return jsonify({"error": "Refresh token is required"}), 400
    
    token = data.get('refresh_token')
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = payload['user_id']
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token has expired. Please log in again."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token. Please log in again."}), 401
    
    try:
        new_access_token = jwt.encode({
            'user_id': user.id, 
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['ACCESS_TOKEN_EXPIRY_HOURS'])
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
    except Exception as e:
        return jsonify({"error": f"Error generating new access token: {str(e)}"}), 500
    
    return jsonify({"access_token": new_access_token}), 200
