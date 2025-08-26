import React from 'react'
import { motion } from 'framer-motion'
import { 
  Bot, 
  Zap, 
  TrendingUp,
  Shield,
  DollarSign,
  Droplets,
  BarChart3
} from 'lucide-react'
import { useAgentStore, Agent } from '../stores/agentStore'

interface AgentGridProps {
  detailed?: boolean
}

const AgentGrid: React.FC<AgentGridProps> = ({ detailed = false }) => {
  const { agents } = useAgentStore()

  const getAgentIcon = (type: Agent['type']) => {
    switch (type) {
      case 'router': return Bot
      case 'crop': return TrendingUp
      case 'pest': return Shield
      case 'market': return BarChart3
      case 'irrigation': return Droplets
      case 'finance': return DollarSign
      case 'data': return Zap
      default: return Bot
    }
  }

  const getAgentColor = (type: Agent['type']) => {
    switch (type) {
      case 'router': return 'text-blue-600 bg-blue-100'
      case 'crop': return 'text-green-600 bg-green-100'
      case 'pest': return 'text-red-600 bg-red-100'
      case 'market': return 'text-purple-600 bg-purple-100'
      case 'irrigation': return 'text-cyan-600 bg-cyan-100'
      case 'finance': return 'text-yellow-600 bg-yellow-100'
      case 'data': return 'text-indigo-600 bg-indigo-100'
      default: return 'text-secondary-600 bg-secondary-100'
    }
  }

  const getStatusBadge = (status: Agent['status']) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium"
    switch (status) {
      case 'idle':
        return `${baseClasses} agent-status-idle`
      case 'busy':
        return `${baseClasses} agent-status-busy`
      case 'completed':
        return `${baseClasses} agent-status-completed`
      case 'error':
        return `${baseClasses} agent-status-error`
      default:
        return `${baseClasses} agent-status-idle`
    }
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-secondary-900">Agent Network</h2>
        <div className="text-sm text-secondary-500">
          {agents.filter(a => a.status === 'busy').length} of {agents.length} active
        </div>
      </div>

      <div className={`grid gap-4 ${detailed ? 'grid-cols-1' : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'}`}>
        {agents.map((agent, index) => {
          const Icon = getAgentIcon(agent.type)
          const colorClasses = getAgentColor(agent.type)
          
          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-secondary-50 rounded-lg p-4 border border-secondary-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${colorClasses}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-medium text-secondary-900">{agent.name}</h3>
                    <p className="text-sm text-secondary-500 capitalize">{agent.type} Agent</p>
                  </div>
                </div>
                <span className={getStatusBadge(agent.status)}>
                  {agent.status}
                </span>
              </div>

              {agent.status === 'busy' && agent.progress > 0 && (
                <div className="mb-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-secondary-600">Progress</span>
                    <span className="text-secondary-900 font-medium">{agent.progress}%</span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <motion.div
                      className="bg-primary-600 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${agent.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              )}

              {agent.lastMessage && (
                <div className="mb-3">
                  <p className="text-sm text-secondary-600 bg-white rounded p-2 border">
                    {agent.lastMessage}
                  </p>
                </div>
              )}

              {detailed && (
                <>
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-secondary-700 mb-2">Capabilities</h4>
                    <div className="flex flex-wrap gap-1">
                      {agent.capabilities.map((capability, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-white text-xs text-secondary-600 rounded border"
                        >
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>

                  {agent.metrics && (
                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div>
                        <p className="text-sm font-medium text-secondary-900">{agent.metrics.tasksCompleted}</p>
                        <p className="text-xs text-secondary-500">Tasks</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-secondary-900">{agent.metrics.avgResponseTime}s</p>
                        <p className="text-xs text-secondary-500">Avg Time</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-secondary-900">{agent.metrics.successRate}%</p>
                        <p className="text-xs text-secondary-500">Success</p>
                      </div>
                    </div>
                  )}
                </>
              )}
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

export default AgentGrid
