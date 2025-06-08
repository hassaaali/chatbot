import React, { useState, useRef } from 'react';

const ChatBox = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState('');
  const controllerRef = useRef(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }

    setResponse([]);
    setError('');
    setIsStreaming(true);

    try {
      controllerRef.current = new AbortController();
      const res = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controllerRef.current.signal,
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          if (buffer.trim()) {
            setResponse(prev => [...prev, buffer.trim()]);
          }
          break;
        }
        const chunk = decoder.decode(value, { stream: true });
        chunk.split('\n').forEach(line => {
          if (line.startsWith('data:')) {
            const content = line.slice(5).trim();
            if (content && content !== '[DONE]') {
              if (content.startsWith('[ERROR]')) {
                setError(content.slice(7));
                setIsStreaming(false);
              } else if (content.startsWith('[METADATA]')) {
                console.log('Metadata:', content.slice(10));
              } else {
                buffer += content + '\n';
                // Split by section headers or bullets
                const lines = buffer.split(/(?=\d+\s*letters\s*:|- )|\n+/i);
                buffer = lines.pop() || '';
                lines.forEach(line => {
                  if (line.trim()) {
                    setResponse(prev => [...prev, line.trim()]);
                  }
                });
              }
            }
          }
        });
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(`Failed to fetch response: ${err.message}`);
      }
    } finally {
      setIsStreaming(false);
    }
  };

  const handleStop = () => {
    if (controllerRef.current) {
      controllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  const handleClear = () => {
    setPrompt('');
    setResponse([]);
    setError('');
  };

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: '0 auto' }}>
      <h2>🧠 Hassaan.ai Chatbot</h2>
      <textarea
        rows={4}
        cols={60}
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Ask me anything..."
        disabled={isStreaming}
        style={{ width: '100%', resize: 'vertical' }}
      />
      <div style={{ margin: '10px 0' }}>
        <button onClick={handleSubmit} disabled={isStreaming || !prompt.trim()}>
          Ask
        </button>
        <button onClick={handleStop} disabled={!isStreaming} style={{ marginLeft: 10 }}>
          Stop
        </button>
        <button onClick={handleClear} disabled={isStreaming} style={{ marginLeft: 10 }}>
          Clear
        </button>
      </div>
      {error && <div style={{ color: 'red', marginBottom: 10 }}>{error}</div>}
      {isStreaming && <div style={{ color: 'blue' }}>Streaming response...</div>}
      <div style={{ marginTop: 20, whiteSpace: 'pre-wrap', border: '1px solid #ccc', padding: 10 }}>
        <strong>Response:</strong>
        <ul>
          {response.length ? (
            response.map((line, index) => (
              <li key={index} style={{ marginBottom: 5 }}>
                {line.startsWith('-') ? line.slice(2).trim() : line}
              </li>
            ))
          ) : (
            <div>No response yet.</div>
          )}
        </ul>
      </div>
    </div>
  );
};

export default ChatBox;