#!/usr/bin/env python3
"""
YouTube Video/Audio Downloader with Quality Options
Uses yt-dlp to download videos or extract audio as MP3
"""

import yt_dlp
import sys
import re
import os
import random
import time
import shutil

# Path to cookies file - place cookies.txt in the same folder as this script
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

# VPS-friendly options to help bypass YouTube restrictions
VPS_OPTIONS = {
    # Bypass geo-restrictions
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    
    # Retry settings
    'retries': 10,
    'fragment_retries': 10,
    'file_access_retries': 5,
    
    # Sleep between requests to avoid rate limiting
    'sleep_interval': 1,
    'max_sleep_interval': 5,
    'sleep_interval_requests': 1,
    
    # HTTP settings
    'socket_timeout': 30,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    },
}


def check_ffmpeg():
    """Check if ffmpeg is available for audio conversion"""
    return shutil.which('ffmpeg') is not None


def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    # Patterns to match video ID from different URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',  # Just the video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def clean_url(url):
    """
    Clean YouTube URL by removing playlist and other unnecessary parameters.
    This prevents issues with playlist/radio URLs that can cause hanging.
    """
    url = url.strip()
    
    # Extract video ID
    video_id = extract_video_id(url)
    
    if video_id:
        # Return a clean URL with just the video ID
        clean = f"https://www.youtube.com/watch?v={video_id}"
        
        # Check if original URL had playlist parameters
        if 'list=' in url or 'start_radio=' in url:
            print(f"[INFO] Cleaned URL (removed playlist parameters)")
            print(f"       Original: {url[:70]}{'...' if len(url) > 70 else ''}")
            print(f"       Clean: {clean}")
        
        return clean
    
    # If we couldn't extract video ID, return original URL
    print(f"Warning: Could not extract video ID from URL: {url}")
    return url


def validate_url(url):
    """Validate YouTube URL"""
    url = url.strip()
    
    # Check if it's a valid YouTube URL pattern
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',
        r'^[a-zA-Z0-9_-]{11}$'  # Just the video ID
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    
    return False


def get_video_info(url):
    """Get video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'ignoreerrors': False,
        'noplaylist': True,  # Only download single video, not playlist
        **VPS_OPTIONS,
    }
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
        print(f"Using cookies from: {COOKIES_FILE}")
    else:
        print(f"Warning: cookies.txt not found at {COOKIES_FILE}")
    
    # Add random delay to avoid detection
    time.sleep(random.uniform(0.5, 2))
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting video information...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("Error: Could not extract video information")
                return None
            
            return info
            
    except Exception as e:
        print(f"\n[ERROR] Error fetching video information:")
        print(f"   {str(e)}")
        return None


def display_video_info(info):
    """Display video title and available formats"""
    print(f"\nTitle: {info.get('title', 'Unknown')}")
    duration = info.get('duration', 0)
    print(f"Duration: {duration // 60}:{duration % 60:02d}")
    print(f"Channel: {info.get('channel', 'Unknown')}")


def download_video(url, quality='best'):
    """Download video with specified quality"""
    
    # Quality presets
    quality_options = {
        'best': 'bestvideo+bestaudio/best',
        '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
        '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
    }
    
    format_string = quality_options.get(quality.lower(), quality_options['best'])
    
    ydl_opts = {
        'format': format_string,
        'outtmpl': '%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'noplaylist': True,  # Only download single video, not playlist
        **VPS_OPTIONS,
    }
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    # Add random delay before download
    delay = random.uniform(1, 3)
    print(f"Waiting {delay:.1f}s before starting download...")
    time.sleep(delay)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nDownloading VIDEO with quality: {quality}...")
            ydl.download([url])
            print("\n[SUCCESS] Video download completed!")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error downloading video:")
        print(f"   {str(e)}")
        return False


def download_audio(url, quality='320'):
    """Download audio and convert to MP3"""
    
    # Audio quality presets (kbps)
    audio_quality_map = {
        '320': '0',   # Best quality (VBR ~320kbps)
        '256': '1',   # High quality
        '192': '2',   # Good quality
        '128': '5',   # Medium quality
        '96': '6',    # Low quality
        '64': '8',    # Very low quality
    }
    
    quality_setting = audio_quality_map.get(quality, '0')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'noplaylist': True,  # Only download single video, not playlist
        **VPS_OPTIONS,
        # Post-processing to convert to MP3
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality_setting,
        }],
    }
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    # Add random delay before download
    delay = random.uniform(1, 3)
    print(f"Waiting {delay:.1f}s before starting download...")
    time.sleep(delay)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nDownloading AUDIO and converting to MP3 ({quality} kbps)...")
            ydl.download([url])
            print("\n[SUCCESS] Audio download and conversion completed!")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error downloading audio:")
        print(f"   {str(e)}")
        return False


def progress_hook(d):
    """Display download progress"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            speed = d.get('speed', 0)
            speed_str = f"{speed / (1024*1024):.2f} MB/s" if speed else "Unknown"
            print(f"\rProgress: {percent:.1f}% | Speed: {speed_str}", end='', flush=True)
        elif '_percent_str' in d:
            print(f"\rProgress: {d['_percent_str']} | Speed: {d.get('_speed_str', 'Unknown')}", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\rDownload finished, processing...", flush=True)


def main():
    print("=" * 70)
    print("       YouTube Video/Audio Downloader")
    print("=" * 70)
    
    # Check for ffmpeg
    if not check_ffmpeg():
        print("\n[WARNING] ffmpeg not found! Audio/MP3 conversion may not work.")
        print("          Install ffmpeg: https://ffmpeg.org/download.html")
    
    # Get video URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nEnter YouTube URL: ").strip()
    
    if not url:
        print("Error: No URL provided!")
        return
    
    # Validate URL
    if not validate_url(url):
        print(f"Error: Invalid YouTube URL: {url}")
        return
    
    # Clean URL (remove playlist parameters)
    url = clean_url(url)
    print(f"\nProcessing URL: {url}")
    
    # Get video info
    info = get_video_info(url)
    if not info:
        return
    
    display_video_info(info)
    
    # Mode selection: Video or Audio
    print("\n" + "=" * 70)
    print("Download Mode:")
    print("=" * 70)
    print("1. VIDEO (MP4)")
    print("2. AUDIO (MP3)")
    print("=" * 70)
    
    mode_choice = input("\nSelect mode (1 for Video, 2 for Audio) [default: 1]: ").strip()
    
    if mode_choice == '2':
        # Audio/MP3 mode
        print("\n" + "-" * 70)
        print("Audio Quality Options (MP3):")
        print("-" * 70)
        print("1. 320 kbps (Best quality)")
        print("2. 256 kbps (High quality)")
        print("3. 192 kbps (Good quality)")
        print("4. 128 kbps (Medium quality)")
        print("5. 96 kbps (Low quality)")
        print("6. 64 kbps (Very low quality)")
        print("-" * 70)
        
        audio_choice = input("\nSelect audio quality (1-6) [default: 1]: ").strip()
        
        audio_quality_map = {
            '1': '320',
            '2': '256',
            '3': '192',
            '4': '128',
            '5': '96',
            '6': '64',
        }
        
        audio_quality = audio_quality_map.get(audio_choice, '320')
        download_audio(url, audio_quality)
        
    else:
        # Video mode
        print("\n" + "-" * 70)
        print("Video Quality Options:")
        print("-" * 70)
        print("1. Best available quality")
        print("2. 2160p (4K)")
        print("3. 1440p (2K)")
        print("4. 1080p (Full HD)")
        print("5. 720p (HD)")
        print("6. 480p")
        print("7. 360p")
        print("-" * 70)
        
        video_choice = input("\nSelect video quality (1-7) [default: 1]: ").strip()
        
        video_quality_map = {
            '1': 'best',
            '2': '2160p',
            '3': '1440p',
            '4': '1080p',
            '5': '720p',
            '6': '480p',
            '7': '360p',
        }
        
        video_quality = video_quality_map.get(video_choice, 'best')
        download_video(url, video_quality)


if __name__ == "__main__":
    main()
