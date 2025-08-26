import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Bot, 
  Activity, 
  MessageSquare, 
  Network,
  BarChart3,
  Settings,
  Zap,
  Users,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Play,
  Pause
} from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'
import AgentGrid from './AgentGrid'
import WorkflowVisualization from './WorkflowVisualization'
import QueryInterface from './QueryInterface'
import SystemMetrics from './SystemMetrics'
import WorkflowHistory from './WorkflowHistory'

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'workflows' | 'metrics'>('overview')
  const { 
    agents, 
    currentWorkflow, 
    isConnected, 
    setConnectionStatus,
    resetAgents
  } = useAgentStore()

  // Simulate WebSocket connection
  useEffect(() => {
    const timer = setTimeout(() => setConnectionStatus(true), 1000)
    return () => clearTimeout(timer)
  }, [setConnectionStatus])

  const totalAgents = agents.length
  const activeAgents = agents.filter(a => a.status === 'busy').length
  const completedTasks = agents.reduce((sum, agent) => sum + (agent.metrics?.tasksCompleted || 0), 0)
  const avgSuccessRate = agents.reduce((sum, agent) => sum + (agent.metrics?.successRate || 0), 0) / agents.length

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'agents', label: 'Agents', icon: Bot },
    { id: 'workflows', label: 'Workflows', icon: Network },
    { id: 'metrics', label: 'Metrics', icon: TrendingUp }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 to-secondary-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <Bot className="h-8 w-8 text-primary-600" />
                  <div className="absolute -top-1 -right-1 h-3 w-3 bg-primary-500 rounded-full animate-pulse" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-secondary-900">AgentWeaver</h1>
                  <p className="text-sm text-secondary-500">Multi-Agent Agriculture System</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-secondary-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-secondary-600">
                <Users className="h-4 w-4" />
                <span>{activeAgents}/{totalAgents} Active</span>
              </div>
              
              <button
                onClick={resetAgents}
                className="flex items-center space-x-1 px-3 py-1 text-sm bg-secondary-100 hover:bg-secondary-200 rounded-lg transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span>Reset</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-secondary-600">Total Agents</p>
                <p className="text-2xl font-bold text-secondary-900">{totalAgents}</p>
              </div>
              <Bot className="h-8 w-8 text-primary-600" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-secondary-600">Active Agents</p>
                <p className="text-2xl font-bold text-secondary-900">{activeAgents}</p>
              </div>
              <Activity className="h-8 w-8 text-yellow-600" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-secondary-600">Tasks Completed</p>
                <p className="text-2xl font-bold text-secondary-900">{completedTasks}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-secondary-600">Success Rate</p>
                <p className="text-2xl font-bold text-secondary-900">{avgSuccessRate.toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </motion.div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-secondary-600 hover:bg-secondary-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8">
            <AnimatePresence mode="wait">
              {activeTab === 'overview' && (
                <motion.div
                  key="overview"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <AgentGrid />
                  {currentWorkflow && <WorkflowVisualization workflow={currentWorkflow} />}
                </motion.div>
              )}

              {activeTab === 'agents' && (
                <motion.div
                  key="agents"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <AgentGrid detailed />
                </motion.div>
              )}

              {activeTab === 'workflows' && (
                <motion.div
                  key="workflows"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <WorkflowHistory />
                </motion.div>
              )}

              {activeTab === 'metrics' && (
                <motion.div
                  key="metrics"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <SystemMetrics />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="lg:col-span-4">
            <QueryInterface />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
