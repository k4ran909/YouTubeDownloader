from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import yt_dlp
import os
import time
import glob

app = Flask(__name__, static_folder='website', template_folder='website')

# Ensure temp directory exists
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_downloads')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Cleanup old files on startup
def cleanup_temp():
    try:
        now = time.time()
        for f in glob.glob(os.path.join(TEMP_DIR, '*')):
            if os.stat(f).st_mtime < now - 3600: # Remove files older than 1 hour
                os.remove(f)
    except:
        pass

cleanup_temp()

@app.route('/')
def home():
    return send_file('website/index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_file(f'website/{path}')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract relevant formats
            formats = []
            
            # Video formats
            video_formats = {} # Dedup by height
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    h = f['height']
                    # Prefer mp4 container
                    if f.get('ext') == 'mp4':
                        video_formats[h] = f['format_id']
            
            # Sort heights desc
            for h in sorted(video_formats.keys(), reverse=True):
                formats.append({
                    'type': 'video',
                    'quality': f"{h}p",
                    'format_id': video_formats[h], # We will use special logic for download to merge audio
                    'label': f"Video (MP4) - {h}p"
                })
                
            # Audio format
            formats.append({
                'type': 'audio',
                'quality': '320kbps',
                'format_id': 'bestaudio',
                'label': "Audio (MP3) - Best Quality"
            })

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration_string') or info.get('duration'),
                'author': info.get('uploader'),
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format_type = data.get('type') # 'video' or 'audio'
    quality = data.get('quality') # e.g. '1080p' or '320kbps'
    
    if not url:
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Create unique filename ID
        timestamp = int(time.time())
        output_template = os.path.join(TEMP_DIR, f'%(title)s_{timestamp}.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            # Use project bin ffmpeg if available
            'ffmpeg_location': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin'),
        }

        if format_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # Video
            height = quality.replace('p', '')
            ydl_opts.update({
                'format': f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            # Verify file exists
            if not os.path.exists(filename):
                # Sometimes file extension differs
                base = os.path.splitext(filename)[0]
                for ext in ['.mp4', '.mkv', '.webm', '.mp3']:
                    if os.path.exists(base + ext):
                        filename = base + ext
                        break

            if not os.path.exists(filename):
                return jsonify({'error': 'Download failed to produce file'}), 500

            # Schedule cleanup after sending
            @after_this_request
            def remove_file(response):
                try:
                    # Delay slightly or just rely on global cleanup if lock issues occur on Windows
                    # Windows often locks files being sent. 
                    # We will comment out immediate delete and rely on periodic cleanup or try/except
                    # os.remove(filename) 
                    pass
                except Exception as e:
                    print(e)
                return response

            return jsonify({
                'download_url': f'/api/files/{os.path.basename(filename)}',
                'filename': os.path.basename(filename)
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<filename>')
def serve_file(filename):
    # Security check: ensure no path traversal
    filename = os.path.basename(filename)
    return send_file(os.path.join(TEMP_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    print("Starting Web App on http://localhost:5000")
    app.run(debug=True, port=5000)
