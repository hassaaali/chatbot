import React, { useState, useRef, useEffect } from 'react';

const ChatBox = ({ useRAG }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add a welcome message when the component mounts
  useEffect(() => {
    const welcomeMessage = {
      role: 'assistant',
      content: useRAG 
        ? 'Hello! I\'m your RAG-enhanced PDF chatbot. Upload some PDF documents using the sidebar, and I\'ll help you find information from them. RAG (Retrieval-Augmented Generation) is enabled by default to provide you with context-aware answers based on your documents.'
        : 'Hello! I\'m your PDF chatbot. Upload some PDF documents using the sidebar and enable RAG to get context-aware answers based on your documents.',
      isWelcome: true
    };
    setMessages([welcomeMessage]);
  }, [useRAG]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: input,
          use_rag: useRAG
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '', sources: [] };
      
      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            
            if (data.startsWith('[CONTEXT]')) {
              // Extract source information
              const contextInfo = data.replace('[CONTEXT] Using information from: ', '');
              assistantMessage.sources = contextInfo.split(', ');
            } else if (data.startsWith('[ERROR]')) {
              assistantMessage.content += `Error: ${data.replace('[ERROR] ', '')}`;
            } else if (data.trim()) {
              assistantMessage.content += data;
            }

            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = { ...assistantMessage };
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running on http://localhost:8000',
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chatbox">
      <div className="chat-header">
        <h3>💬 Chat with your PDFs</h3>
        <div className="rag-status">
          <span className={`status-indicator ${useRAG ? 'enabled' : 'disabled'}`}>
            {useRAG ? '🧠 RAG Enabled' : '❌ RAG Disabled'}
          </span>
        </div>
      </div>
      
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role} ${message.isWelcome ? 'welcome' : ''}`}>
            <div className="message-content">
              {message.content}
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <strong>📚 Sources:</strong>
                  <ul>
                    {message.sources.map((source, idx) => (
                      <li key={idx}>{source}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={useRAG ? "Ask me anything about your uploaded PDFs..." : "Enable RAG to ask questions about your PDFs..."}
          disabled={isLoading}
          rows="3"
        />
        <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
          <span>Send</span>
          <span className="send-icon">📤</span>
        </button>
      </div>
      <style jsx>{`
        .chatbox {
          display: flex;
          flex-direction: column;
          height: 600px;
          padding: 20px;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 2px solid #e9ecef;
        }

        .chat-header h3 {
          margin: 0;
          color: #333;
          font-size: 1.3rem;
        }

        .rag-status {
          display: flex;
          align-items: center;
        }

        .status-indicator {
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 600;
          border: 2px solid;
        }

        .status-indicator.enabled {
          background-color: #d4edda;
          color: #155724;
          border-color: #c3e6cb;
        }

        .status-indicator.disabled {
          background-color: #f8d7da;
          color: #721c24;
          border-color: #f5c6cb;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          margin-bottom: 20px;
          padding-right: 10px;
        }

        .message {
          margin-bottom: 15px;
          padding: 12px 16px;
          border-radius: 12px;
          max-width: 80%;
          position: relative;
        }

        .message.user {
          background: linear-gradient(135deg, #007bff, #0056b3);
          color: white;
          margin-left: auto;
          text-align: right;
          border-bottom-right-radius: 4px;
        }

        .message.assistant {
          background-color: #f8f9fa;
          color: #333;
          margin-right: auto;
          border: 1px solid #e9ecef;
          border-bottom-left-radius: 4px;
        }

        .message.assistant.welcome {
          background: linear-gradient(135deg, #e3f2fd, #bbdefb);
          border-color: #2196f3;
          color: #1565c0;
        }

        .message.assistant.loading {
          opacity: 0.8;
        }

        .message.assistant.error {
          background-color: #ffebee;
          color: #c62828;
          border-color: #ffcdd2;
        }

        .typing-indicator {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          margin-right: 8px;
        }

        .typing-indicator span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background-color: #007bff;
          animation: typing 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typing {
          0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }

        .sources {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #dee2e6;
          font-size: 0.9em;
        }

        .sources strong {
          color: #495057;
          display: block;
          margin-bottom: 6px;
        }

        .sources ul {
          margin: 0;
          padding-left: 20px;
          color: #6c757d;
        }

        .sources li {
          margin-bottom: 2px;
        }

        .input-area {
          display: flex;
          gap: 12px;
          align-items: flex-end;
          padding: 16px;
          background-color: #f8f9fa;
          border-radius: 12px;
          border: 1px solid #e9ecef;
        }

        .input-area textarea {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #ced4da;
          border-radius: 8px;
          resize: vertical;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.4;
          transition: border-color 0.2s ease;
        }

        .input-area textarea:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .input-area button {
          padding: 12px 20px;
          background: linear-gradient(135deg, #007bff, #0056b3);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          font-size: 14px;
          display: flex;
          align-items: center;
          gap: 6px;
          transition: all 0.2s ease;
          min-width: 80px;
          justify-content: center;
        }

        .input-area button:hover:not(:disabled) {
          background: linear-gradient(135deg, #0056b3, #004085);
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
        }

        .input-area button:disabled {
          background: linear-gradient(135deg, #ccc, #999);
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .send-icon {
          font-size: 16px;
        }

        /* Scrollbar styling */
        .messages::-webkit-scrollbar {
          width: 6px;
        }

        .messages::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }

        .messages::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;
        }

        .messages::-webkit-scrollbar-thumb:hover {
          background: #a8a8a8;
        }
      `}</style>
    </div>
  );
};

export default ChatBox;