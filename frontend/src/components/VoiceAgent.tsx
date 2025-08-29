import React, { useState, useRef, useCallback, useEffect } from 'react';
import './VoiceAgent.css';

interface VoiceAgentProps {
  onVoiceQuery: (query: string) => void;
  isProcessing: boolean;
  response?: string;
}

interface VoiceSettings {
  geminiApiKey: string;
  elevenLabsApiKey: string;
  selectedVoice: string;
  language: string;
  autoSpeak: boolean;
}

const VoiceAgent: React.FC<VoiceAgentProps> = ({ onVoiceQuery, isProcessing, response }) => {
  // State management
  const viteEnv: Record<string, string> = (typeof import.meta !== 'undefined' && (import.meta as { env?: Record<string, string> }).env) ? (import.meta as { env: Record<string, string> }).env : {};
  const initialGeminiKey =
    viteEnv.VITE_GEMINI_API_KEY ||
    viteEnv.REACT_APP_GEMINI_API_KEY ||
    '';
  const initialElevenKey =
    viteEnv.VITE_ELEVENLABS_API_KEY ||
    viteEnv.REACT_APP_ELEVENLABS_API_KEY ||
    '';
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [settings, setSettings] = useState<VoiceSettings>({
    geminiApiKey: initialGeminiKey,
    elevenLabsApiKey: initialElevenKey,
    selectedVoice: 'JBFqnCBsd6RMkjVDRZzb', // Default ElevenLabs voice
    language: 'auto',
    autoSpeak: true
  });
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<Array<{ voice_id: string; name: string; category?: string }>>([]);

  // Refs for audio handling
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioQueueRef = useRef<HTMLAudioElement[]>([]);

  // Initialize audio context and load voices
  useEffect(() => {
    initializeAudioContext();
    loadAvailableVoices();
    
    return () => {
      cleanup();
    };
  }, []);

  // Auto-speak response when received
  useEffect(() => {
    if (response && settings.autoSpeak && !isProcessing) {
      speakText(response);
    }
  }, [response, settings.autoSpeak, isProcessing]);

  const initializeAudioContext = useCallback(async () => {
    try {
      const AudioContextClass = window.AudioContext || (window as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (AudioContextClass) {
        audioContextRef.current = new AudioContextClass();
      }
    } catch (error) {
      console.error('Failed to initialize audio context:', error);
    }
  }, []);

  const loadAvailableVoices = useCallback(async () => {
    if (!settings.elevenLabsApiKey) return;

    try {
      const response = await fetch('https://api.elevenlabs.io/v1/voices', {
        headers: {
          'xi-api-key': settings.elevenLabsApiKey
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableVoices(data.voices || []);
      }
    } catch (error) {
      console.error('Failed to load voices:', error);
    }
  }, [settings.elevenLabsApiKey]);

  const cleanup = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    // Stop any playing audio
    audioQueueRef.current.forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
    audioQueueRef.current = [];
  }, []);

  const startListening = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        } 
      });

      audioStreamRef.current = stream;

      // Set up audio analysis for visual feedback
      if (audioContextRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        source.connect(analyserRef.current);

        // Start audio level monitoring
        monitorAudioLevel();
      }

      // Set up MediaRecorder for Gemini Live API
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      const audioChunks: Blob[] = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        if (audioChunks.length > 0) {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
          await processAudioWithGemini(audioBlob);
        }
      };

      // Start recording
      mediaRecorderRef.current.start(1000); // Collect data every second
      setIsListening(true);
      setTranscript('Listening...');

    } catch (error) {
      console.error('Error starting voice recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  }, []);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }
    setIsListening(false);
    setAudioLevel(0);
  }, []);

  const monitorAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateLevel = () => {
      if (!isListening || !analyserRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
      setAudioLevel(average / 255);

      requestAnimationFrame(updateLevel);
    };

    updateLevel();
  }, [isListening]);

  const processAudioWithGemini = useCallback(async (audioBlob: Blob) => {
    if (!settings.geminiApiKey) {
      alert('Please configure Gemini API key in settings');
      return;
    }

    try {
      setTranscript('Processing...');

      // Convert audio to base64
      const audioBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(audioBuffer)));

      // Use Gemini for speech-to-text
      const geminiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${settings.geminiApiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: "Please transcribe the following audio to text. Only return the transcribed text, nothing else."
            }, {
              inline_data: {
                mime_type: "audio/webm",
                data: base64Audio
              }
            }]
          }]
        })
      });

      if (geminiResponse.ok) {
        const data = await geminiResponse.json();
        const transcribedText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
        
        if (transcribedText.trim()) {
          setTranscript(transcribedText);
          onVoiceQuery(transcribedText);
        } else {
          setTranscript('Could not understand audio. Please try again.');
        }
      } else {
        throw new Error('Failed to transcribe audio');
      }

    } catch (error) {
      console.error('Error processing audio:', error);
      setTranscript('Error processing audio. Please try again.');
    }
  }, [settings.geminiApiKey, onVoiceQuery]);

  const speakText = useCallback(async (text: string) => {
    if (!settings.elevenLabsApiKey || !text.trim()) return;

    try {
      setIsSpeaking(true);

      // Use ElevenLabs for text-to-speech
      const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${settings.selectedVoice}/stream`, {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': settings.elevenLabsApiKey
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_multilingual_v2',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.5,
            style: 0.2,
            use_speaker_boost: true
          }
        })
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Add to queue for cleanup
        audioQueueRef.current.push(audio);

        audio.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
          // Remove from queue
          audioQueueRef.current = audioQueueRef.current.filter(a => a !== audio);
        };

        audio.onerror = () => {
          setIsSpeaking(false);
          console.error('Error playing audio');
        };

        await audio.play();
      } else {
        throw new Error('Failed to generate speech');
      }

    } catch (error) {
      console.error('Error generating speech:', error);
      setIsSpeaking(false);
    }
  }, [settings.elevenLabsApiKey, settings.selectedVoice]);

  const toggleVoiceRecording = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  const handleSettingsChange = useCallback((key: keyof VoiceSettings, value: string | boolean) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  return (
    <div className="voice-agent">
      <div className="voice-controls">
        <button
          className={`voice-button ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''}`}
          onClick={toggleVoiceRecording}
          disabled={isProcessing}
          title={isListening ? 'Stop listening' : 'Start voice input'}
        >
          <div className="voice-button-content">
            {isListening ? (
              <div className="listening-indicator">
                <div className="mic-icon">🎤</div>
                <div className="audio-bars">
                  {[...Array(5)].map((_, i) => (
                    <div 
                      key={i}
                      className="audio-bar"
                      style={{ 
                        height: `${Math.max(20, audioLevel * 100 * (1 + Math.random() * 0.5))}%`,
                        animationDelay: `${i * 0.1}s`
                      }}
                    />
                  ))}
                </div>
              </div>
            ) : isSpeaking ? (
              <div className="speaking-indicator">
                <div className="speaker-icon">🔊</div>
                <div className="sound-waves">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className={`sound-wave wave-${i + 1}`} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="idle-state">
                <div className="mic-icon">🎤</div>
                <span>Voice Input</span>
              </div>
            )}
          </div>
        </button>

        <button
          className="settings-button"
          onClick={() => setIsConfigOpen(!isConfigOpen)}
          title="Voice settings"
        >
          ⚙️
        </button>
      </div>

      {transcript && (
        <div className="transcript-display">
          <div className="transcript-label">Voice Input:</div>
          <div className="transcript-text">{transcript}</div>
        </div>
      )}

      {isConfigOpen && (
        <div className="voice-settings">
          <div className="settings-header">
            <h3>Voice Agent Settings</h3>
            <button
              className="close-settings"
              onClick={() => setIsConfigOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="settings-content">
            <div className="setting-group">
              <label>Gemini API Key:</label>
              <input
                type="password"
                value={settings.geminiApiKey}
                onChange={(e) => handleSettingsChange('geminiApiKey', e.target.value)}
                placeholder="Enter your Gemini API key"
              />
            </div>

            <div className="setting-group">
              <label>ElevenLabs API Key:</label>
              <input
                type="password"
                value={settings.elevenLabsApiKey}
                onChange={(e) => handleSettingsChange('elevenLabsApiKey', e.target.value)}
                placeholder="Enter your ElevenLabs API key"
                onBlur={loadAvailableVoices}
              />
            </div>

            <div className="setting-group">
              <label>Voice:</label>
              <select
                value={settings.selectedVoice}
                onChange={(e) => handleSettingsChange('selectedVoice', e.target.value)}
              >
                <option value="JBFqnCBsd6RMkjVDRZzb">Default Voice</option>
                {availableVoices.map(voice => (
                  <option key={voice.voice_id} value={voice.voice_id}>
                    {voice.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="setting-group">
              <label>Language:</label>
              <select
                value={settings.language}
                onChange={(e) => handleSettingsChange('language', e.target.value)}
              >
                <option value="auto">Auto Detect</option>
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="mr">Marathi</option>
                <option value="pa">Punjabi</option>
                <option value="gu">Gujarati</option>
                <option value="bn">Bengali</option>
                <option value="ta">Tamil</option>
                <option value="te">Telugu</option>
                <option value="kn">Kannada</option>
                <option value="ml">Malayalam</option>
              </select>
            </div>

            <div className="setting-group">
              <label>
                <input
                  type="checkbox"
                  checked={settings.autoSpeak}
                  onChange={(e) => handleSettingsChange('autoSpeak', e.target.checked)}
                />
                Auto-speak responses
              </label>
            </div>

            <div className="settings-info">
              <p><strong>Setup Instructions:</strong></p>
              <ol>
                <li>Get your Gemini API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a></li>
                <li>Get your ElevenLabs API key from <a href="https://elevenlabs.io/app/speech-synthesis" target="_blank" rel="noopener noreferrer">ElevenLabs Dashboard</a></li>
                <li>Choose your preferred voice and language settings</li>
                <li>Enable auto-speak to hear responses automatically</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      <div className="voice-status">
        {isListening && (
          <div className="status-item listening">
            <span className="status-icon">👂</span>
            <span>Listening...</span>
          </div>
        )}
        {isProcessing && (
          <div className="status-item processing">
            <span className="status-icon">🧠</span>
            <span>Processing query...</span>
          </div>
        )}
        {isSpeaking && (
          <div className="status-item speaking">
            <span className="status-icon">🗣️</span>
            <span>Speaking response...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAgent;
