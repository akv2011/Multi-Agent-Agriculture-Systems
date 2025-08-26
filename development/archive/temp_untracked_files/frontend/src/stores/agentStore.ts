import { create } from 'zustand'

export interface Agent {
  id: string
  name: string
  type: 'router' | 'crop' | 'pest' | 'market' | 'irrigation' | 'finance' | 'data'
  status: 'idle' | 'busy' | 'completed' | 'error'
  progress: number
  lastMessage?: string
  capabilities: string[]
  metrics?: {
    tasksCompleted: number
    avgResponseTime: number
    successRate: number
  }
}

export interface WorkflowStep {
  id: string
  agentId: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  startTime?: Date
  endTime?: Date
  input?: any
  output?: any
}

export interface AgentWorkflow {
  id: string
  name: string
  description: string
  steps: WorkflowStep[]
  status: 'idle' | 'running' | 'completed' | 'failed'
  startTime?: Date
  endTime?: Date
  query?: string
}

interface AgentStore {
  agents: Agent[]
  workflows: AgentWorkflow[]
  currentWorkflow?: AgentWorkflow
  isConnected: boolean
  
  // Actions
  updateAgent: (agentId: string, updates: Partial<Agent>) => void
  createWorkflow: (query: string) => void
  updateWorkflow: (workflowId: string, updates: Partial<AgentWorkflow>) => void
  updateWorkflowStep: (workflowId: string, stepId: string, updates: Partial<WorkflowStep>) => void
  setConnectionStatus: (connected: boolean) => void
  resetAgents: () => void
}

// Mock initial agents based on the agriculture system
const initialAgents: Agent[] = [
  {
    id: 'router',
    name: 'Router Agent',
    type: 'router',
    status: 'idle',
    progress: 0,
    capabilities: ['Query Classification', 'Intent Detection', 'Agent Routing'],
    metrics: { tasksCompleted: 156, avgResponseTime: 1.2, successRate: 98.5 }
  },
  {
    id: 'crop',
    name: 'Crop Selection Agent',
    type: 'crop',
    status: 'idle',
    progress: 0,
    capabilities: ['Crop Recommendation', 'Yield Prediction', 'Soil Analysis'],
    metrics: { tasksCompleted: 89, avgResponseTime: 3.4, successRate: 94.2 }
  },
  {
    id: 'pest',
    name: 'Pest Forecaster Agent',
    type: 'pest',
    status: 'idle',
    progress: 0,
    capabilities: ['Pest Detection', 'Disease Identification', 'Treatment Recommendation'],
    metrics: { tasksCompleted: 67, avgResponseTime: 2.8, successRate: 91.7 }
  },
  {
    id: 'market',
    name: 'Market Timing Agent',
    type: 'market',
    status: 'idle',
    progress: 0,
    capabilities: ['Price Forecasting', 'Market Analysis', 'Selling Recommendations'],
    metrics: { tasksCompleted: 134, avgResponseTime: 2.1, successRate: 96.3 }
  },
  {
    id: 'irrigation',
    name: 'Irrigation Agent',
    type: 'irrigation',
    status: 'idle',
    progress: 0,
    capabilities: ['Water Scheduling', 'ET Calculation', 'Weather Integration'],
    metrics: { tasksCompleted: 98, avgResponseTime: 1.8, successRate: 97.1 }
  },
  {
    id: 'finance',
    name: 'Finance & Policy Agent',
    type: 'finance',
    status: 'idle',
    progress: 0,
    capabilities: ['Loan Eligibility', 'Subsidy Information', 'Financial Planning'],
    metrics: { tasksCompleted: 45, avgResponseTime: 4.2, successRate: 88.9 }
  },
  {
    id: 'data',
    name: 'Data Layer Agent',
    type: 'data',
    status: 'idle',
    progress: 0,
    capabilities: ['Satellite Data', 'Weather Data', 'Soil Monitoring'],
    metrics: { tasksCompleted: 203, avgResponseTime: 0.8, successRate: 99.1 }
  }
]

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: initialAgents,
  workflows: [],
  currentWorkflow: undefined,
  isConnected: false,

  updateAgent: (agentId, updates) => 
    set((state) => ({
      agents: state.agents.map(agent => 
        agent.id === agentId ? { ...agent, ...updates } : agent
      )
    })),

  createWorkflow: (query) => {
    const workflowId = `workflow-${Date.now()}`
    const workflow: AgentWorkflow = {
      id: workflowId,
      name: 'Multi-Agent Query Processing',
      description: 'Processing agricultural query through specialized agents',
      query,
      status: 'idle',
      steps: [
        {
          id: 'step-1',
          agentId: 'router',
          name: 'Query Analysis & Routing',
          status: 'pending'
        }
      ]
    }
    
    set((state) => ({
      workflows: [workflow, ...state.workflows.slice(0, 4)], // Keep only last 5
      currentWorkflow: workflow
    }))
  },

  updateWorkflow: (workflowId, updates) =>
    set((state) => ({
      workflows: state.workflows.map(w => 
        w.id === workflowId ? { ...w, ...updates } : w
      ),
      currentWorkflow: state.currentWorkflow?.id === workflowId 
        ? { ...state.currentWorkflow, ...updates } 
        : state.currentWorkflow
    })),

  updateWorkflowStep: (workflowId, stepId, updates) =>
    set((state) => ({
      workflows: state.workflows.map(w => 
        w.id === workflowId 
          ? { 
              ...w, 
              steps: w.steps.map(s => 
                s.id === stepId ? { ...s, ...updates } : s
              ) 
            }
          : w
      ),
      currentWorkflow: state.currentWorkflow?.id === workflowId
        ? {
            ...state.currentWorkflow,
            steps: state.currentWorkflow.steps.map(s =>
              s.id === stepId ? { ...s, ...updates } : s
            )
          }
        : state.currentWorkflow
    })),

  setConnectionStatus: (connected) => set({ isConnected: connected }),

  resetAgents: () => 
    set({ 
      agents: initialAgents.map(agent => ({ ...agent, status: 'idle', progress: 0 }))
    })
}))
