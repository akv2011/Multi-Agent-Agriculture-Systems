import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Mic, Image, Loader2 } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'
import { workflowSimulation } from '../services/workflowSimulation'

const QueryInterface: React.FC = () => {
  const [query, setQuery] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const { createWorkflow, currentWorkflow } = useAgentStore()

  const sampleQueries = [
    "What crops should I plant this season in Punjab?",
    "My wheat crop has yellow spots, what could it be?",
    "When should I water my cotton field?",
    "What's the best time to sell my rice harvest?",
    "How can I get a loan for new farming equipment?"
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isProcessing) return

    setIsProcessing(true)
    
    // Start workflow simulation
    workflowSimulation.simulateWorkflow(query)
    
    setTimeout(() => {
      setIsProcessing(false)
      setQuery('')
    }, 500)
  }

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery)
  }

  return (
    <div className="space-y-6">
      {/* Query Input */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-secondary-900 mb-4">Ask Your Question</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your agricultural question here... (English/Hindi/मिश्रित)"
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={4}
            />
            <div className="absolute bottom-3 right-3 flex space-x-2">
              <button
                type="button"
                className="p-1 text-secondary-400 hover:text-secondary-600 transition-colors"
                title="Voice input"
              >
                <Mic className="h-4 w-4" />
              </button>
              <button
                type="button"
                className="p-1 text-secondary-400 hover:text-secondary-600 transition-colors"
                title="Upload image"
              >
                <Image className="h-4 w-4" />
              </button>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={!query.trim() || isProcessing}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Send Query</span>
              </>
            )}
          </button>
        </form>

        {/* Sample Queries */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-secondary-700 mb-3">Sample Questions:</h3>
          <div className="space-y-2">
            {sampleQueries.map((sampleQuery, index) => (
              <button
                key={index}
                onClick={() => handleSampleQuery(sampleQuery)}
                className="block w-full text-left px-3 py-2 text-sm text-secondary-600 hover:bg-secondary-50 rounded-lg transition-colors"
              >
                "{sampleQuery}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Current Query Status */}
      {currentWorkflow && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6"
        >
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">Current Query</h2>
          
          <div className="bg-secondary-50 rounded-lg p-4 mb-4">
            <p className="text-sm text-secondary-700">"{currentWorkflow.query}"</p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-secondary-600">Status</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                currentWorkflow.status === 'running' ? 'bg-yellow-100 text-yellow-700' :
                currentWorkflow.status === 'completed' ? 'bg-green-100 text-green-700' :
                currentWorkflow.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-secondary-100 text-secondary-700'
              }`}>
                {currentWorkflow.status}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-secondary-600">Progress</span>
                <span className="text-secondary-900">
                  {currentWorkflow.steps.filter(s => s.status === 'completed').length} of {currentWorkflow.steps.length} steps
                </span>
              </div>
              <div className="w-full bg-secondary-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${(currentWorkflow.steps.filter(s => s.status === 'completed').length / currentWorkflow.steps.length) * 100}%`
                  }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-medium text-secondary-700">Steps:</h4>
              {currentWorkflow.steps.map((step) => (
                <div key={step.id} className="flex items-center space-x-3 text-sm">
                  <div className={`w-2 h-2 rounded-full ${
                    step.status === 'completed' ? 'bg-green-500' :
                    step.status === 'running' ? 'bg-yellow-500 animate-pulse' :
                    step.status === 'failed' ? 'bg-red-500' :
                    'bg-secondary-300'
                  }`} />
                  <span className="text-secondary-700">{step.name}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default QueryInterface
