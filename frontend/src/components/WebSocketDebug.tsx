import React, { useState, useEffect } from 'react';
import config from '../config';

interface WebSocketDebugProps {
  className?: string;
}

const WebSocketDebug: React.FC<WebSocketDebugProps> = ({ className = '' }) => {
  const [status, setStatus] = useState<string>('Disconnected');
  const [logs, setLogs] = useState<string[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    setLogs(prev => [...prev.slice(-20), logEntry]); // Keep last 20 logs
    console.log(logEntry);
  };

  const connect = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      addLog('Already connected');
      return;
    }

    // Construct WebSocket URL from base URL, replacing http/https with ws/wss
    const wsBaseUrl = config.websocket.url.replace(/^(http|ws)s?:\/\/([^\/]+).*$/, 'ws://$2');
    const url = `${wsBaseUrl}/ws/updates`;
    addLog(`Connecting to: ${url}`);
    setStatus('Connecting...');

    try {
      const newWs = new WebSocket(url);

      newWs.onopen = () => {
        addLog('✅ WebSocket connected successfully');
        setStatus('Connected');
      };

      newWs.onclose = (event) => {
        addLog(`❌ WebSocket closed: Code ${event.code}, Reason: ${event.reason}`);
        setStatus('Disconnected');
        setWs(null);
      };

      newWs.onerror = (error) => {
        addLog(`❌ WebSocket error: ${error}`);
        setStatus('Error');
      };

      newWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          addLog(`📨 Message: ${data.type || 'unknown'}`);
        } catch (e) {
          addLog(`📨 Raw message received`);
        }
      };

      setWs(newWs);
    } catch (error) {
      addLog(`❌ Failed to create WebSocket: ${error}`);
      setStatus('Error');
    }
  };

  const disconnect = () => {
    if (ws) {
      ws.close(1000, 'User disconnected');
      setWs(null);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  useEffect(() => {
    addLog('WebSocket Debug Component mounted');
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const getStatusColor = () => {
    if (status.includes('Connected')) return '#4caf50';
    if (status.includes('Connecting')) return '#ff9800';
    if (status.includes('Error')) return '#f44336';
    return '#666';
  };

  return (
    <div className={`websocket-debug ${className}`} style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: '#2d2d2d',
      border: '1px solid #404040',
      borderRadius: '8px',
      padding: '15px',
      minWidth: '300px',
      maxWidth: '400px',
      zIndex: 1000,
      fontSize: '12px',
      color: '#fff'
    }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#61dafb' }}>WebSocket Debug</h4>
      
      <div style={{ 
        padding: '5px 10px', 
        background: getStatusColor(), 
        borderRadius: '4px', 
        marginBottom: '10px',
        color: '#fff',
        fontWeight: 'bold'
      }}>
        Status: {status}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <button 
          onClick={connect} 
          style={{
            background: '#4caf50',
            color: 'white',
            border: 'none',
            padding: '5px 10px',
            borderRadius: '4px',
            marginRight: '5px',
            cursor: 'pointer'
          }}
        >
          Connect
        </button>
        <button 
          onClick={disconnect}
          style={{
            background: '#f44336',
            color: 'white',
            border: 'none',
            padding: '5px 10px',
            borderRadius: '4px',
            marginRight: '5px',
            cursor: 'pointer'
          }}
        >
          Disconnect
        </button>
        <button 
          onClick={clearLogs}
          style={{
            background: '#666',
            color: 'white',
            border: 'none',
            padding: '5px 10px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Clear
        </button>
      </div>

      <div style={{
        background: '#1a1a1a',
        padding: '10px',
        borderRadius: '4px',
        maxHeight: '200px',
        overflowY: 'auto',
        fontFamily: 'monospace',
        fontSize: '11px'
      }}>
        {logs.length === 0 ? (
          <div style={{ color: '#888' }}>No logs yet...</div>
        ) : (
          logs.map((log, index) => (
            <div key={index} style={{ marginBottom: '2px' }}>
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WebSocketDebug;
