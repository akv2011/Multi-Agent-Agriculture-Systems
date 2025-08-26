/**
 * Dashboard Update Service
 * Handles real-time updates to dashboard metrics and statistics
 */

interface QueryMetrics {
  totalQueries: number;
  successfulQueries: number;
  failedQueries: number;
  avgProcessingTime: number;
  agentUsage: Record<string, number>;
  fallbackUsage: Record<string, number>;
}

interface DashboardStats {
  activeAgents: number;
  runningWorkflows: number;
  totalAnalyses: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  lastUpdate: string;
}

interface DashboardUpdateData {
  metrics: QueryMetrics;
  stats: DashboardStats;
  detailed: ReturnType<DashboardUpdateService['getDetailedStats']>;
}

interface AgentStatus {
  status: 'idle' | 'busy' | 'error';
  timestamp: string;
}

class DashboardUpdateService {
  private static instance: DashboardUpdateService;
  private metrics: QueryMetrics;
  private dashboardStats: DashboardStats;
  private subscribers: Array<(data: DashboardUpdateData) => void> = [];

  private constructor() {
    this.metrics = {
      totalQueries: 0,
      successfulQueries: 0,
      failedQueries: 0,
      avgProcessingTime: 0,
      agentUsage: {},
      fallbackUsage: {}
    };

    this.dashboardStats = {
      activeAgents: 5,
      runningWorkflows: 0,
      totalAnalyses: 0,
      systemHealth: 'healthy',
      lastUpdate: new Date().toISOString()
    };

    // Load existing metrics from localStorage
    this.loadMetricsFromStorage();
  }

  public static getInstance(): DashboardUpdateService {
    if (!DashboardUpdateService.instance) {
      DashboardUpdateService.instance = new DashboardUpdateService();
    }
    return DashboardUpdateService.instance;
  }

  private loadMetricsFromStorage(): void {
    try {
      const stored = localStorage.getItem('agriSystemMetrics');
      if (stored) {
        const parsedMetrics = JSON.parse(stored);
        this.metrics = { ...this.metrics, ...parsedMetrics };
      }

      const storedDashboard = localStorage.getItem('agriDashboardStats');
      if (storedDashboard) {
        const parsedDashboard = JSON.parse(storedDashboard);
        this.dashboardStats = { ...this.dashboardStats, ...parsedDashboard };
      }
    } catch (error) {
      console.warn('Failed to load metrics from storage:', error);
    }
  }

  private saveMetricsToStorage(): void {
    try {
      localStorage.setItem('agriSystemMetrics', JSON.stringify(this.metrics));
      localStorage.setItem('agriDashboardStats', JSON.stringify(this.dashboardStats));
    } catch (error) {
      console.warn('Failed to save metrics to storage:', error);
    }
  }

  public updateQueryMetrics(
    agentId: string, 
    processingTime: number, 
    success: boolean, 
    fallbackUsed?: string
  ): void {
    // Update basic metrics
    this.metrics.totalQueries++;
    
    if (success) {
      this.metrics.successfulQueries++;
    } else {
      this.metrics.failedQueries++;
    }

    // Update average processing time
    const totalTime = this.metrics.avgProcessingTime * (this.metrics.totalQueries - 1) + processingTime;
    this.metrics.avgProcessingTime = totalTime / this.metrics.totalQueries;

    // Update agent usage
    if (!this.metrics.agentUsage[agentId]) {
      this.metrics.agentUsage[agentId] = 0;
    }
    this.metrics.agentUsage[agentId]++;

    // Update fallback usage
    const fallback = fallbackUsed || 'none';
    if (!this.metrics.fallbackUsage[fallback]) {
      this.metrics.fallbackUsage[fallback] = 0;
    }
    this.metrics.fallbackUsage[fallback]++;

    // Update dashboard stats
    this.dashboardStats.totalAnalyses++;
    this.dashboardStats.lastUpdate = new Date().toISOString();
    
    // Update system health based on success rate
    const successRate = this.metrics.successfulQueries / this.metrics.totalQueries;
    if (successRate >= 0.9) {
      this.dashboardStats.systemHealth = 'healthy';
    } else if (successRate >= 0.7) {
      this.dashboardStats.systemHealth = 'warning';
    } else {
      this.dashboardStats.systemHealth = 'error';
    }

    // Save to storage
    this.saveMetricsToStorage();

    // Notify subscribers
    this.notifySubscribers();
  }

  public updateAgentStatus(agentId: string, status: 'idle' | 'busy' | 'error'): void {
    // This could be enhanced to track individual agent statuses
    // For now, we'll simulate active agent count
    const timestamp = new Date().toISOString();
    
    // Store agent status update
    const agentStatuses = JSON.parse(localStorage.getItem('agentStatuses') || '{}');
    agentStatuses[agentId] = { status, timestamp };
    localStorage.setItem('agentStatuses', JSON.stringify(agentStatuses));

    // Update active agents count
    const agentStatusValues = Object.values(agentStatuses) as AgentStatus[];
    const activeCount = agentStatusValues.filter(
      (agent: AgentStatus) => agent.status === 'busy' || agent.status === 'idle'
    ).length;
    
    this.dashboardStats.activeAgents = Math.max(activeCount, 4); // Minimum 4 agents
    this.dashboardStats.lastUpdate = timestamp;
    
    this.saveMetricsToStorage();
    this.notifySubscribers();
  }

  public startWorkflow(workflowId: string): void {
    this.dashboardStats.runningWorkflows++;
    this.dashboardStats.lastUpdate = new Date().toISOString();
    
    // Store workflow info
    const workflows = JSON.parse(localStorage.getItem('activeWorkflows') || '{}');
    workflows[workflowId] = {
      id: workflowId,
      startTime: new Date().toISOString(),
      status: 'running'
    };
    localStorage.setItem('activeWorkflows', JSON.stringify(workflows));
    
    this.saveMetricsToStorage();
    this.notifySubscribers();
  }

  public completeWorkflow(workflowId: string): void {
    this.dashboardStats.runningWorkflows = Math.max(0, this.dashboardStats.runningWorkflows - 1);
    this.dashboardStats.lastUpdate = new Date().toISOString();
    
    // Update workflow info
    const workflows = JSON.parse(localStorage.getItem('activeWorkflows') || '{}');
    if (workflows[workflowId]) {
      workflows[workflowId].status = 'completed';
      workflows[workflowId].endTime = new Date().toISOString();
    }
    localStorage.setItem('activeWorkflows', JSON.stringify(workflows));
    
    this.saveMetricsToStorage();
    this.notifySubscribers();
  }

  public getMetrics(): QueryMetrics {
    return { ...this.metrics };
  }

  public getDashboardStats(): DashboardStats {
    return { ...this.dashboardStats };
  }

  public getDetailedStats() {
    const successRate = this.metrics.totalQueries > 0 
      ? (this.metrics.successfulQueries / this.metrics.totalQueries) * 100 
      : 0;

    const fallbackRate = this.metrics.totalQueries > 0
      ? ((this.metrics.fallbackUsage['ground_search'] || 0) / this.metrics.totalQueries) * 100
      : 0;

    return {
      overview: {
        totalQueries: this.metrics.totalQueries,
        successRate: successRate.toFixed(1),
        avgProcessingTime: this.metrics.avgProcessingTime.toFixed(0),
        fallbackRate: fallbackRate.toFixed(1)
      },
      agents: {
        totalActive: this.dashboardStats.activeAgents,
        usage: this.metrics.agentUsage,
        mostUsed: this.getMostUsedAgent()
      },
      system: {
        health: this.dashboardStats.systemHealth,
        runningWorkflows: this.dashboardStats.runningWorkflows,
        lastUpdate: this.dashboardStats.lastUpdate
      }
    };
  }

  private getMostUsedAgent(): string {
    let maxUsage = 0;
    let mostUsed = 'none';
    
    for (const [agent, usage] of Object.entries(this.metrics.agentUsage)) {
      if (usage > maxUsage) {
        maxUsage = usage;
        mostUsed = agent;
      }
    }
    
    return mostUsed;
  }

  public subscribe(callback: (data: DashboardUpdateData) => void): () => void {
    this.subscribers.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.subscribers.indexOf(callback);
      if (index > -1) {
        this.subscribers.splice(index, 1);
      }
    };
  }

  private notifySubscribers(): void {
    const data = {
      metrics: this.getMetrics(),
      stats: this.getDashboardStats(),
      detailed: this.getDetailedStats()
    };

    this.subscribers.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('Error notifying dashboard subscriber:', error);
      }
    });
  }

  // Method to simulate real-time updates for demo purposes
  public simulateRealtimeUpdate(): void {
    // Simulate some background activity
    const agents = ['disease_identification', 'crop_recommendation', 'irrigation_scheduling', 'market_analysis'];
    const randomAgent = agents[Math.floor(Math.random() * agents.length)];
    
    // Simulate agent status change
    this.updateAgentStatus(randomAgent, Math.random() > 0.7 ? 'busy' : 'idle');
    
    // Occasionally simulate a background query
    if (Math.random() > 0.8) {
      this.updateQueryMetrics(
        randomAgent,
        800 + Math.random() * 1200, // Random processing time
        Math.random() > 0.1, // 90% success rate
        Math.random() > 0.8 ? 'ground_search' : undefined
      );
    }
  }

  // Method to reset metrics (for testing)
  public resetMetrics(): void {
    this.metrics = {
      totalQueries: 0,
      successfulQueries: 0,
      failedQueries: 0,
      avgProcessingTime: 0,
      agentUsage: {},
      fallbackUsage: {}
    };

    this.dashboardStats = {
      activeAgents: 5,
      runningWorkflows: 0,
      totalAnalyses: 0,
      systemHealth: 'healthy',
      lastUpdate: new Date().toISOString()
    };

    localStorage.removeItem('agriSystemMetrics');
    localStorage.removeItem('agriDashboardStats');
    localStorage.removeItem('agentStatuses');
    localStorage.removeItem('activeWorkflows');

    this.notifySubscribers();
  }
}

export default DashboardUpdateService;
