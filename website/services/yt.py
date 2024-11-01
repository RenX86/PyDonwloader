import yt_dlp
import os
from flask import send_file

class YouTubeDownloader:
    def __init__(self):
        self.download_path = 'downloads'
        os.makedirs(self.download_path, exist_ok=True)

    def download_youtube(self, url):
        if not url:
            raise ValueError("URL is required")

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Video')
                ext = info.get('ext', 'mp4')
                filename = f"{video_title}.{ext}"
                filepath = os.path.join(self.download_path, filename)
                
                # Return both success message and file details
                return {
                    'message': f"Successfully downloaded: {video_title}",
                    'filename': filename,
                    'filepath': filepath
                }
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")

    @staticmethod
    def progress_hook(d):
        if d['status'] == 'downloading':
            pass
        elif d['status'] == 'finished':
            print('Download complete')

    def get_video_path(self, filename):
        """Get the full path of a downloaded video"""
        return os.path.join(self.download_path, filename)

# Create a single instance to be used by the application
downloader = YouTubeDownloader()
download_youtube = downloader.download_youtube
get_video_path = downloader.get_video_path