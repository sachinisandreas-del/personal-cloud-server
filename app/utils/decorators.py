from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Malformed Authorization header"}), 401
        
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], 
                               algorithms=["HS256"])
            user_id = payload['user_id']
            current_user = User.query.get(user_id)
            if current_user is None:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid access token"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
