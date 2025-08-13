import React from 'react';
import './AgentList.css';

// Type definitions for agent data
export interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'busy' | 'error' | 'offline';
  lastActivity?: string;
  currentTask?: string;
  metrics?: {
    tasksCompleted: number;
    averageExecutionTime: number;
    successRate: number;
  };
}

interface AgentListProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
}

const AgentList: React.FC<AgentListProps> = ({ agents, onAgentClick }) => {
  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'idle':
        return '🟡';
      case 'running':
        return '🟢';
      case 'busy':
        return '🔵';
      case 'error':
        return '🔴';
      case 'offline':
        return '⚫';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'idle':
        return '#ffd60a';
      case 'running':
        return '#06ffa5';
      case 'busy':
        return '#0066ff';
      case 'error':
        return '#ff4757';
      case 'offline':
        return '#747d8c';
      default:
        return '#cccccc';
    }
  };

  const formatLastActivity = (lastActivity?: string) => {
    if (!lastActivity) return 'Never';
    
    const now = new Date();
    const activityTime = new Date(lastActivity);
    const diffMs = now.getTime() - activityTime.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  if (agents.length === 0) {
    return (
      <div className="agent-list">
        <div className="agent-list-empty">
          <p>No agents available</p>
          <span className="empty-icon">🤖</span>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-list">
      {agents.map((agent) => (
        <div
          key={agent.id}
          className={`agent-item ${agent.status}`}
          onClick={() => onAgentClick?.(agent)}
          style={{ cursor: onAgentClick ? 'pointer' : 'default' }}
        >
          {/* Agent Header */}
          <div className="agent-header">
            <div className="agent-info">
              <span className="agent-id">{agent.id}</span>
              <span className="agent-name">{agent.name}</span>
            </div>
            <div className="agent-status-badge">
              <span className="status-icon">{getStatusIcon(agent.status)}</span>
              <span 
                className="status-text"
                style={{ color: getStatusColor(agent.status) }}
              >
                {agent.status.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Agent Details */}
          <div className="agent-details">
            <div className="detail-row">
              <span className="detail-label">Last Activity:</span>
              <span className="detail-value">{formatLastActivity(agent.lastActivity)}</span>
            </div>
            
            {agent.currentTask && (
              <div className="detail-row">
                <span className="detail-label">Current Task:</span>
                <span className="detail-value current-task">{agent.currentTask}</span>
              </div>
            )}
            
            {agent.metrics && (
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-value">{agent.metrics.tasksCompleted}</span>
                  <span className="metric-label">Tasks</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{agent.metrics.averageExecutionTime.toFixed(1)}s</span>
                  <span className="metric-label">Avg Time</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{(agent.metrics.successRate * 100).toFixed(0)}%</span>
                  <span className="metric-label">Success</span>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default AgentList;
