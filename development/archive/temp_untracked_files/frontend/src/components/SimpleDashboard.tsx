import { useState } from 'react'
import { useAgentStore } from '../stores/agentStore'

const SimpleDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const { agents } = useAgentStore()
  
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          AgentWeaver Dashboard
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-white rounded-lg p-6 shadow">
              <h3 className="text-xl font-semibold mb-2">{agent.name}</h3>
              <p className="text-gray-600 mb-4">Status: {agent.status}</p>
              <div className="space-y-2">
                {agent.capabilities.slice(0, 2).map((cap, idx) => (
                  <span key={idx} className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded mr-2">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow">
          <h2 className="text-2xl font-bold mb-4">Quick Test</h2>
          <p>Active tab: {activeTab}</p>
          <button 
            onClick={() => setActiveTab(activeTab === 'overview' ? 'agents' : 'overview')}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Toggle Tab
          </button>
        </div>
      </div>
    </div>
  )
}

export default SimpleDashboard
