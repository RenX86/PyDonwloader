import subprocess
import os

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def download_video(url):
    script_dir = get_script_dir()
    os.chdir(script_dir)
    try:
        result = subprocess.run(["yt-dlp", url], check=True)
        if result.returncode == 0:
            print(f"Video downloaded successfully from {url}")
    except subprocess.CalledProcessError:
        print(f"Failed to download video from {url}. Please check the URL or your connection.")

def download_from_file(file_path):
    script_dir = get_script_dir()
    os.chdir(script_dir)
    try:
        result = subprocess.run(["yt-dlp", "-a", file_path], check=True)
        if result.returncode == 0:
            print(f"Videos successfully downloaded from {file_path}")
    except subprocess.CalledProcessError:
        print(f"Failed to download videos from {file_path}. Please check the file or your connection.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found. Please check the path and try again.")

def main():
    while True:
        print(f"========================")
        print("Python Video Downloader")
        print(f"========================")
        print("\nOptions:")
        print("1. Single URL Download")
        print("2. Multiple URL Download (from a file)")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            while True:
                url = input("Enter the YouTube video URL (or type 'ext' to return to the main menu): ")
                if url.lower() == 'ext':
                    break
                elif url:
                    download_video(url)
                else:
                    print("No URL entered. Please try again.")
                    
        elif choice == "2":
            while True:
                file_path = input("Enter the path to the file containing URLs (or type 'ext' to return to the main menu): ")
                if file_path.lower() == 'ext':
                    break
                elif os.path.exists(file_path):
                    download_from_file(file_path)
                else:
                    print(f"File '{file_path}' not found. Please ensure the file exists and try again.")
                    
        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please choose a valid option (1, 2, or 3).")

if __name__ == "__main__":
    main()
