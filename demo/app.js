const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://your-api-endpoint.example.com'; // ← UPDATE FOR PRODUCTION

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(`${tab.dataset.mode}-panel`).classList.add('active');
    });
});

// Insert vocal events on chip click
document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
        const textarea = document.getElementById('text-input');
        const pos = textarea.selectionStart;
        const event = chip.dataset.event;
        textarea.value = textarea.value.slice(0, pos) + ` ${event} ` + textarea.value.slice(pos);
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = pos + event.length + 2;
    });
});

// Generate button
document.getElementById('generate-btn').addEventListener('click', async () => {
    const btn = document.getElementById('generate-btn');
    const status = document.getElementById('status');
    const audio = document.getElementById('audio-output');
    
    btn.disabled = true;
    status.textContent = '🔄 Connecting to streaming endpoint...';
    audio.src = '';

    try {
        const ws = new WebSocket(API_BASE.replace('http', 'ws') + '/v1/tts/stream');
        const chunks = [];

        ws.onopen = () => {
            status.textContent = '🌊 Streaming audio...';
            const activeMode = document.querySelector('.tab.active').dataset.mode;
            
            if (activeMode === 'design') {
                ws.send(JSON.stringify({
                    action: 'init', mode: 'design',
                    voice_description: document.getElementById('voice-desc').value
                }));
                ws.send(JSON.stringify({
                    action: 'synthesize',
                    text: document.getElementById('text-input').value,
                    language: 'en'
                }));
            } else {
                // Clone mode would use FormData via REST, simplified here
                status.textContent = '⚠️ Clone mode requires file upload endpoint';
            }
            ws.send(JSON.stringify({ action: 'flush' }));
        };

        ws.onmessage = (event) => {
            if (event.data instanceof Blob && event.data.size > 0) {
                chunks.push(event.data);
            }
        };

        ws.onclose = () => {
            if (chunks.length > 0) {
                const blob = new Blob(chunks, { type: 'audio/pcm' });
                audio.src = URL.createObjectURL(blob);
                audio.play();
                status.textContent = `✅ Generated ${chunks.length} chunks`;
            } else {
                status.textContent = '❌ No audio received';
            }
            btn.disabled = false;
        };

        ws.onerror = () => {
            status.textContent = '❌ Connection failed. Is the API server running?';
            btn.disabled = false;
        };

    } catch (err) {
        status.textContent = `❌ Error: ${err.message}`;
        btn.disabled = false;
    }
});
