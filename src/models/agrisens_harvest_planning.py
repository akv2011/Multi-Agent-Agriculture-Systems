"""
<<<<<<< HEAD
AgriMitr Harvest Planning Integration
=======
AgriSens Harvest Planning Integration
>>>>>>> upstream/main
Advanced harvest scheduling with crop maturity detection and weather integration
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MaturityStage(Enum):
    """Crop maturity stages"""
    IMMATURE = "Immature"
    DEVELOPING = "Developing"
    MATURE = "Mature"
    OPTIMUM = "Optimum Harvest Window"
    OVER_MATURE = "Over Mature"

@dataclass
class MaturityAssessment:
    """Crop maturity assessment results"""
    current_stage: MaturityStage
    days_to_harvest: int
    confidence: float
    maturity_score: float  # 0-100
    growth_rate_status: str
    risk_factors: List[str]
    optimal_moisture: float

@dataclass
class WeatherWindow:
    """Weather window for harvest planning"""
    start_date: datetime
    end_date: datetime
    quality: float  # 0-1
    precipitation_risk: float
    temperature_forecast: List[float]
    humidity_forecast: List[float]
    wind_forecast: List[float]
    risk_assessment: str

@dataclass
class HarvestRecommendation:
    """Detailed harvest recommendation"""
    primary_window: WeatherWindow
    alternative_windows: List[WeatherWindow]
    expected_yield: float
    expected_quality: float
    moisture_recommendation: str
    equipment_recommendations: List[str]
    labor_requirements: int  # person-days per hectare
    cost_estimate: float
    storage_recommendations: List[str]

@dataclass
class HarvestPlan:
    """Complete harvest planning solution"""
    crop_type: str
    crop_variety: str
    current_status: MaturityAssessment
    primary_recommendation: HarvestRecommendation
    risk_mitigation: List[str]
    quality_optimization: List[str]
    post_harvest_handling: List[str]
    satellite_enhancement: Optional[Dict[str, Any]] = None

<<<<<<< HEAD
class AgriMitrHarvestModel:
    """AgriMitr harvest planning model"""
=======
class AgriSensHarvestModel:
    """AgriSens harvest planning model"""
>>>>>>> upstream/main
    
    def __init__(self):
        self.crop_maturity_models = self._load_crop_maturity_models()
        self.weather_impact_models = self._load_weather_impact_models()
<<<<<<< HEAD
        logger.info("AgriMitr Harvest Planning Model initialized")
=======
        logger.info("AgriSens Harvest Planning Model initialized")
>>>>>>> upstream/main
    
    def _load_crop_maturity_models(self) -> Dict[str, Dict[str, Any]]:
        """Load crop maturity models and standards"""
        return {
            "Rice": {
                "growing_degree_days": 2500,
                "grain_moisture_optimal": 20.0,
                "maturity_indicators": ["grain_hardness", "hull_color", "leaf_senescence"],
                "variety_adjustments": {
                    "short_duration": 0.8,
                    "medium_duration": 1.0,
                    "long_duration": 1.2
                }
            },
            "Wheat": {
                "growing_degree_days": 2000,
                "grain_moisture_optimal": 15.0,
                "maturity_indicators": ["spike_color", "grain_hardness", "leaf_dryness"],
                "variety_adjustments": {
                    "winter_wheat": 1.2,
                    "spring_wheat": 1.0
                }
            },
            "Maize": {
                "growing_degree_days": 2700,
                "grain_moisture_optimal": 24.0,
                "maturity_indicators": ["black_layer", "husk_dryness", "kernel_dent"],
                "variety_adjustments": {
                    "early": 0.8,
                    "medium": 1.0,
                    "late": 1.2
                }
            },
            "Cotton": {
                "growing_degree_days": 2200,
                "fiber_moisture_optimal": 12.0,
                "maturity_indicators": ["boll_opening", "fiber_development", "leaf_drop"],
                "variety_adjustments": {
                    "short_staple": 0.9,
                    "medium_staple": 1.0,
                    "long_staple": 1.1
                }
            }
        }
    
    def _load_weather_impact_models(self) -> Dict[str, Dict[str, Any]]:
        """Load weather impact models for harvest conditions"""
        return {
            "Rice": {
                "precipitation_threshold": 5.0,  # mm/day
                "temperature_optimal": (20, 32),  # °C
                "humidity_optimal": (40, 70),  # %
                "wind_threshold": 20.0  # km/h
            },
            "Wheat": {
                "precipitation_threshold": 2.0,
                "temperature_optimal": (15, 28),
                "humidity_optimal": (30, 60),
                "wind_threshold": 25.0
            },
            "Maize": {
                "precipitation_threshold": 3.0,
                "temperature_optimal": (18, 30),
                "humidity_optimal": (35, 65),
                "wind_threshold": 22.0
            },
            "Cotton": {
                "precipitation_threshold": 1.0,
                "temperature_optimal": (20, 35),
                "humidity_optimal": (30, 50),
                "wind_threshold": 18.0
            }
        }
    
    def assess_maturity(self, 
                      crop_type: str, 
                      crop_variety: str,
                      planting_date: datetime,
                      growth_data: Dict[str, Any],
                      satellite_data: Optional[Dict[str, Any]] = None) -> MaturityAssessment:
        """
        Assess crop maturity status and days to harvest
        
        Args:
            crop_type: Type of crop (Rice, Wheat, etc)
            crop_variety: Specific variety of the crop
            planting_date: Date when crop was planted
            growth_data: Current growth indicators (GDD, moisture, etc)
            satellite_data: Optional satellite imagery data
            
        Returns:
            MaturityAssessment with detailed maturity status
        """
        # Get crop model
        crop_model = self.crop_maturity_models.get(crop_type, self.crop_maturity_models.get("Rice", {}))
        
        # Calculate days since planting
        days_elapsed = (datetime.now() - planting_date).days
        
        # Get target GDD (Growing Degree Days)
        target_gdd = crop_model.get("growing_degree_days", 2000)
        
        # Get actual accumulated GDD
        current_gdd = growth_data.get("accumulated_gdd", 0)
        
        # Calculate GDD progress
        gdd_progress = min(1.0, current_gdd / target_gdd)
        
        # Apply variety adjustment if available
        variety_factor = crop_model.get("variety_adjustments", {}).get(
            crop_variety.lower(), 1.0)
        adjusted_gdd_progress = gdd_progress / variety_factor
        
        # Calculate maturity score (0-100)
        maturity_score = adjusted_gdd_progress * 100
        
        # Determine maturity stage
        current_stage = self._determine_maturity_stage(maturity_score)
        
        # Estimate days to harvest
        if gdd_progress >= 1.0:
            days_to_harvest = 0
        else:
            # Estimate days based on GDD progress and average daily GDD
            avg_daily_gdd = growth_data.get("daily_gdd", 10)
            remaining_gdd = target_gdd - current_gdd
            days_to_harvest = int(remaining_gdd / avg_daily_gdd) if avg_daily_gdd > 0 else 10
        
        # Determine growth rate status
        if growth_data.get("daily_gdd", 0) < growth_data.get("expected_daily_gdd", 10) * 0.8:
            growth_rate_status = "Slower than expected"
        elif growth_data.get("daily_gdd", 0) > growth_data.get("expected_daily_gdd", 10) * 1.2:
            growth_rate_status = "Faster than expected"
        else:
            growth_rate_status = "Normal"
        
        # Identify risk factors
        risk_factors = []
        if growth_data.get("moisture_stress", False):
            risk_factors.append("Moisture stress")
        if growth_data.get("disease_pressure", False):
            risk_factors.append("Disease pressure")
        if growth_data.get("nutrient_deficiency", False):
            risk_factors.append("Nutrient deficiency")
        
        # Get optimal moisture for harvest
        optimal_moisture = crop_model.get("grain_moisture_optimal", 15.0)
        
        # Enhance with satellite data if available
        confidence = 0.75  # Default confidence
        if satellite_data:
            # Adjust confidence based on satellite data quality
            confidence = min(0.95, confidence + satellite_data.get("data_quality", 0.0) * 0.2)
            
            # Adjust maturity assessment based on vegetation indices
            if "ndvi_trend" in satellite_data:
                ndvi_trend = satellite_data["ndvi_trend"]
                if ndvi_trend < -0.1:  # Declining NDVI indicates maturing
                    maturity_score = min(100, maturity_score * 1.1)
                    days_to_harvest = max(0, int(days_to_harvest * 0.9))
                elif ndvi_trend > 0.1:  # Increasing NDVI indicates active growth
                    maturity_score = max(0, maturity_score * 0.9)
                    days_to_harvest = int(days_to_harvest * 1.1)
            
            # Add satellite-detected risk factors
            if satellite_data.get("detected_stress", False):
                risk_factors.append("Satellite-detected crop stress")
        
        return MaturityAssessment(
            current_stage=current_stage,
            days_to_harvest=days_to_harvest,
            confidence=confidence,
            maturity_score=maturity_score,
            growth_rate_status=growth_rate_status,
            risk_factors=risk_factors,
            optimal_moisture=optimal_moisture
        )
    
    def _determine_maturity_stage(self, maturity_score: float) -> MaturityStage:
        """Determine maturity stage based on score"""
        if maturity_score < 60:
            return MaturityStage.IMMATURE
        elif maturity_score < 80:
            return MaturityStage.DEVELOPING
        elif maturity_score < 90:
            return MaturityStage.MATURE
        elif maturity_score <= 100:
            return MaturityStage.OPTIMUM
        else:
            return MaturityStage.OVER_MATURE
    
    def plan_harvest(self,
                   crop_type: str,
                   crop_variety: str,
                   maturity_assessment: MaturityAssessment,
                   field_size: float,
                   weather_forecast: List[Dict[str, Any]],
                   equipment_availability: Optional[Dict[str, Any]] = None,
                   satellite_data: Optional[Dict[str, Any]] = None) -> HarvestPlan:
        """
        Generate optimal harvest plan based on maturity and weather
        
        Args:
            crop_type: Type of crop
            crop_variety: Specific variety
            maturity_assessment: Current maturity assessment
            field_size: Size of field in hectares
            weather_forecast: 10-day weather forecast
            equipment_availability: Optional equipment constraints
            satellite_data: Optional satellite imagery data
            
        Returns:
            HarvestPlan with detailed recommendations
        """
        # Get weather impact model for this crop
        weather_model = self.weather_impact_models.get(crop_type, self.weather_impact_models.get("Rice", {}))
        
        # Find optimal weather windows
        weather_windows = self._identify_weather_windows(
            weather_forecast, 
            weather_model, 
            maturity_assessment.days_to_harvest
        )
        
        # Sort windows by quality
        weather_windows.sort(key=lambda w: w.quality, reverse=True)
        
        if not weather_windows:
            # Create a default window if none found
            default_start = datetime.now() + timedelta(days=maturity_assessment.days_to_harvest)
            default_end = default_start + timedelta(days=2)
            default_window = WeatherWindow(
                start_date=default_start,
                end_date=default_end,
                quality=0.5,
                precipitation_risk=0.5,
                temperature_forecast=[25.0, 25.0, 25.0],
                humidity_forecast=[60.0, 60.0, 60.0],
                wind_forecast=[10.0, 10.0, 10.0],
                risk_assessment="No optimal window found, using default timeframe"
            )
            weather_windows = [default_window]
        
        # Primary window is the best quality window
        primary_window = weather_windows[0]
        alternative_windows = weather_windows[1:3]  # Up to 2 alternatives
        
        # Calculate expected yield based on maturity and harvest timing
        base_yield = 1.0  # Relative to optimal (1.0 = 100%)
        
        # Adjust for maturity
        if maturity_assessment.current_stage == MaturityStage.IMMATURE:
            base_yield *= 0.7
        elif maturity_assessment.current_stage == MaturityStage.DEVELOPING:
            base_yield *= 0.9
        elif maturity_assessment.current_stage == MaturityStage.MATURE:
            base_yield *= 0.95
        elif maturity_assessment.current_stage == MaturityStage.OPTIMUM:
            base_yield *= 1.0
        elif maturity_assessment.current_stage == MaturityStage.OVER_MATURE:
            base_yield *= 0.85
        
        # Adjust for harvest window quality
        base_yield *= 0.8 + (primary_window.quality * 0.2)
        
        # Adjust for satellite data if available
        if satellite_data:
            if satellite_data.get("vegetation_health", 0.0) > 0.8:
                base_yield *= 1.1
            elif satellite_data.get("vegetation_health", 0.0) < 0.5:
                base_yield *= 0.9
        
        # Calculate expected quality
        expected_quality = 0.7 + (maturity_assessment.maturity_score / 100 * 0.3)
        expected_quality *= 0.8 + (primary_window.quality * 0.2)
        
        # Generate equipment recommendations
        equipment_recs = self._generate_equipment_recommendations(crop_type, field_size)
        
        # Calculate labor requirements (person-days per hectare)
        labor_req = self._calculate_labor_requirements(crop_type, field_size, equipment_availability)
        
        # Calculate cost estimate
        cost_estimate = self._calculate_harvest_cost(crop_type, field_size, labor_req)
        
        # Create primary recommendation
        primary_recommendation = HarvestRecommendation(
            primary_window=primary_window,
            alternative_windows=alternative_windows,
            expected_yield=base_yield,
            expected_quality=expected_quality,
            moisture_recommendation=f"Target moisture content: {maturity_assessment.optimal_moisture:.1f}%",
            equipment_recommendations=equipment_recs,
            labor_requirements=labor_req,
            cost_estimate=cost_estimate,
            storage_recommendations=self._generate_storage_recommendations(crop_type)
        )
        
        # Generate risk mitigation strategies
        risk_mitigation = self._generate_risk_mitigation(
            crop_type, 
            maturity_assessment.risk_factors, 
            primary_window
        )
        
        # Generate quality optimization strategies
        quality_optimization = self._generate_quality_optimization(crop_type, crop_variety)
        
        # Generate post-harvest handling recommendations
        post_harvest = self._generate_post_harvest_handling(crop_type)
        
        # Create complete harvest plan
        return HarvestPlan(
            crop_type=crop_type,
            crop_variety=crop_variety,
            current_status=maturity_assessment,
            primary_recommendation=primary_recommendation,
            risk_mitigation=risk_mitigation,
            quality_optimization=quality_optimization,
            post_harvest_handling=post_harvest,
            satellite_enhancement=satellite_data
        )
    
    def _identify_weather_windows(self, 
                               weather_forecast: List[Dict[str, Any]],
                               weather_model: Dict[str, Any],
                               days_to_harvest: int) -> List[WeatherWindow]:
        """Identify optimal weather windows for harvesting"""
        windows = []
        
        # Skip to the first day where harvest is possible
        start_idx = max(0, min(days_to_harvest, len(weather_forecast) - 3))
        
        # Look for 3-day windows
        for i in range(start_idx, len(weather_forecast) - 2):
            window_days = weather_forecast[i:i+3]
            
            # Get weather parameters
            precip_risk = max(day.get("precipitation_chance", 0) for day in window_days)
            temp_forecast = [day.get("temperature", 25) for day in window_days]
            humidity_forecast = [day.get("humidity", 60) for day in window_days]
            wind_forecast = [day.get("wind_speed", 10) for day in window_days]
            
            # Calculate window quality
            quality = self._calculate_window_quality(
                window_days,
                weather_model
            )
            
            # Generate risk assessment
            risk_assessment = self._assess_weather_risk(
                window_days,
                weather_model
            )
            
            # Create window
            start_date = datetime.now() + timedelta(days=i)
            end_date = start_date + timedelta(days=2)
            
            window = WeatherWindow(
                start_date=start_date,
                end_date=end_date,
                quality=quality,
                precipitation_risk=precip_risk,
                temperature_forecast=temp_forecast,
                humidity_forecast=humidity_forecast,
                wind_forecast=wind_forecast,
                risk_assessment=risk_assessment
            )
            
            windows.append(window)
        
        return windows
    
    def _calculate_window_quality(self, 
                               window_days: List[Dict[str, Any]],
                               weather_model: Dict[str, Any]) -> float:
        """Calculate quality score for a weather window"""
        # Initialize score at 1.0 (perfect)
        score = 1.0
        
        # Get weather thresholds
        precip_threshold = weather_model.get("precipitation_threshold", 5.0)
        temp_range = weather_model.get("temperature_optimal", (15, 32))
        humidity_range = weather_model.get("humidity_optimal", (40, 70))
        wind_threshold = weather_model.get("wind_threshold", 20.0)
        
        for day in window_days:
            # Check precipitation
            precip = day.get("precipitation_mm", 0)
            precip_chance = day.get("precipitation_chance", 0)
            
            if precip > precip_threshold or precip_chance > 60:
                score *= 0.7
            elif precip > 0 or precip_chance > 30:
                score *= 0.9
                
            # Check temperature
            temp = day.get("temperature", 25)
            if temp < temp_range[0] or temp > temp_range[1]:
                score *= 0.8
                
            # Check humidity
            humidity = day.get("humidity", 60)
            if humidity < humidity_range[0] or humidity > humidity_range[1]:
                score *= 0.9
                
            # Check wind
            wind = day.get("wind_speed", 10)
            if wind > wind_threshold:
                score *= 0.8
        
        return score
    
    def _assess_weather_risk(self,
                          window_days: List[Dict[str, Any]],
                          weather_model: Dict[str, Any]) -> str:
        """Assess weather risks for a given window"""
        risks = []
        
        # Get weather thresholds
        precip_threshold = weather_model.get("precipitation_threshold", 5.0)
        temp_range = weather_model.get("temperature_optimal", (15, 32))
        humidity_range = weather_model.get("humidity_optimal", (40, 70))
        wind_threshold = weather_model.get("wind_threshold", 20.0)
        
        # Check for rain
        max_precip = max(day.get("precipitation_mm", 0) for day in window_days)
        max_precip_chance = max(day.get("precipitation_chance", 0) for day in window_days)
        
        if max_precip > precip_threshold:
            risks.append(f"High rainfall ({max_precip}mm)")
        elif max_precip_chance > 60:
            risks.append(f"High precipitation chance ({max_precip_chance}%)")
            
        # Check temperature
        min_temp = min(day.get("temperature", 25) for day in window_days)
        max_temp = max(day.get("temperature", 25) for day in window_days)
        
        if min_temp < temp_range[0]:
            risks.append(f"Low temperature ({min_temp}°C)")
        if max_temp > temp_range[1]:
            risks.append(f"High temperature ({max_temp}°C)")
            
        # Check humidity
        max_humidity = max(day.get("humidity", 60) for day in window_days)
        if max_humidity > humidity_range[1]:
            risks.append(f"High humidity ({max_humidity}%)")
            
        # Check wind
        max_wind = max(day.get("wind_speed", 10) for day in window_days)
        if max_wind > wind_threshold:
            risks.append(f"Strong winds ({max_wind}km/h)")
            
        if not risks:
            return "Optimal conditions, minimal risk"
        else:
            return f"Potential risks: {', '.join(risks)}"
    
    def _generate_equipment_recommendations(self, crop_type: str, field_size: float) -> List[str]:
        """Generate equipment recommendations based on crop and field size"""
        recommendations = []
        
        if crop_type == "Rice":
            if field_size < 5:
                recommendations.append("Mini combine harvester")
            else:
                recommendations.append("Medium-duty combine harvester with paddy modification")
            recommendations.append("Grain moisture meter")
            recommendations.append("Paddy thresher")
        
        elif crop_type == "Wheat":
            if field_size < 10:
                recommendations.append("Standard combine harvester")
            else:
                recommendations.append("Large combine harvester with grain header")
            recommendations.append("Grain moisture meter")
            recommendations.append("Grain cleaning equipment")
        
        elif crop_type == "Cotton":
            if field_size < 5:
                recommendations.append("Manual picking with adequate labor")
            else:
                recommendations.append("Cotton picker machine")
            recommendations.append("Cotton module builder")
        
        elif crop_type == "Maize":
            recommendations.append("Corn combine harvester")
            recommendations.append("Grain moisture meter")
            recommendations.append("Corn sheller")
        
        else:
            recommendations.append("Standard harvest equipment")
            recommendations.append("Moisture meter")
        
        return recommendations
    
    def _calculate_labor_requirements(self, 
                                   crop_type: str, 
                                   field_size: float,
                                   equipment_availability: Optional[Dict[str, Any]]) -> int:
        """Calculate labor requirements in person-days per hectare"""
        base_labor = 0
        
        # Base labor requirements by crop type (person-days/hectare)
        if crop_type == "Rice":
            base_labor = 5
        elif crop_type == "Wheat":
            base_labor = 3
        elif crop_type == "Cotton":
            base_labor = 15  # Cotton is labor intensive
        elif crop_type == "Maize":
            base_labor = 4
        else:
            base_labor = 5
        
        # Adjust for equipment availability
        if equipment_availability:
            if equipment_availability.get("mechanized_harvester", False):
                base_labor *= 0.3  # 70% reduction with mechanization
            elif equipment_availability.get("semi_mechanized", False):
                base_labor *= 0.6  # 40% reduction with semi-mechanization
        
        # Adjust for scale (economies of scale)
        if field_size > 10:
            base_labor *= 0.8
        elif field_size < 2:
            base_labor *= 1.2
        
        return round(base_labor)
    
    def _calculate_harvest_cost(self, crop_type: str, field_size: float, labor_req: int) -> float:
        """Calculate harvest cost in INR per hectare"""
        # Base cost includes labor, equipment, fuel, etc.
        labor_cost = labor_req * 500  # 500 INR per person-day
        
        # Equipment cost
        equipment_cost = 0
        if crop_type == "Rice":
            equipment_cost = 2500
        elif crop_type == "Wheat":
            equipment_cost = 2000
        elif crop_type == "Cotton":
            equipment_cost = 3000
        elif crop_type == "Maize":
            equipment_cost = 2200
        else:
            equipment_cost = 2500
        
        # Adjust for scale
        if field_size > 10:
            equipment_cost *= 0.8  # Economy of scale
        elif field_size < 2:
            equipment_cost *= 1.2  # Diseconomy of scale
        
        # Transport and miscellaneous
        misc_cost = 1000
        
        return labor_cost + equipment_cost + misc_cost
    
    def _generate_storage_recommendations(self, crop_type: str) -> List[str]:
        """Generate storage recommendations based on crop type"""
        if crop_type == "Rice":
            return [
                "Ensure moisture content below 14% before storage",
                "Use hermetic bags or silos for longer storage",
                "Implement regular monitoring for pests"
            ]
        elif crop_type == "Wheat":
            return [
                "Store at moisture content below 12%",
                "Clean and fumigate storage facility",
                "Maintain cool, dry storage conditions"
            ]
        elif crop_type == "Cotton":
            return [
                "Store in dry, well-ventilated space",
                "Keep away from direct sunlight",
                "Protect from moisture and contaminants"
            ]
        elif crop_type == "Maize":
            return [
                "Dry to moisture content below 15%",
                "Use well-ventilated storage structures",
                "Implement pest monitoring and control"
            ]
        else:
            return [
                "Ensure proper drying before storage",
                "Use appropriate storage containers",
                "Monitor regularly for quality and pests"
            ]
    
    def _generate_risk_mitigation(self, 
                               crop_type: str, 
                               risk_factors: List[str], 
                               weather_window: WeatherWindow) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        # Weather-related risks
        if weather_window.precipitation_risk > 0.3:
            strategies.append("Monitor weather forecasts daily and be prepared to adjust schedule")
            strategies.append("Have tarps/covers ready for harvested crop if rain occurs")
        
        if max(weather_window.humidity_forecast) > 70:
            strategies.append("Harvest during mid-day when humidity is lowest")
            strategies.append("Ensure proper drying facilities are available")
        
        if max(weather_window.wind_forecast) > 15:
            strategies.append("Harvest in early morning when winds are typically lighter")
        
        # Crop condition risks
        if "Moisture stress" in risk_factors:
            strategies.append("Prioritize affected areas for earlier harvest")
        
        if "Disease pressure" in risk_factors:
            strategies.append("Segregate harvested crop from affected areas")
            strategies.append("Apply post-harvest treatments if necessary")
        
        # Add general recommendations
        strategies.append("Have backup equipment or parts readily available")
        strategies.append("Secure adequate labor before harvest window begins")
        
        return strategies
    
    def _generate_quality_optimization(self, crop_type: str, crop_variety: str) -> List[str]:
        """Generate quality optimization strategies"""
        if crop_type == "Rice":
            return [
                "Harvest at optimal grain moisture (20-22%)",
                "Minimize grain breakage by adjusting combine settings",
                "Ensure proper drying to 14% moisture for storage",
                "Clean harvested grain to remove impurities"
            ]
        elif crop_type == "Wheat":
            return [
                "Harvest at optimal moisture content (12-14%)",
                "Adjust combine settings to minimize grain damage",
                "Clean grain thoroughly before storage",
                "Test for protein content and moisture"
            ]
        elif crop_type == "Cotton":
            return [
                "Harvest when bolls are fully open but before weathering",
                "Avoid harvesting wet cotton",
                "Remove leaf trash and other contaminants",
                "Grade cotton based on fiber length and quality"
            ]
        elif crop_type == "Maize":
            return [
                "Harvest at optimal kernel moisture (23-25% for wet milling, 15-18% for storage)",
                "Adjust combine settings to minimize kernel damage",
                "Clean thoroughly to remove broken kernels and debris",
                "Dry carefully to prevent stress cracks"
            ]
        else:
            return [
                "Harvest at optimal maturity",
                "Handle carefully to minimize damage",
                "Remove foreign materials and debris",
                "Ensure proper drying and storage conditions"
            ]
    
    def _generate_post_harvest_handling(self, crop_type: str) -> List[str]:
        """Generate post-harvest handling recommendations"""
        if crop_type == "Rice":
            return [
                "Dry paddy to 14% moisture content",
                "Store in clean, dry containers or bags",
                "Monitor regularly for insect infestation",
                "Mill within 3-6 months for best quality"
            ]
        elif crop_type == "Wheat":
            return [
                "Clean grain to remove chaff and impurities",
                "Dry to 12% moisture content for storage",
                "Store in well-ventilated, cool conditions",
                "Check regularly for moisture and pests"
            ]
        elif crop_type == "Cotton":
            return [
                "Keep harvested cotton clean and dry",
                "Transport to gin as soon as possible",
                "Protect from contamination during storage",
                "Maintain proper documentation for quality"
            ]
        elif crop_type == "Maize":
            return [
                "Dry kernels to 14% moisture for storage",
                "Remove damaged kernels before storage",
                "Store in well-ventilated structures",
                "Apply appropriate pest control measures"
            ]
        else:
            return [
                "Implement appropriate drying techniques",
                "Remove damaged or diseased product",
                "Store in appropriate conditions for crop type",
                "Monitor quality regularly during storage"
            ]
        
# Global instance
<<<<<<< HEAD
_AgriMitr_harvest_model = None

def get_AgriMitr_harvest_model() -> AgriMitrHarvestModel:
    """Get singleton instance of AgriMitr harvest model"""
    global _AgriMitr_harvest_model
    if _AgriMitr_harvest_model is None:
        _AgriMitr_harvest_model = AgriMitrHarvestModel()
        logger.info("AgriMitr Harvest Planning Model initialized successfully")
    return _AgriMitr_harvest_model

def enhance_harvest_planning_with_AgriMitr(
=======
_agrisens_harvest_model = None

def get_agrisens_harvest_model() -> AgriSensHarvestModel:
    """Get singleton instance of AgriSens harvest model"""
    global _agrisens_harvest_model
    if _agrisens_harvest_model is None:
        _agrisens_harvest_model = AgriSensHarvestModel()
        logger.info("AgriSens Harvest Planning Model initialized successfully")
    return _agrisens_harvest_model

def enhance_harvest_planning_with_agrisens(
>>>>>>> upstream/main
    crop_type: str,
    crop_variety: str,
    planting_date: datetime,
    growth_data: Dict[str, Any],
    field_size: float,
    weather_forecast: List[Dict[str, Any]],
    equipment_availability: Optional[Dict[str, Any]] = None,
    satellite_data: Optional[Dict[str, Any]] = None
) -> HarvestPlan:
    """
<<<<<<< HEAD
    Enhance harvest planning with AgriMitr harvest timing model
=======
    Enhance harvest planning with AgriSens harvest timing model
>>>>>>> upstream/main
    
    Args:
        crop_type: Type of crop (Rice, Wheat, etc)
        crop_variety: Specific variety of the crop
        planting_date: Date when crop was planted
        growth_data: Current growth indicators (GDD, moisture, etc)
        field_size: Size of field in hectares
        weather_forecast: 10-day weather forecast data
        equipment_availability: Optional equipment constraints
        satellite_data: Optional satellite imagery data
            
    Returns:
        HarvestPlan with detailed harvest recommendations
    """
<<<<<<< HEAD
    model = get_AgriMitr_harvest_model()
=======
    model = get_agrisens_harvest_model()
>>>>>>> upstream/main
    
    # Assess crop maturity
    maturity = model.assess_maturity(
        crop_type=crop_type,
        crop_variety=crop_variety,
        planting_date=planting_date,
        growth_data=growth_data,
        satellite_data=satellite_data
    )
    
    # Generate harvest plan
    harvest_plan = model.plan_harvest(
        crop_type=crop_type,
        crop_variety=crop_variety,
        maturity_assessment=maturity,
        field_size=field_size,
        weather_forecast=weather_forecast,
        equipment_availability=equipment_availability,
        satellite_data=satellite_data
    )
    
    logger.info(f"Harvest planning completed for {crop_type} ({crop_variety})")
    logger.info(f"Maturity status: {maturity.current_stage.value}, Days to harvest: {maturity.days_to_harvest}")
    logger.info(f"Optimal harvest window: {harvest_plan.primary_recommendation.primary_window.start_date.strftime('%Y-%m-%d')} to {harvest_plan.primary_recommendation.primary_window.end_date.strftime('%Y-%m-%d')}")
    
    return harvest_plan
