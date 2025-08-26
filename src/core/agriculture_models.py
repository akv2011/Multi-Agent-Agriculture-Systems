"""
Agricultural data models for the Multi-Agent Agriculture Advisory System.
Extends the existing AgentWeaver core models with agriculture-specific structures.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass

# Handle imports flexibly for different execution contexts
try:
    from ..core.models import AgentCapability, Task, TaskPriority
except ImportError:
    try:
        from src.core.models import AgentCapability, Task, TaskPriority
    except ImportError:
        # For standalone execution, define minimal required classes
        from enum import Enum
        class AgentCapability(str, Enum):
            pass
        class TaskPriority(str, Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
        class Task:
            pass


# Agricultural Domain Enums
class CropType(str, Enum):
    WHEAT = "wheat"
    RICE = "rice"
    MAIZE = "maize"
    COTTON = "cotton"
    SUGARCANE = "sugarcane"
    SOYBEAN = "soybean"
    BARLEY = "barley"
    MILLET = "millet"
    PULSES = "pulses"
    MUSTARD = "mustard"
    FODDER = "fodder"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    SPICES = "spices"
    OTHER = "other"


class SoilType(str, Enum):
    ALLUVIAL = "alluvial"
    BLACK = "black"
    RED = "red"
    LATERITE = "laterite"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    SALINE = "saline"
    CLAY = "clay"
    LOAMY = "loamy"
    SANDY = "sandy"


class SeasonType(str, Enum):
    KHARIF = "kharif"      # Monsoon season crops
    RABI = "rabi"          # Winter season crops
    ZAID = "zaid"          # Summer season crops


class QueryDomain(str, Enum):
    CROP_SELECTION = "crop_selection"
    PEST_MANAGEMENT = "pest_management"
    IRRIGATION = "irrigation"
    FINANCE_POLICY = "finance_policy"
    MARKET_TIMING = "market_timing"
    HARVEST_PLANNING = "harvest_planning"
    INPUT_MATERIALS = "input_materials"
    DISEASE_IDENTIFICATION = "disease_identification"  # AgriMitr disease identification
    FERTILIZER_RECOMMENDATION = "fertilizer_recommendation"  # AgriMitr fertilizer recommendation
    WEATHER_FORECAST = "weather_forecast"  # AgriMitr weather forecast
    SMART_FARMING = "smart_farming"  # AgriMitr smart farming guidance
    GENERAL = "general"


class Language(str, Enum):
    HINDI = "hi"
    ENGLISH = "en"
    MIXED = "mixed"  # Code-switched Hindi-English


# Agricultural Agent Capabilities
class AgricultureCapability(str, Enum):
    # Agriculture-specific capabilities (not extending enum)
    CROP_RECOMMENDATION = "crop_recommendation"
    PEST_IDENTIFICATION = "pest_identification"
    YIELD_PREDICTION = "yield_prediction"
    IRRIGATION_PLANNING = "irrigation_planning"
    FINANCE_ADVISORY = "finance_advisory"
    MARKET_ANALYSIS = "market_analysis"
    HARVEST_OPTIMIZATION = "harvest_optimization"
    INPUT_OPTIMIZATION = "input_optimization"
    WEATHER_ANALYSIS = "weather_analysis"
    SATELLITE_DATA_PROCESSING = "satellite_data_processing"
    MULTILINGUAL_NLP = "multilingual_nlp"
    QUERY_ROUTING = "query_routing"


# Core Data Models
@dataclass
class Location:
    """Geographic location information"""
    state: str
    district: str
    tehsil: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    pincode: Optional[str] = None


@dataclass
class FarmProfile:
    """Farmer's farm information"""
    farm_id: str
    farmer_name: str
    location: Location
    total_area: float  # in acres
    soil_type: SoilType
    current_crops: List[CropType]
    irrigation_type: str = "rainfed"  # rainfed, tube_well, canal, drip, etc.
    farm_type: str = "small"  # small, medium, large
    annual_income: Optional[float] = None
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class WeatherData:
    """Weather information"""
    location: Location
    date: date
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    pressure: Optional[float] = None
    uv_index: Optional[float] = None


@dataclass
class SatelliteData:
    """Satellite imagery derived metrics"""
    location: Location
    date: date
    ndvi: Optional[float] = None  # Normalized Difference Vegetation Index
    evi: Optional[float] = None   # Enhanced Vegetation Index
    soil_moisture: Optional[float] = None
    land_surface_temperature: Optional[float] = None
    chlorophyll_content: Optional[float] = None
    crop_stress_index: Optional[float] = None
    source: str = "unknown"  # sentinel, landsat, modis, etc.
    resolution: Optional[str] = None  # 10m, 30m, 250m, etc.


@dataclass
class CropVariety:
    """Crop variety information"""
    variety_id: str
    crop_type: CropType
    name: str
    duration_days: int
    season: SeasonType
    yield_potential: float  # quintals per hectare
    water_requirement: float  # mm
    suitable_soil_types: List[SoilType]
    local_name: Optional[str] = None
    resistance_traits: List[str] = None  # drought, pest, disease resistance
    seed_rate: Optional[float] = None  # kg per hectare
    spacing: Optional[str] = None
    market_demand: str = "medium"  # high, medium, low


# Query and Response Models
class AgricultureQuery(BaseModel):
    """User query for agricultural advice"""
    query_id: str = Field(default_factory=lambda: f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    user_id: Optional[str] = None
    farm_profile: Optional[FarmProfile] = None
    query_text: str
    query_language: Language = Language.ENGLISH
    query_domains: List[QueryDomain] = Field(default_factory=list)
    location: Optional[Location] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[str] = Field(default_factory=list)  # Image paths, etc.
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: TaskPriority = TaskPriority.MEDIUM


class AgentResponse(BaseModel):
    """Response from an agricultural agent"""
    agent_id: str
    agent_name: str
    query_id: str
    response_text: str
    response_language: Language = Language.ENGLISH
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RoutingDecision(BaseModel):
    """Router's decision on how to handle a query"""
    query_id: str
    detected_domains: List[QueryDomain]
    detected_language: Language
    confidence: float = Field(ge=0.0, le=1.0)
    selected_agents: List[str]  # Agent IDs
    execution_plan: str  # sequential, parallel, hierarchical
    reasoning: str
    fallback_agents: List[str] = Field(default_factory=list)
    estimated_processing_time: Optional[int] = None  # seconds
    requires_clarification: bool = False
    clarification_questions: List[str] = Field(default_factory=list)


class AggregatedResponse(BaseModel):
    """Final aggregated response to user"""
    query_id: str
    original_query: str
    detected_domains: List[QueryDomain]
    agent_responses: List[AgentResponse]
    final_response: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    response_language: Language = Language.ENGLISH
    processing_summary: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    total_processing_time_ms: int = 0


# Agricultural Task Types that extend base Task
class AgricultureTask(Task):
    """Extended task for agricultural operations"""
    farm_profile: Optional[FarmProfile] = None
    location: Optional[Location] = None
    crop_data: Optional[Dict[str, Any]] = None
    weather_data: Optional[List[WeatherData]] = None
    satellite_data: Optional[List[SatelliteData]] = None
    query_data: Optional[AgricultureQuery] = None
    expected_output_format: str = "text"  # text, json, chart, etc.


# Data Source Models
@dataclass
class DataSource:
    """Information about data sources"""
    source_id: str
    name: str
    type: str  # api, database, file, scraping
    url: Optional[str] = None
    api_key_required: bool = False
    rate_limit: Optional[int] = None  # requests per hour
    last_updated: Optional[datetime] = None
    reliability_score: float = 1.0
    data_types: List[str] = None  # weather, market, satellite, etc.
    coverage: str = "india"  # geographical coverage
    update_frequency: str = "daily"


# Common Agricultural Constants
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry"
]

COMMON_CROPS_BY_SEASON = {
    SeasonType.KHARIF: [CropType.RICE, CropType.COTTON, CropType.SUGARCANE, CropType.MAIZE],
    SeasonType.RABI: [CropType.WHEAT, CropType.BARLEY, CropType.MUSTARD],
    SeasonType.ZAID: [CropType.VEGETABLES, CropType.FODDER]
}

# Data validation functions
def validate_location(location: Location) -> bool:
    """Validate location data"""
    if location.state not in INDIAN_STATES:
        return False
    if location.latitude and not (-90 <= location.latitude <= 90):
        return False
    if location.longitude and not (-180 <= location.longitude <= 180):
        return False
    return True


def validate_farm_profile(farm: FarmProfile) -> bool:
    """Validate farm profile data"""
    if not validate_location(farm.location):
        return False
    if farm.total_area <= 0:
        return False
    return True
