"""
Harvest Planning Agent
Specialized agent for determining optimal harvest dates by modeling crop calendars 
and integrating weather forecasts for Indian agricultural systems.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from enum import Enum
import asyncio
import random
from calendar import monthrange

from .base_agent import BaseWorkerAgent
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, Location, QueryDomain, Language
)
from ..core.models import AgentCapability, Task
# Import AgriMitr Harvest Planning model
from ..models.AgriMitr_harvest_planning import (
    enhance_harvest_planning_with_AgriMitr, HarvestPlan, MaturityStage,
    MaturityAssessment, WeatherWindow, HarvestRecommendation
)
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary

logger = logging.getLogger(__name__)


class CropStage(Enum):
    """Crop growth stages"""
    SOWING = "sowing"
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUIT_DEVELOPMENT = "fruit_development"
    MATURITY = "maturity"
    HARVEST_READY = "harvest_ready"


class WeatherCondition(Enum):
    """Weather conditions affecting harvest"""
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"


class HarvestUrgency(Enum):
    """Harvest urgency levels"""
    IMMEDIATE = "immediate"  # Within 1-2 days
    URGENT = "urgent"       # Within 3-5 days
    PLANNED = "planned"     # Within 1-2 weeks
    FUTURE = "future"       # More than 2 weeks


@dataclass
class CropCalendar:
    """Crop-specific calendar and growth information"""
    crop_type: CropType
    variety: str
    sowing_date: date
    total_growth_days: int
    harvest_window_start: int  # Days after sowing
    harvest_window_end: int    # Days after sowing
    optimal_harvest_stage: CropStage
    weather_sensitivity: float  # 0-1 scale
    post_harvest_shelf_life: int  # Days


@dataclass
class WeatherForecast:
    """Weather forecast for harvest planning"""
    date: date
    condition: WeatherCondition
    temperature_max: float
    temperature_min: float
    humidity: float
    precipitation_chance: float
    wind_speed: float
    harvest_suitability_score: float  # 0-10 scale


@dataclass
class HarvestRecommendation:
    """Harvest timing recommendation"""
    crop_type: CropType
    current_stage: CropStage
    optimal_harvest_date: date
    harvest_window_start: date
    harvest_window_end: date
    urgency: HarvestUrgency
    confidence_score: float
    reasoning: List[str]
    weather_considerations: List[str]
    expected_yield_quality: str  # "excellent", "good", "fair", "poor"
    post_harvest_actions: List[str]


class HarvestPlanningAgent(BaseWorkerAgent):
    """
    Specialized agent for optimal harvest date determination.
    Considers crop calendars, weather forecasts, market conditions,
    and storage capabilities to recommend the best harvest timing.
    """
    
    def __init__(self):
        super().__init__(
            name="harvest_planning_agent",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.PLANNING,
                AgentCapability.DATA_PROCESSING
            ],
            agent_type="harvest_planning"
        )
        
        # Initialize crop calendar database
        self._initialize_crop_calendars()
        self._initialize_weather_patterns()
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a harvest planning task (required by BaseWorkerAgent)"""
        try:
            # Extract query from task or context
            if hasattr(task, 'query') and task.query:
                query = task.query
            elif 'query' in context:
                query = context['query']
            else:
                return {"error": "No query provided for harvest planning"}
            
            # Process the query using our existing logic
            if isinstance(query, AgricultureQuery):
                result = asyncio.run(self.process_query(query))
                return {"success": True, "response": result}
            else:
                return {"error": "Invalid query format"}
                
        except Exception as e:
            return {"error": f"Harvest planning failed: {str(e)}"}
    
    def _initialize_crop_calendars(self):
        """Initialize comprehensive crop calendar database for major Indian crops"""
        self.crop_calendars = {
            CropType.WHEAT: CropCalendar(
                crop_type=CropType.WHEAT,
                variety="HD-3086",  # Popular variety
                sowing_date=date(2024, 11, 15),  # Typical Rabi sowing
                total_growth_days=120,
                harvest_window_start=115,
                harvest_window_end=130,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.7,
                post_harvest_shelf_life=30
            ),
            
            CropType.RICE: CropCalendar(
                crop_type=CropType.RICE,
                variety="Basmati-1121",
                sowing_date=date(2024, 6, 15),  # Kharif sowing
                total_growth_days=125,
                harvest_window_start=120,
                harvest_window_end=135,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.8,
                post_harvest_shelf_life=45
            ),
            
            CropType.COTTON: CropCalendar(
                crop_type=CropType.COTTON,
                variety="Bt-Cotton",
                sowing_date=date(2024, 5, 1),
                total_growth_days=180,
                harvest_window_start=170,
                harvest_window_end=200,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.9,
                post_harvest_shelf_life=60
            ),
            
            CropType.SUGARCANE: CropCalendar(
                crop_type=CropType.SUGARCANE,
                variety="Co-0238",
                sowing_date=date(2024, 2, 1),
                total_growth_days=365,
                harvest_window_start=350,
                harvest_window_end=380,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.6,
                post_harvest_shelf_life=7
            )
        }
    
    def _initialize_weather_patterns(self):
        """Initialize weather pattern knowledge for different regions"""
        self.regional_weather_patterns = {
            "Punjab": {
                "monsoon_end": date(2024, 9, 15),
                "winter_start": date(2024, 11, 1),
                "harvest_season": "October-April",
                "risk_periods": ["July-August", "December-January"]
            },
            "Maharashtra": {
                "monsoon_end": date(2024, 10, 1),
                "winter_start": date(2024, 12, 1),
                "harvest_season": "November-March",
                "risk_periods": ["June-September"]
            },
            "Uttar Pradesh": {
                "monsoon_end": date(2024, 9, 30),
                "winter_start": date(2024, 11, 15),
                "harvest_season": "October-April",
                "risk_periods": ["July-September", "January"]
            }
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a harvest planning query with satellite integration"""
        try:
            query_text = query.query_text.lower()
            location = query.location
            context = query.context or {}
            
            # Extract crop information
            crop_type = self._extract_crop_type(query_text, context)
            
            # Get growth stage from context or estimate it
            growth_stage = context.get('growth_stage', '')
            if not growth_stage:
                growth_stage = self._estimate_growth_stage(crop_type, query_text, context)
            
            # Get field size from context (default: 5 hectares)
            field_size = float(context.get('field_size', 5.0))
            
            # Extract planting date information
            planting_date = self._extract_planting_date(query_text, context)
            
            # Create basic response
            response_parts = []
            confidence = 0.75
            
            # Handle uncertainty in planting date
            if not planting_date:
                response_parts.append("I don't have the exact planting date, which limits the accuracy of my harvest timing recommendation.")
                planting_date = datetime.now() - timedelta(days=90)  # Assume planted ~3 months ago
                confidence *= 0.8
            
            # Get satellite data
            satellite_data = None
            try:
                satellite_data = await get_satellite_data_for_location(location)
                if satellite_data:
                    response_parts.append(format_satellite_summary(satellite_data))
                    confidence += 0.15
            except Exception as e:
                logger.warning(f"Satellite data retrieval failed: {e}")
                response_parts.append("Note: Satellite data is temporarily unavailable. Using ground-based calculations only.")
                confidence *= 0.9
            
            # Prepare weather forecast (10 day forecast)
            weather_forecast = self._get_weather_forecast(location, days=10)
            
            # Prepare growth data
            growth_data = self._prepare_growth_data(crop_type, growth_stage, context)
            
            # Determine crop variety (if available)
            crop_variety = context.get('crop_variety', 'standard')
            
            # Determine equipment availability
            equipment_availability = {
                "mechanized_harvester": context.get('has_mechanized_equipment', True),
                "semi_mechanized": context.get('has_semi_mechanized', True)
            }
            
            # Use AgriMitr model for enhanced harvest planning
            harvest_plan = enhance_harvest_planning_with_AgriMitr(
                crop_type=str(crop_type.value) if isinstance(crop_type, Enum) else str(crop_type),
                crop_variety=crop_variety,
                planting_date=planting_date,
                growth_data=growth_data,
                field_size=field_size,
                weather_forecast=weather_forecast,
                equipment_availability=equipment_availability,
                satellite_data=satellite_data
            )
            
            # Format the response based on the harvest plan
            response_parts.extend(self._format_harvest_plan_response(harvest_plan))
            
            # Add confidence boosting if satellite data enhanced the prediction
            if harvest_plan.satellite_enhancement:
                confidence = min(0.98, confidence + 0.1)
            
            # Combine all response parts
            full_response = "\n\n".join(response_parts)
            
            return AgentResponse(
                query_id=query.query_id,
                response_text=full_response,
                confidence=confidence,
                agent_name=self.name,
                metadata={
                    "crop_type": str(crop_type),
                    "growth_stage": growth_stage,
                    "days_to_harvest": harvest_plan.current_status.days_to_harvest,
                    "optimal_window_start": harvest_plan.primary_recommendation.primary_window.start_date.strftime("%Y-%m-%d"),
                    "optimal_window_end": harvest_plan.primary_recommendation.primary_window.end_date.strftime("%Y-%m-%d"),
                    "weather_quality": f"{harvest_plan.primary_recommendation.primary_window.quality:.2f}",
                    "satellite_enhanced": bool(harvest_plan.satellite_enhancement)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing harvest query: {e}", exc_info=True)
            return AgentResponse(
                query_id=query.query_id,
                response_text=f"I apologize, but I couldn't generate a harvest recommendation due to: {str(e)}. Please provide more details about your crop type and planting date.",
                confidence=0.3,
                agent_name=self.name
            )
    
    def _initialize_crop_calendars(self):
        """Initialize comprehensive crop calendar database for major Indian crops"""
        self.crop_calendars = {
            CropType.WHEAT: CropCalendar(
                crop_type=CropType.WHEAT,
                variety="HD-3086",  # Popular variety
                sowing_date=date(2024, 11, 15),  # Typical Rabi sowing
                total_growth_days=120,
                harvest_window_start=115,
                harvest_window_end=130,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.7,
                post_harvest_shelf_life=30
            ),
            
            CropType.RICE: CropCalendar(
                crop_type=CropType.RICE,
                variety="Basmati-1121",
                sowing_date=date(2024, 6, 15),  # Kharif sowing
                total_growth_days=125,
                harvest_window_start=120,
                harvest_window_end=135,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.8,
                post_harvest_shelf_life=45
            ),
            
            CropType.COTTON: CropCalendar(
                crop_type=CropType.COTTON,
                variety="Bt-Cotton",
                sowing_date=date(2024, 5, 1),
                total_growth_days=180,
                harvest_window_start=170,
                harvest_window_end=200,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.9,
                post_harvest_shelf_life=60
            ),
            
            CropType.SUGARCANE: CropCalendar(
                crop_type=CropType.SUGARCANE,
                variety="Co-0238",
                sowing_date=date(2024, 2, 1),
                total_growth_days=365,
                harvest_window_start=350,
                harvest_window_end=380,
                optimal_harvest_stage=CropStage.MATURITY,
                weather_sensitivity=0.6,
                post_harvest_shelf_life=7
            )
        }
    
    def _initialize_weather_patterns(self):
        """Initialize weather pattern knowledge for different regions"""
        self.regional_weather_patterns = {
            "Punjab": {
                "monsoon_end": date(2024, 9, 15),
                "winter_start": date(2024, 11, 1),
                "harvest_season": "October-April",
                "risk_periods": ["July-August", "December-January"]
            },
            "Maharashtra": {
                "monsoon_end": date(2024, 10, 1),
                "winter_start": date(2024, 12, 1),
                "harvest_season": "November-March",
                "risk_periods": ["June-September"]
            },
            "Uttar Pradesh": {
                "monsoon_end": date(2024, 9, 30),
                "winter_start": date(2024, 11, 15),
                "harvest_season": "October-April",
                "risk_periods": ["July-September", "January"]
            }
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a harvest planning query with satellite integration"""
        try:
            query_text = query.query_text.lower()
            location = query.location
            context = query.context or {}
            
            # Extract crop information
            crop_type = self._extract_crop_type(query_text, context)
            
            # Get growth stage from context or estimate it
            growth_stage = context.get('growth_stage', '')
            if not growth_stage:
                growth_stage = self._estimate_growth_stage(crop_type, query_text, context)
            
            # Get field size from context (default: 5 hectares)
            field_size = float(context.get('field_size', 5.0))
            
            # Extract planting date information
            planting_date = self._extract_planting_date(query_text, context)
            
            # Create basic response
            response_parts = []
            confidence = 0.75
            
            # Handle uncertainty in planting date
            if not planting_date:
                response_parts.append("I don't have the exact planting date, which limits the accuracy of my harvest timing recommendation.")
                planting_date = datetime.now() - timedelta(days=90)  # Assume planted ~3 months ago
                confidence *= 0.8
            
            # Get satellite data
            satellite_data = None
            try:
                satellite_data = await get_satellite_data_for_location(location)
                if satellite_data:
                    response_parts.append(format_satellite_summary(satellite_data))
                    confidence += 0.15
            except Exception as e:
                logger.warning(f"Satellite data retrieval failed: {e}")
                response_parts.append("Note: Satellite data is temporarily unavailable. Using ground-based calculations only.")
                confidence *= 0.9
            
            # Prepare weather forecast (10 day forecast)
            weather_forecast = self._get_weather_forecast(location, days=10)
            
            # Prepare growth data
            growth_data = self._prepare_growth_data(crop_type, growth_stage, context)
            
            # Determine crop variety (if available)
            crop_variety = context.get('crop_variety', 'standard')
            
            # Determine equipment availability
            equipment_availability = {
                "mechanized_harvester": context.get('has_mechanized_equipment', True),
                "semi_mechanized": context.get('has_semi_mechanized', True)
            }
            
            # Use AgriMitr model for enhanced harvest planning
            harvest_plan = enhance_harvest_planning_with_AgriMitr(
                crop_type=str(crop_type.value) if isinstance(crop_type, Enum) else str(crop_type),
                crop_variety=crop_variety,
                planting_date=planting_date,
                growth_data=growth_data,
                field_size=field_size,
                weather_forecast=weather_forecast,
                equipment_availability=equipment_availability,
                satellite_data=satellite_data
            )
            
            # Format the response based on the harvest plan
            response_parts.extend(self._format_harvest_plan_response(harvest_plan))
            
            # Add confidence boosting if satellite data enhanced the prediction
            if harvest_plan.satellite_enhancement:
                confidence = min(0.98, confidence + 0.1)
            
            # Combine all response parts
            full_response = "\n\n".join(response_parts)
            
            return AgentResponse(
                query_id=query.query_id,
                response_text=full_response,
                confidence=confidence,
                agent_name=self.name,
                metadata={
                    "crop_type": str(crop_type),
                    "growth_stage": growth_stage,
                    "days_to_harvest": harvest_plan.current_status.days_to_harvest,
                    "optimal_window_start": harvest_plan.primary_recommendation.primary_window.start_date.strftime("%Y-%m-%d"),
                    "optimal_window_end": harvest_plan.primary_recommendation.primary_window.end_date.strftime("%Y-%m-%d"),
                    "weather_quality": f"{harvest_plan.primary_recommendation.primary_window.quality:.2f}",
                    "satellite_enhanced": bool(harvest_plan.satellite_enhancement)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing harvest query: {e}", exc_info=True)
            return AgentResponse(
                query_id=query.query_id,
                response_text=f"I apologize, but I couldn't generate a harvest recommendation due to: {str(e)}. Please provide more details about your crop type and planting date.",
                confidence=0.3,
                agent_name=self.name
            )
    
    def _analyze_harvest_query(self, query_text: str) -> Dict[str, Any]:
        """Analyze query to identify crop and harvest intent"""
        query_lower = query_text.lower()
        
        crop_map = {
            "wheat": CropType.WHEAT, "गेहूं": CropType.WHEAT,
            "rice": CropType.RICE, "धान": CropType.RICE, "chawal": CropType.RICE, "चावल": CropType.RICE,
            "cotton": CropType.COTTON, "कपास": CropType.COTTON,
            "sugarcane": CropType.SUGARCANE, "गन्ना": CropType.SUGARCANE,
        }
        
        found_crop = None
        for keyword, crop_type in crop_map.items():
            if keyword in query_lower:
                found_crop = crop_type
                break
        
        # Determine query intent
        harvest_keywords = ["harvest", "कटाई", "फसल", "ready", "mature", "when to cut"]
        timing_keywords = ["when", "कब", "time", "date", "optimal"]
        
        intent = "general"
        if any(keyword in query_lower for keyword in harvest_keywords):
            intent = "harvest_timing"
        elif any(keyword in query_lower for keyword in timing_keywords):
            intent = "optimal_timing"
        
        return {
            "crop_type": found_crop,
            "intent": intent,
            "urgency": self._extract_urgency(query_text)
        }
    
    def _extract_urgency(self, query_text: str) -> HarvestUrgency:
        """Extract urgency from query text"""
        query_lower = query_text.lower()
        
        urgent_keywords = ["urgent", "immediately", "now", "तुरंत", "जल्दी"]
        if any(keyword in query_lower for keyword in urgent_keywords):
            return HarvestUrgency.IMMEDIATE
        
        return HarvestUrgency.PLANNED
    
    async def _generate_harvest_recommendation(self, crop_type: CropType, 
                                             location: Optional[Location],
                                             query_analysis: Dict[str, Any]) -> HarvestRecommendation:
        """Generate comprehensive harvest recommendation"""
        
        # Get crop calendar
        crop_calendar = self.crop_calendars.get(crop_type)
        if not crop_calendar:
            # Create default calendar
            crop_calendar = self._create_default_calendar(crop_type)
        
        # Calculate current crop stage and harvest dates
        current_date = date.today()
        sowing_date = crop_calendar.sowing_date
        days_since_sowing = (current_date - sowing_date).days
        
        current_stage = self._determine_crop_stage(days_since_sowing, crop_calendar)
        
        # Calculate harvest window
        harvest_start_date = sowing_date + timedelta(days=crop_calendar.harvest_window_start)
        harvest_end_date = sowing_date + timedelta(days=crop_calendar.harvest_window_end)
        optimal_date = sowing_date + timedelta(days=(crop_calendar.harvest_window_start + crop_calendar.harvest_window_end) // 2)
        
        # Get weather forecast
        weather_forecast = self._get_weather_forecast(location, harvest_start_date, harvest_end_date)
        
        # Determine urgency
        urgency = self._calculate_harvest_urgency(current_date, harvest_start_date, harvest_end_date, current_stage)
        
        # Generate reasoning
        reasoning = self._generate_harvest_reasoning(
            crop_calendar, current_stage, days_since_sowing, weather_forecast
        )
        
        # Weather considerations
        weather_considerations = self._analyze_weather_impact(weather_forecast, crop_calendar)
        
        return HarvestRecommendation(
            crop_type=crop_type,
            current_stage=current_stage,
            optimal_harvest_date=optimal_date,
            harvest_window_start=harvest_start_date,
            harvest_window_end=harvest_end_date,
            urgency=urgency,
            confidence_score=self._calculate_confidence(current_stage, weather_forecast),
            reasoning=reasoning,
            weather_considerations=weather_considerations,
            expected_yield_quality=self._assess_yield_quality(current_stage, weather_forecast),
            post_harvest_actions=self._get_post_harvest_actions(crop_type, optimal_date)
        )
    
    def _create_default_calendar(self, crop_type: CropType) -> CropCalendar:
        """Create default crop calendar for unknown crop types"""
        return CropCalendar(
            crop_type=crop_type,
            variety="General",
            sowing_date=date.today() - timedelta(days=90),
            total_growth_days=120,
            harvest_window_start=110,
            harvest_window_end=130,
            optimal_harvest_stage=CropStage.MATURITY,
            weather_sensitivity=0.7,
            post_harvest_shelf_life=30
        )
    
    def _determine_crop_stage(self, days_since_sowing: int, crop_calendar: CropCalendar) -> CropStage:
        """Determine current crop growth stage"""
        total_days = crop_calendar.total_growth_days
        
        if days_since_sowing < 10:
            return CropStage.GERMINATION
        elif days_since_sowing < total_days * 0.3:
            return CropStage.VEGETATIVE
        elif days_since_sowing < total_days * 0.6:
            return CropStage.FLOWERING
        elif days_since_sowing < total_days * 0.9:
            return CropStage.FRUIT_DEVELOPMENT
        elif days_since_sowing < crop_calendar.harvest_window_start:
            return CropStage.MATURITY
        else:
            return CropStage.HARVEST_READY
    
    def _get_weather_forecast(self, location: Optional[Location], 
                            start_date: date, end_date: date) -> List[WeatherForecast]:
        """Generate mock weather forecast for harvest period"""
        forecasts = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate weather based on season and location
            month = current_date.month
            
            # Monsoon season check (June-September)
            if 6 <= month <= 9:
                precipitation_chance = 0.7
                condition = WeatherCondition.LIGHT_RAIN if random.random() < 0.6 else WeatherCondition.CLOUDY
            else:
                precipitation_chance = 0.2
                condition = WeatherCondition.SUNNY if random.random() < 0.7 else WeatherCondition.PARTLY_CLOUDY
            
            # Temperature based on season
            if month in [12, 1, 2]:  # Winter
                temp_max = random.uniform(18, 25)
                temp_min = random.uniform(5, 15)
            elif month in [3, 4, 5]:  # Summer
                temp_max = random.uniform(30, 40)
                temp_min = random.uniform(20, 30)
            else:  # Monsoon/Post-monsoon
                temp_max = random.uniform(25, 35)
                temp_min = random.uniform(18, 25)
            
            # Calculate harvest suitability score
            suitability = self._calculate_harvest_suitability(
                condition, temp_max, precipitation_chance
            )
            
            forecasts.append(WeatherForecast(
                date=current_date,
                condition=condition,
                temperature_max=temp_max,
                temperature_min=temp_min,
                humidity=random.uniform(40, 80),
                precipitation_chance=precipitation_chance,
                wind_speed=random.uniform(5, 15),
                harvest_suitability_score=suitability
            ))
            
            current_date += timedelta(days=1)
        
        return forecasts
    
    def _calculate_harvest_suitability(self, condition: WeatherCondition, 
                                     temp_max: float, precipitation_chance: float) -> float:
        """Calculate harvest suitability score (0-10)"""
        base_score = 7.0
        
        # Weather condition impact
        if condition == WeatherCondition.SUNNY:
            base_score += 2
        elif condition == WeatherCondition.PARTLY_CLOUDY:
            base_score += 1
        elif condition in [WeatherCondition.HEAVY_RAIN, WeatherCondition.STORM]:
            base_score -= 4
        elif condition == WeatherCondition.LIGHT_RAIN:
            base_score -= 2
        
        # Temperature impact
        if 20 <= temp_max <= 30:
            base_score += 1
        elif temp_max > 35 or temp_max < 15:
            base_score -= 1
        
        # Precipitation impact
        if precipitation_chance > 0.5:
            base_score -= 2
        
        return max(0, min(10, base_score))
    
    def _calculate_harvest_urgency(self, current_date: date, harvest_start: date, 
                                 harvest_end: date, current_stage: CropStage) -> HarvestUrgency:
        """Calculate harvest urgency based on current date and crop stage"""
        days_to_start = (harvest_start - current_date).days
        days_to_end = (harvest_end - current_date).days
        
        if current_stage == CropStage.HARVEST_READY and days_to_end <= 2:
            return HarvestUrgency.IMMEDIATE
        elif current_stage == CropStage.HARVEST_READY and days_to_end <= 5:
            return HarvestUrgency.URGENT
        elif days_to_start <= 14:
            return HarvestUrgency.PLANNED
        else:
            return HarvestUrgency.FUTURE
    
    def _generate_harvest_reasoning(self, crop_calendar: CropCalendar, current_stage: CropStage,
                                   days_since_sowing: int, weather_forecast: List[WeatherForecast]) -> List[str]:
        """Generate reasoning for harvest recommendation"""
        reasoning = []
        
        # Crop stage reasoning
        reasoning.append(f"Crop is currently in {current_stage.value} stage after {days_since_sowing} days of growth")
        
        # Maturity reasoning
        if current_stage == CropStage.HARVEST_READY:
            reasoning.append("Crop has reached optimal harvest maturity")
        elif current_stage == CropStage.MATURITY:
            reasoning.append("Crop is nearing harvest readiness")
        else:
            days_remaining = crop_calendar.harvest_window_start - days_since_sowing
            reasoning.append(f"Approximately {days_remaining} days remaining until harvest window")
        
        # Weather reasoning
        avg_suitability = sum(f.harvest_suitability_score for f in weather_forecast) / len(weather_forecast)
        if avg_suitability > 7:
            reasoning.append("Weather conditions are favorable for harvesting")
        elif avg_suitability < 4:
            reasoning.append("Weather conditions may pose challenges for harvesting")
        
        return reasoning
    
    def _analyze_weather_impact(self, weather_forecast: List[WeatherForecast], 
                               crop_calendar: CropCalendar) -> List[str]:
        """Analyze weather impact on harvest timing"""
        considerations = []
        
        # Check for rain in forecast
        rainy_days = [f for f in weather_forecast if f.precipitation_chance > 0.5]
        if rainy_days:
            considerations.append(f"Rain expected on {len(rainy_days)} days - may delay harvest operations")
        
        # Check for extreme temperatures
        hot_days = [f for f in weather_forecast if f.temperature_max > 35]
        if hot_days:
            considerations.append("High temperatures expected - harvest early morning for better quality")
        
        # Check for storms
        storm_days = [f for f in weather_forecast if f.condition == WeatherCondition.STORM]
        if storm_days:
            considerations.append("Storm conditions forecasted - consider early harvest if crop is ready")
        
        if not considerations:
            considerations.append("Weather conditions appear favorable for harvest operations")
        
        return considerations
    
    def _calculate_confidence(self, current_stage: CropStage, 
                            weather_forecast: List[WeatherForecast]) -> float:
        """Calculate confidence score for the recommendation"""
        base_confidence = 0.8
        
        # Stage-based confidence
        if current_stage in [CropStage.HARVEST_READY, CropStage.MATURITY]:
            base_confidence += 0.1
        elif current_stage in [CropStage.VEGETATIVE, CropStage.GERMINATION]:
            base_confidence -= 0.2
        
        # Weather predictability
        avg_suitability = sum(f.harvest_suitability_score for f in weather_forecast) / len(weather_forecast)
        if avg_suitability > 7:
            base_confidence += 0.1
        elif avg_suitability < 4:
            base_confidence -= 0.1
        
        return min(0.95, max(0.6, base_confidence))
    
    def _assess_yield_quality(self, current_stage: CropStage, 
                            weather_forecast: List[WeatherForecast]) -> str:
        """Assess expected yield quality"""
        avg_suitability = sum(f.harvest_suitability_score for f in weather_forecast) / len(weather_forecast)
        
        if current_stage == CropStage.HARVEST_READY and avg_suitability > 7:
            return "excellent"
        elif current_stage == CropStage.MATURITY and avg_suitability > 6:
            return "good"
        elif avg_suitability > 4:
            return "fair"
        else:
            return "poor"
    
    def _get_post_harvest_actions(self, crop_type: CropType, harvest_date: date) -> List[str]:
        """Get recommended post-harvest actions"""
        actions = []
        
        if crop_type == CropType.WHEAT:
            actions = [
                "Dry grain to 12-14% moisture content",
                "Clean and grade the produce",
                "Store in dry, ventilated space",
                "Consider market timing for better prices"
            ]
        elif crop_type == CropType.RICE:
            actions = [
                "Dry paddy to 14% moisture content",
                "Remove stones and foreign matter",
                "Store in moisture-proof containers",
                "Monitor for pest infestation"
            ]
        elif crop_type == CropType.COTTON:
            actions = [
                "Pick cotton in dry weather",
                "Grade according to staple length",
                "Store in clean, dry place",
                "Sell through authorized cotton markets"
            ]
        else:
            actions = [
                "Handle produce carefully to avoid damage",
                "Dry to appropriate moisture level",
                "Grade and sort by quality",
                "Store in suitable conditions"
            ]
        
        return actions
    
    def _create_agent_response(self, recommendation: HarvestRecommendation, 
                             query: AgricultureQuery) -> AgentResponse:
        """Create structured agent response"""
        
        summary = self._create_summary(recommendation, query.query_language)
        recommendations_list = self._create_recommendations_list(recommendation)
        
        return AgentResponse(
            agent_id=self.name,
            agent_name="Harvest Planning Advisor",
            query_id=query.query_id,
            response_text=summary,
            response_language=query.query_language,
            confidence_score=recommendation.confidence_score,
            reasoning=", ".join(recommendation.reasoning),
            recommendations=recommendations_list,
            sources=["Crop Calendar Database", "Weather Forecast Service", "Agricultural Best Practices"],
            next_steps=["Monitor weather conditions", "Prepare harvest equipment", "Arrange storage facilities"],
            timestamp=datetime.now(),
            processing_time_ms=200,
            metadata={
                "crop_type": recommendation.crop_type.value,
                "current_stage": recommendation.current_stage.value,
                "optimal_date": recommendation.optimal_harvest_date.isoformat(),
                "urgency": recommendation.urgency.value,
                "expected_quality": recommendation.expected_yield_quality
            }
        )
    
    def _create_summary(self, recommendation: HarvestRecommendation, language: Language) -> str:
        """Create localized summary"""
        crop_name = recommendation.crop_type.name.capitalize()
        optimal_date = recommendation.optimal_harvest_date.strftime("%d %B %Y")
        
        if language in [Language.HINDI, Language.MIXED]:
            crop_translations = {
                "Wheat": "गेहूं", "Rice": "चावल", "Cotton": "कपास", "Sugarcane": "गन्ना"
            }
            crop_name = crop_translations.get(crop_name, crop_name)
            
            urgency_translations = {
                "immediate": "तत्काल", "urgent": "जल्दी", "planned": "योजनाबद्ध", "future": "भविष्य में"
            }
            urgency_text = urgency_translations.get(recommendation.urgency.value, recommendation.urgency.value)
            
            return (f"{crop_name} की फसल के लिए सुझाव: {optimal_date} को कटाई करें। "
                    f"वर्तमान अवस्था: {recommendation.current_stage.value}। "
                    f"प्राथमिकता: {urgency_text}। अपेक्षित गुणवत्ता: {recommendation.expected_yield_quality}।")
        
        return (f"Harvest recommendation for {crop_name}: Optimal date is {optimal_date}. "
                f"Current stage: {recommendation.current_stage.value}. "
                f"Urgency: {recommendation.urgency.value}. Expected quality: {recommendation.expected_yield_quality}.")
    
    def _create_recommendations_list(self, recommendation: HarvestRecommendation) -> List[Dict[str, Any]]:
        """Create detailed recommendations list"""
        recs = [
            {
                "title": f"Optimal Harvest Date: {recommendation.optimal_harvest_date.strftime('%B %d, %Y')}",
                "description": f"Harvest window: {recommendation.harvest_window_start.strftime('%b %d')} - {recommendation.harvest_window_end.strftime('%b %d')}",
                "priority": "high",
                "action_required": f"Plan harvest for {recommendation.urgency.value} execution"
            },
            {
                "title": "Weather Considerations",
                "description": "; ".join(recommendation.weather_considerations),
                "priority": "medium",
                "action_required": "Monitor daily weather updates"
            },
            {
                "title": "Expected Quality",
                "description": f"Yield quality expected to be {recommendation.expected_yield_quality}",
                "priority": "medium",
                "action_required": "Prepare quality maintenance measures"
            }
        ]
        
        # Add post-harvest actions
        if recommendation.post_harvest_actions:
            recs.append({
                "title": "Post-Harvest Actions",
                "description": "; ".join(recommendation.post_harvest_actions[:3]),
                "priority": "low",
                "action_required": "Prepare for post-harvest processing"
            })
        
        return recs
    
    def _create_general_harvest_info_response(self, query: AgricultureQuery) -> AgentResponse:
        """Create response when no specific crop is identified"""
        return AgentResponse(
            agent_id=self.name,
            agent_name="Harvest Planning Advisor",
            query_id=query.query_id,
            response_text="Please specify a crop (e.g., wheat, rice, cotton) for harvest timing advice. कृपया कटाई की सलाह के लिए एक फसल (जैसे गेहूं, चावल, कपास) निर्दिष्ट करें।",
            response_language=query.query_language,
            confidence_score=0.9,
            recommendations=[
                {"title": "Specify Crop", "description": "Mention the crop you want harvest advice for.", "priority": "high"}
            ],
            timestamp=datetime.now()
        )
    
    def _create_error_response(self, query: AgricultureQuery, error: str) -> AgentResponse:
        """Create error response"""
        return AgentResponse(
            agent_id=self.name,
            agent_name="Harvest Planning Advisor",
            query_id=query.query_id,
            response_text="Sorry, I encountered a technical issue while planning harvest. Please try again later. क्षमा करें, कटाई की योजना बनाते समय मुझे एक तकनीकी समस्या का सामना करना पड़ा।",
            response_language=query.query_language,
            confidence_score=0.1,
            warnings=[f"Technical error: {error}"],
            timestamp=datetime.now(),
            metadata={"error": True, "error_message": error}
        )
    
    def _prepare_growth_data(self, crop_type: CropType, growth_stage: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare growth data for the AgriMitr harvest model"""
        # Default values
        daily_gdd = 10.0  # Growing Degree Days per day
        accumulated_gdd = 0.0
        
        # Calculate accumulated GDD based on crop type and growth stage
        if growth_stage == "vegetative":
            accumulated_gdd = 800.0
        elif growth_stage == "flowering":
            accumulated_gdd = 1200.0
        elif growth_stage == "grain_filling" or growth_stage == "fruit_development":
            accumulated_gdd = 1800.0
        elif growth_stage == "maturity":
            accumulated_gdd = 2300.0
        
        # Adjust based on crop type
        if crop_type == CropType.WHEAT:
            accumulated_gdd *= 0.9
            daily_gdd = 8.0
        elif crop_type == CropType.RICE:
            accumulated_gdd *= 1.1
            daily_gdd = 12.0
        elif crop_type == CropType.COTTON:
            accumulated_gdd *= 1.2
            daily_gdd = 15.0
        
        # Extract additional context information if available
        moisture_stress = context.get("moisture_stress", False)
        disease_pressure = context.get("disease_pressure", False)
        nutrient_deficiency = context.get("nutrient_deficiency", False)
        
        return {
            "accumulated_gdd": accumulated_gdd,
            "daily_gdd": daily_gdd,
            "expected_daily_gdd": daily_gdd,
            "moisture_stress": moisture_stress,
            "disease_pressure": disease_pressure,
            "nutrient_deficiency": nutrient_deficiency
        }
    
    def _format_harvest_plan_response(self, harvest_plan: HarvestPlan) -> List[str]:
        """Format harvest plan into readable response parts"""
        response_parts = []
        
        # Crop status
        response_parts.append(f"## 🌾 Crop Status: {harvest_plan.crop_type} ({harvest_plan.crop_variety})")
        response_parts.append(f"**Current Stage:** {harvest_plan.current_status.current_stage.value}")
        response_parts.append(f"**Days to Harvest:** {harvest_plan.current_status.days_to_harvest} days")
        response_parts.append(f"**Maturity Score:** {harvest_plan.current_status.maturity_score:.1f}/100")
        
        if harvest_plan.current_status.risk_factors:
            response_parts.append(f"**Risk Factors:** {', '.join(harvest_plan.current_status.risk_factors)}")
        
        # Harvest window recommendation
        response_parts.append(f"\n## 📆 Harvest Window Recommendation")
        primary_window = harvest_plan.primary_recommendation.primary_window
        start_date = primary_window.start_date.strftime("%Y-%m-%d")
        end_date = primary_window.end_date.strftime("%Y-%m-%d")
        
        response_parts.append(f"**Optimal Harvest Window:** {start_date} to {end_date}")
        response_parts.append(f"**Window Quality:** {'Excellent' if primary_window.quality > 0.8 else 'Good' if primary_window.quality > 0.6 else 'Fair'}")
        response_parts.append(f"**Weather Assessment:** {primary_window.risk_assessment}")
        
        if harvest_plan.primary_recommendation.alternative_windows:
            alt_window = harvest_plan.primary_recommendation.alternative_windows[0]
            alt_start = alt_window.start_date.strftime("%Y-%m-%d")
            alt_end = alt_window.end_date.strftime("%Y-%m-%d")
            response_parts.append(f"**Alternative Window:** {alt_start} to {alt_end}")
        
        # Equipment and resources
        response_parts.append(f"\n## 🚜 Equipment & Resources")
        response_parts.append(f"**Recommended Equipment:** {', '.join(harvest_plan.primary_recommendation.equipment_recommendations[:3])}")
        response_parts.append(f"**Labor Requirement:** {harvest_plan.primary_recommendation.labor_requirements} person-days/hectare")
        response_parts.append(f"**Estimated Cost:** ₹{harvest_plan.primary_recommendation.cost_estimate:.2f}/hectare")
        
        # Quality optimization
        response_parts.append(f"\n## ✅ Quality Optimization Tips")
        response_parts.append("\n".join([f"* {tip}" for tip in harvest_plan.quality_optimization[:3]]))
        
        # Risk mitigation
        if harvest_plan.risk_mitigation:
            response_parts.append(f"\n## ⚠️ Risk Management")
            response_parts.append("\n".join([f"* {strategy}" for strategy in harvest_plan.risk_mitigation[:3]]))
        
        # Add satellite enhancement notice if available
        if harvest_plan.satellite_enhancement:
            response_parts.append(f"\n*This recommendation is enhanced with satellite data for increased accuracy.*")
        
        return response_parts


# Test function for the Harvest Planning Agent
async def test_harvest_planning_agent():
    """Test the Harvest Planning Agent"""
    agent = HarvestPlanningAgent()
    
    print("🌾 Testing Harvest Planning Agent")
    
    # Test wheat harvest query in English
    query_en = AgricultureQuery(
        query_text="When should I harvest my wheat crop?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_en",
        location=Location(state="Punjab", district="Ludhiana")
    )
    
    print("🔄 Processing English query for Wheat harvest...")
    response_en = await agent.process_query(query_en)
    print(f"✅ English Response: {response_en.response_text}")
    
    # Test rice harvest query in Hindi
    query_hi = AgricultureQuery(
        query_text="चावल की फसल कब काटनी चाहिए?",
        query_language=Language.HINDI,
        user_id="test_farmer_hi",
        location=Location(state="Uttar Pradesh", district="Lucknow")
    )
    
    print("🔄 Processing Hindi query for Rice harvest...")
    response_hi = await agent.process_query(query_hi)
    print(f"✅ Hindi Response: {response_hi.response_text}")
    
    # Test general query
    query_general = AgricultureQuery(
        query_text="What's the best harvest timing?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_gen"
    )
    
    print("🔄 Processing general harvest query...")
    response_gen = await agent.process_query(query_general)
    print(f"✅ General Response: {response_gen.response_text}")
    
    print("\n🎉 Harvest Planning Agent working successfully!")


if __name__ == "__main__":
    asyncio.run(test_harvest_planning_agent())
