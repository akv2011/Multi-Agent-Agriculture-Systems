/**
 * WebSocket Configuration for Multi-Agent Agriculture Systems
 * 
 * Provides the WebSocket URL from centralized configuration with a safe fallback.
 */

import config from '../config';

/**
 * Get the WebSocket URL from environment configuration.
 * Ensures a valid WebSocket protocol is returned.
 * 
 * @returns WebSocket URL string
 */
const getWebSocketUrl = (): string => {
  const url = config.websocket.url;

  if (!url.startsWith("ws://") && !url.startsWith("wss://")) {
    console.warn(
      `⚠️ Invalid WebSocket URL provided in configuration: "${url}". Falling back to ws://localhost:8765`
    );
    return "ws://localhost:8765";
  }

  return url;
};

export default getWebSocketUrl;

