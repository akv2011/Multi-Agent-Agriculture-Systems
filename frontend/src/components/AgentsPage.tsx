import React, { useState } from 'react';
import './AgentsPage.css';
import './Dashboard.css';

interface AgentMetrics {
  tasksCompleted: number;
  averageExecutionTime: number;
  successRate: number;
  uptime?: number;
  errorRate?: number;
  requestsHandled?: number;
}

interface AgentLogs {
  timestamp: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}

interface VegetationIndices {
  ndvi?: number;
  evi?: number;
  savi?: number;
  ndmi?: number;
  mndwi?: number;
  vari?: number;
  tcari?: number;
  nbr?: number;
  cmr?: number;
}

interface AgentData {
  id: number;
  name: string;
  status: 'active' | 'inactive' | 'maintenance' | 'error';
  description: string;
  type: string;
  lastActive: string;
  performance: number;
  metrics?: AgentMetrics;
  cpu?: number;
  memory?: number;
  version?: string;
  logs?: AgentLogs[];
  connections?: string[];
  dependencies?: string[];
  vegetationIndices?: VegetationIndices;
}

const AgentsPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AgentData | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'logs' | 'connections'>('overview');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Function to get vegetation indices for a specific agent based on analysis results
  const getVegetationIndicesForAgent = (agentName: string): VegetationIndices | undefined => {
    const analysisData = localStorage.getItem('vegetationAnalysis');
    if (!analysisData) return undefined;

    const parsedData = JSON.parse(analysisData);
    if (!parsedData.isAnalyzed || !parsedData.vegetationIndices) {
      return undefined;
    }

    // Return specific indices based on agent type
    if (agentName === 'Crop Selection Agent') {
      return {
        ndvi: parsedData.vegetationIndices.ndvi,
        evi: parsedData.vegetationIndices.evi,
        savi: parsedData.vegetationIndices.savi
      };
    } else if (agentName === 'Irrigation Controller') {
      return {
        ndmi: parsedData.vegetationIndices.ndmi,
        mndwi: parsedData.vegetationIndices.mndwi || 0.18
      };
    } else if (agentName === 'Market Timing Agent') {
      return {
        ndvi: parsedData.vegetationIndices.ndvi,
        evi: parsedData.vegetationIndices.evi
      };
    } else if (agentName === 'Pest Detection Agent') {
      return {
        vari: parsedData.vegetationIndices.vari || 0.15,
        tcari: parsedData.vegetationIndices.tcari || 1.2
      };
    } else if (agentName === 'Harvest Prediction Agent') {
      return {
        ndvi: parsedData.vegetationIndices.ndvi,
        nbr: parsedData.vegetationIndices.nbr || 0.12,
        cmr: parsedData.vegetationIndices.cmr || 2.1
      };
    } else if (agentName === 'Input Materials Agent') {
      return {
        ndvi: parsedData.vegetationIndices.ndvi,
        vari: parsedData.vegetationIndices.vari || 0.08,
        tcari: parsedData.vegetationIndices.tcari || 1.6
      };
    } else if (agentName === 'Finance Policy Agent') {
      return {
        ndvi: parsedData.vegetationIndices.ndvi,
        ndmi: parsedData.vegetationIndices.ndmi
      };
    }

    return undefined;
  };
  
  // Sample agents data - in a real application, this would come from an API
  const agents: AgentData[] = [
    {
      id: 1,
      name: 'Crop Selection Agent',
      status: 'active',
      description: 'Analyzes vegetation indices and recommends optimal crop varieties',
      type: 'planning',
      lastActive: '1 minute ago',
      performance: 95,
      metrics: {
        tasksCompleted: 234,
        averageExecutionTime: 1.8,
        successRate: 0.97,
        requestsHandled: 345,
        errorRate: 0.03,
        uptime: 99.2
      },
      cpu: 15,
      memory: 189,
      version: '2.1.3',
      // vegetationIndices will be populated after query submission
      logs: [
        { timestamp: '2025-08-15T14:35:20', message: 'NDVI analysis completed for Field C7', level: 'info' },
        { timestamp: '2025-08-15T14:33:15', message: 'Crop health assessment: Excellent vegetation density', level: 'success' },
        { timestamp: '2025-08-15T14:30:45', message: 'Updated vegetation indices from satellite data', level: 'info' },
        { timestamp: '2025-08-15T14:28:30', message: 'Recommended wheat variety for optimal NDVI conditions', level: 'success' }
      ],
      connections: ['Satellite Data API', 'Weather Service', 'Soil Database', 'Crop Variety Database'],
      dependencies: ['Vegetation Analysis Library 3.1.2', 'Satellite Processing SDK 2.8', 'Agricultural ML Framework 4.0']
    },
    {
      id: 2,
      name: 'Market Timing Agent',
      status: 'active',
      description: 'Analyzes market trends and suggests optimal timing for crop sales',
      type: 'finance',
      lastActive: '2 minutes ago',
      performance: 92,
      metrics: {
        tasksCompleted: 156,
        averageExecutionTime: 2.3,
        successRate: 0.98,
        requestsHandled: 230,
        errorRate: 0.02,
        uptime: 99.8
      },
      cpu: 18,
      memory: 245,
      version: '1.3.2',
      vegetationIndices: {
        ndvi: 0.72,
        evi: 0.58
      },
      logs: [
        { timestamp: '2025-08-15T14:32:15', message: 'Market analysis completed successfully', level: 'info' },
        { timestamp: '2025-08-15T14:30:00', message: 'Fetched latest market data from external API', level: 'info' },
        { timestamp: '2025-08-15T14:28:45', message: 'Scheduled task: Market analysis initiated', level: 'info' },
        { timestamp: '2025-08-15T13:15:22', message: 'Connection restored to pricing service', level: 'success' },
        { timestamp: '2025-08-15T13:12:10', message: 'Warning: Slow response from pricing service', level: 'warning' }
      ],
      connections: ['Weather Service', 'Market Data API', 'Price Prediction Model', 'Notification System'],
      dependencies: ['TensorFlow 2.9.0', 'Market Analysis Library 3.2.1', 'Data Processing Pipeline 1.4']
    },
    {
      id: 2,
      name: 'Irrigation Controller',
      status: 'active',
      description: 'Monitors soil moisture levels and controls irrigation systems',
      type: 'irrigation',
      lastActive: '5 minutes ago',
      performance: 87,
      metrics: {
        tasksCompleted: 302,
        averageExecutionTime: 1.5,
        successRate: 0.94,
        requestsHandled: 512,
        errorRate: 0.06,
        uptime: 98.2
      },
      cpu: 12,
      memory: 128,
      version: '2.1.0',
      vegetationIndices: {
        ndmi: 0.234,
        mndwi: 0.18
      },
      logs: [
        { timestamp: '2025-08-15T14:22:35', message: 'Irrigation cycle completed for Field A12', level: 'info' },
        { timestamp: '2025-08-15T14:20:12', message: 'Initiated irrigation in response to low moisture levels', level: 'info' },
        { timestamp: '2025-08-15T14:15:08', message: 'Soil moisture below threshold (23.5%) in Field A12', level: 'warning' },
        { timestamp: '2025-08-15T14:25:30', message: 'NDMI moisture index updated: 0.234 (moderate stress)', level: 'warning' },
        { timestamp: '2025-08-15T13:45:22', message: 'System health check: Operational', level: 'success' }
      ],
      connections: ['Weather Station', 'Soil Moisture Sensors', 'Valve Control System', 'Central Water Management'],
      dependencies: ['IoT Control Framework 2.0', 'Sensor Integration API 1.8.5', 'Irrigation Scheduler 3.1']
    },
    {
      id: 3,
      name: 'Pest Detection Agent',
      status: 'inactive',
      description: 'Analyzes satellite and drone imagery to identify pest outbreaks',
      type: 'monitoring',
      lastActive: '3 hours ago',
      performance: 78,
      metrics: {
        tasksCompleted: 89,
        averageExecutionTime: 5.7,
        successRate: 0.85,
        requestsHandled: 98,
        errorRate: 0.15,
        uptime: 92.5
      },
      cpu: 0,
      memory: 15,
      version: '1.2.4',
      vegetationIndices: {
        vari: 0.15,
        tcari: 1.2
      },
      logs: [
        { timestamp: '2025-08-15T11:42:15', message: 'Agent stopped: Scheduled maintenance', level: 'info' },
        { timestamp: '2025-08-15T11:40:33', message: 'Backing up detection model parameters', level: 'info' },
        { timestamp: '2025-08-15T11:32:08', message: 'Warning: Image processing taking longer than expected', level: 'warning' },
        { timestamp: '2025-08-15T10:15:22', message: 'Satellite imagery reception delayed', level: 'warning' },
        { timestamp: '2025-08-15T09:05:10', message: 'Daily system check: Performance degradation detected', level: 'warning' }
      ],
      connections: ['Satellite Imagery Provider', 'Drone Fleet Control', 'Image Processing Pipeline', 'Alert System'],
      dependencies: ['TensorFlow 2.8.0', 'OpenCV 4.5.5', 'Imagery Analysis Toolkit 2.3.4']
    },
    {
      id: 4,
      name: 'Harvest Prediction Agent',
      status: 'active',
      description: 'Predicts optimal harvest times based on weather and crop data',
      type: 'planning',
      lastActive: '1 hour ago',
      performance: 94,
      metrics: {
        tasksCompleted: 208,
        averageExecutionTime: 3.2,
        successRate: 0.96,
        requestsHandled: 312,
        errorRate: 0.04,
        uptime: 99.5
      },
      cpu: 22,
      memory: 356,
      version: '2.2.1',
      vegetationIndices: {
        ndvi: 0.65,
        nbr: 0.12,
        cmr: 2.1
      },
      logs: [
        { timestamp: '2025-08-15T13:20:15', message: 'Updated harvest schedule for Fields B3-B8', level: 'info' },
        { timestamp: '2025-08-15T13:18:00', message: 'Applied weather forecast adjustments to prediction model', level: 'info' },
        { timestamp: '2025-08-15T13:15:45', message: 'Received updated weather forecast data', level: 'info' },
        { timestamp: '2025-08-15T12:10:22', message: 'Crop maturity estimates updated successfully', level: 'success' }
      ],
      connections: ['Weather Forecast Service', 'Crop Database', 'Field Sensor Network', 'Logistics Planning System'],
      dependencies: ['Agricultural ML Framework 3.0', 'Predictive Analytics Suite 2.5.1', 'Time Series Analysis 4.2']
    },
    {
      id: 5,
      name: 'Input Materials Agent',
      status: 'maintenance',
      description: 'Manages and orders farm input materials based on needs and pricing',
      type: 'logistics',
      lastActive: '1 day ago',
      performance: 81,
      metrics: {
        tasksCompleted: 162,
        averageExecutionTime: 2.8,
        successRate: 0.89,
        requestsHandled: 210,
        errorRate: 0.11,
        uptime: 94.2
      },
      cpu: 5,
      memory: 72,
      version: '1.8.3',
      vegetationIndices: {
        ndvi: 0.42,
        vari: 0.08,
        tcari: 1.6
      },
      logs: [
        { timestamp: '2025-08-14T10:42:15', message: 'Maintenance mode activated: Database optimization', level: 'info' },
        { timestamp: '2025-08-14T10:40:33', message: 'Backing up transaction history', level: 'info' },
        { timestamp: '2025-08-14T10:35:18', message: 'Warning: Supply chain data inconsistency detected', level: 'warning' },
        { timestamp: '2025-08-14T09:25:45', message: 'Error: Failed to connect to supplier API endpoint', level: 'error' },
        { timestamp: '2025-08-14T08:15:22', message: 'Scheduled maintenance announced for 10:30 AM', level: 'info' }
      ],
      connections: ['Inventory System', 'Supplier Network API', 'Procurement Database', 'Cost Analysis Engine'],
      dependencies: ['Supply Chain Manager 2.4', 'Inventory Control System 3.1.5', 'Financial Analytics 1.9']
    },
    {
      id: 6,
      name: 'Finance Policy Agent',
      status: 'active',
      description: 'Manages financial policies, loan eligibility, and risk assessment',
      type: 'finance',
      lastActive: '30 minutes ago',
      performance: 89,
      metrics: {
        tasksCompleted: 134,
        averageExecutionTime: 3.5,
        successRate: 0.93,
        requestsHandled: 187,
        errorRate: 0.07,
        uptime: 97.8
      },
      cpu: 14,
      memory: 198,
      version: '2.0.5',
      vegetationIndices: {
        ndvi: 0.68,
        ndmi: 0.25
      },
      logs: [
        { timestamp: '2025-08-15T14:05:20', message: 'Risk assessment completed for loan application #LA-2024-0892', level: 'info' },
        { timestamp: '2025-08-15T14:02:15', message: 'NDVI score above minimum threshold: 0.68 (>0.3)', level: 'success' },
        { timestamp: '2025-08-15T13:58:30', message: 'Environmental risk score calculated: 0.45', level: 'info' },
        { timestamp: '2025-08-15T13:55:10', message: 'Loan eligibility approved based on satellite data', level: 'success' }
      ],
      connections: ['Credit Bureau API', 'Satellite Data Service', 'Risk Assessment Engine', 'Banking Integration'],
      dependencies: ['Financial Risk Framework 3.2', 'Credit Scoring ML 2.1', 'Environmental Analytics 1.8']
    }
  ];

  // Filter options for the agents
  const filterOptions = ['All', 'Active', 'Inactive', 'Maintenance'];
  const typeOptions = ['All Types', 'Finance', 'Irrigation', 'Monitoring', 'Planning', 'Logistics'];

  // Stats for the agent status card
  const totalAgents = agents.length;
  const activeAgents = agents.filter(a => a.status === 'active').length;
  const inactiveAgents = agents.filter(a => a.status === 'inactive').length;
  const maintenanceAgents = agents.filter(a => a.status === 'maintenance').length;
  const errorAgents = agents.filter(a => a.status === 'error').length;
  
  // Calculate overall system health based on agent statuses and performance
  const calculateSystemHealth = () => {
    const totalPerformance = agents.reduce((sum, agent) => sum + agent.performance, 0);
    const avgPerformance = totalPerformance / agents.length;
    
    if (errorAgents > 0 || avgPerformance < 70) return 'critical';
    if (maintenanceAgents > 1 || avgPerformance < 80) return 'warning';
    return 'healthy';
  };
  
  const systemHealth = calculateSystemHealth();
  
  const handleAgentSelect = (agent: AgentData) => {
    setSelectedAgent(agent);
    setActiveTab('overview');
  };
  
  const handleTabChange = (tab: 'overview' | 'metrics' | 'logs' | 'connections') => {
    setActiveTab(tab);
  };

  return (
    <div className="agents-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Agent Management</h1>
          <p>View and manage your active agricultural agents</p>
        </div>
        <div className="header-actions">
          <button className="btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            Add New Agent
          </button>
        </div>
      </div>
      
      {/* Agent Status Card */}
      <div className="agent-status-card dashboard-card">
        <div className="dashboard-card-header">
          <h3 className="dashboard-card-title">
            <span>Agent Status Overview</span>
            {activeAgents > 0 && (
              <span className="active-count"> • {activeAgents} Active</span>
            )}
          </h3>
          <div className={`system-health ${systemHealth}`}>
            <span className="health-indicator"></span>
            System Health: {systemHealth.charAt(0).toUpperCase() + systemHealth.slice(1)}
          </div>
        </div>
        
        <div className="dashboard-card-body">
          <div className="status-metrics">
            <div className="status-metric-item">
              <div className="metric-value">{totalAgents}</div>
              <div className="metric-label">Total Agents</div>
            </div>
            <div className="status-metric-item active">
              <div className="metric-value">{activeAgents}</div>
              <div className="metric-label">Active</div>
            </div>
            <div className="status-metric-item inactive">
              <div className="metric-value">{inactiveAgents}</div>
              <div className="metric-label">Inactive</div>
            </div>
            <div className="status-metric-item maintenance">
              <div className="metric-value">{maintenanceAgents}</div>
              <div className="metric-label">Maintenance</div>
            </div>
            <div className="status-metric-item error">
              <div className="metric-value">{errorAgents}</div>
              <div className="metric-label">Error</div>
            </div>
          </div>
          
          <div className="status-chart">
            <div className="chart-header">
              <h3>Agent Performance</h3>
              <span className="chart-legend">
                <span className="legend-item"><span className="legend-color high"></span>High (90-100%)</span>
                <span className="legend-item"><span className="legend-color medium"></span>Medium (70-89%)</span>
                <span className="legend-item"><span className="legend-color low"></span>Low (&lt;70%)</span>
              </span>
            </div>
            <div className="performance-bars">
              {agents.map(agent => (
                <div key={`perf-${agent.id}`} className="performance-bar-container">
                  <div className="bar-label">{agent.name.split(' ')[0]}</div>
                  <div className="performance-bar-wrapper">
                    <div 
                      className={`performance-bar ${
                        agent.performance >= 90 ? 'high' : 
                        agent.performance >= 70 ? 'medium' : 'low'
                      }`}
                      style={{ width: `${agent.performance}%` }}
                    ></div>
                  </div>
                  <div className="bar-value">{agent.performance}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="dashboard-card-footer">
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
          <div className="card-actions-footer">
            <button className="action-button">View All Metrics</button>
            <button className="action-button">Export Data</button>
          </div>
        </div>
      </div>

      <div className="filter-section">
        <div className="search-container">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="search-icon">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
          <input 
            type="text" 
            placeholder="Search agents..." 
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-options">
          <div className="filter-group">
            <label>Status:</label>
            <select className="filter-select">
              {filterOptions.map((option, index) => (
                <option key={index} value={option.toLowerCase()}>{option}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Type:</label>
            <select className="filter-select">
              {typeOptions.map((option, index) => (
                <option key={index} value={option === 'All Types' ? 'all' : option.toLowerCase()}>{option}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="main-content-area">
        <div className="agents-list">
          {agents
            .filter(agent => 
              !searchQuery ||
              agent.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
              agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
              agent.type.toLowerCase().includes(searchQuery.toLowerCase())
            )
            .map(agent => (
            <div 
              key={agent.id} 
              className={`agent-card ${agent.status} ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
              onClick={() => handleAgentSelect(agent)}
            >
              <div className="agent-header">
                <div className="agent-name-section">
                  <div className={`status-indicator ${agent.status}`}></div>
                  <h3>{agent.name}</h3>
                  <span className={`agent-type ${agent.type}`}>{agent.type}</span>
                </div>
                <div className="agent-actions">
                  <button className="action-btn" onClick={(e) => e.stopPropagation()}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                      <path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
                      <path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
                    </svg>
                  </button>
                  <button className="action-btn" onClick={(e) => e.stopPropagation()}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                      <path d="M10 3a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM10 8.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM11.5 15.5a1.5 1.5 0 10-3 0 1.5 1.5 0 003 0z" />
                    </svg>
                  </button>
                </div>
              </div>

              <p className="agent-description">{agent.description}</p>

              <div className="agent-details">
                <div className="detail-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="detail-icon">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clipRule="evenodd" />
                  </svg>
                  <span>Last active: {agent.lastActive}</span>
                </div>
                <div className="detail-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="detail-icon">
                    <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clipRule="evenodd" />
                  </svg>
                  <span>Performance: {agent.performance}%</span>
                </div>
              </div>

              <div className="agent-footer">
                <button className="btn-secondary" onClick={(e) => e.stopPropagation()}>Configure</button>
                <button 
                  className={`btn-toggle ${agent.status === 'active' ? 'active' : ''}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  {agent.status === 'active' ? 'Active' : 'Inactive'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Agent Details Panel */}
        {selectedAgent && (
          <div className="agent-details-panel">
            <div className="panel-header">
              <div className="panel-title">
                <div className={`status-indicator ${selectedAgent.status}`}></div>
                <h2>{selectedAgent.name}</h2>
                <span className={`agent-type ${selectedAgent.type}`}>{selectedAgent.type}</span>
              </div>
              <button className="close-btn" onClick={() => setSelectedAgent(null)}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
            
            <div className="panel-tabs">
              <button 
                className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} 
                onClick={() => handleTabChange('overview')}
              >
                Overview
              </button>
              <button 
                className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`} 
                onClick={() => handleTabChange('metrics')}
              >
                Metrics
              </button>
              <button 
                className={`tab-btn ${activeTab === 'logs' ? 'active' : ''}`} 
                onClick={() => handleTabChange('logs')}
              >
                Logs
              </button>
              <button 
                className={`tab-btn ${activeTab === 'connections' ? 'active' : ''}`} 
                onClick={() => handleTabChange('connections')}
              >
                Connections
              </button>
            </div>
            
            <div className="panel-content">
              {activeTab === 'overview' && (
                <div className="overview-tab">
                  <div className="agent-status-section">
                    <h3>Status Information</h3>
                    <div className="status-grid">
                      <div className="status-item">
                        <span className="item-label">Status</span>
                        <span className={`item-value status-${selectedAgent.status}`}>
                          {selectedAgent.status.charAt(0).toUpperCase() + selectedAgent.status.slice(1)}
                        </span>
                      </div>
                      <div className="status-item">
                        <span className="item-label">Last Activity</span>
                        <span className="item-value">{selectedAgent.lastActive}</span>
                      </div>
                      <div className="status-item">
                        <span className="item-label">Performance</span>
                        <span className="item-value">{selectedAgent.performance}%</span>
                      </div>
                      <div className="status-item">
                        <span className="item-label">Version</span>
                        <span className="item-value">{selectedAgent.version || 'N/A'}</span>
                      </div>
                      <div className="status-item">
                        <span className="item-label">CPU Usage</span>
                        <span className="item-value">{selectedAgent.cpu || 0}%</span>
                      </div>
                      <div className="status-item">
                        <span className="item-label">Memory</span>
                        <span className="item-value">{selectedAgent.memory || 0} MB</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="agent-description-section">
                    <h3>Description</h3>
                    <p>{selectedAgent.description}</p>
                  </div>
                  
                  <div className="quick-actions">
                    <button className="action-button primary">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                      {selectedAgent.status === 'active' ? 'Stop Agent' : 'Start Agent'}
                    </button>
                    <button className="action-button">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                      </svg>
                      Configure
                    </button>
                    <button className="action-button">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                      </svg>
                      Restart
                    </button>
                    <button className="action-button danger">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Delete
                    </button>
                  </div>
                </div>
              )}
              
              {activeTab === 'metrics' && selectedAgent.metrics && (
                <div className="metrics-tab">
                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="metric-title">Tasks Completed</div>
                      <div className="metric-value">{selectedAgent.metrics.tasksCompleted}</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-title">Avg. Execution Time</div>
                      <div className="metric-value">{selectedAgent.metrics.averageExecutionTime}s</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-title">Success Rate</div>
                      <div className="metric-value">{(selectedAgent.metrics.successRate * 100).toFixed(1)}%</div>
                      <div className="metric-bar">
                        <div className="bar-fill" style={{ width: `${selectedAgent.metrics.successRate * 100}%` }}></div>
                      </div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-title">Uptime</div>
                      <div className="metric-value">{selectedAgent.metrics.uptime?.toFixed(1) || 'N/A'}%</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-title">Error Rate</div>
                      <div className="metric-value">{(selectedAgent.metrics.errorRate || 0) * 100}%</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-title">Requests Handled</div>
                      <div className="metric-value">{selectedAgent.metrics.requestsHandled || 0}</div>
                    </div>
                  </div>

                  {/* Vegetation Indices Section */}
                  {(() => {
                    const dynamicVegetationIndices = getVegetationIndicesForAgent(selectedAgent.name);
                    return dynamicVegetationIndices && (
                    <div className="vegetation-indices-section" style={{ marginTop: '30px' }}>
                      <h3>🌱 Vegetation Indices</h3>
                      <div className="vegetation-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
                        {dynamicVegetationIndices.ndvi && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #e8f5e8, #f0f8f0)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #4caf50',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#2e7d32', marginBottom: '8px' }}>
                              NDVI (Crop Health)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#1b5e20' }}>
                              {dynamicVegetationIndices.ndvi!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#388e3c', marginTop: '5px' }}>
                              {dynamicVegetationIndices.ndvi! >= 0.6 ? 'Excellent' :
                               dynamicVegetationIndices.ndvi! >= 0.4 ? 'Good' :
                               dynamicVegetationIndices.ndvi! >= 0.2 ? 'Fair' : 'Poor'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.evi && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #e8f5e8, #f0f8f0)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #4caf50',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#2e7d32', marginBottom: '8px' }}>
                              EVI (Enhanced Vegetation)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#1b5e20' }}>
                              {dynamicVegetationIndices.evi!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#388e3c', marginTop: '5px' }}>
                              Enhanced Index
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.savi && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #e8f5e8, #f0f8f0)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #4caf50',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#2e7d32', marginBottom: '8px' }}>
                              SAVI (Soil-Adjusted)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#1b5e20' }}>
                              {dynamicVegetationIndices.savi!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#388e3c', marginTop: '5px' }}>
                              Soil Compensated
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.ndmi && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #e3f2fd, #f0f8ff)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #2196f3',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#1565c0', marginBottom: '8px' }}>
                              NDMI (Moisture Index)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#0d47a1' }}>
                              {dynamicVegetationIndices.ndmi!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#1976d2', marginTop: '5px' }}>
                              {dynamicVegetationIndices.ndmi! >= 0.2 ? 'Good Moisture' :
                               dynamicVegetationIndices.ndmi! >= 0 ? 'Moderate' : 'Stress'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.mndwi && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #e3f2fd, #f0f8ff)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #2196f3',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#1565c0', marginBottom: '8px' }}>
                              MNDWI (Water Index)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#0d47a1' }}>
                              {dynamicVegetationIndices.mndwi!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#1976d2', marginTop: '5px' }}>
                              {dynamicVegetationIndices.mndwi! >= 0.2 ? 'High Moisture' :
                               dynamicVegetationIndices.mndwi! >= 0 ? 'Moderate' : 'Low Moisture'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.vari && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #fff3e0, #ffeaa7)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #ff9800',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#e65100', marginBottom: '8px' }}>
                              VARI (Visible Atmospherically Resistant Index)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#bf360c' }}>
                              {dynamicVegetationIndices.vari!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#d84315', marginTop: '5px' }}>
                              {dynamicVegetationIndices.vari! >= 0.2 ? 'Healthy' :
                               dynamicVegetationIndices.vari! >= 0 ? 'Mild Stress' : 'Moderate Stress'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.tcari && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #fff3e0, #ffeaa7)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #ff9800',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#e65100', marginBottom: '8px' }}>
                              TCARI (Chlorophyll Absorption)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#bf360c' }}>
                              {dynamicVegetationIndices.tcari!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#d84315', marginTop: '5px' }}>
                              {dynamicVegetationIndices.tcari! <= 0.5 ? 'Healthy Chlorophyll' :
                               dynamicVegetationIndices.tcari! <= 1.0 ? 'Moderate' : 'Deficient'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.nbr && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #f3e5f5, #e1bee7)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #9c27b0',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#6a1b9a', marginBottom: '8px' }}>
                              NBR (Normalized Burn Ratio)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#4a148c' }}>
                              {dynamicVegetationIndices.nbr!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#7b1fa2', marginTop: '5px' }}>
                              {dynamicVegetationIndices.nbr! >= 0.1 ? 'Healthy' : 'Monitor'}
                            </div>
                          </div>
                        )}

                        {dynamicVegetationIndices.cmr && (
                          <div className="vegetation-card" style={{
                            background: 'linear-gradient(135deg, #f3e5f5, #e1bee7)',
                            padding: '15px',
                            borderRadius: '10px',
                            border: '2px solid #9c27b0',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontWeight: '600', color: '#6a1b9a', marginBottom: '8px' }}>
                              CMR (Crop Maturity Ratio)
                            </div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '700', color: '#4a148c' }}>
                              {dynamicVegetationIndices.cmr!.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#7b1fa2', marginTop: '5px' }}>
                              {dynamicVegetationIndices.cmr! >= 2.0 && dynamicVegetationIndices.cmr! <= 3.0 ? 'Optimal' :
                               dynamicVegetationIndices.cmr! < 2.0 ? 'Underripe' : 'Overripe'}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                  })()}

                  <div className="metrics-chart">
                    <h3>Performance Over Time</h3>
                    <div className="chart-placeholder">
                      <div className="placeholder-text">Performance chart visualization will appear here</div>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTab === 'logs' && selectedAgent.logs && (
                <div className="logs-tab">
                  <div className="logs-header">
                    <h3>Recent Logs</h3>
                    <div className="logs-filter">
                      <label>Filter:</label>
                      <select>
                        <option value="all">All Levels</option>
                        <option value="info">Info</option>
                        <option value="warning">Warning</option>
                        <option value="error">Error</option>
                        <option value="success">Success</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="logs-container">
                    {selectedAgent.logs.map((log, index) => (
                      <div key={index} className={`log-entry ${log.level}`}>
                        <span className="log-timestamp">{new Date(log.timestamp).toLocaleTimeString()}</span>
                        <span className={`log-level ${log.level}`}>{log.level.toUpperCase()}</span>
                        <span className="log-message">{log.message}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="logs-footer">
                    <button className="action-button small">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Export Logs
                    </button>
                    <button className="action-button small">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM4.332 8.027a6.012 6.012 0 011.912-2.706C6.512 5.73 6.974 6 7.5 6A1.5 1.5 0 019 7.5V8a2 2 0 004 0 2 2 0 011.523-1.943A5.977 5.977 0 0116 10c0 .34-.028.675-.083 1H15a2 2 0 00-2 2v2.197A5.973 5.973 0 0110 16v-2a2 2 0 00-2-2 2 2 0 01-2-2 2 2 0 00-1.668-1.973z" clipRule="evenodd" />
                      </svg>
                      View Full Log
                    </button>
                  </div>
                </div>
              )}
              
              {activeTab === 'connections' && (
                <div className="connections-tab">
                  <div className="section">
                    <h3>Connected Services</h3>
                    {selectedAgent.connections && (
                      <div className="connections-list">
                        {selectedAgent.connections.map((connection, index) => (
                          <div key={index} className="connection-item">
                            <div className="connection-icon">
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                              </svg>
                            </div>
                            <div className="connection-name">{connection}</div>
                            <div className="connection-status">
                              <span className="status-badge connected">Connected</span>
                            </div>
                            <div className="connection-action">
                              <button className="small-action-btn">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                  <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="section">
                    <h3>Dependencies</h3>
                    {selectedAgent.dependencies && (
                      <div className="dependencies-list">
                        {selectedAgent.dependencies.map((dependency, index) => (
                          <div key={index} className="dependency-item">
                            <span className="dependency-name">{dependency.split(' ')[0]}</span>
                            <span className="dependency-version">{dependency.split(' ')[1] || ''}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {!selectedAgent && (
        <div className="pagination">
          <button className="page-btn active">1</button>
          <button className="page-btn">2</button>
          <button className="page-btn">3</button>
          <span className="page-ellipsis">...</span>
          <button className="page-btn">8</button>
        </div>
      )}
    </div>
  );
};

export default AgentsPage;
