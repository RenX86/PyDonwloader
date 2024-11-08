from flask import Blueprint, render_template, jsonify, send_file, request
from website.services.image import *
from website.services.video import *
import os
from pathlib import Path
import logging
import mimetypes

links = Blueprint('links', __name__)

@links.route("/")
def index():
    return render_template('index.html')

@links.route("/download-image", methods=["POST"])
def download_image_route():
    try:
        data = request.get_json()
        url = data.get("url")
        
        if not url:
            return jsonify({"message": "URL is required"}), 400
        
        # Download the image
        result = download_image(url)
        
        if result["status"] == "success":
            file_path = result["file_path"]
            original_name = result.get("original_name", "")
            
            # Verify the file exists and is actually a file (not a directory)
            if not os.path.isfile(file_path):
                logger.error(f"Not a valid file: {file_path}")
                return jsonify({"message": "Download resulted in a directory, not a file"}), 400
                
            try:
                # Ensure we have read permissions
                Path(file_path).chmod(0o644)
                
                # Determine the correct filename and mimetype
                download_name = original_name if original_name else os.path.basename(file_path)
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                
                # Serve the file to the user
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name=download_name,
                    mimetype=mime_type
                )
                
                # Clean up: remove the file after sending
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.isfile(file_path):
                            os.chmod(file_path, 0o666)  # Ensure we have permission to delete
                            os.remove(file_path)
                            logger.debug(f"Cleaned up file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error cleaning up file: {str(e)}")
                
                return response
                
            except Exception as e:
                logger.error(f"Error sending file: {str(e)}")
                # Try to clean up if we failed to send
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass
                return jsonify({"message": f"Error sending file: {str(e)}"}), 500
        else:
            return jsonify({"message": result["message"]}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in download route: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    
@links.route("/video-info", methods=["POST"])
def video_info_route():
    """Get video information without downloading."""
    try:
        data = request.get_json()
        url = data.get("url")
        
        if not url:
            return jsonify({"message": "URL is required"}), 400
            
        result = get_video_info(url)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify({"message": result["message"]}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in video info route: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@links.route("/download-video", methods=["POST"])
def download_video_route():
    """Download video and send to user."""
    try:
        data = request.get_json()
        url = data.get("url")
        format_id = data.get("format_id")  # Optional format selection
        
        if not url:
            return jsonify({"message": "URL is required"}), 400
        
        # Create progress tracker
        progress = VideoDownloadProgress()
        
        # Download the video
        result = download_video(url, format_id, progress_hooks=[progress])
        
        if result["status"] == "success":
            file_path = result["file_path"]
            original_name = result.get("original_name", "")
            
            # Verify the file exists and is actually a file
            if not os.path.isfile(file_path):
                logger.error(f"Not a valid file: {file_path}")
                return jsonify({"message": "Download resulted in a directory, not a file"}), 400
                
            try:
                # Ensure we have read permissions
                Path(file_path).chmod(0o644)
                
                # Determine the correct filename and mimetype
                download_name = original_name if original_name else os.path.basename(file_path)
                mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                
                # Serve the file to the user
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name=download_name,
                    mimetype=mime_type
                )
                
                # Clean up: remove the file after sending
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.isfile(file_path):
                            os.chmod(file_path, 0o666)  # Ensure we have permission to delete
                            os.remove(file_path)
                            logger.debug(f"Cleaned up file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error cleaning up file: {str(e)}")
                
                return response
                
            except Exception as e:
                logger.error(f"Error sending file: {str(e)}")
                # Try to clean up if we failed to send
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass
                return jsonify({"message": f"Error sending file: {str(e)}"}), 500
        else:
            return jsonify({"message": result["message"]}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in video download route: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500