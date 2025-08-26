/**
 * Dashboard Hook for Real-time Updates
 * Provides components with access to dashboard metrics and real-time updates
 */

import { useState, useEffect } from 'react';
import DashboardUpdateService from '../services/dashboardUpdateService';

interface DashboardMetrics {
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

interface DetailedStats {
  overview: {
    totalQueries: number;
    successRate: string;
    avgProcessingTime: string;
    fallbackRate: string;
  };
  agents: {
    totalActive: number;
    usage: Record<string, number>;
    mostUsed: string;
  };
  system: {
    health: 'healthy' | 'warning' | 'error';
    runningWorkflows: number;
    lastUpdate: string;
  };
}

export interface UseDashboardReturn {
  metrics: DashboardMetrics;
  stats: DashboardStats;
  detailed: DetailedStats;
  isConnected: boolean;
  updateMetrics: (agentId: string, processingTime: number, success: boolean, fallbackUsed?: string) => void;
  updateAgentStatus: (agentId: string, status: 'idle' | 'busy' | 'error') => void;
  startWorkflow: (workflowId: string) => void;
  completeWorkflow: (workflowId: string) => void;
  resetMetrics: () => void;
}

export const useDashboard = (): UseDashboardReturn => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalQueries: 0,
    successfulQueries: 0,
    failedQueries: 0,
    avgProcessingTime: 0,
    agentUsage: {},
    fallbackUsage: {}
  });

  const [stats, setStats] = useState<DashboardStats>({
    activeAgents: 5,
    runningWorkflows: 0,
    totalAnalyses: 0,
    systemHealth: 'healthy',
    lastUpdate: new Date().toISOString()
  });

  const [detailed, setDetailed] = useState<DetailedStats>({
    overview: {
      totalQueries: 0,
      successRate: '0.0',
      avgProcessingTime: '0',
      fallbackRate: '0.0'
    },
    agents: {
      totalActive: 5,
      usage: {},
      mostUsed: 'none'
    },
    system: {
      health: 'healthy',
      runningWorkflows: 0,
      lastUpdate: new Date().toISOString()
    }
  });

  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const service = DashboardUpdateService.getInstance();
    
    // Load initial data
    setMetrics(service.getMetrics());
    setStats(service.getDashboardStats());
    setDetailed(service.getDetailedStats());

    // Subscribe to updates
    const unsubscribe = service.subscribe((data) => {
      setMetrics(data.metrics);
      setStats(data.stats);
      setDetailed(data.detailed);
      setIsConnected(true);
    });

    // Check connection periodically
    const connectionCheck = setInterval(() => {
      try {
        // Simple check - if service is responding
        service.getMetrics();
        setIsConnected(true);
      } catch (error) {
        console.warn('Dashboard service connection issue:', error);
        setIsConnected(false);
      }
    }, 10000); // Check every 10 seconds

    return () => {
      unsubscribe();
      clearInterval(connectionCheck);
    };
  }, []);

  const updateMetrics = (agentId: string, processingTime: number, success: boolean, fallbackUsed?: string) => {
    const service = DashboardUpdateService.getInstance();
    service.updateQueryMetrics(agentId, processingTime, success, fallbackUsed);
  };

  const updateAgentStatus = (agentId: string, status: 'idle' | 'busy' | 'error') => {
    const service = DashboardUpdateService.getInstance();
    service.updateAgentStatus(agentId, status);
  };

  const startWorkflow = (workflowId: string) => {
    const service = DashboardUpdateService.getInstance();
    service.startWorkflow(workflowId);
  };

  const completeWorkflow = (workflowId: string) => {
    const service = DashboardUpdateService.getInstance();
    service.completeWorkflow(workflowId);
  };

  const resetMetrics = () => {
    const service = DashboardUpdateService.getInstance();
    service.resetMetrics();
  };

  return {
    metrics,
    stats,
    detailed,
    isConnected,
    updateMetrics,
    updateAgentStatus,
    startWorkflow,
    completeWorkflow,
    resetMetrics
  };
};

export default useDashboard;
