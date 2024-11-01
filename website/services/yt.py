import yt_dlp

def download_video(data):
    url = data.get("url")
    if not url:
        return "Error: No URL provided"

    ydl_opts = {"format": "best"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return f"Downloaded content from {url}"
