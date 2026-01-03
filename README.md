# YouTube Video/Audio Downloader

A powerful YouTube downloader that supports both **video (MP4)** and **audio (MP3)** downloads with quality selection options. Built with Python and yt-dlp.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red.svg)

## Features

- ✅ **Download Videos** in MP4 format with quality options (4K, 2K, 1080p, 720p, 480p, 360p)
- ✅ **Download Audio** in MP3 format with bitrate options (320kbps, 256kbps, 192kbps, 128kbps, 96kbps, 64kbps)
- ✅ **Cookie Support** for age-restricted and authenticated content
- ✅ **VPS Friendly** with built-in anti-detection features
- ✅ **Progress Display** with download speed and percentage
- ✅ **Cross-Platform** works on Windows, Linux, and macOS

## Requirements

- Python 3.7 or higher
- FFmpeg (required for MP3 conversion)
- yt-dlp

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
cd youtube-downloader
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows:**
```bash
# Using winget
winget install --id=Gyan.FFmpeg -e

# Or using chocolatey
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 4. Set Up Cookies (Optional but Recommended)

Cookies are required for:
- Age-restricted videos
- Private/unlisted videos
- Avoiding bot detection

**How to export cookies:**

1. Install a browser extension:
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. Go to [youtube.com](https://youtube.com) and make sure you're logged in

3. Click the extension icon and export cookies

4. Save the file as `cookies.txt` in the same folder as the script

## Usage

### Basic Usage

```bash
python youtube_downloader.py
```

You will be prompted to:
1. Enter the YouTube URL
2. Choose download mode (Video or Audio)
3. Select quality

### With URL as Argument

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Example Session

```
======================================================================
       YouTube Video/Audio Downloader
======================================================================
Using cookies from: D:\youtube-downloader\cookies.txt

Enter YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Processing URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Extracting video information...

Title: Rick Astley - Never Gonna Give You Up
Duration: 3:33
Channel: Rick Astley

======================================================================
Download Mode:
======================================================================
1. VIDEO (MP4)
2. AUDIO (MP3)
======================================================================

Select mode (1 for Video, 2 for Audio) [default: 1]: 2

----------------------------------------------------------------------
Audio Quality Options (MP3):
----------------------------------------------------------------------
1. 320 kbps (Best quality)
2. 256 kbps (High quality)
3. 192 kbps (Good quality)
4. 128 kbps (Medium quality)
5. 96 kbps (Low quality)
6. 64 kbps (Very low quality)
----------------------------------------------------------------------

Select audio quality (1-6) [default: 1]: 1

Waiting 2.3s before starting download...

Downloading AUDIO and converting to MP3 (320 kbps)...
Progress: 100.0% | Speed: 1.25 MB/s
Download finished, processing...

[SUCCESS] Audio download and conversion completed!
```

## Quality Options

### Video Quality
| Option | Resolution | Description |
|--------|------------|-------------|
| 1 | Best | Highest available quality |
| 2 | 2160p | 4K Ultra HD |
| 3 | 1440p | 2K QHD |
| 4 | 1080p | Full HD |
| 5 | 720p | HD |
| 6 | 480p | SD |
| 7 | 360p | Low |

### Audio Quality (MP3)
| Option | Bitrate | Description |
|--------|---------|-------------|
| 1 | 320 kbps | Best quality |
| 2 | 256 kbps | High quality |
| 3 | 192 kbps | Good quality |
| 4 | 128 kbps | Medium quality |
| 5 | 96 kbps | Low quality |
| 6 | 64 kbps | Very low quality |

## VPS Usage

This script includes VPS-friendly options to help bypass YouTube's bot detection:

- Geo-bypass enabled
- Retry mechanisms for failed downloads
- Sleep intervals between requests
- Browser-like HTTP headers

**Tips for VPS:**
1. Always use cookies exported from your local machine
2. Keep yt-dlp updated: `pip install --upgrade yt-dlp`
3. If downloads fail, try updating cookies

## Troubleshooting

### "Sign in to confirm you're not a bot"
- Make sure you have a valid `cookies.txt` file
- Re-export cookies from your browser
- Update yt-dlp: `pip install --upgrade yt-dlp`

### "FFmpeg not found"
- Install FFmpeg following the instructions above
- Make sure FFmpeg is in your system PATH
- Restart your terminal after installation

### "Video unavailable"
- Check if the video is accessible in your region
- Some videos may be private or deleted
- Try using a VPN if geo-restricted

## File Structure

```
youtube-downloader/
├── youtube_downloader.py  # Main script
├── requirements.txt       # Python dependencies
├── cookies.txt           # Your cookies (create this yourself)
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore           # Git ignore file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal use only. Please respect YouTube's Terms of Service and copyright laws. Only download content you have the right to download.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The amazing YouTube downloader library
- [FFmpeg](https://ffmpeg.org/) - For audio/video processing
