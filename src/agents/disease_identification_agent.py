"""
Disease Identification Agent
Specialized agent for detecting and diagnosing plant diseases from images using AgriMitr AI models.
Provides treatment recommendations and prevention strategies.
"""

import logging
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import re

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..models.AgriMitr_disease_identification import (
    AgriMitrDiseaseModel, DiseaseIdentificationResult, 
    load_disease_model, preprocess_image, get_disease_details,
    identify_disease_from_symptoms
)
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType,
    WeatherData, Location, FarmProfile, QueryDomain, AgricultureCapability
)

logger = logging.getLogger(__name__)


class DiseaseIdentificationAgent(BaseWorkerAgent):
    """
    Agent for identifying crop diseases from images and providing treatment recommendations
    using AgriMitr CNN models for 38 diseases across 14 crops
    
    Capabilities:
    - Image-based disease identification using CNN models
    - Text-based symptom analysis for disease identification
    - Treatment and prevention recommendations
    - Integration with satellite data for enhanced recommendations
    - Multiple image processing
    """
    
    def __init__(self, agent_id: str = "disease_specialist", name: str = "Disease Identification Specialist"):
        """Initialize the disease identification agent"""
        super().__init__(agent_id, name)
        self.model = None
        self._supported_crops = set([crop.value for crop in CropType])
        self._capabilities = [
            AgricultureCapability.PEST_IDENTIFICATION,
            AgricultureCapability.MULTILINGUAL_NLP
        ]
        self.symptom_patterns = self._compile_symptom_patterns()
    
    def _compile_symptom_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for common disease symptoms"""
        return {
            "leaf_spot": [
                re.compile(r"(?i)\b(spot|spots|धब्बे|दाग)\b"),
                re.compile(r"(?i)\b(brown|yellow|black|white)\s+(spot|spots|lesion|lesions)\b"),
            ],
            "blight": [
                re.compile(r"(?i)\b(blight|झुलसा|झुलस)\b"),
                re.compile(r"(?i)\b(early|late)\s+blight\b")
            ],
            "rust": [
                re.compile(r"(?i)\b(rust|रस्ट|जंग)\b"),
                re.compile(r"(?i)\b(orange|brown|red)\s+(pustule|pustules)\b")
            ],
            "mildew": [
                re.compile(r"(?i)\b(mildew|फफूंदी|फफूंद)\b"),
                re.compile(r"(?i)\b(downy|powdery)\s+mildew\b"),
                re.compile(r"(?i)\b(white|gray)\s+powder\b")
            ],
            "wilt": [
                re.compile(r"(?i)\b(wilt|wilting|मुरझाना|मुरझा)\b"),
                re.compile(r"(?i)\b(drooping|droop|सूखना)\b")
            ],
            "mosaic": [
                re.compile(r"(?i)\b(mosaic|मोज़ेक|चितकबरा)\b"),
                re.compile(r"(?i)\b(mottling|mottled|धब्बेदार)\b")
            ],
            "rot": [
                re.compile(r"(?i)\b(rot|सड़न|सड़ना)\b"),
                re.compile(r"(?i)\b(fruit|root|stem|crown)\s+rot\b")
            ]
        }
    
    def initialize(self):
        """Load the disease identification model"""
        logger.info("Loading AgriMitr disease identification model...")
        self.model = load_disease_model()
        logger.info("Disease identification agent initialized successfully")
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [cap.value for cap in self._capabilities]
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a disease identification query with support for both image and text-based queries"""
        logger.info(f"Processing disease identification query: {query.query_text}")
        
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="disease_identification",
            message="Processing disease identification query",
            data={}
        )
        
        try:
            # Check if we have image data for visual identification
            if query.image_data:
                return await self._process_image_query(query)
            
            # If no image, attempt text-based symptom analysis
            elif query.query_text:
                return await self._process_text_query(query)
            
            # No image or useful text
            else:
                response.message = "Please provide an image of the affected plant or describe the symptoms"
                return response
                
        except Exception as e:
            logger.error(f"Error in disease identification: {e}", exc_info=True)
            response.message = f"Error processing disease identification: {str(e)}"
        
        return response
    
    async def _process_image_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process image-based disease identification query"""
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="disease_identification",
            message="Processing image for disease identification",
            data={}
        )
        
        try:
            # Process the image and identify disease
            image_data = base64.b64decode(query.image_data)
            result = self._identify_disease(image_data, query.crop_type)
            
            # Get satellite data if location is available
            satellite_data = await self._get_satellite_data(query.location)
            
            # Generate treatment and prevention recommendations
            recommendations = self._generate_recommendations(
                result.disease_name, 
                result.confidence,
                query.crop_type, 
                query.soil_type,
                satellite_data
            )
            
            response.success = True
            response.message = f"Detected {result.disease_name} with {result.confidence:.2f}% confidence"
            response.data = {
                "disease": result.disease_name,
                "confidence": result.confidence,
                "affected_area_percentage": result.affected_area_percentage,
                "severity": result.severity,
                "recommendations": recommendations,
                "satellite_data": format_satellite_summary(satellite_data) if satellite_data else None,
                "identification_method": "image_analysis",
                "supported_crops": list(self._supported_crops)[:10] + ["...and more"]  # First 10 for brevity
            }
            
        except Exception as e:
            logger.error(f"Error in image-based disease identification: {e}", exc_info=True)
            response.message = f"Error processing disease image: {str(e)}"
        
        return response
    
    async def _process_text_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process text-based disease identification from symptom description"""
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="disease_identification",
            message="Processing symptom description",
            data={}
        )
        
        try:
            # Extract symptoms and crop information from query
            symptoms = self._extract_symptoms_from_text(query.query_text)
            crop_type = query.crop_type or self._extract_crop_from_text(query.query_text)
            
            if not symptoms:
                response.message = "Could not identify specific disease symptoms in your description. Please provide more details about the symptoms you're observing."
                response.data = {
                    "identification_method": "text_analysis",
                    "symptom_examples": [
                        "yellow spots on leaves", 
                        "wilting plants",
                        "white powdery coating",
                        "brown lesions",
                        "curling leaves"
                    ]
                }
                return response
                
            # Identify disease from symptoms
            result = identify_disease_from_symptoms(symptoms, crop_type)
            
            # Get satellite data if location is available
            satellite_data = await self._get_satellite_data(query.location)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                result.disease_name, 
                result.confidence,
                crop_type, 
                query.soil_type,
                satellite_data
            )
            
            response.success = True
            response.message = f"Based on the symptoms described, detected possible {result.disease_name} with {result.confidence:.2f}% confidence"
            response.data = {
                "disease": result.disease_name,
                "confidence": result.confidence,
                "identified_symptoms": symptoms,
                "recommendations": recommendations,
                "satellite_data": format_satellite_summary(satellite_data) if satellite_data else None,
                "identification_method": "symptom_analysis",
                "note": "For more accurate diagnosis, consider uploading an image of the affected plant."
            }
            
        except Exception as e:
            logger.error(f"Error in text-based disease identification: {e}", exc_info=True)
            response.message = f"Error processing symptoms: {str(e)}"
        
        return response
    
    async def _get_satellite_data(self, location: Optional[Location]) -> Optional[Dict[str, Any]]:
        """Get satellite data for the location if available"""
        if not location or not location.latitude or not location.longitude:
            return None
            
        try:
            return await get_satellite_data_for_location(
                location.latitude,
                location.longitude
            )
        except Exception as e:
            logger.warning(f"Failed to get satellite data: {e}")
            return None
    
    def _extract_symptoms_from_text(self, query_text: str) -> List[str]:
        """Extract disease symptoms from the query text"""
        symptoms = []
        
        for symptom_type, patterns in self.symptom_patterns.items():
            for pattern in patterns:
                if pattern.search(query_text):
                    # Find the matching context around the symptom
                    matches = pattern.finditer(query_text)
                    for match in matches:
                        start = max(0, match.start() - 20)
                        end = min(len(query_text), match.end() + 20)
                        context = query_text[start:end].strip()
                        symptoms.append(context)
        
        # If no specific symptoms found but query is about disease
        if not symptoms and re.search(r"(?i)\b(disease|बीमारी|रोग|infection|problem)\b", query_text):
            # Extract a portion of the query that may contain symptoms
            symptoms = [query_text]
        
        return symptoms
    
    def _extract_crop_from_text(self, query_text: str) -> Optional[str]:
        """Extract crop information from query text"""
        for crop in self._supported_crops:
            if re.search(fr"\b{crop}\b", query_text, re.IGNORECASE):
                return crop
        return None
    
    def _identify_disease(self, image_data: bytes, crop_type: Optional[str] = None) -> DiseaseIdentificationResult:
        """
        Process image and identify disease using AgriMitr model
        
        Args:
            image_data: Raw image data bytes
            crop_type: Optional crop type to narrow disease scope
            
        Returns:
            DiseaseIdentificationResult object with disease details
        """
        if self.model is None:
            self.initialize()
            
        # Preprocess image for the model
        processed_image = preprocess_image(image_data)
        
        # Get model prediction
        predictions = self.model.predict(processed_image)
        result = self.model.interpret_prediction(predictions[0], crop_type)
        
        # Get disease details like symptoms, causes
        disease_details = get_disease_details(result.disease_name)
        result.disease_details = disease_details
        
        return result
    
    def _generate_recommendations(
        self, 
        disease: str, 
        confidence: float,
        crop_type: Optional[str] = None,
        soil_type: Optional[str] = None,
        satellite_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate treatment and prevention recommendations
        
        Args:
            disease: Identified disease
            confidence: Confidence level of identification
            crop_type: Type of crop
            soil_type: Type of soil
            satellite_data: Optional satellite data for enhanced recommendations
            
        Returns:
            Dictionary with treatment and prevention recommendations
        """
        # Get disease details which include standard treatments
        disease_details = get_disease_details(disease)
        
        # Default recommendations
        recommendations = {
            "treatment": disease_details.get("treatments", [
                "Consult a local agricultural extension specialist",
                "Remove and destroy infected plant parts"
            ]),
            "prevention": disease_details.get("prevention", [
                "Practice crop rotation",
                "Use disease-resistant varieties",
                "Ensure proper spacing for air circulation"
            ]),
            "organic_options": disease_details.get("organic_treatments", [
                "Neem oil spray",
                "Copper-based fungicides (if applicable)"
            ]),
            "chemical_options": disease_details.get("chemical_treatments", [])
        }
        
        # Enhance recommendations with satellite data if available
        if satellite_data:
            moisture = satellite_data.get("soil_moisture", {}).get("value")
            rainfall = satellite_data.get("precipitation", {}).get("recent_mm")
            
            # Adjust recommendations based on moisture conditions
            if moisture and moisture > 80:
                recommendations["prevention"].append("Improve drainage to reduce moisture levels")
                recommendations["treatment"].append("Allow soil to dry between waterings")
            
            if rainfall and rainfall > 50:  # Heavy rain in last period
                recommendations["treatment"].append(
                    "Consider protective covering during rainy periods"
                )
        
        return recommendations
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other agents"""
        if message.get("type") == "disease_check_request":
            # Handle requests from other agents to analyze disease data
            if "image_data" in message:
                try:
                    result = self._identify_disease(
                        base64.b64decode(message["image_data"]),
                        message.get("crop_type")
                    )
                    return {
                        "success": True,
                        "disease": result.disease_name,
                        "confidence": result.confidence,
                        "severity": result.severity,
                        "details": result.disease_details
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
            # Handle symptom-based disease identification requests
            elif "symptoms" in message:
                try:
                    result = identify_disease_from_symptoms(
                        message["symptoms"],
                        message.get("crop_type")
                    )
                    return {
                        "success": True,
                        "disease": result.disease_name,
                        "confidence": result.confidence,
                        "details": result.disease_details
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
            else:
                return {"success": False, "error": "No image or symptoms provided"}
                
        return {"success": False, "error": "Unknown message type"}
