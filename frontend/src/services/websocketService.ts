// WebSocket message types that match the backend implementation
export interface WebSocketMessage {
  type: 'workflow_update' | 'agent_update' | 'system_notification';
  timestamp: string;
}

export interface WorkflowUpdateMessage extends WebSocketMessage {
  type: 'workflow_update';
  event: 'workflow_started' | 'step_completed' | 'workflow_completed' | 'workflow_failed';
  workflow_id: string;
  status: 'running' | 'completed' | 'failed';
  current_step: string;
  progress: number;
  details: {
    [key: string]: any;
  };
}

export interface AgentUpdateMessage extends WebSocketMessage {
  type: 'agent_update';
  event: 'status_changed';
  agent_id: string;
  status: string;
  previous_status: string;
  details: {
    [key: string]: any;
  };
}

export interface SystemNotificationMessage extends WebSocketMessage {
  type: 'system_notification';
  event_type: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
  details: {
    [key: string]: any;
  };
}

export type AllWebSocketMessages = WorkflowUpdateMessage | AgentUpdateMessage | SystemNotificationMessage;

export const WebSocketConnectionStatus = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
  RECONNECTING: 'reconnecting'
} as const;

export type WebSocketConnectionStatus = typeof WebSocketConnectionStatus[keyof typeof WebSocketConnectionStatus];

export interface WebSocketServiceConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketServiceConfig;
  private reconnectAttempts = 0;
  private reconnectTimeoutId: number | null = null;
  private heartbeatIntervalId: number | null = null;
  private connectionStatus: WebSocketConnectionStatus = WebSocketConnectionStatus.DISCONNECTED;
  private messageHandlers: Map<string, (message: AllWebSocketMessages) => void> = new Map();
  private statusHandlers: Map<string, (status: WebSocketConnectionStatus) => void> = new Map();

  constructor(config: WebSocketServiceConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...config
    };
    
    console.log(`🚀 WebSocketService constructor: status initialized as "${this.connectionStatus}"`);
    console.log(`   Config:`, this.config);
  }

  public connect(): void {
    // Prevent multiple connections
    if (this.ws) {
      if (this.ws.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        return;
      } else if (this.ws.readyState === WebSocket.CONNECTING) {
        console.log('WebSocket already connecting');
        return;
      }
    }

    this.setConnectionStatus(WebSocketConnectionStatus.CONNECTING);
    console.log(`Attempting to connect to WebSocket: ${this.config.url}`);
    
    try {
      this.ws = new WebSocket(this.config.url);
      console.log('WebSocket instance created, setting up event listeners...');
      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.setConnectionStatus(WebSocketConnectionStatus.ERROR);
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.clearReconnectTimeout();
    this.clearHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected');
      this.ws = null;
    }
    
    this.setConnectionStatus(WebSocketConnectionStatus.DISCONNECTED);
  }

  public send(message: object): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        return false;
      }
    }
    
    console.warn('WebSocket not connected, cannot send message');
    return false;
  }

  public onMessage(id: string, handler: (message: AllWebSocketMessages) => void): () => void {
    this.messageHandlers.set(id, handler);
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(id);
    };
  }

  public onStatusChange(id: string, handler: (status: WebSocketConnectionStatus) => void): () => void {
    console.log(`📋 Registering status handler '${id}' (current status: ${this.connectionStatus})`);
    this.statusHandlers.set(id, handler);
    
    // Immediately call with current status
    console.log(`   Immediately calling handler '${id}' with status: ${this.connectionStatus}`);
    handler(this.connectionStatus);
    
    // Return unsubscribe function
    return () => {
      console.log(`🗑️ Unregistering status handler '${id}'`);
      this.statusHandlers.delete(id);
    };
  }

  public getConnectionStatus(): WebSocketConnectionStatus {
    return this.connectionStatus;
  }

  public isConnected(): boolean {
    return this.connectionStatus === WebSocketConnectionStatus.CONNECTED;
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('✅ WebSocket onopen event fired!');
      console.log('   Connected to:', this.config.url);
      console.log('   WebSocket readyState:', this.ws?.readyState);
      console.log('   Previous status:', this.connectionStatus);
      this.reconnectAttempts = 0;
      this.setConnectionStatus(WebSocketConnectionStatus.CONNECTED);
      this.startHeartbeat();
      console.log('   Status handlers count:', this.statusHandlers.size);
      console.log('   New status should be:', WebSocketConnectionStatus.CONNECTED);
    };

    this.ws.onclose = (event) => {
      console.log('❌ WebSocket connection closed:', event.code, event.reason);
      console.log('Close event details:', { code: event.code, reason: event.reason, wasClean: event.wasClean });
      this.clearHeartbeat();
      
      if (event.code !== 1000) { // Not a normal closure
        this.setConnectionStatus(WebSocketConnectionStatus.DISCONNECTED);
        this.scheduleReconnect();
      } else {
        this.setConnectionStatus(WebSocketConnectionStatus.DISCONNECTED);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error occurred:', error);
      console.log('WebSocket readyState:', this.ws?.readyState);
      this.setConnectionStatus(WebSocketConnectionStatus.ERROR);
    };

    this.ws.onmessage = (event) => {
      try {
        const message: AllWebSocketMessages = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error, event.data);
      }
    };
  }

  private handleMessage(message: AllWebSocketMessages): void {
    // Log received message for debugging
    console.log('WebSocket message received:', message);
    
    // Notify all registered handlers
    this.messageHandlers.forEach((handler) => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  private setConnectionStatus(status: WebSocketConnectionStatus): void {
    if (this.connectionStatus !== status) {
      const oldStatus = this.connectionStatus;
      this.connectionStatus = status;
      console.log(`🔄 WebSocket status changed: ${oldStatus} → ${status}`);
      console.log(`   Current handlers: ${this.statusHandlers.size}`);
      
      // Notify all status handlers
      this.statusHandlers.forEach((handler, id) => {
        try {
          console.log(`   Notifying handler '${id}' of status change to: ${status}`);
          handler(status);
        } catch (error) {
          console.error(`   Error in status handler '${id}':`, error);
        }
      });
    } else {
      console.log(`⚡ WebSocket status unchanged: ${status} (not notifying handlers)`);
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts!) {
      console.error('Max reconnection attempts reached');
      this.setConnectionStatus(WebSocketConnectionStatus.ERROR);
      return;
    }

    this.clearReconnectTimeout();
    
    const delay = this.config.reconnectInterval! * Math.pow(1.5, this.reconnectAttempts);
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts + 1} in ${delay}ms`);
    
    this.setConnectionStatus(WebSocketConnectionStatus.RECONNECTING);
    
    this.reconnectTimeoutId = window.setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }

  private startHeartbeat(): void {
    this.clearHeartbeat();
    
    this.heartbeatIntervalId = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, this.config.heartbeatInterval!);
  }

  private clearHeartbeat(): void {
    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId);
      this.heartbeatIntervalId = null;
    }
  }
}

// Import the WebSocket URL from configuration
import getWebSocketUrl from './websocketConfig.ts';

// Default WebSocket service instance
export const defaultWebSocketService = new WebSocketService({
  url: getWebSocketUrl()
});
