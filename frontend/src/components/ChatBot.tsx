import React, { useState, useRef, useEffect } from 'react';
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
  const [isMinimized, setIsMinimized] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  
  // Use our WebSocket hook - with memoized callbacks
  const { 
    messages: wsMessages, 
    isTyping, 
    connectionStatus, 
    isConnected,
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
  const messages: Message[] = wsMessages.map(msg => ({
    ...msg,
    timestamp: new Date(msg.timestamp)
  }));

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Update unread count when new messages arrive and chat is not expanded
  useEffect(() => {
    if (!isExpanded && messages.length > 0 && messages[messages.length - 1].sender === 'bot') {
      setUnreadCount(prev => prev + 1);
    }
  }, [messages, isExpanded]);

  const toggleChat = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setUnreadCount(0);
    }
  };

  const minimizeChat = () => {
    setIsMinimized(true);
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
  
  // Local fallback when WebSocket is not connected
  // We're no longer using this local processing as we've implemented the mock handler in the service
  const processUserInput = (text: string) => {
    // This is only a placeholder - all processing is now handled in ChatBotWebSocketService
    console.log("Local processing not needed - handled by ChatBotWebSocketService");
  };
  
  const getOptionsForResponse = (userInput: string): QuickOption[] | undefined => {
    const input = userInput.toLowerCase();
    
    if (input.includes('weather')) {
      return [
        { text: '🗓️ Weekly Forecast', action: 'weekly forecast' },
        { text: '☔ Rain Probability', action: 'rain chances' },
        { text: '🌡️ Temperature Trends', action: 'temperature' }
      ];
    } else if (input.includes('pest') || input.includes('insect')) {
      return [
        { text: '🌿 Organic Solutions', action: 'organic pest control' },
        { text: '🧪 Chemical Options', action: 'chemical pest control' },
        { text: '🔍 Identify Pests', action: 'identify pests' }
      ];
    } else if (input.includes('crop') || input.includes('plant')) {
      return [
        { text: '🌾 Seasonal Crops', action: 'seasonal crops' },
        { text: '💧 Water Requirements', action: 'crop water needs' },
        { text: '🌿 Crop Rotation', action: 'crop rotation' }
      ];
    } else if (input.includes('market') || input.includes('price')) {
      return [
        { text: '📊 Price Trends', action: 'market trends' },
        { text: '📈 Price Forecasts', action: 'price forecast' },
        { text: '🚚 Distribution Channels', action: 'distribution' }
      ];
    }
    return [
      { text: '❓ Ask Different Question', action: 'help' },
      { text: '👨‍🌾 Talk to Expert', action: 'expert' }
    ];
  };
  
  const handleQuickOption = (action: string) => {
    // Send quick option via WebSocket - the service handles both real and mock responses
    sendWsMessage(action);
  };
  
  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('weather')) {
      return 'Based on your location, our weather forecast shows clear skies for the next 3 days with a high of 78°F and low of 62°F. Perfect for crop maintenance! There\'s a 20% chance of light rain on Friday.';
    } else if (input.includes('weekly forecast')) {
      return 'Here\'s your 7-day forecast:\nMonday: 78°F, Sunny\nTuesday: 75°F, Partly Cloudy\nWednesday: 76°F, Sunny\nThursday: 79°F, Sunny\nFriday: 74°F, 20% Rain\nSaturday: 72°F, 40% Rain\nSunday: 75°F, Partly Cloudy';
    } else if (input.includes('rain')) {
      return 'Rain probability for your area over the next 10 days is relatively low. We expect some light precipitation (20-40% chance) on Friday and Saturday. Total expected rainfall: 0.25 inches.';
    } else if (input.includes('temperature')) {
      return 'Temperature trends show a stable pattern around 75°F daytime highs with overnight lows in the low 60s. No extreme temperatures expected in the 10-day forecast.';
    } else if (input.includes('pest') || input.includes('insect')) {
      return 'I detect you\'re asking about pest control. Based on recent reports in your area, farmers are seeing increased aphid activity on crops. Would you like information about organic or chemical treatments?';
    } else if (input.includes('organic pest')) {
      return 'For organic aphid control, we recommend introducing ladybugs as natural predators. Additionally, neem oil spray (2 tbsp per gallon of water) applied in the evening has shown 85% effectiveness in local test plots.';
    } else if (input.includes('chemical pest')) {
      return 'For chemical aphid control, products containing imidacloprid have been most effective (92% control rate) in your area. Always follow label instructions and apply in early morning for best results.';
    } else if (input.includes('identify pest')) {
      return 'Common pests in your region this season include: aphids, cucumber beetles, and tomato hornworms. Would you like to upload an image of your pest for identification?';
    } else if (input.includes('crop') || input.includes('plant')) {
      return 'Based on your soil analysis (pH 6.8, loamy texture) and current season, we recommend planting wheat, barley, or pulse crops for maximum yield. Your location has received sufficient rainfall for germination.';
    } else if (input.includes('seasonal crop')) {
      return 'For this planting window (August), top performing crops in your region are: winter wheat (est. yield 65 bu/acre), fall barley (est. yield 58 bu/acre), and cool season vegetables like spinach and kale.';
    } else if (input.includes('water')) {
      return 'Current recommended irrigation for your registered crops: Corn: 1.2 inches/week, Soybeans: 1.0 inches/week. Soil moisture sensors indicate adequate levels in north fields, but south fields are 15% below optimal.';
    } else if (input.includes('rotation')) {
      return 'Based on your previous 3 years of crop data, we recommend rotating to legumes (soybeans, peas) in fields 3 and 4 to improve nitrogen fixation. Fields 1 and 2 would benefit from small grains after consecutive corn seasons.';
    } else if (input.includes('market') || input.includes('price')) {
      return 'Current market prices show: Corn: $4.85/bu (+2.1% weekly), Soybeans: $13.20/bu (+1.5% weekly), Wheat: $6.75/bu (-0.5% weekly). Organic produce is trading at a 15-25% premium over conventional.';
    } else if (input.includes('trend')) {
      return 'Market analysis indicates upward price trends for corn and soybeans through harvest season. Analysts predict a potential 5-7% increase by October due to lower than expected yield reports from southern regions.';
    } else if (input.includes('forecast')) {
      return 'Commodity price forecasts for Q4 2025: Corn expected to strengthen to $5.10-5.30/bu, Soybeans projected to reach $13.75-14.25/bu by December. Wheat markets expected to remain stable with slight downward pressure.';
    } else if (input.includes('distribution')) {
      return 'Local distribution options: Johnson County Co-op (3 miles) offering $4.78/bu corn, $13.05/bu soybeans. River Valley Processors (12 miles) offering $4.92/bu corn, $13.18/bu soybeans. Both have available storage capacity.';
    } else if (input.includes('hello') || input.includes('hi')) {
      return 'Hello! I\'m your AgriHelper assistant. I can provide information on weather forecasts, pest control, crop recommendations, and market prices tailored to your farm\'s location and conditions.';
    } else if (input.includes('help')) {
      return 'I can help with: weather forecasts, pest identification, crop recommendations, market prices, irrigation planning, and connecting you with agricultural experts. What would you like information about?';
    } else if (input.includes('expert')) {
      return 'I\'ve notified our agricultural specialist about your query. Someone will contact you via your registered phone number within 2 business hours. Is there anything else I can assist with while you wait?';
    } else {
      return 'I\'ll analyze your question and find the most relevant information. To provide better assistance, would you like me to consider your farm\'s specific soil type, location, and current crops in my response?';
    }
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
