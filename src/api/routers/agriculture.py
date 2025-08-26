"""
Agriculture API Router
Provides REST API endpoints for agricultural queries and agent management.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from ...core.agriculture_models import (
    AgricultureQuery, QueryDomain, Language, Location, FarmProfile
)
from ...services.agriculture_integration import get_agriculture_service
from ...config import get_config, ConfigService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agriculture", tags=["Agriculture"])


# Request/Response Models
class AgricultureQueryRequest(BaseModel):
    """Request model for agricultural queries"""
    query_text: str = Field(..., description="The agricultural question or query")
    user_id: Optional[str] = Field(None, description="User identifier")
    language: Language = Field(Language.ENGLISH, description="Query language")
    location: Optional[Dict[str, Any]] = Field(None, description="User location information")
    farm_profile: Optional[Dict[str, Any]] = Field(None, description="Farm profile data")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    priority: str = Field("medium", description="Query priority (low, medium, high)")


class AgricultureQueryResponse(BaseModel):
    """Response model for agricultural queries"""
    status: str
    query_id: str
    message: Optional[str] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    estimated_time: Optional[int] = None  # seconds


class AgricultureStatusResponse(BaseModel):
    """Response model for agriculture system status"""
    status: str
    router_available: bool
    specialist_agents: int
    active_queries: int
    agent_details: Dict[str, Any] = Field(default_factory=dict)


class GroundSearchRequest(BaseModel):
    """Request model for ground search functionality"""
    query: str = Field(..., description="Search query")
    language: str = Field("english", description="Language for search")
    domain: str = Field("general", description="Agricultural domain")
    max_results: int = Field(5, description="Maximum number of results")


class GroundSearchResponse(BaseModel):
    """Response model for ground search results"""
    status: str
    query: str
    language: str
    results: list
    search_time: float
    data_source: str = "web_search"


@router.post("/query", response_model=AgricultureQueryResponse)
async def submit_agriculture_query(
    request: AgricultureQueryRequest,
    background_tasks: BackgroundTasks
) -> AgricultureQueryResponse:
    """
    Submit an agricultural query for processing.
    The query will be analyzed and routed to appropriate specialist agents.
    """
    try:
        # Get agriculture service
        service = get_agriculture_service()
        if not service:
            raise HTTPException(
                status_code=503, 
                detail="Agriculture service not available"
            )
        
        # Convert request to AgricultureQuery
        query_data = {
            "query_text": request.query_text,
            "user_id": request.user_id,
            "query_language": request.language,
            "context": request.context,
            "priority": request.priority
        }
        
        # Add location if provided
        if request.location:
            query_data["location"] = Location(**request.location)
        
        # Add farm profile if provided
        if request.farm_profile:
            query_data["farm_profile"] = FarmProfile(**request.farm_profile)
        
        logger.info(f"Received agriculture query: {request.query_text[:100]}...")
        
        # Process query (this will be async and send updates via WebSocket)
        result = await service.handle_agriculture_query(query_data)
        
        if "error" in result:
            return AgricultureQueryResponse(
                status="error",
                query_id="",
                error=result["error"]
            )
        
        elif result.get("status") == "clarification_needed":
            return AgricultureQueryResponse(
                status="clarification_needed",
                query_id=result["query_id"],
                message="Need more information",
                response={"questions": result["questions"]}
            )
        
        else:
            return AgricultureQueryResponse(
                status="success",
                query_id=result["query_id"],
                message="Query processed successfully",
                response=result["response"]
            )
    
    except Exception as e:
        logger.error(f"Failed to process agriculture query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AgricultureStatusResponse)
async def get_agriculture_status() -> AgricultureStatusResponse:
    """
    Get the current status of the agriculture system.
    Shows availability of router, specialist agents, and active queries.
    """
    try:
        service = get_agriculture_service()
        if not service:
            return AgricultureStatusResponse(
                status="unavailable",
                router_available=False,
                specialist_agents=0,
                active_queries=0
            )
        
        status_data = await service.get_status({})
        
        return AgricultureStatusResponse(
            status=status_data.get("status", "unknown"),
            router_available=status_data.get("router_available", False),
            specialist_agents=status_data.get("specialist_agents", 0),
            active_queries=status_data.get("active_queries", 0),
            agent_details=status_data.get("agent_details", {})
        )
    
    except Exception as e:
        logger.error(f"Failed to get agriculture status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/{query_id}")
async def get_query_status(query_id: str) -> Dict[str, Any]:
    """
    Get the status of a specific query by ID.
    Shows processing status, responses, and completion status.
    """
    try:
        service = get_agriculture_service()
        if not service:
            raise HTTPException(
                status_code=503, 
                detail="Agriculture service not available"
            )
        
        query_status = service.get_query_status(query_id)
        
        if not query_status:
            raise HTTPException(
                status_code=404, 
                detail=f"Query {query_id} not found"
            )
        
        # Convert datetime objects to strings for JSON serialization
        response_data = {
            "query_id": query_id,
            "status": query_status["status"],
            "start_time": query_status["start_time"].isoformat(),
            "responses_count": len(query_status.get("responses", {}))
        }
        
        # Add final response if completed
        if "final_response" in query_status:
            response_data["final_response"] = query_status["final_response"].dict()
        
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get query status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def get_supported_domains(config: ConfigService = Depends(get_config)) -> Dict[str, Any]:
    """
    Get list of supported agricultural domains and their descriptions.
    Uses region-specific configuration for recommendations.
    """
    try:
        # Get region-specific data
        current_region = config.get_region_name()
        region_data = config.region
        
        # Load domains info
        domains_info = {
            QueryDomain.CROP_SELECTION.value: {
                "name": "Crop Selection",
                "description": "Recommendations for optimal crop varieties based on location, soil, and weather conditions",
                "keywords": ["crop", "seed", "variety", "plant", "cultivation", "fasal", "beej"],
                "region_crops": config.get_region_data("agriculture_data.major_crops", [])
            },
            QueryDomain.PEST_MANAGEMENT.value: {
                "name": "Pest Management", 
                "description": "Pest identification, outbreak forecasting, and treatment recommendations",
                "keywords": ["pest", "insect", "disease", "spray", "treatment", "keet", "bimari"]
            },
            QueryDomain.IRRIGATION.value: {
                "name": "Irrigation Scheduling",
                "description": f"Water requirement calculation and optimal irrigation scheduling for {current_region}",
                "keywords": ["water", "irrigation", "watering", "schedule", "pani", "sinchai"],
                "irrigation_systems": config.get_region_data("agriculture_data.irrigation_systems", [])
            },
            QueryDomain.FINANCE_POLICY.value: {
                "name": "Finance & Policy",
                "description": "Agricultural loans, subsidies, insurance, and government schemes",
                "keywords": ["loan", "subsidy", "insurance", "scheme", "bank", "karza", "yojana"],
                "govt_schemes": config.get_region_data("government_schemes", [])
            },
            QueryDomain.MARKET_TIMING.value: {
                "name": "Market Timing",
                "description": "Price forecasting and optimal selling time recommendations",
                "keywords": ["sell", "market", "price", "mandi", "rate", "bhav"],
                "market_centers": config.get_region_data("market_centers", [])
            },
            QueryDomain.HARVEST_PLANNING.value: {
                "name": "Harvest Planning",
                "description": "Optimal harvest timing and post-harvest handling advice",
                "keywords": ["harvest", "cutting", "maturity", "katana", "fasal"],
                "growing_seasons": config.get_region_data("agriculture_data.growing_seasons", {})
            },
            QueryDomain.INPUT_MATERIALS.value: {
                "name": "Input Materials",
                "description": "Fertilizer, seed, and pesticide recommendations with cost optimization",
                "keywords": ["fertilizer", "seed", "pesticide", "khad", "urvarak", "beej"]
            }
        }
        
        return {
            "supported_domains": domains_info,
            "languages": {
                Language.ENGLISH.value: "English",
                Language.HINDI.value: "Hindi (हिंदी)",
                Language.MIXED.value: "Mixed (Hindi-English)"
            },
            "example_queries": [
                {
                    "domain": QueryDomain.CROP_SELECTION.value,
                    "query": "What crop should I grow in Punjab during Rabi season?",
                    "hindi": "रबी के मौसम में पंजाब में कौन सी फसल उगानी चाहिए?"
                },
                {
                    "domain": QueryDomain.PEST_MANAGEMENT.value,
                    "query": "My wheat has yellow spots, what spray should I use?",
                    "hindi": "मेरे गेहूं पर पीले धब्बे हैं, कौन सा स्प्रे करूं?"
                },
                {
                    "domain": QueryDomain.IRRIGATION.value,
                    "query": "When should I water my cotton crop?",
                    "hindi": "कपास की फसल में कब पानी देना चाहिए?"
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to get supported domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit feedback on agricultural advice quality.
    Used to improve agent responses and accuracy.
    """
    try:
        # Log feedback for analysis
        logger.info(f"Received agriculture feedback: {feedback_data}")
        
        # In a production system, this would be stored in a database
        # For now, we'll just acknowledge receipt
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "feedback_id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_agriculture_system(config: ConfigService = Depends(get_config)) -> Dict[str, Any]:
    """
    Test endpoint to verify agriculture system is working.
    Runs basic connectivity and functionality tests.
    """
    try:
        service = get_agriculture_service()
        
        tests = {
            "service_available": service is not None,
            "router_initialized": False,
            "agents_registered": 0,
            "config_service": True,
            "environment": config.settings.APP_ENV.value,
            "region": config.get_region_name(),
            "region_loaded": bool(config.region)
        }
        
        if service:
            status = await service.get_status({})
            tests["router_initialized"] = status.get("router_available", False)
            tests["agents_registered"] = status.get("specialist_agents", 0)
        
        # Check if the region has major crops data
        tests["region_crops_loaded"] = bool(config.get_region_data("agriculture_data.major_crops", []))
        
        overall_status = "healthy" if all([
            tests["service_available"],
            tests["router_initialized"],
            tests["config_service"],
            tests["region_loaded"],
            tests["region_crops_loaded"]
        ]) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "tests": tests,
            "environment": config.settings.APP_ENV.value,
            "region": {
                "name": config.get_region_name(),
                "major_crops": config.get_region_data("agriculture_data.major_crops", []),
                "agricultural_zones": config.get_region_data("agriculture_data.agricultural_zones", [])
            },
            "api_url": config.get_api_url(),
            "ws_url": config.get_ws_url(),
            "message": "Agriculture system test completed"
        }
    
    except Exception as e:
        logger.error(f"Agriculture system test failed: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Agriculture system test failed"
        }


@router.post("/ground-search", response_model=GroundSearchResponse)
async def perform_ground_search(request: GroundSearchRequest):
    """
    Perform ground search when model data is not available
    """
    start_time = datetime.now()
    
    try:
        # Get ground search service
        from ...services.ground_search_service import GroundSearchService
        search_service = GroundSearchService()
        
        # Perform search
        search_results = await search_service.search(
            query=request.query,
            language=request.language,
            domain=request.domain,
            max_results=request.max_results
        )
        
        # Calculate search time
        search_time = (datetime.now() - start_time).total_seconds()
        
        return GroundSearchResponse(
            status="success",
            query=request.query,
            language=request.language,
            results=search_results,
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"Ground search failed: {e}")
        search_time = (datetime.now() - start_time).total_seconds()
        
        # Return mock results for development
        mock_results = get_mock_search_results(request.query, request.language, request.domain)
        
        return GroundSearchResponse(
            status="success_mock",
            query=request.query,
            language=request.language,
            results=mock_results,
            search_time=search_time,
            data_source="mock_search"
        )


def get_mock_search_results(query: str, language: str, domain: str) -> list:
    """Generate mock search results for development"""
    
    if "disease" in query.lower() or "நோய்" in query:
        if language == "tamil":
            return [
                {
                    "title": "தாவர நோய் கண்டறிதல் மற்றும் சிகிச்சை வழிமுறைகள்",
                    "snippet": "தாவர நோய்களை எளிதாக கண்டறிந்து சரியான சிகிச்சை முறைகளை பயன்படுத்துவது எப்படி",
                    "url": "https://example.com/plant-diseases-tamil",
                    "source": "AgriGuide Tamil"
                },
                {
                    "title": "இயற்கை பூஞ்சாணக் கொல்லி தயாரிப்பு",
                    "snippet": "வீட்டிலேயே தயாரிக்கக்கூடிய இயற்கை பூஞ்சாணக் கொல்லி மருந்துகள்",
                    "url": "https://example.com/organic-fungicide-tamil",
                    "source": "Organic Farming Tamil"
                }
            ]
        else:
            return [
                {
                    "title": "Plant Disease Identification and Treatment Guide",
                    "snippet": "Comprehensive guide to identify common plant diseases and their organic treatment methods",
                    "url": "https://example.com/plant-diseases",
                    "source": "Agricultural Extension Service"
                },
                {
                    "title": "Organic Fungicide Preparation Methods",
                    "snippet": "Learn how to prepare effective organic fungicides at home using common ingredients",
                    "url": "https://example.com/organic-fungicides",
                    "source": "Sustainable Agriculture Network"
                }
            ]
    
    elif "crop" in query.lower() or "பயிர்" in query:
        if language == "tamil":
            return [
                {
                    "title": "மண் பரிசோதனை அடிப்படையில் பயிர் தேர்வு",
                    "snippet": "உங்கள் மண்ணின் NPK அளவுகளின் அடிப்படையில் சரியான பயிரை தேர்ந்தெடுக்கும் முறை",
                    "url": "https://example.com/crop-selection-tamil",
                    "source": "வேளாண் அறிவியல் மையம்"
                }
            ]
        else:
            return [
                {
                    "title": "Soil-Based Crop Recommendation System",
                    "snippet": "Choose the right crop based on your soil NPK levels and climatic conditions",
                    "url": "https://example.com/crop-recommendation",
                    "source": "Agricultural Research Institute"
                }
            ]
    
    elif "irrigation" in query.lower() or "நீர்" in query:
        if language == "tamil":
            return [
                {
                    "title": "நீர்ப்பாசன அட்டவணை திட்டமிடல்",
                    "snippet": "பயிர் வகை மற்றும் மண் வகையின் அடிப்படையில் நீர்ப்பாசன அட்டவணை",
                    "url": "https://example.com/irrigation-tamil",
                    "source": "நீர் மேலாண்மை வழிகாட்டி"
                }
            ]
        else:
            return [
                {
                    "title": "Smart Irrigation Scheduling Guide",
                    "snippet": "Create efficient irrigation schedules based on crop type, soil conditions, and weather",
                    "url": "https://example.com/irrigation-scheduling",
                    "source": "Water Management Institute"
                }
            ]
    
    else:
        # General agricultural advice
        if language == "tamil":
            return [
                {
                    "title": "நவீன விவசாய வழிmுறைகள்",
                    "snippet": "சுற்றுச்சூழல் நட்பு விவசாய முறைகள் மற்றும் அதிக விளைச்சல் பெறும் வழிகள்",
                    "url": "https://example.com/modern-farming-tamil",
                    "source": "தமிழ்நாடு வேளாண் பல்கலைக்கழகம்"
                }
            ]
        else:
            return [
                {
                    "title": "Modern Agricultural Practices Guide",
                    "snippet": "Sustainable farming methods and best practices for higher yields",
                    "url": "https://example.com/modern-agriculture",
                    "source": "National Agricultural Institute"
                }
            ]
