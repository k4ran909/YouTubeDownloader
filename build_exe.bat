@echo off
TITLE Building YouTube Downloader EXE
CLS
ECHO ======================================================================
ECHO                Building YouTube Downloader EXE
ECHO ======================================================================
ECHO.

:: Check/Install PyInstaller
python -m pip install pyinstaller customtkinter >nul 2>&1

:: Clean previous build
ECHO [INFO] Cleaning previous build files...
IF EXIST "dist" RMDIR /S /Q "dist"
IF EXIST "build" RMDIR /S /Q "build"
IF EXIST "*.spec" DEL /Q "*.spec"

:: Build EXE
ECHO [INFO] Building executable... This may take a minute.
ECHO.
python -m PyInstaller --noconfirm --onefile --windowed --name "YouTubeDownloader" --collect-all customtkinter youtube_downloader_gui.py

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Build Failed!
    PAUSE
    EXIT /B
)

ECHO.
ECHO ======================================================================
ECHO [SUCCESS] Build Complete!
ECHO.
ECHO Your new executable is located in the "dist" folder:
ECHO %~dp0dist\YouTubeDownloader.exe
ECHO ======================================================================
PAUSE
