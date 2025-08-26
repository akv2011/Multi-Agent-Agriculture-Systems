"""
Weather Forecast Agent
Specialized agent for providing weather forecasts and weather-related agricultural guidance.
Integrates with external weather APIs and satellite data.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import urllib.parse
import aiohttp

from .base_agent import BaseWorkerAgent
from .satellite_integration import get_satellite_data_for_location, format_satellite_summary
from ..core.models import AgentCapability
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, SoilType, SeasonType,
    WeatherData, Location, FarmProfile, QueryDomain
)

logger = logging.getLogger(__name__)


@dataclass
class WeatherForecast:
    """Weather forecast data structure"""
    date: datetime
    temperature_min: float
    temperature_max: float
    temperature_avg: float
    humidity: float
    precipitation_mm: float
    wind_speed_kmh: float
    wind_direction: str
    conditions: str
    uv_index: float
    sunrise: datetime
    sunset: datetime
    farming_impact: str = ""
    alert_level: str = "normal"


class WeatherForecastAgent(BaseWorkerAgent):
    """
    Agent for providing weather forecasts and weather-related agricultural guidance
    Includes integration with external weather APIs and satellite data
    """
    
    def __init__(self, agent_id: str, name: str):
        """Initialize the weather forecast agent"""
        super().__init__(agent_id, name)
        self.api_key = self._get_weather_api_key()
        self._capabilities = [
            AgentCapability.WEATHER_FORECAST,
            AgentCapability.CLIMATE_ANALYSIS,
            AgentCapability.AGRICULTURAL_ALERTS
        ]
    
    def _get_weather_api_key(self) -> str:
        """Get weather API key from environment or config"""
        import os
        # Try to get from environment
        api_key = os.environ.get("WEATHER_API_KEY", "")
        if api_key:
            return api_key
            
        # Try to get from config file
        try:
            import json
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "api_keys.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("weather_api_key", "")
        except Exception as e:
            logger.warning(f"Failed to load weather API key from config: {e}")
            
        # Return empty key (will use mock data)
        return ""
    
    def initialize(self):
        """Initialize the weather forecast agent"""
        logger.info("Initializing weather forecast agent")
        # No specific initialization needed for now
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [cap.value for cap in self._capabilities]
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a weather forecast query"""
        logger.info(f"Processing weather forecast query: {query.query_text}")
        
        response = AgentResponse(
            agent_id=self.agent_id,
            success=False,
            response_type="weather_forecast",
            message="Processing weather forecast",
            data={}
        )
        
        try:
            # Check if location is provided
            if not query.location:
                response.message = "Location is required for weather forecast"
                return response
            
            # Get satellite data if available
            satellite_data = None
            try:
                satellite_data = await get_satellite_data_for_location(
                    query.location.latitude,
                    query.location.longitude
                )
            except Exception as e:
                logger.warning(f"Failed to get satellite data: {e}")
            
            # Get weather forecast
            forecast_data = await self._get_weather_forecast(
                query.location.latitude, 
                query.location.longitude,
                query.location.address
            )
            
            # Get agricultural impact
            crop_impacts = self._analyze_crop_impact(forecast_data, query.crop_type)
            
            # Prepare response
            response.success = True
            response.message = self._generate_forecast_summary(forecast_data)
            response.data = {
                "current_weather": self._format_current_weather(forecast_data[0]),
                "forecast": [self._format_forecast_day(day) for day in forecast_data],
                "agricultural_impact": crop_impacts,
                "satellite_data": format_satellite_summary(satellite_data) if satellite_data else None,
                "satellite_enhanced": satellite_data is not None,
                "alerts": self._generate_weather_alerts(forecast_data, satellite_data)
            }
            
        except Exception as e:
            logger.error(f"Error in weather forecast: {e}", exc_info=True)
            response.message = f"Error processing weather forecast: {str(e)}"
        
        return response
    
    async def _get_weather_forecast(
        self, latitude: float, longitude: float, location_name: str = ""
    ) -> List[WeatherForecast]:
        """
        Get weather forecast for the given location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            location_name: Optional location name
            
        Returns:
            List of WeatherForecast objects for today and next 7 days
        """
        if self.api_key:
            return await self._get_weather_from_api(latitude, longitude)
        else:
            # Use mock data if no API key is available
            return self._get_mock_weather_data(latitude, longitude, location_name)
    
    async def _get_weather_from_api(self, latitude: float, longitude: float) -> List[WeatherForecast]:
        """
        Get weather forecast from external API
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            List of WeatherForecast objects
        """
        # Note: This is a placeholder for an actual API integration
        # Replace with your preferred weather API (OpenWeatherMap, Weather.com, etc.)
        try:
            # Example with OpenWeatherMap API
            url = f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&exclude=minutely,hourly&units=metric&appid={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        forecasts = []
                        # Process current weather
                        current = data.get('current', {})
                        today = datetime.now()
                        current_forecast = WeatherForecast(
                            date=today,
                            temperature_min=current.get('temp', 0) - 2,  # Approximate
                            temperature_max=current.get('temp', 0) + 2,  # Approximate
                            temperature_avg=current.get('temp', 0),
                            humidity=current.get('humidity', 0),
                            precipitation_mm=current.get('rain', {}).get('1h', 0) * 24 if 'rain' in current else 0,
                            wind_speed_kmh=current.get('wind_speed', 0) * 3.6,  # Convert m/s to km/h
                            wind_direction=self._degrees_to_direction(current.get('wind_deg', 0)),
                            conditions=current.get('weather', [{}])[0].get('description', 'Unknown'),
                            uv_index=current.get('uvi', 0),
                            sunrise=datetime.fromtimestamp(current.get('sunrise', today.timestamp())),
                            sunset=datetime.fromtimestamp(current.get('sunset', (today + timedelta(hours=12)).timestamp()))
                        )
                        forecasts.append(current_forecast)
                        
                        # Process daily forecasts
                        for day_data in data.get('daily', [])[:7]:  # Get 7 day forecast
                            day_date = datetime.fromtimestamp(day_data.get('dt', today.timestamp()))
                            day_forecast = WeatherForecast(
                                date=day_date,
                                temperature_min=day_data.get('temp', {}).get('min', 0),
                                temperature_max=day_data.get('temp', {}).get('max', 0),
                                temperature_avg=(day_data.get('temp', {}).get('min', 0) + 
                                               day_data.get('temp', {}).get('max', 0)) / 2,
                                humidity=day_data.get('humidity', 0),
                                precipitation_mm=day_data.get('rain', 0),
                                wind_speed_kmh=day_data.get('wind_speed', 0) * 3.6,
                                wind_direction=self._degrees_to_direction(day_data.get('wind_deg', 0)),
                                conditions=day_data.get('weather', [{}])[0].get('description', 'Unknown'),
                                uv_index=day_data.get('uvi', 0),
                                sunrise=datetime.fromtimestamp(day_data.get('sunrise', day_date.timestamp())),
                                sunset=datetime.fromtimestamp(day_data.get('sunset', (day_date + timedelta(hours=12)).timestamp()))
                            )
                            forecasts.append(day_forecast)
                        
                        return forecasts
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_weather_data(latitude, longitude)
                        
        except Exception as e:
            logger.error(f"Failed to get weather from API: {e}", exc_info=True)
            return self._get_mock_weather_data(latitude, longitude)
    
    def _get_mock_weather_data(
        self, latitude: float, longitude: float, location_name: str = ""
    ) -> List[WeatherForecast]:
        """
        Get mock weather data when API is not available
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            location_name: Optional location name
            
        Returns:
            List of WeatherForecast objects
        """
        forecasts = []
        today = datetime.now()
        
        # Generate weather pattern based on location
        # Higher latitude = cooler, higher longitude = drier (simplified)
        base_temp = 30 - abs(latitude) / 2  # Base temperature decreases with latitude
        temp_variation = 5  # Daily temperature variation
        humidity_base = max(40, 80 - longitude / 4) if longitude > 0 else min(80, 40 + abs(longitude) / 4)
        
        # Adjust for location name if provided (for demo purposes)
        if location_name:
            location_lower = location_name.lower()
            if any(desert in location_lower for desert in ["desert", "sahara", "arid"]):
                base_temp += 5
                humidity_base = 20
            elif any(mountain in location_lower for mountain in ["mountain", "hill", "highland"]):
                base_temp -= 5
                humidity_base += 10
            elif any(tropical in location_lower for tropical in ["tropical", "rainforest", "jungle"]):
                base_temp += 2
                humidity_base += 30
            
        # Generate forecasts
        for i in range(8):  # Today + 7 days
            day_date = today + timedelta(days=i)
            
            # Vary temperature by day with a slight downward trend for demo purposes
            day_factor = i / 10
            day_temp_max = base_temp - day_factor * 2 + ((i % 3) - 1) * 2
            day_temp_min = day_temp_max - temp_variation
            
            # Generate some weather pattern
            is_rainy = i % 3 == 0  # Every third day is rainy
            conditions = "Rainy" if is_rainy else "Sunny" if i % 4 == 1 else "Partly cloudy"
            precipitation = 15.0 if is_rainy else 0.0
            
            # Create forecast
            forecast = WeatherForecast(
                date=day_date,
                temperature_min=day_temp_min,
                temperature_max=day_temp_max,
                temperature_avg=(day_temp_min + day_temp_max) / 2,
                humidity=humidity_base + (20 if is_rainy else 0) - i,
                precipitation_mm=precipitation,
                wind_speed_kmh=10.0 + i * 1.5,
                wind_direction=self._degrees_to_direction((i * 45) % 360),
                conditions=conditions,
                uv_index=8.0 if conditions == "Sunny" else 4.0,
                sunrise=datetime.combine(day_date.date(), datetime.min.time()) + timedelta(hours=6),
                sunset=datetime.combine(day_date.date(), datetime.min.time()) + timedelta(hours=18)
            )
            
            # Add agricultural impact
            if is_rainy and i == 0:
                forecast.farming_impact = "Heavy rain may impact field operations"
                forecast.alert_level = "warning"
            elif forecast.temperature_max > 35:
                forecast.farming_impact = "High temperature may cause heat stress in crops"
                forecast.alert_level = "caution"
            
            forecasts.append(forecast)
        
        return forecasts
    
    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def _format_current_weather(self, forecast: WeatherForecast) -> Dict[str, Any]:
        """Format current weather for response"""
        return {
            "temperature": {
                "current": round(forecast.temperature_avg, 1),
                "min": round(forecast.temperature_min, 1),
                "max": round(forecast.temperature_max, 1),
                "unit": "°C"
            },
            "humidity": {
                "value": forecast.humidity,
                "unit": "%"
            },
            "wind": {
                "speed": round(forecast.wind_speed_kmh, 1),
                "direction": forecast.wind_direction,
                "unit": "km/h"
            },
            "precipitation": {
                "amount": round(forecast.precipitation_mm, 1),
                "unit": "mm"
            },
            "conditions": forecast.conditions,
            "uv_index": forecast.uv_index,
            "sunrise": forecast.sunrise.strftime("%H:%M"),
            "sunset": forecast.sunset.strftime("%H:%M"),
            "alert_level": forecast.alert_level
        }
    
    def _format_forecast_day(self, forecast: WeatherForecast) -> Dict[str, Any]:
        """Format forecast day for response"""
        return {
            "date": forecast.date.strftime("%Y-%m-%d"),
            "day_of_week": forecast.date.strftime("%A"),
            "temperature": {
                "min": round(forecast.temperature_min, 1),
                "max": round(forecast.temperature_max, 1),
                "avg": round(forecast.temperature_avg, 1),
                "unit": "°C"
            },
            "humidity": forecast.humidity,
            "precipitation": {
                "amount": round(forecast.precipitation_mm, 1),
                "unit": "mm",
                "probability": 80 if forecast.precipitation_mm > 0 else 10
            },
            "wind": {
                "speed": round(forecast.wind_speed_kmh, 1),
                "direction": forecast.wind_direction,
                "unit": "km/h"
            },
            "conditions": forecast.conditions,
            "uv_index": forecast.uv_index,
            "farming_impact": forecast.farming_impact
        }
    
    def _generate_forecast_summary(self, forecasts: List[WeatherForecast]) -> str:
        """Generate a text summary of the weather forecast"""
        if not forecasts:
            return "Weather forecast not available"
        
        today = forecasts[0]
        tomorrow = forecasts[1] if len(forecasts) > 1 else None
        
        # Create summary
        summary = f"Today's weather forecast: {today.conditions} with temperatures between {int(today.temperature_min)}°C and {int(today.temperature_max)}°C."
        
        if today.precipitation_mm > 0:
            summary += f" Expect {round(today.precipitation_mm, 1)}mm of precipitation."
        
        if tomorrow:
            summary += f" Tomorrow will be {tomorrow.conditions.lower()} with temperatures between {int(tomorrow.temperature_min)}°C and {int(tomorrow.temperature_max)}°C."
        
        # Add any alerts
        if today.alert_level != "normal":
            summary += f" Weather alert: {today.farming_impact}."
        
        return summary
    
    def _analyze_crop_impact(
        self, forecasts: List[WeatherForecast], crop_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the impact of weather forecast on crops
        
        Args:
            forecasts: List of weather forecasts
            crop_type: Optional crop type
            
        Returns:
            Dictionary with crop impact analysis
        """
        today = forecasts[0]
        week_forecasts = forecasts[:7]  # Next 7 days
        
        # Calculate metrics
        avg_temp = sum(f.temperature_avg for f in week_forecasts) / len(week_forecasts)
        total_rain = sum(f.precipitation_mm for f in week_forecasts)
        avg_humidity = sum(f.humidity for f in week_forecasts) / len(week_forecasts)
        hot_days = sum(1 for f in week_forecasts if f.temperature_max > 35)
        rainy_days = sum(1 for f in week_forecasts if f.precipitation_mm > 1)
        
        # Determine general farming conditions
        if total_rain > 50:
            general_conditions = "Very wet conditions expected"
        elif total_rain > 20:
            general_conditions = "Moderate rainfall expected"
        elif total_rain < 5:
            general_conditions = "Dry conditions expected"
        else:
            general_conditions = "Average conditions expected"
            
        # Default recommendations
        recommendations = [
            "Monitor soil moisture levels regularly",
            "Adjust irrigation based on rainfall"
        ]
        
        # Determine disease risk
        disease_risk = "low"
        if avg_humidity > 80 and avg_temp > 25:
            disease_risk = "high"
            recommendations.append("Watch for fungal diseases due to high humidity and temperature")
        elif avg_humidity > 70 or rainy_days > 3:
            disease_risk = "moderate"
            recommendations.append("Consider preventive fungicide application")
            
        # Determine crop-specific impact if crop type is provided
        crop_specific_impact = {}
        if crop_type:
            crop_specific_impact = self._get_crop_specific_impact(
                crop_type, avg_temp, total_rain, hot_days, avg_humidity, disease_risk
            )
            if "recommendations" in crop_specific_impact:
                recommendations.extend(crop_specific_impact["recommendations"])
        
        return {
            "general_conditions": general_conditions,
            "disease_risk": disease_risk,
            "irrigation_need": "low" if total_rain > 30 else "high" if total_rain < 10 else "moderate",
            "field_workability": "poor" if total_rain > 40 else "good" if total_rain < 20 else "fair",
            "recommendations": recommendations,
            "crop_specific": crop_specific_impact
        }
    
    def _get_crop_specific_impact(
        self, crop_type: str, avg_temp: float, total_rain: float, 
        hot_days: int, avg_humidity: float, disease_risk: str
    ) -> Dict[str, Any]:
        """Get crop-specific weather impact analysis"""
        # Crop-specific thresholds and recommendations
        crop_info = {
            "wheat": {
                "ideal_temp": (15, 24),
                "ideal_rain": (20, 40),
                "disease_prone": ["stripe rust", "leaf rust", "powdery mildew"],
                "heat_sensitive": True,
                "drought_tolerant": False
            },
            "rice": {
                "ideal_temp": (20, 35),
                "ideal_rain": (40, 70),
                "disease_prone": ["blast", "bacterial leaf blight"],
                "heat_sensitive": False,
                "drought_tolerant": False
            },
            "cotton": {
                "ideal_temp": (25, 35),
                "ideal_rain": (15, 30),
                "disease_prone": ["boll rot", "bacterial blight"],
                "heat_sensitive": False,
                "drought_tolerant": True
            },
            "maize": {
                "ideal_temp": (20, 32),
                "ideal_rain": (25, 40),
                "disease_prone": ["southern leaf blight", "gray leaf spot"],
                "heat_sensitive": True,
                "drought_tolerant": False
            }
        }
        
        # Get crop name in lowercase
        crop_lower = crop_type.lower()
        
        # Find matching crop or use default
        crop_data = None
        for crop_name, data in crop_info.items():
            if crop_name in crop_lower or crop_lower in crop_name:
                crop_data = data
                break
                
        if not crop_data:
            return {
                "impact_summary": "No specific data available for this crop",
                "recommendations": []
            }
            
        # Analyze impact
        min_ideal_temp, max_ideal_temp = crop_data["ideal_temp"]
        min_ideal_rain, max_ideal_rain = crop_data["ideal_rain"]
        
        impact_factors = []
        recommendations = []
        
        # Temperature analysis
        if avg_temp < min_ideal_temp:
            impact_factors.append("Below optimal temperature")
            recommendations.append("Consider protective measures against cold")
        elif avg_temp > max_ideal_temp:
            impact_factors.append("Above optimal temperature")
            if crop_data["heat_sensitive"]:
                impact_factors.append("Heat stress likely")
                recommendations.append("Increase irrigation frequency to mitigate heat stress")
        
        # Rainfall analysis
        if total_rain < min_ideal_rain:
            impact_factors.append("Below optimal rainfall")
            if not crop_data["drought_tolerant"]:
                impact_factors.append("Irrigation required")
                recommendations.append("Schedule irrigation to compensate for rainfall deficit")
        elif total_rain > max_ideal_rain:
            impact_factors.append("Above optimal rainfall")
            recommendations.append("Ensure proper drainage to prevent waterlogging")
            
        # Disease risk analysis
        if disease_risk != "low":
            disease_names = ", ".join(crop_data["disease_prone"])
            impact_factors.append(f"Risk of {disease_names}")
            if disease_risk == "high":
                recommendations.append(f"Monitor for {disease_names} and apply preventive treatments")
        
        # Generate summary
        if impact_factors:
            impact_summary = f"Weather conditions are not ideal for {crop_type}: {', '.join(impact_factors)}"
        else:
            impact_summary = f"Weather conditions are favorable for {crop_type}"
            
        return {
            "impact_summary": impact_summary,
            "recommendations": recommendations,
            "ideal_temperature_range": f"{min_ideal_temp}°C - {max_ideal_temp}°C",
            "ideal_rainfall_range": f"{min_ideal_rain}mm - {max_ideal_rain}mm",
            "current_temperature": f"{avg_temp:.1f}°C",
            "current_rainfall": f"{total_rain:.1f}mm"
        }
    
    def _generate_weather_alerts(
        self, forecasts: List[WeatherForecast], satellite_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate weather alerts based on forecast and satellite data"""
        alerts = []
        
        # Check for extreme temperatures
        for i, forecast in enumerate(forecasts[:3]):  # Check next 3 days
            day_label = "Today" if i == 0 else "Tomorrow" if i == 1 else forecast.date.strftime("%A")
            
            if forecast.temperature_max > 38:
                alerts.append({
                    "type": "extreme_heat",
                    "severity": "high",
                    "day": day_label,
                    "message": f"Extreme heat expected ({forecast.temperature_max:.1f}°C). "
                              f"Protect crops and increase irrigation."
                })
            elif forecast.temperature_max > 35:
                alerts.append({
                    "type": "high_temperature",
                    "severity": "medium",
                    "day": day_label,
                    "message": f"High temperature expected ({forecast.temperature_max:.1f}°C). "
                              f"Monitor sensitive crops and consider afternoon shading."
                })
                
            if forecast.precipitation_mm > 30:
                alerts.append({
                    "type": "heavy_rain",
                    "severity": "high",
                    "day": day_label,
                    "message": f"Heavy rainfall expected ({forecast.precipitation_mm:.1f}mm). "
                              f"Ensure proper drainage and delay chemical applications."
                })
            elif forecast.precipitation_mm > 15:
                alerts.append({
                    "type": "moderate_rain",
                    "severity": "medium",
                    "day": day_label,
                    "message": f"Moderate rainfall expected ({forecast.precipitation_mm:.1f}mm). "
                              f"Plan field operations accordingly."
                })
                
            if forecast.wind_speed_kmh > 40:
                alerts.append({
                    "type": "strong_wind",
                    "severity": "high",
                    "day": day_label,
                    "message": f"Strong winds expected ({forecast.wind_speed_kmh:.1f}km/h). "
                              f"Delay spraying operations and secure structures."
                })
        
        # Add satellite-based alerts
        if satellite_data:
            if satellite_data.get('precipitation', {}).get('forecast_mm', 0) > 50:
                alerts.append({
                    "type": "flood_risk",
                    "severity": "high",
                    "day": "Coming days",
                    "message": "Satellite data indicates high flood risk due to accumulated rainfall. "
                              "Take preventive measures."
                })
            
            if satellite_data.get('soil_moisture', {}).get('value', 50) < 20:
                alerts.append({
                    "type": "drought_conditions",
                    "severity": "medium",
                    "day": "Current",
                    "message": "Satellite data indicates low soil moisture levels. "
                              "Increase irrigation to prevent crop stress."
                })
        
        return alerts
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other agents"""
        if message.get("type") == "weather_request":
            # Handle requests from other agents for weather data
            latitude = message.get("latitude")
            longitude = message.get("longitude")
            
            if latitude is not None and longitude is not None:
                try:
                    forecast_data = await self._get_weather_forecast(latitude, longitude)
                    current_weather = self._format_current_weather(forecast_data[0])
                    
                    return {
                        "success": True,
                        "current_weather": current_weather,
                        "forecast_summary": self._generate_forecast_summary(forecast_data)
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
            else:
                return {"success": False, "error": "Latitude and longitude are required"}
                
        return {"success": False, "error": "Unknown message type"}
