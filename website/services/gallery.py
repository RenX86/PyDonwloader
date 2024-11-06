import gallery_dl
import os
from pathlib import Path

class ImageDownloader:
    def __init__(self):
        # Use Path for cross-platform compatibility
        base_dir = Path(__file__).resolve().parent.parent
        self.download_path = base_dir / 'static' / 'downloads'
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_image(self, url):
        if not url:
            raise ValueError("URL is required")
        
        try:
            # Start the download with minimal configuration
            job = gallery_dl.job.Job(url)
            success = job.run()

            if success:
                return f"Successfully downloaded image from: {url}"
            else:
                raise Exception("Download failed")
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")

# Create a single instance to be used by the application
downloader = ImageDownloader()
download_image = downloader.download_image