import tkinter as tk
import customtkinter as ctk
import threading
import sys
import os
import shutil
from tkinter import filedialog, messagebox
import yt_dlp
import re
import time
import random

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MyLogger:
    def __init__(self, gui):
        self.gui = gui
    
    def debug(self, msg):
        if not msg.startswith('[debug] '):
            self.gui.log_message(msg)
    
    def info(self, msg):
        self.gui.log_message(msg)

    def warning(self, msg):
        self.gui.log_message(f"[Warning] {msg}")

    def error(self, msg):
        self.gui.log_message(f"[Error] {msg}")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("YouTube Downloader Pro")
        self.geometry("800x600")
        self.resizable(False, False)

        # Variables
        self.url_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="video")
        self.quality_var = tk.StringVar(value="Best")
        self.status_var = tk.StringVar(value="Ready")
        self.playlist_option_var = tk.StringVar(value="video") # 'video', 'playlist', 'select'
        self.download_folder = os.getcwd()

        # Cookies file path
        self.cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

        # Create UI
        self.create_widgets()
        
        # Check FFmpeg
        self.check_ffmpeg()

    def create_widgets(self):
        # Allow grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # === Header ===
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="YouTube Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        # === URL Input ===
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="YouTube URL:")
        self.url_label.pack(side="left", padx=10, pady=10)
        
        self.url_entry = ctk.CTkEntry(self.url_frame, textvariable=self.url_var, width=500, placeholder_text="Paste video or playlist URL here...")
        self.url_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # === Options Frame ===
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Mode Selection
        self.mode_label = ctk.CTkLabel(self.options_frame, text="Mode:", font=ctk.CTkFont(weight="bold"))
        self.mode_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.radio_video = ctk.CTkRadioButton(self.options_frame, text="Video (MP4)", variable=self.mode_var, value="video", command=self.update_quality_options)
        self.radio_video.grid(row=0, column=1, padx=10, pady=10)

        self.radio_audio = ctk.CTkRadioButton(self.options_frame, text="Audio (MP3)", variable=self.mode_var, value="audio", command=self.update_quality_options)
        self.radio_audio.grid(row=0, column=2, padx=10, pady=10)

        # Quality Selection
        self.quality_label = ctk.CTkLabel(self.options_frame, text="Quality:", font=ctk.CTkFont(weight="bold"))
        self.quality_label.grid(row=0, column=3, padx=15, pady=10, sticky="w")

        self.quality_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.quality_var, values=["Best", "2160p", "1440p", "1080p", "720p", "480p", "360p"])
        self.quality_menu.grid(row=0, column=4, padx=10, pady=10)

        # === Playlist Options (Hidden by default) ===
        self.playlist_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.playlist_label = ctk.CTkLabel(self.playlist_frame, text="Playlist Detected:", text_color="#3B8ED0", font=ctk.CTkFont(weight="bold"))
        self.playlist_label.pack(side="left", padx=(0, 10))
        
        self.dl_single_btn = ctk.CTkRadioButton(self.playlist_frame, text="Download Video Only", variable=self.playlist_option_var, value="video")
        self.dl_single_btn.pack(side="left", padx=10)
        
        self.dl_playlist_btn = ctk.CTkRadioButton(self.playlist_frame, text="Download Entire Playlist", variable=self.playlist_option_var, value="playlist")
        self.dl_playlist_btn.pack(side="left", padx=10)
        
        # === Authentication Frame ===
        self.auth_frame = ctk.CTkFrame(self)
        self.auth_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.auth_label = ctk.CTkLabel(self.auth_frame, text="Auth / Cookies:", font=ctk.CTkFont(weight="bold"))
        self.auth_label.pack(side="left", padx=15, pady=10)

        self.cookie_source_var = tk.StringVar(value="None")
        self.cookie_source_menu = ctk.CTkOptionMenu(
            self.auth_frame, 
            variable=self.cookie_source_var, 
            values=["None", "Chrome", "Firefox", "Edge", "Opera", "Brave", "Select File..."],
            command=self.on_cookie_source_change,
            width=150
        )
        self.cookie_source_menu.pack(side="left", padx=5, pady=10)

        self.browse_btn = ctk.CTkButton(self.auth_frame, text="Browse...", width=80, command=self.browse_cookie_file)
        self.auth_path_label = ctk.CTkLabel(self.auth_frame, text="", text_color="gray")

        # === Download Button & Status ===
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        self.download_btn = ctk.CTkButton(self.action_frame, text="Start Download", font=ctk.CTkFont(size=15, weight="bold"), height=40, command=self.start_download_thread)
        self.download_btn.pack(fill="x")
        
        # === Stats Frame ===
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="ew")
        
        self.stat_speed = ctk.CTkLabel(self.stats_frame, text="Speed: -", font=("Consolas", 12))
        self.stat_speed.pack(side="left", padx=10, expand=True)
        
        self.stat_eta = ctk.CTkLabel(self.stats_frame, text="ETA: -", font=("Consolas", 12))
        self.stat_eta.pack(side="left", padx=10, expand=True)
        
        self.stat_size = ctk.CTkLabel(self.stats_frame, text="Size: -", font=("Consolas", 12))
        self.stat_size.pack(side="left", padx=10, expand=True)

        # === Console / Log ===
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.log_textbox = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12))
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_textbox.configure(state="disabled")

        # === Progress Bar ===
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        # Bind URL change to detect playlist
        self.url_var.trace_add("write", self.on_url_change)
        
        # Initial Auth State
        self.custom_cookie_file = None

        # Row configuration
        self.grid_rowconfigure(6, weight=1) 

    def check_ffmpeg(self):
        if not shutil.which('ffmpeg'):
            self.log_message("[WARNING] FFmpeg not found! Audio conversion may fail.")
            self.log_message("Please install FFmpeg and add it to your PATH.")
        else:
            self.log_message("[System] FFmpeg detected.")

    def log_message(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def update_quality_options(self):
        mode = self.mode_var.get()
        if mode == "video":
            values = ["Best", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
            self.quality_var.set("Best")
        else:
            values = ["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "64 kbps"]
            self.quality_var.set("320 kbps")
        
        self.quality_menu.configure(values=values)

    def on_url_change(self, *args):
        url = self.url_var.get()
        
        if 'list=' in url and not 'start_radio=' in url:
            # Shift for Playlist UI
            self.playlist_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
            self.auth_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
            self.action_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
            self.stats_frame.grid(row=6, column=0, padx=20, pady=(0, 5), sticky="ew")
            self.log_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="nsew")
            self.progress_bar.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")
            
            # Check for Radio playlist
            if 'list=RD' in url:
                self.dl_playlist_btn.configure(state="disabled", text="Playlist (Radio - Not Downloadable)")
                self.playlist_option_var.set("video")
            else:
                self.dl_playlist_btn.configure(state="normal", text="Download Entire Playlist")
            
            self.grid_rowconfigure(6, weight=0)
            self.grid_rowconfigure(7, weight=1) # Log frame expanvsion
            
        else:
            self.playlist_frame.grid_forget()
            # Standard UI
            self.auth_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
            self.action_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
            self.stats_frame.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="ew")
            self.log_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
            self.progress_bar.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
            
            self.grid_rowconfigure(6, weight=1) # Log frame expansion
            self.grid_rowconfigure(7, weight=0)

    def on_cookie_source_change(self, choice):
        if choice == "Select File...":
            self.browse_btn.pack(side="left", padx=5)
            self.auth_path_label.pack(side="left", padx=5)
            if not self.auth_path_label.cget("text"):
                self.browse_cookie_file()
        else:
            self.browse_btn.pack_forget()
            self.auth_path_label.pack_forget()
            self.custom_cookie_file = None

    def browse_cookie_file(self):
        filename = filedialog.askopenfilename(title="Select Cookies File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.custom_cookie_file = filename
            basename = os.path.basename(filename)
            self.auth_path_label.configure(text=basename if len(basename) < 20 else basename[:17]+"...")
        elif not self.custom_cookie_file:
            self.cookie_source_var.set("None")
            self.on_cookie_source_change("None")

    def start_download_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please provide a URL")
            return

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.run_download)
        thread.daemon = True
        thread.start()

    def run_download(self):
        try:
            url = self.url_var.get().strip()
            mode = self.mode_var.get()
            quality = self.quality_var.get()
            playlist_choice = self.playlist_option_var.get()
            cookie_source = self.cookie_source_var.get()
            
            # Determine if we are downloading playlist
            download_playlist = False
            if 'list=' in url and playlist_choice == 'playlist':
                download_playlist = True
            
            # Configure Options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'noplaylist': not download_playlist,
                # VPS Options
                'geo_bypass': True,
                'retries': 10,
                'sleep_interval': 1,
            }

            # === Authentication Logic ===
            if cookie_source == "Select File..." and self.custom_cookie_file:
                if os.path.exists(self.custom_cookie_file):
                    ydl_opts['cookiefile'] = self.custom_cookie_file
                    self.log_message(f"[Auth] Using Cookie File: {os.path.basename(self.custom_cookie_file)}")
                else:
                    self.log_message(f"[Warning] Selected cookie file not found!")
            
            elif cookie_source in ["Chrome", "Firefox", "Edge", "Opera", "Brave"]:
                browser_map = {
                    "Chrome": "chrome", "Firefox": "firefox", "Edge": "edge", 
                    "Opera": "opera", "Brave": "brave"
                }
                browser_key = browser_map.get(cookie_source)
                if browser_key:
                    ydl_opts['cookiesfrombrowser'] = (browser_key,)
                    self.log_message(f"[Auth] Extracting cookies from {cookie_source}...")
            
            elif os.path.exists(self.cookies_file) and cookie_source == "None":
                 pass

            # Video Mode
            if mode == "video":
                quality_map = {
                    'Best': 'bestvideo+bestaudio/best',
                    '2160p': 'bestvideo[height<=2160]+bestaudio/best',
                    '1440p': 'bestvideo[height<=1440]+bestaudio/best',
                    '1080p': 'bestvideo[height<=1080]+bestaudio/best',
                    '720p': 'bestvideo[height<=720]+bestaudio/best',
                    '480p': 'bestvideo[height<=480]+bestaudio/best',
                    '360p': 'bestvideo[height<=360]+bestaudio/best',
                }
                format_str = quality_map.get(quality, 'bestvideo+bestaudio/best')
                ydl_opts.update({
                    'format': format_str,
                    'merge_output_format': 'mp4',
                    'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if download_playlist else '%(title)s.%(ext)s',
                })
                self.log_message(f"[Start] Downloading Video ({quality})...")

            # Audio Mode
            else:
                quality_val = quality.split()[0] # "320 kbps" -> "320"
                audio_map = {'320': '0', '256': '1', '192': '2', '128': '5', '96': '6', '64': '8'}
                
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if download_playlist else '%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_map.get(quality_val, '0'),
                    }],
                })
                self.log_message(f"[Start] Downloading Audio ({quality})...")

            # Start Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log_message(f"Processing: {url}")
                ydl.download([url])
            
            self.log_message("[Success] Download Completed!")
            messagebox.showinfo("Success", "Download Completed Successfully!")

        except Exception as e:
            error_msg = str(e)
            self.log_message(f"[Error] {error_msg}")
            
            # Check for specific browser cookie error
            if "Could not copy" in error_msg and "cookie database" in error_msg:
                messagebox.showerror("Browser Error", 
                    f"Could not access {self.cookie_source_var.get()} cookies.\n\n"
                    "Please CLOSE your browser completely and try again.\n"
                    "(The database is locked while the browser is open)"
                )
            
            # Check for DPAPI/Decryption error
            elif "decrypt" in error_msg and "DPAPI" in error_msg:
                messagebox.showerror("Encryption Error", 
                    f"Could not decrypt {self.cookie_source_var.get()} cookies.\n\n"
                    "Chrome's encryption is blocking access.\n"
                    "Workarounds:\n"
                    "1. Try using Firefox (it works better)\n"
                    "2. Or select 'Select File...' and use a manually exported cookies.txt"
                )
            else:
                messagebox.showerror("Error", f"Download Failed:\n{error_msg}")
        
        finally:
            self.download_btn.configure(state="normal", text="Start Download")
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Update progress bar
                if 'total_bytes' in d:
                    p = d['downloaded_bytes'] / d['total_bytes']
                    self.progress_bar.set(p)
                elif 'total_bytes_estimate' in d:
                    p = d['downloaded_bytes'] / d['total_bytes_estimate']
                    self.progress_bar.set(p)

                # Update stats labels
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                # Size formatting
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                if total_bytes:
                    size_mb = total_bytes / 1024 / 1024
                    size_str = f"{size_mb:.1f} MiB"
                else:
                    size_str = "N/A"

                self.stat_speed.configure(text=f"Speed: {speed}")
                self.stat_eta.configure(text=f"ETA: {eta}")
                self.stat_size.configure(text=f"Size: {size_str}")

                self.progress_bar.configure(mode="determinate")
            except Exception as e:
                # print(e)
                pass
        
        elif d['status'] == 'finished':
            self.log_message("Download finished. Processing/Converting...")
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.stat_speed.configure(text="Speed: -")
            self.stat_eta.configure(text="ETA: Complete")

    def on_cookie_source_change(self, choice):
        if choice == "Select File...":
            self.browse_btn.pack(side="left", padx=5)
            self.auth_path_label.pack(side="left", padx=5)
            if not self.auth_path_label.cget("text"):
                self.browse_cookie_file()
        else:
            self.browse_btn.pack_forget()
            self.auth_path_label.pack_forget()
            self.custom_cookie_file = None

    def browse_cookie_file(self):
        filename = filedialog.askopenfilename(title="Select Cookies File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.custom_cookie_file = filename
            basename = os.path.basename(filename)
            self.auth_path_label.configure(text=basename if len(basename) < 20 else basename[:17]+"...")
        elif not self.custom_cookie_file:
            self.cookie_source_var.set("None")
            self.on_cookie_source_change("None")

    def start_download_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please provide a URL")
            return

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.run_download)
        thread.daemon = True
        thread.start()

    def run_download(self):
        try:
            url = self.url_var.get().strip()
            mode = self.mode_var.get()
            quality = self.quality_var.get()
            playlist_choice = self.playlist_option_var.get()
            cookie_source = self.cookie_source_var.get()
            
            # Determine if we are downloading playlist
            download_playlist = False
            if 'list=' in url and playlist_choice == 'playlist':
                download_playlist = True
            
            # Configure Options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'logger': MyLogger(self),
                'noplaylist': not download_playlist,
                # VPS Options
                'geo_bypass': True,
                'retries': 10,
                'sleep_interval': 1,
            }

            # === Authentication Logic ===
            if cookie_source == "Select File..." and self.custom_cookie_file:
                if os.path.exists(self.custom_cookie_file):
                    ydl_opts['cookiefile'] = self.custom_cookie_file
                    self.log_message(f"[Auth] Using Cookie File: {os.path.basename(self.custom_cookie_file)}")
                else:
                    self.log_message(f"[Warning] Selected cookie file not found!")
            
            elif cookie_source in ["Chrome", "Firefox", "Edge", "Opera", "Brave"]:
                browser_map = {
                    "Chrome": "chrome", "Firefox": "firefox", "Edge": "edge", 
                    "Opera": "opera", "Brave": "brave"
                }
                browser_key = browser_map.get(cookie_source)
                if browser_key:
                    ydl_opts['cookiesfrombrowser'] = (browser_key,)
                    self.log_message(f"[Auth] Extracting cookies from {cookie_source}...")
            
            elif os.path.exists(self.cookies_file) and cookie_source == "None":
                 pass

            # Video Mode
            if mode == "video":
                quality_map = {
                    'Best': 'bestvideo+bestaudio/best',
                    '2160p': 'bestvideo[height<=2160]+bestaudio/best',
                    '1440p': 'bestvideo[height<=1440]+bestaudio/best',
                    '1080p': 'bestvideo[height<=1080]+bestaudio/best',
                    '720p': 'bestvideo[height<=720]+bestaudio/best',
                    '480p': 'bestvideo[height<=480]+bestaudio/best',
                    '360p': 'bestvideo[height<=360]+bestaudio/best',
                }
                format_str = quality_map.get(quality, 'bestvideo+bestaudio/best')
                ydl_opts.update({
                    'format': format_str,
                    'merge_output_format': 'mp4',
                    'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if download_playlist else '%(title)s.%(ext)s',
                })
                self.log_message(f"[Start] Downloading Video ({quality})...")

            # Audio Mode
            else:
                quality_val = quality.split()[0] # "320 kbps" -> "320"
                audio_map = {'320': '0', '256': '1', '192': '2', '128': '5', '96': '6', '64': '8'}
                
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s' if download_playlist else '%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_map.get(quality_val, '0'),
                    }],
                })
                self.log_message(f"[Start] Downloading Audio ({quality})...")

            # Start Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log_message(f"Processing: {url}")
                ydl.download([url])
            
            self.log_message("[Success] Download Completed!")
            messagebox.showinfo("Success", "Download Completed Successfully!")

        except Exception as e:
            error_msg = str(e)
            self.log_message(f"[Error] {error_msg}")
            
            # Check for specific browser cookie error
            if "Could not copy" in error_msg and "cookie database" in error_msg:
                messagebox.showerror("Browser Error", 
                    f"Could not access {self.cookie_source_var.get()} cookies.\n\n"
                    "Please CLOSE your browser completely and try again.\n"
                    "(The database is locked while the browser is open)"
                )
            
            # Check for DPAPI/Decryption error
            elif "decrypt" in error_msg and "DPAPI" in error_msg:
                messagebox.showerror("Encryption Error", 
                    f"Could not decrypt {self.cookie_source_var.get()} cookies.\n\n"
                    "Chrome's encryption is blocking access.\n"
                    "Workarounds:\n"
                    "1. Try using Firefox (it works better)\n"
                    "2. Or select 'Select File...' and use a manually exported cookies.txt"
                )
            else:
                messagebox.showerror("Error", f"Download Failed:\n{error_msg}")
        
        finally:
            self.download_btn.configure(state="normal", text="Start Download")
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(1)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Update progress bar
                if 'total_bytes' in d:
                    p = d['downloaded_bytes'] / d['total_bytes']
                    self.progress_bar.set(p)
                    self.progress_bar.configure(mode="determinate")
                
                # Log progress (throttled)
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                # We don't want to spam the log, so maybe just last line update?
                # For this simple GUI, we will just print to console which redirects to our log
                # But tkinter isn't thread safe for UI updates from hook
                # So we won't spam the text box, just the progress bar
            except:
                pass
        
        elif d['status'] == 'finished':
            self.log_message("Download finished. Processing/Converting...")
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
