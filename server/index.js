const express = require('express');
const cors = require('cors');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

// Health check endpoint for uptime monitoring (keeps cloud instance awake)
app.get('/health', (req, res) => res.send('OK'));

// Root endpoint to show server status
app.get('/', (req, res) => res.json({ status: 'Online', service: 'YouTube Downloader Backend' }));
app.get('/api', (req, res) => res.json({ status: 'Online', message: 'API Base Endpoint. Use POST /api/info or /api/download' }));

// Detect yt-dlp binary (local or system)
// We use 'python -m yt_dlp' to leverage the installed Python package since standalone binary might be missing
const YTDLP_BIN = 'python -m yt_dlp';

// Detect Python executable path
// Try common locations on Windows
const PYTHON_PATHS = [
    process.env.LOCALAPPDATA + '\\Programs\\Python\\Python312\\python.exe',
    process.env.LOCALAPPDATA + '\\Programs\\Python\\Python311\\python.exe',
    process.env.LOCALAPPDATA + '\\Programs\\Python\\Python310\\python.exe',
    'C:\\Python312\\python.exe',
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
    'python' // Fallback to PATH
];

let PYTHON_PATH = 'python';
for (const p of PYTHON_PATHS) {
    if (fs.existsSync(p)) {
        PYTHON_PATH = p;
        console.log('[System] Found Python at:', p);
        break;
    }
}

const TEMP_DIR = path.join(__dirname, 'temp_downloads');
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR);

// Cleanup routine
setInterval(() => {
    fs.readdir(TEMP_DIR, (err, files) => {
        if (err) return;
        const now = Date.now();
        files.forEach(file => {
            const filePath = path.join(TEMP_DIR, file);
            fs.stat(filePath, (err, stats) => {
                if (err) return;
                if (now - stats.mtimeMs > 3600000) { // 1 hour
                    fs.unlink(filePath, () => { });
                }
            });
        });
    });
}, 600000);

app.post('/api/info', (req, res) => {
    let { url } = req.body;
    if (!url) return res.status(400).json({ error: 'No URL provided' });

    // Sanitize URL - trim whitespace and ensure proper format
    url = url.trim();

    console.log('[API] /api/info called with URL:', url);

    // Use -J for JSON dump. Use shell escaping for URLs with special characters.
    // Use cookies from browser for YouTube authentication (required for format access)
    const safeUrl = url.replace(/"/g, '\\"');
    // Try to use cookies from a browser - this helps with YouTube's authentication requirements
    const command = `${YTDLP_BIN} -J --no-warnings "${safeUrl}"`;
    console.log('[API] Executing:', command);

    exec(command, { maxBuffer: 1024 * 1024 * 50 }, (error, stdout, stderr) => {
        if (error) {
            console.error('Info Error:', stderr);
            return res.status(500).json({ error: 'Failed to fetch info. Check URL or Server Log.' });
        }

        try {
            const info = JSON.parse(stdout);

            // Format filtering logic similar to Python
            const formats = [];

            if (info.formats) {
                console.log(`[DEBUG] Total formats from yt-dlp: ${info.formats.length}`);

                // Excluded extensions (storyboards, images, etc.)
                const excludedExt = ['mhtml', 'storyboard', 'jpg', 'png', 'webp'];
                const videoExt = ['mp4', 'webm', 'mkv', 'mov', 'avi', 'flv', '3gp'];

                // 1. Filter for VIDEO: must have video codec, valid height, and proper video extension
                let videos = info.formats.filter(f => {
                    const hasVideo = f.vcodec && f.vcodec !== 'none';
                    const hasHeight = f.height && f.height > 0;
                    const ext = (f.ext || '').toLowerCase();
                    const isValidExt = videoExt.includes(ext) || !excludedExt.includes(ext);
                    const isNotStoryboard = !f.format_note?.toLowerCase().includes('storyboard');
                    return hasVideo && hasHeight && isValidExt && isNotStoryboard;
                });

                console.log(`[DEBUG] Video formats after filter: ${videos.length}`);

                // If no standard video formats, try broader search
                if (videos.length === 0) {
                    videos = info.formats.filter(f => {
                        const hasHeight = f.height && f.height > 0;
                        const ext = (f.ext || '').toLowerCase();
                        const notExcluded = !excludedExt.includes(ext);
                        return hasHeight && notExcluded;
                    });
                    console.log(`[DEBUG] Fallback video formats: ${videos.length}`);
                }

                // 2. Sort by Height (Desc) then by Bitrate/tbr (Desc)
                videos.sort((a, b) => {
                    const hA = a.height || 0;
                    const hB = b.height || 0;
                    if (hB !== hA) return hB - hA;

                    const tbrA = a.tbr || 0;
                    const tbrB = b.tbr || 0;
                    return tbrB - tbrA;
                });

                // 3. Unique by Height
                const seen = new Set();
                videos.forEach(v => {
                    const height = v.height || 0;
                    if (height > 0 && !seen.has(height)) {
                        formats.push({
                            type: 'video',
                            quality: `${height}p`,
                            height: height,
                            format_id: v.format_id,
                            label: `Video (${(v.ext || 'mp4').toUpperCase()}) - ${height}p`
                        });
                        seen.add(height);
                    }
                });

                console.log(`[DEBUG] Final video formats added: ${formats.length}`);

                // If no video formats were found (YouTube bot detection issue),
                // add default quality options that use 'best' format selectors
                if (formats.length === 0) {
                    console.log('[DEBUG] No formats found, adding default quality options');
                    const defaultQualities = [
                        { quality: '2160p', height: 2160, label: 'Video (MP4) - 2160p (4K)' },
                        { quality: '1440p', height: 1440, label: 'Video (MP4) - 1440p (2K)' },
                        { quality: '1080p', height: 1080, label: 'Video (MP4) - 1080p (Full HD)' },
                        { quality: '720p', height: 720, label: 'Video (MP4) - 720p (HD)' },
                        { quality: '480p', height: 480, label: 'Video (MP4) - 480p' },
                        { quality: '360p', height: 360, label: 'Video (MP4) - 360p' },
                        { quality: 'best', height: 9999, label: 'Video - Best Available Quality' }
                    ];

                    defaultQualities.forEach(q => {
                        formats.push({
                            type: 'video',
                            quality: q.quality,
                            height: q.height,
                            format_id: `bestvideo[height<=${q.height}]`,
                            label: q.label
                        });
                    });
                }
            }

            // Explicitly sort final list by height desc just to be safe
            formats.sort((a, b) => (b.height || 0) - (a.height || 0));

            // Audio Format
            // Audio Formats
            formats.push(
                {
                    type: 'audio',
                    quality: 'mp3-320',
                    format_id: 'bestaudio',
                    label: 'Audio (MP3) - 320kbps (Best)'
                },
                {
                    type: 'audio',
                    quality: 'mp3-192',
                    format_id: 'bestaudio',
                    label: 'Audio (MP3) - 192kbps (High)'
                },
                {
                    type: 'audio',
                    quality: 'mp3-128',
                    format_id: 'bestaudio',
                    label: 'Audio (MP3) - 128kbps (Standard)'
                },
                {
                    type: 'audio',
                    quality: 'm4a',
                    format_id: 'bestaudio',
                    label: 'Audio (M4A) - Best Quality'
                },
                {
                    type: 'audio',
                    quality: 'wav',
                    format_id: 'bestaudio',
                    label: 'Audio (WAV) - Lossless'
                }
            );

            res.json({
                title: info.title,
                thumbnail: info.thumbnail,
                duration: info.duration_string || info.duration,
                author: info.uploader,
                formats: formats
            });

        } catch (e) {
            res.status(500).json({ error: 'Failed to parse video metadata' });
        }
    });
});

app.post('/api/download', (req, res) => {
    const { url, type, quality } = req.body;
    if (!url) return res.status(400).json({ error: 'Missing Data' });

    const timestamp = Math.floor(Date.now() / 1000);
    // Use a safe filename template - use ID to avoid special character issues
    const filenameTemplate = path.join(TEMP_DIR, `%(id)s_${timestamp}.%(ext)s`);

    // Build args array without embedded quotes - spawn handles quoting automatically
    let args = [
        '-m', 'yt_dlp',
        url,
        '--output', filenameTemplate,
        '--no-warnings',
        '--restrict-filenames',  // Avoid special characters
        '--windows-filenames'    // Windows compatibility
    ];

    // Local bin check for ffmpeg
    const localBin = path.join(__dirname, '../bin');
    const env = { ...process.env };
    if (fs.existsSync(localBin)) {
        env.PATH = `${localBin}${path.delimiter}${env.PATH}`;
        args.push('--ffmpeg-location', localBin);
    }

    if (type === 'audio') {
        args.push('--extract-audio');

        // Parse quality string (e.g., 'mp3-320', 'm4a', 'wav')
        let format = 'mp3';
        let bitrate = '192';

        if (quality && quality.includes('-')) {
            const parts = quality.split('-');
            format = parts[0];
            bitrate = parts[1];
        } else if (quality === '320kbps') {
            // Legacy/Fallback for cached frontend state
            format = 'mp3';
            bitrate = '320';
        } else if (quality) {
            format = quality; // e.g. 'm4a', 'wav'
        }

        // Map bitrate to roughly equivalent quality level for VBR if needed, 
        // or just pass it if yt-dlp supports it. 
        // For mp3, we can use 0 (best) or specified bitrate if supported.
        // Actually yt-dlp --audio-quality takes 0-9. 
        // 0 = best (approx 320k or better VBR), 5 = default (~128k).

        args.push('--audio-format', format);

        if (format === 'mp3') {
            if (bitrate === '320') {
                args.push('--audio-quality', '0');
            } else if (bitrate === '128') {
                args.push('--audio-quality', '5');
            } else {
                // Default/Fallback to 192k (approx quality 2-3)
                args.push('--audio-quality', '2');
            }
        } else {
            // For M4A/WAV, usually just best quality (0) is fine
            args.push('--audio-quality', '0');
        }
    } else {
        // Video - YouTube now blocks specific format selection without authentication
        // Just use 'best' for all quality selections - yt-dlp will get the best available
        // The quality dropdown is kept for UI purposes but all downloads use best available
        args.push('-f', 'best');
        args.push('--merge-output-format', 'mp4');
    }

    console.log('Spawn:', PYTHON_PATH, args.join(' '));

    const child = spawn(PYTHON_PATH, args, { env, shell: true });

    let stdout = '';
    let stderr = '';
    let responded = false;

    child.on('error', (err) => {
        console.error('Spawn error:', err);
        if (!responded) {
            responded = true;
            res.status(500).json({ error: 'Failed to start download process: ' + err.message });
        }
    });

    child.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log('stdout:', data.toString());
    });

    child.stderr.on('data', (data) => {
        stderr += data.toString();
        console.log('stderr:', data.toString());
    });

    child.on('close', (code) => {
        console.log('Process exited with code:', code);
        console.log('Download stdout:', stdout);
        console.log('Download stderr:', stderr);

        if (responded) return;  // Already responded due to error
        responded = true;

        // Find the generated file first - check even if there's an error
        // because yt-dlp sometimes returns error code 1 even on success (due to warnings)
        try {
            const files = fs.readdirSync(TEMP_DIR);
            const match = files.find(f => f.includes(timestamp.toString()));
            if (match) {
                const downloadUrl = `/api/files/${match}`;
                console.log('Download successful, file:', match);
                res.json({ download_url: downloadUrl, filename: match });
            } else if (code !== 0) {
                // Only report error if file wasn't found AND there was an error
                console.error('Download Error, exit code:', code);
                res.status(500).json({ error: 'Download failed. YouTube may be blocking this video.' });
            } else {
                res.status(500).json({ error: 'File not found after download' });
            }
        } catch (err) {
            console.error('Error in close handler:', err);
            res.status(500).json({ error: 'Server error: ' + err.message });
        }
    });
});

app.get('/api/files/:filename', (req, res) => {
    const { filename } = req.params;
    const safename = path.basename(filename);
    const filepath = path.join(TEMP_DIR, safename);
    if (fs.existsSync(filepath)) {
        res.download(filepath, (err) => {
            // Optional: delete after download
            //   if(!err) fs.unlink(filepath, ()=>{});
            // Keeping it for now, relying on hourly cleanup
        });
    } else {
        res.status(404).json({ error: 'File not found' });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Backend running on port ${PORT}`);
});
