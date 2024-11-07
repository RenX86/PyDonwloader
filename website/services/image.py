import os
from pathlib import Path
import subprocess
import requests

class ImageDownloader:
    def __init__(self):
        # Use Path for cross-platform compatibility
        self.base_dir = Path(__file__).resolve().parent.parent
        self.download_path = self.base_dir / 'static' / 'downloads'
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_image(self, url):
        if not url:
            raise ValueError("URL is required")
        
        try:
            # Use the gallery-dl CLI to download the image
            image_filepath = os.path.join(self.download_path, f"image_{len(os.listdir(self.download_path))}.jpg")
            subprocess.run(["gallery-dl", "-d", self.download_path, url], check=True)
            
            # Get the filename of the downloaded image
            image_filename = os.path.basename(image_filepath)
            
            print(f"Successfully downloaded image from: {url}")
            return image_filepath, image_filename
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to download image: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")
        
    def fetch(url):
        response = requests.get(url)
        return response.content  # Return the media data as bytes

# Create a single instance to be used by the application
downloader = ImageDownloader()
download_image = downloader.download_image  