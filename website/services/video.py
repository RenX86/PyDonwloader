import yt_dlp
from pathlib import Path
import os

class VideoDownloader:
    def __init__(self):
        # Use Path for cross-platform compatibility
        base_dir = Path(__file__).resolve().parent.parent
        self.download_path = base_dir / 'static' / 'downloads'
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_video(self, url):
        if not url:
            raise ValueError("URL is required")

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video')
                video_ext = info.get('ext', 'mp4')
                video_filepath = os.path.join(self.download_path, f"{video_title}.{video_ext}")
                ydl.download([url])
                return video_filepath, video_title
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")

    @staticmethod
    def progress_hook(d):
        if d['status'] == 'downloading':
            pass
        elif d['status'] == 'finished':
            print('Download complete')

# Create a single instance to be used by the application
downloader = VideoDownloader()
download_video = downloader.download_video