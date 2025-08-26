import { useAgentStore } from '../stores/agentStore'

export class WorkflowSimulationService {
  private static instance: WorkflowSimulationService
  private intervalId?: NodeJS.Timeout
  private store = useAgentStore.getState()

  static getInstance(): WorkflowSimulationService {
    if (!WorkflowSimulationService.instance) {
      WorkflowSimulationService.instance = new WorkflowSimulationService()
    }
    return WorkflowSimulationService.instance
  }

  startSimulation() {
    if (this.intervalId) {
      this.stopSimulation()
    }

    this.intervalId = setInterval(() => {
      this.simulateAgentActivity()
    }, 3000)
  }

  stopSimulation() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = undefined
    }
  }

  private simulateAgentActivity() {
    const state = useAgentStore.getState()
    const { agents, updateAgent } = state

    // Randomly select an agent to update
    const randomAgent = agents[Math.floor(Math.random() * agents.length)]
    
    if (randomAgent.status === 'idle') {
      // Start a new task
      updateAgent(randomAgent.id, {
        status: 'busy',
        progress: 10,
        lastMessage: this.getRandomTask(randomAgent.type)
      })
    } else if (randomAgent.status === 'busy') {
      const newProgress = Math.min(randomAgent.progress + 20, 100)
      
      if (newProgress >= 100) {
        // Complete the task
        updateAgent(randomAgent.id, {
          status: 'completed',
          progress: 100,
          lastMessage: 'Task completed successfully'
        })

        // Reset to idle after a short delay
        setTimeout(() => {
          updateAgent(randomAgent.id, {
            status: 'idle',
            progress: 0,
            lastMessage: undefined
          })
        }, 2000)
      } else {
        // Update progress
        updateAgent(randomAgent.id, {
          progress: newProgress,
          lastMessage: this.getProgressMessage(randomAgent.type, newProgress)
        })
      }
    } else if (randomAgent.status === 'completed') {
      // Reset to idle
      updateAgent(randomAgent.id, {
        status: 'idle',
        progress: 0,
        lastMessage: undefined
      })
    }
  }

  private getRandomTask(agentType: string): string {
    const tasks = {
      router: [
        'Analyzing query intent...',
        'Classifying user request...',
        'Routing to appropriate agents...'
      ],
      crop: [
        'Analyzing soil conditions...',
        'Calculating yield predictions...',
        'Recommending crop varieties...'
      ],
      pest: [
        'Identifying pest patterns...',
        'Analyzing crop damage...',
        'Recommending treatments...'
      ],
      market: [
        'Fetching price trends...',
        'Analyzing market conditions...',
        'Forecasting price movements...'
      ],
      irrigation: [
        'Calculating water requirements...',
        'Analyzing weather patterns...',
        'Optimizing irrigation schedule...'
      ],
      finance: [
        'Checking loan eligibility...',
        'Analyzing subsidy options...',
        'Calculating financial projections...'
      ],
      data: [
        'Processing satellite imagery...',
        'Fetching weather data...',
        'Updating sensor readings...'
      ]
    }

    const agentTasks = tasks[agentType as keyof typeof tasks] || ['Processing request...']
    return agentTasks[Math.floor(Math.random() * agentTasks.length)]
  }

  private getProgressMessage(agentType: string, progress: number): string {
    if (progress < 30) {
      return 'Initializing task...'
    } else if (progress < 60) {
      return 'Processing data...'
    } else if (progress < 90) {
      return 'Generating results...'
    } else {
      return 'Finalizing output...'
    }
  }

  simulateWorkflow(query: string) {
    const { createWorkflow, updateWorkflow, updateWorkflowStep, agents } = useAgentStore.getState()
    
    // Create workflow
    createWorkflow(query)
    
    // Simulate workflow execution
    setTimeout(() => {
      const currentWorkflow = useAgentStore.getState().currentWorkflow
      if (!currentWorkflow) return

      // Start the workflow
      updateWorkflow(currentWorkflow.id, {
        status: 'running',
        startTime: new Date()
      })

      // Determine which agents to involve based on query
      const involvedAgents = this.determineAgentsForQuery(query)
      
      // Add steps for each agent
      const steps = involvedAgents.map((agentType, index) => ({
        id: `step-${index + 1}`,
        agentId: agentType,
        name: this.getStepName(agentType),
        status: index === 0 ? 'running' : 'pending'
      }))

      updateWorkflow(currentWorkflow.id, { steps })

      // Execute steps sequentially
      this.executeWorkflowSteps(currentWorkflow.id, steps, 0)
    }, 500)
  }

  private determineAgentsForQuery(query: string): string[] {
    query = query.toLowerCase()
    const agents = []

    // Always start with router
    agents.push('router')

    // Determine relevant agents based on query keywords
    if (query.includes('crop') || query.includes('plant') || query.includes('seed')) {
      agents.push('crop')
    }
    if (query.includes('pest') || query.includes('disease') || query.includes('insect')) {
      agents.push('pest')
    }
    if (query.includes('water') || query.includes('irrigat') || query.includes('rain')) {
      agents.push('irrigation')
    }
    if (query.includes('price') || query.includes('market') || query.includes('sell')) {
      agents.push('market')
    }
    if (query.includes('loan') || query.includes('finance') || query.includes('subsidy')) {
      agents.push('finance')
    }
    
    // Always include data layer for comprehensive analysis
    agents.push('data')

    return agents
  }

  private getStepName(agentType: string): string {
    const stepNames = {
      router: 'Query Analysis & Routing',
      crop: 'Crop Analysis & Recommendations',
      pest: 'Pest Detection & Treatment',
      market: 'Market Analysis & Pricing',
      irrigation: 'Irrigation Optimization',
      finance: 'Financial Analysis',
      data: 'Data Integration & Processing'
    }

    return stepNames[agentType as keyof typeof stepNames] || 'Processing'
  }

  private executeWorkflowSteps(workflowId: string, steps: any[], currentIndex: number) {
    if (currentIndex >= steps.length) {
      // Complete the workflow
      const { updateWorkflow } = useAgentStore.getState()
      updateWorkflow(workflowId, {
        status: 'completed',
        endTime: new Date()
      })
      return
    }

    const currentStep = steps[currentIndex]
    const { updateWorkflowStep } = useAgentStore.getState()

    // Start current step
    updateWorkflowStep(workflowId, currentStep.id, {
      status: 'running',
      startTime: new Date()
    })

    // Simulate step execution time (2-5 seconds)
    const executionTime = Math.random() * 3000 + 2000
    
    setTimeout(() => {
      // Complete current step
      updateWorkflowStep(workflowId, currentStep.id, {
        status: 'completed',
        endTime: new Date()
      })

      // Start next step
      if (currentIndex + 1 < steps.length) {
        updateWorkflowStep(workflowId, steps[currentIndex + 1].id, {
          status: 'running'
        })
      }

      // Continue with next step
      this.executeWorkflowSteps(workflowId, steps, currentIndex + 1)
    }, executionTime)
  }
}

export const workflowSimulation = WorkflowSimulationService.getInstance()
