import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Chat.css';

const Chat = () => {
  const API_PATH = import.meta.env.VITE_REACT_API_URL;
  const navigate = useNavigate();

  // ✅ Redirect if no token
  const token = localStorage.getItem('token');
  if (!token) {
    navigate('/');
    return null;
  }

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_PATH}/history`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/');
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError('');

    const newUserMessage = {
      id: Date.now(),
      message: userMessage,
      response: '',
      timestamp: new Date().toISOString(),
      isUser: true,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_PATH}/chat`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();

        const botMessage = {
          id: Date.now() + 1,
          message: userMessage,
          response: data.response,
          timestamp: data.timestamp || new Date().toISOString(),
          isUser: false,
        };

        setMessages((prev) => [...prev, botMessage]);
        fetchHistory();
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Network error. Please try again.');
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

  const loadHistoryMessage = (historyItem) => {
    const userMessage = {
      id: Date.now(),
      message: historyItem.message,
      response: '',
      timestamp: historyItem.timestamp,
      isUser: true,
    };

    const botMessage = {
      id: Date.now() + 1,
      message: historyItem.message,
      response: historyItem.response,
      timestamp: historyItem.timestamp,
      isUser: false,
    };

    setMessages([userMessage, botMessage]);
    setShowHistory(false);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
  };

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  // New: Clear history from backend
  const clearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all chat history?')) return;

    try {
      const response = await fetch(`${API_PATH}/clearhistory`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setHistory([]);
        clearChat();
        alert('Chat history cleared successfully.');
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/');
      } else {
        const data = await response.json();
        alert(data.detail || 'Failed to clear history.');
      }
    } catch (err) {
      console.error('Error clearing history:', err);
      alert('Error clearing history.');
    }
  };

  return (
    <div className="chat-container">
      {/* Mobile Menu Button */}
      <button
        className="menu-toggle-btn"
        onClick={() => setShowHistory((prev) => !prev)}
        aria-label="Toggle chat history sidebar"
      >
        ☰
      </button>

      {/* History Sidebar */}
      <div className={`history-sidebar ${showHistory ? 'visible' : 'hidden'}`}>
        <div className="history-header">
          <h3>Chat History</h3>
          <button className="btn clear-history-btn" onClick={clearHistory}>
            Clear History
          </button>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <div className="no-history">No chat history available</div>
          ) : (
            history.map((item, index) => (
              <div
                key={index}
                className="history-item"
                onClick={() => loadHistoryMessage(item)}
              >
                <div className="history-message-preview">
                  {item.message.length > 50
                    ? item.message.substring(0, 50) + '...'
                    : item.message}
                </div>
                <div className="history-response-preview">
                  {item.response.length > 80
                    ? item.response.substring(0, 80) + '...'
                    : item.response}
                </div>
                <div className="history-timestamp">{formatTimestamp(item.timestamp)}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-title">
            <h1>Medical Chat Assistant</h1>
            <p>Ask me about health and medical topics</p>
          </div>
          <div className="chat-actions">
            <button
              className="btn toggle-history-btn desktop-only"
              onClick={() => setShowHistory((prev) => !prev)}
            >
              {showHistory ? 'Hide' : 'Show'} History
            </button>
            <button className="btn clear-chat-btn" onClick={clearChat}>
              Clear Chat
            </button>
            <button className="btn logout-btn" onClick={logout}>
              Logout
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h3>Welcome to Medical Chat Assistant</h3>
              <p>
                I can help you with medical questions, health concerns, symptoms,
                treatments, and wellness topics.
              </p>
              <div className="examples">
                <p>
                  <strong>Examples:</strong> "What are the symptoms of diabetes?", "How to
                  treat a headache?", "First aid for burns"
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message-item ${message.isUser ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  <p>{message.isUser ? message.message : message.response}</p>
                  <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="loading-indicator">
              <div>
                <p>🤔 Thinking...</p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && <div className="error-message">⚠️ {error}</div>}

        {/* Input Area */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              className="chat-input"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your health concerns, symptoms, treatments, or medical questions..."
              rows="3"
              disabled={isLoading}
            />
            <button
              className="send-button"
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="input-info">
            Press Enter to send • This assistant only responds to medical and health-related questions
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
