import React, { useState, useEffect } from 'react';
import './AgricultureTester.css';

interface QueryResponse {
  status: string;
  query_id: string;
  original_query: string;
  routing_analysis: {
    agent: string;
    confidence: number;
    reasoning: string;
    language_detected: string;
  };
  satellite_data: {
    ndvi: number;
    soil_moisture: number;
    temperature: number;
    humidity: number;
    environmental_score: number;
    risk_level: string;
  };
  response_text: string;
  technical_metrics: {
    processing_time_ms: number;
    confidence_level: number;
    satellite_data_integrated: boolean;
    risk_assessment: string;
    agent: string;
  };
  timestamp: string;
}

interface SystemCapabilities {
  system_status: string;
  completion_percentage: number;
  operational_agents: string[];
  capabilities: string[];
  satellite_features: string[];
  supported_languages: string[];
}

const AgricultureTester: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('punjab_ludhiana');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [capabilities, setCapabilities] = useState<SystemCapabilities | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample queries for quick testing
  const sampleQueries = [
    {
      category: 'Crop Selection (Hindi)',
      query: 'कौन सी फसल बोनी चाहिए?',
      description: 'Test Hindi language crop recommendation'
    },
    {
      category: 'Crop Selection (English)',
      query: 'What crops should I plant this season?',
      description: 'Test English crop recommendation'
    },
    {
      category: 'Pest Management',
      query: 'My wheat crop has brown spots. What disease is this?',
      description: 'Test pest identification and treatment'
    },
    {
      category: 'Irrigation Planning',
      query: 'How much water does my corn crop need?',
      description: 'Test irrigation recommendations'
    },
    {
      category: 'Fertilizer Advice',
      query: 'What fertilizer should I use for rice?',
      description: 'Test fertilizer recommendations'
    },
    {
      category: 'Market Timing',
      query: 'When should I sell my wheat crop for best price?',
      description: 'Test market timing advice'
    }
  ];

  // Load system capabilities on component mount
  useEffect(() => {
    fetchCapabilities();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const response = await fetch('http://localhost:8001/demo/capabilities');
      const data = await response.json();
      setCapabilities(data);
    } catch (err) {
      console.error('Failed to fetch capabilities:', err);
    }
  };

  const submitQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const response = await fetch('http://localhost:8001/demo/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: query,
          location: location
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery);
  };

  return (
    <div className="agriculture-tester">
      <div className="header">
<<<<<<< HEAD
        <h1>🌾 AgriMitr Agent Tester</h1>
        <p>Test your Multi-Agent Agriculture System and verify AgriMitr integration</p>
=======
        <h1>🌾 AgriSens Agent Tester</h1>
        <p>Test your Multi-Agent Agriculture System and verify AgriSens integration</p>
>>>>>>> upstream/main
      </div>

      {/* System Status */}
      {capabilities && (
        <div className="system-status">
          <h2>📊 System Status</h2>
          <div className="status-grid">
            <div className="status-card">
              <h3>System Health</h3>
              <p className="status-value">{capabilities.system_status}</p>
            </div>
            <div className="status-card">
              <h3>Completion</h3>
              <p className="status-value">{capabilities.completion_percentage}%</p>
            </div>
            <div className="status-card">
              <h3>Active Agents</h3>
              <p className="status-value">{capabilities.operational_agents.length}</p>
            </div>
            <div className="status-card">
              <h3>Features</h3>
              <p className="status-value">{capabilities.capabilities.length}</p>
            </div>
          </div>
          
          <div className="capabilities-detail">
            <div className="capability-section">
              <h4>🤖 Operational Agents:</h4>
              <ul>
                {capabilities.operational_agents.map((agent, index) => (
                  <li key={index} className="agent-item">
                    <span className="agent-status">✅</span>
                    {agent.replace('_', ' ').toUpperCase()}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="capability-section">
              <h4>🛰️ Satellite Features:</h4>
              <ul>
                {capabilities.satellite_features.map((feature, index) => (
                  <li key={index} className="feature-item">
                    <span className="feature-status">🛰️</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Query Input Section */}
      <div className="query-section">
        <h2>🔍 Test Agriculture Agents</h2>
        
        <div className="input-group">
          <label htmlFor="location">📍 Location:</label>
          <select 
            id="location"
            value={location} 
            onChange={(e) => setLocation(e.target.value)}
            className="location-select"
          >
            <option value="punjab_ludhiana">Punjab, Ludhiana</option>
            <option value="haryana_karnal">Haryana, Karnal</option>
            <option value="uttar_pradesh_meerut">Uttar Pradesh, Meerut</option>
            <option value="maharashtra_pune">Maharashtra, Pune</option>
          </select>
        </div>

        <div className="input-group">
          <label htmlFor="query">❓ Your Agriculture Query:</label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your agriculture question in Hindi or English..."
            className="query-input"
            rows={3}
          />
        </div>

        <button 
          onClick={submitQuery} 
          disabled={loading || !query.trim()}
          className="submit-button"
        >
          {loading ? '⏳ Processing...' : '🚀 Test Agent'}
        </button>
      </div>

      {/* Sample Queries */}
      <div className="sample-queries">
        <h3>📋 Quick Test Queries</h3>
        <div className="sample-grid">
          {sampleQueries.map((sample, index) => (
            <div key={index} className="sample-card">
              <h4>{sample.category}</h4>
              <p className="sample-description">{sample.description}</p>
              <button 
                onClick={() => handleSampleQuery(sample.query)}
                className="sample-button"
              >
                Use This Query
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-section">
          <h3>❌ Error</h3>
          <p className="error-message">{error}</p>
          <p className="error-help">
            Make sure the backend server is running on http://localhost:8001
          </p>
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="response-section">
          <h2>📋 Agent Response</h2>
          
          {/* Agent Analysis */}
          <div className="analysis-grid">
            <div className="analysis-card">
              <h3>🤖 Agent Routing</h3>
              <p><strong>Selected Agent:</strong> {response.routing_analysis.agent}</p>
              <p><strong>Confidence:</strong> {(response.routing_analysis.confidence * 100).toFixed(1)}%</p>
              <p><strong>Language:</strong> {response.routing_analysis.language_detected}</p>
              <p><strong>Reasoning:</strong> {response.routing_analysis.reasoning}</p>
            </div>

            <div className="analysis-card">
              <h3>🛰️ Satellite Data</h3>
              <p><strong>NDVI Score:</strong> {response.satellite_data.ndvi}</p>
              <p><strong>Soil Moisture:</strong> {(response.satellite_data.soil_moisture * 100).toFixed(1)}%</p>
              <p><strong>Temperature:</strong> {response.satellite_data.temperature}°C</p>
              <p><strong>Humidity:</strong> {response.satellite_data.humidity}%</p>
              <p><strong>Environmental Score:</strong> {response.satellite_data.environmental_score}/100</p>
              <p><strong>Risk Level:</strong> <span className={`risk-${response.satellite_data.risk_level.toLowerCase()}`}>{response.satellite_data.risk_level}</span></p>
            </div>

            <div className="analysis-card">
              <h3>⚡ Performance Metrics</h3>
              <p><strong>Processing Time:</strong> {response.technical_metrics.processing_time_ms}ms</p>
              <p><strong>Confidence Level:</strong> {(response.technical_metrics.confidence_level * 100).toFixed(1)}%</p>
              <p><strong>Satellite Integration:</strong> {response.technical_metrics.satellite_data_integrated ? '✅ Yes' : '❌ No'}</p>
              <p><strong>Risk Assessment:</strong> {response.technical_metrics.risk_assessment}</p>
            </div>
          </div>

          {/* Agent Response */}
          <div className="agent-response">
            <h3>💬 Agent Response</h3>
            <div className="response-text">
              {response.response_text.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>

          {/* Technical Details */}
          <div className="technical-details">
            <h3>🔧 Technical Details</h3>
            <div className="tech-info">
              <p><strong>Query ID:</strong> {response.query_id}</p>
              <p><strong>Timestamp:</strong> {new Date(response.timestamp).toLocaleString()}</p>
              <p><strong>Original Query:</strong> "{response.original_query}"</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgricultureTester;
