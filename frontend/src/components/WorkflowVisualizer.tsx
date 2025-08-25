import React from 'react';
import './WorkflowVisualizer.css';

// Type definitions for workflow data
export interface WorkflowStep {
  id: string;
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed' | 'skipped';
  startTime?: string;
  endTime?: string;
  duration?: number;
  output?: string;
  error?: string;
  agent?: string;
}

export interface Workflow {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  steps: WorkflowStep[];
  startTime?: string;
  endTime?: string;
  totalDuration?: number;
  progress: number; // 0 to 1
  isIncreasing?: boolean; // Flag to indicate if progress is increasing
  metadata?: {
    [key: string]: any;
  };
}

interface WorkflowVisualizerProps {
  workflow: Workflow | null;
  onStepClick?: (step: WorkflowStep) => void;
  showDetails?: boolean;
}

const WorkflowVisualizer: React.FC<WorkflowVisualizerProps> = ({ 
  workflow, 
  onStepClick, 
  showDetails = true 
}) => {
  const getStepIcon = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'in-progress':
        return '🔄';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'skipped':
        return '⏭️';
      default:
        return '❓';
    }
  };

  const getWorkflowIcon = (status: Workflow['status']) => {
    switch (status) {
      case 'pending':
        return '⏸️';
      case 'running':
        return '▶️';
      case 'completed':
        return '🏁';
      case 'failed':
        return '💥';
      case 'cancelled':
        return '🛑';
      default:
        return '❓';
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return 'N/A';
    
    if (duration < 1000) return `${duration}ms`;
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`;
    
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const formatTime = (timeString?: string) => {
    if (!timeString) return 'N/A';
    
    try {
      const time = new Date(timeString);
      return time.toLocaleTimeString();
    } catch {
      return 'Invalid time';
    }
  };

  const calculateStepProgress = (step: WorkflowStep) => {
    if (step.status === 'completed') return 100;
    if (step.status === 'failed') return 100;
    if (step.status === 'in-progress') return 50;
    return 0;
  };

  if (!workflow) {
    return (
      <div className="workflow-visualizer">
        <div className="no-workflow">
          <div className="no-workflow-icon">🔄</div>
          <h3>No Active Workflow</h3>
          <p>Start a workflow to see the execution visualization here.</p>
        </div>
      </div>
    );
  }

  const completedSteps = workflow.steps.filter(step => step.status === 'completed').length;
  const totalSteps = workflow.steps.length;
  const progressPercentage = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div className="workflow-visualizer">
      {/* Workflow Header */}
      <div className="workflow-header">
        <div className="workflow-info">
          <div className="workflow-title">
            <span className="workflow-icon">{getWorkflowIcon(workflow.status)}</span>
            <h3>{workflow.name}</h3>
            <span className={`workflow-status ${workflow.status}`}>
              {workflow.status.toUpperCase()}
            </span>
          </div>
          <div className="workflow-id">ID: {workflow.id}</div>
        </div>
        
        {/* Progress Bar */}
        <div className="workflow-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <div className="progress-text">
            {completedSteps}/{totalSteps} steps ({Math.round(progressPercentage)}%)
            {workflow.isIncreasing && workflow.status === 'running' && (
              <span className="increasing-label" style={{ marginLeft: '8px', color: '#2db782', fontSize: '0.8em', fontWeight: 'bold' }}>
                ↑ Increasing
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Workflow Details */}
      {showDetails && (
        <div className="workflow-details">
          <div className="detail-item">
            <span className="detail-label">Started:</span>
            <span className="detail-value">{formatTime(workflow.startTime)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Duration:</span>
            <span className="detail-value">{formatDuration(workflow.totalDuration)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Progress:</span>
            <span className="detail-value">
              {Math.round(workflow.progress * 100)}%
              {workflow.isIncreasing && workflow.status === 'running' && (
                <span style={{ marginLeft: '5px', color: '#2db782', fontWeight: 'bold' }}>↑</span>
              )}
            </span>
          </div>
        </div>
      )}

      {/* Removed Execution Steps section as it's now in a separate card */}
    </div>
  );
};

export default WorkflowVisualizer;
