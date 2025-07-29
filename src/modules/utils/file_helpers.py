"""
File Helper Functions
Utilities for file operations and encoding
"""

import logging
import base64
import uuid
import os
import mimetypes
from datetime import datetime


def generate_document_id():
    """Generate a unique document ID"""
    return str(uuid.uuid4())


def encode_file_to_base64(file_path):
    """Encode a file to base64 string"""
    try:
        with open(file_path, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logging.error(f"Failed to encode file to base64: {e}")
        raise


def decode_base64_to_bytes(base64_string):
    """Decode base64 string to bytes"""
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        logging.error(f"Failed to decode base64 string: {e}")
        raise


def get_file_info(file_path):
    """Get file information including size, type, and timestamps"""
    try:
        stat_info = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "size_bytes": stat_info.st_size,
            "mime_type": mime_type,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat()
        }
    except Exception as e:
        logging.error(f"Failed to get file info: {e}")
        raise


def validate_file_type(file_path, allowed_extensions=None):
    """Validate file type based on extension"""
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    file_extension = os.path.splitext(file_path)[1].lower()
    is_valid = file_extension in allowed_extensions
    
    if not is_valid:
        logging.warning(f"File type {file_extension} not in allowed types: {allowed_extensions}")
    
    return is_valid


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized


def cleanup_temp_files(file_paths):
    """Clean up temporary files"""
    cleaned_count = 0
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                cleaned_count += 1
                logging.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logging.warning(f"Failed to clean up temp file {file_path}: {e}")
    
    logging.info(f"Cleaned up {cleaned_count} temporary files")
    return cleaned_count
