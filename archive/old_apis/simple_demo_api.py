#!/usr/bin/env python3
"""
Simple Demo API Server
Provides the same output as demo_presentation.py but through API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import time

app = FastAPI(
    title="🌾🛰️ Multi-Agent Agriculture Demo API",
    description="Satellite-Enhanced AI Agricultural Advisory System",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query_text: str
    language: Optional[str] = None
    location: Optional[str] = "punjab_ludhiana"

class QueryResponse(BaseModel):
    status: str
    query_id: str
    original_query: str
    routing_analysis: Dict[str, Any]
    satellite_data: Dict[str, Any]
    response_text: str
    technical_metrics: Dict[str, Any]
    timestamp: str

# Hardcoded demo responses matching your script exactly
DEMO_RESPONSES = {
    "crop_selection_hindi": """🌾 नमस्ते किसान भाई! पंजाब में गेहूं की बेहतरीन किस्में:

**🛰️ उपग्रह डेटा विश्लेषण:**
• NDVI स्कोर: 0.72 (अच्छी मिट्टी की स्थिति)
• मिट्टी में नमी: 45%
• पर्यावरणीय स्कोर: 78/100

**सुझावी किस्में:**
1. **HD-2967**: उच्च उत्पादन (45-50 क्विंटल/एकड़)
2. **PBW-343**: रोग प्रतिरोधी, सिंचाई वाले क्षेत्रों के लिए
3. **DBW-88**: देर से बुआई के लिए उत्तम

**🛰️ उपग्रह सिफारिश:** मौजूदा मिट्टी की स्थिति के अनुसार HD-2967 सबसे उपयुक्त है।
**विश्वसनीयता:** 95% ✅""",

    "pest_management_mixed": """🐛 कॉटन में पीले पत्ते - Satellite Analysis:

**🛰️ Field Health Status:**
• NDVI: 0.72 (Below optimal 0.8)
• Temperature: 28.5°C (High stress range)
• Humidity: 65% (Fungal risk zone)

**Diagnosis:** Yellow leaves + high humidity = **Fungal infection likely**

**Immediate Action:**
1. **Copper-based fungicide** spray करें
2. Field drainage improve करें
3. नीम oil + soap solution use करें

**🛰️ Satellite Monitoring:** Risk level: MODERATE
**Success Rate:** 88% with early treatment ✅""",

    "crop_selection_english": """🌾 Hello Farmer! Best wheat varieties for Punjab:

**🛰️ Satellite Analysis:**
• NDVI Score: 0.72 (Good field conditions)
• Soil Moisture: 45%
• Environmental Score: 78/100

**Recommended Varieties:**
1. **HD-2967**: High yield (45-50 quintals/acre)
2. **PBW-343**: Disease resistant, ideal for irrigated areas
3. **DBW-88**: Perfect for late sowing

**🛰️ Satellite Recommendation:** Based on current soil conditions, HD-2967 is most suitable.
**Confidence:** 95% ✅""",

    "irrigation_english": """💧 Smart Irrigation Recommendation - Satellite Guided:

**🛰️ Current Field Status:**
• Soil Moisture: 45% (CRITICAL - Below 30%)
• Temperature: 28.5°C
• Next Rainfall: 5+ days (satellite weather prediction)
• Crop Growth Stage: Flowering (high water demand)

**⚠️ URGENT IRRIGATION NEEDED:**
• **Apply 75mm water TODAY**
• **Next irrigation:** 4 days (based on satellite forecast)
• **Method:** Drip irrigation preferred (30% water saving)

**🛰️ Satellite Schedule:**
- Day 1: 75mm (immediate)
- Day 5: 50mm
- Day 9: 60mm

**Water Optimization:** Satellite-guided scheduling saves 30% water
**Yield Protection:** 95% ✅""",

    "finance_policy_mixed": """💰 Farming Loan Guidance - Satellite Risk Assessment:

**🛰️ Field Risk Analysis:**
• Environmental Score: 78/100
• Risk Level: MODERATE
• Crop Health: Good (NDVI: 0.72)

**Loan Options Available:**
1. **Kisan Credit Card:** ₹3 लाख तक, 4% interest
2. **PM-KISAN:** Equipment loan, 6% interest
3. **Mudra Scheme:** Small equipment, collateral-free

**🛰️ Satellite Advantage:**
• आपका risk profile: MODERATE (satellite verified)
• Higher loan approval chances: 85%
• Lower interest rate eligible due to good field health

**Application Process:**
1. Bank में जाएं with land documents
2. Satellite report attach करें (we provide)
3. Expected approval: 15-20 days

**Confidence:** 90% approval chance ✅"""
}

def detect_language(query: str) -> str:
    """Simple language detection"""
    hindi_chars = any('\u0900' <= char <= '\u097F' for char in query)
    english_chars = any('a' <= char.lower() <= 'z' for char in query)
    
    if hindi_chars and english_chars:
        return "mixed"
    elif hindi_chars:
        return "hindi"
    else:
        return "english"

def route_query(query: str) -> Dict[str, Any]:
    """Route query to appropriate agent"""
    query_lower = query.lower()
    
    # Agent routing logic
    if any(word in query_lower for word in ["गेहूं", "wheat", "crop", "variety", "किस्म"]):
        agent = "crop_selection"
    elif any(word in query_lower for word in ["पत्ते", "pest", "disease", "yellow", "leaves"]):
        agent = "pest_management"
    elif any(word in query_lower for word in ["irrigation", "water", "पानी", "सिंचाई"]):
        agent = "irrigation"
    elif any(word in query_lower for word in ["loan", "finance", "apply", "कर्ज"]):
        agent = "finance_policy"
    elif any(word in query_lower for word in ["sell", "market", "profit", "बेचना"]):
        agent = "market_timing"
    else:
        agent = "general_agriculture"
    
    # Detect reasoning keyword
    reasoning_word = "general query"
    for word in ["गेहूं", "wheat", "पत्ते", "pest", "irrigation", "water", "loan", "sell"]:
        if word in query_lower:
            reasoning_word = word
            break
    
    return {
        "agent": agent,
        "confidence": 0.92,
        "reasoning": f"Detected '{reasoning_word}' indicating {agent} domain",
        "language_detected": detect_language(query)
    }

def get_response_text(query: str, routing: Dict[str, Any]) -> str:
    """Get appropriate response text"""
    agent = routing["agent"]
    language = routing["language_detected"]
    
    # Match responses to agent and language
    if agent == "crop_selection":
        if language in ["hindi", "mixed"]:
            return DEMO_RESPONSES["crop_selection_hindi"]
        else:
            return DEMO_RESPONSES["crop_selection_english"]
    elif agent == "pest_management":
        return DEMO_RESPONSES["pest_management_mixed"]
    elif agent == "irrigation":
        return DEMO_RESPONSES["irrigation_english"]
    elif agent == "finance_policy":
        return DEMO_RESPONSES["finance_policy_mixed"]
    else:
        return DEMO_RESPONSES["crop_selection_english"]  # Default

@app.get("/")
async def root():
    return {
        "message": "🌾🛰️ Multi-Agent Agriculture Systems Demo API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "query": "/demo/query",
            "capabilities": "/demo/capabilities",
            "health": "/demo/health"
        }
    }

@app.get("/demo/capabilities")
async def get_capabilities():
    return {
        "system_status": "Satellite-Enhanced AI Agricultural Advisory System",
        "completion_percentage": 71,
        "operational_agents": [
            "crop_selection", "pest_management", "irrigation", 
            "finance_policy", "market_timing"
        ],
        "capabilities": [
            "Multilingual Query Processing (Hindi/English/Mixed)",
            "Intelligent Agent Routing",
            "Satellite Data Integration",
            "Real-time Agricultural Advisory", 
            "Confidence-based Recommendations"
        ],
        "satellite_features": [
            "NDVI Analysis", "Soil Moisture Monitoring",
            "Weather Prediction", "Risk Assessment",
            "Environmental Scoring"
        ],
        "supported_languages": ["hindi", "english", "mixed"]
    }

@app.get("/demo/session")
async def get_session():
    return {
        "session_id": f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "start_time": datetime.now().isoformat(),
        "total_queries": 5,
        "sample_queries": [
            {
                "query": "पंजाब में गेहूं की सबसे अच्छी किस्म कौन सी है?",
                "type": "Hindi crop selection",
                "agent": "crop_selection"
            },
            {
                "query": "Meri cotton crop mein पीले पत्ते दिख रहे हैं, क्या करूं?",
                "type": "Code-switched pest management",
                "agent": "pest_management"
            },
            {
                "query": "When should I sell my wheat crop for maximum profit?",
                "type": "English market timing",
                "agent": "market_timing"
            },
            {
                "query": "My field needs irrigation - when and how much water?",
                "type": "Irrigation scheduling",
                "agent": "irrigation"
            },
            {
                "query": "Loan ke liye apply कैसे करूं for farming equipment?",
                "type": "Financial advisory",
                "agent": "finance_policy"
            }
        ]
    }

@app.post("/demo/query")
async def process_query(request: QueryRequest):
    start_time = time.time()
    
    # Route the query
    routing = route_query(request.query_text)
    
    # Get satellite data (hardcoded)
    satellite_data = {
        "ndvi": 0.72,
        "soil_moisture": 0.45,
        "temperature": 28.5,
        "humidity": 65,
        "environmental_score": 78,
        "risk_level": "moderate"
    }
    
    # Get response text
    response_text = get_response_text(request.query_text, routing)
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    return QueryResponse(
        status="success",
        query_id=f"demo_query_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        original_query=request.query_text,
        routing_analysis=routing,
        satellite_data=satellite_data,
        response_text=response_text,
        technical_metrics={
            "processing_time_ms": round(processing_time, 0),
            "confidence_level": routing["confidence"],
            "satellite_data_integrated": True,
            "risk_assessment": satellite_data["risk_level"].upper(),
            "agent": routing["agent"]
        },
        timestamp=datetime.now().isoformat()
    )

@app.get("/demo/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "demo_mode": True,
        "mock_data": True
    }

if __name__ == "__main__":
    print("🎬 Starting Demo API Server...")
    print("🌾🛰️ Multi-Agent Agriculture Systems - Demo API")
    print("📊 Server will run on http://localhost:8001")
    print("📚 API docs available at http://localhost:8001/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
