# video.py
import os
import logging
from pathlib import Path
import uuid
import yt_dlp
import shutil
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VideoDownloadProgress:
    def __init__(self):
        self.status = "starting"
        self.filename = ""
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.speed = 0
        self.eta = 0
        self.percent = 0

    def __call__(self, d: Dict[str, Any]) -> None:
        if d['status'] == 'downloading':
            self.status = "downloading"
            self.filename = d.get('filename', '')
            self.downloaded_bytes = d.get('downloaded_bytes', 0)
            self.total_bytes = d.get('total_bytes', 0)
            self.speed = d.get('speed', 0)
            self.eta = d.get('eta', 0)
            
            if self.total_bytes:
                self.percent = (self.downloaded_bytes / self.total_bytes) * 100
            
            logger.debug(f"Download progress: {self.percent:.1f}% - Speed: {self.speed/1024:.1f} KB/s - ETA: {self.eta}s")
            
        elif d['status'] == 'finished':
            self.status = "finished"
            logger.debug(f"Download finished: {self.filename}")
        
        elif d['status'] == 'error':
            self.status = "error"
            logger.error(f"Download error: {d.get('error', 'Unknown error')}")

def get_video_info(url: str) -> Dict[str, Any]:
    """Get video information without downloading."""
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
                    if f.get('filesize', 0) > 0  # Only include formats with known filesize
                ]
            }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return {"status": "error", "message": str(e)}

def download_video(url: str, format_id: Optional[str] = None, progress_hooks: Optional[list] = None) -> Dict[str, Any]:
    """
    Download video from URL using yt-dlp.
    
    Args:
        url: The video URL
        format_id: Optional format ID to download specific quality
        progress_hooks: Optional list of progress hook functions
    
    Returns:
        Dict containing status and file information
    """
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
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format_id if format_id else 'best',
            'outtmpl': os.path.join(temp_download_folder, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': progress_hooks if progress_hooks else [],
        }
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            if not os.path.exists(downloaded_file):
                logger.error("Downloaded file not found")
                return {"status": "error", "message": "Downloaded file not found"}
            
            # Create final filename with UUID and original extension
            original_name = os.path.basename(downloaded_file)
            file_extension = os.path.splitext(downloaded_file)[1]
            final_filename = f"{uuid.uuid4().hex}{file_extension}"
            final_path = os.path.join(base_dir, "static", "downloads", final_filename)
            
            # Copy the file to the final location
            shutil.copy2(downloaded_file, final_path)
            
            # Ensure the final file has proper permissions
            Path(final_path).chmod(0o644)
            
            logger.debug(f"Final file path: {final_path}")
            
            return {
                "status": "success",
                "file_path": final_path,
                "original_name": original_name,
                "title": info.get('title', ''),
                "duration": info.get('duration', 0),
                "format": info.get('format', ''),
                "filesize": os.path.getsize(final_path)
            }
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        return {"status": "error", "message": f"Download failed: {str(e)}"}
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