import React, { useState, useRef, useEffect, useMemo } from 'react';
import './ChatBot.css';
import useChatBot from '../hooks/useChatBot';
import { WebSocketConnectionStatus } from '../services/websocketService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'system';
  timestamp: Date;
  options?: QuickOption[];
}

interface QuickOption {
  text: string;
  action: string;
}

const ChatBot: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  
  // Use our WebSocket hook - with memoized callbacks
  const { 
    messages: wsMessages, 
    isTyping, 
  connectionStatus, 
    sendMessage: sendWsMessage
  } = useChatBot({
    initialMessages: [
      {
        id: '1',
        text: 'Hello! How can I help with your agricultural questions today?',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        options: [
          { text: '🌦️ Weather Forecast', action: 'weather' },
          { text: '🐛 Pest Control', action: 'pests' },
          { text: '💰 Market Prices', action: 'prices' },
          { text: '🌱 Crop Suggestions', action: 'crops' }
        ]
      }
    ],
    autoConnect: true
  });
  
  // Convert WebSocket messages to the format expected by the component
  // Memoize to avoid new array/object each render triggering effects
  const messages: Message[] = useMemo(() => {
    return wsMessages.map(msg => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));
  }, [wsMessages]);

  // Track last processed bot message to avoid incrementing unread repeatedly
  const lastBotMessageIdRef = useRef<string | null>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Update unread count only when a new bot message arrives and chat is not expanded
  useEffect(() => {
    if (!isExpanded && messages.length > 0) {
      const last = messages[messages.length - 1];
      if (last.sender === 'bot' && last.id !== lastBotMessageIdRef.current) {
        setUnreadCount(prev => prev + 1);
        lastBotMessageIdRef.current = last.id;
      }
    }
  }, [messages, isExpanded]);

  const toggleChat = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setUnreadCount(0);
    }
  };

  const minimizeChat = () => {
    setIsExpanded(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Send message via WebSocket - the service handles both real and mock responses
    sendWsMessage(inputValue);
    setInputValue('');
  };
  
  // Note: local fallback helpers were removed; WebSocket service provides responses now.
  const handleQuickOption = (action: string) => {
    // Send quick option via WebSocket - the service handles both real and mock responses
    sendWsMessage(action);
  };

  return (
    <div className={`chatbot-container ${isExpanded ? 'expanded' : ''}`}>
      {!isExpanded ? (
        <button className="chatbot-button" onClick={toggleChat} title="Open AgriHelper Chat">
          <svg className="chatbot-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 13.5997 2.37562 15.1116 3.04346 16.4525C3.22094 16.8088 3.28001 17.2161 3.17712 17.6006L2.58151 19.8267C2.32295 20.793 3.20701 21.677 4.17335 21.4185L6.39939 20.8229C6.78393 20.72 7.19121 20.7791 7.54753 20.9565C8.88837 21.6244 10.4003 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            <path d="M8 12H8.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 12H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M16 12H16.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </button>
      ) : (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>
              <span className="chatbot-logo">🌾</span>
              <span className="chatbot-title">AgriHelper</span>
            </h3>
            <div className="header-actions">
              <button className="minimize-button" onClick={minimizeChat} title="Minimize">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              <button className="close-button" onClick={toggleChat} title="Close">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <div className="chatbot-messages">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`chat-message ${message.sender === 'bot' ? 'bot' : 'user'}`}
              >
                <div className="message-content">
                  <p>{message.text}</p>
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  
                  {message.options && message.options.length > 0 && (
                    <div className="quick-options">
                      {message.options.map((option, index) => (
                        <button 
                          key={index} 
                          className="quick-option-btn"
                          onClick={() => handleQuickOption(option.action)}
                        >
                          {option.text}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Show typing indicator when the bot is typing */}
            {isTyping && (
              <div className="chat-message bot">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            {/* Connection status indicator when disconnected */}
            {connectionStatus !== WebSocketConnectionStatus.CONNECTED && (
              <div className="connection-status-indicator">
                {connectionStatus === WebSocketConnectionStatus.CONNECTING ? 
                  '🔄 Connecting...' : 
                  connectionStatus === WebSocketConnectionStatus.RECONNECTING ?
                  '🔄 Reconnecting...' :
                  '⚠️ Disconnected - using local responses'}
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          <form className="chatbot-input" onSubmit={sendMessage}>
            <input
              type="text"
              placeholder="Type your question here..."
              value={inputValue}
              onChange={handleInputChange}
              autoFocus={isExpanded}
            />
            <button type="submit" title="Send message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
