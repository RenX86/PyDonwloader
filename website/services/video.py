from typing import Dict, Any, Optional, List, Callable
import yt_dlp
from pathlib import Path
import uuid
from config import Config
from utils import FileManager, URLValidator
from logger import logger
import shutil
import time



class VideoDownloadProgress:
    
    def __init__(self):
        self.status: str = "starting"
        self.filename: str = ""
        self.downloaded_bytes: int = 0
        self.total_bytes: int = 1
        self.speed: float = 0
        self.eta: int = 0
        self.percent: float = 0
        self._last_log_time: float = 0
        self._log_interval: float = 1.0  # Log every second
    
    def __call__(self, d: Dict[str, Any]) -> None:
        
        if d['status'] == 'downloading':
            self.status = "downloading"
            self.filename = d.get('filename', '')
            self.downloaded_bytes = d.get('downloaded_bytes', 0) or 0
            self.total_bytes = d.get('total_bytes', 1) or 1
            self.speed = d.get('speed', 0) or 0
            self.eta = d.get('eta', 0) or 0
            
            if self.total_bytes > 0:
                self.percent = (self.downloaded_bytes / self.total_bytes) * 100
            else:
                self.percent = 0
            
            # Rate-limited logging
            current_time = time.time()
            if current_time - self._last_log_time >= self._log_interval:
                logger.debug(
                    f"Download progress: {self.percent:.1f}% - "
                    f"Speed: {self.speed/1024:.1f} KB/s - "
                    f"ETA: {self.eta}s"
                )
                self._last_log_time = current_time

def download_video(
    url: str,
    format_id: Optional[str] = None,
    progress_hooks: Optional[List[Callable]] = None
) -> Dict[str, Any]:
    
    if not URLValidator.is_valid_url(url):
        return {"status": "error", "message": "Invalid URL format"}
    
    try:
        # Prepare download folder
        Config.init_folders()
        temp_folder = FileManager.create_temp_folder()
        
        ydl_opts = {
            'format': format_id if format_id else 'best',
            'outtmpl': str(temp_folder / '%(title)s.%(ext)s'),
            'progress_hooks': progress_hooks or [],
            'ignoreerrors': True,
            'max_filesize': Config.MAX_FILE_SIZE,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = Path(ydl.prepare_filename(info))
            
            if not downloaded_file.is_file():
                return {"status": "error", "message": "Downloaded file not found"}
            
            # Validate file size
            if not FileManager.validate_file_size(downloaded_file):
                return {"status": "error", "message": "File exceeds maximum allowed size"}
            
            # Move to final location
            final_filename = f"{uuid.uuid4().hex}{downloaded_file.suffix}"
            final_path = FileManager.secure_path(Config.DOWNLOAD_FOLDER, final_filename)
            shutil.move(str(downloaded_file), str(final_path))
            
            return {
                "status": "success",
                "file_path": str(final_path),
                "original_name": downloaded_file.name,
                "title": info.get('title', ''),
                "duration": info.get('duration', 0),
            }
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        return {"status": "error", "message": f"Download failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    finally:
        if temp_folder:
            FileManager.cleanup_file(temp_folder)

def get_video_info(url: str) -> Dict[str, Any]:
    
    if not URLValidator.is_valid_url(url):
        return {"status": "error", "message": "Invalid URL format"}
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "status": "success",
                "title": info.get('title', ''),
                "duration": info.get('duration', 0),
                "thumbnail": info.get('thumbnail', ''),
                "formats": [
                    {
                        "format_id": f.get('format_id', ''),
                        "ext": f.get('ext', ''),
                        "resolution": f.get('resolution', 'unknown'),
                        "filesize": f.get('filesize', 0),
                        "format_note": f.get('format_note', '')
                    }
                    for f in info.get('formats', [])
                    if f.get('filesize', 0) > 0
                ]
            }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return {"status": "error", "message": str(e)}