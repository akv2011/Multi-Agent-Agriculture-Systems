"""
AgriMitr Irrigation Scheduling Model
====================================

Advanced machine learning model for optimizing irrigation scheduling based on:
- Crop-specific water requirements at different growth stages
- Soil moisture analysis from satellite data
- Weather forecasts and historical rainfall patterns
- Evapotranspiration calculations
- Soil type characteristics

The model provides precise water application recommendations and scheduling
to minimize water usage while maximizing crop yield.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

# Irrigation-related constants
WATER_STRESS_THRESHOLD = 0.7  # Ratio of readily available water to total available water
ET_ADJUSTMENT_FACTOR = 1.1  # Safety factor for ET calculations
EFFICIENCY_FACTORS = {
    "flood": 0.4,
    "furrow": 0.6, 
    "sprinkler": 0.75,
    "drip": 0.9,
    "micro_sprinkler": 0.85
}

# Growth stage crop coefficients (Kc)
CROP_COEFFICIENTS = {
    "rice": {"initial": 1.05, "development": 1.2, "mid_season": 1.3, "late_season": 0.9},
    "wheat": {"initial": 0.3, "development": 0.7, "mid_season": 1.15, "late_season": 0.4},
    "cotton": {"initial": 0.35, "development": 0.7, "mid_season": 1.15, "late_season": 0.7},
    "maize": {"initial": 0.3, "development": 0.7, "mid_season": 1.2, "late_season": 0.6},
    "sugarcane": {"initial": 0.4, "development": 0.8, "mid_season": 1.25, "late_season": 0.75},
    "potato": {"initial": 0.5, "development": 0.8, "mid_season": 1.15, "late_season": 0.75},
    "tomato": {"initial": 0.6, "development": 0.85, "mid_season": 1.15, "late_season": 0.8},
}

# Available water capacity by soil type (mm water per meter of soil)
SOIL_AWC = {
    "sandy": 80,
    "loamy_sand": 120,
    "sandy_loam": 150,
    "loam": 180,
    "clay_loam": 200,
    "clay": 170
}

class IrrigationModel:
    """
    ML-based model for irrigation scheduling recommendations
    """
    
    def __init__(self):
        """Initialize the irrigation scheduling model"""
        logger.info("Initializing AgriMitr Irrigation Scheduling Model")
        
    def calculate_crop_water_needs(self, 
                                  crop_type: str,
                                  growth_stage: str, 
                                  et0: float,  # reference evapotranspiration (mm/day)
                                  field_size: float = 1.0,  # hectares
                                  ) -> float:
        """
        Calculate daily crop water requirement
        
        Args:
            crop_type: Type of crop (rice, wheat, etc.)
            growth_stage: Current growth stage (initial, development, etc.)
            et0: Reference evapotranspiration in mm/day
            field_size: Size of field in hectares
            
        Returns:
            Daily water requirement in cubic meters
        """
        if crop_type.lower() not in CROP_COEFFICIENTS:
            logger.warning(f"Crop type {crop_type} not found. Using generic coefficients.")
            crop_coeffs = {"initial": 0.5, "development": 0.75, "mid_season": 1.0, "late_season": 0.6}
        else:
            crop_coeffs = CROP_COEFFICIENTS[crop_type.lower()]
        
        if growth_stage.lower() not in crop_coeffs:
            logger.warning(f"Growth stage {growth_stage} not found. Using mid_season.")
            kc = crop_coeffs["mid_season"]
        else:
            kc = crop_coeffs[growth_stage.lower()]
        
        # Calculate crop evapotranspiration (ETc)
        etc = et0 * kc * ET_ADJUSTMENT_FACTOR
        
        # Convert from mm/day to cubic meters for the field
        # 1 mm over 1 ha = 10 cubic meters of water
        water_volume = etc * field_size * 10
        
        return water_volume
    
    def calculate_irrigation_schedule(self,
                                     crop_type: str,
                                     soil_type: str,
                                     growth_stage: str,
                                     rooting_depth: float,  # meters
                                     current_moisture: Optional[float] = None,  # % of field capacity
                                     forecast_data: Optional[List[Dict]] = None,
                                     irrigation_method: str = "sprinkler",
                                     field_size: float = 1.0,  # hectares
                                     ) -> Dict[str, Any]:
        """
        Generate an optimized irrigation schedule
        
        Args:
            crop_type: Type of crop
            soil_type: Type of soil
            growth_stage: Current growth stage
            rooting_depth: Current rooting depth in meters
            current_moisture: Current soil moisture (% of field capacity)
            forecast_data: Weather forecast data for next 7 days
            irrigation_method: Method of irrigation
            field_size: Size of field in hectares
            
        Returns:
            Dictionary with irrigation schedule recommendations
        """
        # Get soil water capacity
        if soil_type.lower() not in SOIL_AWC:
            logger.warning(f"Soil type {soil_type} not found. Using loam.")
            awc = SOIL_AWC["loam"]
        else:
            awc = SOIL_AWC[soil_type.lower()]
        
        # Calculate total available water in root zone (mm)
        taw = awc * rooting_depth
        
        # Calculate readily available water (mm)
        raw = taw * WATER_STRESS_THRESHOLD
        
        # Default values if no weather forecast
        if not forecast_data:
            logger.warning("No forecast data provided. Using default values.")
            forecast_data = [
                {"date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "et0": 5.0, 
                 "rainfall": 0} for i in range(7)
            ]
        
        # Calculate water depletion
        depletion_start = 0
        if current_moisture is not None:
            depletion_start = taw * (1 - (current_moisture / 100))
        else:
            depletion_start = raw * 0.5  # Assume 50% of RAW is depleted
        
        schedule = []
        cumulative_depletion = depletion_start
        
        for day in forecast_data:
            date = day.get("date", "")
            et0 = day.get("et0", 5.0)  # mm/day
            rainfall = day.get("rainfall", 0)  # mm
            
            # Get crop coefficient for current stage
            if crop_type.lower() not in CROP_COEFFICIENTS:
                kc = 0.8  # Default coefficient
            else:
                crop_coeffs = CROP_COEFFICIENTS[crop_type.lower()]
                kc = crop_coeffs.get(growth_stage.lower(), 0.8)
            
            # Calculate daily crop water use
            etc = et0 * kc
            
            # Update water depletion
            effective_rainfall = min(rainfall * 0.8, etc)  # Assume 80% effectiveness
            daily_depletion = etc - effective_rainfall
            cumulative_depletion += daily_depletion
            
            # Check if irrigation is needed
            irrigate_today = False
            irrigation_amount = 0
            
            if cumulative_depletion >= raw:
                irrigate_today = True
                irrigation_amount = cumulative_depletion
                
                # Apply irrigation efficiency factor
                efficiency = EFFICIENCY_FACTORS.get(irrigation_method.lower(), 0.7)
                gross_irrigation = irrigation_amount / efficiency
                
                # Reset depletion after irrigation
                cumulative_depletion = 0
                
                # Calculate volume of water needed
                water_volume_m3 = gross_irrigation * field_size * 10  # mm to m3 conversion
            else:
                gross_irrigation = 0
                water_volume_m3 = 0
            
            schedule.append({
                "date": date,
                "etc_mm": round(etc, 2),
                "rainfall_mm": rainfall,
                "depletion_mm": round(cumulative_depletion, 2),
                "irrigate": irrigate_today,
                "irrigation_mm": round(gross_irrigation, 2),
                "water_volume_m3": round(water_volume_m3, 2)
            })
        
        return {
            "crop": crop_type,
            "soil": soil_type,
            "growth_stage": growth_stage,
            "root_depth_m": rooting_depth,
            "total_available_water_mm": round(taw, 2),
            "readily_available_water_mm": round(raw, 2),
            "initial_depletion_mm": round(depletion_start, 2),
            "irrigation_method": irrigation_method,
            "field_size_ha": field_size,
            "schedule": schedule
        }
    
    def analyze_soil_moisture_from_satellite(self, satellite_data: Dict) -> Dict:
        """
        Analyze soil moisture data from satellite imagery
        
        Args:
            satellite_data: Dictionary containing satellite data
            
        Returns:
            Soil moisture analysis results
        """
        moisture_data = satellite_data.get("soil_moisture", {})
        if not moisture_data:
            logger.warning("No soil moisture data found in satellite data")
            return {"moisture_level": "unknown", "moisture_percent": None}
        
        # Extract moisture values
        moisture_values = moisture_data.get("values", [])
        if not moisture_values:
            return {"moisture_level": "unknown", "moisture_percent": None}
        
        # Calculate average moisture
        avg_moisture = np.mean(moisture_values)
        
        # Categorize moisture level
        moisture_level = "adequate"
        if avg_moisture < 30:
            moisture_level = "very_dry"
        elif avg_moisture < 50:
            moisture_level = "dry"
        elif avg_moisture > 85:
            moisture_level = "saturated"
        elif avg_moisture > 70:
            moisture_level = "wet"
        
        return {
            "moisture_level": moisture_level,
            "moisture_percent": round(avg_moisture, 2),
            "field_capacity_percent": round(avg_moisture / 0.8, 2),  # Assuming field capacity at 80% moisture
            "temporal_variation": np.std(moisture_values) if len(moisture_values) > 1 else 0
        }
    
    def get_water_stress_index(self, satellite_data: Dict) -> Dict:
        """
        Calculate water stress index from satellite imagery (NDWI, thermal)
        
        Args:
            satellite_data: Dictionary containing satellite data
            
        Returns:
            Water stress analysis
        """
        # Check for satellite data
        if not satellite_data:
            return {
                "water_stress_index": 0.5,
                "stress_level": "moderate",
                "confidence": "low"
            }
        
        # Extract NDVI (indicates plant health)
        ndvi_data = satellite_data.get("ndvi", {})
        ndvi_value = np.mean(ndvi_data.get("values", [0.5]))
        
        # Extract land surface temperature if available
        lst_data = satellite_data.get("land_surface_temperature", {})
        lst_value = np.mean(lst_data.get("values", [25]))
        
        # Calculate water stress index (simplified model)
        # NDVI values range from -1 to 1, with healthy vegetation ~0.6-0.9
        # Lower NDVI and higher temperature indicate water stress
        wsi_base = max(0, 1 - ((ndvi_value - 0.2) / 0.7))  # Scale to 0-1
        
        # Temperature adjustment (higher temps increase stress)
        temp_factor = min(1, max(0, (lst_value - 15) / 25))  # Scale temp from 15-40°C to 0-1
        
        # Combine factors with weights
        water_stress_index = 0.7 * wsi_base + 0.3 * temp_factor
        
        # Categorize stress level
        stress_level = "none"
        if water_stress_index > 0.8:
            stress_level = "severe"
        elif water_stress_index > 0.6:
            stress_level = "high"
        elif water_stress_index > 0.4:
            stress_level = "moderate"
        elif water_stress_index > 0.2:
            stress_level = "low"
        
        return {
            "water_stress_index": round(water_stress_index, 2),
            "stress_level": stress_level,
            "contributing_factors": {
                "ndvi": round(ndvi_value, 2),
                "temperature": round(lst_value, 2)
            },
            "confidence": "medium" if "ndvi" in satellite_data else "low"
        }
    
    def generate_satellite_enhanced_irrigation_plan(self, 
                                                  crop_data: Dict, 
                                                  soil_data: Dict,
                                                  weather_data: Dict,
                                                  satellite_data: Dict = None) -> Dict:
        """
        Generate a comprehensive irrigation plan enhanced with satellite data
        
        Args:
            crop_data: Crop information
            soil_data: Soil information
            weather_data: Weather forecast data
            satellite_data: Optional satellite imagery data
            
        Returns:
            Complete irrigation plan with scheduling, recommendations and satellite insights
        """
        # Extract required parameters
        crop_type = crop_data.get("crop_type", "wheat").lower()
        growth_stage = crop_data.get("growth_stage", "mid_season").lower()
        soil_type = soil_data.get("soil_type", "loam").lower()
        root_depth = crop_data.get("root_depth", 0.5)  # meters
        field_size = crop_data.get("field_size", 1.0)  # hectares
        irrigation_method = crop_data.get("irrigation_method", "sprinkler")
        
        # Process weather forecast
        forecast = []
        for i in range(7):
            date_key = f"day_{i+1}"
            if date_key in weather_data:
                day_data = weather_data[date_key]
                forecast.append({
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "et0": day_data.get("et0", 5.0),
                    "rainfall": day_data.get("rainfall", 0)
                })
        
        # Get current soil moisture from satellite data if available
        current_moisture = None
        if satellite_data:
            moisture_analysis = self.analyze_soil_moisture_from_satellite(satellite_data)
            current_moisture = moisture_analysis.get("moisture_percent")
        
        # Generate irrigation schedule
        schedule = self.calculate_irrigation_schedule(
            crop_type=crop_type,
            soil_type=soil_type,
            growth_stage=growth_stage,
            rooting_depth=root_depth,
            current_moisture=current_moisture,
            forecast_data=forecast,
            irrigation_method=irrigation_method,
            field_size=field_size
        )
        
        # Add satellite-derived insights if available
        satellite_insights = {}
        if satellite_data:
            satellite_insights["soil_moisture"] = self.analyze_soil_moisture_from_satellite(satellite_data)
            satellite_insights["water_stress"] = self.get_water_stress_index(satellite_data)
        
        # Compile recommendations
        recommendations = []
        
        # Recommend based on irrigation method efficiency
        efficiency = EFFICIENCY_FACTORS.get(irrigation_method.lower(), 0.7)
        if efficiency < 0.6:
            recommendations.append(
                "Consider upgrading to a more efficient irrigation system like drip or micro-sprinkler "
                "to reduce water usage and increase efficiency."
            )
        
        # Add stress-based recommendations
        if satellite_data and satellite_insights["water_stress"]["stress_level"] in ["high", "severe"]:
            recommendations.append(
                "Satellite data indicates significant water stress. Consider immediate irrigation and "
                "adjust the schedule to provide more frequent but lighter applications."
            )
        
        # Soil moisture recommendations
        if satellite_data and satellite_insights["soil_moisture"]["moisture_level"] == "saturated":
            recommendations.append(
                "Soil is currently saturated according to satellite data. Delay irrigation to prevent "
                "waterlogging and potential root diseases."
            )
        
        # Return comprehensive plan
        return {
            "irrigation_schedule": schedule,
            "satellite_insights": satellite_insights,
            "water_savings_potential": round((1 - efficiency) * 100, 1),  # percent
            "recommendations": recommendations,
            "data_sources": {
                "weather_data": "forecast",
                "satellite_data": "integrated" if satellite_data else "none"
            }
        }

# Create a singleton instance
irrigation_model = IrrigationModel()

def get_irrigation_model() -> IrrigationModel:
    """Get the irrigation model instance"""
    return irrigation_model
