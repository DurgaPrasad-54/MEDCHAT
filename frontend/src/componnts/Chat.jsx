import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Chat.css';

const Chat = () => {
  const API_PATH = import.meta.env.VITE_REACT_API_URL;
  const navigate = useNavigate();


  const token = localStorage.getItem('token');
  if (!token) {
    navigate('/');
    return null;
  }

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showSidebar, setShowSidebar] = useState(false);
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
    setShowSidebar(false); 
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const startNewChat = () => {
    setMessages([]);
    setError('');
    setShowSidebar(false); 
  };

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
        startNewChat();
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

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <div className={`sidebar ${showSidebar ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-header-top">
            <button className="close-sidebar-btn" onClick={() => setShowSidebar(false)}>
              <span className="icon">×</span>
            </button>
          </div>
          <button className="new-chat-btn" onClick={startNewChat}>
            <span className="icon">+</span>
            New Chat
          </button>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-actions">
            <button className="clear-history-btn" onClick={clearHistory}>
              <span className="icon">🗑️</span>
              Clear History
            </button>
          </div>
          

          <div className="history-section">
            <h3>Chat History</h3>
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
                    <div className="history-message">
                      {item.message.length > 40
                        ? item.message.substring(0, 40) + '...'
                        : item.message}
                    </div>
                    <div className="history-timestamp">
                      {formatTimestamp(item.timestamp)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      {/* Sidebar Overlay for Mobile */}
      {showSidebar && <div className="sidebar-overlay" onClick={() => setShowSidebar(false)}></div>}

      {/* Main Chat Area */}
      <div className="main-chat">
        {/* Header */}
        <div className="chat-header">
          <button
            className="menu-toggle"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            <span className="hamburger">☰</span>
          </button>
          <div className="header-title">
            <h1>MedChat Assistant</h1>
            <p>Ask me about health and medical topics</p>
          </div>
          <div className="header-spacer"></div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon"></div>
              <h2>Welcome to MedChat Assistant</h2>
              <p>
                I can help you with medical questions, health concerns, symptoms,
                treatments, and wellness topics.
              </p>
              <div className="examples">
                <p><strong>Try asking:</strong></p>
                <ul>
                  <li>"What are the symptoms of diabetes?"</li>
                  <li>"How to treat a headache?"</li>
                  <li>"First aid for burns"</li>
                </ul>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  <div className="message-text">
                    {message.isUser ? message.message : message.response}
                  </div>
                  <div className="message-timestamp">
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="message bot-message">
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <span>AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              className="message-input"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your health concerns"
              rows="1"
              disabled={isLoading}
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
            >
              <span className="send-icon">➤</span>
            </button>
          </div>
          <div className="input-footer">
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;