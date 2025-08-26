"""
Smart Farming Guidance Agent
Specialized agent providing best practices, planting schedules, and sustainable farming recommendations
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..models.AgriMitr_crop_recommendation import get_optimal_planting_schedule
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType,
    WeatherData, Location, FarmProfile, QueryDomain, AgricultureCapability
)

logger = logging.getLogger(__name__)

class SmartFarmingGuidanceAgent(BaseWorkerAgent):
    """
    Agent for providing best practices and guidance for sustainable and efficient farming
    
    Capabilities:
    - Planting schedule recommendations
    - Sustainable farming practices
    - Crop rotation advice
    - Water conservation techniques
    - Integrated pest management guidance
    """
    
    def __init__(self, agent_id: str = "smart_farming_guidance_agent", name: str = "Smart Farming Guide"):
        """Initialize the smart farming guidance agent"""
        super().__init__(agent_id, name)
        self._capabilities = [
            AgricultureCapability.CROP_RECOMMENDATION,
            AgricultureCapability.HARVEST_OPTIMIZATION,
            AgricultureCapability.IRRIGATION_PLANNING
        ]
        self.best_practices_db = self._load_best_practices()
        
    def _load_best_practices(self) -> Dict[str, Any]:
        """Load best practices database"""
        # In production, this would load from a file or database
        return {
            "crop_rotation": {
                "title": "Crop Rotation Best Practices",
                "description": "Crop rotation is the practice of growing different types of crops in the same area across different growing seasons.",
                "benefits": [
                    "Prevents soil depletion",
                    "Reduces pest and disease problems",
                    "Improves soil structure and fertility",
                    "Controls weeds"
                ],
                "techniques": [
                    "Three-year rotation system (legumes, leaf crops, root crops)",
                    "Include cover crops between main crops",
                    "Alternate shallow and deep-rooted crops",
                    "Consider nutrient demands of each crop in sequence"
                ],
                "common_sequences": {
                    "wheat_based": ["wheat", "legumes", "maize"],
                    "rice_based": ["rice", "pulses", "vegetables"],
                    "cotton_based": ["cotton", "chickpea", "sorghum"]
                }
            },
            "water_conservation": {
                "title": "Water Conservation Techniques",
                "description": "Efficient water management is crucial for sustainable agriculture, especially in water-scarce regions.",
                "benefits": [
                    "Reduces water usage",
                    "Lowers irrigation costs",
                    "Prevents soil erosion",
                    "Minimizes environmental impact"
                ],
                "techniques": [
                    "Drip irrigation for row crops",
                    "Mulching to reduce evaporation",
                    "Rainwater harvesting",
                    "Conservation tillage",
                    "Scheduling irrigation based on crop water requirements",
                    "Using soil moisture sensors"
                ]
            },
            "sustainable_pest_management": {
                "title": "Integrated Pest Management (IPM)",
                "description": "IPM combines different pest control methods to minimize economic, health and environmental risks.",
                "benefits": [
                    "Reduces pesticide use",
                    "Preserves beneficial insects",
                    "More cost-effective in long term",
                    "Reduces pesticide resistance"
                ],
                "techniques": [
                    "Regular monitoring of crops for pests",
                    "Use of pest-resistant crop varieties",
                    "Biological control with natural predators",
                    "Physical controls like traps and barriers",
                    "Targeted pesticide application only when necessary"
                ]
            },
            "soil_health": {
                "title": "Soil Health Management",
                "description": "Maintaining soil health is fundamental to sustainable agriculture and improved productivity.",
                "benefits": [
                    "Improves water retention",
                    "Enhances nutrient availability",
                    "Reduces erosion",
                    "Supports beneficial soil organisms"
                ],
                "techniques": [
                    "Regular soil testing",
                    "Addition of organic matter through compost",
                    "Minimal tillage practices",
                    "Cover cropping during fallow periods",
                    "Green manuring",
                    "Balanced fertilizer application"
                ]
            },
            "climate_smart_agriculture": {
                "title": "Climate-Smart Agriculture",
                "description": "Farming approaches that help adapt to climate change while reducing greenhouse gas emissions.",
                "benefits": [
                    "Increases resilience to climate variability",
                    "Reduces agriculture's carbon footprint",
                    "Improves sustainability",
                    "Often increases productivity"
                ],
                "techniques": [
                    "Drought-tolerant crop varieties",
                    "Diversified farming systems",
                    "Agroforestry integration",
                    "Efficient water management",
                    "Reduced synthetic fertilizer use",
                    "Improved livestock management"
                ]
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [cap.value for cap in self._capabilities]
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a smart farming guidance query"""
        logger.info(f"Processing smart farming guidance query: {query.query_text}")
        
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="smart_farming_guidance",
            message="Processing smart farming guidance request",
            data={}
        )
        
        try:
            # Identify the guidance category requested
            guidance_type = self._identify_guidance_type(query.query_text)
            
            # Get location-specific guidance if available
            satellite_data = None
            if query.location:
                try:
                    satellite_data = await get_satellite_data_for_location(
                        query.location.latitude,
                        query.location.longitude
                    )
                except Exception as e:
                    logger.warning(f"Failed to get satellite data: {e}")
            
            # Generate guidance based on query
            guidance = self._generate_guidance(
                guidance_type,
                query.query_text,
                query.crop_type,
                query.soil_type,
                query.location,
                satellite_data
            )
            
            response.success = True
            response.message = f"Smart farming guidance on {guidance['title']}"
            response.data = guidance
            
        except Exception as e:
            logger.error(f"Error generating farming guidance: {e}", exc_info=True)
            response.message = f"Error generating farming guidance: {str(e)}"
        
        return response
    
    def _identify_guidance_type(self, query_text: str) -> str:
        """Identify the type of guidance requested from the query text"""
        query_lower = query_text.lower()
        
        if re.search(r"(?i)\b(rotation|sequence|after|before|previous|next crop)\b", query_lower):
            return "crop_rotation"
        elif re.search(r"(?i)\b(water|irrigation|moisture|dry|drought|conserve|drip|sprinkler)\b", query_lower):
            return "water_conservation"
        elif re.search(r"(?i)\b(pest|disease|insect|fungus|control|spray|ipm|integrated)\b", query_lower):
            return "sustainable_pest_management"
        elif re.search(r"(?i)\b(soil|health|fertility|organic|matter|carbon|erosion|compost)\b", query_lower):
            return "soil_health"
        elif re.search(r"(?i)\b(climate|weather|adapt|sustainable|carbon|emission|resilient)\b", query_lower):
            return "climate_smart_agriculture"
        else:
            # Default to comprehensive guidance
            return "comprehensive"
    
    def _generate_guidance(
        self,
        guidance_type: str,
        query_text: str,
        crop_type: Optional[str] = None,
        soil_type: Optional[str] = None,
        location: Optional[Location] = None,
        satellite_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate smart farming guidance based on query and context"""
        
        if guidance_type == "comprehensive":
            # For general queries, provide overview of multiple practices
            return self._generate_comprehensive_guidance(crop_type, location)
        
        # Get the specific guidance requested
        guidance_data = self.best_practices_db.get(guidance_type, {})
        if not guidance_data:
            return {
                "title": "General Farming Best Practices",
                "description": "Sustainable farming techniques that improve productivity while protecting resources.",
                "recommendations": [
                    "Practice crop rotation to prevent soil depletion",
                    "Use efficient water management techniques",
                    "Implement integrated pest management",
                    "Maintain soil health through organic inputs",
                    "Consider climate-smart agricultural approaches"
                ],
                "guidance_type": "general"
            }
        
        # Customize guidance based on crop type
        crop_specific_recommendations = []
        if crop_type:
            crop_specific_recommendations = self._get_crop_specific_guidance(crop_type, guidance_type)
        
        # Customize guidance based on location
        location_recommendations = []
        if location:
            location_recommendations = self._get_location_specific_guidance(location, guidance_type, satellite_data)
        
        # Combine recommendations
        all_recommendations = guidance_data.get("techniques", []) + crop_specific_recommendations + location_recommendations
        
        # Return structured guidance
        return {
            "title": guidance_data.get("title", "Farming Best Practices"),
            "description": guidance_data.get("description", "Sustainable farming guidance"),
            "benefits": guidance_data.get("benefits", []),
            "recommendations": list(set(all_recommendations)),  # Remove duplicates
            "guidance_type": guidance_type,
            "crop_specific": len(crop_specific_recommendations) > 0,
            "location_specific": len(location_recommendations) > 0
        }
    
    def _generate_comprehensive_guidance(
        self, 
        crop_type: Optional[str] = None,
        location: Optional[Location] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive farming guidance overview"""
        
        recommendations = []
        
        # Add general recommendations
        recommendations.extend([
            "Practice crop rotation to break pest cycles and improve soil health",
            "Implement regular soil testing to optimize fertilizer application",
            "Use water conservation techniques appropriate for your region",
            "Integrate beneficial insects and natural predators for pest management",
            "Maintain soil organic matter through incorporation of crop residues and compost"
        ])
        
        # Add crop-specific recommendations if crop is specified
        if crop_type:
            # Get planting schedule if crop and location available
            if location:
                try:
                    planting_schedule = get_optimal_planting_schedule(crop_type, location)
                    recommendations.append(f"Optimal planting window: {planting_schedule}")
                except:
                    pass
                    
            if crop_type.lower() in ["rice", "paddy"]:
                recommendations.extend([
                    "Consider System of Rice Intensification (SRI) for improved yields with less water",
                    "Use Alternate Wetting and Drying (AWD) irrigation to reduce water use",
                    "Select varieties resistant to common diseases in your area"
                ])
            elif crop_type.lower() in ["wheat", "gehun"]:
                recommendations.extend([
                    "Time sowing to avoid terminal heat stress during grain filling",
                    "Practice zero tillage to conserve soil moisture",
                    "Monitor for rust diseases, especially in humid conditions"
                ])
            elif crop_type.lower() in ["cotton", "kapas"]:
                recommendations.extend([
                    "Implement IPM strategies to reduce dependence on insecticides",
                    "Use trap crops to manage bollworm populations",
                    "Practice high-density planting for improved yields"
                ])
        
        # Add location-specific guidance if available
        if location:
            state = location.state.lower() if location.state else ""
            
            if "punjab" in state or "haryana" in state:
                recommendations.extend([
                    "Consider diversification beyond rice-wheat rotation",
                    "Adopt precision nutrient management to address declining soil fertility",
                    "Manage crop residues without burning to improve air quality and soil health"
                ])
            elif "maharashtra" in state or "gujarat" in state:
                recommendations.extend([
                    "Implement drought-resistant farming techniques",
                    "Prioritize water harvesting structures for rainfall conservation",
                    "Consider intercropping with pulses for nitrogen fixation and risk mitigation"
                ])
            elif "kerala" in state or "tamil nadu" in state:
                recommendations.extend([
                    "Practice agroforestry to maximize land use efficiency",
                    "Implement raised bed farming in flood-prone areas",
                    "Use bio-fertilizers to enhance soil microbial activity in humid conditions"
                ])
        
        return {
            "title": "Comprehensive Smart Farming Guide",
            "description": "Holistic approach to sustainable and productive agriculture",
            "recommendations": recommendations,
            "guidance_type": "comprehensive",
            "categories": list(self.best_practices_db.keys()),
            "crop_specific": crop_type is not None,
            "location_specific": location is not None
        }
    
    def _get_crop_specific_guidance(self, crop_type: str, guidance_type: str) -> List[str]:
        """Get crop-specific recommendations for the given guidance type"""
        crop_lower = crop_type.lower()
        recommendations = []
        
        if guidance_type == "crop_rotation":
            if crop_lower in ["wheat", "gehun"]:
                recommendations.extend([
                    "Follow wheat with legumes like mung bean or cowpea",
                    "Consider short-duration pulses in summer fallow",
                    "Rice-wheat-mung bean is a sustainable rotation"
                ])
            elif crop_lower in ["rice", "paddy", "dhan"]:
                recommendations.extend([
                    "Follow rice with mustard, potato or wheat",
                    "Incorporate green manure crops like Sesbania in rotation",
                    "Consider rice-potato-mung bean rotation for diversification"
                ])
            elif crop_lower in ["cotton", "kapas"]:
                recommendations.extend([
                    "Follow cotton with chickpea for nitrogen fixation",
                    "Consider maize or sorghum in rotation with cotton",
                    "Intercrop cotton with pulses during early growth"
                ])
                
        elif guidance_type == "water_conservation":
            if crop_lower in ["rice", "paddy", "dhan"]:
                recommendations.extend([
                    "Implement Alternate Wetting and Drying (AWD) technique",
                    "Consider direct seeded rice to reduce water use",
                    "Level fields precisely for efficient water distribution"
                ])
            elif crop_lower in ["wheat", "gehun"]:
                recommendations.extend([
                    "Schedule irrigation at critical growth stages (CRI, tillering, flowering)",
                    "Use zero tillage to conserve soil moisture",
                    "Mulch with previous crop residues to reduce evaporation"
                ])
            elif crop_lower in ["sugarcane", "ganna"]:
                recommendations.extend([
                    "Implement drip irrigation with fertigation",
                    "Practice trash mulching between rows",
                    "Use skip-furrow irrigation technique"
                ])
                
        elif guidance_type == "sustainable_pest_management":
            if crop_lower in ["cotton", "kapas"]:
                recommendations.extend([
                    "Monitor for bollworms using pheromone traps",
                    "Use neem-based formulations for early-stage pest control",
                    "Implement border trap crops like marigold or okra"
                ])
            elif crop_lower in ["rice", "paddy", "dhan"]:
                recommendations.extend([
                    "Use light traps to monitor and control stem borers",
                    "Encourage natural predators like spiders and dragonflies",
                    "Time planting to avoid peak pest pressure periods"
                ])
                
        return recommendations
    
    def _get_location_specific_guidance(
        self, 
        location: Location, 
        guidance_type: str,
        satellite_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Get location-specific recommendations for the given guidance type"""
        recommendations = []
        state = location.state.lower() if location.state else ""
        
        # Water conservation recommendations by region
        if guidance_type == "water_conservation":
            if "rajasthan" in state or "gujarat" in state:
                recommendations.extend([
                    "Prioritize rainwater harvesting structures like farm ponds",
                    "Implement micro-irrigation systems (drip/sprinkler)",
                    "Use drought-resistant crop varieties"
                ])
            elif "punjab" in state or "haryana" in state:
                recommendations.extend([
                    "Address groundwater depletion with water-efficient crops",
                    "Laser land leveling for uniform water distribution",
                    "Consider direct seeded rice instead of puddled transplanting"
                ])
            elif "kerala" in state or "west bengal" in state:
                recommendations.extend([
                    "Focus on drainage systems for excess water management",
                    "Consider raised bed farming to manage waterlogging",
                    "Use water storage systems to capture monsoon rainfall"
                ])
                
        # Soil health recommendations by region
        elif guidance_type == "soil_health":
            if "punjab" in state or "haryana" in state:
                recommendations.extend([
                    "Address soil alkalinity with gypsum application",
                    "Use green manures to improve organic carbon content",
                    "Practice residue incorporation instead of burning"
                ])
            elif "tamil nadu" in state or "andhra pradesh" in state:
                recommendations.extend([
                    "Address coastal soil salinity with tolerant varieties",
                    "Use organic amendments to improve soil structure",
                    "Implement soil conservation measures on sloping lands"
                ])
                
        # Use satellite data if available
        if satellite_data and guidance_type == "water_conservation":
            soil_moisture = satellite_data.get("soil_moisture", {}).get("value")
            rainfall = satellite_data.get("precipitation", {}).get("recent_mm")
            
            if soil_moisture and soil_moisture < 30:
                recommendations.append("Critical soil moisture levels detected - prioritize water conservation")
            elif rainfall and rainfall > 100:
                recommendations.append("Recent heavy rainfall detected - focus on water storage for dry periods")
                
        return recommendations
        
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other agents"""
        
        if message.get("type") == "guidance_request":
            try:
                guidance_type = message.get("guidance_type", "comprehensive")
                crop_type = message.get("crop_type")
                
                guidance = self._generate_guidance(
                    guidance_type,
                    f"Request for {guidance_type} guidance",
                    crop_type,
                    message.get("soil_type"),
                    message.get("location"),
                    message.get("satellite_data")
                )
                
                return {
                    "success": True,
                    "guidance": guidance
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        return {"success": False, "error": "Unknown message type"}
