import uuid, shutil
from pathlib import Path
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from config import Config
from logger import logger
from threading import Timer
import os

class FileManager:
    """Handles file operations with security measures."""
    
    @staticmethod
    def create_temp_folder() -> Path:
        """Create a temporary folder with unique name."""
        temp_folder = Config.TEMP_FOLDER / f"temp_{uuid.uuid4().hex}"
        temp_folder.mkdir(parents=True, exist_ok=True)
        return temp_folder
    
    @staticmethod
    def secure_path(base_path: Path, filename: str) -> Path:
        """Create a secure path that prevents directory traversal."""
        secure_name = secure_filename(filename)
        return base_path / secure_name
    
    @staticmethod
    def validate_file_size(file_path: Path) -> bool:
        """Check if file size is within allowed limits."""
        return file_path.stat().st_size <= Config.MAX_FILE_SIZE
    
    @staticmethod
    def cleanup_file(file_path: Path) -> None:
        """Safely remove a file or directory."""
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error for {file_path}: {str(e)}")

class URLValidator:
    """Validates and processes URLs."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format and scheme."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
        
def delayed_cleanup(file_path, delay=20, download_store=None, file_id=None):
    
    def cleanup():
        try:
            # Delete the file
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file after delay: {file_path}")

            # Remove entry from download_store if specified
            if download_store is not None and file_id is not None:
                download_store.pop(file_id, None)
                logger.debug(f"Removed {file_id} from download store")

            # Check if the parent folder is empty and not DOWNLOAD_FOLDER, then delete
            temp_folder = Path(file_path).parent
            if temp_folder != Config.DOWNLOAD_FOLDER and not any(temp_folder.iterdir()):
                shutil.rmtree(temp_folder)
                logger.debug(f"Deleted empty temporary folder: {temp_folder}")

        except Exception as e:
            logger.error(f"Failed to clean up file or folder: {str(e)}")

    # Start the timer for delayed cleanup
    Timer(delay, cleanup).start()