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
          message: input,
          use_rag: useRAG
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        sources: data.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
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
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.content}
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <strong>Sources:</strong>
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
            <div className="message-content">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          disabled={isLoading}
          rows="3"
        />
        <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
      <style jsx>{`
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 8px;
          margin-bottom: 10px;
          background-color: #fafafa;
        }

        .message {
          margin-bottom: 15px;
          padding: 10px;
          border-radius: 8px;
          max-width: 80%;
        }

        .message.user {
          background-color: #007bff;
          color: white;
          margin-left: auto;
          text-align: right;
        }

        .message.assistant {
          background-color: #e9ecef;
          color: #333;
          margin-right: auto;
        }

        .message.loading {
          opacity: 0.7;
          font-style: italic;
        }

        .sources {
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #ccc;
          font-size: 0.9em;
        }

        .sources ul {
          margin: 5px 0;
          padding-left: 20px;
        }

        .input-container {
          display: flex;
          gap: 10px;
          align-items: flex-end;
        }

        .input-container textarea {
          flex: 1;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          resize: vertical;
          min-height: 60px;
        }

        .input-container button {
          padding: 10px 20px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          height: fit-content;
        }

        .input-container button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }

        .input-container button:hover:not(:disabled) {
          background-color: #0056b3;
        }
      `}</style>
    </div>
  );
};

export default ChatBox;