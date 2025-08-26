"""
Input Materials Advisor Agent
Specialized agent for recommending optimal and cost-effective fertilizers, 
seeds, and pesticides for Indian agricultural systems.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from enum import Enum
import asyncio
import random
import re

from .base_agent import BaseWorkerAgent
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, Location, QueryDomain, Language
)
from ..core.models import AgentCapability, Task
from ..models.AgriMitr_fertilizer_recommendation import (
    enhance_input_materials_with_fertilizer_recommend as AgriMitr_fertilizer_recommend,
    NutrientPlan as AgriNutrientPlan,
    FertilizerRecommendation, SoilAnalysis
)
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary

logger = logging.getLogger(__name__)


class InputType(Enum):
    """Types of agricultural inputs"""
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide" 
    SEED = "seed"
    GROWTH_REGULATOR = "growth_regulator"
    SOIL_AMENDMENT = "soil_amendment"


class FertilizerType(Enum):
    """Types of fertilizers"""
    UREA = "urea"
    DAP = "dap"  # Di-ammonium phosphate
    MOP = "mop"  # Muriate of potash
    NPK = "npk"
    ORGANIC = "organic"
    BIOFERTILIZER = "biofertilizer"
    MICRONUTRIENT = "micronutrient"


class PesticideType(Enum):
    """Types of pesticides"""
    INSECTICIDE = "insecticide"
    FUNGICIDE = "fungicide"
    HERBICIDE = "herbicide"
    NEMATICIDE = "nematicide"
    BIOPESTICIDE = "biopesticide"


class ApplicationMethod(Enum):
    """Methods of application"""
    SOIL_APPLICATION = "soil_application"
    FOLIAR_SPRAY = "foliar_spray"
    SEED_TREATMENT = "seed_treatment"
    DRIP_IRRIGATION = "drip_irrigation"
    BROADCAST = "broadcast"


@dataclass
class InputProduct:
    """Agricultural input product details"""
    product_name: str
    input_type: InputType
    sub_type: str  # FertilizerType, PesticideType, etc.
    composition: Dict[str, float]  # Active ingredients/nutrients
    application_rate: str
    application_method: ApplicationMethod
    cost_per_unit: float
    unit: str  # kg, liter, packet
    brand: str
    availability: str  # "widely_available", "limited", "seasonal"
    organic_certified: bool
    target_crops: List[CropType]
    soil_suitability: List[SoilType]


@dataclass
class InputRecommendation:
    """Input material recommendation"""
    crop_type: CropType
    growth_stage: str
    soil_type: SoilType
    primary_inputs: List[InputProduct]
    secondary_inputs: List[InputProduct]
    total_cost_estimate: float
    cost_breakdown: Dict[str, float]
    application_schedule: List[Dict[str, Any]]
    expected_benefits: List[str]
    precautions: List[str]
    alternatives: List[InputProduct]


class InputMaterialsAgent(BaseWorkerAgent):
    """
    Specialized agent for recommending optimal agricultural inputs.
    Provides cost-effective recommendations for fertilizers, pesticides,
    and seeds based on crop requirements, soil conditions, and budget.
    """
    
    def __init__(self):
        super().__init__(
            name="input_materials_agent",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.PLANNING,
                AgentCapability.DATA_PROCESSING
            ],
            agent_type="input_materials"
        )
        
        # Initialize product databases
        self._initialize_fertilizer_database()
        self._initialize_pesticide_database()
        self._initialize_seed_database()
        self._initialize_cost_data()
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an input materials recommendation task (required by BaseWorkerAgent)"""
        try:
            # Extract query from task or context
            if hasattr(task, 'query') and task.query:
                query = task.query
            elif 'query' in context:
                query = context['query']
            else:
                return {"error": "No query provided for input materials analysis"}
            
            # Process the query using our existing logic
            if isinstance(query, AgricultureQuery):
                result = asyncio.run(self.process_query(query))
                return {"success": True, "response": result}
            else:
                return {"error": "Invalid query format"}
                
        except Exception as e:
            return {"error": f"Input materials analysis failed: {str(e)}"}
    
    def _initialize_fertilizer_database(self):
        """Initialize comprehensive fertilizer database"""
        self.fertilizers = {
            "urea_46": InputProduct(
                product_name="Urea 46%",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.UREA.value,
                composition={"nitrogen": 46.0},
                application_rate="120-150 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=350.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IFFCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.MAIZE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "dap_fertilizer": InputProduct(
                product_name="DAP (Di-Ammonium Phosphate)",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.DAP.value,
                composition={"nitrogen": 18.0, "phosphorus": 46.0},
                application_rate="100-125 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=1450.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IFFCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.COTTON],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.SANDY]
            ),
            
            "npk_complex": InputProduct(
                product_name="NPK Complex 10:26:26",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.NPK.value,
                composition={"nitrogen": 10.0, "phosphorus": 26.0, "potassium": 26.0},
                application_rate="150-200 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=1200.0,
                unit="50kg bag",
                brand="KRIBHCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.COTTON, CropType.SUGARCANE],
                soil_suitability=[SoilType.BLACK, SoilType.RED, SoilType.LATERITE]
            ),
            
            "organic_compost": InputProduct(
                product_name="Organic Compost",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.ORGANIC.value,
                composition={"organic_matter": 45.0, "nitrogen": 1.5, "phosphorus": 1.0, "potassium": 1.5},
                application_rate="5-10 tonnes/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=150.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="Local/FPO",
                availability="seasonal",
                organic_certified=True,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.COTTON, CropType.SUGARCANE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED, SoilType.SANDY]
            )
        }
    
    def _initialize_pesticide_database(self):
        """Initialize pesticide and pest control database"""
        self.pesticides = {
            "chlorpyrifos": InputProduct(
                product_name="Chlorpyrifos 20% EC",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.INSECTICIDE.value,
                composition={"chlorpyrifos": 20.0},
                application_rate="2-2.5 ml/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=280.0,  # Rs per 250ml bottle
                unit="250ml bottle",
                brand="Tata Rallis",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.COTTON, CropType.RICE, CropType.WHEAT],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "mancozeb": InputProduct(
                product_name="Mancozeb 75% WP",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.FUNGICIDE.value,
                composition={"mancozeb": 75.0},
                application_rate="2-3 grams/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=320.0,  # Rs per 500g pack
                unit="500g pack",
                brand="UPL",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.RICE, CropType.WHEAT, CropType.COTTON],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "neem_oil": InputProduct(
                product_name="Neem Oil Organic",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.BIOPESTICIDE.value,
                composition={"azadirachtin": 1.0, "neem_oil": 99.0},
                application_rate="3-5 ml/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=180.0,  # Rs per 250ml bottle
                unit="250ml bottle",
                brand="Organic India",
                availability="widely_available",
                organic_certified=True,
                target_crops=[CropType.COTTON, CropType.RICE, CropType.WHEAT, CropType.SUGARCANE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED, SoilType.SANDY]
            )
        }
    
    def _initialize_seed_database(self):
        """Initialize seed variety database"""
        self.seeds = {
            "wheat_hd3086": InputProduct(
                product_name="Wheat HD-3086",
                input_type=InputType.SEED,
                sub_type="high_yielding_variety",
                composition={"purity": 98.0, "germination": 85.0},
                application_rate="100-125 kg/hectare",
                application_method=ApplicationMethod.BROADCAST,
                cost_per_unit=2800.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IARI",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK]
            ),
            
            "rice_pusa1121": InputProduct(
                product_name="Basmati Rice Pusa-1121",
                input_type=InputType.SEED,
                sub_type="premium_variety",
                composition={"purity": 97.0, "germination": 80.0},
                application_rate="20-25 kg/hectare",
                application_method=ApplicationMethod.SEED_TREATMENT,
                cost_per_unit=5500.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IARI",
                availability="seasonal",
                organic_certified=False,
                target_crops=[CropType.RICE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK]
            ),
            
            "cotton_bt": InputProduct(
                product_name="Bt Cotton RCH-659",
                input_type=InputType.SEED,
                sub_type="genetically_modified",
                composition={"purity": 95.0, "germination": 80.0},
                application_rate="1.5-2.0 kg/hectare",
                application_method=ApplicationMethod.SEED_TREATMENT,
                cost_per_unit=950.0,  # Rs per 450g packet
                unit="450g packet",
                brand="Rasi Seeds",
                availability="seasonal",
                organic_certified=False,
                target_crops=[CropType.COTTON],
                soil_suitability=[SoilType.BLACK, SoilType.RED]
            )
        }
    
    def _initialize_cost_data(self):
        """Initialize regional cost and availability data"""
        self.regional_cost_factors = {
            "Punjab": 1.0,      # Base pricing
            "Haryana": 1.05,    # 5% higher
            "Uttar Pradesh": 0.95,  # 5% lower
            "Maharashtra": 1.1,  # 10% higher
            "Karnataka": 1.08,   # 8% higher
            "Andhra Pradesh": 0.98  # 2% lower
        }
        
        self.seasonal_factors = {
            "peak_season": 1.2,  # 20% higher during peak
            "off_season": 0.9,   # 10% lower during off-season
            "normal": 1.0        # Normal pricing
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process an input materials query with AgriMitr model integration"""
        try:
            query_text = query.query_text.lower()
            location = query.location
            context = query.context or {}
            
            # Extract key information
            crop_type = self._extract_crop_type(query_text, context)
            soil_type = self._extract_soil_type(query_text, context)
            growth_stage = self._extract_growth_stage(query_text, context)
            budget_constraint = self._extract_budget_constraint(query_text, context)
            
            # Determine if user prefers organic inputs
            organic_preference = "organic" in query_text.lower() or context.get("organic_preference", False)
            
            # Get soil data (from context or default values)
            soil_data = self._prepare_soil_data(soil_type, context)
            
            # Initialize response parts
            response_parts = []
            confidence = 0.75
            
            # Get satellite data if available
            satellite_data = None
            try:
                satellite_data = await get_satellite_data_for_location(location)
                if satellite_data:
                    response_parts.append(format_satellite_summary(satellite_data))
                    confidence += 0.15
                    
                    # Enhance soil data with satellite information
                    if "ndvi" in satellite_data:
                        # Adjust nitrogen levels based on vegetation index
                        ndvi = satellite_data.get("ndvi", 0.5)
                        if ndvi < 0.3:
                            soil_data["nitrogen"] *= 0.8  # Likely nitrogen deficient
                        elif ndvi > 0.7:
                            soil_data["nitrogen"] *= 1.2  # Good nitrogen levels
            
            except Exception as e:
                logger.warning(f"Satellite data retrieval failed: {e}")
                response_parts.append("Note: Satellite data is temporarily unavailable.")
                confidence *= 0.9
                
            # Use AgriMitr fertilizer recommendation model
            crop_type_str = str(crop_type.value) if isinstance(crop_type, Enum) else str(crop_type)
            nutrient_plan = AgriMitr_fertilizer_recommend(
                crop_type=crop_type_str,
                soil_data=soil_data,
                growth_stage=growth_stage,
                budget_constraint=budget_constraint,
                organic_preference=organic_preference,
                location_data=satellite_data
            )
            
            # Generate response based on nutrient plan
            response_parts.extend(self._format_nutrient_plan_response(nutrient_plan, crop_type_str, soil_type))
            
            # Add confidence boosting if we have satellite data
            if satellite_data:
                confidence = min(0.98, confidence + 0.1)
                
            # Generate final response
            full_response = "\n\n".join(response_parts)
            
            return AgentResponse(
                query_id=query.query_id,
                response_text=full_response,
                confidence=confidence,
                agent_name=self.name,
                metadata={
                    "crop_type": str(crop_type),
                    "soil_type": str(soil_type),
                    "growth_stage": growth_stage,
                    "organic_preference": organic_preference,
                    "soil_health_score": nutrient_plan.current_status.health_score,
                    "recommendation_count": len(nutrient_plan.recommendations),
                    "total_cost": nutrient_plan.total_cost,
                    "expected_roi": nutrient_plan.expected_roi,
                    "satellite_enhanced": bool(satellite_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing input materials query: {e}", exc_info=True)
            return AgentResponse(
                query_id=query.query_id,
                response_text=f"I apologize, but I couldn't generate input material recommendations due to: {str(e)}. Please provide more details about your crop and soil type.",
                confidence=0.3,
                agent_name=self.name
            )
    
    def _initialize_fertilizer_database(self):
        """Initialize comprehensive fertilizer database"""
        self.fertilizers = {
            "urea_46": InputProduct(
                product_name="Urea 46%",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.UREA.value,
                composition={"nitrogen": 46.0},
                application_rate="120-150 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=350.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IFFCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.MAIZE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "dap_fertilizer": InputProduct(
                product_name="DAP (Di-Ammonium Phosphate)",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.DAP.value,
                composition={"nitrogen": 18.0, "phosphorus": 46.0},
                application_rate="100-125 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=1450.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IFFCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.COTTON],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.SANDY]
            ),
            
            "npk_complex": InputProduct(
                product_name="NPK Complex 10:26:26",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.NPK.value,
                composition={"nitrogen": 10.0, "phosphorus": 26.0, "potassium": 26.0},
                application_rate="150-200 kg/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=1200.0,
                unit="50kg bag",
                brand="KRIBHCO",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.COTTON, CropType.SUGARCANE],
                soil_suitability=[SoilType.BLACK, SoilType.RED, SoilType.LATERITE]
            ),
            
            "organic_compost": InputProduct(
                product_name="Organic Compost",
                input_type=InputType.FERTILIZER,
                sub_type=FertilizerType.ORGANIC.value,
                composition={"organic_matter": 45.0, "nitrogen": 1.5, "phosphorus": 1.0, "potassium": 1.5},
                application_rate="5-10 tonnes/hectare",
                application_method=ApplicationMethod.SOIL_APPLICATION,
                cost_per_unit=150.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="Local/FPO",
                availability="seasonal",
                organic_certified=True,
                target_crops=[CropType.WHEAT, CropType.RICE, CropType.COTTON, CropType.SUGARCANE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED, SoilType.SANDY]
            )
        }
    
    def _initialize_pesticide_database(self):
        """Initialize pesticide and pest control database"""
        self.pesticides = {
            "chlorpyrifos": InputProduct(
                product_name="Chlorpyrifos 20% EC",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.INSECTICIDE.value,
                composition={"chlorpyrifos": 20.0},
                application_rate="2-2.5 ml/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=280.0,  # Rs per 250ml bottle
                unit="250ml bottle",
                brand="Tata Rallis",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.COTTON, CropType.RICE, CropType.WHEAT],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "mancozeb": InputProduct(
                product_name="Mancozeb 75% WP",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.FUNGICIDE.value,
                composition={"mancozeb": 75.0},
                application_rate="2-3 grams/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=320.0,  # Rs per 500g pack
                unit="500g pack",
                brand="UPL",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.RICE, CropType.WHEAT, CropType.COTTON],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED]
            ),
            
            "neem_oil": InputProduct(
                product_name="Neem Oil Organic",
                input_type=InputType.PESTICIDE,
                sub_type=PesticideType.BIOPESTICIDE.value,
                composition={"azadirachtin": 1.0, "neem_oil": 99.0},
                application_rate="3-5 ml/liter water",
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                cost_per_unit=180.0,  # Rs per 250ml bottle
                unit="250ml bottle",
                brand="Organic India",
                availability="widely_available",
                organic_certified=True,
                target_crops=[CropType.COTTON, CropType.RICE, CropType.WHEAT, CropType.SUGARCANE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK, SoilType.RED, SoilType.SANDY]
            )
        }
    
    def _initialize_seed_database(self):
        """Initialize seed variety database"""
        self.seeds = {
            "wheat_hd3086": InputProduct(
                product_name="Wheat HD-3086",
                input_type=InputType.SEED,
                sub_type="high_yielding_variety",
                composition={"purity": 98.0, "germination": 85.0},
                application_rate="100-125 kg/hectare",
                application_method=ApplicationMethod.BROADCAST,
                cost_per_unit=2800.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IARI",
                availability="widely_available",
                organic_certified=False,
                target_crops=[CropType.WHEAT],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK]
            ),
            
            "rice_pusa1121": InputProduct(
                product_name="Basmati Rice Pusa-1121",
                input_type=InputType.SEED,
                sub_type="premium_variety",
                composition={"purity": 97.0, "germination": 80.0},
                application_rate="20-25 kg/hectare",
                application_method=ApplicationMethod.SEED_TREATMENT,
                cost_per_unit=5500.0,  # Rs per 50kg bag
                unit="50kg bag",
                brand="IARI",
                availability="seasonal",
                organic_certified=False,
                target_crops=[CropType.RICE],
                soil_suitability=[SoilType.ALLUVIAL, SoilType.BLACK]
            ),
            
            "cotton_bt": InputProduct(
                product_name="Bt Cotton RCH-659",
                input_type=InputType.SEED,
                sub_type="genetically_modified",
                composition={"purity": 95.0, "germination": 80.0},
                application_rate="1.5-2.0 kg/hectare",
                application_method=ApplicationMethod.SEED_TREATMENT,
                cost_per_unit=950.0,  # Rs per 450g packet
                unit="450g packet",
                brand="Rasi Seeds",
                availability="seasonal",
                organic_certified=False,
                target_crops=[CropType.COTTON],
                soil_suitability=[SoilType.BLACK, SoilType.RED]
            )
        }
    
    def _initialize_cost_data(self):
        """Initialize regional cost and availability data"""
        self.regional_cost_factors = {
            "Punjab": 1.0,      # Base pricing
            "Haryana": 1.05,    # 5% higher
            "Uttar Pradesh": 0.95,  # 5% lower
            "Maharashtra": 1.1,  # 10% higher
            "Karnataka": 1.08,   # 8% higher
            "Andhra Pradesh": 0.98  # 2% lower
        }
        
        self.seasonal_factors = {
            "peak_season": 1.2,  # 20% higher during peak
            "off_season": 0.9,   # 10% lower during off-season
            "normal": 1.0        # Normal pricing
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process an input materials query with AgriMitr model integration"""
        try:
            query_text = query.query_text.lower()
            location = query.location
            context = query.context or {}
            
            # Extract key information
            crop_type = self._extract_crop_type(query_text, context)
            soil_type = self._extract_soil_type(query_text, context)
            growth_stage = self._extract_growth_stage(query_text, context)
            budget_constraint = self._extract_budget_constraint(query_text, context)
            
            # Determine if user prefers organic inputs
            organic_preference = "organic" in query_text.lower() or context.get("organic_preference", False)
            
            # Get soil data (from context or default values)
            soil_data = self._prepare_soil_data(soil_type, context)
            
            # Initialize response parts
            response_parts = []
            confidence = 0.75
            
            # Get satellite data if available
            satellite_data = None
            try:
                satellite_data = await get_satellite_data_for_location(location)
                if satellite_data:
                    response_parts.append(format_satellite_summary(satellite_data))
                    confidence += 0.15
                    
                    # Enhance soil data with satellite information
                    if "ndvi" in satellite_data:
                        # Adjust nitrogen levels based on vegetation index
                        ndvi = satellite_data.get("ndvi", 0.5)
                        if ndvi < 0.3:
                            soil_data["nitrogen"] *= 0.8  # Likely nitrogen deficient
                        elif ndvi > 0.7:
                            soil_data["nitrogen"] *= 1.2  # Good nitrogen levels
            
            except Exception as e:
                logger.warning(f"Satellite data retrieval failed: {e}")
                response_parts.append("Note: Satellite data is temporarily unavailable.")
                confidence *= 0.9
                
            # Use AgriMitr fertilizer recommendation model
            crop_type_str = str(crop_type.value) if isinstance(crop_type, Enum) else str(crop_type)
            nutrient_plan = AgriMitr_fertilizer_recommend(
                crop_type=crop_type_str,
                soil_data=soil_data,
                growth_stage=growth_stage,
                budget_constraint=budget_constraint,
                organic_preference=organic_preference,
                location_data=satellite_data
            )
            
            # Generate response based on nutrient plan
            response_parts.extend(self._format_nutrient_plan_response(nutrient_plan, crop_type_str, soil_type))
            
            # Add confidence boosting if we have satellite data
            if satellite_data:
                confidence = min(0.98, confidence + 0.1)
                
            # Generate final response
            full_response = "\n\n".join(response_parts)
            
            return AgentResponse(
                query_id=query.query_id,
                response_text=full_response,
                confidence=confidence,
                agent_name=self.name,
                metadata={
                    "crop_type": str(crop_type),
                    "soil_type": str(soil_type),
                    "growth_stage": growth_stage,
                    "organic_preference": organic_preference,
                    "soil_health_score": nutrient_plan.current_status.health_score,
                    "recommendation_count": len(nutrient_plan.recommendations),
                    "total_cost": nutrient_plan.total_cost,
                    "expected_roi": nutrient_plan.expected_roi,
                    "satellite_enhanced": bool(satellite_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing input materials query: {e}", exc_info=True)
            return AgentResponse(
                query_id=query.query_id,
                response_text=f"I apologize, but I couldn't generate input material recommendations due to: {str(e)}. Please provide more details about your crop and soil type.",
                confidence=0.3,
                agent_name=self.name
            )
    
    def _analyze_input_query(self, query_text: str) -> Dict[str, Any]:
        """Analyze query to identify crop and input requirements"""
        query_lower = query_text.lower()
        
        # Crop identification
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
        
        # Input type identification
        input_keywords = {
            "fertilizer": InputType.FERTILIZER, "खाद": InputType.FERTILIZER, "उर्वरक": InputType.FERTILIZER,
            "pesticide": InputType.PESTICIDE, "कीटनाशक": InputType.PESTICIDE, "दवा": InputType.PESTICIDE,
            "seed": InputType.SEED, "बीज": InputType.SEED, "variety": InputType.SEED,
            "urea": InputType.FERTILIZER, "यूरिया": InputType.FERTILIZER,
            "dap": InputType.FERTILIZER,
            "spray": InputType.PESTICIDE, "छिड़काव": InputType.PESTICIDE
        }
        
        found_input_type = None
        for keyword, input_type in input_keywords.items():
            if keyword in query_lower:
                found_input_type = input_type
                break
        
        # Growth stage identification
        stage_keywords = {
            "sowing": "sowing", "बुआई": "sowing",
            "flowering": "flowering", "फूल": "flowering",
            "fruiting": "fruiting", "फल": "fruiting",
            "harvest": "harvest", "कटाई": "harvest"
        }
        
        found_stage = "general"
        for keyword, stage in stage_keywords.items():
            if keyword in query_lower:
                found_stage = stage
                break
        
        return {
            "crop_type": found_crop,
            "input_type": found_input_type,
            "growth_stage": found_stage,
            "budget_conscious": any(word in query_lower for word in ["cheap", "low cost", "सस्ता", "कम कीमत"])
        }
    
    async def _generate_input_recommendation(self, query_analysis: Dict[str, Any],
                                           farm_profile: Optional[Any],
                                           location: Optional[Location]) -> InputRecommendation:
        """Generate comprehensive input recommendation"""
        
        crop_type = query_analysis.get("crop_type", CropType.WHEAT)
        input_type = query_analysis.get("input_type")
        growth_stage = query_analysis.get("growth_stage", "general")
        budget_conscious = query_analysis.get("budget_conscious", False)
        
        # Get soil type from farm profile
        soil_type = SoilType.ALLUVIAL  # Default
        if farm_profile and hasattr(farm_profile, 'soil_type'):
            soil_type = farm_profile.soil_type
        
        # Filter relevant products
        if input_type == InputType.FERTILIZER:
            relevant_products = [p for p in self.fertilizers.values() 
                               if crop_type in p.target_crops and soil_type in p.soil_suitability]
        elif input_type == InputType.PESTICIDE:
            relevant_products = [p for p in self.pesticides.values() 
                               if crop_type in p.target_crops]
        elif input_type == InputType.SEED:
            relevant_products = [p for p in self.seeds.values() 
                               if crop_type in p.target_crops]
        else:
            # Mixed recommendation
            relevant_products = []
            relevant_products.extend([p for p in self.fertilizers.values() 
                                    if crop_type in p.target_crops and soil_type in p.soil_suitability][:2])
            relevant_products.extend([p for p in self.pesticides.values() 
                                    if crop_type in p.target_crops][:1])
        
        # Sort by cost if budget conscious
        if budget_conscious:
            relevant_products.sort(key=lambda x: x.cost_per_unit)
        
        # Select primary and secondary inputs
        primary_inputs = relevant_products[:3]
        secondary_inputs = relevant_products[3:5] if len(relevant_products) > 3 else []
        
        # Calculate costs with regional factors
        cost_factor = 1.0
        if location and location.state in self.regional_cost_factors:
            cost_factor = self.regional_cost_factors[location.state]
        
        total_cost = sum(p.cost_per_unit * cost_factor for p in primary_inputs)
        
        # Create cost breakdown
        cost_breakdown = {p.product_name: p.cost_per_unit * cost_factor for p in primary_inputs}
        
        # Generate application schedule
        application_schedule = self._create_application_schedule(primary_inputs, growth_stage)
        
        return InputRecommendation(
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_type=soil_type,
            primary_inputs=primary_inputs,
            secondary_inputs=secondary_inputs,
            total_cost_estimate=total_cost,
            cost_breakdown=cost_breakdown,
            application_schedule=application_schedule,
            expected_benefits=self._get_expected_benefits(primary_inputs),
            precautions=self._get_safety_precautions(primary_inputs),
            alternatives=self._get_alternatives(primary_inputs, budget_conscious)
        )
    
    def _create_application_schedule(self, products: List[InputProduct], growth_stage: str) -> List[Dict[str, Any]]:
        """Create application schedule for inputs"""
        schedule = []
        
        for i, product in enumerate(products):
            if product.input_type == InputType.FERTILIZER:
                if "urea" in product.product_name.lower():
                    schedule.append({
                        "product": product.product_name,
                        "timing": "30-35 days after sowing",
                        "method": product.application_method.value,
                        "rate": product.application_rate,
                        "notes": "Apply after first irrigation"
                    })
                elif "dap" in product.product_name.lower():
                    schedule.append({
                        "product": product.product_name,
                        "timing": "At sowing time",
                        "method": product.application_method.value,
                        "rate": product.application_rate,
                        "notes": "Mix with soil before sowing"
                    })
            elif product.input_type == InputType.PESTICIDE:
                schedule.append({
                    "product": product.product_name,
                    "timing": "As per pest incidence",
                    "method": product.application_method.value,
                    "rate": product.application_rate,
                    "notes": "Spray during evening hours"
                })
        
        return schedule
    
    def _get_expected_benefits(self, products: List[InputProduct]) -> List[str]:
        """Get expected benefits from recommended inputs"""
        benefits = []
        
        for product in products:
            if product.input_type == InputType.FERTILIZER:
                if "nitrogen" in product.composition:
                    benefits.append("Enhanced vegetative growth and green color")
                if "phosphorus" in product.composition:
                    benefits.append("Better root development and flowering")
                if "potassium" in product.composition:
                    benefits.append("Improved disease resistance and fruit quality")
                if product.organic_certified:
                    benefits.append("Improved soil health and structure")
            
            elif product.input_type == InputType.PESTICIDE:
                if product.sub_type == PesticideType.INSECTICIDE.value:
                    benefits.append("Effective control of harmful insects")
                elif product.sub_type == PesticideType.FUNGICIDE.value:
                    benefits.append("Prevention of fungal diseases")
                if product.organic_certified:
                    benefits.append("Environmentally safe pest control")
        
        return list(set(benefits))  # Remove duplicates
    
    def _get_safety_precautions(self, products: List[InputProduct]) -> List[str]:
        """Get safety precautions for recommended inputs"""
        precautions = []
        
        has_chemical_pesticide = any(p.input_type == InputType.PESTICIDE and not p.organic_certified 
                                   for p in products)
        has_fertilizer = any(p.input_type == InputType.FERTILIZER for p in products)
        
        if has_chemical_pesticide:
            precautions.extend([
                "Wear protective clothing and mask during application",
                "Do not spray during windy conditions",
                "Maintain pre-harvest interval as per label instructions"
            ])
        
        if has_fertilizer:
            precautions.extend([
                "Apply fertilizers based on soil test recommendations",
                "Ensure adequate moisture before fertilizer application",
                "Store fertilizers in dry, ventilated place"
            ])
        
        precautions.append("Keep all inputs away from children and animals")
        
        return precautions
    
    def _get_alternatives(self, primary_products: List[InputProduct], budget_conscious: bool) -> List[InputProduct]:
        """Get alternative product recommendations"""
        alternatives = []
        
        # Add organic alternatives
        organic_products = [p for p in list(self.fertilizers.values()) + list(self.pesticides.values()) 
                          if p.organic_certified and p not in primary_products]
        alternatives.extend(organic_products[:2])
        
        # Add budget-friendly alternatives if budget conscious
        if budget_conscious:
            all_products = list(self.fertilizers.values()) + list(self.pesticides.values())
            budget_products = sorted([p for p in all_products if p not in primary_products], 
                                   key=lambda x: x.cost_per_unit)[:2]
            alternatives.extend(budget_products)
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _create_agent_response(self, recommendation: InputRecommendation, 
                             query: AgricultureQuery, nutrient_plan: Optional[AgriNutrientPlan] = None, AgriMitr_used: bool = False) -> AgentResponse:
        """Create structured agent response (extended to include AgriMitr nutrient plan)."""
        summary = self._create_summary(recommendation, query.query_language)
        recommendations_list = self._create_recommendations_list(recommendation)

        # Append nutrient plan recommendations (top 1-2) if available
        if nutrient_plan and nutrient_plan.recommendations:
            for rec in nutrient_plan.recommendations[:2]:
                recommendations_list.append({
                    "title": f"Fertilizer Plan: {rec.primary_fertilizer.value}",
                    "description": f"Rate: {rec.application_rate:.1f} kg/ha | NPK: {rec.npk_ratio} | Cost≈₹{rec.cost_estimate:,.0f}",
                    "priority": "high",
                    "action_required": "Follow staged application schedule"
                })

        sources = ["Fertilizer Database", "Pesticide Registry", "Seed Catalog", "Market Price Data"]
        if nutrient_plan:
            sources.append("AgriMitr Fertilizer Model")

        metadata_extra = {}
        if nutrient_plan:
            metadata_extra = {
                "AgriMitr_soil_health": nutrient_plan.current_status.health_score,
                "AgriMitr_total_cost": nutrient_plan.total_cost,
                "AgriMitr_expected_roi": nutrient_plan.expected_roi,
                "AgriMitr_growth_stage": nutrient_plan.growth_stage,
                "AgriMitr_used": AgriMitr_used
            }

        return AgentResponse(
            agent_id=self.name,
            agent_name="Input Materials Advisor",
            query_id=query.query_id,
            response_text=summary + (" | AgriMitr nutrient optimization applied" if nutrient_plan else ""),
            response_language=query.query_language,
            confidence_score=0.88 if nutrient_plan else 0.85,
            reasoning=(f"Based on {recommendation.crop_type.value} requirements, soil conditions, and AgriMitr analysis" if nutrient_plan else f"Based on {recommendation.crop_type.value} requirements and {recommendation.soil_type.value} soil conditions"),
            recommendations=recommendations_list,
            sources=sources,
            next_steps=["Purchase recommended inputs", "Apply as per schedule", "Monitor crop response"] + (["Follow nutrient monitoring schedule"] if nutrient_plan else []),
            timestamp=datetime.now(),
            processing_time_ms=220 if nutrient_plan else 180,
            metadata={
                "crop_type": recommendation.crop_type.value,
                "soil_type": recommendation.soil_type.value,
                "total_cost": recommendation.total_cost_estimate,
                "num_primary_inputs": len(recommendation.primary_inputs),
                "growth_stage": recommendation.growth_stage,
                **metadata_extra
            }
        )
    
    def _create_summary(self, recommendation: InputRecommendation, language: Language) -> str:
        """Create localized summary"""
        crop_name = recommendation.crop_type.name.capitalize()
        cost = recommendation.total_cost_estimate
        
        if language in [Language.HINDI, Language.MIXED]:
            crop_translations = {
                "Wheat": "गेहूं", "Rice": "चावल", "Cotton": "कपास", "Sugarcane": "गन्ना"
            }
            crop_name = crop_translations.get(crop_name, crop_name)
            
            return (f"{crop_name} के लिए इनपुट सुझाव: {len(recommendation.primary_inputs)} मुख्य उत्पाद। "
                    f"कुल लागत: ₹{cost:,.0f}। मिट्टी के प्रकार: {recommendation.soil_type.value}। "
                    f"वृद्धि अवस्था: {recommendation.growth_stage}।")
        
        return (f"Input recommendations for {crop_name}: {len(recommendation.primary_inputs)} primary products. "
                f"Total cost: ₹{cost:,.0f}. Soil type: {recommendation.soil_type.value}. "
                f"Growth stage: {recommendation.growth_stage}.")
    
    def _create_recommendations_list(self, recommendation: InputRecommendation) -> List[Dict[str, Any]]:
        """Create detailed recommendations list"""
        recs = []
        
        # Primary inputs
        for i, product in enumerate(recommendation.primary_inputs[:3]):
            priority = ["high", "medium", "low"][i]
            recs.append({
                "title": f"{product.product_name} ({product.brand})",
                "description": f"Rate: {product.application_rate} | Cost: ₹{product.cost_per_unit}/{product.unit}",
                "priority": priority,
                "action_required": f"Purchase from {product.availability} sources"
            })
        
        # Cost breakdown
        if recommendation.cost_breakdown:
            cost_desc = " | ".join([f"{k}: ₹{v:,.0f}" for k, v in list(recommendation.cost_breakdown.items())[:2]])
            recs.append({
                "title": "Cost Breakdown",
                "description": cost_desc,
                "priority": "medium",
                "action_required": "Budget allocation"
            })
        
        # Application schedule
        if recommendation.application_schedule:
            schedule_desc = recommendation.application_schedule[0].get("timing", "As recommended")
            recs.append({
                "title": "Application Schedule",
                "description": f"First application: {schedule_desc}",
                "priority": "high",
                "action_required": "Follow timing strictly"
            })
        
        return recs
    
    def _create_general_input_info_response(self, query: AgricultureQuery) -> AgentResponse:
        """Create response when no specific crop or input is identified"""
        return AgentResponse(
            agent_id=self.name,
            agent_name="Input Materials Advisor",
            query_id=query.query_id,
            response_text="Please specify a crop and input type (fertilizer, pesticide, or seed) for recommendations. कृपया सुझावों के लिए एक फसल और इनपुट प्रकार (उर्वरक, कीटनाशक, या बीज) निर्दिष्ट करें।",
            response_language=query.query_language,
            confidence_score=0.9,
            recommendations=[
                {"title": "Specify Crop and Input", "description": "Mention the crop and type of input needed.", "priority": "high"}
            ],
            timestamp=datetime.now()
        )
    
    def _create_error_response(self, query: AgricultureQuery, error: str) -> AgentResponse:
        """Create error response"""
        return AgentResponse(
            agent_id=self.name,
            agent_name="Input Materials Advisor",
            query_id=query.query_id,
            response_text="Sorry, I encountered a technical issue while recommending inputs. Please try again later. क्षमा करें, इनपुट की सिफारिश करते समय मुझे एक तकनीकी समस्या का सामना करना पड़ा।",
            response_language=query.query_language,
            confidence_score=0.1,
            warnings=[f"Technical error: {error}"],
            timestamp=datetime.now(),
            metadata={"error": True, "error_message": error}
        )
    
    # ---------------- AgriMitr Integration Helpers ----------------
    def _extract_soil_data(self, query: AgricultureQuery) -> Dict[str, float]:
        soil_ctx = query.context.get("soil_data") if query.context else None
        if isinstance(soil_ctx, dict):
            return soil_ctx
        # Try to parse from text
        return self._parse_soil_values_from_text(query.query_text.lower())

    def _parse_soil_values_from_text(self, text: str) -> Dict[str, float]:
        soil: Dict[str, float] = {}
        patterns = {
            'nitrogen': r'(?:n|nitrogen)[:=\s]+(\d{1,4})',
            'phosphorus': r'(?:p|phosphorus)[:=\s]+(\d{1,4})',
            'potassium': r'(?:k|potassium)[:=\s]+(\d{1,4})',
            'ph': r'(?:ph)[:=\s]+(\d(?:\.\d)?)',
            'organic_matter': r'(?:om|organic matter)[:=\s]+(\d(?:\.\d)?)',
            'moisture_content': r'(?:moisture)[:=\s]+(\d{1,3})'
        }
        for key, pattern in patterns.items():
            m = re.search(pattern, text)
            if m:
                try:
                    soil[key] = float(m.group(1))
                except ValueError:
                    pass
        return soil

    def _extract_growth_stage_from_text(self, text: str) -> Optional[str]:
        stages = {
            'tillering': 'tillering', 'flowering': 'flowering', 'boll': 'flowering', 'vegetative': 'vegetative',
            'panicle': 'panicle_initiation', 'grain': 'grain_filling', 'fruit': 'fruiting', 'planting': 'planting'
        }
        for k, stage in stages.items():
            if k in text.lower():
                return stage
        return None

    def _serialize_location(self, location: Optional[Location]) -> Dict[str, Any]:
        if not location:
            return {}
        return {
            'state': getattr(location, 'state', None),
            'district': getattr(location, 'district', None),
            'latitude': getattr(location, 'latitude', None),
            'longitude': getattr(location, 'longitude', None)
        }

    def _prepare_soil_data(self, soil_type: SoilType, context: Dict[str, Any]) -> Dict[str, float]:
        """Prepare soil data for fertilizer recommendation model"""
        # Default values based on soil type
        soil_defaults = {
            SoilType.ALLUVIAL: {"nitrogen": 280, "phosphorus": 25, "potassium": 220, "ph": 7.2, "organic_matter": 2.5},
            SoilType.BLACK: {"nitrogen": 200, "phosphorus": 18, "potassium": 300, "ph": 7.8, "organic_matter": 1.8},
            SoilType.RED: {"nitrogen": 180, "phosphorus": 12, "potassium": 180, "ph": 6.0, "organic_matter": 1.2},
            SoilType.LATERITE: {"nitrogen": 140, "phosphorus": 8, "potassium": 120, "ph": 5.5, "organic_matter": 0.8},
            SoilType.SANDY: {"nitrogen": 120, "phosphorus": 10, "potassium": 100, "ph": 6.8, "organic_matter": 0.6},
            SoilType.CLAY: {"nitrogen": 220, "phosphorus": 15, "potassium": 200, "ph": 7.5, "organic_matter": 2.0}
        }
        
        # Get default values for the soil type
        defaults = soil_defaults.get(soil_type, soil_defaults[SoilType.ALLUVIAL])
        
        # Override with values from context if available
        soil_data = {
            "nitrogen": float(context.get("nitrogen", defaults["nitrogen"])),
            "phosphorus": float(context.get("phosphorus", defaults["phosphorus"])),
            "potassium": float(context.get("potassium", defaults["potassium"])),
            "ph": float(context.get("ph", defaults["ph"])),
            "organic_matter": float(context.get("organic_matter", defaults["organic_matter"])),
            "moisture_content": float(context.get("moisture_content", 50.0)),
            "soil_type": str(soil_type.value) if isinstance(soil_type, Enum) else str(soil_type)
        }
        
        return soil_data
    
    def _format_nutrient_plan_response(self, nutrient_plan: AgriNutrientPlan, crop_type: str, soil_type: SoilType) -> List[str]:
        """Format nutrient plan into readable response parts"""
        response_parts = []
        
        # Soil analysis
        soil_analysis = nutrient_plan.current_status
        response_parts.append(f"## 🌱 Soil Analysis for {crop_type}")
        response_parts.append(f"**Soil Health Score:** {soil_analysis.health_score:.1f}/100")
        
        if soil_analysis.health_score >= 80:
            health_desc = "excellent"
        elif soil_analysis.health_score >= 60:
            health_desc = "good"
        elif soil_analysis.health_score >= 40:
            health_desc = "fair"
        else:
            health_desc = "poor"
        
        response_parts.append(f"Your soil health is {health_desc}.")
        
        # Nutrient levels
        response_parts.append(f"\n**Current Nutrient Levels:**")
        response_parts.append(f"* Nitrogen (N): {soil_analysis.nitrogen} kg/ha")
        response_parts.append(f"* Phosphorus (P): {soil_analysis.phosphorus} kg/ha")
        response_parts.append(f"* Potassium (K): {soil_analysis.potassium} kg/ha")
        response_parts.append(f"* pH: {soil_analysis.ph}")
        
        # Deficiencies and excesses
        if soil_analysis.deficiencies:
            response_parts.append(f"\n**Deficiencies:** {', '.join(soil_analysis.deficiencies)}")
        if soil_analysis.excesses:
            response_parts.append(f"\n**Excesses:** {', '.join(soil_analysis.excesses)}")
            
        # Fertilizer recommendations
        response_parts.append(f"\n## 💧 Fertilizer Recommendations")
        
        if nutrient_plan.recommendations:
            # Primary recommendation
            primary_rec = nutrient_plan.recommendations[0]
            response_parts.append(f"**Primary Recommendation:** {primary_rec.primary_fertilizer.value}")
            response_parts.append(f"**Application Rate:** {primary_rec.application_rate:.1f} kg/hectare")
            response_parts.append(f"**NPK Ratio:** {primary_rec.npk_ratio}")
            response_parts.append(f"**Application Method:** {primary_rec.application_method}")
            response_parts.append(f"**Cost Estimate:** ₹{primary_rec.cost_estimate:.2f}/hectare")
            
            # Add timing information
            if primary_rec.application_timing:
                response_parts.append(f"**Application Timing:** {', '.join(primary_rec.application_timing)}")
            
            # Secondary recommendations if available
            if len(nutrient_plan.recommendations) > 1:
                response_parts.append(f"\n**Secondary Recommendations:**")
                for i, rec in enumerate(nutrient_plan.recommendations[1:], 1):
                    if i > 2:  # Limit to 2 secondary recommendations
                        break
                    response_parts.append(f"* {rec.primary_fertilizer.value}: {rec.application_rate:.1f} kg/ha (₹{rec.cost_estimate:.2f}/ha)")
            
            # Organic alternatives if available
            if primary_rec.organic_alternatives:
                response_parts.append(f"\n**Organic Alternatives:**")
                response_parts.append(", ".join(primary_rec.organic_alternatives))
        else:
            response_parts.append("No specific fertilizer recommendations available.")
            
        # Economics
        response_parts.append(f"\n## 💰 Economics")
        response_parts.append(f"**Total Cost:** ₹{nutrient_plan.total_cost:.2f}/hectare")
        response_parts.append(f"**Expected Return on Investment:** {nutrient_plan.expected_roi:.1f}%")
        
        # Monitoring schedule
        response_parts.append(f"\n## 📊 Monitoring Schedule")
        for i, item in enumerate(nutrient_plan.monitoring_schedule):
            if i > 3:  # Limit to 4 monitoring points
                break
            response_parts.append(f"* {item}")
            
        return response_parts
