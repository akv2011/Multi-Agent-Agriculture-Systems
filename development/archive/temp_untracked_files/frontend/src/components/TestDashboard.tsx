import { useState } from 'react'
import { useAgentStore } from '../stores/agentStore'
import AgentGrid from './AgentGrid'

const TestDashboard = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'workflows' | 'metrics'>('overview')
  const { agents } = useAgentStore()
  
  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-secondary-900">AgentWeaver</h1>
            <p className="text-secondary-600 mt-2">Multi-Agent Agriculture Intelligence System</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-primary-500 rounded-full mr-2"></div>
              <span className="text-sm text-secondary-600">
                {agents.filter(a => a.status !== 'idle').length} Active Agents
              </span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex space-x-1 mb-8 bg-white rounded-xl p-1 shadow-sm">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'agents', label: 'Agents', icon: '🤖' },
            { id: 'workflows', label: 'Workflows', icon: '⚡' },
            { id: 'metrics', label: 'Metrics', icon: '📈' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-2xl font-bold text-secondary-900 mb-6">System Overview</h2>
              <AgentGrid />
              <div className="mt-8 bg-white rounded-xl p-6 shadow-sm">
                <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2 border-b border-secondary-100">
                    <span className="text-secondary-700">Router Agent processed new query</span>
                    <span className="text-sm text-secondary-500">2 mins ago</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-secondary-100">
                    <span className="text-secondary-700">Crop Selection completed analysis</span>
                    <span className="text-sm text-secondary-500">5 mins ago</span>
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <span className="text-secondary-700">Market Timing updated forecasts</span>
                    <span className="text-sm text-secondary-500">12 mins ago</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'agents' && (
            <div>
              <h2 className="text-2xl font-bold text-secondary-900 mb-6">Agent Details</h2>
              <AgentGrid detailed />
            </div>
          )}

          {activeTab === 'workflows' && (
            <div>
              <h2 className="text-2xl font-bold text-secondary-900 mb-6">Workflow Management</h2>
              <div className="bg-white rounded-xl p-8 shadow-sm text-center">
                <p className="text-secondary-600">Workflow visualization coming soon...</p>
              </div>
            </div>
          )}

          {activeTab === 'metrics' && (
            <div>
              <h2 className="text-2xl font-bold text-secondary-900 mb-6">System Metrics</h2>
              <div className="bg-white rounded-xl p-8 shadow-sm text-center">
                <p className="text-secondary-600">Metrics dashboard coming soon...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TestDashboard
