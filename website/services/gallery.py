import gallery_dl
import os

class GalleryDownloader:
    def __init__(self):
        self.download_path = os.path.abspath('downloads')
        os.makedirs(self.download_path, exist_ok=True)

    def download_gallery(self, url):
        if not url:
            raise ValueError("URL is required")

        try:
            # Change the working directory to downloads folder
            original_dir = os.getcwd()
            os.chdir(self.download_path)

            # Start the download with minimal configuration
            job = gallery_dl.job.Job(url)
            success = job.run()

            # Restore original working directory
            os.chdir(original_dir)

            if success:
                return f"Successfully downloaded gallery from: {url}"
            else:
                raise Exception("Download failed")
        except Exception as e:
            # Make sure we restore the working directory even if there's an error
            if 'original_dir' in locals():
                os.chdir(original_dir)
            raise Exception(f"Failed to download gallery: {str(e)}")

# Create a single instance to be used by the application
downloader = GalleryDownloader()
download_gallery = downloader.download_gallery