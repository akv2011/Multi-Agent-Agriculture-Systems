import '../App.css'
import './Dashboard.css'
import AgentList from './AgentList'
import type { Agent } from './AgentList'
import type { Workflow } from './WorkflowVisualizer'
import { useWebSocket, useAgentUpdates, useWorkflowUpdates } from '../hooks/useWebSocket'
import { WebSocketConnectionStatus } from '../services/websocketService'
import { useMemo, useEffect, useState } from 'react'

// Mock data for testing
const mockAgents: Agent[] = [
  {
    id: 'agent-001',
    name: 'Text Analysis Agent',
    status: 'running',
    lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    currentTask: 'Analyzing sentiment in customer reviews',
    metrics: {
      tasksCompleted: 23,
      averageExecutionTime: 2.4,
      successRate: 0.96
    }
  },
  {
    id: 'agent-002',
    name: 'Data Processing Agent',
    status: 'idle',
    lastActivity: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    metrics: {
      tasksCompleted: 47,
      averageExecutionTime: 1.8,
      successRate: 0.98
    }
  },
  {
    id: 'agent-003',
    name: 'API Interaction Agent',
    status: 'busy',
    lastActivity: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    currentTask: 'Fetching external API data',
    metrics: {
      tasksCompleted: 12,
      averageExecutionTime: 4.2,
      successRate: 0.91
    }
  },
  {
    id: 'agent-004',
    name: 'Backup Agent',
    status: 'error',
    lastActivity: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    currentTask: 'Failed: Connection timeout',
    metrics: {
      tasksCompleted: 8,
      averageExecutionTime: 3.1,
      successRate: 0.75
    }
  },
  {
    id: 'agent-005',
    name: 'Monitor Agent',
    status: 'offline',
    lastActivity: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    metrics: {
      tasksCompleted: 156,
      averageExecutionTime: 0.8,
      successRate: 0.99
    }
  }
];

// Mock workflow data for testing
const mockWorkflow: Workflow = {
  id: 'workflow-001',
  name: 'Customer Review Analysis Pipeline',
  status: 'running',
  progress: 0.6,
  startTime: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
  totalDuration: 10 * 60 * 1000,
  steps: [
    {
      id: 'step-1',
      name: 'Initialize Data Source',
      status: 'completed',
      startTime: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 9 * 60 * 1000).toISOString(),
      duration: 45000,
      output: 'Connected to customer review database\nLoaded 1,247 reviews for processing',
      agent: 'agent-002'
    },
    {
      id: 'step-2',
      name: 'Text Preprocessing',
      status: 'completed',
      startTime: new Date(Date.now() - 9 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 7 * 60 * 1000).toISOString(),
      duration: 120000,
      output: 'Cleaned and tokenized text data\nRemoved stop words and normalized format',
      agent: 'agent-001'
    },
    {
      id: 'step-3',
      name: 'Sentiment Analysis',
      status: 'in-progress',
      startTime: new Date(Date.now() - 7 * 60 * 1000).toISOString(),
      agent: 'agent-001'
    },
    {
      id: 'step-4',
      name: 'Category Classification',
      status: 'pending',
      agent: 'agent-003'
    },
    {
      id: 'step-5',
      name: 'Generate Report',
      status: 'pending',
      agent: 'agent-002'
    }
  ],
  metadata: {
    priority: 'high',
    source: 'customer_feedback_system',
    estimated_completion: new Date(Date.now() + 5 * 60 * 1000).toISOString()
  }
};

function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  const { connectionStatus, isConnected, connect, disconnect, lastMessage } = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      console.log('Received WebSocket message:', message);
    },
    onStatusChange: (status) => {
      console.log('WebSocket status changed:', status);
    }
  });

  useEffect(() => {
    console.log(`🔄 Dashboard component: connectionStatus changed to "${connectionStatus}"`);
    console.log(`   isConnected: ${isConnected}`);
  }, [connectionStatus, isConnected]);

  (window as any).debugWebSocket = () => {
    console.log('=== WebSocket Debug Info ===');
    console.log('Current connection status:', connectionStatus);
    console.log('Is connected:', isConnected);
    console.log('Last message:', lastMessage);
    console.log('Status enum values:', WebSocketConnectionStatus);
    console.log('Current status type:', typeof connectionStatus);
    console.log('Current status comparison:', connectionStatus === WebSocketConnectionStatus.CONNECTED);
    console.log('============================');
  };

  const { getAllAgents } = useAgentUpdates();
  const { getAllWorkflows, getActiveWorkflows } = useWorkflowUpdates();

  const realTimeAgents = getAllAgents();
  const realTimeWorkflows = getAllWorkflows();
  const activeWorkflows = getActiveWorkflows();

  const mapBackendStatusToFrontend = (backendStatus: string): Agent['status'] => {
    const statusMap: Record<string, Agent['status']> = {
      'idle': 'idle',
      'running': 'running',
      'busy': 'busy',
      'active': 'running',
      'error': 'error',
      'failed': 'error',
      'offline': 'offline',
      'disconnected': 'offline'
    };
    return statusMap[backendStatus?.toLowerCase()] || 'idle';
  };

  const currentWorkflow = useMemo(() => {
    if (activeWorkflows.length > 0) {
      const rtWorkflow = activeWorkflows[0];
      return {
        id: rtWorkflow.id,
        name: rtWorkflow.details?.name || `Workflow ${rtWorkflow.id}`,
        status: rtWorkflow.status as Workflow['status'],
        progress: rtWorkflow.progress || 0,
        startTime: rtWorkflow.details?.started_at,
        endTime: rtWorkflow.details?.completed_at,
        totalDuration: rtWorkflow.details?.execution_time ? rtWorkflow.details.execution_time * 1000 : undefined,
        steps: rtWorkflow.details?.steps || mockWorkflow.steps.map((step, index) => ({
          ...step,
          status: index < (rtWorkflow.details?.steps_completed || 0) ? 'completed' as const : 
                  index === (rtWorkflow.details?.steps_completed || 0) ? 'in-progress' as const : 
                  'pending' as const
        })),
        metadata: rtWorkflow.details
      } as Workflow;
    }
    return mockWorkflow;
  }, [activeWorkflows]);

  const mergedAgents = useMemo(() => {
    const agentMap = new Map<string, Agent>();
    mockAgents.forEach(agent => {
      agentMap.set(agent.id, agent);
    });
    realTimeAgents.forEach(rtAgent => {
      const existingAgent = agentMap.get(rtAgent.id);
      if (existingAgent) {
        agentMap.set(rtAgent.id, {
          ...existingAgent,
          status: mapBackendStatusToFrontend(rtAgent.status),
          lastActivity: rtAgent.last_update,
          currentTask: rtAgent.details?.current_task || existingAgent.currentTask
        });
      } else {
        agentMap.set(rtAgent.id, {
          id: rtAgent.id,
          name: rtAgent.details?.name || `Agent ${rtAgent.id}`,
          status: mapBackendStatusToFrontend(rtAgent.status),
          lastActivity: rtAgent.last_update,
          currentTask: rtAgent.details?.current_task,
          metrics: rtAgent.details?.metrics || {
            tasksCompleted: 0,
            averageExecutionTime: 0,
            successRate: 1.0
          }
        });
      }
    });
    return Array.from(agentMap.values());
  }, [realTimeAgents]);

  const handleAgentClick = (agent: Agent) => {
    console.log('Agent clicked:', agent);
  };

  const getConnectionStatusDisplay = () => {
    switch (connectionStatus) {
      case WebSocketConnectionStatus.CONNECTED:
        return '🟢 Connected';
      case WebSocketConnectionStatus.CONNECTING:
        return '🟡 Connecting';
      case WebSocketConnectionStatus.RECONNECTING:
        return '🟠 Reconnecting';
      case WebSocketConnectionStatus.ERROR:
        return '🔴 Error';
      default:
        return '🔴 Disconnected';
    }
  };

  const handleConnectionToggle = () => {
    if (isConnected) {
      disconnect();
    } else {
      connect();
    }
  };

  const activeAgentCount = mergedAgents.filter(agent => 
    ['running', 'busy'].includes(agent.status)
  ).length;

  const handleStepClick = (step: any) => {
    console.log('Workflow step clicked:', step);
  };

  return (
    <div className="dashboard-content">
      <header className="dashboard-header">
        <div className="search-bar">
          <input 
            type="text" 
            placeholder="Search workflows, agents, or reports..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="search-btn">Search</button>
        </div>
        <div className="header-info">
          <span 
            className="connection-status"
            onClick={handleConnectionToggle}
            style={{ cursor: 'pointer' }}
            title={`Click to toggle connection. Current: ${connectionStatus}`}
          >
            {getConnectionStatusDisplay()}
          </span>
          <span className="timestamp">{new Date().toLocaleTimeString()}</span>
        </div>
      </header>

      <main className="dashboard-main">
        {/* Metrics Row */}
        <div className="metrics-row" style={{ 
          gridColumn: "1 / -1", 
          display: "flex", 
          gap: "1.5rem", 
          marginBottom: "1.5rem" 
        }}>
          <div className="metric-card" style={{
            flex: 1,
            backgroundColor: "#fff",
            borderRadius: "12px",
            padding: "1.2rem",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
            display: "flex",
            flexDirection: "column",
            transition: "all 0.3s ease",
            border: "1px solid rgba(240, 242, 245, 0.8)",
            position: "relative",
            overflow: "hidden"
          }}>
            <span style={{ fontSize: "0.8rem", color: "#6B7280", fontWeight: "500" }}>Active Agents</span>
            <div style={{ display: "flex", alignItems: "baseline", marginTop: "0.5rem" }}>
              <span style={{ fontSize: "1.8rem", fontWeight: "700", color: "#18A1CC" }}>{activeAgentCount}</span>
              <span style={{ fontSize: "1rem", marginLeft: "0.5rem", color: "#22C55E" }}>/{mergedAgents.length}</span>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#6B7280", marginTop: "0.5rem" }}>Working on tasks</span>
            <div style={{ 
              position: "absolute", 
              right: "-10px", 
              bottom: "-10px", 
              width: "60px", 
              height: "60px", 
              borderRadius: "50%", 
              backgroundColor: "rgba(24, 161, 204, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem"
            }}>🤖</div>
          </div>
          
          <div className="metric-card" style={{
            flex: 1,
            backgroundColor: "#fff",
            borderRadius: "12px",
            padding: "1.2rem",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
            display: "flex",
            flexDirection: "column",
            transition: "all 0.3s ease",
            border: "1px solid rgba(240, 242, 245, 0.8)",
            position: "relative",
            overflow: "hidden"
          }}>
            <span style={{ fontSize: "0.8rem", color: "#6B7280", fontWeight: "500" }}>Active Workflows</span>
            <div style={{ display: "flex", alignItems: "baseline", marginTop: "0.5rem" }}>
              <span style={{ fontSize: "1.8rem", fontWeight: "700", color: "#DFBA47" }}>{activeWorkflows.length}</span>
              <span style={{ fontSize: "1rem", marginLeft: "0.5rem", color: "#22C55E" }}>/{realTimeWorkflows.length || 1}</span>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#6B7280", marginTop: "0.5rem" }}>In execution</span>
            <div style={{ 
              position: "absolute", 
              right: "-10px", 
              bottom: "-10px", 
              width: "60px", 
              height: "60px", 
              borderRadius: "50%", 
              backgroundColor: "rgba(223, 186, 71, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem"
            }}>📊</div>
          </div>
          
          <div className="metric-card" style={{
            flex: 1,
            backgroundColor: "#fff",
            borderRadius: "12px",
            padding: "1.2rem",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
            display: "flex",
            flexDirection: "column",
            transition: "all 0.3s ease",
            border: "1px solid rgba(240, 242, 245, 0.8)",
            position: "relative",
            overflow: "hidden"
          }}>
            <span style={{ fontSize: "0.8rem", color: "#6B7280", fontWeight: "500" }}>Overall Progress</span>
            <div style={{ display: "flex", alignItems: "baseline", marginTop: "0.5rem" }}>
              <span style={{ fontSize: "1.8rem", fontWeight: "700", color: "#22C55E" }}>
                {Math.round(currentWorkflow.progress * 100)}%
              </span>
            </div>
            <div style={{ marginTop: "0.5rem", height: "6px", backgroundColor: "rgba(34, 197, 94, 0.1)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ 
                height: "100%", 
                width: `${Math.round(currentWorkflow.progress * 100)}%`, 
                backgroundColor: "#22C55E",
                borderRadius: "3px",
                transition: "width 0.5s ease"
              }}></div>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#6B7280", marginTop: "0.5rem" }}>Tasks completed</span>
            <div style={{ 
              position: "absolute", 
              right: "-10px", 
              bottom: "-10px", 
              width: "60px", 
              height: "60px", 
              borderRadius: "50%", 
              backgroundColor: "rgba(34, 197, 94, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.5rem"
            }}>✅</div>
          </div>
        </div>

        {/* Analysis Controls and Temporal Trends Row */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "1.5rem",
          marginBottom: "1.5rem",
          gridColumn: "1 / -1"
        }}>
          {/* Temporal Trends & Spectral Profile Box - Left 50% */}
          <div className="dashboard-card" style={{ overflow: "hidden" }}>
            <div className="dashboard-card-header">
              <h3 className="dashboard-card-title">
                <span>📈 Temporal Trends & Spectral Profile</span>
              </h3>
              <div className="card-actions">
                <span style={{ cursor: 'pointer', fontSize: '0.9rem', opacity: '0.7' }} title="Toggle view">📊</span>
              </div>
            </div>
            <div className="dashboard-card-body" style={{ padding: '1rem', height: "calc(100% - 120px)", overflowY: "auto" }}>
              {/* Temporal Trends Analysis - Top Half */}
              <div style={{
                background: "#f8f9fa",
                borderRadius: "8px",
                padding: "1rem",
                border: "1px solid #e9ecef",
                marginBottom: "1rem",
                height: "48%"
              }}>
                <h4 style={{ marginBottom: "1rem", color: "#495057", fontSize: "0.9rem" }}>📈 Temporal Trends Analysis</h4>
                <div style={{
                  background: "white",
                  borderRadius: "6px",
                  padding: "0.75rem",
                  marginBottom: "1rem",
                  border: "1px solid #dee2e6",
                  height: "60%"
                }}>
                  <canvas
                    width="400"
                    height="180"
                    style={{
                      width: "100%",
                      height: "100%",
                      background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                      borderRadius: "4px"
                    }}
                    ref={(canvas) => {
                      if (canvas) {
                        const ctx = canvas.getContext('2d');
                        if (ctx) {
                          // Clear canvas
                          ctx.clearRect(0, 0, canvas.width, canvas.height);

                          // Draw NDVI trend line
                          const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                          const ndviValues = [0.3, 0.35, 0.4, 0.45, 0.65, 0.7];

                          ctx.strokeStyle = '#27ae60';
                          ctx.lineWidth = 3;
                          ctx.beginPath();

                          const stepX = canvas.width / (months.length - 1);
                          const maxY = Math.max(...ndviValues);

                          ndviValues.forEach((value, index) => {
                            const x = index * stepX;
                            const y = canvas.height - (value / maxY) * (canvas.height - 40) - 20;

                            if (index === 0) {
                              ctx.moveTo(x, y);
                            } else {
                              ctx.lineTo(x, y);
                            }

                            // Draw points
                            ctx.fillStyle = '#27ae60';
                            ctx.beginPath();
                            ctx.arc(x, y, 4, 0, 2 * Math.PI);
                            ctx.fill();

                            // Labels
                            ctx.fillStyle = '#2c3e50';
                            ctx.font = '12px Arial';
                            ctx.textAlign = 'center';
                            ctx.fillText(months[index], x, canvas.height - 5);
                            ctx.fillText(value.toFixed(2), x, y - 10);
                          });

                          ctx.stroke();
                        }
                      }
                    }}
                  />
                </div>

                <div style={{ fontSize: "0.8rem", color: "#6c757d" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                    <span><strong>Current NDVI:</strong> 0.70 (Excellent)</span>
                    <span><strong>Trend:</strong> ↗️ +16.7%</span>
                  </div>
                  <div>
                    <strong>Forecast:</strong> Continued growth expected
                  </div>
                </div>
              </div>

              {/* Spectral Profile - Bottom Half */}
              <div style={{
                background: "#f8f9fa",
                borderRadius: "8px",
                padding: "1rem",
                border: "1px solid #e9ecef",
                height: "48%"
              }}>
                <h4 style={{ marginBottom: "1rem", color: "#495057", fontSize: "0.9rem" }}>🌈 Spectral Profile</h4>
                <div style={{
                  background: "white",
                  borderRadius: "6px",
                  padding: "0.75rem",
                  marginBottom: "1rem",
                  border: "1px solid #dee2e6",
                  height: "60%"
                }}>
                  <canvas
                    width="400"
                    height="180"
                    style={{
                      width: "100%",
                      height: "100%",
                      background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                      borderRadius: "4px"
                    }}
                    ref={(canvas) => {
                      if (canvas) {
                        const ctx = canvas.getContext('2d');
                        if (ctx) {
                          // Clear canvas
                          ctx.clearRect(0, 0, canvas.width, canvas.height);

                          // Spectral bands data
                          const bands = ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'];
                          const values = [0.045, 0.067, 0.089, 0.456, 0.234, 0.123];
                          const colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#34495e'];

                          // Draw bars
                          const barWidth = canvas.width / bands.length - 15;
                          const maxValue = Math.max(...values);

                          values.forEach((value, index) => {
                            const barHeight = (value / maxValue) * (canvas.height - 50);
                            const x = index * (barWidth + 15) + 10;
                            const y = canvas.height - barHeight - 25;

                            ctx.fillStyle = colors[index];
                            ctx.fillRect(x, y, barWidth, barHeight);

                            // Labels
                            ctx.fillStyle = '#2c3e50';
                            ctx.font = '11px Arial';
                            ctx.textAlign = 'center';
                            ctx.fillText(bands[index], x + barWidth/2, canvas.height - 8);
                            ctx.fillText(value.toFixed(3), x + barWidth/2, y - 8);
                          });
                        }
                      }
                    }}
                  />
                </div>

                <div style={{ fontSize: "0.8rem", color: "#6c757d" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                    <span><strong>NIR/Red:</strong> 5.12</span>
                    <span><strong>Chlorophyll:</strong> High</span>
                  </div>
                  <div>
                    <strong>Water Content:</strong> Moderate SWIR response
                  </div>
                </div>
              </div>
            </div>
            <div className="dashboard-card-footer">
              <div>
                <span>Data Source: Sentinel-2 (10m resolution)</span>
                <span style={{
                  marginLeft: '1rem',
                  fontWeight: '500',
                  color: '#22C55E'
                }}>
                  Cloud Coverage: &lt; 5%
                </span>
              </div>
              <div className="card-actions-footer">
                <button className="action-button">Full Screen</button>
                <button className="action-button">Export Charts</button>
              </div>
            </div>
          </div>

          {/* Analysis Controls Box - Right 50% */}
          <div className="dashboard-card" style={{ overflow: "hidden" }}>
            <div className="dashboard-card-header">
              <h3 className="dashboard-card-title">
                <span>🛰️ Analysis Controls</span>
              </h3>
              <div className="card-actions">
                <span style={{ cursor: 'pointer', fontSize: '1.1rem', opacity: '0.7' }} title="Settings">⚙️</span>
              </div>
            </div>
            <div className="dashboard-card-body" style={{ height: "calc(100% - 120px)", overflowY: "auto", padding: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Satellite Configuration Section */}
              <div style={{
                background: "#f8f9fa",
                borderRadius: "8px",
                padding: "1rem",
                border: "1px solid #e9ecef"
              }}>
                <h4 style={{ marginBottom: "1rem", color: "#495057", fontSize: "0.9rem", fontWeight: "600" }}>🛰️ Satellite Configuration</h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      📡 Data Source:
                    </label>
                    <select style={{
                      width: "100%",
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }}>
                      <option value="sentinel2">Sentinel-2 (10m)</option>
                      <option value="landsat8">Landsat 8 (30m)</option>
                      <option value="modis">MODIS (250m)</option>
                      <option value="planetscope">PlanetScope (3m)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      ☁️ Cloud Coverage:
                    </label>
                    <select style={{
                      width: "100%",
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }}>
                      <option value="5">&lt; 5% (Excellent)</option>
                      <option value="10">&lt; 10% (Very Good)</option>
                      <option value="20">&lt; 20% (Good)</option>
                      <option value="30">&lt; 30% (Acceptable)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                    📅 Analysis Period:
                  </label>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                    <input type="date" style={{
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }} />
                    <input type="date" style={{
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }} />
                  </div>
                </div>
              </div>

              {/* Analysis Parameters Section */}
              <div style={{
                background: "#f8f9fa",
                borderRadius: "8px",
                padding: "1rem",
                border: "1px solid #e9ecef"
              }}>
                <h4 style={{ marginBottom: "1rem", color: "#495057", fontSize: "0.9rem", fontWeight: "600" }}>📊 Analysis Parameters</h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      🎯 Resolution:
                    </label>
                    <select style={{
                      width: "100%",
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }}>
                      <option value="10m">10m (High Detail)</option>
                      <option value="20m">20m (Standard)</option>
                      <option value="30m">30m (Regional)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      🌍 Area Coverage:
                    </label>
                    <select style={{
                      width: "100%",
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }}>
                      <option value="field">Single Field</option>
                      <option value="farm">Entire Farm</option>
                      <option value="region">Regional Analysis</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      📈 Indices to Calculate:
                    </label>
                    <div style={{
                      background: "white",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      padding: "8px",
                      fontSize: "0.8rem",
                      color: "#333"
                    }}>
                      <div style={{ marginBottom: "3px", color: "#333" }}>✅ NDVI (Crop Health)</div>
                      <div style={{ marginBottom: "3px", color: "#333" }}>✅ EVI (Enhanced Vegetation)</div>
                      <div style={{ marginBottom: "3px", color: "#333" }}>✅ SAVI (Soil-Adjusted)</div>
                      <div style={{ color: "#333" }}>✅ NDMI (Moisture Index)</div>
                    </div>
                  </div>

                  <div>
                    <label style={{ display: "block", fontWeight: "600", marginBottom: "5px", color: "#555", fontSize: "0.85rem" }}>
                      ⚡ Processing Priority:
                    </label>
                    <select style={{
                      width: "100%",
                      padding: "10px",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.9rem",
                      background: "white",
                      color: "#333"
                    }}>
                      <option value="high">High (Real-time)</option>
                      <option value="normal">Normal (5-10 min)</option>
                      <option value="low">Low (Background)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Action Buttons Section */}
              <div style={{
                background: "#f8f9fa",
                borderRadius: "8px",
                padding: "1rem",
                border: "1px solid #e9ecef"
              }}>
                <h4 style={{ marginBottom: "1rem", color: "#495057", fontSize: "0.9rem", fontWeight: "600" }}>🚀 Actions</h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", marginBottom: "1rem" }}>
                  <button style={{
                    background: "linear-gradient(135deg, #27ae60, #2ecc71)",
                    color: "white",
                    border: "none",
                    padding: "12px 16px",
                    borderRadius: "6px",
                    fontSize: "0.9rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    boxShadow: "0 2px 4px rgba(39, 174, 96, 0.2)"
                  }}>
                    📊 Generate Report
                  </button>

                  <button style={{
                    background: "linear-gradient(135deg, #3498db, #2980b9)",
                    color: "white",
                    border: "none",
                    padding: "12px 16px",
                    borderRadius: "6px",
                    fontSize: "0.9rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    boxShadow: "0 2px 4px rgba(52, 152, 219, 0.2)"
                  }}>
                    💾 Export Data
                  </button>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem" }}>
                  <button style={{
                    background: "linear-gradient(135deg, #f39c12, #e67e22)",
                    color: "white",
                    border: "none",
                    padding: "12px 16px",
                    borderRadius: "6px",
                    fontSize: "0.9rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    boxShadow: "0 2px 4px rgba(243, 156, 18, 0.2)"
                  }}>
                    📋 Save Template
                  </button>

                  <button style={{
                    background: "linear-gradient(135deg, #9b59b6, #8e44ad)",
                    color: "white",
                    border: "none",
                    padding: "12px 16px",
                    borderRadius: "6px",
                    fontSize: "0.9rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    boxShadow: "0 2px 4px rgba(155, 89, 182, 0.2)"
                  }}>
                    🔄 Auto-Schedule
                  </button>
                </div>
              </div>
            </div>
            <div className="dashboard-card-footer">
              <span>Last Analysis: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        {/* Agent Status Card - Full Width Below */}
        <div style={{ gridColumn: "1 / -1" }}>
          <section className="agents-panel dashboard-card" style={{ height: "600px", overflow: "hidden" }}>
            <div className="dashboard-card-header">
              <h3 className="dashboard-card-title">
                <span>Agent Status ({mergedAgents.length})</span>
                {activeAgentCount > 0 && (
                  <span className="active-count"> • {activeAgentCount} Active</span>
                )}
              </h3>
              <div className="card-actions">
                <span style={{ cursor: 'pointer', fontSize: '0.9rem', opacity: '0.7' }} title="Filter Agents">🔍</span>
              </div>
            </div>
            <div className="dashboard-card-body" style={{ height: "calc(100% - 120px)", overflowY: "auto" }}>
              <AgentList 
                agents={mergedAgents} 
                onAgentClick={handleAgentClick}
              />
            </div>
            <div className="dashboard-card-footer">
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </section>
        </div>

        {lastMessage && (
          <section className="last-message-panel">
            <h2>WebSocket Debug</h2>
            <div className="last-message">
              <h4>Last Message:</h4>
              <pre>{JSON.stringify(lastMessage, null, 2)}</pre>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default DashboardPage;
