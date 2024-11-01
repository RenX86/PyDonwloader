import gallery_dl

def download_gallery(data):
    url = data.get("url")
    if not url:
        return "Error: No URL provided"

    gallery_dl.download(url)  # Adjust as needed for gallery_dl
    return f"Downloaded gallery from {url}"
