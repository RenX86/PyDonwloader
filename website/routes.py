from flask import Blueprint, request, jsonify, render_template, redirect, url_for, send_from_directory
from .services.yt import download_youtube
from .services.gallery import download_gallery
import os 

links = Blueprint('links', __name__)

@links.route("/")
def index():
    return render_template('index.html')

@links.route('/download-youtube', methods=['POST'])
def youtube_downloader():  # Fixed function name
    data = request.get_json()
    url = data.get('url')
    try:
        result = download_youtube(url)
        return jsonify({'status': 'success', 'message': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@links.route('/download-gallery', methods=['POST'])
def gallery_downloader():
    data = request.get_json()
    url = data.get('url')
    try:
        result = download_gallery(url)
        return jsonify({'status': 'success', 'message': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@links.route('/downloads/<filename>')
def download_file(filename):
    download_path = os.path.join('website', 'static', 'downloads')
    return send_from_directory(download_path, filename, as_attachment=True)