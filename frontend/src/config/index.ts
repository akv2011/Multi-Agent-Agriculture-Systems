/**
 * Frontend Configuration System
 * 
 * Centralized configuration management for the frontend application
 * Loads configuration from environment variables with appropriate defaults
 */

export interface AppConfig {
  api: {
    baseUrl: string;
  };
  websocket: {
    url: string;
  };
  features: {
    enableSatelliteVisualization: boolean;
    enableMultilingualSupport: boolean;
    enableWebSocketMock?: boolean;
    enableMockData?: boolean;
    enableChatbot?: boolean;
  };
  analytics?: {
    key?: string;
  };
}

/**
 * Parse boolean from environment variable string
 */
const parseBoolean = (value: string | undefined): boolean => {
  if (!value) return false;
  return ['true', '1', 'yes'].includes(value.toLowerCase());
};

/**
 * Application configuration loaded from environment variables
 * Using import.meta.env for Vite compatibility
 */
const config: AppConfig = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  },
  websocket: {
    url: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8765',
  },
  features: {
    enableSatelliteVisualization: parseBoolean(import.meta.env.VITE_ENABLE_SATELLITE_VISUALIZATION),
    enableMultilingualSupport: parseBoolean(import.meta.env.VITE_ENABLE_MULTILINGUAL_SUPPORT),
    enableWebSocketMock: parseBoolean(import.meta.env.VITE_ENABLE_WEBSOCKET_MOCK) || true,
    enableMockData: parseBoolean(import.meta.env.VITE_ENABLE_MOCK_DATA) || true,
    enableChatbot: parseBoolean(import.meta.env.VITE_ENABLE_CHATBOT) || true,
  },
  analytics: {
    key: import.meta.env.VITE_ANALYTICS_KEY,
  },
};

export default config;
