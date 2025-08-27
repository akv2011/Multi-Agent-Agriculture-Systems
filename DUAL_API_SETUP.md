# 🌾🤖 Agricultural Platform - Dual API Setup

This platform runs two complementary APIs that work together to provide a complete agricultural ecosystem.

## 🏗️ Architecture Overview

### Port 8000 - Unified Agricultural API 🌾 ✅ RUNNING
- **Purpose**: Marketplace, Farmer Profiles, Business Intelligence
- **File**: `unified_agricultural_api.py`
- **Status**: ✅ Active on http://localhost:8000
- **Features**:
  - 🛒 B2B/B2C Marketplace: http://localhost:8000/marketplace/products
  - 👨‍🌾 Farmer Profiles: http://localhost:8000/farmer-profiles
  - 📈 Business Intelligence: http://localhost:8000/business-intel/market-intelligence
  - 🔍 System Status: http://localhost:8000/system/status

### Port 8001 - AgentWeaver API 🤖 ✅ RUNNING
- **Purpose**: AI Agents, Demo Queries, Satellite Analysis
- **File**: `main.py`
- **Status**: ✅ Active on http://localhost:8001
- **Features**:
  - 🔍 Agricultural Query Processing: `/demo/query`
  - 🛰️ Satellite Data Analysis
  - 🤖 Multi-Agent System
  - 🔄 Real-time WebSocket Updates

## 🚀 Current Status - BOTH APIS RUNNING

✅ **Successfully started with**: `python start_both.py`

### Active Endpoints:

**Unified API (Port 8000):**
- 📊 API Documentation: http://localhost:8000/docs
- 🛒 Marketplace Products: http://localhost:8000/marketplace/products
- 👨‍🌾 Farmer Profiles: http://localhost:8000/farmer-profiles
- 📈 Business Intelligence: http://localhost:8000/business-intel/market-intelligence
- 🔍 System Status: http://localhost:8000/system/status

**AgentWeaver API (Port 8001):**
- 📊 API Documentation: http://localhost:8001/docs
- 🔍 Demo Query Endpoint: http://localhost:8001/demo/query
- 💊 Health Check: http://localhost:8001/health
- 🌐 WebSocket Updates: ws://localhost:8001/ws

## 🌐 Frontend Configuration

The frontend automatically connects to the correct APIs:

- **Marketplace, BI, Farmer Profiles** → Port 8000
- **Demo Queries, Satellite Analysis** → Port 8001

### Environment Variables (frontend/.env)
```bash
VITE_API_BASE_URL=http://localhost:8000          # Unified API
VITE_AGENTWEAVER_API_URL=http://localhost:8001   # AgentWeaver API
VITE_GEMINI_API_KEY=your_gemini_api_key_here     # Optional: For AI analysis
```

## 🔧 Development Notes

### Key Differences:
- **Port 8000**: Production-ready unified API for core business functions
- **Port 8001**: Development API with AI agents and experimental features

### Frontend Routing:
- SimpleDemoInterface → Port 8001 (AgentWeaver)
- MarketplacePage → Port 8000 (Unified)
- BusinessIntelligencePage → Port 8000 (Unified)
- FarmerProfilePage → Port 8000 (Unified)

## 🛠️ Troubleshooting

### Common Issues:

1. **Port Conflicts**: Ensure both ports 8000 and 8001 are available
2. **Redis Warnings**: Normal in development mode, uses local storage
3. **Google Credentials**: Optional, system works without them

### Health Checks:
```bash
# Check Unified API
curl http://localhost:8000/

# Check AgentWeaver API  
curl http://localhost:8001/health

# Test Demo Query
curl -X POST http://localhost:8001/demo/query \
  -H "Content-Type: application/json" \
  -d '{"query_text":"test agricultural query"}'
```

## 📝 Recent Fixes Applied

✅ **Gemini API Configuration Removed from UI**
- API key configuration moved to backend only
- Frontend no longer shows Gemini setup interface

✅ **Agriculture Router Fixed**
- Resolved `'str' object has no attribute 'get_next_version'` error
- Proper agent state conversion to dictionary format

✅ **Demo Query Endpoint Added**
- `/demo/query` endpoint now available on port 8001
- Frontend properly routes demo queries to AgentWeaver API

✅ **Dual Port Configuration**
- Clear separation of concerns between the two APIs
- Documented environment variables for frontend configuration

## 🎯 Usage Examples

### For Marketplace/Business Operations:
Visit http://localhost:8000/docs

### For Agricultural AI Analysis:
Visit http://localhost:8001/docs

### Full System Demo:
1. Start both APIs: `python start_both.py`
2. Open frontend application
3. Navigate between different features to see both APIs in action
