import os
from typing import Optional, Dict, Any
from pathlib import Path
import uuid
import shutil
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from config import Config
from logger import logger
from urllib.parse import unquote

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
        
