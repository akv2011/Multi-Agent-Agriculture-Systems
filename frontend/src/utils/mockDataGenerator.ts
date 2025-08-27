/**
 * Mock Data Generator for Dashboard
 * Generates random agent and workflow data for development and testing
 */

// Import and export the types we need
import type { Agent } from '../components/AgentList';
import type { Workflow, WorkflowStep } from '../components/WorkflowVisualizer';

// Agent Names Pool
const AGENT_NAMES = [
  'Crop Selection Agent',
  'Irrigation Agent',
  'Pest Management Agent',
  'Finance Policy Agent',
  'Market Timing Agent',
  'Harvest Planning Agent',
  'Input Materials Agent',
  'Weather Analysis Agent',
  'Soil Monitoring Agent',
  'Supply Chain Agent',
  'Data Processing Agent',
  'Farmer Communication Agent'
];

// Agent Status Types - Added recovery tracking
type AgentStatus = 'running' | 'idle' | 'busy' | 'error' | 'offline';
const AGENT_STATUSES: AgentStatus[] = ['running', 'idle', 'busy', 'error', 'offline'];

// Track agents in error state for automated recovery
const agentErrorStates = new Map<string, { errorStart: number; hasHighErrorRate: boolean }>();

/**
 * Get weighted agent status with reduced error probability and automated recovery
 */
const getAgentStatus = (agentId: string): AgentStatus => {
  const now = Date.now();
  
  // Check if this agent is in error recovery mode
  if (agentErrorStates.has(agentId)) {
    const errorState = agentErrorStates.get(agentId)!;
    const errorDuration = now - errorState.errorStart;
    
    // Auto-recover after 30-60 seconds for most agents
    const recoveryTime = errorState.hasHighErrorRate ? 60000 : 30000; // 1 minute for high error rate agent, 30s for others
    
    if (errorDuration > recoveryTime) {
      agentErrorStates.delete(agentId);
      console.log(`Agent ${agentId} recovered from error state`);
      return 'running'; // Recovered agent goes to running state
    } else {
      return 'error'; // Still in error state
    }
  }
  
  // Weighted status distribution (much lower error probability)
  const random = Math.random();
  
  // Special case for agent-002 - higher error rate (10% instead of 1%)
  if (agentId === 'agent-002') {
    if (random < 0.1) { // 10% error rate for agent-002
      agentErrorStates.set(agentId, { errorStart: now, hasHighErrorRate: true });
      return 'error';
    }
  } else {
    if (random < 0.01) { // 1% error rate for other agents
      agentErrorStates.set(agentId, { errorStart: now, hasHighErrorRate: false });
      return 'error';
    }
  }
  
  // Normal status distribution
  if (random < 0.4) return 'running';
  if (random < 0.7) return 'idle';
  if (random < 0.9) return 'busy';
  return 'offline';
};

// Task Descriptions Pool
const TASK_DESCRIPTIONS = [
  'Analyzing soil moisture levels',
  'Processing satellite imagery',
  'Calculating optimal irrigation timing',
  'Analyzing weather patterns',
  'Predicting pest outbreaks',
  'Recommending crop rotations',
  'Calculating market price trends',
  'Analyzing crop health indicators',
  'Processing farmer queries',
  'Generating harvest schedule',
  'Optimizing fertilizer application',
  'Monitoring crop growth stages',
  'Assessing drought risk factors',
  'Calculating yield estimates'
];

// Workflow Names Pool
const WORKFLOW_NAMES = [
  'Crop Planning Workflow',
  'Irrigation Optimization',
  'Pest Management System',
  'Market Analysis Pipeline',
  'Yield Prediction Workflow',
  'Weather Risk Assessment',
  'Farmer Recommendation System',
  'Soil Health Monitoring',
  'Supply Chain Optimization',
  'Harvest Planning Automation'
];

// Workflow Status Types
type WorkflowStatus = 'pending' | 'running' | 'completed' | 'failed';
const WORKFLOW_STATUSES: WorkflowStatus[] = ['pending', 'running', 'completed', 'failed'];

// Step Status Types
type StepStatus = 'pending' | 'in-progress' | 'completed' | 'failed';
const STEP_STATUSES: StepStatus[] = ['pending', 'in-progress', 'completed', 'failed'];

// Helper Functions
const randomInt = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const randomFloat = (min: number, max: number, decimals: number = 2): number => {
  const value = Math.random() * (max - min) + min;
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
};

const randomElement = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

const randomDate = (start: Date, end: Date): Date => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
};

const randomPastDate = (maxMinutesAgo: number): Date => {
  const now = new Date();
  const past = new Date(now.getTime() - randomInt(1, maxMinutesAgo) * 60 * 1000);
  return past;
};

/**
 * Generates a random agent with realistic agricultural context
 * @param id Optional ID to use (otherwise generates sequentially)
 */
export const generateRandomAgent = (id?: string): Agent => {
  const agentId = id || `agent-${String(randomInt(1, 999)).padStart(3, '0')}`;
  const status = getAgentStatus(agentId); // Use new status function with recovery logic
  const lastActivityMinutes = randomInt(1, 30);
  const lastActivity = new Date(Date.now() - lastActivityMinutes * 60 * 1000).toISOString();
  
  return {
    id: agentId,
    name: randomElement(AGENT_NAMES),
    status,
    lastActivity,
    // Only include current task for certain statuses
    ...(status === 'running' || status === 'busy' || status === 'error' 
        ? { currentTask: randomElement(TASK_DESCRIPTIONS) } 
        : {}),
    metrics: {
      tasksCompleted: randomInt(0, 100),
      averageExecutionTime: randomFloat(0.5, 10),
      successRate: status === 'error' ? randomFloat(0.6, 0.9) : randomFloat(0.85, 1.0)
    }
  };
};

/**
 * Generates a set of random agents
 * @param count Number of agents to generate
 */
export const generateRandomAgents = (count: number): Agent[] => {
  return Array.from({ length: count }, (_, i) => 
    generateRandomAgent(`agent-${String(i + 1).padStart(3, '0')}`)
  );
};

/**
 * Generates a workflow step with realistic properties
 */
const generateWorkflowStep = (
  stepId: number, 
  totalSteps: number,
  agents: Agent[],
  workflowStartTime: Date
): WorkflowStep => {
  // Determine status based on step position
  let status: StepStatus;
  const stepsCompleted = randomInt(0, totalSteps - 1);
  
  if (stepId < stepsCompleted) {
    status = 'completed';
  } else if (stepId === stepsCompleted) {
    status = 'in-progress';
  } else {
    status = 'pending';
  }

  // Assign a random agent to the step
  const agent = randomElement(agents).id;

  // Calculate timing for completed steps
  const stepDuration = status === 'completed' ? randomInt(30, 120) * 1000 : undefined;
  const startTime = status !== 'pending' 
    ? new Date(workflowStartTime.getTime() + (stepId * 2 * 60 * 1000)).toISOString() 
    : undefined;
  const endTime = status === 'completed' && startTime
    ? new Date(new Date(startTime).getTime() + (stepDuration || 0)).toISOString()
    : undefined;

  // Generate step data
  return {
    id: `step-${stepId + 1}`,
    name: `Step ${stepId + 1}: ${randomElement(TASK_DESCRIPTIONS)}`,
    status,
    startTime,
    endTime,
    duration: stepDuration,
    output: status === 'completed' ? `Completed processing with ${randomInt(80, 99)}% confidence.\nProcessed ${randomInt(100, 1000)} data points.` : undefined,
    agent
  };
};

/**
 * Generates a random workflow with steps
 */
export const generateRandomWorkflow = (agents: Agent[]): Workflow => {
  const workflowId = `workflow-${String(randomInt(1, 999)).padStart(3, '0')}`;
  const numSteps = randomInt(3, 7);
  const startTime = randomPastDate(60); // Started within last hour
  const totalDuration = randomInt(5, 30) * 60 * 1000; // 5-30 minutes
  
  // Generate steps for this workflow
  const steps = Array.from({ length: numSteps }, (_, i) => 
    generateWorkflowStep(i, numSteps, agents, startTime)
  );
  
  // Calculate progress based on completed steps
  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const calculatedProgress = completedSteps / numSteps;

  return {
    id: workflowId,
    name: randomElement(WORKFLOW_NAMES),
    status: randomElement(WORKFLOW_STATUSES) as Workflow['status'],
    progress: calculatedProgress,
    startTime: startTime.toISOString(),
    totalDuration,
    steps,
    metadata: {
      priority: randomElement(['high', 'medium', 'low']),
      source: randomElement(['satellite_data', 'weather_api', 'farmer_query', 'scheduled_task']),
      estimated_completion: new Date(startTime.getTime() + totalDuration).toISOString()
    }
  };
};

/**
 * Generates multiple random workflows
 */
export const generateRandomWorkflows = (count: number, agents: Agent[]): Workflow[] => {
  return Array.from({ length: count }, () => generateRandomWorkflow(agents));
};

/**
 * Returns a subset of workflows that are considered "active"
 */
export const getActiveWorkflows = (workflows: Workflow[]): Workflow[] => {
  return workflows.filter(workflow => workflow.status === 'running');
};

/**
 * Generate an entirely new set of random data for the dashboard
 */
export const generateDashboardData = (agentCount: number = 8, workflowCount: number = 3) => {
  const agents = generateRandomAgents(agentCount);
  const workflows = generateRandomWorkflows(workflowCount, agents);
  const activeWorkflows = getActiveWorkflows(workflows);

  return {
    agents,
    workflows,
    activeWorkflows
  };
};
