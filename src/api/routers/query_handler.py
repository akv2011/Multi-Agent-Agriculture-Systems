"""
Query Handler API Router
Handles intelligent query routing, agent execution, and fallback to ground search
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import time
import asyncio
import json

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from src.services.ground_search_service import create_ground_search_service
from src.services.websocket_integration import integration_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/query", tags=["Query Processing"])

# Request/Response Models
class QueryRequest(BaseModel):
    query_text: str
    image_base64: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    vegetation_analysis: Optional[Dict[str, Any]] = None

class AgentClassification(BaseModel):
    agent_id: str
    confidence: float
    reasons: List[str]
    used_image: bool

class QueryResponse(BaseModel):
    status: str
    query_id: str
    original_query: str
    classification: AgentClassification
    agent_result: Dict[str, Any]
    fallback_used: bool = False
    fallback_source: Optional[str] = None
    processing_time_ms: float
    timestamp: str

class StatsUpdate(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_processing_time: float
    agent_usage: Dict[str, int]
    fallback_usage: Dict[str, int]

# In-memory stats (in production, use Redis/database)
query_stats = {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "processing_times": [],
    "agent_usage": {},
    "fallback_usage": {"ground_search": 0, "none": 0}
}

def classify_query(text: str, has_image: bool = False) -> AgentClassification:
    """
    Intelligent query classification based on keywords and context
    """
    lower_text = text.lower()
    reasons = []
    confidence = 0.3  # base confidence
    agent_id = "general"
    
    # Disease identification patterns
    disease_patterns = [
        'disease', 'blight', 'rust', 'spot', 'infection', 'leaf', 'pest',
        'bug', 'insect', 'fungus', 'virus', 'bacteria', 'pathogen',
        'yellowing', 'browning', 'wilting', 'rotting', 'मरंड', 'कीड़े'
    ]
    
    # Crop recommendation patterns
    crop_patterns = [
        'recommend', 'which crop', 'best crop', 'grow', 'variety', 'fertiliz',
        'soil', 'nutrient', 'plant', 'seed', 'किस्म', 'खाद', 'बीज'
    ]
    
    # Irrigation patterns
    irrigation_patterns = [
        'irrigat', 'water', 'moisture', 'schedule', 'drip', 'spray',
        'pump', 'tube well', 'सिंचाई', 'पानी'
    ]
    
    # Market analysis patterns
    market_patterns = [
        'price', 'market', 'sell', 'demand', 'forecast', 'rate', 'mandi',
        'profit', 'loss', 'revenue', 'कीमत', 'बाजार', 'मंडी'
    ]
    
    # Check patterns and assign agent
    if any(pattern in lower_text for pattern in disease_patterns):
        agent_id = "disease_identification"
        confidence += 0.4
        reasons.append("Disease-related keywords detected")
        
    elif any(pattern in lower_text for pattern in crop_patterns):
        agent_id = "crop_recommendation" 
        confidence += 0.35
        reasons.append("Crop recommendation keywords detected")
        
    elif any(pattern in lower_text for pattern in irrigation_patterns):
        agent_id = "irrigation_scheduling"
        confidence += 0.35
        reasons.append("Irrigation/water management keywords detected")
        
    elif any(pattern in lower_text for pattern in market_patterns):
        agent_id = "market_analysis"
        confidence += 0.4
        reasons.append("Market analysis keywords detected")
    
    # Image bonus for disease detection
    if has_image:
        if agent_id == "general":
            agent_id = "disease_identification"
            confidence += 0.3
            reasons.append("Image provided - defaulting to disease identification")
        elif agent_id == "disease_identification":
            confidence += 0.15
            reasons.append("Image supports disease identification")
    
    # Language bonus
    if any(char in text for char in 'हिंदीपंजाबीग्रामीणकृषि'):
        confidence += 0.1
        reasons.append("Hindi/regional language detected")
    
    return AgentClassification(
        agent_id=agent_id,
        confidence=min(1.0, confidence),
        reasons=reasons,
        used_image=has_image
    )

async def execute_agent(agent_id: str, query: str, image_data: Optional[str] = None, 
                       location: Optional[Dict] = None, 
                       vegetation: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute the appropriate agent based on classification
    """
    try:
        # Notify dashboard of agent execution
        await integration_service.notify_agent_status_change(
            agent_id, "idle", "busy", 
            {"current_task": f"Processing query: {query[:50]}..."}
        )
        
        # Simulate agent processing time
        await asyncio.sleep(1.0 + (len(query) / 100))
        
        # Agent-specific processing logic
        if agent_id == "disease_identification":
            result = await process_disease_query(query, image_data)
        elif agent_id == "crop_recommendation":
            result = await process_crop_query(query, location, vegetation)
        elif agent_id == "irrigation_scheduling":
            result = await process_irrigation_query(query, location, vegetation)
        elif agent_id == "market_analysis":
            result = await process_market_query(query, location)
        else:
            result = await process_general_query(query)
        
        # Update agent status back to idle
        await integration_service.notify_agent_status_change(
            agent_id, "busy", "idle", 
            {"last_task": f"Completed: {query[:30]}..."}
        )
        
        return {
            "success": True,
            "agent_id": agent_id,
            "result": result,
            "source": "agent"
        }
        
    except Exception as e:
        logger.error(f"Agent execution failed for {agent_id}: {e}")
        
        # Update agent status to error
        await integration_service.notify_agent_status_change(
            agent_id, "busy", "error",
            {"error": str(e)}
        )
        
        return {
            "success": False,
            "agent_id": agent_id,
            "error": str(e),
            "source": "agent"
        }

async def process_disease_query(query: str, image_data: Optional[str]) -> Dict[str, Any]:
    """Process disease identification queries"""
    # Simulate disease analysis
    diseases = [
        {"name": "Leaf Blight", "probability": 0.85, "treatment": "Apply copper fungicide"},
        {"name": "Powdery Mildew", "probability": 0.72, "treatment": "Use sulfur-based spray"},
        {"name": "Rust Disease", "probability": 0.68, "treatment": "Apply propiconazole"}
    ]
    
    recommendations = [
        "Remove affected leaves immediately",
        "Improve air circulation around plants", 
        "Apply preventive fungicide spray",
        "Monitor weather conditions for humidity"
    ]
    
    return {
        "type": "disease_identification",
        "detected_diseases": diseases,
        "recommendations": recommendations,
        "confidence": 0.85,
        "image_analyzed": image_data is not None
    }

async def process_crop_query(query: str, location: Optional[Dict], vegetation: Optional[Dict]) -> Dict[str, Any]:
    """Process crop recommendation queries"""
    crops = [
        {"name": "Wheat", "suitability": 0.92, "season": "Rabi", "yield_potential": "High"},
        {"name": "Rice", "suitability": 0.78, "season": "Kharif", "yield_potential": "Medium"}, 
        {"name": "Maize", "suitability": 0.85, "season": "Both", "yield_potential": "High"}
    ]
    
    factors = {
        "soil_type": "Loamy",
        "ph_level": 7.2,
        "rainfall": "Adequate",
        "temperature": "Optimal"
    }
    
    return {
        "type": "crop_recommendation",
        "recommended_crops": crops,
        "soil_factors": factors,
        "location_considered": location is not None,
        "satellite_data_used": vegetation is not None
    }

async def process_irrigation_query(query: str, location: Optional[Dict], vegetation: Optional[Dict]) -> Dict[str, Any]:
    """Process irrigation scheduling queries"""
    schedule = [
        {"day": "Monday", "time": "06:00", "duration": "2 hours", "amount": "25mm"},
        {"day": "Thursday", "time": "06:00", "duration": "2 hours", "amount": "25mm"},
        {"day": "Sunday", "time": "06:00", "duration": "1.5 hours", "amount": "20mm"}
    ]
    
    return {
        "type": "irrigation_scheduling", 
        "schedule": schedule,
        "water_requirement": "50-60mm per week",
        "efficiency_tips": [
            "Irrigate early morning to reduce evaporation",
            "Use drip irrigation for water conservation",
            "Monitor soil moisture levels"
        ],
        "location_considered": location is not None
    }

async def process_market_query(query: str, location: Optional[Dict]) -> Dict[str, Any]:
    """Process market analysis queries"""
    prices = [
        {"crop": "Wheat", "current_price": "₹2,150/quintal", "trend": "increasing", "change": "+5.2%"},
        {"crop": "Rice", "current_price": "₹3,800/quintal", "trend": "stable", "change": "+0.8%"},
        {"crop": "Maize", "current_price": "₹1,950/quintal", "trend": "decreasing", "change": "-2.1%"}
    ]
    
    return {
        "type": "market_analysis",
        "current_prices": prices,
        "market_outlook": "Wheat prices expected to rise due to increased demand",
        "selling_recommendations": [
            "Hold wheat for 2-3 weeks for better prices",
            "Sell rice immediately - prices stable",
            "Wait for maize prices to stabilize"
        ]
    }

async def process_general_query(query: str) -> Dict[str, Any]:
    """Process general agricultural queries"""
    return {
        "type": "general_advisory",
        "response": "General agricultural guidance provided based on best practices",
        "tips": [
            "Regular soil testing is recommended",
            "Follow integrated pest management",
            "Maintain proper crop rotation",
            "Monitor weather forecasts regularly"
        ]
    }

async def fallback_to_ground_search(query: str) -> Dict[str, Any]:
    """
    Fallback to Google Ground Search when agents fail
    """
    try:
        ground_service = create_ground_search_service()
        
        # Perform ground search
        search_results = await ground_service.search_with_grounding(query)
        
        return {
            "success": True,
            "source": "ground_search",
            "results": search_results,
            "search_query": query
        }
        
    except Exception as e:
        logger.error(f"Ground search failed: {e}")
        return {
            "success": False,
            "source": "ground_search", 
            "error": str(e),
            "fallback_response": {
                "message": "Unable to process query. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try rephrasing your question",
                    "Contact support if the issue persists"
                ]
            }
        }

def update_statistics(processing_time: float, agent_id: str, success: bool, fallback_used: str = "none"):
    """Update query statistics"""
    query_stats["total_queries"] += 1
    
    if success:
        query_stats["successful_queries"] += 1
    else:
        query_stats["failed_queries"] += 1
    
    query_stats["processing_times"].append(processing_time)
    
    # Keep only last 100 processing times for average calculation
    if len(query_stats["processing_times"]) > 100:
        query_stats["processing_times"] = query_stats["processing_times"][-100:]
    
    # Update agent usage
    if agent_id not in query_stats["agent_usage"]:
        query_stats["agent_usage"][agent_id] = 0
    query_stats["agent_usage"][agent_id] += 1
    
    # Update fallback usage
    query_stats["fallback_usage"][fallback_used] += 1

async def notify_dashboard_update():
    """Notify dashboard of updated statistics"""
    try:
        avg_time = sum(query_stats["processing_times"]) / len(query_stats["processing_times"]) if query_stats["processing_times"] else 0
        
        stats_update = StatsUpdate(
            total_queries=query_stats["total_queries"],
            successful_queries=query_stats["successful_queries"], 
            failed_queries=query_stats["failed_queries"],
            avg_processing_time=avg_time,
            agent_usage=query_stats["agent_usage"],
            fallback_usage=query_stats["fallback_usage"]
        )
        
        await integration_service.notify_statistics_update(stats_update.dict())
        
    except Exception as e:
        logger.error(f"Failed to notify dashboard update: {e}")

@router.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Main query processing endpoint
    Classifies query, routes to appropriate agent, handles fallbacks
    """
    start_time = time.time()
    query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    try:
        # Step 1: Classify the query
        classification = classify_query(request.query_text, bool(request.image_base64))
        
        # Step 2: Try to execute with appropriate agent
        agent_result = await execute_agent(
            classification.agent_id,
            request.query_text,
            request.image_base64,
            request.location,
            request.vegetation_analysis
        )
        
        fallback_used = False
        fallback_source = None
        
        # Step 3: If agent fails, try ground search
        if not agent_result.get("success", False):
            logger.warning(f"Agent {classification.agent_id} failed, trying ground search")
            ground_result = await fallback_to_ground_search(request.query_text)
            
            if ground_result.get("success", False):
                agent_result = ground_result
                fallback_used = True
                fallback_source = "ground_search"
            else:
                # If both fail, return error result
                agent_result = ground_result
                fallback_used = True
                fallback_source = "ground_search"
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update statistics
        success = agent_result.get("success", False)
        update_statistics(
            processing_time, 
            classification.agent_id, 
            success, 
            fallback_source or "none"
        )
        
        # Notify dashboard in background
        background_tasks.add_task(notify_dashboard_update)
        
        return QueryResponse(
            status="success" if success else "partial_success",
            query_id=query_id,
            original_query=request.query_text,
            classification=classification,
            agent_result=agent_result,
            fallback_used=fallback_used,
            fallback_source=fallback_source,
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Query processing failed: {e}")
        
        # Update failure statistics
        update_statistics(processing_time, "unknown", False, "none")
        background_tasks.add_task(notify_dashboard_update)
        
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@router.get("/stats")
async def get_query_statistics():
    """Get current query processing statistics"""
    avg_time = sum(query_stats["processing_times"]) / len(query_stats["processing_times"]) if query_stats["processing_times"] else 0
    
    return {
        "total_queries": query_stats["total_queries"],
        "successful_queries": query_stats["successful_queries"],
        "failed_queries": query_stats["failed_queries"],
        "success_rate": query_stats["successful_queries"] / max(1, query_stats["total_queries"]),
        "avg_processing_time_ms": avg_time,
        "agent_usage": query_stats["agent_usage"],
        "fallback_usage": query_stats["fallback_usage"]
    }

@router.get("/health")
async def query_health_check():
    """Health check for query processing service"""
    try:
        # Test ground search service availability
        ground_service = create_ground_search_service()
        ground_available = True
    except:
        ground_available = False
    
    return {
        "status": "healthy",
        "ground_search_available": ground_available,
        "total_queries_processed": query_stats["total_queries"],
        "timestamp": datetime.now().isoformat()
    }
