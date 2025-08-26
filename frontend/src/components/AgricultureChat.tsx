import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle, Clock, User, Bot, Camera, X, Upload, FileImage } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot' | 'system';
  content: string;
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  queryId?: string;
  agentResponses?: AgentResponse[];
  language?: 'english' | 'tamil';
  detectedCategory?: string;
  uploadedImage?: string;
}

interface AgentResponse {
  agentId: string;
  agentName: string;
  response: string;
  confidence: number;
  status: 'processing' | 'completed' | 'error';
  category?: string;
}

interface AgricultureChatProps {
  websocketUrl?: string;
  onConnectionStatusChange?: (connected: boolean) => void;
}

const AgricultureChat: React.FC<AgricultureChatProps> = ({
  websocketUrl = 'ws://localhost:8000/ws/updates',
  onConnectionStatusChange
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState<'english' | 'tamil'>('english');
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  // Advanced input states (AgriSens integrations)
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [diseaseImagePreview, setDiseaseImagePreview] = useState<string | null>(null);
  const [soilFormOpen, setSoilFormOpen] = useState(false);
  const [soilData, setSoilData] = useState<{ [k: string]: string }>({
    nitrogen: '', phosphorus: '', potassium: '', ph: '', organic_matter: '', moisture_content: ''
  });
  const [cropType, setCropType] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Query categorization helper
  const categorizeQuery = (text: string, hasImage: boolean): string => {
    const lowerText = text.toLowerCase();
    
    if (hasImage || lowerText.includes('disease') || lowerText.includes('pest') || lowerText.includes('infection') || 
        lowerText.includes('நோய்') || lowerText.includes('பூச்சி')) {
      return 'disease_identification';
    }
    if (lowerText.includes('crop') || lowerText.includes('recommend') || lowerText.includes('plant') ||
        lowerText.includes('பயிர்') || lowerText.includes('சிபாரிசு')) {
      return 'crop_recommendation';
    }
    if (lowerText.includes('irrigation') || lowerText.includes('water') || lowerText.includes('watering') ||
        lowerText.includes('நீர்') || lowerText.includes('பாசனம்')) {
      return 'irrigation';
    }
    if (lowerText.includes('fertilizer') || lowerText.includes('nutrient') || lowerText.includes('npk') ||
        lowerText.includes('உரம்') || lowerText.includes('சத்து')) {
      return 'fertilizer_recommendation';
    }
    if (lowerText.includes('market') || lowerText.includes('price') || lowerText.includes('sell') ||
        lowerText.includes('சந்தை') || lowerText.includes('விலை')) {
      return 'market_timing';
    }
    if (lowerText.includes('harvest') || lowerText.includes('harvest time') || 
        lowerText.includes('அறுவடை') || lowerText.includes('காலம்')) {
      return 'harvest_planning';
    }
    if (lowerText.includes('weather') || lowerText.includes('forecast') || lowerText.includes('rain') ||
        lowerText.includes('வானிலை') || lowerText.includes('மழை')) {
      return 'weather_forecast';
    }
    return 'general';
  };

  // Loading steps for different categories
  const getLoadingSteps = (category: string, language: string): string[] => {
    if (language === 'tamil') {
      switch (category) {
        case 'disease_identification':
          return ['படத்தை பகுப்பாய்வு செய்கிறது...', 'நோய் கண்டறிதல் மாதிரியை இயக்குகிறது...', 'முடிவுகளை தயாரிக்கிறது...'];
        case 'crop_recommendation':
          return ['மண் தரவை பகுப்பாய்வு செய்கிறது...', 'பயிர் பரிந்துரை மாதிரியை இயக்குகிறது...', 'சிறந்த பயிர்களை தேர்ந்தெடுக்கிறது...'];
        case 'irrigation':
          return ['மண் ஈரப்பதத்தை சரிபார்க்கிறது...', 'நீர்ப்பாசன அட்டவணையை கணக்கிடுகிறது...', 'பரிந்துரைகளை தயாரிக்கிறது...'];
        default:
          return ['தரவை பகுப்பாய்வு செய்கிறது...', 'முடிவுகளை கணக்கிடுகிறது...', 'பதிலை தயாரிக்கிறது...'];
      }
    } else {
      switch (category) {
        case 'disease_identification':
          return ['Analyzing uploaded image...', 'Running disease detection model...', 'Preparing diagnosis...'];
        case 'crop_recommendation':
          return ['Analyzing soil data...', 'Running crop recommendation model...', 'Selecting optimal crops...'];
        case 'irrigation':
          return ['Checking soil moisture...', 'Calculating irrigation schedule...', 'Preparing recommendations...'];
        default:
          return ['Analyzing query...', 'Processing with AI agents...', 'Preparing response...'];
      }
    }
  };

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
        updateQueryStatus(data.query_id, data.status);
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
    // Allow basic markdown bold -> replace for simple emphasis
    const formatted = content.replace(/\*\*(.*?)\*\*/g, '$1');
    const message: Message = {
      id: Date.now().toString(),
      type: 'bot',
      content: formatted,
      timestamp: new Date().toISOString(),
      queryId
    };
    setMessages(prev => [...prev, message]);
  };

  const updateQueryStatus = (queryId: string, status: string) => {
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

  const updateAgentResponse = (queryId: string, agentId: string, response: Record<string, unknown>) => {
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

  // Image upload handler
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setImagePreview(result);
        setDiseaseImagePreview(result); // Keep existing compatibility
      };
      reader.readAsDataURL(file);
    }
  };

  const clearUploadedImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    setDiseaseImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const clearDiseaseImage = () => {
    clearUploadedImage();
  };

  const updateSoilField = (field: string, value: string) => {
    setSoilData(prev => ({ ...prev, [field]: value }));
  };

  const soilDataProvided = () => Object.values(soilData).some(v => v.trim() !== '');

  const sendMessage = async () => {
    if (!inputText.trim() && !imagePreview) return;
    if (isLoading || !isConnected) return;

    // Categorize the query
    const hasImage = !!imagePreview;
    const detectedCategory = categorizeQuery(inputText, hasImage);
    
    // Auto-synthesize query if only image uploaded
    let queryToSend = inputText.trim();
    if (!queryToSend && imagePreview) {
      queryToSend = selectedLanguage === 'tamil' 
        ? `இந்த படத்தில் உள்ள நோயை கண்டறியவும்${cropType ? ' - ' + cropType + ' பயிருக்கு' : ''}` 
        : `Identify disease from this image${cropType ? ' for ' + cropType : ''}`;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: queryToSend,
      timestamp: new Date().toISOString(),
      status: 'sending',
      uploadedImage: imagePreview || undefined,
      language: selectedLanguage,
      detectedCategory
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Show loading animation with steps
    const steps = getLoadingSteps(detectedCategory, selectedLanguage);
    let stepIndex = 0;
    const stepInterval = setInterval(() => {
      if (stepIndex < steps.length) {
        setLoadingStep(steps[stepIndex]);
        stepIndex++;
      } else {
        clearInterval(stepInterval);
      }
    }, 1500);

    // Simulate 5-second delay as requested
    setTimeout(() => {
      clearInterval(stepInterval);
      setLoadingStep('');
    }, 5000);

    const contextPayload: Record<string, unknown> = {
      timestamp: new Date().toISOString(),
      source: 'web_chat',
      language: selectedLanguage,
      category: detectedCategory
    };
    
    if (imagePreview) {
      const base64 = imagePreview.split(',')[1];
      contextPayload.image_base64 = base64;
      if (cropType) contextPayload.crop_type = cropType;
    }
    
    if (soilDataProvided()) {
      const parsed: Record<string, number> = {};
      ['nitrogen','phosphorus','potassium','ph','organic_matter','moisture_content'].forEach(k => {
        if (soilData[k]) {
          const num = parseFloat(soilData[k]);
          if (!isNaN(num)) parsed[k === 'moisture_content' ? 'moisture_content' : k] = num;
        }
      });
      if (Object.keys(parsed).length) contextPayload.soil_data = parsed;
      if (cropType) contextPayload.crop_type = cropType;
    }

    const queryText = queryToSend;
    setInputText('');

    try {
      const response = await fetch('/agriculture/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_text: queryText,
          language: selectedLanguage,
            user_id: 'user-' + Date.now(),
          context: contextPayload
        })
      });
      const result = await response.json();
      if (result.status === 'success') {
        setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'sent', queryId: result.query_id } : msg));
        // Reset one-shot advanced inputs after successful send
        if (diseaseImagePreview) clearDiseaseImage();
      } else if (result.status === 'clarification_needed') {
        setIsLoading(false);
        addBotMessage(`I need more information: ${result.response?.questions?.join(', ')}`);
      } else {
        setIsLoading(false);
        setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'error' } : msg));
        addSystemMessage(`Error: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
      setMessages(prev => prev.map(msg => msg.id === userMessage.id ? { ...msg, status: 'error' } : msg));
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

  const diseaseExampleQueries = [
    "Identify this disease and suggest treatment",
    "What's wrong with my plant? How to cure it?",
    "Disease diagnosis and prevention tips",
    "Recommend fungicide for this condition"
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
            onChange={(e) => setSelectedLanguage(e.target.value as 'english' | 'tamil')}
            className="bg-green-700 text-white px-2 py-1 rounded text-sm"
          >
            <option value="english">English</option>
            <option value="tamil">தமிழ் (Tamil)</option>
          </select>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {/* Advanced Inputs Panel (streamlined) */}
        {showAdvanced && (
          <div className="bg-white border border-green-200 rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-green-700">Advanced Options</h3>
              <button onClick={() => setShowAdvanced(false)} className="text-sm text-green-600 hover:underline">Hide</button>
            </div>
            
            {/* Crop Type */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-600 mb-1">Crop Type (optional)</label>
                <input 
                  value={cropType} 
                  onChange={e => setCropType(e.target.value)} 
                  placeholder="e.g. Wheat, Rice, Tomato" 
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500" 
                />
              </div>
              {cropType && (
                <div className="flex items-end">
                  <button type="button" onClick={() => setCropType('')} className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1">Clear</button>
                </div>
              )}
            </div>
            
            {/* Disease Image Upload (secondary access) */}
            <div className="bg-gray-50 rounded-lg p-3">
              <label className="block text-sm font-medium text-gray-600 mb-2">Disease Image Upload</label>
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  {diseaseImagePreview ? (
                    <span className="text-green-600 font-medium">✓ Image attached and ready</span>
                  ) : (
                    "Use the camera button in the query bar for quick image upload"
                  )}
                </div>
                {diseaseImagePreview && (
                  <button type="button" onClick={clearDiseaseImage} className="text-sm text-red-600 hover:underline">Remove</button>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Supports 38 diseases across 14 crops including Apple, Tomato, Wheat, and more
              </div>
            </div>
            
            {/* Soil Data Toggle */}
            <div>
              <button 
                type="button" 
                onClick={() => setSoilFormOpen(o => !o)} 
                className="flex items-center text-sm font-medium text-green-700 hover:underline"
              >
                <span>{soilFormOpen ? '− Hide' : '+ Add'} Soil Test Data</span>
                {soilDataProvided() && !soilFormOpen && (
                  <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Data provided</span>
                )}
              </button>
              {soilFormOpen && (
                <div className="mt-3 space-y-3">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {['nitrogen','phosphorus','potassium','ph','organic_matter','moisture_content'].map(key => (
                      <div key={key}>
                        <label className="block text-xs uppercase tracking-wide text-gray-500 mb-1">
                          {key.replace('_',' ')}
                        </label>
                        <input 
                          type="number" 
                          step="any" 
                          value={soilData[key] || ''} 
                          onChange={e => updateSoilField(key, e.target.value)} 
                          className="w-full border rounded px-2 py-1 text-sm focus:ring-green-500 focus:border-green-500" 
                          placeholder={key === 'ph' ? '6.5' : key.includes('moisture') ? '15' : '50'} 
                        />
                      </div>
                    ))}
                  </div>
                  <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    💡 Provide lab soil test values (kg/ha for N/P/K, pH scale 5.5–8, moisture %)
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        {/* Existing messages */}
        {messages.length === 0 && (
          <div className="text-center text-gray-500">
            <Bot className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p className="mb-4">
              {diseaseImagePreview 
                ? "Image ready for disease analysis! Try asking:" 
                : "Welcome to Agricultural Advisory! Try asking:"
              }
            </p>
            <div className="space-y-2">
              {(diseaseImagePreview ? diseaseExampleQueries : exampleQueries).map((query, index) => (
                <button
                  key={index}
                  onClick={() => setInputText(query)}
                  className="block w-full text-left p-2 bg-white rounded border hover:bg-green-50 text-sm"
                >
                  "{query}"
                </button>
              ))}
            </div>
            {!diseaseImagePreview && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-700 mb-2">🌱 Quick Disease Detection:</p>
                <p className="text-xs text-green-600">Click the camera button in the query bar to upload a plant image for instant disease identification!</p>
              </div>
            )}
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
                  {/* Show uploaded image for user messages */}
                  {message.uploadedImage && (
                    <div className="mb-2">
                      <img 
                        src={message.uploadedImage} 
                        alt="Uploaded" 
                        className="max-w-xs rounded-lg border border-white/20"
                      />
                    </div>
                  )}
                  
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {/* Show detected category for user messages */}
                  {message.detectedCategory && message.type === 'user' && (
                    <div className="mt-2 text-xs bg-white/20 rounded px-2 py-1 inline-block">
                      📂 {message.detectedCategory.replace('_', ' ').toUpperCase()}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs ${
                        message.type === 'user' ? 'text-green-100' : 'text-gray-500'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </span>
                      {message.language && (
                        <span className={`text-xs px-1 rounded ${
                          message.type === 'user' ? 'bg-white/20 text-green-100' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {message.language === 'tamil' ? 'தமிழ்' : 'EN'}
                        </span>
                      )}
                    </div>
                    {message.status && getStatusIcon(message.status)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4 mr-12 min-w-[300px]">
              <div className="flex items-center space-x-3">
                <Bot className="w-6 h-6 text-green-600 flex-shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Loader2 className="w-4 h-4 animate-spin text-green-600" />
                    <span className="text-gray-700 font-medium">
                      {selectedLanguage === 'tamil' ? 'முகவர் செயல்படுகிறது...' : 'Agent Processing...'}
                    </span>
                  </div>
                  {loadingStep && (
                    <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded animate-pulse">
                      {loadingStep}
                    </div>
                  )}
                  <div className="mt-2 bg-gray-200 rounded-full h-1.5">
                    <div className="bg-green-600 h-1.5 rounded-full animate-pulse" style={{width: '75%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4 rounded-b-lg">
        {/* Image Preview Area (when image attached) */}
        {imagePreview && (
          <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-green-700">
                {selectedLanguage === 'tamil' ? 'நோய் கண்டறிதல் படம்' : 'Disease Detection Image'}
              </span>
              <button
                onClick={clearUploadedImage}
                className="text-red-600 hover:text-red-800 p-1"
                title="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-3">
              <img src={imagePreview} alt="Preview" className="h-16 w-16 object-cover rounded border" />
              <div className="text-sm text-green-600">
                {selectedLanguage === 'tamil' 
                  ? 'AgriSens AI மாதிரியுடன் நோய் கண்டறிதலுக்கு தயார்' 
                  : 'Ready for AI disease identification using AgriSens CNN model'}
              </div>
            </div>
          </div>
        )}
        
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={selectedLanguage === 'tamil' 
                ? `உங்கள் விவசாய கேள்வியை கேளுங்கள்...${imagePreview ? ' (நோய் கண்டறிதலுக்கு படம் தயார்)' : ' அல்லது நோய் கண்டறிதலுக்கு படம் பதிவேற்றவும்'}`
                : `Ask your agricultural question...${imagePreview ? ' (image ready for disease ID)' : ' or upload plant image for disease detection'}`
              }
              className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              rows={2}
              disabled={!isConnected || isLoading}
            />
            {/* Image Upload Button - Prominent in query bar */}
            <div className="absolute right-2 top-2">
              <label
                htmlFor="disease-image-upload"
                className={`cursor-pointer p-2 rounded-lg transition-colors ${
                  imagePreview 
                    ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                title={selectedLanguage === 'tamil' ? 'நோய் கண்டறிதலுக்கு படம் பதிவேற்றவும்' : 'Upload plant/leaf image for disease identification'}
              >
                <Camera className="w-5 h-5" />
              </label>
              <input
                id="disease-image-upload"
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </div>
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!isConnected || isLoading || (!inputText.trim() && !imagePreview)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span className="hidden sm:inline">
              {selectedLanguage === 'tamil' ? 'அனுப்பு' : 'Send'}
            </span>
          </button>
        </div>
        
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <div>
            {selectedLanguage === 'tamil' ? 'Enter அழுத்தி அனுப்பவும்' : 'Press Enter to send, Shift+Enter for new line'}
          </div>
          <div className="flex items-center space-x-2">
            {imagePreview && (
              <span className="text-green-600 font-medium">
                📷 {selectedLanguage === 'tamil' ? 'படம் தயார்' : 'Image ready'}
              </span>
            )}
            {soilDataProvided() && (
              <span className="text-blue-600 font-medium">
                🌱 {selectedLanguage === 'tamil' ? 'மண் தரவு சேர்க்கப்பட்டது' : 'Soil data included'}
              </span>
            )}
            {!showAdvanced && (
              <button 
                onClick={() => setShowAdvanced(true)} 
                className="text-green-600 hover:underline"
              >
                + {selectedLanguage === 'tamil' ? 'மேம்பட்ட விருப்பங்கள்' : 'Advanced options'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgricultureChat;
