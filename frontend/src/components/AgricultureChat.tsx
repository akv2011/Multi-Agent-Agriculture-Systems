import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle, Clock, User, Bot } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot' | 'system';
  content: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  queryId?: string;
  agentResponses?: AgentResponse[];
}

interface AgentResponse {
  agentId: string;
  agentName: string;
  response: string;
  confidence: number;
  status: 'processing' | 'completed' | 'error';
}

import config from '../config';

interface AgricultureChatProps {
  websocketUrl?: string;
  onConnectionStatusChange?: (connected: boolean) => void;
}

// Get WebSocket URL from config and apply proper path
const getDefaultWebsocketUrl = () => {
  // Construct WebSocket URL from base URL, replacing http/https with ws/wss
  const wsBaseUrl = config.websocket.url.replace(/^(http|ws)s?:\/\/([^\/]+).*$/, 'ws://$2');
  return `${wsBaseUrl}/ws/updates`;
};

const AgricultureChat: React.FC<AgricultureChatProps> = ({
  websocketUrl = getDefaultWebsocketUrl(),
  onConnectionStatusChange
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'english' | 'hindi' | 'mixed'>('english');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket(websocketUrl);
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          onConnectionStatusChange?.(true);
          
          // Send welcome message
          addSystemMessage('Connected to Agricultural Advisory System. How can I help you today?');
        };
        
        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          onConnectionStatusChange?.(false);
          
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          addSystemMessage('Connection error. Attempting to reconnect...');
        };
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      wsRef.current?.close();
    };
  }, [websocketUrl, onConnectionStatusChange]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'agriculture_query_status':
        updateQueryStatus(data.query_id, data.status, data.data);
        break;
      case 'agent_response':
        updateAgentResponse(data.query_id, data.agent_id, data.response);
        break;
      case 'final_response':
        addBotMessage(data.response, data.query_id);
        setIsLoading(false);
        break;
      case 'error':
        addSystemMessage(`Error: ${data.message}`);
        setIsLoading(false);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const addSystemMessage = (content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, message]);
  };

  const addBotMessage = (content: string, queryId?: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'bot',
      content,
      timestamp: new Date().toISOString(),
      queryId
    };
    setMessages(prev => [...prev, message]);
  };

  const updateQueryStatus = (queryId: string, status: string, data: any) => {
    setMessages(prev => prev.map(msg => {
      if (msg.queryId === queryId) {
        return {
          ...msg,
          status: status === 'completed' ? 'sent' : 'sending'
        };
      }
      return msg;
    }));
  };

  const updateAgentResponse = (queryId: string, agentId: string, response: any) => {
    // Add intermediate agent response display
    const agentMessage: Message = {
      id: `${queryId}-${agentId}`,
      type: 'bot',
      content: `**${response.agent_name || agentId}**: ${response.response || response.summary}`,
      timestamp: new Date().toISOString(),
      queryId
    };
    setMessages(prev => [...prev, agentMessage]);
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading || !isConnected) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    const queryText = inputText;
    setInputText('');

    try {
      // Send query to backend API
      const response = await fetch('/agriculture/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: queryText,
          language: selectedLanguage,
          user_id: 'user-' + Date.now(),
          context: {
            timestamp: new Date().toISOString(),
            source: 'web_chat'
          }
        }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        // Update user message status
        setMessages(prev => prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: 'sent', queryId: result.query_id }
            : msg
        ));
        
        // WebSocket will handle the response updates
      } else if (result.status === 'clarification_needed') {
        setIsLoading(false);
        addBotMessage(`I need more information: ${result.response?.questions?.join(', ')}`);
      } else {
        setIsLoading(false);
        addSystemMessage(`Error: ${result.error || 'Unknown error occurred'}`);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id 
          ? { ...msg, status: 'error' }
          : msg
      ));
      addSystemMessage('Failed to send message. Please try again.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'sent':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const exampleQueries = [
    "What crop should I grow in Punjab during Rabi season?",
    "मेरे गेहूं पर पीले धब्बे हैं, कौन सा स्प्रे करूं?",
    "When should I water my cotton crop?",
    "Kisan loan kaise milega?"
  ];

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-green-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Agricultural Advisory Chat</h2>
            <p className="text-green-100 text-sm">
              Ask questions about crops, pests, irrigation, finance & more
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-300' : 'bg-red-300'}`} />
            <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        
        {/* Language Selector */}
        <div className="mt-3">
          <label className="text-sm text-green-100 mr-2">Language:</label>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value as any)}
            className="bg-green-700 text-white px-2 py-1 rounded text-sm"
          >
            <option value="english">English</option>
            <option value="hindi">हिंदी (Hindi)</option>
            <option value="mixed">Mixed (Hindi-English)</option>
          </select>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500">
            <Bot className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p className="mb-4">Welcome to Agricultural Advisory! Try asking:</p>
            <div className="space-y-2">
              {exampleQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => setInputText(query)}
                  className="block w-full text-left p-2 bg-white rounded border hover:bg-green-50 text-sm"
                >
                  "{query}"
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-green-600 text-white ml-12'
                  : message.type === 'bot'
                  ? 'bg-white border border-gray-200 mr-12'
                  : 'bg-blue-50 border border-blue-200 text-blue-800 mx-12'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'user' ? (
                  <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
                ) : message.type === 'bot' ? (
                  <Bot className="w-5 h-5 mt-0.5 flex-shrink-0 text-green-600" />
                ) : null}
                
                <div className="flex-1">
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs ${
                      message.type === 'user' ? 'text-green-100' : 'text-gray-500'
                    }`}>
                      {formatTimestamp(message.timestamp)}
                    </span>
                    {message.status && getStatusIcon(message.status)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-3 mr-12">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-green-600" />
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-green-600" />
                  <span className="text-gray-600">Analyzing your query...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4 rounded-b-lg">
        <div className="flex space-x-2">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask your agricultural question in ${selectedLanguage}...`}
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
            rows={2}
            disabled={!isConnected || isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected || isLoading || !inputText.trim()}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default AgricultureChat;
