import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Clock, CheckCircle, AlertCircle, Play } from 'lucide-react'
import { AgentWorkflow } from '../stores/agentStore'

interface WorkflowVisualizationProps {
  workflow: AgentWorkflow
}

const WorkflowVisualization: React.FC<WorkflowVisualizationProps> = ({ workflow }) => {
  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'running':
        return <Play className="h-4 w-4 text-blue-600 animate-pulse" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-secondary-400" />
    }
  }

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50'
      case 'running':
        return 'border-blue-200 bg-blue-50'
      case 'failed':
        return 'border-red-200 bg-red-50'
      default:
        return 'border-secondary-200 bg-secondary-50'
    }
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-secondary-900">Workflow Execution</h2>
        <div className="flex items-center space-x-2 text-sm text-secondary-500">
          <span>{workflow.steps.filter(s => s.status === 'completed').length} of {workflow.steps.length} completed</span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Query Display */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-primary-900 mb-2">Query</h3>
          <p className="text-primary-800">"{workflow.query}"</p>
        </div>

        {/* Workflow Steps */}
        <div className="relative">
          {workflow.steps.map((step, index) => (
            <div key={step.id} className="relative">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center space-x-4 p-4 rounded-lg border ${getStepColor(step.status)}`}
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-current">
                  {getStepIcon(step.status)}
                </div>
                
                <div className="flex-1">
                  <h4 className="font-medium text-secondary-900">{step.name}</h4>
                  <p className="text-sm text-secondary-600">Agent: {step.agentId}</p>
                  {step.status === 'running' && (
                    <div className="mt-2">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-white rounded-full h-2">
                          <motion.div
                            className="bg-blue-600 h-2 rounded-full"
                            initial={{ width: '0%' }}
                            animate={{ width: '60%' }}
                            transition={{ duration: 2, repeat: Infinity, repeatType: 'reverse' }}
                          />
                        </div>
                        <span className="text-xs text-secondary-500">Processing...</span>
                      </div>
                    </div>
                  )}
                  {(step.startTime || step.endTime) && (
                    <div className="flex items-center space-x-4 mt-2 text-xs text-secondary-500">
                      {step.startTime && <span>Started: {step.startTime.toLocaleTimeString()}</span>}
                      {step.endTime && <span>Completed: {step.endTime.toLocaleTimeString()}</span>}
                      {step.startTime && step.endTime && (
                        <span>Duration: {Math.round((step.endTime.getTime() - step.startTime.getTime()) / 1000)}s</span>
                      )}
                    </div>
                  )}
                </div>

                <div className="text-sm font-medium capitalize">
                  {step.status}
                </div>
              </motion.div>

              {index < workflow.steps.length - 1 && (
                <div className="flex justify-center py-2">
                  <ArrowRight className="h-4 w-4 text-secondary-400" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Workflow Summary */}
        <div className="bg-secondary-50 rounded-lg p-4 border border-secondary-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-lg font-semibold text-secondary-900">
                {workflow.steps.filter(s => s.status === 'completed').length}
              </p>
              <p className="text-sm text-secondary-600">Completed</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-secondary-900">
                {workflow.steps.filter(s => s.status === 'running').length}
              </p>
              <p className="text-sm text-secondary-600">Running</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-secondary-900">
                {workflow.steps.filter(s => s.status === 'pending').length}
              </p>
              <p className="text-sm text-secondary-600">Pending</p>
            </div>
            <div>
              <p className="text-lg font-semibold text-secondary-900">
                {workflow.steps.filter(s => s.status === 'failed').length}
              </p>
              <p className="text-sm text-secondary-600">Failed</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowVisualization
