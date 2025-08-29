#!/bin/bash

# Voice Agent Demo Script for Multi-Agent Agriculture Systems
# This script demonstrates the voice agent capabilities

echo "🌾 AgriMitr Voice Agent Demo Setup"
echo "================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the frontend directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please add your API keys:"
    echo "   - REACT_APP_GEMINI_API_KEY"
    echo "   - REACT_APP_ELEVENLABS_API_KEY"
    echo ""
    echo "🔗 Get your API keys from:"
    echo "   - Gemini: https://makersuite.google.com/app/apikey"
    echo "   - ElevenLabs: https://elevenlabs.io/app/speech-synthesis"
    echo ""
    echo "💡 After adding API keys, run this script again to start the demo"
    exit 0
fi

# Check if API keys are configured
if ! grep -q "your_.*_api_key_here" .env; then
    echo "✅ API keys appear to be configured"
else
    echo "⚠️  Warning: Default API key placeholders detected"
    echo "   Please update your .env file with actual API keys"
fi

echo ""
echo "🚀 Starting Voice Agent Demo..."
echo ""
echo "📋 Demo Instructions:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Allow microphone access when prompted"
echo "   3. Click the voice button (🎤) to start speaking"
echo "   4. Ask agricultural questions like:"
echo "      - 'What crops should I plant this season?'"
echo "      - 'How do I treat wheat rust disease?'"
echo "      - 'What's the best irrigation schedule for rice?'"
echo "   5. The system will transcribe, process, and respond with voice"
echo ""
echo "⚙️  Voice Agent Features:"
echo "   - Real-time speech recognition (Gemini AI)"
echo "   - Natural language processing"
echo "   - High-quality text-to-speech (ElevenLabs)"
echo "   - Multi-language support"
echo "   - Visual audio feedback"
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server..."
npm start

echo ""
echo "🎉 Voice Agent Demo Complete!"
echo ""
echo "💡 Tips for best results:"
echo "   - Speak clearly and at normal pace"
echo "   - Use agricultural terminology"
echo "   - Try different languages (Hindi, English, etc.)"
echo "   - Configure voice settings via the gear icon"
echo ""
echo "📚 For more information, see VOICE_AGENT_README.md"
