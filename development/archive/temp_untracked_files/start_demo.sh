#!/bin/bash
echo "🚀 AgentWeaver Multi-Agent System Demo"
echo "======================================"
echo ""

# Check if we're already in a conda environment
if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "✅ Using conda environment: $CONDA_DEFAULT_ENV"
else
    echo "💡 Consider using conda environment for better dependency management"
    echo "   Run: conda create -n agentweaver python=3.11 -y && conda activate agentweaver"
fi

echo ""
echo "📊 Starting backend server..."
echo "   API docs will be available at: http://localhost:8000/docs"

# Start backend in background
python demo_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo ""
echo "🎨 Starting frontend development server..."
echo "   Dashboard will be available at: http://localhost:5173"

cd frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
