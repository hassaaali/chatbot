import React, { useState, useRef, useEffect } from 'react';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch available models on component mount
  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/models');
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.available_models || []);
        setSelectedModel(data.current_model || '');
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  // Add a welcome message when the component mounts
  useEffect(() => {
    const welcomeMessage = {
      role: 'assistant',
      content: 'Welcome to your Legal AI Assistant powered by Together AI! I\'m here to help you analyze legal documents and answer legal questions using advanced AI models. Upload PDF legal documents using the sidebar, and I\'ll provide expert legal analysis based on your materials.\n\n🤖 **Powered by Together AI**: Access to state-of-the-art language models including Llama 2, Mistral, and CodeLlama for legal analysis.\n\n⚠️ **Important Legal Disclaimer**: This AI assistant provides general legal information and document analysis. It does not constitute legal advice and should not replace consultation with a qualified attorney for specific legal matters.',
      isWelcome: true
    };
    setMessages([welcomeMessage]);
  }, []);

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
          use_rag: true, // Always use RAG for legal analysis
          model: selectedModel || undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '', sources: [], model: '' };
      
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
              const contextInfo = data.replace('[CONTEXT] Using legal information from: ', '');
              assistantMessage.sources = contextInfo.split(', ');
            } else if (data.startsWith('[MODEL]')) {
              // Extract model information
              const modelInfo = data.replace('[MODEL] Using Together AI model: ', '');
              assistantMessage.model = modelInfo;
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
        content: 'Sorry, I encountered an error. Please make sure the backend server is running on http://localhost:8000 and your Together AI API key is configured.',
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

  const legalQuestionSuggestions = [
    "What are the key terms and conditions in this contract?",
    "Explain the legal implications of this clause",
    "What are my rights and obligations under this agreement?",
    "Are there any potential legal risks in this document?",
    "What does this legal provision mean in plain language?",
    "How does this document protect my interests?"
  ];

  return (
    <div className="chatbox">
      <div className="chat-header">
        <h3>⚖️ Legal Document Analysis</h3>
        <div className="legal-status">
          <span className="status-indicator legal-enabled">
            🤖 Together AI Active
          </span>
        </div>
      </div>

      {availableModels.length > 0 && (
        <div className="model-selector">
          <label htmlFor="model-select">🤖 AI Model:</label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading}
          >
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model.split('/').pop()} {model === selectedModel ? '(current)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}
      
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role} ${message.isWelcome ? 'welcome' : ''}`}>
            <div className="message-content">
              {message.content}
              {message.model && (
                <div className="model-info">
                  <strong>🤖 Model:</strong> {message.model}
                </div>
              )}
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <strong>📚 Legal Sources Referenced:</strong>
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
              Analyzing with Together AI...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggestions">
          <h4>💡 Try asking:</h4>
          <div className="suggestion-buttons">
            {legalQuestionSuggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-btn"
                onClick={() => setInput(suggestion)}
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about your legal documents... (e.g., 'What are the key terms in this contract?', 'Explain this clause', 'What are my legal obligations?')"
          disabled={isLoading}
          rows="3"
        />
        <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
          <span>Analyze</span>
          <span className="send-icon">🤖</span>
        </button>
      </div>

      <div className="legal-disclaimer">
        <p><strong>⚠️ Legal Disclaimer:</strong> This AI provides general legal information and document analysis. It does not constitute legal advice. Always consult with a qualified attorney for specific legal matters.</p>
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
          margin-bottom: 15px;
          padding-bottom: 15px;
          border-bottom: 2px solid #e9ecef;
        }

        .chat-header h3 {
          margin: 0;
          color: #333;
          font-size: 1.3rem;
        }

        .legal-status {
          display: flex;
          align-items: center;
        }

        .status-indicator {
          padding: 8px 16px;
          border-radius: 25px;
          font-size: 0.9rem;
          font-weight: 700;
          border: 2px solid;
        }

        .legal-enabled {
          background: linear-gradient(135deg, #e8f5e8, #d4edda);
          color: #155724;
          border-color: #28a745;
          box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
        }

        .model-selector {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
          padding: 10px;
          background: linear-gradient(135deg, #f8f9fa, #e9ecef);
          border-radius: 8px;
          border: 1px solid #dee2e6;
        }

        .model-selector label {
          font-weight: 600;
          color: #495057;
          font-size: 0.9rem;
        }

        .model-selector select {
          flex: 1;
          padding: 6px 10px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.85rem;
          background-color: white;
        }

        .model-selector select:focus {
          outline: none;
          border-color: #1e3a8a;
          box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.25);
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
          background: linear-gradient(135deg, #1e3a8a, #1e40af);
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
          background: linear-gradient(135deg, #fff3cd, #ffeaa7);
          border-color: #ffc107;
          color: #856404;
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
          background-color: #1e3a8a;
          animation: typing 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typing {
          0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }

        .model-info {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid #dee2e6;
          font-size: 0.8em;
          color: #6c757d;
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

        .suggestions {
          margin-bottom: 20px;
          padding: 16px;
          background: linear-gradient(135deg, #f8f9fa, #e9ecef);
          border-radius: 12px;
          border: 1px solid #dee2e6;
        }

        .suggestions h4 {
          margin: 0 0 12px 0;
          color: #495057;
          font-size: 1rem;
        }

        .suggestion-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .suggestion-btn {
          padding: 8px 12px;
          background: linear-gradient(135deg, #ffffff, #f8f9fa);
          border: 1px solid #dee2e6;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          color: #495057;
          transition: all 0.2s ease;
        }

        .suggestion-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #1e3a8a, #1e40af);
          color: white;
          border-color: #1e3a8a;
          transform: translateY(-1px);
        }

        .suggestion-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .input-area {
          display: flex;
          gap: 12px;
          align-items: flex-end;
          padding: 16px;
          background-color: #f8f9fa;
          border-radius: 12px;
          border: 1px solid #e9ecef;
          margin-bottom: 15px;
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
          border-color: #1e3a8a;
          box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.25);
        }

        .input-area button {
          padding: 12px 20px;
          background: linear-gradient(135deg, #1e3a8a, #1e40af);
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
          min-width: 100px;
          justify-content: center;
        }

        .input-area button:hover:not(:disabled) {
          background: linear-gradient(135deg, #1e40af, #1d4ed8);
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(30, 58, 138, 0.3);
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

        .legal-disclaimer {
          padding: 12px;
          background: linear-gradient(135deg, #fff3cd, #ffeaa7);
          border: 1px solid #ffc107;
          border-radius: 8px;
          font-size: 0.85rem;
        }

        .legal-disclaimer p {
          margin: 0;
          color: #856404;
          line-height: 1.4;
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