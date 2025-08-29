#!/bin/bash

# Voice Agent Setup Verification Script
echo "🎤 Voice Agent Configuration Check"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Run: cp .env.example .env"
    exit 1
fi

echo "✅ .env file found"

# Check ElevenLabs API key
if grep -q "sk_.*" .env; then
    echo "✅ ElevenLabs API key configured"
    ELEVENLABS_OK=true
else
    echo "⚠️  ElevenLabs API key not found or invalid format"
    echo "   Expected format: sk_..."
    ELEVENLABS_OK=false
fi

# Check Gemini API key
GEMINI_KEY=$(grep "VITE_GEMINI_API_KEY=" .env | cut -d'=' -f2)
if [[ "$GEMINI_KEY" != *"your_gemini_api_key_here"* && "$GEMINI_KEY" != "" ]]; then
    echo "✅ Gemini API key configured"
    GEMINI_OK=true
else
    echo "❌ Gemini API key needs to be configured"
    echo "   Get one from: https://makersuite.google.com/app/apikey"
    GEMINI_OK=false
fi

echo
if [ "$ELEVENLABS_OK" = true ] && [ "$GEMINI_OK" = true ]; then
    echo "🎉 Voice Agent Setup Complete!"
    echo "================================="
    echo "✅ All API keys configured"
    echo "✅ Ready to use voice features"
    echo
    echo "🚀 Next Steps:"
    echo "1. Run: npm start"
    echo "2. Test voice features at http://localhost:3000"
    echo "3. Click the microphone button to start voice interaction"
else
    echo "🔧 Next Steps:"
    if [ "$GEMINI_OK" != true ]; then
        echo "1. Get Gemini API key: https://makersuite.google.com/app/apikey"
        echo "2. Add it to your .env file"
        echo "3. Run: npm start"
    fi
    if [ "$ELEVENLABS_OK" != true ]; then
        echo "1. Get ElevenLabs API key: https://elevenlabs.io/app/speech-synthesis"
        echo "2. Add it to your .env file"
        echo "3. Run: npm start"
    fi
    echo "4. Test voice features at http://localhost:3000"
fi

echo ""
echo "📋 Voice Agent Features:"
echo "- Speech-to-text (Gemini AI)"
echo "- Text-to-speech (ElevenLabs)"
echo "- Multi-language support"
echo "- Real-time audio feedback"
echo "- Agricultural query processing"
