from flask import Flask, request, jsonify
import subprocess
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def is_valid_url(url):
    # Basic validation for URL format
    return url.startswith("http://") or url.startswith("https://")

def download_with_gallery_dl(url, *args):
    """Helper function to download using gallery-dl."""
    if not is_valid_url(url):
        logging.warning(f"Invalid URL format: {url}")
        return jsonify({"error": "Invalid URL format"}), 400
    
    try:
        command = ["gallery-dl", url, *args]
        result = subprocess.run(command, check=True)
        logging.info(f"Image downloaded successfully from {url}")
        return jsonify({"message": "Image downloaded successfully"}), 200
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download image from {url}. Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_image', methods=['POST, GET'])
def download_image():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    return download_with_gallery_dl(url)

@app.route('/unsupported_image_download', methods=['POST'])
def unsupported_image_download():
    data = request.json
    url = data.get("url")
    args = data.get("args", [])
    
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    return download_with_gallery_dl(url, *args)

@app.route('/download_images_from_urls_in_file', methods=['POST'])
def download_images_from_urls_in_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "File is required"}), 400
    
    try:
        urls = [url.strip() for url in file.read().decode('utf-8').splitlines() if url.strip()]
        for url in urls:
            response = download_with_gallery_dl(url)
            if response[1] != 200:
                return response  # Return the error if any download fails
        return jsonify({"message": "All images downloaded successfully"}), 200
    except Exception as e:
        logging.error(f"Error processing URL file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_video', methods=['POST'])
def download_video():
    url = request.json.get("url")
    if not url or not is_valid_url(url):
        return jsonify({"error": "Valid URL is required"}), 400

    try:
        result = subprocess.run(["yt-dlp", url], check=True)
        logging.info(f"Video downloaded successfully from {url}")
        return jsonify({"message": "Video downloaded successfully"}), 200
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download video from {url}. Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_from_file', methods=['POST'])
def download_from_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "File is required"}), 400

    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)

    try:
        result = subprocess.run(["yt-dlp", "-a", file_path], check=True)
        logging.info(f"Videos successfully downloaded from {file.filename}")
        return jsonify({"message": "Videos downloaded successfully"}), 200
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download videos from {file.filename}. Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=False)
