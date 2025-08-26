/**
 * Global configuration for the application
 */

// Define the type for our config object
interface AppConfig {
  api: {
    url: string;
    baseUrl: string;
  };
  websocket: {
    url: string;
    reconnectInterval: number;
    maxReconnectAttempts: number;
  };
  features: {
    enableMockData: boolean;
    enableChatbot: boolean;
    enableWebSocketMock: boolean;
    // Adding these to ensure compatibility with other code
    enableSatelliteVisualization?: boolean;
    enableMultilingualSupport?: boolean;
  };
}

const config: AppConfig = {
  // API configuration
  api: {
    url: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  },
  
  // WebSocket configuration
  websocket: {
    // Using import.meta.env for Vite environment variables
    url: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080',
    reconnectInterval: 5000,
    maxReconnectAttempts: 10
  },
  
  // Feature flags
  features: {
    enableMockData: true,
    enableChatbot: true,
    enableWebSocketMock: true // Set this to true to use mock WebSocket responses
  }
};

export default config;
