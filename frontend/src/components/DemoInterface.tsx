import React, { useState, useEffect } from 'react';
import './DemoInterface.css';
import apiClient from '../services/apiClient';
// import VoiceAgent from './VoiceAgent'; // Removed - using SimpleDemoInterface for Query tab

interface DemoQuery {
  query: string;
  type: string;
  agent: string;
}

interface RoutingAnalysis {
  agent: string;
  confidence: number;
  reasoning: string;
  language_detected: string;
}

interface SatelliteData {
  ndvi: number;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  environmental_score: number;
  risk_level: string;
}

interface TechnicalMetrics {
  processing_time_ms: number;
  confidence_level: number;
  satellite_data_integrated: boolean;
  risk_assessment: string;
  agent: string;
}

interface DemoResponse {
  status: string;
  query_id: string;
  original_query: string;
  routing_analysis: RoutingAnalysis;
  satellite_data: SatelliteData;
  response_text: string;
  technical_metrics: TechnicalMetrics;
  timestamp: string;
}

interface Capabilities {
  system_status: string;
  completion_percentage: number;
  operational_agents: string[];
  capabilities: string[];
  satellite_features: string[];
  supported_languages: string[];
}

const DemoInterface: React.FC = () => {
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [sampleQueries, setSampleQueries] = useState<DemoQuery[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [selectedLocation, setSelectedLocation] = useState<string>('punjab_ludhiana');
  const [demoResponse, setDemoResponse] = useState<DemoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchCapabilities();
    fetchSampleQueries();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const data = await apiClient.get<Capabilities>('/demo/capabilities');
      setCapabilities(data);
    } catch (err) {
      setError('Failed to fetch capabilities');
      console.error(err);
    }
  };

  const fetchSampleQueries = async () => {
    try {
      const data = await apiClient.get<{ sample_queries: DemoQuery[] }>('/demo/session');
      setSampleQueries(data?.sample_queries || []);
    } catch (err) {
      setError('Failed to fetch sample queries');
      console.error(err);
    }
  };

  const submitQuery = async () => {
    if (!currentQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    setIsLoading(true);
    setError('');
    setDemoResponse(null);

    try {
      const data = await apiClient.post<DemoResponse>('/demo/query', {
        query_text: currentQuery,
        language: selectedLanguage || undefined,
        location: selectedLocation,
      });
      
      setDemoResponse(data);
    } catch (err) {
      setError('Failed to process query: ' + (err as Error).message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice functionality moved to SimpleDemoInterface for the Query tab

  const selectSampleQuery = (query: DemoQuery) => {
    setCurrentQuery(query.query);
    // Auto-detect language based on query content
    if (query.query.includes('गेहूं') || query.query.includes('पत्ते') || query.query.includes('करूं')) {
      setSelectedLanguage('hindi');
    } else if (query.query.includes('Meri') || query.query.includes('ke liye')) {
      setSelectedLanguage('mixed');
    } else {
      setSelectedLanguage('english');
    }
  };

  return (
    <div className="demo-interface">
      <div className="demo-header">
        <h1>🌾🛰️ Multi-Agent Agriculture Systems - Live Demo</h1>
        {capabilities && (
          <div className="system-status">
            <div className="status-badge">
              {capabilities.system_status}
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${capabilities.completion_percentage}%` }}
              >
                {capabilities.completion_percentage}% Complete
              </div>
            </div>
            <div className="agents-count">
              {capabilities?.operational_agents?.length || 0}/7 Agents Operational
            </div>
          </div>
        )}
      </div>

      {capabilities && (
        <div className="capabilities-section">
          <h3>🎯 System Capabilities:</h3>
          <div className="capabilities-grid">
            {capabilities?.capabilities?.map((capability, index) => (
              <div key={index} className="capability-item">
                ✓ {capability}
              </div>
            )) || <div>Loading capabilities...</div>}
          </div>
        </div>
      )}

      <div className="query-section">
        <h3>💬 Ask Your Agricultural Question</h3>
        
        <div className="sample-queries">
          <h4>Sample Queries:</h4>
          <div className="queries-grid">
            {sampleQueries?.length > 0 ? sampleQueries.map((query, index) => (
              <div 
                key={index} 
                className="sample-query"
                onClick={() => selectSampleQuery(query)}
              >
                <div className="query-text">{query.query}</div>
                <div className="query-meta">
                  <span className="query-type">{query.type}</span>
                  <span className="query-agent">{query.agent}</span>
                </div>
              </div>
            )) : <div>Loading sample queries...</div>}
          </div>
        </div>

        <div className="query-input-section">
          <div className="input-controls">
            <select 
              value={selectedLanguage} 
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="language-select"
            >
              <option value="">Auto-detect Language</option>
              <option value="hindi">Hindi</option>
              <option value="english">English</option>
              <option value="mixed">Mixed (Hindi-English)</option>
            </select>

            <select 
              value={selectedLocation} 
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="location-select"
            >
              <option value="punjab_ludhiana">Punjab - Ludhiana</option>
              <option value="maharashtra_nagpur">Maharashtra - Nagpur</option>
            </select>
          </div>

          <div className="query-input">
            <textarea
              value={currentQuery}
              onChange={(e) => setCurrentQuery(e.target.value)}
              placeholder="Type your agricultural question here..."
              rows={3}
              className="query-textarea"
            />
            {/* Voice integration moved to SimpleDemoInterface */}
            <button 
              onClick={submitQuery} 
              disabled={isLoading}
              className="submit-button"
            >
              {isLoading ? '🔄 Processing...' : '🚀 Submit Query'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {demoResponse && (
        <div className="response-section">
          <h3>🤖 AI Response</h3>
          
          <div className="routing-analysis">
            <h4>🧠 AI Routing Analysis:</h4>
            <div className="analysis-grid">
              <div className="analysis-item">
                <strong>Agent Selected:</strong> {demoResponse.routing_analysis.agent}
              </div>
              <div className="analysis-item">
                <strong>Confidence:</strong> {(demoResponse.routing_analysis.confidence * 100).toFixed(1)}%
              </div>
              <div className="analysis-item">
                <strong>Language Detected:</strong> {demoResponse.routing_analysis.language_detected}
              </div>
              <div className="analysis-item">
                <strong>Reasoning:</strong> {demoResponse.routing_analysis.reasoning}
              </div>
            </div>
          </div>

          <div className="satellite-data">
            <h4>🛰️ Satellite Data Analysis:</h4>
            <div className="satellite-grid">
              <div className="satellite-item">
                <strong>NDVI Score:</strong> {demoResponse.satellite_data.ndvi}
              </div>
              <div className="satellite-item">
                <strong>Soil Moisture:</strong> {(demoResponse.satellite_data.soil_moisture * 100).toFixed(0)}%
              </div>
              <div className="satellite-item">
                <strong>Temperature:</strong> {demoResponse.satellite_data.temperature}°C
              </div>
              <div className="satellite-item">
                <strong>Humidity:</strong> {demoResponse.satellite_data.humidity}%
              </div>
              <div className="satellite-item">
                <strong>Environmental Score:</strong> {demoResponse.satellite_data.environmental_score}/100
              </div>
              <div className="satellite-item">
                <strong>Risk Level:</strong> {demoResponse.satellite_data.risk_level.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="ai-response">
            <h4>🌾 Satellite-Enhanced Response:</h4>
            <div className="response-text">
              <pre>{demoResponse.response_text}</pre>
            </div>
          </div>

          <div className="technical-metrics">
            <h4>📊 Technical Metrics:</h4>
            <div className="metrics-grid">
              <div className="metric-item">
                <strong>Processing Time:</strong> {demoResponse.technical_metrics.processing_time_ms}ms
              </div>
              <div className="metric-item">
                <strong>Confidence Level:</strong> {(demoResponse.technical_metrics.confidence_level * 100).toFixed(1)}%
              </div>
              <div className="metric-item">
                <strong>Satellite Data:</strong> {demoResponse.technical_metrics.satellite_data_integrated ? '✅ Integrated' : '❌ Not Available'}
              </div>
              <div className="metric-item">
                <strong>Risk Assessment:</strong> {demoResponse.technical_metrics.risk_assessment}
              </div>
              <div className="metric-item">
                <strong>Agent:</strong> {demoResponse.technical_metrics.agent}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoInterface;
