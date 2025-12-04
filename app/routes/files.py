from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app.utils import token_required, get_file_type

files_bp = Blueprint('files', __name__)

@files_bp.route('/')
def index():
    return "Personal Cloud Server is running!"


@files_bp.route('/files', methods=['GET'])
@token_required
def list_files(current_user):
    try:
        user_storage_path = current_user.storage_path
        if not os.path.isdir(user_storage_path):
            os.makedirs(user_storage_path, exist_ok=True)
            return jsonify([]), 200
        
        files_metadata = []
        for filename in os.listdir(user_storage_path):
            path = os.path.join(user_storage_path, filename)
            if os.path.isfile(path):
                stat_result = os.stat(path)
                file_info = {
                    "filename": filename,
                    "file_type": get_file_type(filename),
                    "size": stat_result.st_size,
                    "modified_at": datetime.fromtimestamp(stat_result.st_mtime).isoformat() + "Z"
                }
                files_metadata.append(file_info)
        
        files_metadata.sort(key=lambda x: x['filename'].lower())
        return jsonify(files_metadata), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to list files: {str(e)}"}), 500


@files_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    file = request.files['file']
    
    if file:
        original_filename = secure_filename(file.filename)
        user_storage_path = current_user.storage_path
        
        # Handle duplicate filenames
        base_name, extension = os.path.splitext(original_filename)
        final_filename = original_filename
        counter = 1
        
        while os.path.exists(os.path.join(user_storage_path, final_filename)):
            final_filename = f"{base_name}_{counter}{extension}"
            counter += 1
        
        try:
            file_path = os.path.join(user_storage_path, final_filename)
            file.save(file_path)
            
            stat_result = os.stat(file_path)
            file_info = {
                "filename": final_filename,
                "file_type": get_file_type(final_filename),
                "size": stat_result.st_size,
                "modified_at": datetime.fromtimestamp(stat_result.st_mtime).isoformat() + "Z"
            }
            
            return jsonify({
                "message": "File uploaded successfully",
                "file": final_filename
            }), 201
            
        except Exception as e:
            return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file"}), 400


@files_bp.route('/download/<filename>', methods=['GET'])
@token_required
def download_file(current_user, filename):
    try:
        user_storage_path = current_user.storage_path
        return send_from_directory(
            user_storage_path, 
            filename, 
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500


@files_bp.route('/delete/<filename>', methods=['DELETE'])
@token_required
def delete_file(current_user, filename):
    try:
        user_storage_path = current_user.storage_path
        file_path = os.path.join(user_storage_path, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        os.remove(file_path)
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500


@files_bp.route('/rename', methods=['PUT'])
@token_required
def rename_file(current_user):
    data = request.get_json()
    old_filename = data.get('old_filename')
    new_filename = secure_filename(data.get('new_filename'))
    
    if not old_filename or not new_filename:
        return jsonify({"error": "Both old and new filenames are required"}), 400
    
    try:
        user_storage_path = current_user.storage_path
        old_path = os.path.join(user_storage_path, old_filename)
        new_path = os.path.join(user_storage_path, new_filename)
        
        if not os.path.exists(old_path):
            return jsonify({"error": "File not found"}), 404
        
        if os.path.exists(new_path):
            return jsonify({"error": "A file with the new name already exists"}), 409
        
        os.rename(old_path, new_path)
        
        return jsonify({
            "message": "File renamed successfully",
            "old_filename": old_filename,
            "new_filename": new_filename
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to rename file: {str(e)}"}), 500
