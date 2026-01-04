
import os
import sys
import zipfile
import urllib.request
import shutil
import time

def install_ffmpeg():
    print("Starting FFmpeg installation...")
    
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(base_dir, 'bin')
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
        
    ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
    ffprobe_exe = os.path.join(bin_dir, 'ffprobe.exe')
    
    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        print("FFmpeg already exists in ./bin")
        return

    # 2. Download
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = os.path.join(base_dir, "ffmpeg.zip")
    
    print(f"Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"Download failed: {e}")
        return

    print("Extracting...")
    # 3. Extract
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the bin folder inside the zip
            for file in zip_ref.namelist():
                if file.endswith("bin/ffmpeg.exe"):
                    print(f"Extracting {file}...")
                    with zip_ref.open(file) as source, open(ffmpeg_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
                        
                elif file.endswith("bin/ffprobe.exe"):
                    print(f"Extracting {file}...")
                    with zip_ref.open(file) as source, open(ffprobe_exe, "wb") as target:
                        shutil.copyfileobj(source, target)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    print("FFmpeg setup complete!")

if __name__ == "__main__":
    install_ffmpeg()
