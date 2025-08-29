# Voice Agent Integration Guide

## Overview

The Voice Agent is an advanced feature that adds speech-to-text and text-to-speech capabilities to the Multi-Agent Agriculture System. It combines Google Gemini AI for speech recognition and processing with ElevenLabs for high-quality text-to-speech synthesis.

## Features

### 🎤 Speech-to-Text
- Real-time voice recording with visual feedback
- Audio level monitoring with animated bars
- Advanced speech processing using Google Gemini AI
- Support for multiple languages including Hindi, English, and regional Indian languages
- Automatic noise cancellation and audio enhancement

### 🗣️ Text-to-Speech
- High-quality voice synthesis using ElevenLabs AI
- Multiple voice options with natural-sounding speech
- Auto-speak responses for hands-free operation
- Multilingual support for agricultural responses
- Customizable voice settings and preferences

### 🤖 AI Integration
- **Google Gemini AI**: Advanced speech recognition and natural language processing
- **ElevenLabs**: Premium text-to-speech synthesis with human-like voices
- **Context7**: Integrated documentation and API references for seamless development

## Setup Instructions

### 1. API Keys Configuration

#### Google Gemini AI Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Copy your API key

#### ElevenLabs Setup
1. Visit [ElevenLabs Dashboard](https://elevenlabs.io/app/speech-synthesis)
2. Sign up for an account or log in
3. Navigate to your profile settings
4. Generate an API key
5. Copy your API key

### 2. Environment Configuration

Create a `.env` file in the frontend directory based on the `.env.example`:

```bash
# Copy the example file
cp frontend/.env.example frontend/.env
```

Add your API keys to the `.env` file:

```bash
# Google Gemini AI API Key
REACT_APP_GEMINI_API_KEY=your_actual_gemini_api_key_here
VITE_GEMINI_API_KEY=your_actual_gemini_api_key_here

# ElevenLabs AI API Key  
REACT_APP_ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key_here
VITE_ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key_here
```

### 3. Browser Permissions

The Voice Agent requires microphone access. Ensure your browser:
- Allows microphone access for the application
- Has audio recording permissions enabled
- Supports the Web Audio API (modern browsers)

## Usage Guide

### 🎯 Basic Voice Input

1. **Start Voice Recording**: Click the large circular voice button
2. **Speak Your Query**: Ask any agricultural question in your preferred language
3. **Stop Recording**: Click the button again or wait for automatic detection
4. **Processing**: The system will transcribe and process your query
5. **Response**: Receive both text and audio responses

### ⚙️ Voice Settings Configuration

Click the settings gear icon to configure:

#### Audio Settings
- **Voice Selection**: Choose from available ElevenLabs voices
- **Language**: Set speech recognition language preference
- **Auto-speak**: Enable/disable automatic response reading

#### API Configuration
- **Gemini API Key**: Configure your Google AI credentials
- **ElevenLabs API Key**: Set up your voice synthesis credentials

### 🎧 Voice Interaction Flow

```
👤 User speaks → 🎤 Audio capture → 🧠 Gemini processing → 📝 Text transcription → 
🤖 AgriMitr analysis → 💬 Response generation → 🗣️ ElevenLabs synthesis → 🔊 Audio playback
```

## Supported Languages

### Speech Recognition (Gemini AI)
- English
- Hindi (हिंदी)
- Marathi (मराठी)
- Punjabi (ਪੰਜਾਬੀ)
- Gujarati (ગુજરાતી)
- Bengali (বাংলা)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)

### Text-to-Speech (ElevenLabs)
- Multilingual voices supporting Indian languages
- Regional accent variations
- Gender-specific voice options
- Professional and conversational tones

## Technical Architecture

### Components

#### VoiceAgent.tsx
- Main voice interface component
- Handles audio recording and playback
- Manages API interactions
- Provides visual feedback

#### VoiceAgent.css
- Responsive design styles
- Animated visual indicators
- Dark mode support
- Mobile-friendly interface

### APIs Integration

#### Google Gemini AI
```typescript
// Speech-to-text processing
const transcription = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    contents: [{
      parts: [{
        text: "Please transcribe the following audio to text.",
      }, {
        inline_data: {
          mime_type: "audio/webm",
          data: base64Audio
        }
      }]
    }]
  })
});
```

#### ElevenLabs
```typescript
// Text-to-speech synthesis
const audioResponse = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`, {
  method: 'POST',
  headers: {
    'Accept': 'audio/mpeg',
    'Content-Type': 'application/json',
    'xi-api-key': apiKey
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
```

## Features in Detail

### 🎨 Visual Indicators

#### Listening State
- Pulsing blue gradient
- Animated audio level bars
- Real-time volume visualization
- Floating microphone icon

#### Speaking State
- Purple gradient with animation
- Sound wave visualization
- Speaker icon with bounce effect
- Smooth audio playback indication

#### Processing State
- Loading spinner overlay
- Status text updates
- Progress indicators
- Error handling display

### 🔒 Security Features

- API keys stored in environment variables
- No credentials in source code
- Secure HTTPS API communications
- Base64 encoding for audio data
- Input validation and sanitization

### 📱 Responsive Design

- Mobile-friendly touch interfaces
- Adaptive button sizing
- Accessible keyboard navigation
- Screen reader compatibility
- High contrast support

## Troubleshooting

### Common Issues

#### Microphone Access Denied
- **Solution**: Enable microphone permissions in browser settings
- **Chrome**: Settings → Privacy → Site Settings → Microphone
- **Firefox**: Preferences → Privacy & Security → Permissions

#### API Key Errors
- **Gemini**: Verify key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **ElevenLabs**: Check quota and key validity at [ElevenLabs Dashboard](https://elevenlabs.io)

#### Audio Playback Issues
- **Solution**: Check browser audio settings
- Ensure audio output device is working
- Try different voice selections

#### Network Connectivity
- **Solution**: Verify API endpoints are accessible
- Check firewall and proxy settings
- Test with sample API calls

### Performance Optimization

#### Audio Quality
```typescript
// Optimized MediaRecorder settings
const recorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm;codecs=opus',
  audioBitsPerSecond: 16000
});
```

#### Caching
- Voice samples cached for repeated queries
- Audio buffers managed for memory efficiency
- API response caching for common requests

## Development

### Testing

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test
```

### Building

```bash
# Production build
npm run build

# Serve production build
npm run preview
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add voice-related enhancements
4. Test with different languages
5. Submit a pull request

## Future Enhancements

### Planned Features
- **Real-time Streaming**: Live audio processing
- **Voice Commands**: Agricultural action triggers
- **Multilingual Mixing**: Code-switching support
- **Voice Profiles**: User-specific voice settings
- **Offline Mode**: Local speech processing

### API Improvements
- **WebRTC Integration**: Reduced latency
- **Custom Voice Training**: Farmer-specific accents
- **Agricultural Vocabulary**: Domain-specific terms
- **Contextual Understanding**: Farm environment awareness

## Support

For technical support:
- 📧 Email: support@agrisens.io
- 📚 Documentation: [AgriMitr Docs](https://docs.agrisens.io)
- 🐛 Issues: [GitHub Issues](https://github.com/akv2011/Multi-Agent-Agriculture-Systems/issues)
- 💬 Community: [Discord Server](https://discord.gg/agrisens)

## License

This voice agent integration is part of the Multi-Agent Agriculture Systems project and is licensed under the MIT License. See LICENSE file for details.

---

**Made with ❤️ for farmers worldwide by the AgriMitr team**
