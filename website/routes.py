from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from .services import yt, gallery


links = Blueprint('links', __name__)

@links.route("/")
def index():
    return render_template("index.html")

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

