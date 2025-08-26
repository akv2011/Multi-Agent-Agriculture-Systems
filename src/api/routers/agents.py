from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import base64
import asyncio

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.api.models import (
    AgentResponse, 
    AgentListResponse, 
    AgentRegistrationRequest,
    AgentUpdateRequest,
    AgentStatus,
    ErrorResponse
)
from src.orchestration.supervisor import SupervisorNode

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])

# New models for enhanced agent functionality
class AgentPredictionRequest(BaseModel):
    agent_type: str
    language: str = "english"
    parameters: Dict[str, Any]
    image_base64: Optional[str] = None

class AgentPredictionResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    agent_type: str
    language: str
    processing_time: float
    data_source: str = "model"
    fallback_to_search: bool = False


def get_supervisor() -> SupervisorNode:
    # This will be injected from the main app state
    from main import app
    return app.state.supervisor


def convert_agent_to_response(agent_data: Dict[str, Any]) -> AgentResponse:
    try:
        # Extract agent information from the supervisor data structure
        agent_id = agent_data.get("id", "unknown")
        agent_name = agent_data.get("name", f"Agent {agent_id}")
        agent_type = agent_data.get("type", "unknown")
        
        # Map internal status to API status enum
        internal_status = agent_data.get("status", "unknown")
        status_mapping = {
            "available": AgentStatus.IDLE,
            "busy": AgentStatus.BUSY,
            "error": AgentStatus.ERROR,
            "active": AgentStatus.ACTIVE,
            "offline": AgentStatus.OFFLINE
        }
        status = status_mapping.get(internal_status, AgentStatus.IDLE)
        
        # Extract capabilities
        capabilities = agent_data.get("capabilities", [])
        if isinstance(capabilities, str):
            capabilities = [capabilities]
        
        # Extract performance metrics
        performance_metrics = agent_data.get("performance_metrics", {})
        if not isinstance(performance_metrics, dict):
            performance_metrics = {}
        
        # Extract metadata
        metadata = agent_data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        return AgentResponse(
            id=agent_id,
            name=agent_name,
            type=agent_type,
            status=status,
            capabilities=capabilities,
            current_task=agent_data.get("current_task"),
            last_activity=metadata.get("last_activity"),
            performance_metrics=performance_metrics,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error converting agent data to response: {e}")
        # Return a basic response with minimal data
        return AgentResponse(
            id=agent_data.get("id", "unknown"),
            name=agent_data.get("name", "Unknown Agent"),
            type=agent_data.get("type", "unknown"),
            status=AgentStatus.ERROR,
            capabilities=[],
            performance_metrics={},
            metadata={"conversion_error": str(e)}
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    status: Optional[str] = Query(None, description="Filter agents by status"),
    agent_type: Optional[str] = Query(None, description="Filter agents by type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip"),
    supervisor: SupervisorNode = Depends(get_supervisor)
):
    try:
        logger.info(f"Listing agents with filters - status: {status}, type: {agent_type}")
        
        # Get agent registry from supervisor
        # For now, we'll create mock data since the supervisor integration is not complete
        mock_agents = [
            {
                "id": "text_analyst_001",
                "name": "Senior Text Analyst",
                "type": "text_analysis",
                "status": "active",
                "capabilities": ["sentiment_analysis", "entity_extraction", "topic_classification"],
                "current_task": None,
                "performance_metrics": {
                    "tasks_completed": 45,
                    "avg_processing_time": 2.3,
                    "success_rate": 0.96
                },
                "metadata": {
                    "version": "1.0",
                    "last_activity": "2025-08-02T14:20:00Z"
                }
            },
            {
                "id": "data_processor_001", 
                "name": "Data Processing Specialist",
                "type": "data_processing",
                "status": "busy",
                "capabilities": ["data_cleaning", "aggregation", "transformation"],
                "current_task": "workflow_001",
                "performance_metrics": {
                    "tasks_completed": 32,
                    "avg_processing_time": 4.1,
                    "success_rate": 0.91
                },
                "metadata": {
                    "version": "1.2",
                    "last_activity": "2025-08-02T14:22:00Z"
                }
            },
            {
                "id": "api_specialist_001",
                "name": "API Integration Agent",
                "type": "api_interaction", 
                "status": "idle",
                "capabilities": ["rest_api", "graphql", "webhook_handling"],
                "current_task": None,
                "performance_metrics": {
                    "tasks_completed": 28,
                    "avg_processing_time": 1.8,
                    "success_rate": 0.94
                },
                "metadata": {
                    "version": "1.1",
                    "last_activity": "2025-08-02T14:15:00Z"
                }
            }
        ]
        
        # Apply filters
        filtered_agents = mock_agents
        
        if status:
            filtered_agents = [a for a in filtered_agents if a.get("status") == status]
        
        if agent_type:
            filtered_agents = [a for a in filtered_agents if a.get("type") == agent_type]
        
        # Apply pagination
        total_count = len(filtered_agents)
        paginated_agents = filtered_agents[offset:offset + limit]
        
        # Convert to response format
        agent_responses = [convert_agent_to_response(agent) for agent in paginated_agents]
        
        # Calculate counts
        active_count = sum(1 for a in filtered_agents if a.get("status") == "active")
        busy_count = sum(1 for a in filtered_agents if a.get("status") == "busy")
        
        response = AgentListResponse(
            agents=agent_responses,
            total_count=total_count,
            active_count=active_count,
            busy_count=busy_count,
            metadata={
                "last_updated": datetime.now().isoformat(),
                "filters_applied": {
                    "status": status,
                    "type": agent_type
                },
                "pagination": {
                    "limit": limit,
                    "offset": offset
                }
            }
        )
        
        logger.info(f"Successfully listed {len(agent_responses)} agents")
        return response
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_details(
    agent_id: str,
    supervisor: SupervisorNode = Depends(get_supervisor)
):
    try:
        logger.info(f"Getting details for agent: {agent_id}")
        
        # Mock agent data for demonstration
        # In a real implementation, this would query the supervisor's agent registry
        mock_agents = {
            "text_analyst_001": {
                "id": "text_analyst_001",
                "name": "Senior Text Analyst",
                "type": "text_analysis",
                "status": "active",
                "capabilities": ["sentiment_analysis", "entity_extraction", "topic_classification", "language_detection"],
                "current_task": None,
                "performance_metrics": {
                    "tasks_completed": 45,
                    "avg_processing_time": 2.3,
                    "success_rate": 0.96,
                    "total_runtime": 1847.5,
                    "peak_memory_usage": 256.7
                },
                "metadata": {
                    "version": "1.0",
                    "created_at": "2025-08-01T10:00:00Z",
                    "last_activity": "2025-08-02T14:20:00Z",
                    "configuration": {
                        "max_text_length": 10000,
                        "confidence_threshold": 0.85,
                        "model_version": "v2.1"
                    },
                    "tags": ["nlp", "production", "high-accuracy"]
                }
            },
            "data_processor_001": {
                "id": "data_processor_001",
                "name": "Data Processing Specialist", 
                "type": "data_processing",
                "status": "busy",
                "capabilities": ["data_cleaning", "aggregation", "transformation", "validation"],
                "current_task": "workflow_001",
                "performance_metrics": {
                    "tasks_completed": 32,
                    "avg_processing_time": 4.1,
                    "success_rate": 0.91,
                    "total_runtime": 2156.3,
                    "peak_memory_usage": 512.1
                },
                "metadata": {
                    "version": "1.2",
                    "created_at": "2025-08-01T10:05:00Z",
                    "last_activity": "2025-08-02T14:22:00Z",
                    "configuration": {
                        "batch_size": 1000,
                        "timeout": 300,
                        "retry_attempts": 3
                    },
                    "tags": ["data", "production", "batch-processing"]
                }
            },
            "api_specialist_001": {
                "id": "api_specialist_001",
                "name": "API Integration Agent",
                "type": "api_interaction",
                "status": "idle", 
                "capabilities": ["rest_api", "graphql", "webhook_handling", "authentication"],
                "current_task": None,
                "performance_metrics": {
                    "tasks_completed": 28,
                    "avg_processing_time": 1.8,
                    "success_rate": 0.94,
                    "total_runtime": 892.4,
                    "peak_memory_usage": 128.3
                },
                "metadata": {
                    "version": "1.1",
                    "created_at": "2025-08-01T10:10:00Z", 
                    "last_activity": "2025-08-02T14:15:00Z",
                    "configuration": {
                        "timeout": 30,
                        "max_retries": 5,
                        "rate_limit": 100
                    },
                    "tags": ["api", "production", "integration"]
                }
            }
        }
        
        # Check if agent exists
        if agent_id not in mock_agents:
            logger.warning(f"Agent not found: {agent_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found"
            )
        
        agent_data = mock_agents[agent_id]
        response = convert_agent_to_response(agent_data)
        
        logger.info(f"Successfully retrieved details for agent: {agent_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting agent details for {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agent details: {str(e)}"
        )


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    try:
        # Mock status data
        status_data = {
            "agent_id": agent_id,
            "status": "active",
            "current_task": None,
            "last_heartbeat": datetime.now().isoformat(),
            "uptime": 3600.5,
            "resource_usage": {
                "cpu_percent": 15.2,
                "memory_percent": 23.8
            }
        }
        
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting agent status for {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agent status: {str(e)}"
        )


@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    try:
        # Mock metrics data
        metrics_data = {
            "agent_id": agent_id,
            "performance_metrics": {
                "tasks_completed_today": 15,
                "tasks_completed_total": 45,
                "avg_processing_time": 2.3,
                "success_rate": 0.96,
                "error_rate": 0.04,
                "throughput_per_hour": 12.5
            },
            "resource_metrics": {
                "current_cpu_usage": 15.2,
                "peak_cpu_usage": 78.9,
                "current_memory_usage": 256.7,
                "peak_memory_usage": 412.3
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error getting agent metrics for {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agent metrics: {str(e)}"
        )


@router.post("/predict", response_model=AgentPredictionResponse)
async def predict_with_agent(request: AgentPredictionRequest):
    """
    Enhanced agent prediction endpoint with multi-language support and fallback to ground search
    """
    start_time = datetime.now()
    
    try:
        # Get the appropriate agent based on type
        agent = await get_specialized_agent(request.agent_type)
        
        if not agent:
            raise HTTPException(
                status_code=404, 
                detail=f"Agent type '{request.agent_type}' not found"
            )
        
        # Prepare the input data for the agent
        agent_input = {
            "parameters": request.parameters,
            "language": request.language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add image data if provided
        if request.image_base64:
            try:
                # Validate base64 image data
                image_data = base64.b64decode(request.image_base64)
                agent_input["image_data"] = image_data
                agent_input["has_image"] = True
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image data: {str(e)}"
                )
        else:
            agent_input["has_image"] = False
        
        # Try to get prediction from the agent
        try:
            result = await agent.predict(agent_input)
            data_source = "model"
            fallback_to_search = False
            
        except Exception as model_error:
            logger.warning(f"Model prediction failed for {request.agent_type}: {model_error}")
            
            # If model fails, use stub model for development
            result = await get_stub_prediction(request.agent_type, request.parameters, request.language)
            data_source = "stub_model"
            fallback_to_search = True
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentPredictionResponse(
            status="success",
            result=result,
            agent_type=request.agent_type,
            language=request.language,
            processing_time=processing_time,
            data_source=data_source,
            fallback_to_search=fallback_to_search
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent prediction: {e}")
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Return error response with fallback suggestion
        return AgentPredictionResponse(
            status="error",
            result={
                "error": str(e),
                "message": "Agent prediction failed, consider using ground search",
                "messageML": "முகவர் கணிப்பு தோல்வியுற்றது, தேடல் பயன்படுத்த பரிந்துரைக்கிறோம்"
            },
            agent_type=request.agent_type,
            language=request.language,
            processing_time=processing_time,
            data_source="error",
            fallback_to_search=True
        )


async def get_specialized_agent(agent_type: str):
    """Get the specialized agent based on type"""
    try:
        from src.agents.disease_identification_agent import DiseaseIdentificationAgent
        from src.agents.crop_selection_agent import CropRecommendationAgent
        from src.agents.irrigation_agent import IrrigationAgent
        from src.agents.fertilizer_recommendation_agent import FertilizerRecommendationAgent
        from src.agents.market_timing_agent import MarketTimingAgent
        from src.agents.harvest_planning_agent import HarvestPlanningAgent
        from src.agents.weather_forecast_agent import WeatherForecastAgent
        
        agent_map = {
            "disease_identification": DiseaseIdentificationAgent,
            "crop_recommendation": CropRecommendationAgent,
            "irrigation_scheduling": IrrigationAgent,
            "fertilizer_recommendation": FertilizerRecommendationAgent,
            "market_timing": MarketTimingAgent,
            "harvest_planning": HarvestPlanningAgent,
            "weather_forecast": WeatherForecastAgent
        }
        
        agent_class = agent_map.get(agent_type)
        if agent_class:
            return agent_class()
        
        return None
        
    except Exception as e:
        logger.error(f"Error creating agent {agent_type}: {e}")
        return None


async def get_stub_prediction(agent_type: str, parameters: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Fallback stub predictions for development"""
    
    # Add some delay to simulate processing
    await asyncio.sleep(1.5)
    
    if agent_type == "disease_identification":
        return {
            "disease": "Leaf Spot" if language == "english" else "இலை புள்ளி",
            "confidence": 0.89,
            "severity": "Moderate" if language == "english" else "மிதமான",
            "treatment": "Apply organic fungicide and improve air circulation" if language == "english" 
                        else "கரிம பூஞ்சாணக் கொல்லியை பயன்படுத்தி காற்று சுழற்சியை மேம்படுத்தவும்",
            "prevention": "Regular inspection and proper spacing" if language == "english"
                         else "வழக்கமான ஆய்வு மற்றும் சரியான இடைவெளி"
        }
    
    elif agent_type == "crop_recommendation":
        crops = [
            {"name": "Rice", "nameML": "அரிசி", "suitability": 0.92, "expectedYield": "4.2 tonnes/ha"},
            {"name": "Wheat", "nameML": "கோதுமை", "suitability": 0.85, "expectedYield": "3.1 tonnes/ha"},
            {"name": "Cotton", "nameML": "பருத்தி", "suitability": 0.78, "expectedYield": "1.6 tonnes/ha"}
        ]
        return {
            "recommendedCrops": crops,
            "reason": "Based on soil analysis and climatic conditions" if language == "english"
                     else "மண் பகுப்பாய்வு மற்றும் காலநிலை நிலைமைகளின் அடிப்படையில்",
            "soilHealth": "Good" if language == "english" else "நல்லது"
        }
    
    elif agent_type == "irrigation_scheduling":
        schedule = [
            {"day": "Monday", "amount": "22mm", "time": "6:00 AM", "duration": "1.8 hours"},
            {"day": "Thursday", "amount": "28mm", "time": "6:00 AM", "duration": "2.2 hours"},
            {"day": "Sunday", "amount": "18mm", "time": "6:00 AM", "duration": "1.4 hours"}
        ]
        return {
            "schedule": schedule,
            "weeklyTotal": "68mm",
            "efficiency": "88%",
            "notes": "Monitor soil moisture and adjust for weather conditions" if language == "english"
                    else "மண் ஈரப்பதத்தை கண்காணித்து வானிலை நிலைமைகளுக்கு ஏற்ப சரிசெய்யவும்"
        }
    
    elif agent_type == "fertilizer_recommendation":
        return {
            "npkRecommendation": {
                "nitrogen": "45 kg/ha",
                "phosphorus": "30 kg/ha", 
                "potassium": "25 kg/ha"
            },
            "organicOptions": ["Compost", "Bio-fertilizer", "Green manure"] if language == "english"
                            else ["இயற்கை உரம்", "உயிர் உரம்", "பசுந்தாள் உரம்"],
            "applicationTiming": "Split application: 50% at planting, 30% at vegetative stage, 20% at flowering" 
                               if language == "english"
                               else "பிரித்து பயன்படுத்தல்: 50% நடவில், 30% வளர்ச்சி நிலையில், 20% பூக்கும் காலத்தில்"
        }
    
    elif agent_type == "market_timing":
        return {
            "optimalSellTime": "Next 2-3 weeks" if language == "english" else "அடுத்த 2-3 வாரங்கள்",
            "currentPrice": "₹2,450/quintal",
            "predictedPrice": "₹2,680/quintal",
            "marketTrend": "Upward" if language == "english" else "மேல்நோக்கி",
            "recommendation": "Hold for better prices" if language == "english" else "சிறந்த விலைக்காக காத்திருக்கவும்"
        }
    
    elif agent_type == "harvest_planning":
        return {
            "optimalHarvestDate": "2024-03-15",
            "maturityIndicators": ["80% grain filling", "Golden color", "Moisture content 22%"] 
                                 if language == "english"
                                 else ["80% தானிய நிரப்புதல்", "தங்க நிறம்", "ஈரப்பத அளவு 22%"],
            "qualityMetrics": {
                "expectedGrade": "A Grade" if language == "english" else "A தரம்",
                "moistureContent": "22%",
                "projectedYield": "4.1 tonnes/ha"
            },
            "postHarvestAdvice": "Immediate drying and proper storage" if language == "english"
                               else "உடனடி உலர்த்தல் மற்றும் சரியான சேமிப்பு"
        }
    
    elif agent_type == "weather_forecast":
        return {
            "forecast": [
                {"date": "2024-02-26", "weather": "Sunny", "temp": "28°C", "rainfall": "0mm"},
                {"date": "2024-02-27", "weather": "Partly cloudy", "temp": "26°C", "rainfall": "2mm"},
                {"date": "2024-02-28", "weather": "Light rain", "temp": "24°C", "rainfall": "15mm"}
            ],
            "advisory": "Good conditions for field operations" if language == "english"
                       else "வயல் பணிகளுக்கு நல்ல நிலைமைகள்",
            "alerts": [] if language == "english" else []
        }
    
    else:
        return {
            "status": "success",
            "message": "Processing completed" if language == "english" else "செயலாக்கம் நிறைவேற்றப்பட்டது",
            "data": parameters
        }
