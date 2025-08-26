import { WebSocketService, WebSocketConnectionStatus } from './websocketService';
import config from '../config';
import { v4 as uuidv4 } from 'uuid';

// Create a mock WebSocket implementation to handle the case when server is unavailable
class MockWebSocketHandler {
  private messageHandlers: ((message: any) => void)[] = [];
  
  addMessageHandler(handler: (message: any) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }
  
  simulateReceiveMessage(message: any) {
    this.messageHandlers.forEach(handler => handler(message));
  }

  // Mock response generator for local testing
  handleUserMessage(text: string) {
    // Simulate typing indicator
    setTimeout(() => {
      this.simulateReceiveMessage({
        type: 'chat_typing',
        timestamp: new Date().toISOString()
      });
      
      // Then simulate a response after a delay
      setTimeout(() => {
        const response = this.getMockResponse(text);
        this.simulateReceiveMessage({
          type: 'chat_message',
          message_id: `bot-${Date.now()}`,
          content: response.text,
          sender: 'bot',
          options: response.options,
          timestamp: new Date().toISOString()
        });
      }, 1500);
    }, 500);
  }
  
  getMockResponse(text: string): { text: string, options?: Array<{ text: string, action: string }> } {
    const input = text.toLowerCase();
    let options;
    
    if (input.includes('weather')) {
      options = [
        { text: '🗓️ Weekly Forecast', action: 'weekly forecast' },
        { text: '☔ Rain Probability', action: 'rain chances' },
        { text: '🌡️ Temperature Trends', action: 'temperature' }
      ];
      return {
        text: 'Based on your location, our weather forecast shows clear skies for the next 3 days with a high of 78°F and low of 62°F. Perfect for crop maintenance! There\'s a 20% chance of light rain on Friday.',
        options
      };
    } else if (input.includes('pest')) {
      options = [
        { text: '🌿 Organic Solutions', action: 'organic pest control' },
        { text: '🧪 Chemical Options', action: 'chemical pest control' },
        { text: '🔍 Identify Pests', action: 'identify pests' }
      ];
      return {
        text: 'I detect you\'re asking about pest control. Based on recent reports in your area, farmers are seeing increased aphid activity on crops. Would you like information about organic or chemical treatments?',
        options
      };
    } else if (input.includes('crop')) {
      options = [
        { text: '🌾 Seasonal Crops', action: 'seasonal crops' },
        { text: '💧 Water Requirements', action: 'crop water needs' },
        { text: '🌿 Crop Rotation', action: 'crop rotation' }
      ];
      return {
        text: 'Based on your soil analysis (pH 6.8, loamy texture) and current season, we recommend planting wheat, barley, or pulse crops for maximum yield. Your location has received sufficient rainfall for germination.',
        options
      };
    } else if (input.includes('market') || input.includes('price')) {
      options = [
        { text: '📊 Price Trends', action: 'market trends' },
        { text: '📈 Price Forecasts', action: 'price forecast' },
        { text: '🚚 Distribution Channels', action: 'distribution' }
      ];
      return {
        text: 'Current market prices show: Corn: $4.85/bu (+2.1% weekly), Soybeans: $13.20/bu (+1.5% weekly), Wheat: $6.75/bu (-0.5% weekly). Organic produce is trading at a 15-25% premium over conventional.',
        options
      };
    }
    
    return {
      text: 'I understand you\'re asking about: "' + text + '". How can I help you with agricultural information today?',
      options: [
        { text: '🌦️ Weather Forecast', action: 'weather' },
        { text: '🐛 Pest Control', action: 'pests' },
        { text: '💰 Market Prices', action: 'prices' },
        { text: '🌱 Crop Suggestions', action: 'crops' }
      ]
    };
  }
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'system';
  timestamp: string;
  options?: Array<{ text: string; action: string }>;
}

export interface ChatBotWebSocketMessage {
  type: 'chat_message' | 'chat_typing' | 'chat_options';
  message_id?: string;
  content?: string;
  sender?: 'user' | 'bot' | 'system';
  options?: Array<{ text: string; action: string }>;
  timestamp: string;
}

export class ChatBotWebSocketService extends WebSocketService {
  private messageHandlers: Map<string, (message: ChatMessage) => void> = new Map();
  private typingHandlers: Map<string, (isTyping: boolean) => void> = new Map();
  private mockHandler: MockWebSocketHandler;
  
  constructor() {
    // Connect to the chat-specific WebSocket endpoint
    // Construct WebSocket URL from base URL, replacing http/https with ws/wss
    const wsBaseUrl = config.websocket.url.replace(/^(http|ws)s?:\/\/([^\/]+).*$/, 'ws://$2');
    super({
      url: `${wsBaseUrl}/ws/chat`
    });
    
    // Create a mock handler for offline mode
    this.mockHandler = new MockWebSocketHandler();
    
    // Connect mock handler to WebSocketService's message system
    this.mockHandler.addMessageHandler((message) => {
      // Process the mock message the same way we would a real WebSocket message
      if (message && message.type) {
        this.processWebSocketMessage(message);
      }
    });
    
    // Set up the message handler for chat-specific messages
    this.onMessage('chat_internal', (wsMessage: any) => {
      this.processWebSocketMessage(wsMessage);
    });
  }
  
  // Process incoming WebSocket messages
  private processWebSocketMessage(wsMessage: any) {
      if (!wsMessage) return;
      
      try {
        // Handle different message types
        const message = wsMessage as ChatBotWebSocketMessage;
        
        switch (message.type) {
          case 'chat_message':
            if (message.content && message.sender) {
              const chatMessage: ChatMessage = {
                id: message.message_id || `msg-${Date.now()}`,
                text: message.content,
                sender: message.sender,
                timestamp: message.timestamp,
                options: message.options
              };
              this.notifyMessageHandlers(chatMessage);
            }
            break;
            
          case 'chat_typing':
            this.notifyTypingHandlers(true);
            // Auto-reset typing after 3 seconds if no message arrives
            setTimeout(() => {
              this.notifyTypingHandlers(false);
            }, 3000);
            break;
            
          case 'chat_options':
            // Handle options sent separately
            if (message.message_id && message.options) {
              this.notifyOptionsUpdate(message.message_id, message.options);
            }
            break;
        }
      } catch (error) {
        console.error('Error processing chat message:', error);
      }
  }
  
  // Send a chat message to the backend
  public sendMessage(text: string): boolean {
    const message: ChatBotWebSocketMessage = {
      type: 'chat_message',
      content: text,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    // Always return true for real-time UI feedback
    const sent = this.send(message);
    
    // If we're not connected or configured to use mocks, use the mock handler
    if ((!sent && config.features.enableWebSocketMock) || 
         this.getConnectionStatus() !== WebSocketConnectionStatus.CONNECTED) {
      // Process with mock handler
      this.mockHandler.handleUserMessage(text);
      return true; // Pretend it was sent successfully
    }
    
    return sent;
  }
  
  // Register a handler for incoming chat messages
  public onChatMessage(id: string, handler: (message: ChatMessage) => void): () => void {
    this.messageHandlers.set(id, handler);
    return () => {
      this.messageHandlers.delete(id);
    };
  }
  
  // Register a handler for typing indicators
  public onTypingIndicator(id: string, handler: (isTyping: boolean) => void): () => void {
    this.typingHandlers.set(id, handler);
    return () => {
      this.typingHandlers.delete(id);
    };
  }
  
  // Notify all registered message handlers
  private notifyMessageHandlers(message: ChatMessage): void {
    this.messageHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in chat message handler:', error);
      }
    });
  }
  
  // Notify all registered typing handlers
  private notifyTypingHandlers(isTyping: boolean): void {
    this.typingHandlers.forEach(handler => {
      try {
        handler(isTyping);
      } catch (error) {
        console.error('Error in typing indicator handler:', error);
      }
    });
  }
  
  // Update options for a specific message
  private notifyOptionsUpdate(messageId: string, options: Array<{ text: string; action: string }>): void {
    // This would need to be implemented if you want to update options after a message is sent
    console.log(`Received options update for message ${messageId}:`, options);
  }
}

// Create and export a singleton instance
export const chatBotService = new ChatBotWebSocketService();
