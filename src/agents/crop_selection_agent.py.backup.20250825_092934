"""
Crop Selection Agent
Specialized agent for recommending optimal crop varieties based on location, soil, and weather conditions.
Provides yield predictions and cultivation advice with satellite data integration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType, 
    WeatherData, Location, FarmProfile, QueryDomain
)

logger = logging.getLogger(__name__)


@dataclass
class CropRecommendation:
    """Individual crop recommendation with details"""
    crop_type: CropType
    variety: str
    suitability_score: float  # 0.0 to 1.0
    expected_yield: float  # kg/hectare
    cultivation_period: int  # days
    water_requirement: float  # mm/season
    investment_cost: float  # rupees/hectare
    market_demand: str  # high, medium, low
    risk_factors: List[str]
    cultivation_tips: List[str]
    reason: str  # Why this crop is recommended


@dataclass
class SeasonalCropData:
    """Seasonal crop cultivation data"""
    season: SeasonType
    suitable_crops: List[CropType]
    planting_window: Tuple[int, int]  # month numbers (1-12)
    harvest_window: Tuple[int, int]  # month numbers (1-12)
    weather_requirements: Dict[str, Any]


class CropSelectionAgent(BaseWorkerAgent):
    """
    Agent specialized in crop selection and yield prediction.
    
    Capabilities:
    - Crop variety recommendations based on soil, weather, location
    - Seasonal crop planning
    - Yield estimation
    - Risk assessment
    - Cultivation guidance
    """
    
    def __init__(self):
        from ..core.agriculture_models import AgricultureCapability
        from ..core.models import AgentCapability
        
        # Use generic capabilities for BaseWorkerAgent compatibility
        capabilities = [
            AgentCapability.ANALYSIS,
            AgentCapability.RESEARCH
        ]
        
        super().__init__(
            name="CropSelectionAgent",
            capabilities=capabilities,
            agent_type="agriculture_specialist"
        )
        
        # Load crop knowledge base
        self._load_crop_database()
        self._load_regional_data()
        logger.info(f"Initialized {self.name} with {len(self.crop_database)} crop varieties")
    
    def execute(self, task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task - required by BaseWorkerAgent"""
        try:
            # For agriculture tasks, convert to AgricultureQuery and process
            if hasattr(task, 'query') and task.query:
                query = task.query
                if isinstance(query, AgricultureQuery):
                    result = asyncio.run(self.process_query(query))
                    return {"status": "success", "result": result}
            
            return {"status": "error", "message": "Invalid task format"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _load_crop_database(self):
        """Load comprehensive crop database with varieties and requirements"""
        self.crop_database = {
            CropType.WHEAT: {
                "varieties": {
                    "HD-2967": {
                        "yield_potential": 4500,  # kg/hectare
                        "duration": 145,  # days
                        "soil_preference": [SoilType.LOAMY, SoilType.LOAMY],
                        "water_requirement": 450,  # mm
                        "temperature_range": (15, 25),  # celsius
                        "rainfall_range": (300, 600),  # mm
                        "resistance": ["rust", "drought_tolerant"],
                        "market_demand": "high",
                        "investment_cost": 25000
                    },
                    "PBW-343": {
                        "yield_potential": 4200,
                        "duration": 140,
                        "soil_preference": [SoilType.LOAMY, SoilType.SANDY],
                        "water_requirement": 420,
                        "temperature_range": (12, 22),
                        "rainfall_range": (250, 500),
                        "resistance": ["yellow_rust"],
                        "market_demand": "high",
                        "investment_cost": 23000
                    },
                    "DBW-88": {
                        "yield_potential": 4800,
                        "duration": 150,
                        "soil_preference": [SoilType.LOAMY, SoilType.CLAY],
                        "water_requirement": 480,
                        "temperature_range": (14, 24),
                        "rainfall_range": (350, 650),
                        "resistance": ["brown_rust", "high_fertility_responsive"],
                        "market_demand": "high",
                        "investment_cost": 27000
                    }
                },
                "seasons": [SeasonType.RABI],
                "planting_months": [10, 11, 12],
                "harvest_months": [3, 4, 5]
            },
            
            CropType.RICE: {
                "varieties": {
                    "Basmati-370": {
                        "yield_potential": 3500,
                        "duration": 140,
                        "soil_preference": [SoilType.LOAMY, SoilType.CLAY],
                        "water_requirement": 1200,
                        "temperature_range": (20, 30),
                        "rainfall_range": (800, 1500),
                        "resistance": ["blast_resistant"],
                        "market_demand": "very_high",
                        "investment_cost": 35000
                    },
                    "PR-126": {
                        "yield_potential": 6000,
                        "duration": 145,
                        "soil_preference": [SoilType.LOAMY, SoilType.LOAMY],
                        "water_requirement": 1350,
                        "temperature_range": (22, 32),
                        "rainfall_range": (900, 1600),
                        "resistance": ["bacterial_blight", "high_yielding"],
                        "market_demand": "high",
                        "investment_cost": 40000
                    },
                    "Pusa-44": {
                        "yield_potential": 5500,
                        "duration": 160,
                        "soil_preference": [SoilType.CLAY, SoilType.LOAMY],
                        "water_requirement": 1400,
                        "temperature_range": (25, 35),
                        "rainfall_range": (1000, 1800),
                        "resistance": ["stem_borer", "leaf_folder"],
                        "market_demand": "medium",
                        "investment_cost": 38000
                    }
                },
                "seasons": [SeasonType.KHARIF, SeasonType.RABI],
                "planting_months": [5, 6, 7, 11, 12],
                "harvest_months": [9, 10, 11, 3, 4]
            },
            
            CropType.COTTON: {
                "varieties": {
                    "Bt-Cotton-RCH-659": {
                        "yield_potential": 2800,
                        "duration": 180,
                        "soil_preference": [SoilType.SANDY, SoilType.LOAMY],
                        "water_requirement": 700,
                        "temperature_range": (25, 35),
                        "rainfall_range": (500, 1000),
                        "resistance": ["bollworm_resistant", "drought_tolerant"],
                        "market_demand": "high",
                        "investment_cost": 45000
                    },
                    "Hybrid-6": {
                        "yield_potential": 3200,
                        "duration": 190,
                        "soil_preference": [SoilType.LOAMY, SoilType.LOAMY],
                        "water_requirement": 750,
                        "temperature_range": (22, 32),
                        "rainfall_range": (600, 1200),
                        "resistance": ["pink_bollworm", "high_fiber_quality"],
                        "market_demand": "very_high",
                        "investment_cost": 50000
                    }
                },
                "seasons": [SeasonType.KHARIF],
                "planting_months": [4, 5, 6],
                "harvest_months": [10, 11, 12]
            },
            
            CropType.SUGARCANE: {
                "varieties": {
                    "Co-86032": {
                        "yield_potential": 85000,  # kg/hectare
                        "duration": 365,  # days
                        "soil_preference": [SoilType.LOAMY, SoilType.LOAMY],
                        "water_requirement": 1500,
                        "temperature_range": (20, 30),
                        "rainfall_range": (1000, 1500),
                        "resistance": ["red_rot", "smut"],
                        "market_demand": "medium",
                        "investment_cost": 60000
                    },
                    "CoS-767": {
                        "yield_potential": 90000,
                        "duration": 360,
                        "soil_preference": [SoilType.LOAMY, SoilType.CLAY],
                        "water_requirement": 1600,
                        "temperature_range": (22, 32),
                        "rainfall_range": (1200, 1800),
                        "resistance": ["early_maturity", "high_sugar_content"],
                        "market_demand": "high",
                        "investment_cost": 65000
                    }
                },
                "seasons": [SeasonType.KHARIF, SeasonType.RABI, SeasonType.ZAID],  # Year-round
                "planting_months": [2, 3, 9, 10],
                "harvest_months": [12, 1, 2, 3]
            },
            
            CropType.MAIZE: {
                "varieties": {
                    "PMH-1": {
                        "yield_potential": 8000,
                        "duration": 90,
                        "soil_preference": [SoilType.LOAMY, SoilType.SANDY],
                        "water_requirement": 400,
                        "temperature_range": (18, 28),
                        "rainfall_range": (300, 700),
                        "resistance": ["early_maturity", "drought_tolerant"],
                        "market_demand": "high",
                        "investment_cost": 20000
                    },
                    "HQPM-1": {
                        "yield_potential": 7500,
                        "duration": 95,
                        "soil_preference": [SoilType.LOAMY, SoilType.LOAMY],
                        "water_requirement": 450,
                        "temperature_range": (20, 30),
                        "rainfall_range": (400, 800),
                        "resistance": ["quality_protein", "stem_borer_tolerant"],
                        "market_demand": "medium",
                        "investment_cost": 22000
                    }
                },
                "seasons": [SeasonType.KHARIF, SeasonType.RABI],
                "planting_months": [6, 7, 11, 12],
                "harvest_months": [9, 10, 2, 3]
            }
        }
    
    def _load_regional_data(self):
        """Load regional crop suitability and climate data"""
        self.regional_data = {
            "Punjab": {
                "major_crops": [CropType.WHEAT, CropType.RICE, CropType.MAIZE],
                "soil_types": [SoilType.LOAMY, SoilType.LOAMY],
                "climate": "subtropical",
                "rainfall_average": 650,  # mm
                "temperature_range": (5, 45),
                "irrigation_availability": "high",
                "market_access": "excellent"
            },
            "Rajasthan": {
                "major_crops": [CropType.WHEAT, CropType.MUSTARD, CropType.COTTON],
                "soil_types": [SoilType.SANDY, SoilType.SANDY],
                "climate": "arid",
                "rainfall_average": 300,
                "temperature_range": (0, 50),
                "irrigation_availability": "limited",
                "market_access": "good"
            },
            "Maharashtra": {
                "major_crops": [CropType.COTTON, CropType.SUGARCANE, CropType.RICE],
                "soil_types": [SoilType.CLAY, SoilType.LOAMY, SoilType.SANDY],
                "climate": "tropical",
                "rainfall_average": 1200,
                "temperature_range": (10, 42),
                "irrigation_availability": "medium",
                "market_access": "excellent"
            },
            "Uttar Pradesh": {
                "major_crops": [CropType.WHEAT, CropType.RICE, CropType.SUGARCANE],
                "soil_types": [SoilType.LOAMY, SoilType.LOAMY],
                "climate": "subtropical",
                "rainfall_average": 800,
                "temperature_range": (2, 46),
                "irrigation_availability": "good",
                "market_access": "good"
            }
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """
        Process crop selection related queries with satellite data integration.
        
        Args:
            query: Agriculture query object
            
        Returns:
            AgentResponse with crop recommendations enhanced by satellite data
        """
        try:
            logger.info(f"Processing crop selection query with satellite integration: {query.query_text}")
            
            # Extract key information from query
            context = self._extract_context_from_query(query)
            
            # Get satellite data if location is available
            satellite_data = None
            if context.get("location") and hasattr(context["location"], "latitude") and hasattr(context["location"], "longitude"):
                try:
                    logger.info(f"[SATELLITE] Fetching satellite data for location: {context['location'].latitude}, {context['location'].longitude}")
                    satellite_data = await get_satellite_data_for_location(
                        context["location"].latitude,
                        context["location"].longitude,
                        getattr(context["location"], "name", None)
                    )
                    logger.info(f"[SATELLITE] Satellite data retrieved successfully")
                except Exception as e:
                    logger.warning(f"[SATELLITE] Could not fetch satellite data: {e}")
                    satellite_data = None
            
            # Enhance context with satellite data
            if satellite_data:
                context = self._enhance_context_with_satellite_data(context, satellite_data)
            
            # Generate crop recommendations with satellite insights
            recommendations = await self._generate_crop_recommendations(context, satellite_data)
            
            # Calculate confidence based on available data (including satellite)
            confidence = self._calculate_confidence(context, recommendations, satellite_data)
            
            # Format response with satellite insights
            response_data = {
                "recommendations": [rec.__dict__ for rec in recommendations],
                "context_analysis": context,
                "satellite_insights": satellite_data,
                "confidence_score": confidence,
                "additional_advice": self._generate_additional_advice(context, recommendations, satellite_data)
            }
            
            # Include satellite summary in sources
            sources = ["crop_database", "regional_data", "agricultural_research"]
            if satellite_data:
                sources.append("satellite_data")
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Crop recommendations for {context.get('location', 'your area')}",
                confidence_score=confidence,
                reasoning=f"Analysis based on {len(sources)} data sources including satellite data",
                sources=sources,
                recommendations=[rec.__dict__ for rec in recommendations],
                metadata=response_data,
                processing_time_ms=int(0.0 * 1000)  # Will be calculated by caller
            )
            
        except Exception as e:
            logger.error(f"Error processing crop selection query: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Error processing query: {str(e)}",
                confidence_score=0.0,
                sources=[],
                recommendations=[]
            )
    
    def _extract_context_from_query(self, query: AgricultureQuery) -> Dict[str, Any]:
        """Extract relevant context from the query"""
        context = {
            "location": None,
            "season": None,
            "soil_type": None,
            "farm_size": None,
            "budget": None,
            "specific_crop": None,
            "weather_conditions": None,
            "irrigation_available": None,
            "experience_level": "intermediate"
        }
        
        # Extract from farm profile if available
        if query.farm_profile:
            context["location"] = query.farm_profile.location
            context["soil_type"] = query.farm_profile.soil_type
            context["farm_size"] = query.farm_profile.farm_size
            context["irrigation_available"] = query.farm_profile.irrigation_available
        
        # Extract from query text using keyword matching
        query_text = query.query_text.lower()
        
        # Season detection
        if any(word in query_text for word in ["rabi", "winter", "december", "january", "february"]):
            context["season"] = SeasonType.RABI
        elif any(word in query_text for word in ["kharif", "monsoon", "june", "july", "august"]):
            context["season"] = SeasonType.KHARIF
        elif any(word in query_text for word in ["zaid", "summer", "march", "april", "may"]):
            context["season"] = SeasonType.ZAID
        
        # Location detection
        for state in self.regional_data.keys():
            if state.lower() in query_text:
                context["location"] = state
                break
        
        # Crop type detection
        for crop_type in CropType:
            crop_names = [crop_type.value, crop_type.name.lower()]
            # Add common Hindi names
            hindi_names = {
                CropType.WHEAT: ["gehu", "gehun"],
                CropType.RICE: ["chawal", "dhan"],
                CropType.COTTON: ["kapas"],
                CropType.SUGARCANE: ["ganna"],
                CropType.MAIZE: ["makka"]
            }
            if crop_type in hindi_names:
                crop_names.extend(hindi_names[crop_type])
            
            if any(name in query_text for name in crop_names):
                context["specific_crop"] = crop_type
                break
        
        # Soil type detection
        soil_keywords = {
            "sandy": SoilType.SANDY,
            "clay": SoilType.CLAY, 
            "loamy": SoilType.LOAMY,
            "black": SoilType.CLAY,
            "red": SoilType.SANDY
        }
        for keyword, soil_type in soil_keywords.items():
            if keyword in query_text:
                context["soil_type"] = soil_type
                break
        
        return context
    
    async def _generate_crop_recommendations(self, context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[CropRecommendation]:
        """Generate crop recommendations based on context and satellite data"""
        recommendations = []
        
        # Determine current season if not specified
        current_month = datetime.now().month
        if not context["season"]:
            if current_month in [10, 11, 12, 1, 2, 3]:
                context["season"] = SeasonType.RABI
            elif current_month in [4, 5, 6, 7, 8, 9]:
                context["season"] = SeasonType.KHARIF
        
        # If specific crop requested, focus on that
        if context["specific_crop"]:
            crop_recommendations = self._analyze_specific_crop(
                context["specific_crop"], context, satellite_data
            )
            recommendations.extend(crop_recommendations)
        else:
            # General recommendations based on season and location
            for crop_type, crop_data in self.crop_database.items():
                if context["season"] in crop_data["seasons"]:
                    crop_recommendations = self._analyze_specific_crop(crop_type, context, satellite_data)
                    recommendations.extend(crop_recommendations)
        
        # Sort by suitability score (enhanced with satellite data)
        recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
        
        # Return top 5 recommendations
        return recommendations[:5]
    
    def _analyze_specific_crop(self, crop_type: CropType, context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[CropRecommendation]:
        """Analyze suitability of a specific crop type with satellite data"""
        recommendations = []
        
        if crop_type not in self.crop_database:
            return recommendations
        
        crop_data = self.crop_database[crop_type]
        
        for variety_name, variety_data in crop_data["varieties"].items():
            suitability_score = self._calculate_suitability_score(
                variety_data, context, satellite_data
            )
            
            if suitability_score > 0.3:  # Only include reasonably suitable crops
                recommendation = CropRecommendation(
                    crop_type=crop_type,
                    variety=variety_name,
                    suitability_score=suitability_score,
                    expected_yield=variety_data["yield_potential"] * suitability_score,
                    cultivation_period=variety_data["duration"],
                    water_requirement=variety_data["water_requirement"],
                    investment_cost=variety_data["investment_cost"],
                    market_demand=variety_data["market_demand"],
                    risk_factors=self._identify_risk_factors(variety_data, context, satellite_data),
                    cultivation_tips=self._generate_cultivation_tips(variety_data, context, satellite_data),
                    reason=self._generate_recommendation_reason(variety_data, context, suitability_score, satellite_data)
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_suitability_score(self, variety_data: Dict[str, Any], context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> float:
        """Calculate suitability score for a crop variety with satellite data enhancement"""
        score = 0.5  # Base score
        factors = []
        
        # Soil suitability (20% weight - reduced to make room for satellite data)
        if context["soil_type"] and context["soil_type"] in variety_data["soil_preference"]:
            score += 0.20
            factors.append("soil_match")
        elif context["soil_type"]:
            score += 0.08  # Partial match
        
        # Satellite data enhancement (20% weight)
        if satellite_data:
            satellite_score = self._calculate_satellite_score(variety_data, satellite_data)
            score += satellite_score
            if satellite_score > 0.1:
                factors.append("satellite_favorable")
        
        # Regional suitability (15% weight)
        if context["location"] and context["location"] in self.regional_data:
            regional_info = self.regional_data[context["location"]]
            if variety_data.get("market_demand") == "high" and context["location"] in ["Punjab", "Maharashtra"]:
                score += 0.12
            score += 0.03  # Base regional bonus
            factors.append("regional_suitable")
        
        # Climate suitability (15% weight)
        if context["location"] and context["location"] in self.regional_data:
            regional_info = self.regional_data[context["location"]]
            temp_range = variety_data["temperature_range"]
            regional_temp = regional_info["temperature_range"]
            
            # Check temperature compatibility
            if (temp_range[0] <= regional_temp[1] and temp_range[1] >= regional_temp[0]):
                score += 0.12
                factors.append("climate_suitable")
        
        # Water availability (15% weight)
        if context["irrigation_available"]:
            if variety_data["water_requirement"] > 800 and context["irrigation_available"]:
                score += 0.12
            elif variety_data["water_requirement"] <= 500:  # Drought tolerant
                score += 0.08
            factors.append("water_suitable")
        
        # Market demand (8% weight)
        market_scores = {"very_high": 0.08, "high": 0.06, "medium": 0.04, "low": 0.02}
        score += market_scores.get(variety_data["market_demand"], 0.02)
        
        # Resistance/tolerance (7% weight)
        if "drought_tolerant" in variety_data.get("resistance", []):
            score += 0.035
        if "disease_resistant" in str(variety_data.get("resistance", [])).lower():
            score += 0.035
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _identify_risk_factors(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors for the crop"""
        risks = []
        
        # Weather risks
        if variety_data["water_requirement"] > 1000:
            risks.append("High water requirement - drought risk")
        
        # Market risks
        if variety_data["market_demand"] == "low":
            risks.append("Limited market demand")
        
        # Investment risks
        if variety_data["investment_cost"] > 40000:
            risks.append("High initial investment required")
        
        # Duration risks
        if variety_data["duration"] > 150:
            risks.append("Long cultivation period - weather risk")
        
        # Regional risks
        if context["location"] == "Rajasthan" and variety_data["water_requirement"] > 600:
            risks.append("Water scarcity in region")
        
        return risks
    
    def _generate_cultivation_tips(self, variety_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate cultivation tips based on variety and context"""
        tips = []
        
        # Soil preparation
        if context["soil_type"] == SoilType.SANDY:
            tips.append("Add organic matter to improve soil water retention")
        elif context["soil_type"] == SoilType.CLAY:
            tips.append("Ensure proper drainage to prevent waterlogging")
        
        # Irrigation
        if variety_data["water_requirement"] > 800:
            tips.append("Install drip irrigation system for water efficiency")
        else:
            tips.append("Monitor soil moisture regularly")
        
        # Fertilization
        tips.append(f"Apply balanced NPK fertilizer as per soil test recommendations")
        
        # Pest management
        if "resistant" in str(variety_data.get("resistance", [])).lower():
            tips.append("Use integrated pest management practices")
        
        # Timing
        tips.append("Plant during optimal weather window for best results")
        
        return tips
    
    def _generate_recommendation_reason(self, variety_data: Dict[str, Any], context: Dict[str, Any], score: float) -> str:
        """Generate explanation for why this crop is recommended"""
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent match for your conditions")
        elif score > 0.6:
            reasons.append("Good suitability for your farm")
        else:
            reasons.append("Moderate suitability with proper management")
        
        if context["soil_type"] and context["soil_type"] in variety_data["soil_preference"]:
            reasons.append(f"well-suited for {context['soil_type'].value} soil")
        
        if variety_data["market_demand"] in ["high", "very_high"]:
            reasons.append("strong market demand")
        
        if "drought_tolerant" in variety_data.get("resistance", []):
            reasons.append("drought tolerance")
        
        return ", ".join(reasons)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "Crop variety recommendation based on soil and climate",
            "Yield prediction and profitability analysis", 
            "Seasonal crop planning and rotation advice",
            "Risk assessment and mitigation strategies",
            "Cultivation guidance and best practices",
            "Market demand analysis for crop selection"
        ]
    
    def get_supported_queries(self) -> List[str]:
        """Return examples of supported query types"""
        return [
            "What crop should I grow in [location] during [season]?",
            "Best wheat variety for clay soil",
            "High yield crops for small farms",
            "Drought resistant crops for water scarce areas",
            "Profitable crops with low investment",
            "Crop recommendations for organic farming"
        ]

    def _enhance_context_with_satellite_data(self, context: Dict, satellite_data: Dict) -> Dict:
        """Enhance context with satellite data insights"""
        enhanced_context = context.copy()
        
        if satellite_data:
            enhanced_context["satellite_insights"] = {
                "vegetation_health": satellite_data.get("ndvi", 0.0),
                "soil_moisture": satellite_data.get("soil_moisture", 0.0),
                "weather_conditions": satellite_data.get("weather", {}),
                "land_suitability": self._assess_land_suitability(satellite_data)
            }
            
        return enhanced_context
    
    def _calculate_satellite_score(self, variety_data: Dict, satellite_data: Dict) -> float:
        """Calculate suitability score based on satellite data"""
        score = 0.0
        
        # NDVI-based vegetation health assessment (0.10 max)
        ndvi = satellite_data.get("ndvi", 0.0)
        if ndvi > 0.7:  # Excellent vegetation health
            score += 0.10
        elif ndvi > 0.5:  # Good vegetation health
            score += 0.07
        elif ndvi > 0.3:  # Moderate vegetation health
            score += 0.05
        
        # Soil moisture assessment (0.06 max)
        soil_moisture = satellite_data.get("soil_moisture", 0.0)
        water_req = variety_data.get("water_requirement", 500)
        
        if water_req > 800:  # High water requirement crops
            if soil_moisture > 0.7:
                score += 0.06
            elif soil_moisture > 0.5:
                score += 0.04
        else:  # Low water requirement crops
            if soil_moisture > 0.3:
                score += 0.06
            elif soil_moisture > 0.2:
                score += 0.04
        
        # Weather pattern assessment (0.04 max)
        weather = satellite_data.get("weather", {})
        if weather:
            temp = weather.get("temperature", 25)
            humidity = weather.get("humidity", 50)
            
            temp_range = variety_data.get("temperature_range", [15, 35])
            if temp_range[0] <= temp <= temp_range[1]:
                score += 0.02
            
            if 40 <= humidity <= 80:  # Optimal humidity range
                score += 0.02
        
        return min(score, 0.20)  # Cap at 20% of total score
    
    def _assess_land_suitability(self, satellite_data: Dict) -> str:
        """Assess overall land suitability based on satellite data"""
        ndvi = satellite_data.get("ndvi", 0.0)
        soil_moisture = satellite_data.get("soil_moisture", 0.0)
        
        if ndvi > 0.7 and soil_moisture > 0.6:
            return "Excellent"
        elif ndvi > 0.5 and soil_moisture > 0.4:
            return "Good"
        elif ndvi > 0.3 and soil_moisture > 0.3:
            return "Moderate"
        else:
            return "Poor"
    
    def _calculate_confidence(self, context: Dict, recommendations: List, satellite_data: Optional[Dict] = None) -> float:
        """Calculate confidence score including satellite data availability"""
        base_confidence = 0.6
        
        # Context completeness
        if context.get("location"):
            base_confidence += 0.1
        if context.get("soil_type"):
            base_confidence += 0.1
        if context.get("season"):
            base_confidence += 0.1
        
        # Satellite data availability bonus
        if satellite_data:
            base_confidence += 0.1
        
        # Recommendation quality
        if recommendations and len(recommendations) > 0:
            avg_suitability = sum(rec.suitability_score for rec in recommendations) / len(recommendations)
            base_confidence += avg_suitability * 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_additional_advice(self, context: Dict, recommendations: List, satellite_data: Optional[Dict] = None) -> List[str]:
        """Generate additional advice including satellite insights"""
        advice = []
        
        # Base advice
        if context.get("season") == SeasonType.KHARIF:
            advice.append("Consider monsoon timing for planting")
        if context.get("soil_type") == "clay":
            advice.append("Ensure proper drainage for clay soil")
        
        # Satellite-based advice
        if satellite_data:
            ndvi = satellite_data.get("ndvi", 0.0)
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            
            if ndvi < 0.3:
                advice.append("[SATELLITE] Satellite data shows low vegetation health - consider soil improvement")
            if soil_moisture < 0.3:
                advice.append("[SATELLITE] Low soil moisture detected - irrigation planning recommended")
            if ndvi > 0.7:
                advice.append("[SATELLITE] Excellent vegetation conditions detected - optimal for planting")
        
        return advice
    
    def _format_recommendations_summary(self, recommendations: List, satellite_data: Optional[Dict] = None) -> List[str]:
        """Format recommendations summary including satellite insights"""
        summary = []
        
        for rec in recommendations[:3]:  # Top 3 recommendations
            rec_text = f"{rec.crop_type.value} ({rec.variety}) - Score: {rec.suitability_score:.2f}"
            if satellite_data:
                rec_text += " [SAT]"
            summary.append(rec_text)
        
        return summary
    
    def _identify_risk_factors(self, variety_data: Dict[str, Any], context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[str]:
        """Identify potential risk factors including satellite-based risks"""
        risks = []
        
        # Traditional risks
        if variety_data["water_requirement"] > 1000:
            risks.append("High water requirement - drought risk")
        if variety_data["market_demand"] == "low":
            risks.append("Limited market demand")
        if variety_data["investment_cost"] > 40000:
            risks.append("High initial investment required")
        if variety_data["duration"] > 150:
            risks.append("Long cultivation period - weather risk")
        
        # Satellite-based risks
        if satellite_data:
            ndvi = satellite_data.get("ndvi", 0.0)
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            
            if ndvi < 0.3:
                risks.append("[SATELLITE] Poor vegetation health detected")
            if soil_moisture < 0.2:
                risks.append("[SATELLITE] Very low soil moisture - drought risk")
        
        return risks
    
    def _generate_cultivation_tips(self, variety_data: Dict[str, Any], context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[str]:
        """Generate cultivation tips including satellite-based insights"""
        tips = []
        
        # Base tips
        if variety_data["water_requirement"] > 800:
            tips.append("Implement drip irrigation for water efficiency")
        if "disease_resistant" not in str(variety_data.get("resistance", [])).lower():
            tips.append("Regular monitoring for disease prevention")
        
        # Satellite-based tips
        if satellite_data:
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            ndvi = satellite_data.get("ndvi", 0.0)
            
            if soil_moisture > 0.8:
                tips.append("[SATELLITE] High soil moisture - ensure good drainage")
            elif soil_moisture < 0.3:
                tips.append("[SATELLITE] Low soil moisture - increase irrigation frequency")
            
            if ndvi > 0.6:
                tips.append("[SATELLITE] Good field conditions for optimal planting")
        
        return tips
    
    def _generate_recommendation_reason(self, variety_data: Dict[str, Any], context: Dict[str, Any], suitability_score: float, satellite_data: Optional[Dict] = None) -> str:
        """Generate recommendation reasoning including satellite insights"""
        reasons = []
        
        # Base reasoning
        if suitability_score > 0.8:
            reasons.append("Excellent match for your conditions")
        elif suitability_score > 0.6:
            reasons.append("Good suitability for your farm")
        else:
            reasons.append("Moderate suitability")
        
        if context.get("soil_type") in variety_data.get("soil_preference", []):
            reasons.append(f"Well-suited for {context['soil_type']} soil")
        
        # Satellite reasoning
        if satellite_data:
            ndvi = satellite_data.get("ndvi", 0.0)
            if ndvi > 0.6:
                reasons.append("[SATELLITE] satellite data confirms favorable field conditions")
            elif ndvi < 0.3:
                reasons.append("[SATELLITE] satellite data suggests field preparation needed")
        
        return ". ".join(reasons) + "."
