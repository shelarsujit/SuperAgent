(function() {
    const ws = new WebSocket(`ws://${location.host}/ws`);
    const messagesEl = document.getElementById('messages');
    const textForm = document.getElementById('text-form');
    const textInput = document.getElementById('text-input');
    const fileForm = document.getElementById('file-form');
    const fileInput = document.getElementById('file-input');

    function appendMessage(text, cls) {
        const div = document.createElement('div');
        div.textContent = text;
        div.className = 'message ' + (cls || '');
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    ws.addEventListener('open', () => {
        appendMessage('WebSocket connected', 'system');
    });

    ws.addEventListener('message', (event) => {
        try {
            const data = JSON.parse(event.data);
            appendMessage('Agent: ' + (data.result || data.message));
        } catch (e) {
            appendMessage('Received: ' + event.data);
        }
    });

    ws.addEventListener('close', () => {
        appendMessage('WebSocket disconnected', 'system');
    });

    textForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = textInput.value.trim();
        if (!text) return;
        appendMessage('You: ' + text);
        ws.send(JSON.stringify({ content: text }));
        textInput.value = '';
    });

    fileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) return;
        appendMessage('Uploading: ' + file.name, 'system');
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            appendMessage('Agent: ' + (data.result || data.message));
        } catch (err) {
            appendMessage('Upload failed', 'system');
        }
        fileInput.value = '';
    });
})();
