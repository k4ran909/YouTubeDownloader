document.addEventListener('DOMContentLoaded', () => {

    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultCard = document.getElementById('resultCard');
    const videoThumb = document.getElementById('videoThumb');
    const videoTitle = document.getElementById('videoTitle');
    const videoMeta = document.getElementById('videoMeta');
    const formatSelect = document.getElementById('formatSelect');
    const downloadBtn = document.getElementById('downloadBtn');
    const statusMsg = document.getElementById('statusMsg');
    const loadingBar = document.getElementById('loadingBar');

    // Smooth Scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Analyze Click
    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a valid YouTube URL');
            return;
        }

        // UI Reset
        analyzeBtn.innerHTML = '<ion-icon name="sync"></ion-icon> Analyzing...';
        analyzeBtn.disabled = true;
        statusMsg.textContent = 'Fetching video info...';
        resultCard.style.display = 'none';

        try {
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (data.error) throw new Error(data.error);

            // Populate Info
            videoTitle.textContent = data.title;
            videoThumb.src = data.thumbnail;
            videoMeta.textContent = `Duration: ${data.duration} | By: ${data.author}`;

            // Populate Formats
            formatSelect.innerHTML = '';
            data.formats.forEach(fmt => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify({
                    type: fmt.type,
                    quality: fmt.quality,
                    format_id: fmt.format_id
                });
                opt.textContent = fmt.label;
                formatSelect.appendChild(opt);
            });

            // Show Result
            resultCard.style.display = 'block';
            statusMsg.textContent = '';

        } catch (err) {
            statusMsg.textContent = `Error: ${err.message}`;
        } finally {
            analyzeBtn.innerHTML = '<ion-icon name="search"></ion-icon> Start';
            analyzeBtn.disabled = false;
        }
    });

    // Download Click
    downloadBtn.addEventListener('click', async () => {
        const formatData = JSON.parse(formatSelect.value);
        const url = urlInput.value.trim();

        // UI
        downloadBtn.innerHTML = '<ion-icon name="cloud-download"></ion-icon> Processing...';
        downloadBtn.disabled = true;
        loadingBar.style.display = 'block';
        statusMsg.textContent = 'Downloading and converting on server... Large videos may take time!';

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    type: formatData.type,
                    quality: formatData.quality
                })
            });

            const data = await response.json();

            if (data.error) throw new Error(data.error);

            // Trigger Download
            statusMsg.textContent = 'Starting file download...';
            window.location.href = data.download_url;

        } catch (err) {
            statusMsg.textContent = `Download Error: ${err.message}`;
        } finally {
            downloadBtn.innerHTML = '<ion-icon name="cloud-download"></ion-icon> Download Now';
            downloadBtn.disabled = false;
            loadingBar.style.display = 'none';
        }
    });

    // Cinematic Theme Switcher Logic
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    let isAnimating = false;

    // Check saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.add('light-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            if (isAnimating) return;
            isAnimating = true;

            // Toggle Theme
            body.classList.toggle('light-mode');
            const isLight = body.classList.contains('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');

            // Generate Particles
            // Create 3 layers of particles
            for (let i = 0; i < 3; i++) {
                createParticleClone(i);
            }

            setTimeout(() => {
                isAnimating = false;
            }, 800);
        });
    }

    function createParticleClone(index) {
        if (!themeToggle) return;
        const particle = document.createElement('div');
        particle.classList.add('particle');

        // Stagger animation
        particle.style.animationDelay = `${index * 0.1}s`;
        particle.style.animationDuration = `${0.6 + index * 0.1}s`;

        const thumb = themeToggle.querySelector('.theme-switch-thumb');
        if (thumb) thumb.appendChild(particle);

        // Force reflow
        void particle.offsetWidth;

        particle.classList.add('exploding');

        setTimeout(() => {
            particle.remove();
        }, 1000);
    }

});
