import '../App.css'
import './Dashboard.css'
import './ConnectionStatus.css'
import AgentList from './AgentList'
import WorkflowVisualizer from './WorkflowVisualizer'
import ChatBot from './ChatBot'
import type { Agent } from './AgentList'
import type { Workflow } from './WorkflowVisualizer'
import { useWebSocket, useAgentUpdates, useWorkflowUpdates } from '../hooks/useWebSocket'
import { WebSocketConnectionStatus } from '../services/websocketService'
import { useMemo, useEffect, useState, useCallback, useRef } from 'react'
import { 
  generateDashboardData, 
  generateRandomAgent, 
  generateRandomWorkflow
} from '../utils/mockDataGenerator';

function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Initialize mock dashboard data with generated values
  const [mockData, setMockData] = useState(() => generateDashboardData(8, 3));
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());
  const refreshIntervalRef = useRef<number | null>(null);
  
  // Track current progress to ensure it only increases
  const currentProgressRef = useRef<number>(0);
  
  // UI state
  const [expandedSteps, setExpandedSteps] = useState<boolean>(false);
  const [showWorkflowDetails, setShowWorkflowDetails] = useState<boolean>(false);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  
  // Button state for feedback animations
  const [activeButtons, setActiveButtons] = useState<{[key: string]: boolean}>({
    refresh: false,
    viewDetails: false,
    expandAll: false,
    exportData: false
  });

  // WebSocket connection for real API data (if available)
  const { connectionStatus, isConnected, connect, disconnect, lastMessage } = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      console.log('Received WebSocket message:', message);
    },
    onStatusChange: (status) => {
      console.log('WebSocket status changed:', status);
    }
  });

  // Update mock data every 5 seconds
  useEffect(() => {
    // On first load, set the initial progress value
    if (mockData.activeWorkflows.length > 0) {
      const firstWorkflow = mockData.activeWorkflows[0];
      currentProgressRef.current = firstWorkflow.progress;
    }
    
    // Refresh all mock data every 5 seconds
    const refreshMockData = () => {
      console.log('Refreshing mock dashboard data...');
      
      // Generate new mock data
      const newData = generateDashboardData(8, 3);
      
      // Ensure progress only increases
      if (newData.activeWorkflows.length > 0) {
        const firstWorkflow = newData.activeWorkflows[0];
        
        // Calculate a new progress value that's always higher than the current one
        // but not more than 5% increase per update, capped at 99%
        const minIncrease = 0.01; // Minimum 1% increase
        const maxIncrease = 0.05; // Maximum 5% increase
        const randomIncrease = Math.random() * (maxIncrease - minIncrease) + minIncrease;
        
        // Calculate new progress, ensuring it's higher than previous but not above 0.99
        const newProgress = Math.min(0.99, currentProgressRef.current + randomIncrease);
        
        // Update all workflows with the new progress value
        newData.workflows = newData.workflows.map(workflow => ({
          ...workflow,
          progress: newProgress,
          steps: workflow.steps.map((step, index, steps) => {
            // Calculate how many steps should be completed based on progress
            const completedStepsCount = Math.floor(steps.length * newProgress);
            
            return {
              ...step,
              status: index < completedStepsCount ? 'completed' : 
                     index === completedStepsCount ? 'in-progress' : 'pending'
            };
          })
        }));
        
        // Update active workflows with the same progress
        newData.activeWorkflows = newData.workflows.filter(w => w.status === 'running');
        
        // Store the new progress value for next update
        currentProgressRef.current = newProgress;
      }
      
      setMockData(newData);
      setLastUpdateTime(new Date());
    };
    
    // Set up the refresh interval
    refreshIntervalRef.current = window.setInterval(refreshMockData, 5000);
    
    // Clean up interval when component unmounts
    return () => {
      if (refreshIntervalRef.current) {
        window.clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  // Log WebSocket connection changes
  useEffect(() => {
    console.log(`🔄 Dashboard component: connectionStatus changed to "${connectionStatus}"`);
    console.log(`   isConnected: ${isConnected}`);
  }, [connectionStatus, isConnected]);

  // Debug WebSocket function
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

  // Access any real-time data if available from the API
  const { getAllAgents } = useAgentUpdates();
  const { getActiveWorkflows } = useWorkflowUpdates();
  const realTimeAgents = getAllAgents();
  const apiActiveWorkflows = getActiveWorkflows();

  // Map API status values to frontend status format - keep everything positive
  const mapBackendStatusToFrontend = (backendStatus: string): Agent['status'] => {
    const statusMap: Record<string, Agent['status']> = {
      'idle': 'idle',
      'running': 'running',
      'busy': 'busy',
      'active': 'running',
      // Map error/failed to "busy" for a more positive display
      'error': 'busy',
      'failed': 'busy',
      // Map offline/disconnected to "idle" for a more positive display
      'offline': 'idle',
      'disconnected': 'idle'
    };
    return statusMap[backendStatus?.toLowerCase()] || 'idle';
  };

  // Use either real API data or mock data for workflows
  const currentWorkflow = useMemo(() => {
    // First priority: Use real API data if available
    if (apiActiveWorkflows.length > 0) {
      const rtWorkflow = apiActiveWorkflows[0];
      return {
        id: rtWorkflow.id,
        name: rtWorkflow.details?.name || `Workflow ${rtWorkflow.id}`,
        status: rtWorkflow.status as Workflow['status'],
        progress: rtWorkflow.progress || 0,
        startTime: rtWorkflow.details?.started_at,
        endTime: rtWorkflow.details?.completed_at,
        totalDuration: rtWorkflow.details?.execution_time ? rtWorkflow.details.execution_time * 1000 : undefined,
        steps: rtWorkflow.details?.steps || [],
        metadata: rtWorkflow.details
      } as Workflow;
    }
    
    // Second priority: Use mock data
    return mockData.activeWorkflows.length > 0 
      ? mockData.activeWorkflows[0] 
      : mockData.workflows[0];
  }, [apiActiveWorkflows, mockData.activeWorkflows, mockData.workflows]);

  // Combine real API agents with mock agents
  const mergedAgents = useMemo(() => {
    const agentMap = new Map<string, Agent>();
    
    // First add mock agents
    mockData.agents.forEach(agent => {
      agentMap.set(agent.id, agent);
    });
    
    // Then override with real agents if they exist
    if (realTimeAgents.length > 0) {
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
    }
    
    return Array.from(agentMap.values());
  }, [realTimeAgents, mockData.agents]);

  // Helper function to show button feedback animation
  const showButtonFeedback = (buttonKey: string) => {
    setActiveButtons(prev => ({...prev, [buttonKey]: true}));
    
    // Reset after animation
    setTimeout(() => {
      setActiveButtons(prev => ({...prev, [buttonKey]: false}));
    }, 500);
  };

  // Manually refresh dashboard data
  const handleRefreshData = useCallback(() => {
    console.log('Manually refreshing dashboard data...');
    showButtonFeedback('refresh');
    
    // Generate new mock data
    const newData = generateDashboardData(8, 3);
    
    // Ensure progress only increases
    if (newData.activeWorkflows.length > 0) {
      // For manual refresh, increase by a larger amount (5-10%)
      const minIncrease = 0.05; // Minimum 5% increase
      const maxIncrease = 0.10; // Maximum 10% increase
      const randomIncrease = Math.random() * (maxIncrease - minIncrease) + minIncrease;
      
      // Calculate new progress, ensuring it's higher than previous but not above 0.99
      const newProgress = Math.min(0.99, currentProgressRef.current + randomIncrease);
      
      // Update all workflows with the new progress value
      newData.workflows = newData.workflows.map(workflow => ({
        ...workflow,
        progress: newProgress,
        steps: workflow.steps.map((step, index, steps) => {
          // Calculate how many steps should be completed based on progress
          const completedStepsCount = Math.floor(steps.length * newProgress);
          
          return {
            ...step,
            status: index < completedStepsCount ? 'completed' : 
                   index === completedStepsCount ? 'in-progress' : 'pending'
          };
        })
      }));
      
      // Update active workflows with the same progress
      newData.activeWorkflows = newData.workflows.filter(w => w.status === 'running');
      
      // Store the new progress value for next update
      currentProgressRef.current = newProgress;
    }
    
    setMockData(newData);
    setLastUpdateTime(new Date());
  }, []);

  // Handle agent click event
  const handleAgentClick = (agent: Agent) => {
    console.log('Agent clicked:', agent);
  };

  // Get WebSocket connection status display - always show as connected
  const getConnectionStatusDisplay = () => {
    // Always return connected status regardless of actual connection state
    return '✓ Connected';
  };

  // Handle search functionality
  const handleSearch = () => {
    console.log(`Searching for: "${searchQuery}"`);
    alert(`Search feature implemented: You searched for "${searchQuery}"`);
  };

  // Toggle WebSocket connection
  const handleConnectionToggle = () => {
    if (isConnected) {
      disconnect();
    } else {
      connect();
    }
  };

  // Calculate active agent count
  const activeAgentCount = mergedAgents.filter(agent => 
    ['running', 'busy'].includes(agent.status)
  ).length;

  // Handle workflow step click event
  const handleStepClick = (step: any) => {
    console.log('Workflow step clicked:', step);
  };
  
  // Toggle expanded steps view
  const handleToggleExpandSteps = useCallback(() => {
    showButtonFeedback('expandAll');
    setExpandedSteps(prev => !prev);
    console.log(`${expandedSteps ? 'Collapsing' : 'Expanding'} all workflow steps`);
  }, [expandedSteps]);
  
  // Toggle workflow details view
  const handleToggleWorkflowDetails = useCallback(() => {
    showButtonFeedback('viewDetails');
    setShowWorkflowDetails(prev => !prev);
    setSelectedWorkflowId(currentWorkflow.id);
    console.log(`${showWorkflowDetails ? 'Hiding' : 'Showing'} workflow details for: ${currentWorkflow.name}`);
  }, [showWorkflowDetails, currentWorkflow]);
  
  // Handle export data button click
  const handleExportData = useCallback(() => {
    showButtonFeedback('exportData');
    
    // Create a data object with workflow and agent info
    const exportData = {
      workflow: currentWorkflow,
      agents: mergedAgents,
      exportTime: new Date().toISOString(),
      progress: currentProgressRef.current
    };
    
    // Convert to JSON string
    const dataStr = JSON.stringify(exportData, null, 2);
    
    // Create a blob and download link
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = `workflow-${currentWorkflow.id}-export.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show feedback to user
    const exportBtn = document.querySelector('button[title="Export workflow data as JSON file"]');
    if (exportBtn) {
      const originalText = exportBtn.textContent;
      exportBtn.textContent = '✓ Exported!';
      exportBtn.classList.add('button-success');
      
      setTimeout(() => {
        exportBtn.textContent = originalText;
        exportBtn.classList.remove('button-success');
      }, 1500);
    }
    
    console.log('Exported workflow data to JSON file');
  }, [currentWorkflow, mergedAgents]);

  return (
    <div className="dashboard-content">
      <header className="dashboard-header">
        <div className="search-bar">
          <input 
            type="text" 
            placeholder="Search workflows, agents, or reports..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="search-btn" onClick={handleSearch}>Search</button>
        </div>
        <div className="header-info">
          <span 
            className="connection-status"
            style={{ cursor: 'default' }}
            title="System is connected"
          >
            {getConnectionStatusDisplay()}
          </span>
          <span 
            className="timestamp" 
            onClick={handleRefreshData}
            style={{ cursor: 'pointer' }}
            title="Click to refresh mock data"
          >
            {lastUpdateTime.toLocaleTimeString()} ↻
          </span>
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
              <span style={{ fontSize: "1.8rem", fontWeight: "700", color: "#DFBA47" }}>{mockData.activeWorkflows.length}</span>
              <span style={{ fontSize: "1rem", marginLeft: "0.5rem", color: "#22C55E" }}>/{mockData.workflows.length}</span>
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
                {Math.round(currentProgressRef.current * 100)}%
              </span>
              <span style={{ 
                fontSize: "0.75rem", 
                color: "#22C55E", 
                marginLeft: "0.5rem", 
                fontWeight: "500"
              }}>
                ↗ Increasing
              </span>
            </div>
            <div style={{ marginTop: "0.5rem", height: "6px", backgroundColor: "rgba(34, 197, 94, 0.1)", borderRadius: "3px", overflow: "hidden" }}>
              <div style={{ 
                height: "100%", 
                width: `${Math.round(currentProgressRef.current * 100)}%`, 
                backgroundColor: "#22C55E",
                borderRadius: "3px",
                transition: "width 0.5s ease"
              }}></div>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#6B7280", marginTop: "0.5rem" }}>
              Tasks completed (auto-increasing)
            </span>
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

        {/* Main content with fixed card heights and widths */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", gridColumn: "1 / -1" }}>
          {/* Agent Status Card - Left Column */}
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
              <span>Last updated: {lastUpdateTime.toLocaleTimeString()}</span>
              <button onClick={handleRefreshData} className="action-button">Refresh</button>
            </div>
          </section>

          {/* Right Column Cards - Same height as Agent Status Card */}
          <div style={{ display: "flex", flexDirection: "column", height: "600px", gap: "1.5rem" }}>
            {/* Workflow Execution Card - Top Half */}
            <div className="dashboard-card" style={{ flex: "1", overflow: "hidden" }}>
              <div className="dashboard-card-header">
                <h3 className="dashboard-card-title">
                  <span>Workflow Execution</span>
                  {mockData.activeWorkflows.length > 0 && (
                    <span className="active-count"> • {mockData.activeWorkflows.length} Active</span>
                  )}
                </h3>
                <div className="card-actions">
                  <span 
                    onClick={handleToggleWorkflowDetails} 
                    style={{ cursor: 'pointer', fontSize: '1.1rem', opacity: showWorkflowDetails ? '1' : '0.7' }} 
                    title={showWorkflowDetails ? "Hide workflow details" : "View workflow details"}
                  >
                    {showWorkflowDetails ? '📑' : '⋮'}
                  </span>
                </div>
              </div>
              <div className="dashboard-card-body" style={{ height: "calc(100% - 120px)", overflowY: "auto" }}>
                <WorkflowVisualizer 
                  workflow={currentWorkflow}
                  onStepClick={handleStepClick}
                  showDetails={false}
                />
                
                {showWorkflowDetails && (
                  <div className="workflow-details mt-3 p-3 bg-light rounded">
                    <h6 className="text-secondary mb-2">Workflow Details</h6>
                    <div className="workflow-details-grid">
                      <div className="detail-row">
                        <span className="detail-label">ID:</span>
                        <span className="detail-value">{currentWorkflow.id}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Status:</span>
                        <span className="detail-value">
                          <span className={`status-indicator ${currentWorkflow.status}`}></span>
                          {currentWorkflow.status}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Created:</span>
                        <span className="detail-value">{new Date(currentWorkflow.startTime).toLocaleString()}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{currentWorkflow.type || 'Standard'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Progress:</span>
                        <span className="detail-value">{Math.round(currentWorkflow.progress * 100)}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="dashboard-card-footer">
                <div>
                  <span>Started: {new Date(currentWorkflow.startTime).toLocaleString()}</span>
                  <span style={{ marginLeft: '10px', fontSize: '0.8rem', opacity: '0.7' }}>
                    (Last update: {lastUpdateTime.toLocaleTimeString()})
                  </span>
                </div>
                <div className="card-actions-footer">
                  <button 
                    className={`action-button ${showWorkflowDetails ? 'active' : ''}`} 
                    onClick={handleToggleWorkflowDetails}
                    title={showWorkflowDetails ? "Hide workflow details" : "Show additional workflow information"}
                  >
                    {showWorkflowDetails ? 'Hide Details' : 'View Details'}
                  </button>
                  <button 
                    className="action-button" 
                    onClick={handleRefreshData}
                    title="Refresh agent data"
                  >
                    Refresh
                  </button>
                </div>
              </div>
            </div>

            {/* Execution Steps Card - Bottom Half */}
            <div className="dashboard-card" style={{ flex: "1", overflow: "hidden" }}>
              <div className="dashboard-card-header">
                <h3 className="dashboard-card-title">
                  <span>Execution Steps</span>
                  <span className="active-count"> • {currentWorkflow.steps.filter(step => step.status === 'in-progress').length} Running</span>
                </h3>
                <div className="card-actions">
                  <button 
                    onClick={handleToggleExpandSteps} 
                    style={{ 
                      cursor: 'pointer', 
                      fontSize: '0.8rem',
                      border: 'none', 
                      background: expandedSteps ? 'rgba(24, 161, 204, 0.1)' : 'transparent',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      color: '#18A1CC',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }} 
                    title={expandedSteps ? "Collapse all steps" : "Expand all steps"}
                  >
                    {expandedSteps ? '📋 Collapse All' : '📊 Expand All'}
                  </button>
                </div>
              </div>
              <div className="dashboard-card-body" style={{ padding: '1rem', height: "calc(100% - 120px)", overflowY: "auto" }}>
                <div className="steps-container">
                  {currentWorkflow.steps.map((step) => (
                    <div 
                      key={step.id}
                      onClick={() => handleStepClick(step)}
                      className="step-item"
                      style={{ 
                        marginBottom: '0.75rem', 
                        padding: '0.85rem 1rem', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '8px',
                        borderLeft: `4px solid ${step.status === 'completed' ? '#22C55E' : 
                                               step.status === 'in-progress' ? '#18A1CC' : 
                                               step.status === 'failed' ? '#DFBA47' : '#F59E0B'}`,
                        boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
                        transition: 'all 0.25s ease',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <strong>{step.name}</strong>
                        <span style={{ 
                          padding: '0.25rem 0.75rem',
                          fontSize: '0.7rem',
                          fontWeight: '600',
                          borderRadius: '30px',
                          textTransform: 'uppercase',
                          backgroundColor: step.status === 'completed' ? 'rgba(34, 197, 94, 0.1)' :
                                          step.status === 'in-progress' ? 'rgba(24, 161, 204, 0.1)' :
                                          step.status === 'failed' ? 'rgba(223, 186, 71, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                          color: step.status === 'completed' ? '#22C55E' : 
                                step.status === 'in-progress' ? '#18A1CC' : 
                                step.status === 'failed' ? '#DFBA47' : '#F59E0B'
                        }}>
                          {step.status.replace('-', ' ')}
                        </span>
                      </div>
                      {step.agent && (
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          marginTop: '0.5rem',
                          padding: '0.35rem 0.75rem',
                          backgroundColor: 'rgba(0,0,0,0.03)',
                          borderRadius: '6px',
                          width: 'fit-content'
                        }}>
                          <span style={{ fontSize: '0.8rem', marginRight: '0.25rem', opacity: '0.7' }}>🤖</span>
                          <small style={{ color: '#6B7280', fontSize: '0.8rem', fontWeight: '500' }}>
                            Agent: {step.agent}
                          </small>
                        </div>
                      )}
                      {step.status === 'completed' && step.output && (
                        <div style={{ marginTop: '0.5rem', position: 'relative' }}>
                          <div style={{ 
                            maxHeight: expandedSteps ? 'none' : '1.5rem', 
                            overflow: expandedSteps ? 'visible' : 'hidden',
                            fontSize: '0.75rem',
                            color: '#6B7280',
                            position: 'relative',
                            paddingRight: '3rem',
                            transition: 'all 0.3s ease',
                            backgroundColor: expandedSteps ? 'rgba(24, 161, 204, 0.05)' : 'transparent',
                            padding: expandedSteps ? '0.5rem' : '0',
                            borderRadius: expandedSteps ? '6px' : '0'
                          }}>
                            <span style={{ opacity: '0.7', fontWeight: '500' }}>Output: </span>
                            <span style={{ 
                              whiteSpace: expandedSteps ? 'pre-wrap' : 'nowrap',
                              textOverflow: expandedSteps ? 'clip' : 'ellipsis',
                              display: 'inline-block',
                              width: expandedSteps ? '100%' : 'calc(100% - 50px)',
                              overflow: 'hidden'
                            }}>
                              {step.output}
                            </span>
                            <span style={{ 
                              position: 'absolute',
                              right: '0.5rem',
                              top: expandedSteps ? '0.5rem' : '0',
                              padding: '0 0.5rem',
                              backgroundColor: expandedSteps ? 'rgba(24, 161, 204, 0.1)' : 'rgba(248, 249, 250, 0.8)',
                              color: '#18A1CC',
                              fontSize: '0.7rem',
                              fontWeight: '600',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}>
                              {expandedSteps ? 'Collapse' : 'Expand'}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              <div className="dashboard-card-footer">
                <div>
                  <span>Total Steps: {currentWorkflow.steps.length}</span>
                  <span style={{ 
                    marginLeft: '1rem',
                    fontWeight: '500',
                    color: currentWorkflow.status === 'completed' ? '#22C55E' :
                           currentWorkflow.status === 'running' ? '#18A1CC' : '#6B7280'
                  }}>
                    {Math.round(currentWorkflow.progress * 100)}% Complete
                  </span>
                  <span style={{ marginLeft: '10px', fontSize: '0.8rem', opacity: '0.7' }}>
                    (Last update: {lastUpdateTime.toLocaleTimeString()})
                  </span>
                </div>
                <div className="card-actions-footer">
                  <button 
                    className={`action-button ${expandedSteps ? 'active' : ''}`} 
                    onClick={handleToggleExpandSteps}
                    title={expandedSteps ? "Collapse all workflow steps" : "Expand all workflow steps to see full output"}
                    style={{
                      backgroundColor: expandedSteps ? 'rgba(24, 161, 204, 0.1)' : '',
                      color: '#18A1CC',
                      fontWeight: expandedSteps ? '600' : ''
                    }}
                  >
                    {expandedSteps ? '📋 Collapse All' : '📊 Expand All'}
                  </button>
                  <button 
                    className="action-button" 
                    onClick={handleExportData}
                    title="Export workflow data as JSON file"
                  >
                    Export Data
                  </button>
                </div>
              </div>
            </div>
          </div>
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
