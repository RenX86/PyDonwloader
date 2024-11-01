from flask import Blueprint, request, jsonify, render_template, send_file, current_app, url_for
import os
from .services.yt import download_youtube, get_video_path
from .services.gallery import download_gallery

links = Blueprint('links', __name__)

@links.route("/")
def index():
    return render_template('index.html')

@links.route('/download-youtube', methods=['POST'])
def youtube_downloader():
    data = request.get_json()
    url = data.get('url')
    try:
        result = download_youtube(url)
        # Return the download URL along with the success message
        download_url = url_for('links.get_file', filename=result['filename'], _external=True)
        return jsonify({
            'status': 'success', 
            'message': result['message'],
            'download_url': download_url
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@links.route('/get-file/<filename>')
def get_file(filename):
    try:
        file_path = get_video_path(filename)
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
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