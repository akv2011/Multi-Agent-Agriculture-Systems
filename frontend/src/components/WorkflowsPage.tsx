import React, { useState, useEffect, useRef } from 'react';
import './WorkflowsPage.css';
import WorkflowVisualizer from './WorkflowVisualizer';
import type { Workflow, WorkflowStep } from './WorkflowVisualizer';
import { faker } from '@faker-js/faker';

// Modal components
const Modal = ({ isOpen, onClose, title, children }: { 
  isOpen: boolean; 
  onClose: () => void; 
  title: string; 
  children: React.ReactNode 
}) => {
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

// Mock data generator using Faker.js
const generateMockWorkflows = (count = 5): Workflow[] => {
  const workflows: Workflow[] = [];
  
  // Define constants for workflow generation
  const workflowTypes = [
    { type: 'Crop Rotation', name: 'Crop Rotation Planning Workflow' }, 
    { type: 'Irrigation', name: 'Irrigation Scheduling Workflow' },
    { type: 'Pest Detection', name: 'Pest Detection Analysis' },
    { type: 'Soil Analysis', name: 'Soil Composition Analysis' },
    { type: 'Yield Prediction', name: 'Yield Prediction Workflow' },
    { type: 'Fertilizer', name: 'Fertilizer Optimization' },
    { type: 'Harvest', name: 'Harvest Planning Workflow' },
    { type: 'Weather', name: 'Weather Impact Assessment' },
    { type: 'Resource', name: 'Resource Allocation Planning' }
  ];
  
  const agentNames = [
    "data-processing-agent", 
    "soil-analysis-agent", 
    "crop-planning-agent", 
    "optimization-agent", 
    "nutrient-analysis-agent",
    "planning-agent",
    "reporting-agent",
    "sensor-data-agent",
    "weather-agent",
    "irrigation-calculation-agent",
    "control-system-agent",
    "image-processing-agent",
    "anomaly-detection-agent",
    "pest-classification-agent",
    "treatment-planning-agent"
  ];

  const stepNames = {
    "Crop Rotation": ["Initialize Field Data", "Analyze Soil Composition", "Generate Crop Options", 
                      "Optimize Rotation Schedule", "Validate Nutrient Balance", "Generate Implementation Plan", "Create Final Report"],
    "Irrigation": ["Load Moisture Sensor Data", "Process Weather Forecast", "Calculate Water Requirements", 
                   "Optimize Irrigation Schedule", "Generate Irrigation Commands"],
    "Pest Detection": ["Process Drone Imagery", "Detect Anomalies", "Classify Pest Types", 
                        "Generate Intervention Plan"],
    "Soil Analysis": ["Collect Samples", "Process Laboratory Results", "Map Soil Properties", 
                      "Generate Recommendations"],
    "Yield Prediction": ["Gather Historical Data", "Process Weather Forecasts", "Analyze Current Growth", 
                         "Generate Yield Estimates", "Create Reports"],
    "Fertilizer": ["Analyze Soil Nutrients", "Determine Crop Requirements", "Calculate Application Rates", 
                   "Generate Application Schedule", "Create Work Orders"],
    "Harvest": ["Monitor Crop Maturity", "Predict Optimal Harvest Date", "Allocate Resources", 
                "Generate Harvest Plan", "Schedule Transportation"],
    "Weather": ["Collect Forecast Data", "Analyze Historical Patterns", "Identify Risk Factors", 
                "Generate Mitigation Strategies"],
    "Resource": ["Inventory Available Resources", "Analyze Field Requirements", "Prioritize Operations", 
                "Allocate Equipment", "Generate Work Orders"]
  };
  
  const statuses: Workflow['status'][] = ['pending', 'running', 'completed', 'failed', 'cancelled'];
  const stepStatuses: WorkflowStep['status'][] = ['pending', 'in-progress', 'completed', 'failed', 'skipped'];
  const priorities = ['low', 'medium', 'high'];
  
  // Generate workflows
  for (let i = 0; i < count; i++) {
    // Generate ID with consistent format
    const id = `wf-${(i + 1).toString().padStart(3, '0')}`;
    
    // Get a random workflow type and name
    const workflowTypeIndex = faker.number.int({ min: 0, max: workflowTypes.length - 1 });
    const workflowType = workflowTypes[workflowTypeIndex].type;
    const name = workflowTypes[workflowTypeIndex].name;
    
    // Get a random status, weighted to have more running workflows
    const statusWeights = [0.2, 0.5, 0.2, 0.1, 0]; // pending, running, completed, failed, cancelled
    let status: Workflow['status'] = 'running';
    const randomValue = faker.number.float({ min: 0, max: 1 });
    let cumulativeWeight = 0;
    for (let s = 0; s < statuses.length; s++) {
      cumulativeWeight += statusWeights[s];
      if (randomValue <= cumulativeWeight) {
        status = statuses[s];
        break;
      }
    }
    
    // Generate start time that varies over time for more realism
    const baseTime = Date.now();
    const timeVariation = Math.sin(baseTime / 10000) * 1800000; // Sine wave variation over time
    const startTime = faker.date.recent({ 
      days: 0.04 + (timeVariation / (24 * 60 * 60 * 1000)) 
    }).toISOString();
    
    // Set progress based on status with time-aware variations
    let progress = 0;
    let isIncreasing = false;
    const currentTime = Date.now();
    const timeOffset = (currentTime / 1000) % 3600; // Hour-based cycle
    
    if (status === 'completed') {
      progress = faker.number.float({ min: 0.95, max: 1.0 }); // 95-100% for completed
    } else if (status === 'running') {
      // Time-based progress that varies and steadily increases
      const baseProgress = faker.number.float({ min: 0.1, max: 0.6 });
      const timeVariation = (Math.sin(timeOffset / 600) + 1) * 0.125; // 0-0.25 variation
      progress = Math.min(baseProgress + timeVariation, 0.85); // Cap at 85%
      isIncreasing = Math.random() > 0.25; // 75% chance of increasing
    } else if (status === 'failed') {
      progress = faker.number.float({ min: 0.05, max: 0.6 }); // 5-60% for failed
    } else if (status === 'pending') {
      progress = faker.number.float({ min: 0.0, max: 0.15 }); // 0-15% for pending
    }
    
    // Get steps array based on workflow type
    const stepsArray = stepNames[workflowType as keyof typeof stepNames] || 
                      ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"];
    
    const totalSteps = stepsArray.length;
    const completedStepCount = Math.floor(progress * totalSteps);
    
    const steps: WorkflowStep[] = [];
    
    for (let j = 0; j < totalSteps; j++) {
      let stepStatus: WorkflowStep['status'] = 'pending';
      let stepStartTime;
      let stepEndTime;
      let duration;
      let output;
      let error;
      
      // Determine step status and related information
      if (j < completedStepCount) {
        stepStatus = 'completed';
        stepStartTime = faker.date.recent({ days: 0.04 }).toISOString();
        stepEndTime = faker.date.between({
          from: new Date(stepStartTime),
          to: new Date(new Date(stepStartTime).getTime() + 15 * 60 * 1000)
        }).toISOString();
        duration = new Date(stepEndTime).getTime() - new Date(stepStartTime).getTime();
        output = `Successfully completed ${stepsArray[j].toLowerCase()} process.`;
      } else if (j === completedStepCount && status === 'running') {
        stepStatus = 'in-progress';
        stepStartTime = faker.date.recent({ days: 0.007 }).toISOString(); // Up to ~10 min ago
      } else if (j === completedStepCount && status === 'failed') {
        stepStatus = 'failed';
        stepStartTime = faker.date.recent({ days: 0.01 }).toISOString(); // Up to ~15 min ago
        stepEndTime = faker.date.between({
          from: new Date(stepStartTime),
          to: new Date(new Date(stepStartTime).getTime() + 5 * 60 * 1000)
        }).toISOString();
        duration = new Date(stepEndTime).getTime() - new Date(stepStartTime).getTime();
        error = faker.helpers.arrayElement([
          'ERROR: Process failed due to missing data.',
          'ERROR: Service unavailability detected.',
          'ERROR: Input validation failed.',
          'ERROR: Resource allocation failed.',
          'ERROR: Timeout occurred during processing.'
        ]);
      }
      
      // Randomly assign an agent from the list
      const agent = faker.helpers.arrayElement(agentNames);
      
      steps.push({
        id: `step-${j + 1}`,
        name: stepsArray[j],
        status: stepStatus,
        startTime: stepStartTime,
        endTime: stepEndTime,
        duration,
        output,
        error,
        agent
      });
    }
    
    // Generate end time if workflow is completed or failed
    let endTime;
    let totalDuration;
    if (status === 'completed' || status === 'failed') {
      endTime = faker.date.between({
        from: new Date(startTime),
        to: new Date(new Date(startTime).getTime() + 2 * 60 * 60 * 1000)
      }).toISOString();
      totalDuration = new Date(endTime).getTime() - new Date(startTime).getTime();
    }
    
    // Generate metadata
    const metadata: { [key: string]: any } = {
      priority: faker.helpers.arrayElement(priorities),
      requestedBy: faker.person.fullName(),
      tags: Array.from({ length: faker.number.int({ min: 1, max: 3 }) }, () => 
        faker.helpers.arrayElement(['automation', 'field', 'irrigation', 'planning', 'critical', 'seasonal', 'analysis'])
      )
    };
    
    // Add workflow-specific metadata
    if (workflowType === 'Crop Rotation') {
      metadata.fieldCount = faker.number.int({ min: 1, max: 15 });
      metadata.estimatedCompletion = faker.date.soon({ days: 1 }).toISOString();
    } else if (workflowType === 'Irrigation') {
      metadata.waterSaved = `${faker.number.int({ min: 5, max: 35 })}%`;
      metadata.nextSchedule = faker.date.soon({ days: 1 }).toISOString();
    } else if (workflowType === 'Pest Detection') {
      metadata.affectedArea = `${faker.number.int({ min: 1, max: 20 })} acres`;
      metadata.retryScheduled = faker.date.soon({ days: 0.25 }).toISOString();
    }
    
    workflows.push({
      id,
      name,
      status,
      startTime,
      endTime,
      totalDuration,
      progress,
      isIncreasing,
      steps,
      metadata
    });
  }
  
  return workflows;
};

// Function to update workflow progress and status
const updateWorkflowProgress = (workflows: Workflow[], isManualRefresh = false): Workflow[] => {
  return workflows.map(workflow => {
    // Only update running workflows
    if (workflow.status !== 'running') {
      // Occasionally change a pending workflow to running
      if (workflow.status === 'pending' && Math.random() < 0.1) {
        return {
          ...workflow,
          status: 'running',
          startTime: new Date().toISOString()
        };
      }
      // Don't modify other non-running workflows
      return workflow;
    }
    
    // Determine progress increment based on whether it's a manual refresh
    // Manual refresh: 5-10% increase
    // Automatic refresh: 1-5% increase
    const minIncrement = isManualRefresh ? 0.05 : 0.01;
    const maxIncrement = isManualRefresh ? 0.10 : 0.05;
    const progressIncrement = faker.number.float({ min: minIncrement, max: maxIncrement });
    
    // Cap progress at 99% so workflows don't complete automatically
    const newProgress = Math.min(workflow.progress + progressIncrement, 0.99);
    
    // Always keep status as running since we cap at 99%
    const newStatus = 'running';
    
    // Update steps based on new progress
    const totalSteps = workflow.steps.length;
    const previousCompletedCount = workflow.steps.filter(s => s.status === 'completed').length;
    const completedStepCount = Math.floor(newProgress * totalSteps);
    
    // Only update steps if the completed count has changed
    let newSteps = [...workflow.steps];
    if (completedStepCount > previousCompletedCount) {
      newSteps = workflow.steps.map((step, index) => {
        if (index < completedStepCount && step.status !== 'completed') {
          // This step is now completed
          const stepEndTime = new Date().toISOString();
          const stepStartTime = step.startTime || faker.date.recent({ days: 0.01 }).toISOString();
          const duration = new Date(stepEndTime).getTime() - new Date(stepStartTime).getTime();
          
          return {
            ...step,
            status: 'completed',
            startTime: stepStartTime,
            endTime: stepEndTime,
            duration,
            output: `Successfully completed ${step.name.toLowerCase()} process.`
          };
        } else if (index === completedStepCount && step.status !== 'in-progress') {
          // This step is now in progress
          return {
            ...step,
            status: 'in-progress',
            startTime: new Date().toISOString()
          };
        }
        return step;
      });
    }
    
    return {
      ...workflow,
      progress: newProgress,
      status: newStatus as Workflow['status'],
      steps: newSteps,
      isIncreasing: true // Flag to indicate progress is increasing
    };
  });
};

const WorkflowsPage: React.FC = () => {
  // State for workflow data with initial mock data
  const [workflows, setWorkflows] = useState<Workflow[]>(() => generateMockWorkflows(5));
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showMobileDetails, setShowMobileDetails] = useState<boolean>(false);
  const intervalRef = useRef<number | null>(null);
  
  // State for modal dialogs
  const [showViewDetailsModal, setShowViewDetailsModal] = useState<boolean>(false);
  const [showExportModal, setShowExportModal] = useState<boolean>(false);

  // Update selected workflow if it gets updated in the workflows list
  useEffect(() => {
    if (selectedWorkflow) {
      const updatedWorkflow = workflows.find(w => w.id === selectedWorkflow.id);
      if (updatedWorkflow && JSON.stringify(updatedWorkflow) !== JSON.stringify(selectedWorkflow)) {
        setSelectedWorkflow(updatedWorkflow);
      }
    } else if (workflows.length > 0) {
      // Select the first workflow if none is selected
      setSelectedWorkflow(workflows[0]);
    }
  }, [workflows, selectedWorkflow]);

  // Setup interval to refresh workflow data every 5 seconds
  useEffect(() => {
    // Update workflow progress every 5 seconds
    intervalRef.current = window.setInterval(() => {
      setWorkflows(prevWorkflows => {
        // Occasionally add a new workflow (10% chance)
        const shouldAddNewWorkflow = Math.random() < 0.1 && prevWorkflows.length < 15;
        
        // Update existing workflows (false = automatic refresh)
        const updatedWorkflows = updateWorkflowProgress(prevWorkflows, false);
        
        // Add new workflow if needed
        if (shouldAddNewWorkflow) {
          const newWorkflow = generateMockWorkflows(1)[0];
          console.log('Auto-generated new workflow:', newWorkflow.id);
          return [...updatedWorkflows, newWorkflow];
        }
        
        return updatedWorkflows;
      });
    }, 5000); // 5 seconds refresh interval
    
    // Cleanup interval on component unmount
    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setShowMobileDetails(true); // Show details panel on mobile
  };

  const handleStepClick = (step: WorkflowStep) => {
    console.log('Step clicked:', step);
  };
  
  // Handler for creating a new workflow
  const handleCreateWorkflow = () => {
    // Generate a new workflow and add it to the list
    const newWorkflow = generateMockWorkflows(1)[0];
    
    // Show a success message
    alert(`Created new workflow: ${newWorkflow.name} (ID: ${newWorkflow.id})`);
    
    setWorkflows(prev => [...prev, newWorkflow]);
    setSelectedWorkflow(newWorkflow);
  };
  
  // Handler for refreshing workflows
  const handleRefresh = (isManual: boolean = true) => {
    // Manual refresh with higher progress increase
    const updatedWorkflows = updateWorkflowProgress(workflows, isManual);
    setWorkflows(updatedWorkflows);
    
    if (isManual) {
      alert('Workflows refreshed with 5-10% progress increase');
    }
  };
  
  // Handler for viewing workflow details
  const handleViewDetails = (workflow: Workflow) => {
    setShowViewDetailsModal(true);
    console.log('Viewing details for workflow:', workflow);
    
    // Simple implementation - display a formatted JSON alert
    const details = JSON.stringify({
      id: workflow.id,
      name: workflow.name,
      status: workflow.status,
      progress: Math.round(workflow.progress * 100) + '%',
      startTime: new Date(workflow.startTime || '').toLocaleString(),
      endTime: workflow.endTime ? new Date(workflow.endTime).toLocaleString() : 'N/A',
      steps: `${workflow.steps.filter(s => s.status === 'completed').length}/${workflow.steps.length} completed`,
      priority: workflow.metadata?.priority || 'normal'
    }, null, 2);
    
    alert(`Workflow Details:\n${details}`);
    setShowViewDetailsModal(false);
  };
  
  // Handler for exporting workflow data
  const handleExportData = (workflow: Workflow) => {
    setShowExportModal(true);
    console.log('Exporting data for workflow:', workflow);
    
    // Simple implementation - create a data blob and download it
    const workflowData = JSON.stringify(workflow, null, 2);
    const blob = new Blob([workflowData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow-${workflow.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Clean up the URL
    URL.revokeObjectURL(url);
    
    // Show confirmation
    alert(`Workflow ${workflow.id} data exported successfully`);
    setShowExportModal(false);
  };
  
  // Handler for cloning a workflow
  const handleCloneWorkflow = (workflow: Workflow) => {
    // Create a clone of the workflow with a new ID
    const clonedWorkflow: Workflow = {
      ...workflow,
      id: `wf-clone-${Date.now().toString().slice(-3)}`,
      status: 'pending',
      progress: 0,
      startTime: undefined,
      endTime: undefined,
      totalDuration: undefined,
      steps: workflow.steps.map(step => ({
        ...step,
        status: 'pending',
        startTime: undefined,
        endTime: undefined,
        duration: undefined,
        output: undefined,
        error: undefined
      })),
      metadata: {
        ...workflow.metadata,
        clonedFrom: workflow.id
      }
    };
    
    // Add the cloned workflow to the list
    setWorkflows(prev => [...prev, clonedWorkflow]);
    
    // Select the cloned workflow
    setSelectedWorkflow(clonedWorkflow);
    
    // Show confirmation
    alert(`Workflow ${workflow.id} cloned successfully as ${clonedWorkflow.id}`);
  };

  // Filter workflows by status and search query
  const filteredWorkflows = workflows
    .filter(wf => filterStatus === 'all' || wf.status === filterStatus)
    .filter(wf => 
      !searchQuery || 
      wf.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wf.id.toLowerCase().includes(searchQuery.toLowerCase())
    );

  return (
    <div className="workflows-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Workflow Management</h1>
          <p>View and manage agricultural workflows</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary"
            onClick={handleCreateWorkflow}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            Create Workflow
          </button>
          <button 
            className="btn-secondary"
            onClick={() => handleRefresh(true)}
            style={{ marginLeft: "10px" }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clipRule="evenodd" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <div className="filter-section">
        <div className="search-container">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="search-icon">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
          <input 
            type="text" 
            placeholder="Search workflows..." 
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-options">
          <div className="filter-group">
            <label>Status:</label>
            <select 
              className="filter-select" 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Type:</label>
            <select className="filter-select">
              <option value="all">All Types</option>
              <option value="irrigation">Irrigation</option>
              <option value="planning">Planning</option>
              <option value="monitoring">Monitoring</option>
            </select>
          </div>
        </div>
      </div>

      <div className="workflows-content">
        {/* Workflow List with scrollable container */}
        <div className="workflows-list">
          {filteredWorkflows.length === 0 ? (
            <div className="no-workflows-message" style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
              No workflows match your current filters.
            </div>
          ) : (
            filteredWorkflows.map(workflow => (
              <div 
                key={workflow.id}
                className={`workflow-card ${workflow.status} ${selectedWorkflow?.id === workflow.id ? 'selected' : ''}`}
                onClick={() => handleWorkflowSelect(workflow)}
              >
                <div className="workflow-card-header">
                  <div className="workflow-name-section">
                    <div className={`status-indicator ${workflow.status}`}></div>
                    <div className="workflow-title">
                      <h3>{workflow.name}</h3>
                      <p className="workflow-description">
                        {workflow.metadata?.description || `${workflow.status.charAt(0).toUpperCase() + workflow.status.slice(1)} agriculture workflow`}
                      </p>
                    </div>
                  </div>
                  <div className="workflow-actions">
                    <button className="action-btn" onClick={(e) => e.stopPropagation()}>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 3a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM10 8.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM11.5 15.5a1.5 1.5 0 10-3 0 1.5 1.5 0 003 0z" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div className="workflow-card-progress">
                  <div className="progress-bar">
                    <div 
                      className={`progress-fill ${workflow.status}`} 
                      style={{ width: `${Math.round(workflow.progress * 100)}%` }}
                    ></div>
                  </div>
                  <div className="progress-text">
                    {Math.round(workflow.progress * 100)}% Complete
                    {workflow.isIncreasing && workflow.status === 'running' && (
                      <span className="increasing-label">
                        ↑ Increasing
                      </span>
                    )}
                  </div>
                </div>

                <div className="workflow-metrics">
                  <div className="metric-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="metric-icon">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clipRule="evenodd" />
                    </svg>
                    <span className="metric-label">Started</span>
                    <span className="metric-value">{new Date(workflow.startTime).toLocaleTimeString()}</span>
                  </div>
                  <div className="metric-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="metric-icon">
                      <path fillRule="evenodd" d="M5.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 011.5 0V4h.25A2.75 2.75 0 0118 6.75v8.5A2.75 2.75 0 0115.25 18H4.75A2.75 2.75 0 012 15.25v-8.5A2.75 2.75 0 014.75 4H5V2.75A.75.75 0 015.75 2zm-1 5.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h10.5c.69 0 1.25-.56 1.25-1.25v-6.5c0-.69-.56-1.25-1.25-1.25H4.75z" clipRule="evenodd" />
                    </svg>
                    <span className="metric-label">Steps</span>
                    <span className="metric-value">{workflow.steps.filter(s => s.status === 'completed').length}/{workflow.steps.length}</span>
                  </div>
                  <div className="metric-item">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="metric-icon">
                      <path fillRule="evenodd" d="M2.24 6.8a.75.75 0 001.06-.04l1.95-2.1v8.59a.75.75 0 001.5 0V4.66l1.95 2.1a.75.75 0 101.06-1.06L6.53 2.44a.75.75 0 00-1.06 0L2.2 5.7a.75.75 0 00.04 1.1zm8 6.4a.75.75 0 00-.04 1.1l3.27 3.26a.75.75 0 001.06 0l3.27-3.26a.75.75 0 00-1.06-1.06l-1.95 1.95V4.75a.75.75 0 00-1.5 0v8.84l-1.95-1.95a.75.75 0 00-1.06.04z" clipRule="evenodd" />
                    </svg>
                    <span className="metric-label">Duration</span>
                    <span className="metric-value">{workflow.endTime ? 
                      Math.round((new Date(workflow.endTime).getTime() - new Date(workflow.startTime).getTime()) / (1000 * 60)) + 'm' : 
                      Math.round((new Date().getTime() - new Date(workflow.startTime).getTime()) / (1000 * 60)) + 'm'
                    }</span>
                  </div>
                </div>

                <div className="workflow-card-footer">
                  <div className="priority-badge">
                    Priority: {workflow.metadata?.priority || 'normal'}
                  </div>
                  <div className="workflow-id">{workflow.id}</div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Workflow Details Panel */}
        {selectedWorkflow && (
          <div className={`workflow-detail-panel ${showMobileDetails ? 'mobile-visible' : ''}`}>
            <div className="panel-header">
              <div className="panel-title">
                <div className={`status-indicator ${selectedWorkflow.status}`}></div>
                <h2>{selectedWorkflow.name}</h2>
              </div>
              <div className="panel-actions">
                <div className="status-badge">
                  {selectedWorkflow.status}
                </div>
                <button 
                  className="close-panel-btn"
                  onClick={() => setShowMobileDetails(false)}
                  aria-label="Close details panel"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Workflow Visualizer Component */}
            <div className="workflow-visualization">
              <WorkflowVisualizer 
                workflow={selectedWorkflow} 
                onStepClick={handleStepClick}
              />
            </div>

            {/* Execution Steps */}
            <div className="execution-steps">
              <h3>Execution Steps</h3>
              <div className="steps-list">
                {selectedWorkflow.steps.map((step, index) => (
                  <div 
                    key={step.id}
                    className={`step-item ${step.status}`}
                    onClick={() => handleStepClick(step)}
                  >
                    <div className="step-content">
                      <div className="step-header">
                        <strong className="step-name">{step.name}</strong>
                        <div className={`step-status ${step.status}`}>
                          {step.status.replace('-', ' ')}
                        </div>
                      </div>
                      
                      {step.agent && (
                        <div className="step-agent">
                          <span>🤖</span>
                          <small>Agent: {step.agent}</small>
                        </div>
                      )}
                      
                      {step.status !== 'pending' && (
                        <div className="step-time">
                          {step.startTime && <span>Started: {new Date(step.startTime).toLocaleTimeString()}</span>}
                          {step.duration && <span>Duration: {(step.duration / 60000).toFixed(1)} min</span>}
                        </div>
                      )}
                      
                      {step.status === 'completed' && step.output && (
                        <div className="step-output">
                          <div className="output-preview">
                            <span style={{ opacity: '0.7' }}>Output: </span>
                            {step.output?.split('\n')[0]}
                          </div>
                        </div>
                      )}
                      
                      {step.error && (
                        <div className="step-error">
                          <div className="error-message">{step.error}</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="workflow-actions-panel">
              <div className="action-buttons">
                {selectedWorkflow.status === 'running' && (
                  <button 
                    className="action-button danger"
                    onClick={() => {
                      // Simple implementation of pause functionality
                      const updatedWorkflows = workflows.map(w => {
                        if (w.id === selectedWorkflow.id) {
                          return { ...w, status: 'pending' };
                        }
                        return w;
                      });
                      setWorkflows(updatedWorkflows);
                      setSelectedWorkflow({...selectedWorkflow, status: 'pending'});
                      alert(`Workflow ${selectedWorkflow.id} paused`);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                    </svg>
                    Pause Workflow
                  </button>
                )}
                {selectedWorkflow.status === 'pending' && (
                  <button 
                    className="action-button primary"
                    onClick={() => {
                      // Simple implementation of start functionality
                      const updatedWorkflows = workflows.map(w => {
                        if (w.id === selectedWorkflow.id) {
                          return { 
                            ...w, 
                            status: 'running',
                            startTime: new Date().toISOString(),
                            progress: 0.01
                          };
                        }
                        return w;
                      });
                      setWorkflows(updatedWorkflows);
                      setSelectedWorkflow({
                        ...selectedWorkflow, 
                        status: 'running',
                        startTime: new Date().toISOString(),
                        progress: 0.01
                      });
                      alert(`Workflow ${selectedWorkflow.id} started`);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                    </svg>
                    Start Workflow
                  </button>
                )}
                {selectedWorkflow.status === 'failed' && (
                  <button 
                    className="action-button primary"
                    onClick={() => {
                      // Simple implementation of retry functionality
                      const updatedWorkflows = workflows.map(w => {
                        if (w.id === selectedWorkflow.id) {
                          // Find the failed step
                          const failedStepIndex = w.steps.findIndex(s => s.status === 'failed');
                          const updatedSteps = [...w.steps];
                          
                          if (failedStepIndex >= 0) {
                            updatedSteps[failedStepIndex] = {
                              ...updatedSteps[failedStepIndex],
                              status: 'in-progress',
                              error: undefined,
                              startTime: new Date().toISOString(),
                              endTime: undefined
                            };
                          }
                          
                          return { 
                            ...w, 
                            status: 'running',
                            endTime: undefined,
                            progress: Math.max(0.01, w.progress),
                            isIncreasing: true,
                            steps: updatedSteps
                          };
                        }
                        return w;
                      });
                      
                      setWorkflows(updatedWorkflows);
                      
                      // Update selected workflow
                      const updatedSelectedWorkflow = updatedWorkflows.find(w => w.id === selectedWorkflow.id);
                      if (updatedSelectedWorkflow) {
                        setSelectedWorkflow(updatedSelectedWorkflow);
                      }
                      
                      alert(`Workflow ${selectedWorkflow.id} retried`);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clipRule="evenodd" />
                    </svg>
                    Retry Workflow
                  </button>
                )}
                <button 
                  className="action-button"
                  onClick={() => selectedWorkflow && handleViewDetails(selectedWorkflow)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                  View Details
                </button>
                <button 
                  className="action-button"
                  onClick={() => selectedWorkflow && handleExportData(selectedWorkflow)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Export Data
                </button>
                <button 
                  className="action-button"
                  onClick={() => selectedWorkflow && handleCloneWorkflow(selectedWorkflow)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  Clone Workflow
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Mobile FAB for showing details */}
      {selectedWorkflow && !showMobileDetails && (
        <button 
          className="mobile-fab"
          onClick={() => setShowMobileDetails(true)}
          aria-label="Show workflow details"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span>View Details</span>
        </button>
      )}
      
      {/* View Details Modal */}
      <Modal 
        isOpen={showViewDetailsModal} 
        onClose={() => setShowViewDetailsModal(false)}
        title={`Workflow Details: ${selectedWorkflow?.name || ''}`}
      >
        {selectedWorkflow && (
          <div className="workflow-details-modal">
            <div className="details-section">
              <h3>General Information</h3>
              <p><strong>ID:</strong> {selectedWorkflow.id}</p>
              <p><strong>Type:</strong> {selectedWorkflow.type}</p>
              <p><strong>Status:</strong> <span className={`status-badge ${selectedWorkflow.status}`}>{selectedWorkflow.status}</span></p>
              <p><strong>Created by:</strong> {selectedWorkflow.createdBy}</p>
              <p><strong>Created At:</strong> {new Date(selectedWorkflow.createdAt).toLocaleString()}</p>
              {selectedWorkflow.startTime && (
                <p><strong>Start Time:</strong> {new Date(selectedWorkflow.startTime).toLocaleString()}</p>
              )}
              {selectedWorkflow.endTime && (
                <p><strong>End Time:</strong> {new Date(selectedWorkflow.endTime).toLocaleString()}</p>
              )}
              <p><strong>Progress:</strong> {Math.round(selectedWorkflow.progress * 100)}%</p>
            </div>
            
            <div className="details-section">
              <h3>Steps</h3>
              <div className="steps-list">
                {selectedWorkflow.steps.map((step, index) => (
                  <div key={index} className={`step-item ${step.status}`}>
                    <h4>{step.name}</h4>
                    <p><strong>Agent:</strong> {step.agent}</p>
                    <p><strong>Status:</strong> <span className={`status-badge ${step.status}`}>{step.status}</span></p>
                    {step.startTime && (
                      <p><strong>Start Time:</strong> {new Date(step.startTime).toLocaleString()}</p>
                    )}
                    {step.endTime && (
                      <p><strong>End Time:</strong> {new Date(step.endTime).toLocaleString()}</p>
                    )}
                    {step.error && (
                      <p className="error-message"><strong>Error:</strong> {step.error}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
      
      {/* Export Data Modal */}
      <Modal 
        isOpen={showExportModal} 
        onClose={() => setShowExportModal(false)}
        title="Export Workflow Data"
      >
        {selectedWorkflow && (
          <div className="export-modal">
            <p>Select the export format for workflow: <strong>{selectedWorkflow.name}</strong></p>
            <div className="export-options">
              <button 
                className="export-option"
                onClick={() => {
                  alert(`Workflow data exported as JSON: ${selectedWorkflow.name}.json`);
                  setShowExportModal(false);
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="option-icon">
                  <path fillRule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clipRule="evenodd" />
                  <path fillRule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clipRule="evenodd" />
                </svg>
                JSON Format
              </button>
              <button 
                className="export-option"
                onClick={() => {
                  alert(`Workflow data exported as CSV: ${selectedWorkflow.name}.csv`);
                  setShowExportModal(false);
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="option-icon">
                  <path fillRule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clipRule="evenodd" />
                  <path fillRule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clipRule="evenodd" />
                </svg>
                CSV Format
              </button>
              <button 
                className="export-option"
                onClick={() => {
                  alert(`Workflow data exported as PDF: ${selectedWorkflow.name}.pdf`);
                  setShowExportModal(false);
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="option-icon">
                  <path fillRule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clipRule="evenodd" />
                  <path fillRule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clipRule="evenodd" />
                </svg>
                PDF Format
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Mobile FAB for workflow details */}
      {selectedWorkflow && !showMobileDetails && (
        <button 
          className="mobile-fab"
          onClick={() => setShowMobileDetails(true)}
          aria-label="View workflow details"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
          </svg>
          View Details
        </button>
      )}
    </div>
  );
};

export default WorkflowsPage;
