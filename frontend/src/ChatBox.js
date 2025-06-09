import React, { useState, useRef } from 'react';

const ChatBox = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState('');
  const [useRag, setUseRag] = useState(true);
  const [contextInfo, setContextInfo] = useState(null);
  const controllerRef = useRef(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt.');
      return;
    }

    setResponse([]);
    setError('');
    setContextInfo(null);
    setIsStreaming(true);

    try {
      controllerRef.current = new AbortController();
      const res = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controllerRef.current.signal,
        body: JSON.stringify({ 
          prompt: prompt,
          use_rag: useRag 
        }),
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
              } else if (content.startsWith('[CONTEXT]')) {
                setContextInfo(content.slice(9).trim());
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
    setContextInfo(null);
  };

  return (
    <div style={{ padding: 20, maxWidth: 800, margin: '0 auto' }}>
      <h2>🧠 RAG-Enhanced Chatbot</h2>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
          <input
            type="checkbox"
            checked={useRag}
            onChange={(e) => setUseRag(e.target.checked)}
            style={{ marginRight: '8px' }}
          />
          <span>Use RAG (Retrieval-Augmented Generation)</span>
        </label>
        <small style={{ color: '#666' }}>
          When enabled, the chatbot will use information from your uploaded documents to provide more accurate answers.
        </small>
      </div>

      <textarea
        rows={4}
        cols={60}
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Ask me anything..."
        disabled={isStreaming}
        style={{ 
          width: '100%', 
          resize: 'vertical',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          fontSize: '14px'
        }}
      />
      
      <div style={{ margin: '10px 0' }}>
        <button 
          onClick={handleSubmit} 
          disabled={isStreaming || !prompt.trim()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isStreaming || !prompt.trim() ? 'not-allowed' : 'pointer',
            marginRight: '10px'
          }}
        >
          Ask
        </button>
        <button 
          onClick={handleStop} 
          disabled={!isStreaming}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !isStreaming ? 'not-allowed' : 'pointer',
            marginRight: '10px'
          }}
        >
          Stop
        </button>
        <button 
          onClick={handleClear} 
          disabled={isStreaming}
          style={{
            padding: '10px 20px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isStreaming ? 'not-allowed' : 'pointer'
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <div style={{ 
          color: '#721c24', 
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '10px' 
        }}>
          {error}
        </div>
      )}

      {contextInfo && (
        <div style={{ 
          color: '#155724', 
          backgroundColor: '#d4edda',
          border: '1px solid #c3e6cb',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '10px' 
        }}>
          📖 {contextInfo}
        </div>
      )}

      {isStreaming && (
        <div style={{ 
          color: '#004085',
          backgroundColor: '#cce7ff',
          border: '1px solid #99d6ff',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          🤖 Generating response...
        </div>
      )}

      <div style={{ 
        marginTop: 20, 
        whiteSpace: 'pre-wrap', 
        border: '1px solid #ccc', 
        padding: 15,
        borderRadius: '4px',
        backgroundColor: '#f8f9fa',
        minHeight: '200px'
      }}>
        <strong>Response:</strong>
        <div style={{ marginTop: '10px' }}>
          {response.length ? (
            response.map((line, index) => (
              <div key={index} style={{ marginBottom: 8, lineHeight: '1.5' }}>
                {line.startsWith('-') ? (
                  <li style={{ marginLeft: '20px' }}>{line.slice(2).trim()}</li>
                ) : (
                  line
                )}
              </div>
            ))
          ) : (
            <div style={{ color: '#666', fontStyle: 'italic' }}>No response yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatBox;