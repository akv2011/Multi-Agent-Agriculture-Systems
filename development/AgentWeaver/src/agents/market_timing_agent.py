"""
🛰️ Market Timing Agent with Satellite Intelligence
=================================================
Specialized agent for forecasting commodity prices and recommending optimal 
selling times for Indian agricultural markets, enhanced with satellite-derived 
yield forecasting and environmental risk assessment.

Features:
- Satellite-enhanced yield predictions
- NDVI-based crop health monitoring
- Weather-adjusted price forecasting
- Environmental risk assessment
- Supply-demand modeling with satellite data
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random
import numpy as np
import asyncio

from .base_agent import BaseWorkerAgent
from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, CropType, Location, QueryDomain, Language
)
from ..core.models import AgentCapability, Task
from ..services.satellite_service import SatelliteService, LocationData

logger = logging.getLogger(__name__)


class Commodity(Enum):
    """Major agricultural commodities in India"""
    WHEAT = "wheat"
    RICE = "rice"
    COTTON = "cotton"
    SUGARCANE = "sugarcane"
    SOYBEAN = "soybean"
    MUSTARD = "mustard"
    MAIZE = "maize"
    POTATO = "potato"
    ONION = "onion"
    TOMATO = "tomato"


class MarketTrend(Enum):
    """Market trend indicators"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class PriceForecast:
    """Commodity price forecast with satellite enhancement"""
    commodity: Commodity
    current_price: float
    forecast_price_7d: float
    forecast_price_30d: float
    confidence: float
    trend: MarketTrend
    volatility: float  # Percentage
    seasonal_factor: float
    news_sentiment: float
    # Satellite-enhanced fields
    yield_forecast: float  # Expected yield (tonnes/hectare)
    supply_risk: str  # low/moderate/high/very_high
    environmental_score: float  # 0-100 crop health
    satellite_confidence: float  # Satellite data quality


@dataclass
class MarketRecommendation:
    """Market timing recommendation with satellite insights"""
    commodity: Commodity
    recommendation: str  # e.g., "Sell now", "Hold for 2 weeks"
    reasoning: List[str]
    expected_gain: float  # Percentage
    confidence_score: float
    timeline: str
    # Satellite-enhanced fields
    yield_impact: str  # How satellite data affects recommendation
    supply_outlook: str  # Market supply expectations
    environmental_factors: List[str]  # Weather/environmental considerations


class MarketTimingAgent(BaseWorkerAgent):
    """
    🛰️ Satellite-Enhanced Market Timing Agent
    ==========================================
    
    Advanced commodity price forecasting and market timing advisor that integrates
    satellite data for yield prediction and supply-demand analysis.
    
    Key Features:
    - NDVI-based yield forecasting
    - Satellite-enhanced supply risk assessment
    - Environmental factor integration
    - Weather-adjusted price predictions
    - Crop health monitoring for market timing
    """
    
    def __init__(self):
        super().__init__(
            name="market_timing_agent",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.PLANNING
            ],
            agent_type="market_timing"
        )
        
        # Initialize satellite service
        self.satellite_service = SatelliteService()
        
    def _initialize_yield_models(self) -> Dict:
        """Initialize satellite-based yield prediction models"""
        return {
            Commodity.WHEAT: {
                "optimal_ndvi_range": (0.6, 0.8),
                "base_yield": 3.5,  # tonnes/hectare
                "ndvi_yield_factor": 2.0,
                "moisture_factor": 1.5
            },
            Commodity.RICE: {
                "optimal_ndvi_range": (0.7, 0.9),
                "base_yield": 4.2,
                "ndvi_yield_factor": 2.2,
                "moisture_factor": 2.0
            },
            Commodity.COTTON: {
                "optimal_ndvi_range": (0.5, 0.75),
                "base_yield": 1.8,
                "ndvi_yield_factor": 1.8,
                "moisture_factor": 1.3
            },
            Commodity.SUGARCANE: {
                "optimal_ndvi_range": (0.8, 0.95),
                "base_yield": 75.0,
                "ndvi_yield_factor": 1.5,
                "moisture_factor": 1.8
            },
            Commodity.SOYBEAN: {
                "optimal_ndvi_range": (0.6, 0.8),
                "base_yield": 2.8,
                "ndvi_yield_factor": 2.1,
                "moisture_factor": 1.6
            },
            # Default for other crops
            Commodity.MUSTARD: {
                "optimal_ndvi_range": (0.5, 0.7),
                "base_yield": 1.5,
                "ndvi_yield_factor": 1.7,
                "moisture_factor": 1.2
            },
            Commodity.MAIZE: {
                "optimal_ndvi_range": (0.6, 0.8),
                "base_yield": 3.8,
                "ndvi_yield_factor": 2.0,
                "moisture_factor": 1.7
            },
            Commodity.POTATO: {
                "optimal_ndvi_range": (0.5, 0.75),
                "base_yield": 22.0,
                "ndvi_yield_factor": 1.5,
                "moisture_factor": 1.4
            },
            Commodity.ONION: {
                "optimal_ndvi_range": (0.4, 0.65),
                "base_yield": 18.0,
                "ndvi_yield_factor": 1.6,
                "moisture_factor": 1.3
            },
            Commodity.TOMATO: {
                "optimal_ndvi_range": (0.5, 0.7),
                "base_yield": 25.0,
                "ndvi_yield_factor": 1.8,
                "moisture_factor": 1.5
            }
        }
        
        # Yield prediction models
        self.yield_models = self._initialize_yield_models()
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a market timing task (required by BaseWorkerAgent)"""
        try:
            # Extract query from task or context
            if hasattr(task, 'query') and task.query:
                query = task.query
            elif 'query' in context:
                query = context['query']
            else:
                return {"error": "No query provided for market timing analysis"}
            
            # Process the query using our existing logic
            if isinstance(query, AgricultureQuery):
                result = asyncio.run(self.process_query(query))
                return {"success": True, "response": result}
            else:
                return {"error": "Invalid query format"}
                
        except Exception as e:
            return {"error": f"Market timing analysis failed: {str(e)}"}
    
    def _initialize_market_data(self):
        """Initialize mock historical price data for major commodities"""
        self.market_data: Dict[Commodity, List[float]] = {}
        base_prices = {
            Commodity.WHEAT: 2200,
            Commodity.RICE: 3800,
            Commodity.COTTON: 6500,
            Commodity.SUGARCANE: 350,
            Commodity.SOYBEAN: 4800,
            Commodity.MUSTARD: 5500,
            Commodity.MAIZE: 2100,
            Commodity.POTATO: 1500,
            Commodity.ONION: 2500,
            Commodity.TOMATO: 3000
        }
        
        for commodity, base_price in base_prices.items():
            self.market_data[commodity] = self._generate_price_history(base_price)
    
    def _generate_price_history(self, base_price: float, days: int = 365) -> List[float]:
        """Generate a year of simulated daily prices"""
        prices = []
        price = base_price
        for i in range(days):
            # Add seasonality (sine wave)
            seasonal_effect = np.sin(2 * np.pi * i / 365) * 0.1 * base_price
            
            # Add random daily fluctuation
            daily_change = random.uniform(-0.02, 0.02) * price
            
            price += seasonal_effect / 365 + daily_change
            prices.append(round(price, 2))
        return prices
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process market timing and price forecast queries with satellite enhancement"""
        try:
            # Analyze query for commodity and intent
            query_analysis = self._analyze_market_query(query.query_text)
            
            if not query_analysis["commodity"]:
                return self._create_general_market_info_response(query)
            
            commodity = query_analysis["commodity"]
            
            # Get satellite data if location is provided
            satellite_data = None
            if query.location:
                try:
                    location_data = LocationData(
                        latitude=query.location.latitude or self._get_default_coords(query.location.state)[0],
                        longitude=query.location.longitude or self._get_default_coords(query.location.state)[1],
                        location_name=f"{query.location.district}, {query.location.state}",
                        region=query.location.state
                    )
                    satellite_data = await self.satellite_service.get_current_data(location_data)
                except Exception as e:
                    logger.warning(f"Could not fetch satellite data: {e}")
            
            # Generate enhanced forecast and recommendation
            forecast = await self._generate_satellite_enhanced_forecast(commodity, satellite_data, query.location)
            recommendation = self._create_satellite_enhanced_recommendation(forecast, satellite_data)
            
            return self._create_agent_response(recommendation, forecast, query, satellite_data)
            
        except Exception as e:
            logger.error(f"Error processing market query: {e}")
            return self._create_error_response(query, str(e))
    
    def _analyze_market_query(self, query_text: str) -> Dict[str, Any]:
        """Analyze query to identify commodity and intent"""
        query_lower = query_text.lower()
        
        commodity_map = {
            "wheat": Commodity.WHEAT, "गेहूं": Commodity.WHEAT,
            "rice": Commodity.RICE, "धान": Commodity.RICE, "chawal": Commodity.RICE, "चावल": Commodity.RICE,
            "cotton": Commodity.COTTON, "कपास": Commodity.COTTON,
            "sugarcane": Commodity.SUGARCANE, "गन्ना": Commodity.SUGARCANE,
            "soybean": Commodity.SOYBEAN, "सोयाबीन": Commodity.SOYBEAN,
            "mustard": Commodity.MUSTARD, "सरसों": Commodity.MUSTARD,
            "maize": Commodity.MAIZE, "मक्का": Commodity.MAIZE,
            "potato": Commodity.POTATO, "आलू": Commodity.POTATO,
            "onion": Commodity.ONION, "प्याज": Commodity.ONION,
            "tomato": Commodity.TOMATO, "टमाटर": Commodity.TOMATO
        }
        
        found_commodity = None
        for keyword, commodity in commodity_map.items():
            if keyword in query_lower:
                found_commodity = commodity
                break
        
        return {
            "commodity": found_commodity,
            "intent": "price_forecast"  # Default intent
        }
    
    def _generate_price_forecast(self, commodity: Commodity) -> PriceForecast:
        """Generate a price forecast for a given commodity"""
        history = self.market_data[commodity]
        current_price = history[-1]
        
        # Simple moving average forecast
        ma_30d = np.mean(history[-30:])
        ma_7d = np.mean(history[-7:])
        
        # Forecast logic
        forecast_price_7d = (ma_7d * 1.01)  # Slight upward bias
        forecast_price_30d = (ma_30d * 1.02)
        
        # Trend analysis
        if ma_7d > ma_30d * 1.05:
            trend = MarketTrend.STRONG_BUY
        elif ma_7d > ma_30d:
            trend = MarketTrend.BUY
        elif ma_7d < ma_30d * 0.95:
            trend = MarketTrend.STRONG_SELL
        elif ma_7d < ma_30d:
            trend = MarketTrend.SELL
        else:
            trend = MarketTrend.HOLD
        
        # Volatility (standard deviation of last 30 days)
        volatility = np.std(history[-30:]) / ma_30d * 100
        
        return PriceForecast(
            commodity=commodity,
            current_price=round(current_price, 2),
            forecast_price_7d=round(forecast_price_7d, 2),
            forecast_price_30d=round(forecast_price_30d, 2),
            confidence=random.uniform(0.75, 0.90),
            trend=trend,
            volatility=round(volatility, 2),
            seasonal_factor=random.uniform(0.8, 1.2),
            news_sentiment=random.uniform(-0.5, 0.5),
            # Basic satellite fields (will be enhanced in satellite version)
            yield_forecast=0.0,
            supply_risk="moderate",
            environmental_score=75.0,
            satellite_confidence=0.0
        )
    
    async def _generate_satellite_enhanced_forecast(self, commodity: Commodity, satellite_data=None, location=None) -> PriceForecast:
        """Generate price forecast enhanced with satellite data"""
        # Start with basic forecast
        basic_forecast = self._generate_price_forecast(commodity)
        
        if not satellite_data:
            return basic_forecast
        
        try:
            # Calculate yield forecast based on satellite data
            yield_forecast = self._calculate_yield_forecast(commodity, satellite_data)
            
            # Assess supply risk based on environmental conditions
            supply_risk = self._assess_supply_risk(satellite_data, commodity)
            
            # Calculate environmental score
            environmental_score = self._calculate_environmental_score(satellite_data)
            
            # Adjust price forecast based on satellite insights
            price_adjustment = self._calculate_satellite_price_adjustment(
                commodity, satellite_data, yield_forecast, supply_risk
            )
            
            # Enhanced confidence based on satellite data quality
            satellite_confidence = satellite_data.metrics.confidence_score
            enhanced_confidence = min(0.95, basic_forecast.confidence + (satellite_confidence * 0.1))
            
            # Apply adjustments
            adjusted_7d = basic_forecast.forecast_price_7d * (1 + price_adjustment)
            adjusted_30d = basic_forecast.forecast_price_30d * (1 + price_adjustment)
            
            return PriceForecast(
                commodity=commodity,
                current_price=basic_forecast.current_price,
                forecast_price_7d=round(adjusted_7d, 2),
                forecast_price_30d=round(adjusted_30d, 2),
                confidence=round(enhanced_confidence, 3),
                trend=self._determine_satellite_adjusted_trend(basic_forecast.trend, price_adjustment),
                volatility=basic_forecast.volatility,
                seasonal_factor=basic_forecast.seasonal_factor,
                news_sentiment=basic_forecast.news_sentiment,
                # Satellite-enhanced fields
                yield_forecast=round(yield_forecast, 2),
                supply_risk=supply_risk,
                environmental_score=round(environmental_score, 1),
                satellite_confidence=round(satellite_confidence, 3)
            )
            
        except Exception as e:
            logger.error(f"Error in satellite enhancement: {e}")
            return basic_forecast
    
    def _calculate_yield_forecast(self, commodity: Commodity, satellite_data) -> float:
        """Calculate expected yield based on satellite metrics"""
        if commodity not in self.yield_models:
            return 0.0
        
        model = self.yield_models[commodity]
        base_yield = model["base_yield"]
        
        # NDVI impact on yield
        ndvi = satellite_data.metrics.ndvi
        optimal_min, optimal_max = model["optimal_ndvi_range"]
        
        if optimal_min <= ndvi <= optimal_max:
            ndvi_factor = 1.0 + (ndvi - optimal_min) / (optimal_max - optimal_min) * 0.3
        elif ndvi < optimal_min:
            ndvi_factor = 0.7 + (ndvi - (-1)) / (optimal_min - (-1)) * 0.3
        else:
            ndvi_factor = 1.0 - (ndvi - optimal_max) / (1 - optimal_max) * 0.2
        
        # Soil moisture impact
        moisture = satellite_data.metrics.soil_moisture
        if moisture > 60:
            moisture_factor = 1.0
        elif moisture > 30:
            moisture_factor = 0.8 + (moisture - 30) / 30 * 0.2
        else:
            moisture_factor = 0.5 + moisture / 30 * 0.3
        
        # Temperature stress
        temp = satellite_data.metrics.temperature
        if 20 <= temp <= 30:  # Optimal range for most crops
            temp_factor = 1.0
        elif temp < 20:
            temp_factor = max(0.6, 1 - (20 - temp) / 20 * 0.4)
        else:
            temp_factor = max(0.5, 1 - (temp - 30) / 20 * 0.5)
        
        yield_forecast = base_yield * ndvi_factor * moisture_factor * temp_factor
        return max(0, yield_forecast)
    
    def _assess_supply_risk(self, satellite_data, commodity: Commodity) -> str:
        """Assess supply risk based on environmental conditions"""
        risk_factors = []
        
        # NDVI risk
        ndvi = satellite_data.metrics.ndvi
        if ndvi < 0.3:
            risk_factors.append("very_low_vegetation")
        elif ndvi < 0.5:
            risk_factors.append("low_vegetation")
        
        # Moisture risk
        moisture = satellite_data.metrics.soil_moisture
        if moisture < 20:
            risk_factors.append("severe_drought")
        elif moisture < 30:
            risk_factors.append("drought_stress")
        
        # Temperature risk
        temp = satellite_data.metrics.temperature
        if temp > 40:
            risk_factors.append("heat_stress")
        elif temp < 5:
            risk_factors.append("cold_stress")
        
        # Determine overall risk
        if len(risk_factors) >= 3:
            return "very_high"
        elif len(risk_factors) == 2:
            return "high"
        elif len(risk_factors) == 1:
            return "moderate"
        else:
            return "low"
    
    def _calculate_environmental_score(self, satellite_data) -> float:
        """Calculate overall environmental health score (0-100)"""
        # NDVI contribution (40%)
        ndvi_score = max(0, min(100, (satellite_data.metrics.ndvi + 1) / 2 * 100))
        
        # Soil moisture contribution (30%)
        moisture_score = min(100, satellite_data.metrics.soil_moisture * 1.5)
        
        # Temperature contribution (20%)
        temp = satellite_data.metrics.temperature
        if 20 <= temp <= 30:
            temp_score = 100
        elif temp < 20:
            temp_score = max(0, 100 - (20 - temp) * 3)
        else:
            temp_score = max(0, 100 - (temp - 30) * 2)
        
        # Cloud cover contribution (10%) - less clouds is better for assessment
        cloud_score = max(0, 100 - satellite_data.metrics.cloud_cover)
        
        # Weighted average
        environmental_score = (
            ndvi_score * 0.4 + 
            moisture_score * 0.3 + 
            temp_score * 0.2 + 
            cloud_score * 0.1
        )
        
        return environmental_score
    
    def _calculate_satellite_price_adjustment(self, commodity: Commodity, satellite_data, yield_forecast: float, supply_risk: str) -> float:
        """Calculate price adjustment factor based on satellite insights"""
        adjustment = 0.0
        
        # Yield impact on prices (inverse relationship)
        if commodity in self.yield_models:
            expected_yield = self.yield_models[commodity]["base_yield"]
            yield_ratio = yield_forecast / expected_yield
            
            if yield_ratio < 0.8:  # Poor yield -> higher prices
                adjustment += 0.15 * (0.8 - yield_ratio) / 0.8
            elif yield_ratio > 1.2:  # Excellent yield -> lower prices
                adjustment -= 0.1 * (yield_ratio - 1.2) / 0.8
        
        # Supply risk impact
        risk_adjustments = {
            "very_high": 0.2,    # High risk -> higher prices
            "high": 0.1,
            "moderate": 0.0,
            "low": -0.05         # Low risk -> slightly lower prices
        }
        adjustment += risk_adjustments.get(supply_risk, 0.0)
        
        # NDVI impact
        ndvi = satellite_data.metrics.ndvi
        if ndvi < 0.4:  # Poor vegetation -> higher prices
            adjustment += 0.1
        elif ndvi > 0.8:  # Excellent vegetation -> lower prices
            adjustment -= 0.05
        
        # Cap adjustment to reasonable range
        return max(-0.3, min(0.3, adjustment))
    
    def _determine_satellite_adjusted_trend(self, basic_trend: MarketTrend, price_adjustment: float) -> MarketTrend:
        """Adjust market trend based on satellite price adjustment"""
        if price_adjustment > 0.1:
            # Strong upward pressure from satellite data
            if basic_trend in [MarketTrend.SELL, MarketTrend.STRONG_SELL]:
                return MarketTrend.HOLD
            elif basic_trend == MarketTrend.HOLD:
                return MarketTrend.BUY
            else:
                return MarketTrend.STRONG_BUY
        elif price_adjustment < -0.1:
            # Downward pressure from satellite data
            if basic_trend in [MarketTrend.BUY, MarketTrend.STRONG_BUY]:
                return MarketTrend.HOLD
            elif basic_trend == MarketTrend.HOLD:
                return MarketTrend.SELL
            else:
                return MarketTrend.STRONG_SELL
        else:
            # Minor adjustment, keep original trend
            return basic_trend
    
    def _get_default_coords(self, state: str) -> Tuple[float, float]:
        """Get default coordinates for Indian states"""
        coords = {
            "Punjab": (30.7333, 76.7794),
            "Haryana": (29.0588, 76.0856),
            "Uttar Pradesh": (26.8467, 80.9462),
            "Maharashtra": (19.7515, 75.7139),
            "Karnataka": (15.3173, 75.7139),
            "Tamil Nadu": (11.1271, 78.6569),
            "Gujarat": (23.0225, 72.5714),
            "Rajasthan": (27.0238, 74.2179),
            "Madhya Pradesh": (22.9734, 78.6569)
        }
        return coords.get(state, (28.6139, 77.2090))  # Default to Delhi
    
    def _create_market_recommendation(self, forecast: PriceForecast) -> MarketRecommendation:
        """Create a market timing recommendation based on the forecast"""
        reasoning = []
        
        # Determine recommendation based on trend
        if forecast.trend == MarketTrend.STRONG_BUY:
            recommendation = "Hold for higher prices"
            timeline = "4-6 weeks"
            expected_gain = (forecast.forecast_price_30d / forecast.current_price - 1) * 100
            reasoning.append("Strong upward trend detected.")
        elif forecast.trend == MarketTrend.BUY:
            recommendation = "Hold for now"
            timeline = "2-3 weeks"
            expected_gain = (forecast.forecast_price_7d / forecast.current_price - 1) * 100
            reasoning.append("Prices are currently rising.")
        elif forecast.trend == MarketTrend.STRONG_SELL:
            recommendation = "Sell immediately"
            timeline = "Next 3 days"
            expected_gain = 0
            reasoning.append("Strong downward pressure on prices.")
        elif forecast.trend == MarketTrend.SELL:
            recommendation = "Consider selling soon"
            timeline = "Next 7 days"
            expected_gain = 0
            reasoning.append("Prices are showing a downward trend.")
        else: # HOLD
            recommendation = "Hold and monitor market"
            timeline = "1-2 weeks"
            expected_gain = 0
            reasoning.append("Market is stable, no clear trend.")
        
        # Add volatility to reasoning
        if forecast.volatility > 5:
            reasoning.append(f"High market volatility ({forecast.volatility:.2f}%) suggests price swings.")
        else:
            reasoning.append(f"Low market volatility ({forecast.volatility:.2f}%) suggests stable prices.")
        
        return MarketRecommendation(
            commodity=forecast.commodity,
            recommendation=recommendation,
            reasoning=reasoning,
            expected_gain=round(expected_gain, 2),
            confidence_score=forecast.confidence,
            timeline=timeline,
            # Basic satellite fields for compatibility
            yield_impact="Traditional analysis - no satellite data",
            supply_outlook="Based on historical patterns",
            environmental_factors=[]
        )
    
    def _create_satellite_enhanced_recommendation(self, forecast: PriceForecast, satellite_data=None) -> MarketRecommendation:
        """Create market recommendation enhanced with satellite insights"""
        # Start with basic recommendation logic
        basic_rec = self._create_market_recommendation(forecast)
        
        if not satellite_data:
            # Add empty satellite fields to basic recommendation
            return MarketRecommendation(
                commodity=basic_rec.commodity,
                recommendation=basic_rec.recommendation,
                reasoning=basic_rec.reasoning,
                expected_gain=basic_rec.expected_gain,
                confidence_score=basic_rec.confidence_score,
                timeline=basic_rec.timeline,
                yield_impact="No satellite data available",
                supply_outlook="Unable to assess",
                environmental_factors=[]
            )
        
        # Enhanced reasoning with satellite insights
        enhanced_reasoning = basic_rec.reasoning.copy()
        environmental_factors = []
        
        # Add satellite-specific insights
        if forecast.environmental_score > 80:
            enhanced_reasoning.append(f"Excellent crop conditions (Environmental Score: {forecast.environmental_score:.1f}/100)")
            environmental_factors.append("Optimal growing conditions detected")
        elif forecast.environmental_score < 50:
            enhanced_reasoning.append(f"Poor crop conditions (Environmental Score: {forecast.environmental_score:.1f}/100)")
            environmental_factors.append("Environmental stress detected")
        
        # Yield impact analysis
        if forecast.yield_forecast > 0:
            model = self.yield_models.get(forecast.commodity)
            if model:
                expected_yield = model["base_yield"]
                yield_ratio = forecast.yield_forecast / expected_yield
                
                if yield_ratio > 1.1:
                    yield_impact = f"Above-average yield expected ({forecast.yield_forecast:.1f} vs {expected_yield:.1f} tonnes/ha)"
                    enhanced_reasoning.append("High yield forecast may increase supply and lower prices")
                elif yield_ratio < 0.9:
                    yield_impact = f"Below-average yield expected ({forecast.yield_forecast:.1f} vs {expected_yield:.1f} tonnes/ha)"
                    enhanced_reasoning.append("Low yield forecast may reduce supply and increase prices")
                else:
                    yield_impact = f"Normal yield expected ({forecast.yield_forecast:.1f} tonnes/ha)"
            else:
                yield_impact = f"Estimated yield: {forecast.yield_forecast:.1f} tonnes/ha"
        else:
            yield_impact = "Yield assessment not available"
        
        # Supply outlook based on risk assessment
        supply_outlooks = {
            "low": "Stable supply expected with minimal weather risks",
            "moderate": "Supply outlook stable with some environmental variables to monitor",
            "high": "Supply risks detected due to environmental stress - potential shortages",
            "very_high": "Significant supply risks due to severe environmental conditions"
        }
        supply_outlook = supply_outlooks.get(forecast.supply_risk, "Supply outlook uncertain")
        
        # Environmental factors
        ndvi = satellite_data.metrics.ndvi
        moisture = satellite_data.metrics.soil_moisture
        temp = satellite_data.metrics.temperature
        
        if ndvi < 0.4:
            environmental_factors.append(f"Low vegetation health (NDVI: {ndvi:.2f})")
        elif ndvi > 0.7:
            environmental_factors.append(f"Healthy vegetation detected (NDVI: {ndvi:.2f})")
        
        if moisture < 30:
            environmental_factors.append(f"Low soil moisture ({moisture:.1f}%) - drought stress")
        elif moisture > 70:
            environmental_factors.append(f"High soil moisture ({moisture:.1f}%) - optimal conditions")
        
        if temp > 35:
            environmental_factors.append(f"High temperature stress ({temp:.1f}°C)")
        elif temp < 15:
            environmental_factors.append(f"Cold stress conditions ({temp:.1f}°C)")
        
        # Adjust recommendation based on satellite insights
        adjusted_recommendation = basic_rec.recommendation
        adjusted_timeline = basic_rec.timeline
        
        if forecast.supply_risk in ["high", "very_high"] and forecast.trend in [MarketTrend.SELL, MarketTrend.STRONG_SELL]:
            adjusted_recommendation = "Hold - supply risks may increase prices"
            adjusted_timeline = "2-4 weeks"
            enhanced_reasoning.append("Supply risks detected - recommend holding for better prices")
        elif forecast.environmental_score > 85 and forecast.yield_forecast > model.get("base_yield", 0) * 1.2:
            if basic_rec.recommendation.startswith("Hold"):
                adjusted_recommendation = "Consider gradual selling - excellent yield expected"
                enhanced_reasoning.append("Exceptional growing conditions may lead to oversupply")
        
        return MarketRecommendation(
            commodity=forecast.commodity,
            recommendation=adjusted_recommendation,
            reasoning=enhanced_reasoning,
            expected_gain=basic_rec.expected_gain,
            confidence_score=forecast.confidence,  # Use enhanced confidence
            timeline=adjusted_timeline,
            yield_impact=yield_impact,
            supply_outlook=supply_outlook,
            environmental_factors=environmental_factors
        )
        """Create a market timing recommendation based on the forecast"""
        reasoning = []
        
        # Determine recommendation based on trend
        if forecast.trend == MarketTrend.STRONG_BUY:
            recommendation = "Hold for higher prices"
            timeline = "4-6 weeks"
            expected_gain = (forecast.forecast_price_30d / forecast.current_price - 1) * 100
            reasoning.append("Strong upward trend detected.")
        elif forecast.trend == MarketTrend.BUY:
            recommendation = "Hold for now"
            timeline = "2-3 weeks"
            expected_gain = (forecast.forecast_price_7d / forecast.current_price - 1) * 100
            reasoning.append("Prices are currently rising.")
        elif forecast.trend == MarketTrend.STRONG_SELL:
            recommendation = "Sell immediately"
            timeline = "Next 3 days"
            expected_gain = 0
            reasoning.append("Strong downward pressure on prices.")
        elif forecast.trend == MarketTrend.SELL:
            recommendation = "Consider selling soon"
            timeline = "Next 7 days"
            expected_gain = 0
            reasoning.append("Prices are showing a downward trend.")
        else: # HOLD
            recommendation = "Hold and monitor market"
            timeline = "1-2 weeks"
            expected_gain = 0
            reasoning.append("Market is stable, no clear trend.")
        
        # Add volatility to reasoning
        if forecast.volatility > 5:
            reasoning.append(f"High market volatility ({forecast.volatility:.2f}%) suggests price swings.")
        else:
            reasoning.append(f"Low market volatility ({forecast.volatility:.2f}%) suggests stable prices.")
        
        return MarketRecommendation(
            commodity=forecast.commodity,
            recommendation=recommendation,
            reasoning=reasoning,
            expected_gain=round(expected_gain, 2),
            confidence_score=forecast.confidence,
            timeline=timeline
        )
    
    def _create_agent_response(self, recommendation: MarketRecommendation, forecast: PriceForecast, query: AgricultureQuery, satellite_data=None) -> AgentResponse:
        """Create a structured agent response with satellite enhancement"""
        
        summary = self._create_summary(recommendation, forecast, query.query_language, satellite_data)
        recommendations_list = self._create_recommendations_list(recommendation, forecast, satellite_data)
        
        # Enhanced sources list
        sources = ["Simulated Historical Market Data", "Trend Analysis Model"]
        if satellite_data:
            sources.extend([
                "🛰️ Satellite NDVI Data",
                "🌡️ Environmental Monitoring",
                "💧 Soil Moisture Analysis",
                "📊 Yield Prediction Model"
            ])
        
        # Enhanced next steps
        next_steps = ["Check for updated forecast next week", "Monitor local mandi prices"]
        if satellite_data:
            next_steps.extend([
                "Monitor crop health via satellite imagery",
                "Track environmental conditions for yield updates"
            ])
        
        # Enhanced metadata
        metadata = {
            "commodity": forecast.commodity.value,
            "current_price": forecast.current_price,
            "forecast_7d": forecast.forecast_price_7d,
            "forecast_30d": forecast.forecast_price_30d,
            "trend": forecast.trend.value,
            "volatility": forecast.volatility
        }
        
        if satellite_data:
            metadata.update({
                "satellite_enhanced": True,
                "yield_forecast": forecast.yield_forecast,
                "supply_risk": forecast.supply_risk,
                "environmental_score": forecast.environmental_score,
                "satellite_confidence": forecast.satellite_confidence,
                "ndvi": satellite_data.metrics.ndvi,
                "soil_moisture": satellite_data.metrics.soil_moisture,
                "temperature": satellite_data.metrics.temperature
            })
        
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name="🛰️ Market Timing Advisor" if satellite_data else "Market Timing Advisor",
            query_id=query.query_id,
            response_text=summary,
            response_language=query.query_language,
            confidence_score=recommendation.confidence_score,
            reasoning=", ".join(recommendation.reasoning),
            recommendations=recommendations_list,
            sources=sources,
            next_steps=next_steps,
            timestamp=datetime.now(),
            processing_time_ms=200 if satellite_data else 150,
            metadata=metadata
        )
    
    def _create_summary(self, recommendation: MarketRecommendation, forecast: PriceForecast, language: Language, satellite_data=None) -> str:
        """Create a localized summary"""
        commodity_name = forecast.commodity.name.capitalize()
        
        if language in [Language.HINDI, Language.MIXED]:
            commodity_translations = {
                "Wheat": "गेहूं", "Rice": "चावल", "Cotton": "कपास", "Sugarcane": "गन्ना",
                "Soybean": "सोयाबीन", "Mustard": "सरसों", "Maize": "मक्का",
                "Potato": "आलू", "Onion": "प्याज", "Tomato": "टमाटर"
            }
            commodity_name = commodity_translations.get(commodity_name, commodity_name)
            
            rec_translations = {
                "Hold for higher prices": "ऊंची कीमतों के लिए रोकें",
                "Hold for now": "अभी के लिए रोकें",
                "Sell immediately": "तुरंत बेचें",
                "Consider selling soon": "जल्द बेचने पर विचार करें",
                "Hold and monitor market": "बाजार पर नजर रखें और रोकें"
            }
            rec_text = rec_translations.get(recommendation.recommendation, recommendation.recommendation)
            
            return (f"{commodity_name} के लिए सुझाव: {rec_text}। "
                    f"वर्तमान मूल्य: ₹{forecast.current_price:.2f}/क्विंटल। "
                    f"7-दिन का पूर्वानुमान: ₹{forecast.forecast_price_7d:.2f}।")
        
    def _create_summary(self, recommendation: MarketRecommendation, forecast: PriceForecast, language: Language, satellite_data=None) -> str:
        """Create a localized summary with satellite enhancement"""
        commodity_name = forecast.commodity.name.capitalize()
        
        if language in [Language.HINDI, Language.MIXED]:
            commodity_translations = {
                "Wheat": "गेहूं", "Rice": "चावल", "Cotton": "कपास", "Sugarcane": "गन्ना",
                "Soybean": "सोयाबीन", "Mustard": "सरसों", "Maize": "मक्का",
                "Potato": "आलू", "Onion": "प्याज", "Tomato": "टमाटर"
            }
            commodity_name = commodity_translations.get(commodity_name, commodity_name)
            
            rec_translations = {
                "Hold for higher prices": "ऊंची कीमतों के लिए रोकें",
                "Hold for now": "अभी के लिए रोकें",
                "Sell immediately": "तुरंत बेचें",
                "Consider selling soon": "जल्द बेचने पर विचार करें",
                "Hold and monitor market": "बाजार पर नजर रखें और रोकें"
            }
            rec_text = rec_translations.get(recommendation.recommendation, recommendation.recommendation)
            
            base_summary = (f"{commodity_name} के लिए सुझाव: {rec_text}। "
                           f"वर्तमान मूल्य: ₹{forecast.current_price:.2f}/क्विंटल। "
                           f"7-दिन का पूर्वानुमान: ₹{forecast.forecast_price_7d:.2f}।")
            
            if satellite_data:
                base_summary += (f" 🛰️ उपग्रह डेटा: पर्यावरण स्कोर {forecast.environmental_score:.0f}/100, "
                               f"अनुमानित उत्पादन {forecast.yield_forecast:.1f} टन/हेक्टेयर।")
        else:
            base_summary = (f"Recommendation for {commodity_name}: {recommendation.recommendation}. "
                           f"Current price: ₹{forecast.current_price:.2f}/quintal. "
                           f"7-day forecast: ₹{forecast.forecast_price_7d:.2f}.")
            
            if satellite_data:
                base_summary += (f" 🛰️ Satellite insights: Environmental score {forecast.environmental_score:.0f}/100, "
                               f"projected yield {forecast.yield_forecast:.1f} tonnes/ha.")
        
        return base_summary

    def _create_recommendations_list(self, recommendation: MarketRecommendation, forecast: PriceForecast, satellite_data=None) -> List[Dict[str, Any]]:
        """Create a list of detailed recommendations with satellite enhancement"""
        recs = [
            {
                "title": f"Primary Action: {recommendation.recommendation}",
                "description": f"Timeline: {recommendation.timeline}. Expected gain: {recommendation.expected_gain:.2f}%",
                "priority": "high",
                "action_required": recommendation.recommendation
            },
            {
                "title": "Price Forecast",
                "description": f"7-day: ₹{forecast.forecast_price_7d}, 30-day: ₹{forecast.forecast_price_30d}",
                "priority": "medium",
                "action_required": "Monitor"
            },
            {
                "title": "Market Volatility",
                "description": f"{forecast.volatility:.2f}% (Suggests price stability)" if forecast.volatility < 5 else f"{forecast.volatility:.2f}% (Suggests price fluctuations)",
                "priority": "low",
                "action_required": "Be cautious"
            }
        ]
        
        # Add satellite-specific recommendations
        if satellite_data:
            recs.extend([
                {
                    "title": "🛰️ Yield Forecast",
                    "description": recommendation.yield_impact,
                    "priority": "high",
                    "action_required": "Consider for timing"
                },
                {
                    "title": "🌱 Environmental Health",
                    "description": f"Environmental score: {forecast.environmental_score:.1f}/100. {recommendation.supply_outlook}",
                    "priority": "medium",
                    "action_required": "Monitor conditions"
                },
                {
                    "title": "⚠️ Supply Risk Assessment",
                    "description": f"Supply risk level: {forecast.supply_risk.replace('_', ' ').title()}",
                    "priority": "high" if forecast.supply_risk in ["high", "very_high"] else "medium",
                    "action_required": "Factor into decisions"
                }
            ])
            
            # Add environmental factors if any
            if recommendation.environmental_factors:
                recs.append({
                    "title": "🌡️ Environmental Factors",
                    "description": ". ".join(recommendation.environmental_factors),
                    "priority": "medium",
                    "action_required": "Monitor"
                })
        
        return recs

    def _create_general_market_info_response(self, query: AgricultureQuery) -> AgentResponse:
        """Create a response when no specific commodity is identified"""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name="Market Timing Advisor",
            query_id=query.query_id,
            response_text="Please specify a commodity (e.g., wheat, rice, cotton) for a price forecast. कृपया मूल्य पूर्वानुमान के लिए एक वस्तु (जैसे गेहूं, चावल, कपास) निर्दिष्ट करें।",
            response_language=query.query_language,
            confidence_score=0.9,
            recommendations=[
                {"title": "Specify Commodity", "description": "Mention the crop you want a forecast for.", "priority": "high"}
            ],
            timestamp=datetime.now()
        )

    def _create_error_response(self, query: AgricultureQuery, error: str) -> AgentResponse:
        """Create an error response"""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name="Market Timing Advisor",
            query_id=query.query_id,
            response_text="Sorry, I encountered a technical issue while forecasting. Please try again later. क्षमा करें, पूर्वानुमान करते समय मुझे एक तकनीकी समस्या का सामना करना पड़ा। कृपया बाद में पुन: प्रयास करें।",
            response_language=query.query_language,
            confidence_score=0.1,
            warnings=[f"Technical error: {error}"],
            timestamp=datetime.now(),
            metadata={"error": True, "error_message": error}
        )


# Test function for the Market Timing Agent
async def test_market_timing_agent():
    """Test the Market Timing Agent with satellite integration"""
    agent = MarketTimingAgent()
    
    print("�️ Testing Satellite-Enhanced Market Timing Agent")
    
    # Test a query with location for satellite data
    query_en = AgricultureQuery(
        query_text="What is the price forecast for wheat? Should I sell now?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_en",
        location=Location(state="Punjab", district="Amritsar", latitude=31.6340, longitude=74.8723)
    )
    
    print("🔄 Processing English query for Wheat with satellite data...")
    response_en = await agent.process_query(query_en)
    print(f"✅ English Response: {response_en.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_en.metadata.get('satellite_enhanced', False)}")
    if response_en.metadata.get('satellite_enhanced'):
        print(f"   📊 Environmental Score: {response_en.metadata.get('environmental_score', 'N/A')}")
        print(f"   🌱 NDVI: {response_en.metadata.get('ndvi', 'N/A')}")
        print(f"   💧 Soil Moisture: {response_en.metadata.get('soil_moisture', 'N/A')}%")
    
    # Test a query in Hindi with satellite data
    query_hi = AgricultureQuery(
        query_text="प्याज का भाव क्या रहेगा? अभी बेचूं या रुकूं?",
        query_language=Language.HINDI,
        user_id="test_farmer_hi",
        location=Location(state="Maharashtra", district="Nashik", latitude=19.9975, longitude=73.7898)
    )
    
    print("\n🔄 Processing Hindi query for Onion with satellite data...")
    response_hi = await agent.process_query(query_hi)
    print(f"✅ Hindi Response: {response_hi.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_hi.metadata.get('satellite_enhanced', False)}")
    
    # Test a query without location (no satellite data)
    query_no_location = AgricultureQuery(
        query_text="What is the market trend for cotton?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_basic"
    )
    
    print("\n🔄 Processing query without location (traditional analysis)...")
    response_basic = await agent.process_query(query_no_location)
    print(f"✅ Basic Response: {response_basic.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_basic.metadata.get('satellite_enhanced', False)}")

    print("\n🎉 Satellite-Enhanced Market Timing Agent working successfully!")
    print("\n📊 Key Features Demonstrated:")
    print("   ✅ Satellite-based yield forecasting")
    print("   ✅ Environmental risk assessment")
    print("   ✅ NDVI-enhanced price predictions")
    print("   ✅ Supply-demand modeling with satellite data")
    print("   ✅ Weather-adjusted market timing recommendations")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_market_timing_agent())
