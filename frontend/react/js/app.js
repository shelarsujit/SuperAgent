const { useState, useEffect, useRef } = React;

function App() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    wsRef.current = new WebSocket(`ws://${location.host}/ws`);
    const ws = wsRef.current;

    function addMessage(msg, cls) {
      setMessages(m => [...m, { text: msg, cls }]);
    }

    ws.addEventListener('open', () => {
      addMessage('WebSocket connected', 'system');
    });

    ws.addEventListener('message', event => {
      try {
        const data = JSON.parse(event.data);
        addMessage('Agent: ' + (data.result || data.message));
      } catch (e) {
        addMessage('Received: ' + event.data);
      }
    });

    ws.addEventListener('close', () => {
      addMessage('WebSocket disconnected', 'system');
    });

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = e => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    setMessages(m => [...m, { text: 'You: ' + trimmed }]);
    wsRef.current.send(JSON.stringify({ content: trimmed }));
    setText('');
  };

  const uploadFile = async e => {
    e.preventDefault();
    if (!file) return;
    setMessages(m => [...m, { text: 'Uploading: ' + file.name, cls: 'system' }]);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('/upload', { method: 'POST', body: formData });
      const data = await response.json();
      setMessages(m => [...m, { text: 'Agent: ' + (data.result || data.message) }]);
    } catch(err) {
      setMessages(m => [...m, { text: 'Upload failed', cls: 'system' }]);
    }
    setFile(null);
    e.target.reset();
  };

  return (
    React.createElement('div', { id: 'chat-container' },
      React.createElement('div', { id: 'messages', ref: messagesEndRef },
        messages.map((m, i) => React.createElement('div', { key: i, className: 'message ' + (m.cls || '') }, m.text))
      ),
      React.createElement('form', { onSubmit: sendMessage, id: 'text-form' },
        React.createElement('input', {
          type: 'text',
          value: text,
          onChange: e => setText(e.target.value),
          id: 'text-input'
        }),
        React.createElement('button', { type: 'submit' }, 'Send')
      ),
      React.createElement('form', { onSubmit: uploadFile, id: 'file-form' },
        React.createElement('input', {
          type: 'file',
          onChange: e => setFile(e.target.files[0]),
          id: 'file-input'
        }),
        React.createElement('button', { type: 'submit' }, 'Upload')
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));

