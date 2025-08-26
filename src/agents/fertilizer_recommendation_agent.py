"""
Fertilizer Recommendation Agent
Specialized agent for recommending optimal fertilizer types and application rates
based on soil NPK values, crop type, and environmental conditions.
Integrates with AgriSens fertilizer recommendation model.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..core.models import AgentCapability
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType,
    WeatherData, Location, FarmProfile, QueryDomain
)
# AgriSens Model Integration
from ..models.agrisens_fertilizer_recommendation import (
    get_fertilizer_recommendation_model, FertilizerRecommendationData, FertilizerRecommendation
)

logger = logging.getLogger(__name__)


@dataclass
class FertilizerAdvice:
    """Detailed fertilizer recommendation with application advice"""
    fertilizer_name: str
    npk_ratio: str
    application_rate: float  # kg/hectare
    application_method: str
    application_timing: str
    cost_estimate: float  # cost per hectare
    environmental_impact: str
    alternatives: List[str]
    soil_suitability: float  # 0-1 scale
    expected_benefits: List[str]
    satellite_enhanced: bool = False


class FertilizerRecommendationAgent(BaseWorkerAgent):
    """
    Agent for recommending optimal fertilizers based on soil analysis,
    crop requirements, and environmental factors
    """
    
    def __init__(self, agent_id: str, name: str):
        """Initialize the fertilizer recommendation agent"""
        super().__init__(agent_id, name)
        self.model = None
        self._capabilities = [
            AgentCapability.FERTILIZER_RECOMMENDATION,
            AgentCapability.SOIL_ANALYSIS,
            AgentCapability.NUTRIENT_MANAGEMENT
        ]
    
    def initialize(self):
        """Load the fertilizer recommendation model"""
        logger.info("Loading AgriSens fertilizer recommendation model...")
        self.model = get_fertilizer_recommendation_model()
        logger.info("Fertilizer recommendation agent initialized successfully")
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [cap.value for cap in self._capabilities]
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a fertilizer recommendation query"""
        logger.info(f"Processing fertilizer recommendation query: {query.query_text}")
        
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="fertilizer_recommendation",
            message="Processing fertilizer recommendation",
            data={}
        )
        
        try:
            # Extract soil data from query
            soil_data = self._extract_soil_data(query)
            if not soil_data:
                response.message = "Insufficient soil data provided for fertilizer recommendation"
                return response
            
            # Get satellite data if location is available
            satellite_data = None
            soil_moisture = None
            if query.location:
                try:
                    satellite_data = await get_satellite_data_for_location(
                        query.location.latitude,
                        query.location.longitude
                    )
                    if satellite_data and 'soil_moisture' in satellite_data:
                        soil_moisture = satellite_data['soil_moisture'].get('value')
                except Exception as e:
                    logger.warning(f"Failed to get satellite data: {e}")
            
            # Adjust moisture based on satellite data
            if soil_moisture is not None:
                soil_data.moisture = soil_moisture
            
            # Generate fertilizer recommendation
            fertilizer_rec = self._generate_fertilizer_recommendation(soil_data, query.crop_type)
            
            # Create detailed fertilizer advice
            fertilizer_advice = self._create_fertilizer_advice(fertilizer_rec, query.crop_type, satellite_data)
            
            # Prepare response
            response.success = True
            response.message = f"Recommended {fertilizer_advice.fertilizer_name} ({fertilizer_advice.npk_ratio}) at {fertilizer_advice.application_rate} kg/hectare"
            response.data = {
                "recommendation": {
                    "fertilizer_name": fertilizer_advice.fertilizer_name,
                    "npk_ratio": fertilizer_advice.npk_ratio,
                    "application_rate": fertilizer_advice.application_rate,
                    "application_method": fertilizer_advice.application_method,
                    "application_timing": fertilizer_advice.application_timing,
                    "cost_estimate": fertilizer_advice.cost_estimate,
                    "environmental_impact": fertilizer_advice.environmental_impact,
                    "alternatives": fertilizer_advice.alternatives,
                    "soil_suitability": fertilizer_advice.soil_suitability,
                    "expected_benefits": fertilizer_advice.expected_benefits,
                    "confidence": fertilizer_rec.confidence
                },
                "soil_analysis": {
                    "nitrogen": soil_data.nitrogen,
                    "phosphorus": soil_data.phosphorus,
                    "potassium": soil_data.potassium,
                    "ph": soil_data.ph,
                    "soil_type": soil_data.soil_type,
                    "moisture": soil_data.moisture,
                    "temperature": soil_data.temperature,
                    "humidity": soil_data.humidity
                },
                "satellite_data": format_satellite_summary(satellite_data) if satellite_data else None,
                "satellite_enhanced": satellite_data is not None
            }
            
        except Exception as e:
            logger.error(f"Error in fertilizer recommendation: {e}", exc_info=True)
            response.message = f"Error processing fertilizer recommendation: {str(e)}"
        
        return response
    
    def _extract_soil_data(self, query: AgricultureQuery) -> Optional[FertilizerRecommendationData]:
        """
        Extract soil data from query
        
        Args:
            query: The agriculture query containing soil data
            
        Returns:
            FertilizerRecommendationData object or None if insufficient data
        """
        # Default values
        nitrogen = 0.0
        phosphorus = 0.0
        potassium = 0.0
        ph = 7.0
        temperature = 25.0
        humidity = 60.0
        moisture = 50.0
        soil_type = "Loamy"
        crop_type = "Wheat"
        
        # Extract soil data if available
        if hasattr(query, 'soil_data') and query.soil_data:
            soil_data = query.soil_data
            nitrogen = soil_data.get('nitrogen', nitrogen)
            phosphorus = soil_data.get('phosphorus', phosphorus) or soil_data.get('phosphorous', phosphorus)
            potassium = soil_data.get('potassium', potassium)
            ph = soil_data.get('ph', ph)
            moisture = soil_data.get('moisture', moisture)
        
        # Extract environmental data if available
        if hasattr(query, 'weather_data') and query.weather_data:
            weather_data = query.weather_data
            temperature = weather_data.get('temperature', temperature)
            humidity = weather_data.get('humidity', humidity)
        
        # Extract soil type
        if query.soil_type:
            soil_type = self._map_soil_type(query.soil_type)
        
        # Extract crop type
        if query.crop_type:
            crop_type = self._map_crop_type(query.crop_type)
        
        # Check if we have enough data
        if nitrogen == 0 and phosphorus == 0 and potassium == 0:
            logger.warning("Insufficient NPK data for fertilizer recommendation")
            return None
        
        return FertilizerRecommendationData(
            temperature=temperature,
            humidity=humidity,
            moisture=moisture,
            soil_type=soil_type,
            crop_type=crop_type,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph=ph
        )
    
    def _map_soil_type(self, soil_type: str) -> str:
        """Map soil type to one recognized by the model"""
        soil_mapping = {
            SoilType.SANDY.value: "Sandy",
            SoilType.LOAM.value: "Loamy",
            SoilType.CLAY.value: "Clayey",
            SoilType.SILT.value: "Loamy",
            SoilType.BLACK_SOIL.value: "Black",
            SoilType.RED_SOIL.value: "Red",
            SoilType.LATERITE.value: "Red"
        }
        return soil_mapping.get(soil_type, "Loamy")
    
    def _map_crop_type(self, crop_type: str) -> str:
        """Map crop type to one recognized by the model"""
        crop_mapping = {
            CropType.WHEAT.value: "Wheat",
            CropType.RICE.value: "Paddy",
            CropType.MAIZE.value: "Maize",
            CropType.SUGARCANE.value: "Sugarcane",
            CropType.COTTON.value: "Cotton",
            CropType.BARLEY.value: "Barley",
            CropType.MILLET.value: "Millets",
            CropType.TOBACCO.value: "Tobacco",
            # Add mappings for other crops as needed
        }
        return crop_mapping.get(crop_type, "Wheat")
    
    def _generate_fertilizer_recommendation(
        self, soil_data: FertilizerRecommendationData, crop_type: Optional[str] = None
    ) -> FertilizerRecommendation:
        """
        Generate fertilizer recommendation based on soil data
        
        Args:
            soil_data: Soil analysis data
            crop_type: Optional crop type
            
        Returns:
            FertilizerRecommendation object
        """
        if self.model is None:
            self.initialize()
        
        # If crop type is provided, update in soil_data
        if crop_type:
            soil_data.crop_type = self._map_crop_type(crop_type)
        
        # Get recommendation from model
        recommendation = self.model.predict(soil_data)
        return recommendation
    
    def _create_fertilizer_advice(
        self, recommendation: FertilizerRecommendation, crop_type: Optional[str], satellite_data: Optional[Dict[str, Any]]
    ) -> FertilizerAdvice:
        """
        Create detailed fertilizer advice from model recommendation
        
        Args:
            recommendation: FertilizerRecommendation from model
            crop_type: Optional crop type
            satellite_data: Optional satellite data
            
        Returns:
            FertilizerAdvice object with detailed application guidance
        """
        # Calculate soil suitability
        soil_suitability = recommendation.confidence / 100.0
        
        # Generate expected benefits
        expected_benefits = self._generate_expected_benefits(
            recommendation.fertilizer_name,
            recommendation.npk_ratio,
            crop_type
        )
        
        # Enhance with satellite data if available
        satellite_enhanced = False
        if satellite_data:
            satellite_enhanced = True
            # Adjust benefits based on satellite data
            if 'ndvi' in satellite_data and satellite_data['ndvi'].get('value', 0) < 0.4:
                expected_benefits.append("Will help improve low vegetation health detected via satellite")
            
            # Adjust application method based on weather forecast
            if 'precipitation' in satellite_data and satellite_data['precipitation'].get('forecast_mm', 0) > 20:
                application_method = f"{recommendation.application_method} (Apply before forecasted rain)"
            else:
                application_method = recommendation.application_method
        else:
            application_method = recommendation.application_method
        
        return FertilizerAdvice(
            fertilizer_name=recommendation.fertilizer_name,
            npk_ratio=recommendation.npk_ratio,
            application_rate=recommendation.application_rate,
            application_method=application_method,
            application_timing=recommendation.timing,
            cost_estimate=recommendation.cost_estimate or 0.0,
            environmental_impact=recommendation.environmental_impact or "Moderate",
            alternatives=recommendation.alternatives or [],
            soil_suitability=soil_suitability,
            expected_benefits=expected_benefits,
            satellite_enhanced=satellite_enhanced
        )
    
    def _generate_expected_benefits(
        self, fertilizer_name: str, npk_ratio: str, crop_type: Optional[str]
    ) -> List[str]:
        """Generate expected benefits based on fertilizer and crop"""
        benefits = []
        
        # Parse NPK ratio
        try:
            n, p, k = map(int, npk_ratio.split('-'))
            
            # Add nitrogen benefits
            if n > 30:
                benefits.append("Promotes leaf growth and vegetative development")
                benefits.append("Increases protein content in the crop")
            
            # Add phosphorus benefits
            if p > 30:
                benefits.append("Enhances root development and flowering")
                benefits.append("Improves seed and fruit formation")
            
            # Add potassium benefits
            if k > 30:
                benefits.append("Improves crop quality and disease resistance")
                benefits.append("Enhances water use efficiency and drought tolerance")
                
            # Balanced fertilizer benefits
            if n > 10 and p > 10 and k > 10:
                benefits.append("Provides balanced nutrition for overall crop development")
        except:
            # Fallback if NPK ratio parsing fails
            if "Urea" in fertilizer_name:
                benefits.append("High nitrogen content for vigorous vegetative growth")
            elif "DAP" in fertilizer_name:
                benefits.append("Good phosphorus content for root development and flowering")
            else:
                benefits.append("Provides essential nutrients for crop growth")
        
        # Add crop-specific benefits
        if crop_type:
            crop_benefits = {
                "Wheat": "Optimizes protein content and grain quality in wheat",
                "Rice": "Enhances tillering and grain filling in paddy",
                "Maize": "Improves cob development and kernel filling in maize",
                "Cotton": "Promotes boll development and fiber quality in cotton",
                "Sugarcane": "Increases sugar content and stalk development in sugarcane"
            }
            if crop_type in crop_benefits:
                benefits.append(crop_benefits[crop_type])
        
        return benefits
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other agents"""
        if message.get("type") == "fertilizer_request":
            # Handle requests from other agents for fertilizer recommendations
            soil_data = message.get("soil_data")
            crop_type = message.get("crop_type")
            
            if soil_data:
                try:
                    rec_data = FertilizerRecommendationData(
                        temperature=soil_data.get("temperature", 25.0),
                        humidity=soil_data.get("humidity", 60.0),
                        moisture=soil_data.get("moisture", 50.0),
                        soil_type=self._map_soil_type(soil_data.get("soil_type", "Loamy")),
                        crop_type=self._map_crop_type(crop_type or "Wheat"),
                        nitrogen=soil_data.get("nitrogen", 0.0),
                        phosphorus=soil_data.get("phosphorus", 0.0) or soil_data.get("phosphorous", 0.0),
                        potassium=soil_data.get("potassium", 0.0),
                        ph=soil_data.get("ph", 7.0)
                    )
                    
                    recommendation = self._generate_fertilizer_recommendation(rec_data, crop_type)
                    
                    return {
                        "success": True,
                        "fertilizer_name": recommendation.fertilizer_name,
                        "application_rate": recommendation.application_rate,
                        "npk_ratio": recommendation.npk_ratio,
                        "cost_estimate": recommendation.cost_estimate
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
            else:
                return {"success": False, "error": "No soil data provided"}
                
        return {"success": False, "error": "Unknown message type"}
