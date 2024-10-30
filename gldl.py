import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def download_image(url):
    try:
        result = subprocess.run(["gallery-dl", url], check=True)
        logging.info(f"Image downloaded successfully from {url}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download image from {url}. Error: {e}")

def unsupported_image_download(url, *args):
    try:
        command = ["gallery-dl", url, *args]
        result = subprocess.run(command, check=True)
        logging.info(f"Image downloaded successfully from {url}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download image from {url}. Error: {e}")

def download_images_from_urls_in_file(file_path):
    try:
        with open(file_path, 'r') as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]

        for url in urls:
            try:
                download_image(url)
            except Exception as e:
                logging.error(f"Error downloading image from {url}: {e}")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error processing URL file: {e}")

def download_images_from_supported_sites():
    while True:
        url = input("Enter the Image url (or type 'ext' to return): ").strip()
        if url.lower() == 'ext':
            break
        elif url:
            try:
                download_image(url)
            except Exception as e:
                logging.error(f"Error downloading image from {url}: {e}")
        else:
            logging.warning("No URL entered.")

def download_images_from_unsupported_sites():
    while True:
        url = input("Enter the Image url (or type 'ext' to return): ").strip()
        if url.lower() == 'ext':
            break
        elif url:
            try:
                unsupported_image_download(url)
            except Exception as e:
                logging.error(f"Error downloading image from {url}: {e}")
        else:
            logging.warning("No URL entered.")

def main():
    while True:
        print(f"========================")
        print("Python Image Downloader")
        print(f"========================")
        print("1. Download from supported site")
        print("2. Download from unsupported site")
        print("3. Download from URL file")
        print("4. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            download_images_from_supported_sites()
        elif choice == "2":
            download_images_from_unsupported_sites()
        elif choice == "3":
            file_path = input("Enter the path to the URL file: ").strip()
            download_images_from_urls_in_file(file_path)
        elif choice == "4":
            logging.info("Exiting the program.")
            break
        else:
            logging.warning("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()