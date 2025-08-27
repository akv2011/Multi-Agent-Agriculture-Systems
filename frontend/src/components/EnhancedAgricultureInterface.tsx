import React, { useState, useEffect, useCallback } from 'react';
import './EnhancedAgricultureInterface.css';

interface ProcessingStep {
  step: string;
  timestamp: string;
  status: string;
  details?: Record<string, unknown>;
}

interface AgentResponse {
  agent_id: string;
  response_text: string;
  confidence_score: number;
}

interface FailedAgent {
  agent_id: string;
  error: string;
}

interface RealTimeUpdate {
  id: string;
  query: string;
  status: string;
  confidence: number;
  timestamp: string;
}

interface SystemMetrics {
  total_queries: number;
  success_rate: number;
  average_response_time_ms: number;
  system_uptime_seconds: number;
  active_workflows: number;
  agent_stats: Record<string, unknown>;
}

interface DashboardUpdate {
  query_processed: boolean;
  processing_time_ms: number;
  success: boolean;
  agents_involved: string[];
  confidence_score: number;
  complexity: string;
  satellite_data_used: boolean;
  recommendations_generated: number;
  workflow_efficiency: number;
}

interface ComprehensiveAnswer {
  primary_response: string;
  confidence: number;
  source_agents: string[];
  supporting_insights: Array<{
    agent: string;
    insight: string;
    confidence: number;
  }>;
  synthesis_method: string;
  response_quality: string;
}

interface EnhancedQueryResponse {
  status: string;
  query_id: string;
  original_query: string;
  processing_timeline: ProcessingStep[];
  query_analysis: {
    language: string;
    intent: string;
    complexity: string;
    entities: {
      crops: string[];
      diseases: string[];
      locations: string[];
    };
  };
  agent_routing: Record<string, unknown>;
  comprehensive_answer: ComprehensiveAnswer;
  confidence_metrics: {
    overall: number;
    agent_confidences: Record<string, number>;
    synthesis_confidence: number;
  };
  recommendations: Array<{
    title: string;
    description: string;
    priority: string;
    confidence: number;
    source_agent: string;
  }>;
  dashboard_metrics: DashboardUpdate;
  workflow_status: {
    id: string;
    status: string;
    current_step: string;
    progress?: number;
  };
  system_performance: SystemMetrics;
  satellite_integration: {
    enabled: boolean;
    data_sources?: string[];
    accuracy?: string;
  };
  agent_performance: Record<string, {
    confidence: number;
    response_length: number;
    processing_time: number;
    success: boolean;
  }>;
  processing_metadata: {
    processing_time_ms: number;
    agents_involved: number;
    complexity: string;
    language_detected: string;
  };
}

interface DashboardMetrics {
  totalQueries: number;
  successfulQueries: number;
  avgProcessingTime: number;
  systemHealth: string;
  activeAgents: number;
  runningWorkflows: number;
}

const EnhancedAgricultureInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('punjab_ludhiana');
  const [language, setLanguage] = useState('auto');
  const [priority, setPriority] = useState('normal');
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [includeSatellite, setIncludeSatellite] = useState(true);
  
  const [response, setResponse] = useState<EnhancedQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingSteps, setProcessingSteps] = useState<string[]>([]);
  
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics>({
    totalQueries: 0,
    successfulQueries: 0,
    avgProcessingTime: 0,
    systemHealth: 'healthy',
    activeAgents: 5,
    runningWorkflows: 0
  });
  
  const [realTimeUpdates, setRealTimeUpdates] = useState<RealTimeUpdate[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const availableAgents = [
    { id: 'crop_selection', name: 'Crop Selection', description: 'Crop recommendations and planning' },
    { id: 'pest_management', name: 'Pest Management', description: 'Disease identification and treatment' },
    { id: 'irrigation_optimization', name: 'Irrigation', description: 'Water management and scheduling' },
    { id: 'market_timing', name: 'Market Analysis', description: 'Price forecasting and market insights' },
    { id: 'input_materials', name: 'Input Materials', description: 'Fertilizer and input recommendations' },
    { id: 'weather_forecast', name: 'Weather Forecast', description: 'Weather predictions and alerts' },
    { id: 'finance_policy', name: 'Finance & Policy', description: 'Loans, subsidies, and policies' },
    { id: 'gemini_agriculture', name: 'General AI Assistant', description: 'Multi-purpose agricultural guidance' }
  ];

  const sampleQueries = {
    'Crop Planning': [
      'कौन सी फसल बोनी चाहिए इस season में?',
      'What crops should I plant in Punjab this winter?',
      'Best profitable crops for black soil in Maharashtra'
    ],
    'Disease Management': [
      'My wheat crop has brown spots, what disease is this?',
      'धान की पत्ती पीली हो रही है, क्या करूं?',
      'How to treat blight in tomato plants?'
    ],
    'Water Management': [
      'How much water does corn need per week?',
      'Drip irrigation system कैसे setup करूं?',
      'Best irrigation schedule for rice crop'
    ],
    'Market Intelligence': [
      'When to sell wheat for best price?',
      'आज मंडी में सोयाबीन का भाव क्या है?',
      'Cotton price forecast for next month'
    ]
  };

  // Real-time dashboard updates
  useEffect(() => {
    const interval = setInterval(() => {
      updateDashboardMetrics();
    }, 5000);

    return () => clearInterval(interval);
  }, [updateDashboardMetrics]);

  const updateDashboardMetrics = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8001/demo/dashboard');
      if (response.ok) {
        const data = await response.json();
        setDashboardMetrics({
          totalQueries: data.total_queries_processed,
          successfulQueries: Math.floor(data.total_queries_processed * data.success_rate),
          avgProcessingTime: data.average_response_time * 1000, // Convert to ms
          systemHealth: data.success_rate > 0.8 ? 'healthy' : 'warning',
          activeAgents: Object.keys(data.agent_utilization || {}).length || 5,
          runningWorkflows: data.current_active_workflows
        });
      }
    } catch (error) {
      console.warn('Could not update dashboard metrics:', error);
    }
  }, []);

  const submitEnhancedQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setProcessingSteps([]);
    setRealTimeUpdates([]);

    try {
      const requestData = {
        query_text: query,
        location: location,
        language: language === 'auto' ? undefined : language,
        include_satellite: includeSatellite,
        agent_preferences: selectedAgents.length > 0 ? selectedAgents : undefined,
        priority_level: priority,
        context: {
          interface: 'enhanced_ui',
          timestamp: new Date().toISOString()
        }
      };

      const response = await fetch('http://localhost:8001/demo/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResponse(data);
      
      // Update processing steps from timeline
      if (data.processing_timeline) {
        setProcessingSteps(data.processing_timeline.map((step: ProcessingStep) => step.step));
      }

      // Update dashboard metrics
      await updateDashboardMetrics();

      // Add real-time update
      setRealTimeUpdates(prev => [{
        id: data.query_id,
        query: query.substring(0, 50) + '...',
        status: data.status,
        confidence: data.confidence_metrics?.overall || 0,
        timestamp: new Date().toISOString()
      }, ...prev.slice(0, 4)]);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery);
  };

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgents(prev => 
      prev.includes(agentId) 
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="enhanced-agriculture-interface">
      {/* Header with Real-time Dashboard */}
      <div className="interface-header">
        <div className="header-content">
<<<<<<< HEAD
          <h1>🌾 Enhanced AgriMitr Intelligence System</h1>
=======
          <h1>🌾 Enhanced AgriSens Intelligence System</h1>
>>>>>>> upstream/main
          <p>Advanced Multi-Agent Agriculture Platform with Real-time Analytics</p>
        </div>
        
        <div className="dashboard-metrics">
          <div className="metric-card">
            <div className="metric-value">{dashboardMetrics.totalQueries}</div>
            <div className="metric-label">Total Queries</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{dashboardMetrics.successfulQueries}</div>
            <div className="metric-label">Successful</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{dashboardMetrics.avgProcessingTime.toFixed(1)}s</div>
            <div className="metric-label">Avg Time</div>
          </div>
          <div className="metric-card">
            <div 
              className="metric-value"
              style={{ color: getHealthColor(dashboardMetrics.systemHealth) }}
            >
              {dashboardMetrics.systemHealth.toUpperCase()}
            </div>
            <div className="metric-label">System Health</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{dashboardMetrics.activeAgents}</div>
            <div className="metric-label">Active Agents</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{dashboardMetrics.runningWorkflows}</div>
            <div className="metric-label">Running Workflows</div>
          </div>
        </div>
      </div>

      <div className="interface-body">
        {/* Query Input Section */}
        <div className="query-section">
          <h2>🔍 Intelligent Query Processing</h2>
          
          <div className="query-form">
            <div className="input-group">
              <label htmlFor="query">Your Agricultural Question:</label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask anything about farming, crops, diseases, market prices, or agricultural practices..."
                rows={3}
                className="query-input"
              />
            </div>

            <div className="form-row">
              <div className="input-group">
                <label htmlFor="location">📍 Location:</label>
                <select 
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="form-select"
                >
                  <option value="punjab_ludhiana">Punjab, Ludhiana</option>
                  <option value="haryana_karnal">Haryana, Karnal</option>
                  <option value="uttar_pradesh_meerut">Uttar Pradesh, Meerut</option>
                  <option value="maharashtra_nashik">Maharashtra, Nashik</option>
                  <option value="karnataka_bangalore">Karnataka, Bangalore</option>
                </select>
              </div>

              <div className="input-group">
                <label htmlFor="language">🌐 Language:</label>
                <select 
                  id="language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="form-select"
                >
                  <option value="auto">Auto Detect</option>
                  <option value="english">English</option>
                  <option value="hindi">Hindi</option>
                  <option value="hinglish">Hinglish</option>
                </select>
              </div>

              <div className="input-group">
                <label htmlFor="priority">⚡ Priority:</label>
                <select 
                  id="priority"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="form-select"
                >
                  <option value="normal">Normal</option>
                  <option value="high">High Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>
            </div>

            {/* Advanced Options */}
            <div className="advanced-options">
              <button 
                className="toggle-advanced"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                {showAdvanced ? '🔽' : '▶️'} Advanced Options
              </button>

              {showAdvanced && (
                <div className="advanced-panel">
                  <div className="option-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={includeSatellite}
                        onChange={(e) => setIncludeSatellite(e.target.checked)}
                      />
                      Include Satellite Data Integration
                    </label>
                  </div>

                  <div className="option-group">
                    <label>Select Specific Agents (optional):</label>
                    <div className="agent-selection">
                      {availableAgents.map(agent => (
                        <div 
                          key={agent.id}
                          className={`agent-chip ${selectedAgents.includes(agent.id) ? 'selected' : ''}`}
                          onClick={() => toggleAgentSelection(agent.id)}
                        >
                          <span className="agent-name">{agent.name}</span>
                          <span className="agent-desc">{agent.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button 
              onClick={submitEnhancedQuery}
              disabled={loading || !query.trim()}
              className={`submit-button ${loading ? 'loading' : ''}`}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Processing...
                </>
              ) : (
                <>
                  🚀 Process Query
                </>
              )}
            </button>
          </div>
        </div>

        {/* Sample Queries */}
        <div className="sample-queries">
          <h3>💡 Sample Queries</h3>
          <div className="query-categories">
            {Object.entries(sampleQueries).map(([category, queries]) => (
              <div key={category} className="query-category">
                <h4>{category}</h4>
                <div className="query-list">
                  {queries.map((sampleQuery, index) => (
                    <button
                      key={index}
                      className="sample-query-button"
                      onClick={() => handleSampleQuery(sampleQuery)}
                    >
                      {sampleQuery}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Processing Status */}
        {loading && (
          <div className="processing-status">
            <h3>⚙️ Processing Status</h3>
            <div className="processing-steps">
              {processingSteps.map((step, index) => (
                <div key={index} className="processing-step completed">
                  ✅ {step.replace('_', ' ').toUpperCase()}
                </div>
              ))}
              <div className="processing-step active">
                🔄 Processing query...
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-display">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Enhanced Response Display */}
        {response && (
          <div className="response-display">
            <h3>📊 Comprehensive Analysis Results</h3>
            
            {/* Query Analysis */}
            <div className="analysis-section">
              <h4>🔍 Query Analysis</h4>
              <div className="analysis-grid">
                <div className="analysis-card">
                  <label>Language Detected:</label>
                  <span className="badge">{response.query_analysis.language}</span>
                </div>
                <div className="analysis-card">
                  <label>Intent Classification:</label>
                  <span className="badge">{response.query_analysis.intent}</span>
                </div>
                <div className="analysis-card">
                  <label>Complexity Level:</label>
                  <span className="badge">{response.query_analysis.complexity}</span>
                </div>
                <div className="analysis-card">
                  <label>Entities Extracted:</label>
                  <div className="entity-list">
                    {response.query_analysis.entities.crops.map(crop => (
                      <span key={crop} className="entity crop">🌾 {crop}</span>
                    ))}
                    {response.query_analysis.entities.diseases.map(disease => (
                      <span key={disease} className="entity disease">🦠 {disease}</span>
                    ))}
                    {response.query_analysis.entities.locations.map(location => (
                      <span key={location} className="entity location">📍 {location}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Agent Performance */}
            <div className="analysis-section">
              <h4>🤖 Agent Performance</h4>
              <div className="agent-coordination">
                {Object.entries(response.agent_performance).map(([agentId, performance]) => (
                  <div key={agentId} className="agent-decision">
                    <div className="agent-info">
                      <span className="agent-name">{agentId}</span>
                      <span 
                        className="confidence-score"
                        style={{ color: getConfidenceColor(performance.confidence) }}
                      >
                        {(performance.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="agent-reason">
                      Processing Time: {performance.processing_time.toFixed(2)}s
                    </div>
                    <div className="priority-indicator">
                      Status: {performance.success ? '✅ Success' : '❌ Failed'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Primary Response - Enhanced with Formatting */}
            <div className="analysis-section">
              <h4>💬 Comprehensive Answer</h4>
              
              {/* Executive Summary */}
              {response.comprehensive_answer.executive_summary && (
                <div className="executive-summary">
                  <h5>📋 Executive Summary</h5>
                  <div className="summary-grid">
                    <div className="summary-item">
                      <label>Query Type:</label>
                      <span className="badge">{response.comprehensive_answer.executive_summary.query_type}</span>
                    </div>
                    <div className="summary-item">
                      <label>Confidence Level:</label>
                      <span className="badge">{response.comprehensive_answer.executive_summary.confidence_level}</span>
                    </div>
                    <div className="summary-item">
                      <label>Urgency:</label>
                      <span className={`badge urgency-${response.comprehensive_answer.executive_summary.urgency.toLowerCase()}`}>
                        {response.comprehensive_answer.executive_summary.urgency}
                      </span>
                    </div>
                  </div>
                  <div className="key-insight">
                    <strong>Key Insight:</strong> {response.comprehensive_answer.executive_summary.key_insight}
                  </div>
                  {response.comprehensive_answer.executive_summary.primary_recommendation && (
                    <div className="primary-recommendation">
                      <strong>Primary Recommendation:</strong> {response.comprehensive_answer.executive_summary.primary_recommendation}
                    </div>
                  )}
                </div>
              )}

              {/* Detailed Analysis Sections */}
              {response.comprehensive_answer.detailed_analysis && response.comprehensive_answer.detailed_analysis.length > 0 && (
                <div className="detailed-analysis">
                  <h5>🔍 Detailed Analysis</h5>
                  {response.comprehensive_answer.detailed_analysis.map((section, index) => (
                    <div key={index} className={`analysis-section-detail importance-${section.importance}`}>
                      <h6>{section.title}</h6>
                      <div 
                        className="section-content"
                        dangerouslySetInnerHTML={{ __html: section.content }}
                      />
                      {section.data_points && section.data_points.length > 0 && (
                        <div className="data-points">
                          <strong>Key Data Points:</strong>
                          <ul>
                            {section.data_points.map((dp, dpIndex) => (
                              <li key={dpIndex}>
                                {dp.text} {dp.values.length > 0 && `(Values: ${dp.values.join(', ')})`}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Fallback to Primary Response if formatted sections not available */}
              {(!response.comprehensive_answer.detailed_analysis || response.comprehensive_answer.detailed_analysis.length === 0) && (
                <div className="primary-response">
                  <div className="response-header">
                    <span className="primary-agent">
                      Quality: {response.comprehensive_answer.response_quality}
                    </span>
                    <span 
                      className="confidence-badge"
                      style={{ backgroundColor: getConfidenceColor(response.comprehensive_answer.confidence) }}
                    >
                      {(response.comprehensive_answer.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  </div>
                  <div className="response-text">
                    {response.comprehensive_answer.primary_response}
                  </div>
                </div>
              )}
            </div>

            {/* Actionable Recommendations */}
            {response.comprehensive_answer.actionable_recommendations && response.comprehensive_answer.actionable_recommendations.length > 0 && (
              <div className="analysis-section">
                <h4>💡 Actionable Recommendations</h4>
                <div className="recommendations-list">
                  {response.comprehensive_answer.actionable_recommendations.map((rec, index) => (
                    <div key={index} className={`recommendation-item priority-${rec.priority} impact-${rec.impact?.toLowerCase()}`}>
                      <div className="recommendation-header">
                        <span className="priority-badge">Priority {rec.priority}</span>
                        <span className="timeline-badge">{rec.timeline}</span>
                        {rec.impact && <span className="impact-badge">{rec.impact} Impact</span>}
                        {rec.difficulty && <span className="difficulty-badge">{rec.difficulty}</span>}
                      </div>
                      <div className="recommendation-action">
                        {rec.action}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            {response.comprehensive_answer.next_steps && response.comprehensive_answer.next_steps.length > 0 && (
              <div className="analysis-section">
                <h4>📝 Next Steps</h4>
                <div className="next-steps-list">
                  {response.comprehensive_answer.next_steps.map((step, index) => (
                    <div key={index} className="next-step-item">
                      <div className="step-number">{step.step}</div>
                      <div className="step-content">
                        <div className="step-action">{step.action}</div>
                        <div className="step-meta">
                          <span className="timeframe">⏱️ {step.timeframe}</span>
                          {step.resources_needed && step.resources_needed.length > 0 && (
                            <span className="resources">🛠️ {step.resources_needed.join(', ')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Supporting Insights */}
            {response.comprehensive_answer.supporting_insights?.length > 0 && (
              <div className="analysis-section">
                <h4>💡 Supporting Insights</h4>
                <div className="supporting-insights">
                  {response.comprehensive_answer.supporting_insights.map((insight, index) => (
                    <div key={index} className="insight-card">
                      <div className="insight-header">
                        <span className="insight-agent">{insight.agent}</span>
                        <span 
                          className="insight-confidence"
                          style={{ color: getConfidenceColor(insight.confidence) }}
                        >
                          {(insight.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="insight-text">{insight.insight}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {response.recommendations?.length > 0 && (
              <div className="analysis-section">
                <h4>📝 Actionable Recommendations</h4>
                <div className="recommendations">
                  {response.recommendations.map((rec, index) => (
                    <div key={index} className={`recommendation-card priority-${rec.priority}`}>
                      <div className="rec-header">
                        <span className="rec-title">{rec.title}</span>
                        <span className="rec-priority">{rec.priority.toUpperCase()}</span>
                      </div>
                      <div className="rec-description">{rec.description}</div>
                      <div className="rec-footer">
                        <span className="rec-source">Source: {rec.source_agent}</span>
                        <span className="rec-confidence">{(rec.confidence * 100).toFixed(0)}% confidence</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Technical Metrics */}
            <div className="analysis-section">
              <h4>⚡ Performance Metrics</h4>
              <div className="metrics-grid">
                <div className="metric-item">
                  <label>Processing Time:</label>
                  <span>{response.processing_metadata.processing_time_ms.toFixed(0)}ms</span>
                </div>
                <div className="metric-item">
                  <label>Agents Used:</label>
                  <span>{response.processing_metadata.agents_involved}</span>
                </div>
                <div className="metric-item">
                  <label>Workflow Efficiency:</label>
                  <span>{(response.dashboard_metrics.workflow_efficiency * 100).toFixed(0)}%</span>
                </div>
                <div className="metric-item">
                  <label>Overall Confidence:</label>
                  <span 
                    style={{ color: getConfidenceColor(response.confidence_metrics.overall) }}
                  >
                    {(response.confidence_metrics.overall * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="metric-item">
                  <label>Satellite Integration:</label>
                  <span>{response.satellite_integration.enabled ? '✅ Yes' : '❌ No'}</span>
                </div>
                <div className="metric-item">
                  <label>Query Complexity:</label>
                  <span>{response.processing_metadata.complexity}</span>
                </div>
                <div className="metric-item">
                  <label>Language:</label>
                  <span>{response.processing_metadata.language_detected}</span>
                </div>
                <div className="metric-item">
                  <label>Recommendations:</label>
                  <span>{response.dashboard_metrics.recommendations_generated}</span>
                </div>
              </div>
            </div>

            {/* Processing Timeline */}
            <div className="analysis-section">
              <h4>📅 Processing Timeline</h4>
              <div className="timeline">
                {response.processing_timeline.map((step, index) => (
                  <div key={index} className={`timeline-step ${step.status}`}>
                    <div className="step-indicator">
                      {step.status === 'completed' ? '✅' : '🔄'}
                    </div>
                    <div className="step-content">
                      <div className="step-name">{step.step.replace('_', ' ').toUpperCase()}</div>
                      <div className="step-time">{new Date(step.timestamp).toLocaleTimeString()}</div>
                      {step.details && (
                        <div className="step-details">
                          {Object.entries(step.details).map(([key, value]) => (
                            <span key={key} className="detail-item">
                              {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Real-time Activity Feed */}
        {realTimeUpdates.length > 0 && (
          <div className="activity-feed">
            <h3>📡 Real-time Activity</h3>
            <div className="activity-list">
              {realTimeUpdates.map((update) => (
                <div key={update.id} className="activity-item">
                  <div className="activity-header">
                    <span className="activity-id">Query {update.id.split('_').pop()}</span>
                    <span className="activity-time">{new Date(update.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="activity-content">
                    <span className="activity-query">{update.query}</span>
                    <span className={`activity-status ${update.status}`}>{update.status.toUpperCase()}</span>
                    <span 
                      className="activity-confidence"
                      style={{ color: getConfidenceColor(update.confidence) }}
                    >
                      {(update.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedAgricultureInterface;
