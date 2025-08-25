import React, { useState } from 'react';
import './SimpleDemoInterface.css';
import apiClient from '../services/apiClient';

interface DemoResponse {
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
}

const SimpleDemoInterface: React.FC = () => {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [demoResponse, setDemoResponse] = useState<DemoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Function to convert markdown-like formatting to HTML
  const formatResponseText = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Convert **text** to bold
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Convert *text* to italic
      .replace(/\n/g, '<br>') // Convert newlines to br tags
      .replace(/•/g, '&bull;'); // Ensure bullet points display correctly
  };

  // Sample queries from the demo script
  const sampleQueries = [
    {
      query: "पंजाब में गेहूं की सबसे अच्छी किस्म कौन सी है?",
      type: "Hindi crop selection",
      agent: "crop_selection"
    },
    {
      query: "Meri cotton crop mein पीले पत्ते दिख रहे हैं, क्या करूं?",
      type: "Code-switched pest management", 
      agent: "pest_management"
    },
    {
      query: "When should I sell my wheat crop for maximum profit?",
      type: "English market timing",
      agent: "market_timing"
    },
    {
      query: "My field needs irrigation - when and how much water?",
      type: "Irrigation scheduling",
      agent: "irrigation"
    },
    {
      query: "Loan ke liye apply कैसे करूं for farming equipment?",
      type: "Financial advisory",
      agent: "finance_policy"
    }
  ];

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
        location: 'punjab_ludhiana',
      });
      setDemoResponse(data);
    } catch (err) {
      setError('Failed to process query: ' + (err as Error).message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectSampleQuery = (query: { query: string }) => {
    setCurrentQuery(query.query);
  };

  return (
    <div className="simple-demo">
      <div className="demo-header">
        <h1>🌾🛰️ Multi-Agent Agriculture Systems </h1>
        <div className="system-status">
          <div className="status-badge">
            Satellite-Enhanced AI Agricultural Advisory System
          </div>
          <div className="progress-info">
            Complete  Agents Operational
          </div>
        </div>
      </div>

      <div className="capabilities">
        <h3>🎯 System Capabilities:</h3>
        <div className="capability-list">
          <div className="capability">✓ Multilingual Query Processing (Hindi/English/Mixed)</div>
          <div className="capability">✓ Intelligent Agent Routing</div>
          <div className="capability">✓ Satellite Data Integration</div>
          <div className="capability">✓ Real-time Agricultural Advisory</div>
          <div className="capability">✓ Confidence-based Recommendations</div>
        </div>
      </div>

      <div className="query-section">
        <h3>💬 Ask Your Agricultural Question</h3>
        
        <div className="sample-queries">
          <h4>Sample Queries:</h4>
          <div className="queries-list">
            {sampleQueries.map((query, index) => (
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
            ))}
          </div>
        </div>

        <div className="query-input">
          <textarea
            value={currentQuery}
            onChange={(e) => setCurrentQuery(e.target.value)}
            placeholder="Type your agricultural question here..."
            rows={3}
            className="query-textarea"
          />
          <button 
            onClick={submitQuery} 
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? '🔄 Processing...' : '🚀 Submit Query'}
          </button>
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
            <div className="analysis-info">
              <div><strong>Agent Selected:</strong> {demoResponse.routing_analysis.agent}</div>
              <div><strong>Confidence:</strong> {(demoResponse.routing_analysis.confidence * 100).toFixed(1)}%</div>
              <div><strong>Language:</strong> {demoResponse.routing_analysis.language_detected}</div>
              <div><strong>Reasoning:</strong> {demoResponse.routing_analysis.reasoning}</div>
            </div>
          </div>

          <div className="satellite-data">
            <h4>🛰️ Satellite Data Analysis:</h4>
            <div className="satellite-info">
              <div><strong>NDVI Score:</strong> {demoResponse.satellite_data.ndvi}</div>
              <div><strong>Soil Moisture:</strong> {(demoResponse.satellite_data.soil_moisture * 100).toFixed(0)}%</div>
              <div><strong>Temperature:</strong> {demoResponse.satellite_data.temperature}°C</div>
              <div><strong>Environmental Score:</strong> {demoResponse.satellite_data.environmental_score}/100</div>
              <div><strong>Risk Level:</strong> {demoResponse.satellite_data.risk_level.toUpperCase()}</div>
            </div>
          </div>

          <div className="ai-response">
            <h4>🌾 Satellite-Enhanced Response:</h4>
            <div 
              className="response-text"
              dangerouslySetInnerHTML={{ 
                __html: formatResponseText(demoResponse.response_text) 
              }}
            />
          </div>

          <div className="technical-metrics">
            <h4>📊 Technical Metrics:</h4>
            <div className="metrics-info">
              <div><strong>Processing Time:</strong> {demoResponse.technical_metrics.processing_time_ms}ms</div>
              <div><strong>Confidence:</strong> {(demoResponse.technical_metrics.confidence_level * 100).toFixed(1)}%</div>
              <div><strong>Satellite Data:</strong> {demoResponse.technical_metrics.satellite_data_integrated ? '✅ Integrated' : '❌ Not Available'}</div>
              <div><strong>Agent:</strong> {demoResponse.technical_metrics.agent}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleDemoInterface;
