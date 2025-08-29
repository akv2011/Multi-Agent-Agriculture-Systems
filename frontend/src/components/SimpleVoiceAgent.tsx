import React, { useState } from 'react';

interface SimpleVoiceAgentProps {
  onVoiceQuery: (query: string) => void;
  isProcessing?: boolean;
}

const SimpleVoiceAgent: React.FC<SimpleVoiceAgentProps> = ({ onVoiceQuery, isProcessing }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  const handleVoiceClick = () => {
    console.log('Voice button clicked!');
    
    if (isListening) {
      // Stop listening
      setIsListening(false);
      setTranscript('Voice recording stopped');
    } else {
      // Start listening (simulated for now)
      setIsListening(true);
      setTranscript('Listening... (This is a test)');
      
      // Simulate voice input after 3 seconds
      setTimeout(() => {
        setIsListening(false);
        const testQuery = "What is the best irrigation method for wheat crops?";
        setTranscript(`Heard: "${testQuery}"`);
        onVoiceQuery(testQuery);
      }, 3000);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '10px',
      padding: '10px'
    }}>
      {/* Large, visible voice button */}
      <button
        onClick={handleVoiceClick}
        disabled={isProcessing}
        style={{
          width: '80px',
          height: '80px',
          borderRadius: '50%',
          border: 'none',
          background: isListening 
            ? 'linear-gradient(145deg, #4ecdc4, #44a08d)' 
            : 'linear-gradient(145deg, #ff6b6b, #ee5a52)',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        {isListening ? '🛑' : '🎤'}
      </button>

      {/* Status text */}
      <div style={{
        fontSize: '14px',
        fontWeight: 'bold',
        color: isListening ? '#4ecdc4' : '#666',
        textAlign: 'center'
      }}>
        {isListening ? 'Listening...' : 'Click to speak'}
      </div>

      {/* Transcript display */}
      {transcript && (
        <div style={{
          fontSize: '12px',
          color: '#888',
          textAlign: 'center',
          maxWidth: '200px',
          padding: '5px 10px',
          background: '#f5f5f5',
          borderRadius: '8px',
          border: '1px solid #ddd'
        }}>
          {transcript}
        </div>
      )}
    </div>
  );
};

export default SimpleVoiceAgent;
