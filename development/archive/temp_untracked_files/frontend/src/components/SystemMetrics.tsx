import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const SystemMetrics: React.FC = () => {
  const performanceData = [
    { name: 'Router', tasks: 156, avgTime: 1.2, success: 98.5 },
    { name: 'Crop', tasks: 89, avgTime: 3.4, success: 94.2 },
    { name: 'Pest', tasks: 67, avgTime: 2.8, success: 91.7 },
    { name: 'Market', tasks: 134, avgTime: 2.1, success: 96.3 },
    { name: 'Irrigation', tasks: 98, avgTime: 1.8, success: 97.1 },
    { name: 'Finance', tasks: 45, avgTime: 4.2, success: 88.9 },
    { name: 'Data', tasks: 203, avgTime: 0.8, success: 99.1 },
  ]

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-secondary-900 mb-4">System Performance</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-secondary-900">792</p>
            <p className="text-sm text-secondary-600">Total Tasks Completed</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-secondary-900">2.1s</p>
            <p className="text-sm text-secondary-600">Average Response Time</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-secondary-900">95.1%</p>
            <p className="text-sm text-secondary-600">Overall Success Rate</p>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="tasks" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Agent Performance Details</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-secondary-200">
                <th className="text-left py-2 text-secondary-700 font-medium">Agent</th>
                <th className="text-right py-2 text-secondary-700 font-medium">Tasks</th>
                <th className="text-right py-2 text-secondary-700 font-medium">Avg Time</th>
                <th className="text-right py-2 text-secondary-700 font-medium">Success Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-secondary-100">
              {performanceData.map((agent) => (
                <tr key={agent.name}>
                  <td className="py-3 font-medium text-secondary-900">{agent.name} Agent</td>
                  <td className="py-3 text-right text-secondary-700">{agent.tasks}</td>
                  <td className="py-3 text-right text-secondary-700">{agent.avgTime}s</td>
                  <td className="py-3 text-right">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      agent.success >= 95 ? 'bg-green-100 text-green-700' :
                      agent.success >= 90 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {agent.success}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default SystemMetrics
