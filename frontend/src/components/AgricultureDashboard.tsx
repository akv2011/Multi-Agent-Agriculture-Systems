import React, { useState, useEffect } from 'react';
import './AgentDashboard.css';

interface AgricultureAgent {
  id: string;
  name: string;
  status: 'available' | 'busy' | 'error' | 'offline' | 'starting' | 'stopping';
  agent_type: string;
  domain: string;
  lastActivity: string;
  currentTask?: string;
  metrics: {
    queriesProcessed: number;
    averageResponseTime: number;
    accuracyRate: number;
    tasksCompleted?: number;
    tasksFailed?: number;
  };
}

interface SystemStats {
  totalQueries: number;
  activeQueries: number;
  completedQueries: number;
  averageResponseTime: number;
  systemUptime: string;
  agentStatusCounts: {
    available: number;
    busy: number;
    starting: number;
    stopping: number;
    error: number;
    offline: number;
  };
}

interface AgricultureDashboardProps {
  className?: string;
}

const AgricultureDashboard: React.FC<AgricultureDashboardProps> = ({ className = '' }) => {
  const [agents, setAgents] = useState<AgricultureAgent[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Mock data for demonstration
  useEffect(() => {
    const mockAgents: AgricultureAgent[] = [
      {
        id: 'crop_selection_agent',
        name: 'Crop Selection Advisor',
        status: 'available',
        agent_type: 'worker',
        domain: 'Crop Selection',
        lastActivity: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        currentTask: 'Analyzing soil conditions for wheat selection',
        metrics: {
          queriesProcessed: 45,
          averageResponseTime: 3.2,
          accuracyRate: 0.92,
          tasksCompleted: 38,
          tasksFailed: 2
        }
      },
      {
        id: 'disease_identification_agent',
        name: 'Disease Identification Specialist',
        status: 'available',
        agent_type: 'worker',
        domain: 'Disease Identification',
        lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        currentTask: 'Processing leaf image analysis',
        metrics: {
          queriesProcessed: 18,
          averageResponseTime: 3.5,
          accuracyRate: 0.93,
          tasksCompleted: 16,
          tasksFailed: 1
        }
      },
      {
        id: 'pest_management_agent',
        name: 'Pest Management Expert',
        status: 'busy',
        agent_type: 'worker',
        domain: 'Pest Management',
        lastActivity: new Date(Date.now() - 1 * 60 * 1000).toISOString(),
        currentTask: 'Processing pest identification request',
        metrics: {
          queriesProcessed: 28,
          averageResponseTime: 4.1,
          accuracyRate: 0.89,
          tasksCompleted: 24,
          tasksFailed: 3
        }
      },
      {
        id: 'irrigation_agent',
        name: 'Irrigation Scheduler',
        status: 'available',
        agent_type: 'worker',
        domain: 'Irrigation',
        lastActivity: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        metrics: {
          queriesProcessed: 33,
          averageResponseTime: 2.8,
          accuracyRate: 0.94,
          tasksCompleted: 31,
          tasksFailed: 1
        }
      },
      {
        id: 'finance_policy_agent',
        name: 'Finance & Policy Advisor',
        status: 'available',
        agent_type: 'worker',
        domain: 'Finance & Policy',
        lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        currentTask: 'Checking loan eligibility criteria',
        metrics: {
          queriesProcessed: 19,
          averageResponseTime: 5.4,
          accuracyRate: 0.96,
          tasksCompleted: 17,
          tasksFailed: 0
        }
      },
      {
        id: 'market_timing_agent',
        name: 'Market Timing Analyst',
        status: 'error',
        agent_type: 'worker',
        domain: 'Market Timing',
        lastActivity: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        currentTask: 'Error: API connection timeout',
        metrics: {
          queriesProcessed: 12,
          averageResponseTime: 6.2,
          accuracyRate: 0.87,
          tasksCompleted: 10,
          tasksFailed: 2
        }
      },
      {
        id: 'harvest_planning_agent',
        name: 'Harvest Planner',
        status: 'available',
        agent_type: 'worker',
        domain: 'Harvest Planning',
        lastActivity: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        metrics: {
          queriesProcessed: 8,
          averageResponseTime: 3.9,
          accuracyRate: 0.91,
          tasksCompleted: 7,
          tasksFailed: 1
        }
      },
      {
        id: 'input_materials_agent',
        name: 'Input Materials Advisor',
        status: 'offline',
        agent_type: 'worker',
        domain: 'Input Materials',
        lastActivity: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        metrics: {
          queriesProcessed: 15,
          averageResponseTime: 4.5,
          accuracyRate: 0.88,
          tasksCompleted: 15,
          tasksFailed: 0
        }
      }
    ];

    const mockStats: SystemStats = {
      totalQueries: 160,
      activeQueries: 3,
      completedQueries: 157,
      averageResponseTime: 4.2,
      systemUptime: '2d 14h 32m',
      agentStatusCounts: {
        available: 4,
        busy: 1,
        starting: 0,
        stopping: 0,
        error: 1,
        offline: 1
      }
    };

    setAgents(mockAgents);
    setSystemStats(mockStats);
    setIsConnected(true);
    setLastUpdate(new Date().toISOString());

    // Simulate real-time updates
    const interval = setInterval(() => {
      setLastUpdate(new Date().toISOString());
      // In a real implementation, this would fetch from the API
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return '🟢';
      case 'busy':
        return '🔵';
      case 'starting':
        return '🟡';
      case 'stopping':
        return '�';
      case 'error':
        return '🔴';
      case 'offline':
        return '⚫';
      default:
        return '⚪';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'agent-card-active';
      case 'busy':
        return 'agent-card-busy';
      case 'starting':
      case 'stopping':
        return 'agent-card-idle';
      case 'error':
        return 'agent-card-error';
      case 'offline':
        return 'agent-card-offline';
      default:
        return 'agent-card-offline';
    }
  };

  const formatLastActivity = (timestamp: string) => {
    const now = new Date();
    const activity = new Date(timestamp);
    const diffMs = now.getTime() - activity.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  if (!systemStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className={`agent-dashboard ${className}`}>
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>Agricultural Advisory System</h2>
          <p>Multi-agent agricultural advisory dashboard</p>
        </div>
        <div className="dashboard-status">
          {isConnected ? (
            <div className="connection-indicator connected">
              <span className="indicator-icon">⚡</span>
              <span className="indicator-text">Connected</span>
            </div>
          ) : (
            <div className="connection-indicator disconnected">
              <span className="indicator-icon">⚠️</span>
              <span className="indicator-text">Disconnected</span>
            </div>
          )}
          <div className="last-update">
            Last update: {formatLastActivity(lastUpdate)}
          </div>
        </div>
      </div>

      {/* System Statistics */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <span>💬</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{systemStats.totalQueries}</div>
            <div className="stat-label">Total Queries</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <span>⏱️</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{systemStats.activeQueries}</div>
            <div className="stat-label">Active Queries</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <span>⚡</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{systemStats.averageResponseTime}s</div>
            <div className="stat-label">Avg Response Time</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <span>🕒</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{systemStats.systemUptime}</div>
            <div className="stat-label">System Uptime</div>
          </div>
        </div>
      </div>

      {/* Agent Status Section */}
      <h3 className="section-title">Agricultural Specialist Agents</h3>
        
      <div className="agent-cards-grid">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-card ${getStatusColor(agent.status)}`}
          >
            <div className="agent-card-header">
              <div className="agent-card-name-container">
                <div className="agent-icon-wrapper">
                  <img 
                    src={`/icons/${agent.id.replace('_agent', '')}-agent.svg`}
                    alt={agent.name}
                    className="agent-icon"
                    onError={(e) => {
                      // Fallback if icon not found
                      e.currentTarget.src = '/icons/crop-selection-agent.svg';
                    }}
                  />
                </div>
                <div>
                  <h4 className="agent-card-name">{agent.name}</h4>
                  <p className="agent-card-domain">{agent.domain}</p>
                </div>
              </div>
              <div className="agent-status-badge">
                <span className={`status-icon status-icon-${agent.status}`}>{getStatusIcon(agent.status)}</span>
                <span className="status-text">{agent.status.toUpperCase()}</span>
              </div>
            </div>

            <div className="agent-card-content">
              {agent.currentTask && (
                <div className="agent-card-task">
                  <div className="agent-card-task-label">Current Task:</div>
                  <div className="agent-card-task-value">{agent.currentTask}</div>
                </div>
              )}

              <div className="agent-card-metrics">
                <div className="agent-metric">
                  <span className="agent-metric-value">{agent.metrics.queriesProcessed}</span>
                  <span className="agent-metric-label">Queries</span>
                </div>
                <div className="agent-metric">
                  <span className="agent-metric-value">{agent.metrics.averageResponseTime}s</span>
                  <span className="agent-metric-label">Avg Time</span>
                </div>
                <div className="agent-metric">
                  <span className="agent-metric-value">{(agent.metrics.accuracyRate * 100).toFixed(0)}%</span>
                  <span className="agent-metric-label">Accuracy</span>
                </div>
              </div>
              {(agent.metrics.tasksCompleted !== undefined || agent.metrics.tasksFailed !== undefined) && (
                <div className="agent-card-tasks">
                  <div className="agent-task-metrics">
                    {agent.metrics.tasksCompleted !== undefined && (
                      <div className="agent-task-metric completed">
                        <span className="agent-task-metric-value">{agent.metrics.tasksCompleted}</span>
                        <span className="agent-task-metric-label">Completed</span>
                      </div>
                    )}
                    {agent.metrics.tasksFailed !== undefined && (
                      <div className="agent-task-metric failed">
                        <span className="agent-task-metric-value">{agent.metrics.tasksFailed}</span>
                        <span className="agent-task-metric-label">Failed</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="agent-card-footer">
              <div className="agent-last-activity">
                Last activity: {formatLastActivity(agent.lastActivity)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3 className="section-title">Quick Actions</h3>
        <div className="action-buttons">
          <button className="action-button">
            <span className="action-icon">🔄</span>
            <span>Restart All Agents</span>
          </button>
          <button className="action-button">
            <span className="action-icon">📊</span>
            <span>View Analytics</span>
          </button>
          <button className="action-button">
            <span className="action-icon">🔍</span>
            <span>System Diagnostics</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgricultureDashboard;
