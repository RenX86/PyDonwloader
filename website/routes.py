<<<<<<< HEAD
from flask import Blueprint, request, jsonify, render_template, send_file, current_app, url_for
import os
from .services.yt import download_youtube, get_video_path
from .services.gallery import download_gallery
=======
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from .services import yt, gallery

>>>>>>> parent of 4b20dd1 (Yt working)

links = Blueprint('links', __name__)

@links.route("/")
def index():
    return render_template("index.html")

<<<<<<< HEAD
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
=======
@links.route('/home')
def home():
    return  "<h1> HOME </h1>"

@links.route("/yt-dlp", methods=["POST, GET"])
def download_video():
    url = request.form.get("url")
    if not url:
        return redirect(url_for("main.index"))
    
    result = yt.download_video({"url": url})
    return jsonify({"result": result})

@links.route("/gallery-dl", methods=["POST,GET"])
def download_gallery():
    url = request.form.get("url")
    if not url:
        return redirect(url_for("main.index"))
    
    result = gallery.download_gallery({"url": url})
    return jsonify({"result": result})
>>>>>>> parent of 4b20dd1 (Yt working)

