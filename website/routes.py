from flask import Blueprint, render_template, jsonify, send_file, request, after_this_request
from website.services.image import download_image
from website.services.video import get_video_info, download_video, VideoDownloadProgress
from logger import logger  # Import centralized logger
import os
from uuid import uuid4
from pathlib import Path
import mimetypes
import re
from threading import Timer  

links = Blueprint('links', __name__)

# Define a URL regex for input validation
URL_REGEX = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$')
download_store = {}

def is_valid_url(url):
    return bool(URL_REGEX.match(url))

@links.route("/")
def index():
    return render_template('index.html')

def cleanup_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file: {str(e)}")

@links.route("/download-image", methods=["POST"])
def download_image_route():
    try:
        data = request.get_json()
        url = data.get("url")

        # URL validation
        if not url or not is_valid_url(url):
            return jsonify({"message": "A valid URL is required"}), 400

        result = download_image(url)

        if result["status"] == "success":
            file_path = result["file_path"]
            original_name = result.get("original_name", "")

            if not os.path.isfile(file_path):
                logger.error(f"Not a valid file: {file_path}")
                return jsonify({"message": "Invalid file path"}), 400

            try:
                # Serve the file to the user
                download_name = original_name if original_name else os.path.basename(file_path)
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name=download_name,
                    mimetype=mime_type
                )

                @response.call_on_close
                def cleanup():
                    cleanup_file(file_path)
                return response

            except Exception as e:
                logger.error(f"Error sending file: {str(e)}")
                cleanup_file(file_path)
                return jsonify({"message": f"Error sending file: {str(e)}"}), 500
        else:
            return jsonify({"message": result["message"]}), 400

    except Exception as e:
        logger.error(f"Unexpected error in download-image route: {str(e)}")
        return jsonify({"message": "Server error"}), 500

# Similar updates should be made to `video_info_route` and `download_video_route`, with `url` validation and file cleanup logic.

    
@links.route("/video-info", methods=["POST"])
def video_info_route():
    try:
        data = request.get_json()
        url = data.get("url")

        # URL validation
        if not url or not is_valid_url(url):
            logger.warning("Invalid URL provided for video information")
            return jsonify({"message": "A valid URL is required"}), 400

        video_info = get_video_info(url)
        if video_info["status"] == "success":
            logger.debug(f"Video info retrieved successfully for URL: {url}")
            return jsonify({
                "status": "success",
                "title": video_info["title"],
                "duration": video_info["duration"],
                "formats": video_info["formats"]
            })
        else:
            logger.error(f"Failed to retrieve video info: {video_info['message']}")
            return jsonify({"message": video_info["message"]}), 400

    except Exception as e:
        logger.error(f"Unexpected error in video_info_route: {str(e)}")
        return jsonify({"message": "Server error"}), 500

@links.route("/download-video", methods=["POST"])
def download_video_route():
    try:
        data = request.get_json()
        url = data.get("url")
        format_id = data.get("format_id", None)

        if not url or not is_valid_url(url):
            logger.warning("Invalid URL provided for video download")
            return jsonify({"message": "A valid URL is required"}), 400

        progress_tracker = VideoDownloadProgress()
        result = download_video(url, format_id=format_id, progress_hooks=[progress_tracker])

        if result["status"] == "success":
            file_path = result["file_path"]
            unique_id = str(uuid4())
            download_store[unique_id] = file_path

            # Provide a "save" link back to the client
            save_url = f"/save-video/{unique_id}"
            return jsonify({"status": "success", "save_url": save_url})

        else:
            logger.error(f"Download error: {result['message']}")
            return jsonify({"message": result["message"]}), 400

    except Exception as e:
        logger.error(f"Unexpected error in download_video_route: {str(e)}")
        return jsonify({"message": "Server error"}), 500

@links.route("/save-video/<file_id>", methods=["GET"])
def save_video_route(file_id):
    try:
        file_path = download_store.get(file_id)

        # Check if the file path is valid
        if not file_path or not os.path.isfile(file_path):
            logger.error(f"File not found for ID: {file_id}")
            return jsonify({"message": "File not found"}), 400

        original_name = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Send the file as an attachment
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=original_name,
            mimetype=mime_type
        )

        # Delayed cleanup function
        def delayed_cleanup():
            try:
                os.remove(file_path)
                download_store.pop(file_id, None)  # Remove entry from download_store
                logger.debug(f"Cleaned up file after delay: {file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up file: {str(e)}")

        # Set up a 20-second delay before calling the cleanup function
        Timer(20, delayed_cleanup).start()

        return response

    except Exception as e:
        logger.error(f"Unexpected error in save_video_route: {str(e)}")
        return jsonify({"message": "Server error"}), 500