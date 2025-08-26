import React from 'react';
import './GeminiAnalysisDisplay.css';

interface QueryAnalysisResponse {
  analysis: string;
  recommendations: string[];
  confidence: number;
  agentType: string;
  priority: 'low' | 'medium' | 'high';
  actionItems: string[];
}

interface GeminiAnalysisDisplayProps {
  analysis: QueryAnalysisResponse;
  isLoading?: boolean;
  query: string;
}

const GeminiAnalysisDisplay: React.FC<GeminiAnalysisDisplayProps> = ({ 
  analysis, 
  isLoading = false, 
  query 
}) => {
  if (isLoading) {
    return (
      <div className="gemini-analysis loading">
        <div className="loading-header">
          <div className="gemini-logo">🤖</div>
          <h3>AI Agricultural Assistant</h3>
          <div className="loading-spinner"></div>
        </div>
        <p>Analyzing your agricultural query with advanced AI...</p>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#22C55E';
      default: return '#6B7280';
    }
  };

  const getAgentIcon = (agentType: string) => {
    const icons: { [key: string]: string } = {
      crop_selection: '🌾',
      pest_management: '🐛',
      irrigation: '💧',
      market_timing: '📈',
      finance_policy: '💰',
      weather_advisory: '🌤️',
      general_advisory: '🌱'
    };
    return icons[agentType] || '🌱';
  };

  const getAgentName = (agentType: string) => {
    const names: { [key: string]: string } = {
      crop_selection: 'Crop Selection Specialist',
      pest_management: 'Pest Management Expert',
      irrigation: 'Irrigation Advisor',
      market_timing: 'Market Timing Analyst',
      finance_policy: 'Financial Advisor',
      weather_advisory: 'Weather Specialist',
      general_advisory: 'General Agricultural Advisor'
    };
    return names[agentType] || 'Agricultural Specialist';
  };

  return (
    <div className="gemini-analysis">
      {/* Header */}
      <div className="analysis-header">
        <div className="gemini-logo">🤖</div>
        <div className="header-content">
          <h3>AI Agricultural Analysis</h3>
          <p className="query-text">"{query}"</p>
        </div>
        <div className="confidence-badge">
          <span className="confidence-label">Confidence</span>
          <span className="confidence-value">{Math.round(analysis.confidence * 100)}%</span>
        </div>
      </div>

      {/* Agent and Priority Info */}
      <div className="analysis-meta">
        <div className="agent-info">
          <span className="agent-icon">{getAgentIcon(analysis.agentType)}</span>
          <div>
            <span className="agent-label">Recommended Specialist</span>
            <span className="agent-name">{getAgentName(analysis.agentType)}</span>
          </div>
        </div>
        <div className="priority-info">
          <span 
            className="priority-badge" 
            style={{ backgroundColor: getPriorityColor(analysis.priority) }}
          >
            {analysis.priority.toUpperCase()} PRIORITY
          </span>
        </div>
      </div>

      {/* Main Analysis */}
      <div className="analysis-section">
        <h4>📋 Detailed Analysis</h4>
        <div className="analysis-content">
          {analysis.analysis.split('\n').map((paragraph, index) => (
            paragraph.trim() && (
              <p key={index} className="analysis-paragraph">
                {paragraph.trim()}
              </p>
            )
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h4>💡 Expert Recommendations</h4>
          <div className="recommendations-list">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index} className="recommendation-item">
                <span className="recommendation-number">{index + 1}</span>
                <span className="recommendation-text">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items */}
      {analysis.actionItems.length > 0 && (
        <div className="action-items-section">
          <h4>⚡ Immediate Action Items</h4>
          <div className="action-items-list">
            {analysis.actionItems.map((item, index) => (
              <div key={index} className="action-item">
                <div className="action-checkbox">
                  <input type="checkbox" id={`action-${index}`} />
                  <label htmlFor={`action-${index}`}></label>
                </div>
                <span className="action-text">{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="analysis-footer">
        <div className="powered-by">
          <span>Powered by</span>
          <div className="gemini-brand">
            <span className="gemini-icon">✨</span>
            <span>Google Gemini AI</span>
          </div>
        </div>
        <div className="timestamp">
          Generated at {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default GeminiAnalysisDisplay;
