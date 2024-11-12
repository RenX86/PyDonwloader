from pathlib import Path
from typing import Set
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base directory configuration
    BASE_DIR: Path = Path(__file__).parent.parent.absolute()
    
    # File size limits (in bytes)
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', 1024 * 1024 * 100))  # 100MB default
    MAX_VIDEO_SIZE: int = int(os.getenv('MAX_VIDEO_SIZE', 1024 * 1024 * 500))  # 500MB default
    
    # File storage configuration
    DOWNLOAD_FOLDER: Path = BASE_DIR / "static" / "downloads"
    UPLOAD_FOLDER: Path = BASE_DIR / "static" / "uploads"  # Added this
    PROCESSED_FOLDER: Path = BASE_DIR / "static" / "processed"  # Added this
    TEMP_FOLDER: Path = DOWNLOAD_FOLDER / "temp"
    
    # File cleanup configuration
    CLEANUP_DELAY: int = int(os.getenv('CLEANUP_DELAY', 3600))  # 1 hour default
    MAX_STORAGE_AGE: int = int(os.getenv('MAX_STORAGE_AGE', 86400))  # 24 hours default
    
    # Allowed file types
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    ALLOWED_VIDEO_EXTENSIONS: Set[str] = {'mp4', 'webm', 'mkv', 'avi'}
    
    # API rate limits
    RATE_LIMIT_GENERAL: str = os.getenv('RATE_LIMIT_GENERAL', "100 per minute")
    RATE_LIMIT_DOWNLOAD: str = os.getenv('RATE_LIMIT_DOWNLOAD', "5 per minute")
    
    # Security settings
    URL_SCHEMES: Set[str] = {'http', 'https'}
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', 3))
    
    # Initialize required directories
    @classmethod
    def init_folders(cls):
        """Create necessary folders if they don't exist"""
        folders = [
            cls.UPLOAD_FOLDER,
            cls.PROCESSED_FOLDER,
            cls.DOWNLOAD_FOLDER,
            cls.TEMP_FOLDER
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)