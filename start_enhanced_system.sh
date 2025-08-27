#!/bin/bash

# Enhanced Agriculture System Startup Script
# Coordinates the startup of all components for the enhanced system

echo "🌾🛰️ Starting Enhanced Multi-Agent Agriculture System"
echo "=================================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to wait for service to start
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to start..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $name failed to start within timeout"
    return 1
}

# Check prerequisites
echo ""
echo "🔍 Checking Prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi
echo "✅ Python3 is available"

# Check if we're in the right directory
if [ ! -f "enhanced_demo_api.py" ]; then
    echo "❌ enhanced_demo_api.py not found. Make sure you're in the project root directory."
    exit 1
fi
echo "✅ Enhanced API script found"

# Check required directories
if [ ! -d "src" ]; then
    echo "❌ src directory not found"
    exit 1
fi
echo "✅ Source directory found"

# Install dependencies if needed
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt not found, creating basic one..."
    cat > requirements.txt << EOF
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
aiofiles>=23.2.1
websockets>=12.0
requests>=2.31.0
sqlalchemy>=2.0.23
sqlite>=3.40.0
python-dateutil>=2.8.2
EOF
fi

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have issues, continuing anyway..."
fi

# Check ports
echo ""
echo "🔌 Checking Ports..."

if ! check_port 8001; then
    echo "💡 Tip: Use 'lsof -ti:8001 | xargs kill' to free the port"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the enhanced demo API
echo ""
echo "🚀 Starting Enhanced Demo API Server..."
echo "   URL: http://localhost:8001"
echo "   Docs: http://localhost:8001/docs"
echo "   Dashboard: http://localhost:8001/dashboard"
echo ""

# Start in background and capture PID
nohup python3 enhanced_demo_api.py > enhanced_api.log 2>&1 &
API_PID=$!
echo "📝 API Server PID: $API_PID"

# Wait for API to be ready
if wait_for_service "http://localhost:8001/demo/health" "Enhanced API"; then
    echo ""
    echo "🎉 Enhanced Agriculture System is now running!"
    echo ""
    echo "📊 Available Endpoints:"
    echo "   • Main API: http://localhost:8001"
    echo "   • Health Check: http://localhost:8001/demo/health"
    echo "   • Dashboard Metrics: http://localhost:8001/demo/dashboard"
    echo "   • System Status: http://localhost:8001/demo/status"
    echo "   • Query Processing: http://localhost:8001/demo/query"
    echo "   • Analytics: http://localhost:8001/demo/analytics"
    echo "   • API Documentation: http://localhost:8001/docs"
    echo ""
    echo "🧪 Testing:"
    echo "   • Run: python3 test_enhanced_api.py"
    echo "   • Or use the frontend interface"
    echo ""
    echo "📝 Logs:"
    echo "   • API Logs: tail -f enhanced_api.log"
    echo ""
    echo "🛑 To Stop:"
    echo "   • Press Ctrl+C or run: kill $API_PID"
    echo ""
    
    # Save PID for cleanup
    echo $API_PID > .enhanced_api.pid
    
    # Optional: Start a simple test
    read -p "🧪 Run a quick test now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔬 Running Quick Test..."
        python3 test_enhanced_api.py
    fi
    
    echo ""
    echo "✨ System is ready for enhanced query processing!"
    echo "   Submit queries and watch the real-time dashboard updates"
    
    # Keep script running to monitor
    echo ""
    echo "🔄 Monitoring system... (Press Ctrl+C to stop)"
    
    # Monitor the service
    while kill -0 $API_PID 2>/dev/null; do
        sleep 5
    done
    
    echo "❌ API Server stopped unexpectedly"
    
else
    echo "❌ Failed to start Enhanced API"
    kill $API_PID 2>/dev/null
    exit 1
fi
