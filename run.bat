@echo off
TITLE YouTube Downloader
CLS
ECHO ======================================================================
ECHO       YouTube Video/Audio Downloader Launcher
ECHO ======================================================================
ECHO.

:: Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Python is not installed or not in PATH.
    ECHO Please install Python 3.7+ from https://www.python.org/downloads/
    PAUSE
    EXIT /B
)

:: Check for required packages
python -c "import yt_dlp" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] Installing necessary dependencies...
    pip install -r requirements.txt
    ECHO.
)

:: Run the script
python youtube_downloader.py

ECHO.
ECHO Application finished.
PAUSE
