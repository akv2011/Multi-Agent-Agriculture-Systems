import React from 'react';
import './GeminiAnalysisDisplay.css'; // Reuse the existing styles for now

interface QueryAnalysisResponse {
  analysis: string;
  recommendations: string[];
  confidence: number;
  agentType: string;
  priority: 'low' | 'medium' | 'high';
  actionItems: string[];
}

interface AIAnalysisDisplayProps {
  analysis: QueryAnalysisResponse;
  isLoading?: boolean;
  query: string;
}

const AIAnalysisDisplay: React.FC<AIAnalysisDisplayProps> = ({ 
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
      weather: '🌤️',
      soil_analysis: '🌱',
      finance_policy: '💰',
      nutrition: '🥬',
      equipment: '🚜',
      default: '🤖'
    };
    return icons[agentType] || icons.default;
  };

  if (!analysis) {
    return (
      <div className="gemini-analysis no-analysis">
        <div className="analysis-header">
          <div className="gemini-logo">🤖</div>
          <h3>AI Agricultural Assistant</h3>
        </div>
        <p>No AI analysis available for this query.</p>
      </div>
    );
  }

  return (
    <div className="gemini-analysis">
      <div className="analysis-header">
        <div className="gemini-logo">🤖</div>
        <h3>AI Agricultural Assistant</h3>
        <div className="confidence-badge">
          {Math.round(analysis.confidence * 100)}% Confidence
        </div>
      </div>

      <div className="query-display">
        <strong>Query:</strong> {query}
      </div>

      <div className="agent-info">
        <div className="agent-type">
          <span className="agent-icon">{getAgentIcon(analysis.agentType)}</span>
          <span className="agent-label">Agent: {analysis.agentType}</span>
        </div>
        <div 
          className="priority-badge"
          style={{ backgroundColor: getPriorityColor(analysis.priority) }}
        >
          {analysis.priority.toUpperCase()} PRIORITY
        </div>
      </div>

      <div className="analysis-section">
        <h4>🔍 Analysis</h4>
        <div className="analysis-content">
          {analysis.analysis}
        </div>
      </div>

      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h4>💡 Recommendations</h4>
          <ul className="recommendations-list">
            {analysis.recommendations.map((rec, index) => (
              <li key={index} className="recommendation-item">
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {analysis.actionItems && analysis.actionItems.length > 0 && (
        <div className="action-items-section">
          <h4>✅ Action Items</h4>
          <ul className="action-items-list">
            {analysis.actionItems.map((item, index) => (
              <li key={index} className="action-item">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="analysis-footer">
        <div className="ai-badge">
          <span className="ai-icon">✨</span>
          <span>Powered by Advanced Agricultural AI</span>
        </div>
      </div>
    </div>
  );
};

export default AIAnalysisDisplay;
