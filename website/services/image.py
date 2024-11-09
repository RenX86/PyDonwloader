import os
import subprocess
import logging
from pathlib import Path
import uuid
import shutil
import imghdr
import mimetypes
from logger import logger

def get_file_extension(file_path):
    img_type = imghdr.what(file_path)
    if img_type:
        return f".{img_type}"
    
    _, ext = os.path.splitext(file_path)
    if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return ext
    
    return '.jpg'

def download_image(url):
    temp_download_folder = None
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_download_folder = os.path.join(base_dir, "static", "downloads", f"temp_{uuid.uuid4().hex}")
        os.makedirs(temp_download_folder, exist_ok=True)

        command = ["gallery-dl", "-d", temp_download_folder, url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f"gallery-dl output: {result.stdout}")

        downloaded_files = []
        for root, _, files in os.walk(temp_download_folder):
            for file in files:
                downloaded_files.append(os.path.join(root, file))

        if not downloaded_files:
            return {"status": "error", "message": "No files downloaded"}

        source_file = downloaded_files[0]
        original_name = os.path.basename(source_file)
        file_extension = get_file_extension(source_file)
        final_filename = f"{uuid.uuid4().hex}{file_extension}"
        final_path = os.path.join(base_dir, "static", "downloads", final_filename)

        shutil.move(source_file, final_path)
        Path(final_path).chmod(0o644)
        logger.debug(f"Final file path: {final_path}")

        return {
            "status": "success", 
            "file_path": final_path,
            "original_name": original_name
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
        if temp_download_folder and os.path.exists(temp_download_folder):
            shutil.rmtree(temp_download_folder)
            logger.debug(f"Cleaned up temporary folder: {temp_download_folder}")
