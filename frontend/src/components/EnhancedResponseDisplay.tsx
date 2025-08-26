import React from 'react';
import './EnhancedResponseDisplay.css';

interface EnhancedResponseDisplayProps {
  originalQuery: string;
  enhancedResponse: string;
  isLoading?: boolean;
  error?: string;
}

const EnhancedResponseDisplay: React.FC<EnhancedResponseDisplayProps> = ({
  originalQuery,
  enhancedResponse,
  isLoading = false,
  error
}) => {
  if (isLoading) {
    return (
      <div className="enhanced-response loading">
        <div className="loading-header">
          <div className="gemini-icon">🤖</div>
          <h3>Enhancing Response with AI</h3>
          <div className="loading-spinner"></div>
        </div>
        <p>Processing your query through advanced agricultural AI for comprehensive insights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="enhanced-response error">
        <div className="error-header">
          <div className="error-icon">⚠️</div>
          <h3>AI Enhancement Failed</h3>
        </div>
        <p className="error-message">{error}</p>
        <p className="error-suggestion">
          Please check your Gemini API key configuration or try again later.
        </p>
      </div>
    );
  }

  // Parse the enhanced response into sections
  const parseResponse = (text: string) => {
    const sections: { [key: string]: string[] } = {};
    const lines = text.split('\n');
    let currentSection = 'overview';
    let currentContent: string[] = [];

    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // Check if this is a heading
      if (trimmedLine.match(/^\*\*.*\*\*:?$/) || trimmedLine.match(/^#+\s/)) {
        // Save previous section
        if (currentContent.length > 0) {
          sections[currentSection] = currentContent;
        }
        
        // Start new section
        const heading = trimmedLine.replace(/^\*\*|\*\*:?$|^#+\s/g, '').toLowerCase();
        currentSection = heading.replace(/[^a-z0-9]/g, '_');
        currentContent = [];
      } else if (trimmedLine) {
        currentContent.push(trimmedLine);
      }
    }
    
    // Save last section
    if (currentContent.length > 0) {
      sections[currentSection] = currentContent;
    }

    return sections;
  };

  const sections = parseResponse(enhancedResponse);

  const formatContent = (content: string[]) => {
    return content.map((item, index) => {
      // Handle bullet points
      if (item.match(/^[-*•]\s/)) {
        return (
          <li key={index} className="bullet-item">
            {item.replace(/^[-*•]\s/, '')}
          </li>
        );
      }
      
      // Handle numbered lists
      if (item.match(/^\d+\.\s/)) {
        return (
          <li key={index} className="numbered-item">
            {item.replace(/^\d+\.\s/, '')}
          </li>
        );
      }
      
      // Regular paragraph
      return (
        <p key={index} className="content-paragraph">
          {item}
        </p>
      );
    });
  };

  const getSectionIcon = (sectionKey: string) => {
    const icons: { [key: string]: string } = {
      overview: '📋',
      implementation: '🔧',
      cost: '💰',
      timing: '⏰',
      prevention: '🛡️',
      recommendations: '💡',
      steps: '📝',
      materials: '🧰',
      follow_up: '📅',
      seasonal: '🌱',
      local_context: '🏘️'
    };
    
    return icons[sectionKey] || '📌';
  };

  const getSectionTitle = (sectionKey: string) => {
    const titles: { [key: string]: string } = {
      overview: 'Overview & Analysis',
      implementation: 'Implementation Guide',
      cost: 'Cost Analysis',
      timing: 'Timing & Schedule',
      prevention: 'Prevention Measures',
      recommendations: 'Expert Recommendations',
      steps: 'Step-by-Step Instructions',
      materials: 'Required Materials',
      follow_up: 'Follow-up Actions',
      seasonal: 'Seasonal Considerations',
      local_context: 'Local Context & Resources'
    };
    
    return titles[sectionKey] || sectionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="enhanced-response">
      {/* Header */}
      <div className="response-header">
        <div className="gemini-icon">🤖</div>
        <div className="header-content">
          <h3>AI-Enhanced Agricultural Guidance</h3>
          <p className="query-display">"{originalQuery}"</p>
        </div>
        <div className="enhancement-badge">
          <span className="badge-text">Enhanced by Gemini AI</span>
        </div>
      </div>

      {/* Enhanced Content */}
      <div className="response-content">
        {Object.keys(sections).length === 0 ? (
          // Fallback for unstructured response
          <div className="content-section">
            <div className="section-header">
              <span className="section-icon">📋</span>
              <h4>Agricultural Guidance</h4>
            </div>
            <div className="section-content">
              {enhancedResponse.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <p key={index} className="content-paragraph">
                    {paragraph.trim()}
                  </p>
                )
              ))}
            </div>
          </div>
        ) : (
          // Structured sections
          Object.entries(sections).map(([sectionKey, content]) => (
            <div key={sectionKey} className="content-section">
              <div className="section-header">
                <span className="section-icon">{getSectionIcon(sectionKey)}</span>
                <h4>{getSectionTitle(sectionKey)}</h4>
              </div>
              <div className="section-content">
                {content.some(item => item.match(/^[-*•]\s/) || item.match(/^\d+\.\s/)) ? (
                  <ul className="content-list">
                    {formatContent(content)}
                  </ul>
                ) : (
                  formatContent(content)
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="response-footer">
        <div className="ai-attribution">
          <span className="gemini-logo">✨</span>
          <span>Enhanced with Google Gemini AI</span>
        </div>
        <div className="timestamp">
          Generated at {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default EnhancedResponseDisplay;
