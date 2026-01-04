import { useState } from 'react';
import axios from 'axios';
import { ThemeProvider } from 'next-themes';
import CinematicThemeSwitcher from './components/ThemeSwitcher';
import {
  CloudDownload, Search, Loader2, Video, Music, List, ShieldCheck,
  AlertCircle
} from 'lucide-react';

function App() {
  const [url, setUrl] = useState('');
  const [info, setInfo] = useState<any>(null);
  const [formats, setFormats] = useState<any[]>([]);
  const [downloadType, setDownloadType] = useState<'video' | 'audio'>('video');
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [status, setStatus] = useState<'idle' | 'analyzing' | 'downloading' | 'completed' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  // Use environment variable for production, fallback to localhost for dev
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

  const analyze = async () => {
    if (!url) return;
    setStatus('analyzing');
    setErrorMsg('');
    setInfo(null);
    try {
      const res = await axios.post(`${backendUrl}/info`, { url });
      setInfo(res.data);
      setFormats(res.data.formats);
      // Select first format by default
      if (res.data.formats && res.data.formats.length > 0) {
        setSelectedFormat(JSON.stringify(res.data.formats[0]));
      }
      setStatus('idle');
    } catch (e: any) {
      setStatus('error');
      setErrorMsg(e.response?.data?.error || 'Failed to analyze URL');
    }
  };

  const download = async () => {
    if (!selectedFormat) return;
    setStatus('downloading');
    setErrorMsg('');
    try {
      const fmt = JSON.parse(selectedFormat);
      const res = await axios.post(`${backendUrl}/download`, {
        url,
        type: fmt.type,
        quality: fmt.quality
      });

      const { download_url } = res.data;
      // Trigger download
      window.location.href = `http://localhost:5000${download_url}`;
      setStatus('completed');
    } catch (e: any) {
      setStatus('error');
      setErrorMsg(e.response?.data?.error || 'Download failed');
    }
  };

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <div className="min-h-screen transition-colors duration-300">

        {/* Navbar */}
        <nav className="fixed top-0 w-full z-50 glass border-b border-white/5 bg-white/70 dark:bg-black/70">
          <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
            <div className="flex items-center gap-2 font-heading font-bold text-2xl">
              <CloudDownload className="text-brand-blue" />
              <span>YouTube Downloader <span className="text-xs bg-brand-blue/20 text-brand-blue px-2 py-0.5 rounded ml-2">PRO</span></span>
            </div>
            <div className="flex items-center gap-6">

              <CinematicThemeSwitcher />
            </div>
          </div>
        </nav>

        {/* Hero */}
        <main className="pt-32 pb-20 px-6 max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h1 className="text-5xl lg:text-7xl font-bold font-heading leading-tight animate-fade-up">
              Download Content <br />
              <span className="gradient-text">From YouTube</span>
            </h1>
            <p className="text-lg text-slate-500 dark:text-slate-400 max-w-xl animate-fade-up" style={{ animationDelay: '0.1s' }}>
              The most powerful open-source downloader. Supports YouTube, TikTok, Twitter, Instagram, and 1000+ others.
            </p>

            {/* Input Area */}
            <div className="glass p-2 rounded-full flex gap-2 w-full max-w-lg animate-fade-up shadow-2xl" style={{ animationDelay: '0.2s' }}>
              <input
                type="text"
                placeholder="Paste video link (YouTube, TikTok, Instagram...)"
                className="flex-1 bg-transparent border-none outline-none px-6 text-slate-800 dark:text-white placeholder:text-slate-400"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && analyze()}
              />
              <button
                onClick={analyze}
                disabled={status === 'analyzing'}
                className="bg-brand-blue hover:bg-blue-600 text-white px-8 py-3 rounded-full font-semibold transition-all hover:shadow-lg hover:shadow-blue-500/20 disabled:opacity-50 flex items-center gap-2"
              >
                {status === 'analyzing' ? <Loader2 className="animate-spin" /> : <><Search size={20} /> Start</>}
              </button>
            </div>

            {/* Error Message */}
            {status === 'error' && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl flex items-center gap-3 animate-fade-up">
                <AlertCircle /> {errorMsg}
              </div>
            )}

            {/* Result Card */}
            {info && (
              <div className="glass-card animate-fade-up">
                <div className="flex gap-4 mb-6">
                  {info.thumbnail && <img src={info.thumbnail} alt={info.title} className="w-32 h-20 object-cover rounded-lg shadow-md" />}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold truncate" title={info.title}>{info.title}</h3>
                    <p className="text-sm text-slate-500">{info.author} • {info.duration}</p>
                  </div>
                </div>

                <div className="bg-slate-100 dark:bg-zinc-900/50 p-1 rounded-lg flex gap-1 mb-6">
                  <button
                    onClick={() => {
                      setDownloadType('video');
                      const vid = formats.find(f => f.type === 'video');
                      if (vid) setSelectedFormat(JSON.stringify(vid));
                    }}
                    className={`flex-1 py-2 rounded-md text-sm font-semibold transition-all ${downloadType === 'video'
                      ? 'bg-white dark:bg-zinc-800 shadow-sm text-brand-blue'
                      : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                      }`}
                  >
                    Video
                  </button>
                  <button
                    onClick={() => {
                      setDownloadType('audio');
                      const aud = formats.find(f => f.type === 'audio');
                      if (aud) setSelectedFormat(JSON.stringify(aud));
                    }}
                    className={`flex-1 py-2 rounded-md text-sm font-semibold transition-all ${downloadType === 'audio'
                      ? 'bg-white dark:bg-zinc-800 shadow-sm text-brand-purple'
                      : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                      }`}
                  >
                    Audio
                  </button>
                </div>

                <div className="space-y-4">
                  <select
                    className="w-full bg-black/5 dark:bg-black/20 border border-black/10 dark:border-white/10 rounded-lg p-3 outline-none focus:border-brand-blue/50 text-slate-800 dark:text-white"
                    onChange={(e) => setSelectedFormat(e.target.value)}
                    value={selectedFormat}
                  >
                    {formats.filter(f => f.type === downloadType).map((f, i) => (
                      <option key={i} value={JSON.stringify(f)}>{f.label}</option>
                    ))}
                  </select>

                  <button
                    onClick={download}
                    disabled={status === 'downloading'}
                    className="w-full bg-gradient-to-r from-brand-blue to-brand-purple text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:scale-[1.02] transition-all disabled:opacity-50 flex justify-center items-center gap-2"
                  >
                    {status === 'downloading' ? (
                      <>
                        <Loader2 className="animate-spin" /> Processing Server-Side...
                      </>
                    ) : (
                      <>
                        <CloudDownload /> Download Now
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

          </div>

          {/* Feature Grid / Image */}
          <div className="relative animate-fade-right" style={{ animationDelay: '0.3s' }}>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: Video, color: 'text-blue-500', bg: 'bg-blue-500/10', title: '4K Support', desc: 'Crystal clear video' },
                { icon: Music, color: 'text-purple-500', bg: 'bg-purple-500/10', title: 'MP3 Audio', desc: 'High quality extraction' },
                { icon: List, color: 'text-pink-500', bg: 'bg-pink-500/10', title: 'Playlists', desc: 'Batch downloading' },
                { icon: ShieldCheck, color: 'text-green-500', bg: 'bg-green-500/10', title: 'Secure', desc: 'No tracking' },
              ].map((item, i) => (
                <div key={i} className="glass-card hover:-translate-y-2">
                  <div className={`w-12 h-12 ${item.bg} ${item.color} rounded-xl flex items-center justify-center mb-4`}>
                    <item.icon />
                  </div>
                  <h3 className="font-bold mb-1">{item.title}</h3>
                  <p className="text-sm text-slate-500">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </main>

      </div>
    </ThemeProvider>
  );
}

export default App;
