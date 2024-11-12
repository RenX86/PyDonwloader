import imghdr
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from config import Config
from utils import FileManager, URLValidator
from logger import logger
import uuid
import shutil

def get_file_extension(file_path: Path) -> str:
    
    # Try to detect image type
    img_type = imghdr.what(str(file_path))
    if img_type and f".{img_type}" in Config.ALLOWED_IMAGE_EXTENSIONS:
        return f".{img_type}"
    
    # Check existing extension
    ext = file_path.suffix.lower()
    if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
        return ext
    
    return '.jpg'  # Default extension

def download_image(url: str) -> Dict[str, Any]:
    
    temp_folder = None
    try:
        # Validate URL
        if not URLValidator.is_valid_url(url):
            return {"status": "error", "message": "Invalid URL format"}
        
        # Create temporary folder
        temp_folder = FileManager.create_temp_folder()
        
        # Download using gallery-dl
        command = ["gallery-dl", "-d", str(temp_folder), url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f"gallery-dl output: {result.stdout}")
        
        # Find downloaded files
        downloaded_files = list(temp_folder.rglob('*'))
        downloaded_files = [f for f in downloaded_files if f.is_file()]
        
        if not downloaded_files:
            return {"status": "error", "message": "No files downloaded"}
        
        source_file = downloaded_files[0]
        
        # Validate file size
        if not FileManager.validate_file_size(source_file):
            return {"status": "error", "message": "File exceeds maximum allowed size"}
        
        # Prepare final path
        file_extension = get_file_extension(source_file)
        final_filename = f"{uuid.uuid4().hex}{file_extension}"
        final_path = FileManager.secure_path(Config.DOWNLOAD_FOLDER, final_filename)
        
        # Move file to final location
        shutil.move(str(source_file), str(final_path))
        final_path.chmod(0o644)
        
        return {
            "status": "success",
            "file_path": str(final_path),
            "original_name": source_file.name
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"gallery-dl error: {e.stderr}")
        return {"status": "error", "message": f"Download failed: {e.stderr}"}
    except PermissionError as e:
        logger.error(f"Permission error: {str(e)}")
        return {"status": "error", "message": f"Permission denied: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    finally:
        if temp_folder:
            FileManager.cleanup_file(temp_folder)
