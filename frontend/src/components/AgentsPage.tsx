import React, { useState, useEffect } from 'react';
import './AgentsPage.css';
import './Dashboard.css';
import { faker } from '@faker-js/faker';

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
  startedAt?: string;
  steps?: {
    total: number;
    completed: number;
  };
  priority?: 'High' | 'Medium' | 'Low';
}

// Mock data generators
const generateRandomTime = () => {
  const options = [
    '1 minute ago',
    '2 minutes ago',
    '5 minutes ago',
    '10 minutes ago',
    '15 minutes ago',
    '30 minutes ago',
    '1 hour ago',
    '2 hours ago',
    '3 hours ago',
    '5 hours ago',
    '1 day ago'
  ];
  
  return faker.helpers.arrayElement(options);
};

const generateAgentStatus = () => {
  const statuses: ('active' | 'inactive' | 'maintenance' | 'error')[] = ['active', 'inactive', 'maintenance', 'error'];
  const weights = [0.65, 0.15, 0.15, 0.05]; // 65% active, 15% inactive, 15% maintenance, 5% error
  
  // Weighted random selection
  const rand = Math.random();
  let sum = 0;
  for (let i = 0; i < weights.length; i++) {
    sum += weights[i];
    if (rand < sum) {
      return statuses[i];
    }
  }
  
  return statuses[0]; // Default to active
};

const generatePriority = () => {
  const priorities: ('High' | 'Medium' | 'Low')[] = ['High', 'Medium', 'Low'];
  const weights = [0.3, 0.5, 0.2]; // 30% High, 50% Medium, 20% Low
  
  const rand = Math.random();
  let sum = 0;
  for (let i = 0; i < weights.length; i++) {
    sum += weights[i];
    if (rand < sum) {
      return priorities[i];
    }
  }
  
  return priorities[1]; // Default to Medium
};

const generateAgentType = () => {
  return faker.helpers.arrayElement(['finance', 'irrigation', 'monitoring', 'planning', 'logistics']);
};

// Define namesByType outside both functions so it's accessible to both
const namesByType: Record<string, string[]> = {
  finance: ['Market Timing Agent', 'Price Prediction Agent', 'Financial Planning Agent', 'Budget Optimization Agent'],
  irrigation: ['Irrigation Controller', 'Water Management System', 'Moisture Optimization Agent', 'Irrigation Scheduler'],
  monitoring: ['Pest Detection Agent', 'Field Monitoring System', 'Crop Health Monitor', 'Disease Detection Agent'],
  planning: ['Harvest Prediction Agent', 'Crop Planning Assistant', 'Rotation Scheduler', 'Yield Forecaster'],
  logistics: ['Input Materials Agent', 'Supply Chain Manager', 'Resource Allocation Agent', 'Inventory Controller']
};

const generateAgentName = (type: string): string => {
  return faker.helpers.arrayElement(namesByType[type] || [`${type.charAt(0).toUpperCase() + type.slice(1)} Agent`]);
};

const generateAgentDescription = (type: string, name: string): string => {
  const descriptionsByType: Record<string, string[]> = {
    finance: [
      'Analyzes market trends and suggests optimal timing for crop sales',
      'Predicts market prices to maximize profit margins',
      'Plans financial operations and optimizes cash flow',
      'Optimizes budget allocation based on current market conditions'
    ],
    irrigation: [
      'Monitors soil moisture levels and controls irrigation systems',
      'Manages water distribution across multiple field zones',
      'Optimizes water usage based on weather and crop needs',
      'Schedules irrigation cycles to maximize efficiency'
    ],
    monitoring: [
      'Analyzes satellite and drone imagery to identify pest outbreaks',
      'Monitors field conditions to detect anomalies',
      'Tracks crop health indicators across all fields',
      'Identifies early signs of disease or pest issues'
    ],
    planning: [
      'Predicts optimal harvest times based on weather and crop data',
      'Assists in planning crop rotations and schedules',
      'Forecasts expected yields based on current conditions',
      'Schedules farm operations for maximum efficiency'
    ],
    logistics: [
      'Manages and orders farm input materials based on needs and pricing',
      'Optimizes the supply chain for farm operations',
      'Allocates resources across different farm activities',
      'Controls inventory levels of critical farming supplies'
    ]
  };
  
  // Find the index of the name in the type's array to match description
  const nameArray = namesByType[type] || [];
  const index = nameArray.indexOf(name);
  
  if (index !== -1 && descriptionsByType[type] && index < descriptionsByType[type].length) {
    return descriptionsByType[type][index];
  }
  
  return faker.helpers.arrayElement(descriptionsByType[type] || ['Manages agricultural operations and provides insights']);
};

const generatePerformance = (status: string): number => {
  // Performance ranges based on status
  if (status === 'active') {
    return faker.number.int({ min: 85, max: 100 });
  } else if (status === 'inactive') {
    return faker.number.int({ min: 70, max: 85 });
  } else if (status === 'maintenance') {
    return faker.number.int({ min: 65, max: 80 });
  } else { // error
    return faker.number.int({ min: 40, max: 70 });
  }
};

const generateMockAgents = (count: number = 5): AgentData[] => {
  const agents: AgentData[] = [];
  
  for (let i = 0; i < count; i++) {
    const type = generateAgentType();
    const name = generateAgentName(type);
    const status = generateAgentStatus();
    const performance = generatePerformance(status);
    
    agents.push({
      id: i + 1,
      name,
      status,
      type,
      description: generateAgentDescription(type, name),
      lastActive: generateRandomTime(),
      performance,
      startedAt: faker.date.recent({ days: 1 }).toISOString(),
      steps: {
        total: faker.number.int({ min: 5, max: 10 }),
        completed: faker.number.int({ min: 0, max: 5 })
      },
      priority: generatePriority(),
      metrics: {
        tasksCompleted: faker.number.int({ min: 50, max: 300 }),
        averageExecutionTime: parseFloat(faker.number.float({ min: 1.2, max: 5.8 }).toFixed(1)),
        successRate: parseFloat(faker.number.float({ min: 0.8, max: 0.99 }).toFixed(2)),
        uptime: parseFloat(faker.number.float({ min: 90, max: 99.9 }).toFixed(1)),
        errorRate: parseFloat(faker.number.float({ min: 0.01, max: 0.2 }).toFixed(2)),
        requestsHandled: faker.number.int({ min: 50, max: 500 })
      },
      cpu: status !== 'inactive' ? faker.number.int({ min: 5, max: 40 }) : 0,
      memory: status !== 'inactive' ? faker.number.int({ min: 50, max: 400 }) : 15,
      version: `${faker.number.int({ min: 1, max: 3 })}.${faker.number.int({ min: 0, max: 9 })}.${faker.number.int({ min: 0, max: 9 })}`,
      logs: [
        { 
          timestamp: faker.date.recent({ days: 1 }).toISOString(), 
          message: 'System health check completed', 
          level: 'info' 
        },
        { 
          timestamp: faker.date.recent({ days: 1 }).toISOString(), 
          message: status === 'error' ? 'Connection error with data source' : 'Data processing completed', 
          level: status === 'error' ? 'error' : 'success' 
        }
      ],
      connections: ['Data Source API', 'Central Management System', 'Notification Service'],
      dependencies: ['Core Framework 2.0', 'Data Processing Library 1.8', 'Analytics Engine 3.2']
    });
  }
  
  // Ensure we have specific agent types included for demonstration
  const requiredTypes = ['finance', 'irrigation', 'monitoring', 'planning', 'logistics'];
  const existingTypes = new Set(agents.map(a => a.type));
  
  // Add any missing required agent types
  requiredTypes.forEach(type => {
    if (!existingTypes.has(type) && agents.length < count + 5) {
      const name = generateAgentName(type);
      const status = generateAgentStatus();
      const performance = generatePerformance(status);
      
      agents.push({
        id: agents.length + 1,
        name,
        status,
        type,
        description: generateAgentDescription(type, name),
        lastActive: generateRandomTime(),
        performance,
        startedAt: faker.date.recent({ days: 1 }).toISOString(),
        steps: {
          total: faker.number.int({ min: 5, max: 10 }),
          completed: faker.number.int({ min: 0, max: 5 })
        },
        priority: generatePriority(),
        metrics: {
          tasksCompleted: faker.number.int({ min: 50, max: 300 }),
          averageExecutionTime: parseFloat(faker.number.float({ min: 1.2, max: 5.8 }).toFixed(1)),
          successRate: parseFloat(faker.number.float({ min: 0.8, max: 0.99 }).toFixed(2)),
          uptime: parseFloat(faker.number.float({ min: 90, max: 99.9 }).toFixed(1)),
          errorRate: parseFloat(faker.number.float({ min: 0.01, max: 0.2 }).toFixed(2)),
          requestsHandled: faker.number.int({ min: 50, max: 500 })
        },
        cpu: status !== 'inactive' ? faker.number.int({ min: 5, max: 40 }) : 0,
        memory: status !== 'inactive' ? faker.number.int({ min: 50, max: 400 }) : 15,
        version: `${faker.number.int({ min: 1, max: 3 })}.${faker.number.int({ min: 0, max: 9 })}.${faker.number.int({ min: 0, max: 9 })}`,
        logs: [
          { 
            timestamp: faker.date.recent({ days: 1 }).toISOString(), 
            message: 'System health check completed', 
            level: 'info' 
          },
          { 
            timestamp: faker.date.recent({ days: 1 }).toISOString(), 
            message: status === 'error' ? 'Connection error with data source' : 'Data processing completed', 
            level: status === 'error' ? 'error' : 'success' 
          }
        ],
        connections: ['Data Source API', 'Central Management System', 'Notification Service'],
        dependencies: ['Core Framework 2.0', 'Data Processing Library 1.8', 'Analytics Engine 3.2']
      });
    }
  });
  
  return agents;
};

const AgentsPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AgentData | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'logs' | 'connections'>('overview');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [agents, setAgents] = useState<AgentData[]>(() => generateMockAgents(5));
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  
  // Setup auto-refresh interval (every 5 seconds)
  useEffect(() => {
    const intervalId = setInterval(() => {
      // Generate new mock agents and update time
      setAgents(prevAgents => {
        const newAgents = generateMockAgents(5);
        
        // If there's a selected agent, update it
        if (selectedAgent) {
          const updatedSelectedAgent = newAgents.find(agent => agent.id === selectedAgent.id);
          if (updatedSelectedAgent) {
            setSelectedAgent(updatedSelectedAgent);
          }
        }
        
        return newAgents;
      });
      
      setLastUpdated(new Date());
    }, 5000); // 5 seconds interval
    
    // Cleanup on component unmount
    return () => clearInterval(intervalId);
  }, [selectedAgent]);
  
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
                  <div className="bar-label" title={agent.name}>{agent.name.split(' ')[0]}</div>
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
          <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
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
                {agent.steps && (
                  <div className="detail-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="detail-icon">
                      <path d="M6 3a1 1 0 00-1 1v2.586l-.707-.707a1 1 0 10-1.414 1.414l3 3a.997.997 0 001.414 0l3-3a1 1 0 10-1.414-1.414L8 6.586V4a1 1 0 00-1-1H6zM14 3a1 1 0 011 1v2.586l.707-.707a1 1 0 111.414 1.414l-3 3a.997.997 0 01-1.414 0l-3-3a1 1 0 111.414-1.414L12 6.586V4a1 1 0 011-1h1z" />
                      <path d="M6 12a1 1 0 00-1 1v2.586l-.707-.707a1 1 0 10-1.414 1.414l3 3a.997.997 0 001.414 0l3-3a1 1 0 10-1.414-1.414L8 15.586V13a1 1 0 00-1-1H6zM14 12a1 1 0 011 1v2.586l.707-.707a1 1 0 111.414 1.414l-3 3a.997.997 0 01-1.414 0l-3-3a1 1 0 111.414-1.414L12 15.586V13a1 1 0 011-1h1z" />
                    </svg>
                    <span>Steps: {agent.steps.completed}/{agent.steps.total}</span>
                  </div>
                )}
              </div>

              <div className="agent-footer">
                <button className="btn-secondary" onClick={(e) => e.stopPropagation()}>Configure</button>
                <div className="agent-meta">
                  {agent.priority && (
                    <span className={`priority-badge ${agent.priority.toLowerCase()}`}>
                      {agent.priority}
                    </span>
                  )}
                  <button 
                    className={`btn-toggle ${agent.status === 'active' ? 'active' : ''}`}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {agent.status === 'active' ? 'Active' : agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </button>
                </div>
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
