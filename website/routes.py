from flask import Blueprint, request, jsonify, render_template, send_from_directory, send_file
import os 
import tempfile
from pathlib import Path
from website.services.yt import VideoDownloader
from website.services.gallery import ImageDownloader

links = Blueprint('links', __name__)

@links.route("/")
def index():
    # Get list of files in download directory
    download_path = Path(__file__).resolve().parent / 'static' / 'downloads'
    files = [f.name for f in download_path.glob('*') if f.is_file()]
    return render_template('index.html', files=files)

@links.route('/download-video', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400

    try:
        downloader = VideoDownloader()
        video_filepath, video_title = downloader.download_video(url)
        return send_file(video_filepath, as_attachment=True, download_name=f"{video_title}.mp4")
    except Exception as e:
        return jsonify({"message": f"Failed to download video: {str(e)}"}), 500
    
@links.route('/download-image', methods=['POST'])
def download_image():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400

    try:
        downloader = ImageDownloader()
        with tempfile.TemporaryDirectory() as tmpdirname:
            downloader.download_path = tmpdirname  # Set temporary directory
            filename = downloader.download_image(url)
            filepath = os.path.join(tmpdirname, filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"message": f"Failed to download image: {str(e)}"}), 500
    
@links.route('/downloads/<filename>')
def download_file(filename):
    download_path = Path(__file__).resolve().parent / 'static' / 'downloads'
    return send_from_directory(str(download_path), filename, as_attachment=True)