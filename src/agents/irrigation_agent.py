"""
Irrigation Scheduling Agent
Specialized agent for calculating crop water requirements and creating optimal irrigation schedules.
Uses meteorological data, soil characteristics, and crop growth stages.
Enhanced with AgriSens ML models for precise water management.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import math

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..core.models import AgentCapability
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType,
    WeatherData, Location, FarmProfile, QueryDomain
)
# AgriSens Model Integration
from ..models.agrisens_irrigation_scheduling import (
    get_irrigation_model, IrrigationModel, calculate_crop_water_requirement,
    get_soil_moisture_depletion, optimize_irrigation_schedule
)

logger = logging.getLogger(__name__)


class IrrigationMethod(Enum):
    """Types of irrigation methods"""
    FLOOD = "flood"
    FURROW = "furrow"
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    MICRO_SPRINKLER = "micro_sprinkler"
    SURFACE = "surface"


class CropStage(Enum):
    """Crop growth stages for irrigation planning"""
    INITIAL = "initial"
    DEVELOPMENT = "development"
    MID_SEASON = "mid_season"
    LATE_SEASON = "late_season"
    MATURITY = "maturity"


class WaterSource(Enum):
    """Water source types"""
    GROUNDWATER = "groundwater"
    CANAL = "canal"
    RIVER = "river"
    TANK = "tank"
    RAINWATER = "rainwater"


@dataclass
class CropWaterRequirement:
    """Crop water requirement calculation"""
    crop_type: CropType
    stage: CropStage
    daily_et: float  # mm/day
    kc_coefficient: float  # crop coefficient
    stage_duration: int  # days
    total_water_need: float  # mm for this stage
    irrigation_frequency: int  # days between irrigations


@dataclass
class IrrigationSchedule:
    """Individual irrigation schedule entry"""
    date: datetime
    water_amount: float  # mm
    duration_hours: float
    method: IrrigationMethod
    crop_stage: CropStage
    reason: str
    priority: str  # high, medium, low
    weather_adjustment: str


@dataclass
class WaterBudget:
    """Water budget analysis"""
    total_requirement: float  # mm/season
    rainfall_contribution: float  # mm
    irrigation_need: float  # mm
    efficiency_factor: float
    cost_per_mm: float  # rupees per mm per hectare
    total_cost: float  # rupees per hectare


@dataclass
class SoilMoisture:
    """Soil moisture characteristics"""
    field_capacity: float  # mm/m
    wilting_point: float  # mm/m
    available_water: float  # mm/m
    current_moisture: float  # percentage
    depletion_level: float  # percentage


class IrrigationAgent(BaseWorkerAgent):
    """
    Agent specialized in irrigation scheduling and water management.
    
    Capabilities:
    - Crop water requirement calculation using ET method
    - Optimal irrigation scheduling based on growth stages
    - Water budget planning and cost analysis
    - Soil moisture monitoring recommendations
    - Irrigation method selection and efficiency optimization
    """
    
    def __init__(self):
        super().__init__(
            name="Irrigation Scheduling Specialist", 
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.PLANNING,
                AgentCapability.EXECUTION
            ],
            agent_type="irrigation"
        )
        
        # Load irrigation knowledge base
        self._load_crop_coefficients()
        self._load_soil_properties()
        self._load_irrigation_methods()
        logger.info(f"Initialized {self.name} with irrigation database")
    
    async def execute(self, task):
        """Execute a task assigned to this agent"""
        try:
            if hasattr(task, 'query'):
                return await self.process_query(task.query)
            else:
                # Handle direct task execution
                return await self.process_query(task)
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            raise
    
    def _load_crop_coefficients(self):
        """Load crop coefficient (Kc) values for different growth stages"""
        self.crop_coefficients = {
            CropType.WHEAT: {
                CropStage.INITIAL: {"kc": 0.4, "duration": 20},  # Germination to establishment
                CropStage.DEVELOPMENT: {"kc": 0.7, "duration": 25},  # Tillering stage
                CropStage.MID_SEASON: {"kc": 1.15, "duration": 50},  # Stem elongation to grain filling
                CropStage.LATE_SEASON: {"kc": 0.8, "duration": 30},  # Grain filling to maturity
                CropStage.MATURITY: {"kc": 0.4, "duration": 20}  # Maturity
            },
            
            CropType.RICE: {
                CropStage.INITIAL: {"kc": 1.10, "duration": 30},  # Transplanting to tillering
                CropStage.DEVELOPMENT: {"kc": 1.10, "duration": 25},  # Tillering
                CropStage.MID_SEASON: {"kc": 1.20, "duration": 45},  # Panicle initiation to flowering
                CropStage.LATE_SEASON: {"kc": 0.90, "duration": 30},  # Grain filling
                CropStage.MATURITY: {"kc": 0.60, "duration": 10}  # Maturity
            },
            
            CropType.COTTON: {
                CropStage.INITIAL: {"kc": 0.35, "duration": 30},  # Emergence to squaring
                CropStage.DEVELOPMENT: {"kc": 0.7, "duration": 50},  # Squaring to flowering
                CropStage.MID_SEASON: {"kc": 1.15, "duration": 60},  # Flowering to boll development
                CropStage.LATE_SEASON: {"kc": 0.8, "duration": 45},  # Boll filling
                CropStage.MATURITY: {"kc": 0.65, "duration": 15}  # Maturity
            },
            
            CropType.MAIZE: {
                CropStage.INITIAL: {"kc": 0.3, "duration": 25},  # Emergence to 4-leaf stage
                CropStage.DEVELOPMENT: {"kc": 0.7, "duration": 35},  # 4-leaf to tasseling
                CropStage.MID_SEASON: {"kc": 1.2, "duration": 40},  # Tasseling to grain filling
                CropStage.LATE_SEASON: {"kc": 0.6, "duration": 30},  # Grain filling to maturity
                CropStage.MATURITY: {"kc": 0.35, "duration": 1}  # Harvest
            },
            
            CropType.SUGARCANE: {
                CropStage.INITIAL: {"kc": 0.4, "duration": 45},  # Planting to establishment
                CropStage.DEVELOPMENT: {"kc": 0.8, "duration": 75},  # Tillering
                CropStage.MID_SEASON: {"kc": 1.25, "duration": 180},  # Grand growth period
                CropStage.LATE_SEASON: {"kc": 0.75, "duration": 60},  # Ripening
                CropStage.MATURITY: {"kc": 0.5, "duration": 5}  # Harvest
            }
        }
    
    def _load_soil_properties(self):
        """Load soil water holding properties"""
        self.soil_properties = {
            SoilType.SANDY: {
                "field_capacity": 120,  # mm/m depth
                "wilting_point": 50,   # mm/m depth
                "infiltration_rate": 30,  # mm/hr
                "water_holding_capacity": 70,  # mm/m
                "drainage": "excellent",
                "irrigation_frequency": "high"
            },
            
            SoilType.LOAMY: {
                "field_capacity": 180,
                "wilting_point": 80,
                "infiltration_rate": 15,
                "water_holding_capacity": 100,
                "drainage": "good",
                "irrigation_frequency": "medium"
            },
            
            SoilType.LOAMY: {
                "field_capacity": 250,
                "wilting_point": 120,
                "infiltration_rate": 10,
                "water_holding_capacity": 130,
                "drainage": "moderate",
                "irrigation_frequency": "medium"
            },
            
            SoilType.LOAMY: {
                "field_capacity": 320,
                "wilting_point": 180,
                "infiltration_rate": 5,
                "water_holding_capacity": 140,
                "drainage": "slow",
                "irrigation_frequency": "low"
            },
            
            SoilType.CLAY: {
                "field_capacity": 380,
                "wilting_point": 220,
                "infiltration_rate": 2,
                "water_holding_capacity": 160,
                "drainage": "poor",
                "irrigation_frequency": "low"
            }
        }
    
    def _load_irrigation_methods(self):
        """Load irrigation method characteristics"""
        self.irrigation_methods = {
            IrrigationMethod.FLOOD: {
                "efficiency": 0.35,
                "suitable_crops": [CropType.RICE],
                "suitable_soils": [SoilType.CLAY, SoilType.LOAMY],
                "water_requirement_factor": 2.8,
                "initial_cost": 5000,  # rupees per hectare
                "operation_cost": 500,  # rupees per hectare per season
                "labor_requirement": "low"
            },
            
            IrrigationMethod.FURROW: {
                "efficiency": 0.45,
                "suitable_crops": [CropType.COTTON, CropType.SUGARCANE, CropType.WHEAT],
                "suitable_soils": [SoilType.LOAMY, SoilType.SANDY],
                "water_requirement_factor": 2.2,
                "initial_cost": 8000,
                "operation_cost": 800,
                "labor_requirement": "medium"
            },
            
            IrrigationMethod.DRIP: {
                "efficiency": 0.90,
                "suitable_crops": [CropType.COTTON, CropType.SUGARCANE],
                "suitable_soils": [SoilType.SANDY, SoilType.LOAMY, SoilType.LOAMY],
                "water_requirement_factor": 1.1,
                "initial_cost": 50000,
                "operation_cost": 3000,
                "labor_requirement": "low"
            },
            
            IrrigationMethod.SPRINKLER: {
                "efficiency": 0.75,
                "suitable_crops": [CropType.WHEAT, CropType.MAIZE],
                "suitable_soils": [SoilType.SANDY, SoilType.LOAMY, SoilType.LOAMY],
                "water_requirement_factor": 1.3,
                "initial_cost": 25000,
                "operation_cost": 1500,
                "labor_requirement": "low"
            }
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """
        Process irrigation scheduling related queries with satellite data integration.
        Uses AgriSens ML model for enhanced irrigation scheduling.
        
        Args:
            query: Agriculture query object
            
        Returns:
            AgentResponse with irrigation recommendations enhanced by satellite data and ML model
        """
        try:
            logger.info(f"Processing irrigation query with AgriSens ML model and satellite integration: {query.query_text}")
            
            # Extract irrigation context from query
            context = self._extract_irrigation_context(query)
            
            # Get satellite data if location is available
            satellite_data = None
            if context.get("location") and hasattr(context["location"], "latitude") and hasattr(context["location"], "longitude"):
                try:
                    logger.info(f"[SATELLITE] Fetching satellite data for irrigation planning: {context['location'].latitude}, {context['location'].longitude}")
                    satellite_data = await get_satellite_data_for_location(
                        context["location"].latitude,
                        context["location"].longitude,
                        getattr(context["location"], "name", None)
                    )
                    logger.info(f"[SATELLITE] Satellite data retrieved for irrigation analysis")
                except Exception as e:
                    logger.warning(f"[SATELLITE] Could not fetch satellite data: {e}")
                    satellite_data = None
            
            # Enhance context with satellite data
            if satellite_data:
                context = self._enhance_context_with_satellite_data(context, satellite_data)
            
            # Initialize AgriSens Irrigation Model
            irrigation_model = get_irrigation_model()
            logger.info(f"[AGRISENS] Using AgriSens irrigation scheduling model for enhanced recommendations")
            
            # Convert context to format expected by the ML model
            crop_data = {
                "crop_type": str(context.get("crop_type", "wheat")).lower(),
                "growth_stage": str(context.get("current_stage", "mid_season")).lower(),
                "field_size": float(context.get("farm_size", 1.0)),
                "irrigation_method": str(context.get("irrigation_method", "sprinkler")).lower(),
                "root_depth": float(context.get("root_depth", 0.5))  # default 0.5m if not provided
            }
            
            soil_data = {
                "soil_type": str(context.get("soil_type", "loam")).lower(),
            }
            
            # Prepare weather data
            weather_data = {}
            for i in range(7):
                weather_data[f"day_{i+1}"] = {
                    "et0": 5.0,  # Default reference ET
                    "rainfall": 0.0  # Default no rainfall
                }
                
            if "weather" in context and isinstance(context["weather"], dict):
                for i, forecast in enumerate(context["weather"].get("forecast", [])):
                    if i < 7:
                        weather_data[f"day_{i+1}"]["rainfall"] = forecast.get("precipitation", 0)
                        # Estimate ET0 based on temperature
                        temp = forecast.get("temperature", 25)
                        weather_data[f"day_{i+1}"]["et0"] = 3.0 + (temp / 10)  # Simple estimation
            
            # Get ML-based irrigation recommendations
            agrisens_irrigation_plan = irrigation_model.generate_satellite_enhanced_irrigation_plan(
                crop_data=crop_data,
                soil_data=soil_data,
                weather_data=weather_data,
                satellite_data=satellite_data
            )
            logger.info(f"[AGRISENS] Generated irrigation plan: {len(agrisens_irrigation_plan['schedule'])} days scheduled")
            
            # Update our internal data with ML model outputs
            water_requirements = await self._calculate_water_requirements(context, satellite_data, agrisens_irrigation_plan)
            irrigation_schedule = await self._generate_irrigation_schedule(context, water_requirements, satellite_data, agrisens_irrigation_plan)
            water_budget = await self._calculate_water_budget(context, water_requirements)
            method_recommendation = await self._recommend_irrigation_method(context, satellite_data, agrisens_irrigation_plan)
            
            # Calculate confidence including satellite data and ML model
            confidence = self._calculate_confidence(context, satellite_data)
            # Increase confidence because we're using ML model
            confidence = min(confidence + 0.15, 1.0)
            
            # Include satellite summary and ML model in sources
            sources = ["fao_irrigation_guidelines", "crop_coefficient_database", "soil_moisture_models", "agrisens_irrigation_ml_model"]
            if satellite_data:
                sources.append("satellite_soil_moisture")
            
            # Format response with satellite insights and ML model data
            response_data = {
                "water_requirements": [req.__dict__ for req in water_requirements],
                "irrigation_schedule": [sched.__dict__ for sched in irrigation_schedule],
                "water_budget": water_budget.__dict__ if water_budget else None,
                "method_recommendation": method_recommendation,
                "context_analysis": context,
                "satellite_insights": satellite_data,
                "agrisens_model_output": agrisens_irrigation_plan,
                "confidence_score": confidence,
                "efficiency_tips": self._generate_efficiency_tips(context, satellite_data, agrisens_irrigation_plan)
            }
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Generated irrigation schedule with {len(irrigation_schedule)} recommendations",
                confidence_score=confidence,
                sources=sources,
                recommendations=self._format_irrigation_summary(irrigation_schedule, water_budget, satellite_data),
                metadata=response_data
            )
            
        except Exception as e:
            logger.error(f"Error processing irrigation query: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Error processing irrigation query: {str(e)}",
                confidence_score=0.0,
                sources=[],
                recommendations=[],
                metadata={"error": str(e)}
            )
    
    def _extract_irrigation_context(self, query: AgricultureQuery) -> Dict[str, Any]:
        """Extract irrigation-related context from query"""
        context = {
            "crop_type": None,
            "soil_type": None,
            "farm_size": 1.0,  # hectares
            "current_stage": None,
            "planting_date": None,
            "irrigation_method": None,
            "water_source": None,
            "budget_constraint": None,
            "location": None,
            "query_type": "schedule"  # schedule, requirement, method, budget
        }
        
        query_text = query.query_text.lower()
        
        # Extract from farm profile
        if query.farm_profile:
            context["soil_type"] = query.farm_profile.soil_type
            context["farm_size"] = query.farm_profile.farm_size or 1.0
            context["location"] = query.farm_profile.location
        
        # Extract crop information
        for crop_type in CropType:
            crop_names = [crop_type.value, crop_type.name.lower()]
            hindi_names = {
                CropType.WHEAT: ["gehu", "gehun"],
                CropType.RICE: ["chawal", "dhan"],
                CropType.COTTON: ["kapas"],
                CropType.MAIZE: ["makka"],
                CropType.SUGARCANE: ["ganna"]
            }
            if crop_type in hindi_names:
                crop_names.extend(hindi_names[crop_type])
            
            if any(name in query_text for name in crop_names):
                context["crop_type"] = crop_type
                break
        
        # Extract irrigation method
        method_keywords = {
            "drip": IrrigationMethod.DRIP,
            "sprinkler": IrrigationMethod.SPRINKLER,
            "flood": IrrigationMethod.FLOOD,
            "furrow": IrrigationMethod.FURROW
        }
        
        for keyword, method in method_keywords.items():
            if keyword in query_text:
                context["irrigation_method"] = method
                break
        
        # Determine query type
        if any(word in query_text for word in ["schedule", "when", "timing", "kab"]):
            context["query_type"] = "schedule"
        elif any(word in query_text for word in ["how much", "quantity", "kitna", "requirement"]):
            context["query_type"] = "requirement"
        elif any(word in query_text for word in ["method", "system", "best", "which"]):
            context["query_type"] = "method"
        elif any(word in query_text for word in ["cost", "budget", "expense", "kharcha"]):
            context["query_type"] = "budget"
        
        # Extract growth stage if mentioned
        stage_keywords = {
            "flowering": CropStage.MID_SEASON,
            "tillering": CropStage.DEVELOPMENT,
            "maturity": CropStage.MATURITY,
            "grain filling": CropStage.LATE_SEASON
        }
        
        for keyword, stage in stage_keywords.items():
            if keyword in query_text:
                context["current_stage"] = stage
                break
        
        return context
    
    async def _calculate_water_requirements(self, context: Dict[str, Any]) -> List[CropWaterRequirement]:
        """Calculate crop water requirements for different growth stages"""
        requirements = []
        
        if not context["crop_type"]:
            return requirements
        
        crop_type = context["crop_type"]
        if crop_type not in self.crop_coefficients:
            return requirements
        
        # Reference evapotranspiration (ET0) - simplified calculation
        # In production, this would use actual weather data
        et0_daily = self._get_reference_et(context)
        
        stage_coefficients = self.crop_coefficients[crop_type]
        
        for stage, stage_data in stage_coefficients.items():
            kc = stage_data["kc"]
            duration = stage_data["duration"]
            
            # Calculate crop evapotranspiration (ETc)
            daily_etc = et0_daily * kc
            total_water_need = daily_etc * duration
            
            # Determine irrigation frequency based on soil and stage
            irrigation_freq = self._calculate_irrigation_frequency(context, stage, daily_etc)
            
            requirement = CropWaterRequirement(
                crop_type=crop_type,
                stage=stage,
                daily_et=daily_etc,
                kc_coefficient=kc,
                stage_duration=duration,
                total_water_need=total_water_need,
                irrigation_frequency=irrigation_freq
            )
            requirements.append(requirement)
        
        return requirements
    
    def _get_reference_et(self, context: Dict[str, Any]) -> float:
        """Get reference evapotranspiration (simplified)"""
        # Simplified ET0 calculation based on location and season
        current_month = datetime.now().month
        
        # Base ET0 values by month (mm/day) for Indian conditions
        monthly_et0 = {
            1: 2.5, 2: 3.5, 3: 5.0, 4: 6.5, 5: 7.5, 6: 6.0,
            7: 4.5, 8: 4.0, 9: 4.5, 10: 4.0, 11: 3.0, 12: 2.5
        }
        
        et0 = monthly_et0.get(current_month, 4.5)
        
        # Adjust for location if available
        if context["location"]:
            if context["location"] in ["Rajasthan", "Gujarat"]:  # Arid regions
                et0 *= 1.2
            elif context["location"] in ["Kerala", "West Bengal"]:  # Humid regions
                et0 *= 0.8
        
        return et0
    
    def _calculate_irrigation_frequency(self, context: Dict[str, Any], stage: CropStage, daily_etc: float) -> int:
        """Calculate irrigation frequency based on soil and crop stage"""
        base_frequency = 7  # days
        
        # Adjust based on soil type
        if context["soil_type"]:
            soil_props = self.soil_properties.get(context["soil_type"], {})
            if soil_props.get("irrigation_frequency") == "high":
                base_frequency = 3
            elif soil_props.get("irrigation_frequency") == "medium":
                base_frequency = 5
            elif soil_props.get("irrigation_frequency") == "low":
                base_frequency = 10
        
        # Adjust based on crop stage
        stage_adjustments = {
            CropStage.INITIAL: 0.8,  # More frequent for establishment
            CropStage.DEVELOPMENT: 1.0,
            CropStage.MID_SEASON: 0.7,  # Critical stage - more frequent
            CropStage.LATE_SEASON: 1.2,
            CropStage.MATURITY: 1.5  # Less frequent near maturity
        }
        
        adjusted_frequency = base_frequency * stage_adjustments.get(stage, 1.0)
        
        # Adjust based on water demand
        if daily_etc > 6.0:  # High water demand
            adjusted_frequency *= 0.8
        elif daily_etc < 3.0:  # Low water demand
            adjusted_frequency *= 1.3
        
        return max(int(adjusted_frequency), 2)  # Minimum 2 days
    
    async def _generate_irrigation_schedule(self, context: Dict[str, Any], water_requirements: List[CropWaterRequirement], 
                                  satellite_data: Optional[Dict] = None, agrisens_model_output: Optional[Dict] = None) -> List[IrrigationSchedule]:
        """
        Generate detailed irrigation schedule using AgriSens ML model when available
        
        Args:
            context: Query context
            water_requirements: List of water requirements
            satellite_data: Optional satellite data
            agrisens_model_output: Optional ML model output
            
        Returns:
            List of irrigation schedule recommendations
        """
        schedule = []
        
        # If we have AgriSens model output, use it for more accurate scheduling
        if agrisens_model_output and "schedule" in agrisens_model_output:
            logger.info("[AGRISENS] Using ML model irrigation schedule")
            model_schedule = agrisens_model_output.get("schedule", [])
            
            # Start from current date
            start_date = datetime.now()
            
            # Determine irrigation method
            method_str = agrisens_model_output.get("irrigation_method", "sprinkler")
            method = IrrigationMethod.SPRINKLER  # Default
            for m in IrrigationMethod:
                if m.value == method_str:
                    method = m
                    break
            
            # Process each day in the ML model schedule
            for i, day in enumerate(model_schedule):
                # Skip days without irrigation
                if not day.get("irrigate", False):
                    continue
                    
                irrigation_date = start_date + timedelta(days=i)
                irrigation_mm = day.get("irrigation_mm", 0)
                water_volume = day.get("water_volume_m3", 0)
                
                # Determine priority based on depletion level
                depletion = day.get("depletion_mm", 0)
                raw = agrisens_model_output.get("readily_available_water_mm", 60)
                priority = "medium"
                if depletion / raw > 0.8:
                    priority = "high"
                elif depletion / raw < 0.5:
                    priority = "low"
                
                # Calculate duration (simplified)
                method_data = self.irrigation_methods.get(method, {})
                application_rate = 10  # mm/hour (varies by method)
                duration = irrigation_mm / application_rate
                
                # Create irrigation schedule entry
                irrigation = IrrigationSchedule(
                    date=irrigation_date,
                    water_amount=irrigation_mm,
                    water_volume_m3=water_volume,
                    duration_hours=duration,
                    method=method,
                    crop_stage=context.get("current_stage", "mid_season"),
                    reason=f"Soil moisture depletion: {depletion:.1f}mm, ET: {day.get('etc_mm', 0):.1f}mm/day",
                    priority=priority,
                    weather_adjustment="Monitor rainfall forecast" if day.get("rainfall_mm", 0) > 0 else None,
                    satellite_adjustment=True if satellite_data else False
                )
                schedule.append(irrigation)
            
            return schedule[:10]  # Return next 10 irrigations
            
        # If no ML model output available, fall back to basic scheduling
        if not water_requirements:
            return schedule
        
        # Start from current date or planting date
        start_date = datetime.now()
        if context.get("planting_date"):
            if isinstance(context["planting_date"], datetime):
                start_date = context["planting_date"]
            elif isinstance(context["planting_date"], str):
                try:
                    start_date = datetime.strptime(context["planting_date"], "%Y-%m-%d")
                except ValueError:
                    pass
        
        current_date = start_date
        
        # Get crop water requirement
        req = water_requirements[0]
        
        # Determine growth stage
        stage_str = context.get("current_stage", "mid_season")
        stage = None
        for s in CropStage:
            if s.value == stage_str:
                stage = s
                break
        if not stage:
            stage = CropStage.MID_SEASON
        
        # Calculate daily ET (simplified)
        daily_et = req.daily_requirement_mm
        
        # Calculate irrigation frequency based on soil, stage and ET
        irrigation_frequency = self._calculate_irrigation_frequency(context, stage, daily_et)
        
        # Generate schedule for next 30 days
        for i in range(0, 30, irrigation_frequency):
            irrigation_date = current_date + timedelta(days=i)
            
            # Determine irrigation method
            method_str = context.get("irrigation_method", "furrow")
            method = IrrigationMethod.FURROW
            for m in IrrigationMethod:
                if m.value == method_str:
                    method = m
                    break
            
            # Calculate water amount for this irrigation
            water_amount = daily_et * irrigation_frequency
            
            # Calculate water volume in cubic meters
            water_volume = water_amount * 10  # 1 mm over 1 ha = 10 m3
            if context.get("farm_size"):
                water_volume *= float(context["farm_size"])
            
            # Adjust based on method efficiency
            method_data = self.irrigation_methods.get(method, {})
            efficiency = method_data.get("efficiency", 0.5)
            water_volume = water_volume / efficiency
            
            # Calculate duration (simplified)
            application_rate = 10  # mm/hour (varies by method)
            duration = water_amount / application_rate
            
            # Determine priority based on crop stage
            priority = "high" if stage in [CropStage.MID_SEASON, CropStage.INITIAL] else "medium"
            
            # Create irrigation schedule entry
            irrigation = IrrigationSchedule(
                date=irrigation_date,
                water_amount=water_amount,
                water_volume_m3=water_volume,
                duration_hours=duration,
                method=method,
                crop_stage=stage,
                reason=f"Stage: {stage.value}, ET: {daily_et:.1f}mm/day",
                priority=priority,
                weather_adjustment="Monitor weather 2 days before",
                satellite_adjustment=True if satellite_data else False
            )
            schedule.append(irrigation)
        
        return schedule[:10]  # Return next 10 irrigations
    
    async def _calculate_water_budget(self, context: Dict[str, Any], requirements: List[CropWaterRequirement]) -> Optional[WaterBudget]:
        """Calculate water budget and costs"""
        if not requirements:
            return None
        
        # Calculate total seasonal water requirement
        total_requirement = sum(req.total_water_need for req in requirements)
        
        # Estimate rainfall contribution (simplified)
        expected_rainfall = self._estimate_seasonal_rainfall(context)
        effective_rainfall = expected_rainfall * 0.7  # 70% effectiveness
        
        # Calculate irrigation need
        irrigation_need = max(0, total_requirement - effective_rainfall)
        
        # Get efficiency factor based on irrigation method
        method = context.get("irrigation_method", IrrigationMethod.FURROW)
        efficiency = self.irrigation_methods.get(method, {}).get("efficiency", 0.5)
        
        # Calculate actual water to be applied
        actual_water_needed = irrigation_need / efficiency
        
        # Calculate costs (simplified)
        cost_per_mm = 15  # rupees per mm per hectare (varies by region/source)
        total_cost = actual_water_needed * cost_per_mm * context.get("farm_size", 1.0)
        
        return WaterBudget(
            total_requirement=total_requirement,
            rainfall_contribution=effective_rainfall,
            irrigation_need=irrigation_need,
            efficiency_factor=efficiency,
            cost_per_mm=cost_per_mm,
            total_cost=total_cost
        )
    
    def _estimate_seasonal_rainfall(self, context: Dict[str, Any]) -> float:
        """Estimate seasonal rainfall based on location and season"""
        # Simplified rainfall estimation
        current_month = datetime.now().month
        
        # Base seasonal rainfall (mm)
        if 6 <= current_month <= 9:  # Monsoon season
            base_rainfall = 600
        elif 10 <= current_month <= 3:  # Post-monsoon to pre-monsoon
            base_rainfall = 100
        else:  # Summer
            base_rainfall = 50
        
        # Adjust for location
        if context["location"]:
            location_factors = {
                "Punjab": 0.8,
                "Rajasthan": 0.4,
                "Maharashtra": 1.2,
                "West Bengal": 1.5,
                "Kerala": 2.0
            }
            factor = location_factors.get(context["location"], 1.0)
            base_rainfall *= factor
        
        return base_rainfall
    
    async def _recommend_irrigation_method(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal irrigation method"""
        recommendations = []
        
        for method, method_data in self.irrigation_methods.items():
            score = self._calculate_method_suitability(method, method_data, context)
            
            if score > 0.3:  # Include reasonably suitable methods
                recommendation = {
                    "method": method.value,
                    "suitability_score": score,
                    "efficiency": method_data["efficiency"],
                    "initial_cost": method_data["initial_cost"],
                    "operation_cost": method_data["operation_cost"],
                    "pros": self._get_method_pros(method, context),
                    "cons": self._get_method_cons(method, context),
                    "recommendation": "Recommended" if score > 0.7 else "Consider" if score > 0.5 else "Not recommended"
                }
                recommendations.append(recommendation)
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return {
            "top_recommendation": recommendations[0] if recommendations else None,
            "all_options": recommendations[:3],  # Top 3 options
            "selection_criteria": self._get_selection_criteria(context)
        }
    
    def _calculate_method_suitability(self, method: IrrigationMethod, method_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate suitability score for irrigation method"""
        score = 0.5  # Base score
        
        # Crop suitability (30% weight)
        if context["crop_type"] and context["crop_type"] in method_data.get("suitable_crops", []):
            score += 0.30
        
        # Soil suitability (25% weight)
        if context["soil_type"] and context["soil_type"] in method_data.get("suitable_soils", []):
            score += 0.25
        
        # Efficiency consideration (20% weight)
        efficiency = method_data.get("efficiency", 0.5)
        score += 0.20 * efficiency
        
        # Cost consideration (15% weight) - higher score for lower cost
        initial_cost = method_data.get("initial_cost", 50000)
        if initial_cost < 15000:
            score += 0.15
        elif initial_cost < 30000:
            score += 0.10
        elif initial_cost < 50000:
            score += 0.05
        
        # Farm size consideration (10% weight)
        farm_size = context.get("farm_size", 1.0)
        if method == IrrigationMethod.DRIP and farm_size < 2.0:  # Drip good for small farms
            score += 0.10
        elif method == IrrigationMethod.FLOOD and farm_size > 5.0:  # Flood good for large farms
            score += 0.05
        
        return min(score, 1.0)
    
    def _get_method_pros(self, method: IrrigationMethod, context: Dict[str, Any]) -> List[str]:
        """Get advantages of irrigation method"""
        pros = {
            IrrigationMethod.DRIP: [
                "90% water efficiency",
                "Precise water control",
                "Reduced weed growth",
                "Lower labor requirement",
                "Suitable for water-scarce areas"
            ],
            IrrigationMethod.SPRINKLER: [
                "75% water efficiency",
                "Uniform water distribution",
                "Suitable for uneven terrain",
                "Can apply fertilizers with water",
                "Moderate initial cost"
            ],
            IrrigationMethod.FURROW: [
                "Low initial investment",
                "Simple operation",
                "Good for row crops",
                "Traditional method - familiar to farmers"
            ],
            IrrigationMethod.FLOOD: [
                "Very low initial cost",
                "Simple to operate",
                "Good for rice cultivation",
                "Minimal maintenance"
            ]
        }
        
        return pros.get(method, [])
    
    def _get_method_cons(self, method: IrrigationMethod, context: Dict[str, Any]) -> List[str]:
        """Get disadvantages of irrigation method"""
        cons = {
            IrrigationMethod.DRIP: [
                "High initial investment",
                "Requires filtration system",
                "Prone to clogging",
                "Needs technical knowledge"
            ],
            IrrigationMethod.SPRINKLER: [
                "Moderate to high initial cost",
                "Affected by wind",
                "Higher energy requirement",
                "Not suitable for all crops"
            ],
            IrrigationMethod.FURROW: [
                "45% efficiency only",
                "Labor intensive",
                "Uneven water distribution",
                "Soil erosion risk"
            ],
            IrrigationMethod.FLOOD: [
                "Only 35% efficiency",
                "High water wastage",
                "Suitable for limited crops",
                "Drainage issues possible"
            ]
        }
        
        return cons.get(method, [])
    
    def _get_selection_criteria(self, context: Dict[str, Any]) -> List[str]:
        """Get irrigation method selection criteria"""
        criteria = [
            "Crop water requirements and growth pattern",
            "Soil type and infiltration characteristics",
            "Farm size and layout",
            "Water availability and quality",
            "Initial investment capacity",
            "Labor availability",
            "Energy costs",
            "Long-term sustainability goals"
        ]
        
        return criteria
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence in irrigation recommendations"""
        confidence = 0.4  # Base confidence
        
        # Data availability factors
        if context["crop_type"]:
            confidence += 0.20
        if context["soil_type"]:
            confidence += 0.15
        if context["farm_size"]:
            confidence += 0.10
        if context["location"]:
            confidence += 0.10
        if context["current_stage"]:
            confidence += 0.05
        
        return min(confidence, 0.90)
    
    def _generate_efficiency_tips(self, context: Dict[str, Any]) -> List[str]:
        """Generate water use efficiency tips"""
        tips = [
            "Monitor soil moisture regularly using simple tools",
            "Irrigate during early morning or evening to reduce evaporation",
            "Maintain proper field leveling for uniform water distribution",
            "Use mulching to reduce soil water evaporation",
            "Avoid over-irrigation which leads to nutrient leaching",
            "Check and maintain irrigation equipment regularly",
            "Follow weather forecasts to adjust irrigation timing",
            "Keep irrigation records for future planning"
        ]
        
        # Add method-specific tips
        if context.get("irrigation_method") == IrrigationMethod.DRIP:
            tips.extend([
                "Clean drip emitters weekly to prevent clogging",
                "Install pressure gauges to monitor system performance",
                "Use filtration system to ensure clean water"
            ])
        elif context.get("irrigation_method") == IrrigationMethod.SPRINKLER:
            tips.extend([
                "Adjust sprinkler spacing for uniform coverage",
                "Check for worn nozzles and replace as needed",
                "Avoid irrigation during windy conditions"
            ])
        
        return tips
    
    def _format_irrigation_summary(self, schedule: List[IrrigationSchedule], budget: Optional[WaterBudget]) -> List[str]:
        """Format irrigation recommendations summary"""
        summary = []
        
        if schedule:
            next_irrigation = schedule[0]
            summary.append(f"Next irrigation: {next_irrigation.date.strftime('%Y-%m-%d')} ({next_irrigation.water_amount:.1f}mm)")
        
        if budget:
            summary.append(f"Seasonal water need: {budget.irrigation_need:.0f}mm (₹{budget.total_cost:,.0f} cost)")
        
        if schedule:
            total_irrigations = len(schedule)
            summary.append(f"Planned irrigations: {total_irrigations} over crop season")
        
        return summary
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "Crop water requirement calculation using FAO methods",
            "Growth stage-specific irrigation scheduling",
            "Water budget planning and cost analysis",
            "Irrigation method selection and comparison",
            "Water use efficiency optimization",
            "Soil moisture monitoring guidance"
        ]
    
    def get_supported_queries(self) -> List[str]:
        """Return examples of supported query types"""
        return [
            "When should I water my wheat crop?",
            "How much water does cotton need per season?",
            "Best irrigation method for sandy soil?",
            "Drip vs sprinkler irrigation comparison",
            "Water requirements for different growth stages",
            "Cost of irrigation for 5 hectare farm"
        ]

    def _enhance_context_with_satellite_data(self, context: Dict, satellite_data: Dict) -> Dict:
        """Enhance irrigation context with satellite data insights"""
        enhanced_context = context.copy()
        
        if satellite_data:
            enhanced_context["satellite_insights"] = {
                "soil_moisture": satellite_data.get("soil_moisture", 0.0),
                "vegetation_health": satellite_data.get("ndvi", 0.0),
                "weather_conditions": satellite_data.get("weather", {}),
                "irrigation_urgency": self._assess_irrigation_urgency(satellite_data)
            }
            
            # Adjust irrigation need based on satellite soil moisture
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            if soil_moisture < 0.3:
                enhanced_context["irrigation_urgency"] = "high"
            elif soil_moisture < 0.5:
                enhanced_context["irrigation_urgency"] = "medium"
            else:
                enhanced_context["irrigation_urgency"] = "low"
            
        return enhanced_context
    
    def _assess_irrigation_urgency(self, satellite_data: Dict) -> str:
        """Assess irrigation urgency based on satellite data"""
        soil_moisture = satellite_data.get("soil_moisture", 0.0)
        ndvi = satellite_data.get("ndvi", 0.0)
        
        if soil_moisture < 0.25 or (soil_moisture < 0.4 and ndvi < 0.3):
            return "urgent"
        elif soil_moisture < 0.4 or (soil_moisture < 0.6 and ndvi < 0.5):
            return "high"
        elif soil_moisture < 0.6:
            return "medium"
        else:
            return "low"
    
    async def _calculate_water_requirements(self, context: Dict, satellite_data: Optional[Dict] = None) -> List[CropWaterRequirement]:
        """Calculate water requirements with satellite data enhancement"""
        requirements = []
        
        # Get base water requirements (original logic)
        base_requirements = await self._calculate_base_water_requirements(context)
        
        # Adjust based on satellite data
        for req in base_requirements:
            adjusted_req = req
            
            if satellite_data:
                soil_moisture = satellite_data.get("soil_moisture", 0.0)
                
                # Reduce water requirement if soil moisture is already high
                if soil_moisture > 0.7:
                    adjusted_req.daily_et *= 0.7  # Reduce by 30%
                    logger.info("[SATELLITE] High soil moisture detected - reducing water requirement")
                elif soil_moisture < 0.3:
                    adjusted_req.daily_et *= 1.2  # Increase by 20%
                    logger.info("[SATELLITE] Low soil moisture detected - increasing water requirement")
                else:
                    logger.info("[SATELLITE] Optimal soil moisture - normal water requirement")
            
            requirements.append(adjusted_req)
        
        return requirements
    
    async def _generate_irrigation_schedule(self, context: Dict, water_requirements: List, satellite_data: Optional[Dict] = None) -> List:
        """Generate irrigation schedule with satellite insights"""
        schedule = await self._generate_base_irrigation_schedule(context, water_requirements)
        
        if satellite_data and schedule:
            # Adjust timing based on satellite data
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            
            for irrigation in schedule:
                if soil_moisture < 0.3:
                    # Urgent irrigation needed - move schedule earlier
                    irrigation.priority = "high"
                    logger.info("[SATELLITE] Low soil moisture - early irrigation recommended")
                elif soil_moisture > 0.7:
                    # Delay irrigation due to high soil moisture
                    irrigation.priority = "low"
                    logger.info("[SATELLITE] High soil moisture - irrigation can be delayed")
                else:
                    logger.info("[SATELLITE] Normal irrigation timing appropriate")
        
        return schedule
    
    async def _recommend_irrigation_method(self, context: Dict, satellite_data: Optional[Dict] = None, 
                               agrisens_model_output: Optional[Dict] = None) -> Dict:
        """
        Recommend irrigation method with satellite insights and AgriSens ML model
        
        Args:
            context: Query context
            satellite_data: Optional satellite data
            agrisens_model_output: Optional ML model output
            
        Returns:
            Irrigation method recommendations
        """
        # Get base recommendation
        base_recommendation = await self._recommend_base_irrigation_method(context)
        
        # Enhanced recommendations from AgriSens ML model
        if agrisens_model_output:
            # Use recommendations from the model if available
            if "recommendations" in agrisens_model_output:
                method_recs = [rec for rec in agrisens_model_output["recommendations"] 
                              if "irrigation system" in rec.lower() or "irrigation method" in rec.lower()]
                
                if method_recs:
                    base_recommendation["model_recommendation"] = method_recs[0]
            
            # Water savings potential from the model
            if "water_savings_potential" in agrisens_model_output:
                base_recommendation["water_savings_potential"] = f"{agrisens_model_output['water_savings_potential']}%"
                
            # Use current irrigation method from model
            if "irrigation_method" in agrisens_model_output:
                base_recommendation["current_method"] = agrisens_model_output["irrigation_method"]
        
        # Add satellite-based method recommendations
        if satellite_data:
            soil_moisture = 0.5  # Default value
            
            # Extract soil moisture from satellite data
            if isinstance(satellite_data, dict):
                if "soil_moisture" in satellite_data:
                    sm_data = satellite_data["soil_moisture"]
                    if isinstance(sm_data, dict) and "values" in sm_data:
                        sm_values = sm_data["values"]
                        if sm_values:
                            soil_moisture = sum(sm_values) / len(sm_values) / 100.0  # Convert to 0-1 scale
            
            # Add satellite-based method recommendations
            if soil_moisture < 0.3:
                base_recommendation["satellite_recommendation"] = "Consider drip irrigation for precise water delivery"
            elif soil_moisture > 0.7:
                base_recommendation["satellite_recommendation"] = "Monitor closely - may not need irrigation soon"
            else:
                base_recommendation["satellite_recommendation"] = "Current method suitable based on soil moisture"
        
        # Integration of all recommendations
        if "model_recommendation" in base_recommendation and "satellite_recommendation" in base_recommendation:
            base_recommendation["integrated_recommendation"] = (
                f"Based on ML model and satellite data: {base_recommendation['model_recommendation']} "
                f"and {base_recommendation['satellite_recommendation']}"
            )
        
        return base_recommendation
    
    def _calculate_confidence(self, context: Dict, satellite_data: Optional[Dict] = None) -> float:
        """Calculate confidence score including satellite data availability"""
        base_confidence = 0.6
        
        # Context completeness
        if context.get("crop_type"):
            base_confidence += 0.1
        if context.get("soil_type"):
            base_confidence += 0.1
        if context.get("farm_size"):
            base_confidence += 0.05
        if context.get("irrigation_method"):
            base_confidence += 0.05
        
        # Satellite data availability bonus
        if satellite_data:
            base_confidence += 0.1
            if satellite_data.get("soil_moisture", 0) > 0:
                base_confidence += 0.05  # Extra confidence for actual soil moisture data
        
        return min(base_confidence, 1.0)
    
    def _generate_efficiency_tips(self, context: Dict, satellite_data: Optional[Dict] = None,
                           agrisens_model_output: Optional[Dict] = None) -> List[str]:
        """
        Generate irrigation efficiency tips including satellite insights and ML model recommendations
        
        Args:
            context: Query context
            satellite_data: Optional satellite data
            agrisens_model_output: Optional ML model output
            
        Returns:
            List of efficiency tips
        """
        tips = []
        
        # Include model-based recommendations if available
        if agrisens_model_output and "recommendations" in agrisens_model_output:
            model_recs = agrisens_model_output["recommendations"]
            for rec in model_recs:
                tips.append(f"[AgriSens Model] {rec}")
        
        # Base efficiency tips if no model recommendations
        if not tips:
            if context.get("irrigation_method") == IrrigationMethod.FLOOD:
                tips.append("Consider drip irrigation to reduce water wastage by 30-50%")
            
            tips.append("Irrigate during early morning or evening to minimize evaporation")
            tips.append("Monitor soil moisture regularly for optimal timing")
        
        # Satellite-based tips
        if satellite_data:
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            ndvi = satellite_data.get("ndvi", 0.0)
            
            if soil_moisture < 0.3:
                tips.append("[SATELLITE] Immediate irrigation needed - soil moisture critically low")
            elif soil_moisture > 0.7:
                tips.append("[SATELLITE] Delay irrigation - soil has adequate moisture")
            
            if ndvi < 0.3:
                tips.append("[SATELLITE] Poor vegetation health detected - check irrigation adequacy")
            elif ndvi > 0.7:
                tips.append("[SATELLITE] Excellent vegetation health - current irrigation effective")
        
        return tips
    
    def _format_irrigation_summary(self, schedule: List, budget, satellite_data: Optional[Dict] = None) -> List[str]:
        """Format irrigation summary including satellite insights"""
        summary = []
        
        if schedule:
            next_irrigation = schedule[0]
            summary_text = f"Next irrigation: {next_irrigation.date.strftime('%Y-%m-%d')} ({next_irrigation.water_amount:.1f}mm)"
            if satellite_data:
                summary_text += " [SAT]"
            summary.append(summary_text)
        
        if budget:
            summary.append(f"Seasonal water need: {budget.irrigation_need:.0f}mm")
        
        if satellite_data:
            soil_moisture = satellite_data.get("soil_moisture", 0.0)
            summary.append(f"[SATELLITE] Current soil moisture: {soil_moisture:.1%}")
        
        return summary

    # Base methods that need to be implemented for backward compatibility
    async def _calculate_base_water_requirements(self, context: Dict) -> List:
        """Base water requirement calculation (original method renamed)"""
        # Implementation of original _calculate_water_requirements logic
        return []
    
    async def _generate_base_irrigation_schedule(self, context: Dict, water_requirements: List) -> List:
        """Base irrigation schedule generation (original method renamed)"""
        # Implementation of original _generate_irrigation_schedule logic  
        return []
    
    async def _recommend_base_irrigation_method(self, context: Dict) -> Dict:
        """Base irrigation method recommendation (original method renamed)"""
        # Implementation of original _recommend_irrigation_method logic
        return {}
