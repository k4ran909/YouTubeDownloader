#!/usr/bin/env python3
"""
YouTube Video/Audio Downloader with Quality Options
Supports single videos and entire playlists
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
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_playlist_id(url):
    """Extract playlist ID from YouTube URL"""
    # Match playlist ID (starts with PL, RD, UU, etc.)
    match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None


def is_radio_playlist(playlist_id):
    """
    Check if playlist is a Radio/Mix (auto-generated, non-downloadable as playlist).
    Radio playlists start with 'RD' and are dynamically generated for each user.
    """
    if playlist_id:
        return playlist_id.startswith('RD')
    return False


def is_playlist_url(url):
    """Check if URL contains a playlist"""
    return 'list=' in url


def get_clean_video_url(video_id):
    """Get a clean video URL from video ID"""
    return f"https://www.youtube.com/watch?v={video_id}"


def get_playlist_url(playlist_id):
    """Get a playlist URL from playlist ID"""
    return f"https://www.youtube.com/playlist?list={playlist_id}"


def validate_url(url):
    """Validate YouTube URL"""
    url = url.strip()
    
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',
        r'^[a-zA-Z0-9_-]{11}$'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    
    return False


def get_video_info(url, playlist_mode=False):
    """Get video/playlist information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist' if playlist_mode else False,
        'skip_download': True,
        'ignoreerrors': True if playlist_mode else False,
        'noplaylist': not playlist_mode,
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
            print("Extracting information...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("Error: Could not extract information")
                return None
            
            return info
            
    except Exception as e:
        print(f"\n[ERROR] Error fetching information:")
        print(f"   {str(e)}")
        return None


def display_video_info(info):
    """Display video title and available formats"""
    print(f"\nTitle: {info.get('title', 'Unknown')}")
    duration = info.get('duration', 0) or 0
    print(f"Duration: {duration // 60}:{duration % 60:02d}")
    print(f"Channel: {info.get('channel', info.get('uploader', 'Unknown'))}")


def display_playlist_info(info):
    """Display playlist information"""
    print(f"\nPlaylist: {info.get('title', 'Unknown')}")
    entries = info.get('entries', [])
    video_count = len([e for e in entries if e])  # Count non-None entries
    print(f"Videos: {video_count}")
    print(f"Channel: {info.get('channel', info.get('uploader', 'Unknown'))}")
    
    # Show first few videos
    print("\nVideos in playlist:")
    print("-" * 50)
    for i, entry in enumerate(entries[:10], 1):
        if entry:
            title = entry.get('title', 'Unknown')[:45]
            print(f"  {i}. {title}{'...' if len(entry.get('title', '')) > 45 else ''}")
    
    if video_count > 10:
        print(f"  ... and {video_count - 10} more videos")
    
    return video_count


def download_video(url, quality='best', playlist_mode=False, playlist_items=None):
    """Download video with specified quality"""
    
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
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if playlist_mode else '%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'noplaylist': not playlist_mode,
        'ignoreerrors': True if playlist_mode else False,  # Skip unavailable videos in playlist
        **VPS_OPTIONS,
    }
    
    if playlist_items:
        ydl_opts['playlist_items'] = playlist_items
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    # Add random delay before download
    delay = random.uniform(1, 3)
    print(f"Waiting {delay:.1f}s before starting download...")
    time.sleep(delay)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            mode_text = "PLAYLIST" if playlist_mode else "VIDEO"
            print(f"\nDownloading {mode_text} with quality: {quality}...")
            ydl.download([url])
            print(f"\n[SUCCESS] {mode_text} download completed!")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error downloading:")
        print(f"   {str(e)}")
        return False


def download_audio(url, quality='320', playlist_mode=False, playlist_items=None):
    """Download audio and convert to MP3"""
    
    audio_quality_map = {
        '320': '0',
        '256': '1',
        '192': '2',
        '128': '5',
        '96': '6',
        '64': '8',
    }
    
    quality_setting = audio_quality_map.get(quality, '0')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if playlist_mode else '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'noplaylist': not playlist_mode,
        'ignoreerrors': True if playlist_mode else False,
        **VPS_OPTIONS,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality_setting,
        }],
    }
    
    if playlist_items:
        ydl_opts['playlist_items'] = playlist_items
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    # Add random delay before download
    delay = random.uniform(1, 3)
    print(f"Waiting {delay:.1f}s before starting download...")
    time.sleep(delay)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            mode_text = "PLAYLIST AUDIO" if playlist_mode else "AUDIO"
            print(f"\nDownloading {mode_text} and converting to MP3 ({quality} kbps)...")
            ydl.download([url])
            print(f"\n[SUCCESS] {mode_text} download and conversion completed!")
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


def select_video_quality():
    """Display video quality menu and get user choice"""
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
    
    return video_quality_map.get(video_choice, 'best')


def select_audio_quality():
    """Display audio quality menu and get user choice"""
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
    
    return audio_quality_map.get(audio_choice, '320')


def main():
    print("=" * 70)
    print("       YouTube Video/Audio Downloader")
    print("          Supports Videos & Playlists")
    print("=" * 70)
    
    # Check for ffmpeg
    if not check_ffmpeg():
        print("\n[WARNING] ffmpeg not found! Audio/MP3 conversion may not work.")
        print("          Install ffmpeg: https://ffmpeg.org/download.html")
    
    # Get URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nEnter YouTube URL (video or playlist): ").strip()
    
    if not url:
        print("Error: No URL provided!")
        return
    
    # Validate URL
    if not validate_url(url):
        print(f"Error: Invalid YouTube URL: {url}")
        return
    
    original_url = url
    video_id = extract_video_id(url)
    playlist_id = extract_playlist_id(url)
    
    # Check if URL contains both video and playlist
    download_playlist = False
    playlist_items = None
    
    if playlist_id and video_id:
        # Check if it's a Radio/Mix playlist (cannot be downloaded as playlist)
        if is_radio_playlist(playlist_id):
            print(f"\n[WARNING] This is a Radio/Mix playlist (auto-generated).")
            print("          Radio playlists cannot be downloaded as playlists.")
            print("          Downloading single video only...")
            url = get_clean_video_url(video_id)
        else:
            # URL has both video and playlist - ask user what they want
            print(f"\n[INFO] This URL contains both a video and a playlist.")
            print("=" * 70)
            print("What would you like to download?")
            print("=" * 70)
            print("1. Single Video only")
            print("2. Entire Playlist")
            print("3. Select specific videos from playlist")
            print("=" * 70)
            
            choice = input("\nSelect option (1-3) [default: 1]: ").strip()
            
            if choice == '2':
                download_playlist = True
                url = get_playlist_url(playlist_id)
                print(f"\n[INFO] Will download entire playlist")
            elif choice == '3':
                download_playlist = True
                url = get_playlist_url(playlist_id)
                playlist_items = input("\nEnter video numbers to download (e.g., 1,3,5-10): ").strip()
                if not playlist_items:
                    playlist_items = None
                print(f"\n[INFO] Will download selected videos from playlist")
            else:
                url = get_clean_video_url(video_id)
                print(f"\n[INFO] Will download single video")
    
    elif playlist_id and not video_id:
        # Pure playlist URL
        download_playlist = True
        url = get_playlist_url(playlist_id)
        print(f"\n[INFO] Playlist URL detected")
        
        # Ask if they want the entire playlist
        print("=" * 70)
        print("Playlist Options:")
        print("=" * 70)
        print("1. Download entire playlist")
        print("2. Select specific videos")
        print("=" * 70)
        
        choice = input("\nSelect option (1-2) [default: 1]: ").strip()
        
        if choice == '2':
            # First, get playlist info to show available videos
            info = get_video_info(url, playlist_mode=True)
            if info:
                video_count = display_playlist_info(info)
                playlist_items = input(f"\nEnter video numbers to download (1-{video_count}, e.g., 1,3,5-10): ").strip()
                if not playlist_items:
                    playlist_items = None
    
    else:
        # Single video URL
        url = get_clean_video_url(video_id) if video_id else url
    
    print(f"\nProcessing URL: {url}")
    
    # Get info
    info = get_video_info(url, playlist_mode=download_playlist)
    if not info:
        return
    
    # Display info
    if download_playlist:
        video_count = display_playlist_info(info)
    else:
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
        # Audio mode
        audio_quality = select_audio_quality()
        download_audio(url, audio_quality, playlist_mode=download_playlist, playlist_items=playlist_items)
    else:
        # Video mode
        video_quality = select_video_quality()
        download_video(url, video_quality, playlist_mode=download_playlist, playlist_items=playlist_items)


if __name__ == "__main__":
    main()
