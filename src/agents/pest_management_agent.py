"""
Pest Management Agent
Specialized agent for pest identification, outbreak forecasting, and treatment recommendations.
Focuses on text-based identification and integrated pest management strategies.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import re

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
# AgriMitr Disease Identification Integration
from ..models.AgriMitr_disease_identification import enhance_pest_management_with_disease_id, DiseaseIdentification
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SeasonType, WeatherData,
    Location, FarmProfile, QueryDomain, AgentCapability
)

logger = logging.getLogger(__name__)


class PestType(Enum):
    """Types of agricultural pests"""
    INSECT = "insect"
    DISEASE = "disease"
    WEED = "weed"
    FUNGAL = "fungal"
    VIRAL = "viral"
    BACTERIAL = "bacterial"
    NEMATODE = "nematode"


class SeverityLevel(Enum):
    """Pest infestation severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class TreatmentType(Enum):
    """Types of pest treatments"""
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"
    CULTURAL = "cultural"
    MECHANICAL = "mechanical"
    INTEGRATED = "integrated"


@dataclass
class PestIdentification:
    """Pest identification result"""
    pest_name: str
    pest_type: PestType
    confidence: float  # 0.0 to 1.0
    symptoms: List[str]
    affected_crops: List[CropType]
    severity_indicators: List[str]
    common_names: List[str]
    description: str


@dataclass
class TreatmentRecommendation:
    """Pest treatment recommendation"""
    treatment_type: TreatmentType
    method: str
    products: List[str]
    application_timing: str
    frequency: str
    dosage: str
    cost_estimate: float  # rupees per hectare
    effectiveness: float  # 0.0 to 1.0
    safety_precautions: List[str]
    environmental_impact: str


@dataclass
class PestForecast:
    """Pest outbreak forecast"""
    pest_name: str
    risk_level: SeverityLevel
    outbreak_probability: float  # 0.0 to 1.0
    peak_activity_period: Tuple[int, int]  # start_week, end_week
    weather_factors: List[str]
    preventive_measures: List[str]


class PestManagementAgent(BaseWorkerAgent):
    """
    Agent specialized in pest identification, forecasting, and management.
    
    Capabilities:
    - Pest identification from symptom descriptions
    - Treatment recommendations (biological, chemical, cultural)
    - Outbreak forecasting based on weather and seasonal patterns
    - Integrated pest management strategies
    - Prevention and early detection advice
    """
    
    def __init__(self):
        super().__init__(
            name="Pest Management Specialist",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.PLANNING,
                AgentCapability.EXECUTION
            ]
        )
        
        # Load pest knowledge base
        self._load_pest_database()
        self._load_treatment_database()
        self._load_forecast_models()
        logger.info(f"Initialized {self.name} with {len(self.pest_database)} pest entries")
    
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
    
    def _load_pest_database(self):
        """Load comprehensive pest identification database"""
        self.pest_database = {
            # Wheat Pests
            "wheat_rust": {
                "scientific_name": "Puccinia triticina",
                "pest_type": PestType.FUNGAL,
                "common_names": ["leaf rust", "brown rust", "पत्ती का किट्ट"],
                "affected_crops": [CropType.WHEAT],
                "symptoms": [
                    "orange-brown pustules on leaves",
                    "yellowing of leaves",
                    "premature leaf drop",
                    "reduced grain filling",
                    "rust-colored spores on leaf surface"
                ],
                "severity_indicators": [
                    "pustules covering >50% leaf area = severe",
                    "flag leaf affected = high",
                    "multiple tillers affected = moderate to high"
                ],
                "favorable_conditions": {
                    "temperature": (15, 25),
                    "humidity": (60, 100),
                    "rainfall": "moderate to high"
                },
                "peak_season": [SeasonType.RABI],
                "description": "Fungal disease causing rust-colored pustules on wheat leaves"
            },
            
            "aphids": {
                "scientific_name": "Rhopalosiphum padi",
                "pest_type": PestType.INSECT,
                "common_names": ["wheat aphids", "green bug", "माहू"],
                "affected_crops": [CropType.WHEAT, CropType.RICE, CropType.MAIZE],
                "symptoms": [
                    "small green insects on leaves",
                    "honeydew on plant surface",
                    "yellowing and curling of leaves",
                    "stunted plant growth",
                    "presence of ants on plants"
                ],
                "severity_indicators": [
                    ">5 aphids per tiller = economic threshold",
                    "sticky honeydew visible = moderate",
                    "ant trails present = established infestation"
                ],
                "favorable_conditions": {
                    "temperature": (20, 25),
                    "humidity": (70, 85),
                    "rainfall": "low to moderate"
                },
                "peak_season": [SeasonType.RABI, SeasonType.KHARIF],
                "description": "Small sucking insects that feed on plant sap"
            },
            
            # Rice Pests
            "blast_disease": {
                "scientific_name": "Magnaporthe oryzae",
                "pest_type": PestType.FUNGAL,
                "common_names": ["rice blast", "leaf blast", "धान का ब्लास्ट"],
                "affected_crops": [CropType.RICE],
                "symptoms": [
                    "diamond-shaped lesions on leaves",
                    "brown spots with gray centers",
                    "neck blast on panicles",
                    "node blast on stems",
                    "white/gray fungal growth"
                ],
                "severity_indicators": [
                    "neck blast = severe yield loss",
                    ">20% leaf area affected = high",
                    "multiple nodes affected = severe"
                ],
                "favorable_conditions": {
                    "temperature": (25, 28),
                    "humidity": (85, 95),
                    "rainfall": "high with intermittent dry periods"
                },
                "peak_season": [SeasonType.KHARIF],
                "description": "Devastating fungal disease of rice causing blast lesions"
            },
            
            "stem_borer": {
                "scientific_name": "Scirpophaga incertulas",
                "pest_type": PestType.INSECT,
                "common_names": ["yellow stem borer", "तना छेदक"],
                "affected_crops": [CropType.RICE],
                "symptoms": [
                    "dead hearts in young plants",
                    "white ears in mature plants",
                    "entry holes in stem",
                    "frass near stem base",
                    "easy pulling of central shoot"
                ],
                "severity_indicators": [
                    ">5% dead hearts = economic threshold",
                    "white ears present = severe damage",
                    "multiple tillers affected = high"
                ],
                "favorable_conditions": {
                    "temperature": (26, 32),
                    "humidity": (70, 85),
                    "rainfall": "moderate"
                },
                "peak_season": [SeasonType.KHARIF],
                "description": "Insect pest that bores into rice stems causing dead hearts"
            },
            
            # Cotton Pests
            "bollworm": {
                "scientific_name": "Helicoverpa armigera",
                "pest_type": PestType.INSECT,
                "common_names": ["cotton bollworm", "American bollworm", "कपास का किट्ट"],
                "affected_crops": [CropType.COTTON],
                "symptoms": [
                    "holes in cotton bolls",
                    "caterpillars inside bolls",
                    "damaged flowers and buds",
                    "frass around feeding sites",
                    "premature boll drop"
                ],
                "severity_indicators": [
                    ">2 larvae per plant = economic threshold",
                    "boll damage >10% = high",
                    "multiple bolls affected = severe"
                ],
                "favorable_conditions": {
                    "temperature": (25, 30),
                    "humidity": (60, 80),
                    "rainfall": "moderate"
                },
                "peak_season": [SeasonType.KHARIF],
                "description": "Major insect pest of cotton attacking bolls and flowers"
            },
            
            "whitefly": {
                "scientific_name": "Bemisia tabaci",
                "pest_type": PestType.INSECT,
                "common_names": ["cotton whitefly", "सफ़ेद मक्खी"],
                "affected_crops": [CropType.COTTON, CropType.TOMATO],
                "symptoms": [
                    "small white flying insects",
                    "yellowing of leaves",
                    "honeydew on leaf surface",
                    "sooty mold development",
                    "leaf curling and distortion"
                ],
                "severity_indicators": [
                    ">5 adults per leaf = economic threshold",
                    "yellowing >25% leaves = moderate",
                    "sooty mold present = established"
                ],
                "favorable_conditions": {
                    "temperature": (25, 32),
                    "humidity": (70, 85),
                    "rainfall": "low"
                },
                "peak_season": [SeasonType.KHARIF],
                "description": "Small white insect that transmits viral diseases"
            },
            
            # General Pests
            "cutworm": {
                "scientific_name": "Agrotis ipsilon",
                "pest_type": PestType.INSECT,
                "common_names": ["cutworm", "कटवर्म"],
                "affected_crops": [CropType.WHEAT, CropType.MAIZE, CropType.COTTON],
                "symptoms": [
                    "cut seedlings at soil level",
                    "plants found lying on ground",
                    "smooth cuts near soil surface",
                    "caterpillars hiding in soil during day",
                    "damage during night"
                ],
                "severity_indicators": [
                    ">5% plant cutting = economic threshold",
                    "multiple plants cut = moderate",
                    "field patches affected = high"
                ],
                "favorable_conditions": {
                    "temperature": (18, 25),
                    "humidity": (70, 85),
                    "rainfall": "moderate"
                },
                "peak_season": [SeasonType.RABI, SeasonType.KHARIF],
                "description": "Soil-dwelling caterpillar that cuts young plants at ground level"
            }
        }
    
    def _load_treatment_database(self):
        """Load treatment recommendations database"""
        self.treatment_database = {
            "wheat_rust": [
                {
                    "treatment_type": TreatmentType.CHEMICAL,
                    "method": "Fungicide spray",
                    "products": ["Propiconazole 25% EC", "Tebuconazole 250 EC"],
                    "application_timing": "At first appearance of symptoms",
                    "frequency": "2-3 sprays at 15-day intervals",
                    "dosage": "1ml per liter water",
                    "cost_estimate": 2500,
                    "effectiveness": 0.85,
                    "safety_precautions": [
                        "Use protective equipment",
                        "Avoid spraying during windy conditions",
                        "Do not spray during flowering"
                    ],
                    "environmental_impact": "moderate"
                },
                {
                    "treatment_type": TreatmentType.CULTURAL,
                    "method": "Resistant varieties",
                    "products": ["HD-2967", "PBW-725"],
                    "application_timing": "At sowing time",
                    "frequency": "Every season",
                    "dosage": "Use certified seed",
                    "cost_estimate": 500,
                    "effectiveness": 0.90,
                    "safety_precautions": [],
                    "environmental_impact": "low"
                }
            ],
            
            "aphids": [
                {
                    "treatment_type": TreatmentType.BIOLOGICAL,
                    "method": "Predator release",
                    "products": ["Ladybird beetles", "Chrysoperla carnea"],
                    "application_timing": "Early infestation stage",
                    "frequency": "Release when needed",
                    "dosage": "5000 predators per hectare",
                    "cost_estimate": 1500,
                    "effectiveness": 0.75,
                    "safety_precautions": [],
                    "environmental_impact": "very low"
                },
                {
                    "treatment_type": TreatmentType.CHEMICAL,
                    "method": "Insecticide spray",
                    "products": ["Imidacloprid 17.8% SL", "Acetamiprid 20% SP"],
                    "application_timing": "When threshold reached",
                    "frequency": "1-2 sprays as needed",
                    "dosage": "0.5ml per liter water",
                    "cost_estimate": 1800,
                    "effectiveness": 0.90,
                    "safety_precautions": [
                        "Avoid application during bee activity",
                        "Use recommended dosage only"
                    ],
                    "environmental_impact": "moderate"
                }
            ],
            
            "blast_disease": [
                {
                    "treatment_type": TreatmentType.CHEMICAL,
                    "method": "Fungicide application",
                    "products": ["Tricyclazole 75% WP", "Carbendazim 50% WP"],
                    "application_timing": "Prophylactic at tillering stage",
                    "frequency": "2-3 sprays at 10-day intervals",
                    "dosage": "0.6g per liter water",
                    "cost_estimate": 3000,
                    "effectiveness": 0.80,
                    "safety_precautions": [
                        "Rotate fungicides to prevent resistance",
                        "Spray in evening hours"
                    ],
                    "environmental_impact": "moderate"
                },
                {
                    "treatment_type": TreatmentType.CULTURAL,
                    "method": "Water management",
                    "products": ["Alternate wetting and drying"],
                    "application_timing": "Throughout crop season",
                    "frequency": "Continuous",
                    "dosage": "Maintain 2-3cm water level",
                    "cost_estimate": 0,
                    "effectiveness": 0.60,
                    "safety_precautions": [],
                    "environmental_impact": "very low"
                }
            ],
            
            "bollworm": [
                {
                    "treatment_type": TreatmentType.INTEGRATED,
                    "method": "IPM package",
                    "products": ["Pheromone traps", "NPV", "Bt spray"],
                    "application_timing": "From flower initiation",
                    "frequency": "Weekly monitoring and treatment",
                    "dosage": "As per IPM schedule",
                    "cost_estimate": 4000,
                    "effectiveness": 0.85,
                    "safety_precautions": [
                        "Monitor trap catches weekly",
                        "Use economic threshold levels"
                    ],
                    "environmental_impact": "low"
                },
                {
                    "treatment_type": TreatmentType.BIOLOGICAL,
                    "method": "Biocontrol agents",
                    "products": ["Trichogramma", "NPV", "Bt"],
                    "application_timing": "Early larval stage",
                    "frequency": "Weekly releases",
                    "dosage": "50,000 parasitoids per hectare",
                    "cost_estimate": 2500,
                    "effectiveness": 0.70,
                    "safety_precautions": [],
                    "environmental_impact": "very low"
                }
            ]
        }
    
    def _load_forecast_models(self):
        """Load pest outbreak forecasting models"""
        self.forecast_models = {
            "wheat_rust": {
                "weather_factors": {
                    "temperature": (15, 25),
                    "humidity": 80,
                    "rainfall": "moderate",
                    "wind": "present"
                },
                "seasonal_pattern": {
                    SeasonType.RABI: {
                        "high_risk_weeks": (8, 16),  # January-March
                        "peak_weeks": (12, 14)  # February
                    }
                },
                "early_warning_indicators": [
                    "Temperature 15-25°C for 5+ days",
                    "Relative humidity >80%",
                    "Light rains with sunny intervals",
                    "Reports from neighboring areas"
                ]
            },
            
            "bollworm": {
                "weather_factors": {
                    "temperature": (25, 30),
                    "humidity": 70,
                    "rainfall": "light_to_moderate"
                },
                "seasonal_pattern": {
                    SeasonType.KHARIF: {
                        "high_risk_weeks": (25, 35),  # June-August
                        "peak_weeks": (28, 32)  # July
                    }
                },
                "early_warning_indicators": [
                    "Flower initiation stage reached",
                    "Temperature 25-30°C consistently",
                    "Adult moth trap catches increasing",
                    "Previous season infestation history"
                ]
            }
        }
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """
        Process pest management related queries with satellite data integration.
        
        Args:
            query: Agriculture query object
            
        Returns:
            AgentResponse with pest identification and treatment recommendations enhanced with satellite insights
        """
        try:
            logger.info(f"Processing pest management query with satellite integration: {query.query_text}")
            
            # Extract pest-related information from query
            context = self._extract_pest_context(query)
            
            # Get satellite data if location is available
            satellite_data = None
            if context.get("location") and hasattr(context["location"], "latitude") and hasattr(context["location"], "longitude"):
                try:
                    logger.info(f"[SATELLITE] Fetching satellite data for pest analysis: {context['location'].latitude}, {context['location'].longitude}")
                    satellite_data = await get_satellite_data_for_location(
                        context["location"].latitude,
                        context["location"].longitude,
                        getattr(context["location"], "state", None)
                    )
                    logger.info(f"[SATELLITE] Satellite data retrieved for pest management")
                except Exception as e:
                    logger.warning(f"[SATELLITE] Could not fetch satellite data: {e}")
                    satellite_data = None
            
            # Enhance context with satellite data
            if satellite_data:
                context = self._enhance_context_with_satellite_data(context, satellite_data)
            
            # Identify pest based on symptoms and weather patterns
            pest_identifications = await self._identify_pest(context, satellite_data)
            
            # Generate treatment recommendations with weather considerations
            treatments = await self._recommend_treatments(pest_identifications, context, satellite_data)
            
            # Generate outbreak forecast enhanced with satellite weather data
            forecasts = await self._generate_pest_forecast(context, satellite_data)
            
            # Calculate confidence including satellite data reliability
            confidence = self._calculate_confidence(context, pest_identifications, satellite_data)
            
            # Format response data
            response_data = {
                "pest_identifications": [pest.__dict__ for pest in pest_identifications],
                "treatment_recommendations": [treatment.__dict__ for treatment in treatments],
                "outbreak_forecasts": [forecast.__dict__ for forecast in forecasts],
                "context_analysis": context,
                "satellite_insights": satellite_data,
                "confidence_score": confidence,
                "prevention_advice": self._generate_prevention_advice(context, satellite_data)
            }
            
            # Include satellite summary in sources
            sources = ["pest_database", "treatment_database", "ipm_guidelines", "weather_analysis"]
            if satellite_data:
                sources.append("satellite_data")
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Identified {len(pest_identifications)} potential pests with {len(treatments)} treatment options",
                confidence_score=confidence,
                sources=sources,
                recommendations=self._format_pest_summary(pest_identifications, treatments, satellite_data),
                metadata=response_data
            )
            
        except Exception as e:
            logger.error(f"Error processing pest management query: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                query_id=query.query_id,
                response_text=f"Error processing pest management query: {str(e)}",
                confidence_score=0.0,
                sources=[],
                recommendations=[],
                metadata={"error": str(e)}
            )
    
    def _extract_pest_context(self, query: AgricultureQuery) -> Dict[str, Any]:
        """Extract pest-related context from query"""
        context = {
            "symptoms": [],
            "crop_type": None,
            "affected_parts": [],
            "severity": None,
            "timing": None,
            "weather_conditions": None,
            "location": None,
            "query_type": "identification"  # identification, treatment, forecast
        }
        
        query_text = query.query_text.lower()
        
        # Extract crop information
        for crop_type in CropType:
            crop_names = [crop_type.value, crop_type.name.lower()]
            hindi_names = {
                CropType.WHEAT: ["gehu", "gehun"],
                CropType.RICE: ["chawal", "dhan"],
                CropType.COTTON: ["kapas"],
                CropType.MAIZE: ["makka"]
            }
            if crop_type in hindi_names:
                crop_names.extend(hindi_names[crop_type])
            
            if any(name in query_text for name in crop_names):
                context["crop_type"] = crop_type
                break
        
        # Extract symptoms
        symptom_keywords = {
            "spots": "spotted lesions",
            "yellow": "yellowing",
            "brown": "browning",
            "holes": "holes in leaves/fruits",
            "insects": "insect presence",
            "rust": "rust-colored pustules",
            "wilting": "plant wilting",
            "stunted": "stunted growth",
            "holes": "feeding holes",
            "sticky": "honeydew presence"
        }
        
        for keyword, symptom in symptom_keywords.items():
            if keyword in query_text:
                context["symptoms"].append(symptom)
        
        # Extract affected plant parts
        part_keywords = ["leaves", "stem", "fruit", "flower", "root", "boll"]
        for part in part_keywords:
            if part in query_text:
                context["affected_parts"].append(part)
        
        # Determine query type
        if any(word in query_text for word in ["spray", "treatment", "control", "manage"]):
            context["query_type"] = "treatment"
        elif any(word in query_text for word in ["forecast", "predict", "when", "outbreak"]):
            context["query_type"] = "forecast"
        
        # Extract location if available
        if query.farm_profile and query.farm_profile.location:
            context["location"] = query.farm_profile.location
        
        return context
    
    async def _identify_pest(self, context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[PestIdentification]:
        """Integrated pest identification combining AgriMitr CNN, symptom/database matching, and weather risk augmentation.
        Order of operations:
        1. Attempt AgriMitr image-based (or symptom) disease identification
        2. Match against internal pest database (legacy logic)
        3. Add weather-based elevated risk pests (humidity / temperature / soil moisture)
        4. De-duplicate and rank by confidence
        """
        pest_identifications: List[PestIdentification] = []
        added_keys = set()

        # Collect location data for AgriMitr
        location_obj = context.get("location")
        location_data = self._serialize_location(location_obj) if location_obj else None

        # Ensure symptoms list exists
        symptoms = context.get("symptoms") or []

        # Try to obtain image data
        image_data = context.get("image_data")
        if not image_data and context.get("image_base64"):
            try:
                import base64
                image_data = base64.b64decode(context["image_base64"])  # type: ignore
            except Exception:
                pass

        # Weather (from satellite) for AgriMitr severity context
        weather_data = None
        if satellite_data:
            weather = satellite_data.get("weather") or {}
            weather_data = {
                "temperature": weather.get("temperature") or satellite_data.get("temperature"),
                "humidity": weather.get("humidity") or satellite_data.get("humidity"),
                "rainfall": weather.get("rainfall") or satellite_data.get("precipitation")
            }

        # 1. AgriMitr disease identification
        try:
            AgriMitr_result = enhance_pest_management_with_disease_id(
                image_data=image_data,
                symptoms=symptoms if symptoms else None,
                crop_type=(context.get("crop_type") or "") if context.get("crop_type") else "",
                location_data=location_data,
                weather_data=weather_data
            )
            if AgriMitr_result and AgriMitr_result.confidence > 0.25:
                mapped_crop = self._map_crop_name_to_type(AgriMitr_result.crop_type)
                pest_id = PestIdentification(
                    pest_name=AgriMitr_result.disease_name,
                    pest_type=PestType.DISEASE,
                    confidence=min(1.0, AgriMitr_result.confidence + 0.05 if image_data else AgriMitr_result.confidence),
                    symptoms=AgriMitr_result.symptoms or symptoms,
                    affected_crops=[mapped_crop] if mapped_crop else [],
                    severity_indicators=[AgriMitr_result.severity_assessment],
                    common_names=[AgriMitr_result.disease_name],
                    description=f"AgriMitr identification ({'image' if image_data else 'symptom'} based)"
                )
                pest_identifications.append(pest_id)
                added_keys.add(pest_id.pest_name.lower())
        except Exception as e:
            logger.warning(f"AgriMitr identification failed: {e}")

        # 2. Internal database symptom matching (legacy logic adapted)
        try:
            for pest_name, pest_data in self.pest_database.items():
                legacy_conf = self._calculate_pest_match_confidence(pest_data, context)
                if legacy_conf > 0.30:
                    key = pest_name.lower()
                    if key in added_keys:
                        # If already present (AgriMitr match), boost confidence moderately
                        for existing in pest_identifications:
                            if existing.pest_name.lower() == key:
                                existing.confidence = min(1.0, max(existing.confidence, legacy_conf) + 0.05)
                        continue
                    pest_identifications.append(PestIdentification(
                        pest_name=pest_name,
                        pest_type=pest_data["pest_type"],
                        confidence=legacy_conf,
                        symptoms=pest_data["symptoms"],
                        affected_crops=pest_data["affected_crops"],
                        severity_indicators=pest_data["severity_indicators"],
                        common_names=pest_data["common_names"],
                        description=pest_data["description"]
                    ))
                    added_keys.add(key)
        except Exception as e:
            logger.error(f"Legacy database matching failed: {e}")

        # 3. Weather-based risk augmentation
        if satellite_data:
            self._add_weather_based_pest_risks(pest_identifications, context, satellite_data, added_keys)

        # 4. De-duplicate (already controlled), sort & trim
        pest_identifications.sort(key=lambda x: x.confidence, reverse=True)
        return pest_identifications[:5]

    async def _recommend_treatments(self, pest_identifications: List[PestIdentification], context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[TreatmentRecommendation]:
        """Generate treatment recommendations with weather & AgriMitr augmentation.
        - Pull from treatment_database
        - If AgriMitr identification present but not in DB, add generic disease management steps
        - Adjust timing & safety based on satellite weather
        """
        treatments: List[TreatmentRecommendation] = []
        if not pest_identifications:
            return treatments

        weather = (satellite_data or {}).get("weather", {})
        humidity = weather.get("humidity") or satellite_data.get("humidity") if satellite_data else None
        wind_speed = weather.get("wind_speed") or satellite_data.get("wind_speed") if satellite_data else None

        for pest in pest_identifications[:3]:  # limit top pests
            if pest.pest_name in self.treatment_database:
                for t_data in self.treatment_database[pest.pest_name]:
                    treatment = TreatmentRecommendation(
                        treatment_type=t_data["treatment_type"],
                        method=t_data["method"],
                        products=t_data["products"],
                        application_timing=t_data["application_timing"],
                        frequency=t_data["frequency"],
                        dosage=t_data["dosage"],
                        cost_estimate=t_data["cost_estimate"],
                        effectiveness=t_data["effectiveness"],
                        safety_precautions=list(t_data["safety_precautions"]),
                        environmental_impact=t_data["environmental_impact"]
                    )
                    self._augment_treatments_with_weather(treatment, humidity, wind_speed)
                    treatments.append(treatment)
            else:
                # Generic disease management (for AgriMitr diseases not in DB)
                generic = TreatmentRecommendation(
                    treatment_type=TreatmentType.INTEGRATED,
                    method="Integrated disease management (sanitation + resistant varieties + preventive spray)",
                    products=["Copper-based fungicide", "Neem oil"],
                    application_timing="At first sign; morning hours if humidity high",
                    frequency="Repeat every 10-14 days if conditions persist",
                    dosage="As per label (rotate actives)",
                    cost_estimate=2000,
                    effectiveness=0.65,
                    safety_precautions=["Use PPE", "Rotate fungicide groups"],
                    environmental_impact="moderate"
                )
                self._augment_treatments_with_weather(generic, humidity, wind_speed)
                treatments.append(generic)

        # Rank (effectiveness, then lower environmental impact) & limit
        treatments.sort(key=lambda x: (x.effectiveness, -1 if x.environmental_impact in ["low", "very low", "positive"] else 0), reverse=True)
        return treatments[:6]

    async def _generate_pest_forecast(self, context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[PestForecast]:
        """Weather & season enhanced outbreak forecasts.
        Adjust base seasonal model with humidity/temperature multipliers from satellite data.
        """
        forecasts: List[PestForecast] = []
        if not (context.get("crop_type") or context.get("query_type") == "forecast"):
            return forecasts

        current_week = datetime.now().isocalendar()[1]
        humidity = None
        temperature = None
        if satellite_data:
            w = satellite_data.get("weather", {})
            humidity = w.get("humidity") or satellite_data.get("humidity")
            temperature = w.get("temperature") or satellite_data.get("temperature")

        for pest_name, model in self.forecast_models.items():
            # Crop relevance
            pest_data = self.pest_database.get(pest_name)
            if context.get("crop_type") and pest_data and context["crop_type"] not in pest_data.get("affected_crops", []):
                continue
            base_risk = self._calculate_outbreak_risk(model, current_week)
            probability = self._calculate_outbreak_probability(model, current_week)

            # Weather adjustments
            if humidity is not None:
                if humidity > 80 and base_risk in [SeverityLevel.MODERATE, SeverityLevel.HIGH]:
                    probability = min(1.0, probability + 0.1)
                elif humidity < 40:
                    probability = max(0.1, probability - 0.1)
            if temperature is not None:
                # Light adjustment: extreme temps reduce risk
                if temperature < 12 or temperature > 38:
                    probability = max(0.1, probability - 0.15)

            # Map probability back to risk
            if probability >= 0.75:
                risk_level = SeverityLevel.HIGH
            elif probability >= 0.5:
                risk_level = SeverityLevel.MODERATE
            else:
                risk_level = SeverityLevel.LOW

            if risk_level != SeverityLevel.LOW:
                peak_weeks = list(model["seasonal_pattern"].values())[0]["peak_weeks"]
                forecasts.append(PestForecast(
                    pest_name=pest_name,
                    risk_level=risk_level,
                    outbreak_probability=round(probability, 2),
                    peak_activity_period=peak_weeks,
                    weather_factors=model.get("early_warning_indicators", []),
                    preventive_measures=self._get_preventive_measures(pest_name)
                ))
        return forecasts[:4]

    def _calculate_confidence(self, context: Dict[str, Any], pest_identifications: List[PestIdentification], satellite_data: Optional[Dict] = None) -> float:
        """Composite confidence using:
        - Symptom detail
        - Top pest confidence (legacy or AgriMitr)
        - Satellite data quality (presence & key fields)
        - Image contribution
        """
        confidence = 0.30  # base

        if context.get("symptoms"):
            confidence += 0.15 if len(context["symptoms"]) >= 2 else 0.08
        if pest_identifications:
            top = pest_identifications[0]
            confidence += min(0.30, top.confidence * 0.30)
        if satellite_data:
            confidence += 0.10 * self._estimate_satellite_data_quality(satellite_data)
        if context.get("image_data") or context.get("image_base64"):
            confidence += 0.10
        if context.get("crop_type"):
            confidence += 0.05
        return round(min(confidence, 0.95), 2)

    def _generate_prevention_advice(self, context: Dict[str, Any], satellite_data: Optional[Dict] = None) -> List[str]:
        """Merge generic, crop-specific, AgriMitr (if any), and weather-based preventive guidance."""
        advice = [
            "Regular scouting 2-3 times per week",
            "Rotate crops to break pest cycles",
            "Remove and destroy infected residues",
            "Avoid excessive nitrogen which encourages aphids & disease",
            "Maintain balanced irrigation to reduce fungal pressure"
        ]
        crop = context.get("crop_type")
        if crop == CropType.WHEAT:
            advice.append("Use rust-resistant varieties; early sowing reduces aphid pressure")
        elif crop == CropType.RICE:
            advice.append("Maintain proper water management to limit blast risk")
        elif crop == CropType.COTTON:
            advice.append("Deploy pheromone traps early for bollworm monitoring")

        if satellite_data:
            w = satellite_data.get("weather", {})
            h = w.get("humidity") or satellite_data.get("humidity")
            if h and h > 75:
                advice.append("High humidity detected – schedule preventive fungicide sprays in morning hours")
            sm = satellite_data.get("soil_moisture")
            if sm and sm > 0.8:
                advice.append("Excess soil moisture – improve drainage to reduce root & fungal diseases")
        return advice[:8]

    def _format_pest_summary(self, pest_identifications: List[PestIdentification], treatments: List[TreatmentRecommendation], satellite_data: Optional[Dict] = None) -> List[str]:
        """Concise summary list for UI display."""
        summary: List[str] = []
        if pest_identifications:
            top = pest_identifications[0]
            summary.append(f"Top suspect: {top.pest_name} ({top.confidence:.0%})")
            if len(pest_identifications) > 1:
                others = ", ".join(p.pest_name for p in pest_identifications[1:3])
                summary.append(f"Other possibilities: {others}")
        if treatments:
            best = treatments[0]
            summary.append(f"Primary treatment: {best.method} (est. effectiveness {best.effectiveness:.0%})")
        if satellite_data:
            summary.append("Satellite weather integrated into risk & timing")
        return summary[:4]

    # ----------------- Helper Methods (AgriMitr & Weather Integration) -----------------
    def _map_crop_name_to_type(self, crop_name: str) -> Optional[CropType]:
        if not crop_name:
            return None
        name = crop_name.lower()
        mapping = {
            "wheat": CropType.WHEAT,
            "rice": CropType.RICE,
            "maize": CropType.MAIZE,
            "corn": CropType.MAIZE,
            "cotton": CropType.COTTON,
            "tomato": CropType.VEGETABLES,
            "potato": CropType.VEGETABLES,
            "apple": CropType.FRUITS,
            "grape": CropType.FRUITS
        }
        return mapping.get(name, CropType.OTHER)

    def _serialize_location(self, location: Any) -> Dict[str, Any]:  # type: ignore
        if not location:
            return {}
        return {
            "state": getattr(location, "state", None),
            "district": getattr(location, "district", None),
            "latitude": getattr(location, "latitude", None),
            "longitude": getattr(location, "longitude", None)
        }

    def _add_weather_based_pest_risks(self, pest_identifications: List[PestIdentification], context: Dict[str, Any], satellite_data: Dict, added_keys: set):
        """Augment identifications with pests favored by current weather (simple heuristic)."""
        weather = satellite_data.get("weather", {})
        humidity = weather.get("humidity") or satellite_data.get("humidity", 0)
        temperature = weather.get("temperature") or satellite_data.get("temperature", 0)
        soil_moisture = satellite_data.get("soil_moisture", 0)

        # Fungal disease boost
        if humidity and humidity > 80 and context.get("crop_type") in [CropType.WHEAT, CropType.RICE, CropType.COTTON]:
            candidate = "wheat_rust" if context.get("crop_type") == CropType.WHEAT else "blast_disease" if context.get("crop_type") == CropType.RICE else None
            if candidate and candidate in self.pest_database and candidate not in added_keys:
                pdata = self.pest_database[candidate]
                pest_identifications.append(PestIdentification(
                    pest_name=candidate,
                    pest_type=pdata["pest_type"],
                    confidence=0.45,
                    symptoms=pdata["symptoms"],
                    affected_crops=pdata["affected_crops"],
                    severity_indicators=pdata["severity_indicators"],
                    common_names=pdata["common_names"],
                    description="Weather-risk augmented (high humidity)"
                ))
                added_keys.add(candidate)

        # High soil moisture -> root/stem fungal risks (generic)
        if soil_moisture and soil_moisture > 0.85 and "soil_root_fungal" not in added_keys:
            pest_identifications.append(PestIdentification(
                pest_name="Root/Stem Fungal Risk",
                pest_type=PestType.FUNGAL,
                confidence=0.35,
                symptoms=context.get("symptoms", []),
                affected_crops=[context.get("crop_type")] if context.get("crop_type") else [],
                severity_indicators=["Prolonged saturated soil"],
                common_names=["Soil fungus"],
                description="Weather-risk augmented (excess moisture)"
            ))
            added_keys.add("soil_root_fungal")

        # Temperature driven insect surge
        if temperature and 24 <= temperature <= 32 and context.get("crop_type") == CropType.COTTON and "bollworm" not in added_keys:
            pdata = self.pest_database.get("bollworm")
            if pdata:
                pest_identifications.append(PestIdentification(
                    pest_name="bollworm",
                    pest_type=pdata["pest_type"],
                    confidence=0.40,
                    symptoms=pdata["symptoms"],
                    affected_crops=pdata["affected_crops"],
                    severity_indicators=pdata["severity_indicators"],
                    common_names=pdata["common_names"],
                    description="Weather-risk augmented (favorable temperature)"
                ))
                added_keys.add("bollworm")

    def _augment_treatments_with_weather(self, treatment: TreatmentRecommendation, humidity: Optional[float], wind_speed: Optional[float]):
        """Adjust timing / precautions based on humidity & wind."""
        if humidity and humidity > 80:
            treatment.application_timing += " (prefer morning dry window)"
            if "Avoid spraying during high humidity" not in treatment.safety_precautions:
                treatment.safety_precautions.append("Avoid spraying during peak humidity periods")
        if wind_speed and wind_speed > 15:
            if "Avoid spraying in high winds" not in treatment.safety_precautions:
                treatment.safety_precautions.append("Avoid spraying in high winds (drift risk)")

    def _estimate_satellite_data_quality(self, satellite_data: Dict[str, Any]) -> float:
        """Rough quality metric 0-1 based on presence of key fields."""
        keys = ["weather", "soil_moisture", "ndvi"]
        present = sum(1 for k in keys if k in satellite_data and satellite_data.get(k) is not None)
        return present / len(keys)
