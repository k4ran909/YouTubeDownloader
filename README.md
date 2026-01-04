# YouTube Downloader PRO

A powerful, universal downloader platform featuring a **Modern Web Application**, **Desktop GUI**, and **CLI tools**.
Download videos and audio from YouTube (and many other sites) in the highest available quality.

<div align="center">
  <img src="https://img.shields.io/badge/Frontend-React_TypeScript-blue?logo=react" alt="React">
  <img src="https://img.shields.io/badge/Backend-Node.js_Express-green?logo=nodedotjs" alt="Node">
  <img src="https://img.shields.io/badge/Core-Python_yt--dlp-yellow?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</div>

## ✨ Features

### 🌐 Web Application (New!)
- **Cinematic UI**: Beautiful dark-mode interface with particle effects and smooth animations.
- **Universal Support**: Optimized for YouTube but works with TikTok, Instagram, Twitter, and more.
- **Auto-Quality**: Automatically bypasses bot detection to grab the **Best Available** video quality.
- **Audio Powerhouse**: Download audio in multiple formats:
  - **MP3** (320kbps, 192kbps, 128kbps)
  - **M4A** (AAC Best Quality)
  - **WAV** (Lossless)
- **Deployment Ready**: Fully configured for cloud hosting (Netlify + Render).

### 🖥️ Desktop Application
- **GUI Version**: User-friendly Python interface with `customtkinter`.
- **CLI Version**: VPS-friendly command-line tool for server automation.
- **Playlist Support**: Batch download entire playlists.

---

## 🚀 Quick Start (Web App)

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- FFmpeg (Must be in system PATH)

### Running Locally

1.  **Start the Backend (Server)**
    ```bash
    cd server
    # Install dependencies (if any specific to server, usually root package.json handles it)
    node index.js
    ```
    The server will run on `http://localhost:5000`.

2.  **Start the Frontend (Client)**
    ```bash
    cd client
    npm install
    npm run dev
    ```
    Open `http://localhost:5173` in your browser.

---

## ☁️ Deployment Guide

You can host this application for free using **Netlify** (Frontend) and **Render** (Backend).

### 1. Deploy Backend (Render)
1.  Push this repository to GitHub.
2.  Create a **Web Service** on [Render](https://render.com).
3.  Connect your repository.
4.  Render will automatically use the `Dockerfile` to build the Node.js+Python environment.
5.  **Copy your Backend URL** (e.g., `https://your-app.onrender.com`).

### 2. Deploy Frontend (Netlify)
1.  Create a **New Site from Git** on [Netlify](https://netlify.com).
2.  Connect your repository.
3.  **Base directory**: `client`
4.  **Build command**: `npm run build`
5.  **Publish directory**: `dist`
6.  **Environment Variables**:
    - Key: `VITE_API_URL`
    - Value: `https://your-app.onrender.com/api` (Your Render URL + /api)

---

## 🐍 Desktop App Usage (Python)

If you prefer the standalone desktop application:

### Requirements
```bash
pip install -r requirements.txt
```

### Running the GUI
```bash
python youtube_downloader_gui.py
```

### Running the CLI
```bash
python youtube_downloader.py "https://youtu.be/VIDEO_ID"
```

---

## 🔧 Troubleshooting

### "Download Failed" / Bot Detection
YouTube aggressively blocks bots. This project uses smart fallbacks:
- **Video**: Automatically selects "Best Available" quality to ensure success.
- **Audio**: Conversion happens server-side using FFmpeg.

### "FFmpeg not found"
FFmpeg is required for audio conversion.
- **Windows**: `winget install Gyan.FFmpeg`
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect YouTube's Terms of Service and copyright laws. Only download content you have the right to download.
