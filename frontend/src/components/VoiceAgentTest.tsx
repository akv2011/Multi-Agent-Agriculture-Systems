import React, { useState } from 'react';
import VoiceAgent from './VoiceAgent';
import './VoiceAgentTest.css';

/**
 * Voice Agent Test Component
 * 
 * This component provides a standalone test environment for the Voice Agent
 * to verify speech-to-text and text-to-speech functionality independently
 * from the main agriculture interface.
 */
const VoiceAgentTest: React.FC = () => {
  const [lastQuery, setLastQuery] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [simulatedResponse, setSimulatedResponse] = useState<string>('');
  const [testHistory, setTestHistory] = useState<Array<{
    query: string;
    response: string;
    timestamp: Date;
  }>>([]);

  // Sample agricultural responses for testing
  const sampleResponses = [
    "Based on your location and current season, I recommend planting wheat and mustard crops. These are well-suited for the winter season in North India.",
    "For wheat rust disease, apply a fungicide containing propiconazole. Also ensure proper field drainage and avoid over-irrigation.",
    "Rice crops need about 2-3 inches of water per week. Maintain 2-inch standing water during tillering and reduce to moist soil during maturity.",
    "Current market prices show wheat at ₹2,100 per quintal. I suggest waiting 2-3 weeks as prices are expected to rise by 8-10%.",
    "For organic farming, use neem-based pesticides and vermicompost. Crop rotation with legumes will improve soil fertility naturally."
  ];

  const handleVoiceQuery = (query: string) => {
    setLastQuery(query);
    setIsProcessing(true);

    // Simulate processing delay
    setTimeout(() => {
      const randomResponse = sampleResponses[Math.floor(Math.random() * sampleResponses.length)];
      setSimulatedResponse(randomResponse);
      
      // Add to test history
      setTestHistory(prev => [{
        query,
        response: randomResponse,
        timestamp: new Date()
      }, ...prev.slice(0, 4)]);
      
      setIsProcessing(false);
    }, 2000);
  };

  const clearHistory = () => {
    setTestHistory([]);
    setLastQuery('');
    setSimulatedResponse('');
  };

  const testTextToSpeech = () => {
    const testMessage = "This is a test of the text-to-speech functionality. The voice agent is working correctly.";
    setSimulatedResponse(testMessage);
  };

  return (
    <div className="voice-agent-test">
      <div className="test-header">
        <h1>🎤 Voice Agent Test Environment</h1>
        <p>Test speech-to-text and text-to-speech functionality independently</p>
      </div>

      <div className="test-content">
        {/* Voice Agent Component */}
        <div className="voice-agent-section">
          <h2>Voice Agent</h2>
          <VoiceAgent
            onVoiceQuery={handleVoiceQuery}
            isProcessing={isProcessing}
            response={simulatedResponse}
          />
        </div>

        {/* Test Controls */}
        <div className="test-controls">
          <h3>Test Controls</h3>
          <div className="control-buttons">
            <button onClick={testTextToSpeech} className="test-button">
              🗣️ Test Text-to-Speech
            </button>
            <button onClick={clearHistory} className="test-button">
              🗑️ Clear History
            </button>
          </div>
        </div>

        {/* Current Query Display */}
        <div className="current-query">
          <h3>Latest Voice Input</h3>
          <div className="query-display">
            {lastQuery || 'No voice input yet. Click the microphone to start.'}
          </div>
        </div>

        {/* Response Display */}
        <div className="response-section">
          <h3>AI Response</h3>
          <div className="response-display">
            {isProcessing ? (
              <div className="processing">
                <span className="spinner"></span>
                Processing your agricultural query...
              </div>
            ) : (
              simulatedResponse || 'No response yet. Ask a voice question first.'
            )}
          </div>
        </div>

        {/* Test History */}
        <div className="test-history">
          <h3>Test History</h3>
          {testHistory.length === 0 ? (
            <p className="no-history">No tests performed yet.</p>
          ) : (
            <div className="history-list">
              {testHistory.map((test, index) => (
                <div key={index} className="history-item">
                  <div className="history-timestamp">
                    {test.timestamp.toLocaleTimeString()}
                  </div>
                  <div className="history-query">
                    <strong>Q:</strong> {test.query}
                  </div>
                  <div className="history-response">
                    <strong>A:</strong> {test.response}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Setup Instructions */}
        <div className="setup-instructions">
          <h3>Setup Instructions</h3>
          <div className="instructions-content">
            <ol>
              <li>Ensure you have configured API keys in your .env file</li>
              <li>Grant microphone permissions when prompted</li>
              <li>Click the voice button and speak clearly</li>
              <li>Wait for transcription and response</li>
              <li>Check audio output is enabled for text-to-speech</li>
            </ol>
            
            <div className="api-links">
              <p><strong>Get API Keys:</strong></p>
              <ul>
                <li>
                  <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">
                    Google Gemini API Key
                  </a>
                </li>
                <li>
                  <a href="https://elevenlabs.io/app/speech-synthesis" target="_blank" rel="noopener noreferrer">
                    ElevenLabs API Key
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceAgentTest;
