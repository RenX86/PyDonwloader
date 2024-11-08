import os
import subprocess
import logging
from pathlib import Path
import uuid
import shutil
import imghdr
import mimetypes

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_file_extension(file_path):
    """Determine the file extension based on file content and name."""
    # Try to get extension from file content
    img_type = imghdr.what(file_path)
    if img_type:
        return f".{img_type}"
    
    # If imghdr fails, try to get from original filename
    _, ext = os.path.splitext(file_path)
    if ext and ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        return ext
    
    # Default to .jpg if we can't determine the type
    return '.jpg'

def download_image(url):
    temp_download_folder = None
    try:
        # Get the absolute path to the website package directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create a unique temporary download directory
        temp_download_folder = os.path.join(base_dir, "static", "downloads", f"temp_{uuid.uuid4().hex}")
        os.makedirs(temp_download_folder, exist_ok=True)
        
        # Ensure the directory has proper permissions
        Path(temp_download_folder).chmod(0o755)
        
        logger.debug(f"Temporary download folder: {temp_download_folder}")
        
        # Build the gallery-dl command with the temporary folder
        command = ["gallery-dl", "-d", temp_download_folder, url]
        logger.debug(f"Executing command: {command}")
        
        # Run the gallery-dl command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.debug(f"gallery-dl output: {result.stdout}")
        
        # Check the download folder for new files
        try:
            downloaded_files = []
            # Walk through the temp directory to find all files
            for root, _, files in os.walk(temp_download_folder):
                for file in files:
                    downloaded_files.append(os.path.join(root, file))
            
            logger.debug(f"Found files: {downloaded_files}")
            
            if not downloaded_files:
                return {"status": "error", "message": "No files downloaded"}
            
            # Get the first downloaded file
            source_file = downloaded_files[0]
            original_name = os.path.basename(source_file)
            
            # Get proper file extension
            file_extension = get_file_extension(source_file)
            
            # Create a new filename with the proper extension
            final_filename = f"{uuid.uuid4().hex}{file_extension}"
            final_path = os.path.join(base_dir, "static", "downloads", final_filename)
            
            # Copy the file to the final location
            shutil.copy2(source_file, final_path)
            
            # Ensure the final file has proper permissions
            Path(final_path).chmod(0o644)
            
            logger.debug(f"Final file path: {final_path}")
            
            return {
                "status": "success", 
                "file_path": final_path,
                "original_name": original_name
            }
            
        except Exception as e:
            logger.error(f"Error processing downloaded files: {str(e)}")
            return {"status": "error", "message": f"Error processing files: {str(e)}"}
            
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
        # Clean up temporary download folder
        if temp_download_folder and os.path.exists(temp_download_folder):
            try:
                shutil.rmtree(temp_download_folder)
                logger.debug(f"Cleaned up temporary folder: {temp_download_folder}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary folder: {str(e)}")