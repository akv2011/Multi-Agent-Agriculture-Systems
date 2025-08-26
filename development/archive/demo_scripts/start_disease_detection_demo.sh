#!/bin/bash
# Quick start script for testing the enhanced image upload functionality

echo "🌱 Starting AgriSens Disease Detection Demo with Enhanced Image Upload"
echo "======================================================================="

# Go to the project root
cd /home/hari/Music/Multi-Agent-Agriculture-Systems

echo "📋 Checking environment..."

# Check if .env exists and has required keys
if [ -f ".env" ]; then
    echo "✅ .env file found"
    if grep -q "GEMINI_API_KEY" .env; then
        echo "✅ Gemini API key configured"
    else
        echo "⚠️ Gemini API key not found in .env"
    fi
else
    echo "❌ .env file not found"
fi

# Check if frontend dependencies are installed
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo ""
echo "🚀 Starting services..."

# Start the backend API in background
echo "🔧 Starting backend API server..."
python run_api.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Start the frontend dev server
echo "🎨 Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for services to start
sleep 5

echo ""
echo "✨ Services started successfully!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo ""
echo "📸 Testing the Enhanced Image Upload:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Look for the camera icon (📷) in the query input area"
echo "3. Click the camera icon to upload a plant/leaf image"
echo "4. Notice the instant image preview"
echo "5. See disease-specific example queries appear"
echo "6. Try sending a message with the image attached"
echo ""
echo "🛑 To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or press Ctrl+C in this terminal"

# Keep the script running
echo "Press Ctrl+C to stop all services..."
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for user to stop
wait
