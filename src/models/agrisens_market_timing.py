"""
<<<<<<< HEAD
AgriMitr Market Timing Model
=======
AgriSens Market Timing Model
>>>>>>> upstream/main
===========================

Advanced predictive model for agricultural market analysis and optimal selling time determination.
Leverages satellite data, historical market trends, and machine learning to provide price forecasts
and selling window recommendations.

Features:
- Price trend analysis with seasonal adjustments
- Supply-demand modeling based on satellite-derived yield estimates
- Price volatility prediction
- Market seasonality patterns
- Risk-adjusted profit optimization
- Satellite-based regional supply forecasting
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)

# Market timing constants
PRICE_VOLATILITY_THRESHOLD = 0.15  # 15% price variation
SEASONAL_ADJUSTMENT_FACTOR = 0.08  # 8% seasonal adjustment
RISK_PREMIUM = 0.05  # 5% risk premium

# Price seasonality patterns (normalized monthly indices, 1.0 = average)
PRICE_SEASONALITY = {
    "rice": [0.94, 0.92, 0.90, 0.92, 0.97, 1.05, 1.08, 1.10, 1.07, 1.03, 1.0, 0.96],
    "wheat": [0.95, 0.92, 0.90, 0.93, 0.98, 1.05, 1.12, 1.15, 1.10, 1.05, 1.0, 0.98],
    "cotton": [1.02, 1.05, 1.07, 1.10, 1.12, 1.08, 1.05, 1.0, 0.92, 0.88, 0.90, 0.97],
    "sugarcane": [1.0, 1.02, 1.05, 1.07, 1.05, 1.02, 1.0, 0.98, 0.96, 0.95, 0.97, 0.98],
    "soybean": [0.97, 0.95, 0.93, 0.95, 1.0, 1.05, 1.10, 1.12, 1.07, 1.03, 1.0, 0.98],
    "maize": [0.94, 0.92, 0.95, 0.98, 1.05, 1.10, 1.12, 1.08, 1.05, 1.0, 0.96, 0.95],
    "potato": [1.15, 1.10, 1.0, 0.90, 0.85, 0.88, 0.92, 0.95, 1.0, 1.05, 1.10, 1.18],
    "onion": [0.85, 0.90, 1.0, 1.10, 1.15, 1.05, 0.95, 0.92, 0.95, 1.0, 1.05, 0.95],
    "tomato": [0.90, 0.95, 1.05, 1.15, 1.20, 1.10, 1.0, 0.90, 0.85, 0.90, 0.95, 1.0],
}

# Historical volatility by crop (standard deviation of monthly price changes)
PRICE_VOLATILITY = {
    "rice": 0.08,
    "wheat": 0.07,
    "cotton": 0.12,
    "sugarcane": 0.06,
    "soybean": 0.14,
    "maize": 0.11,
    "potato": 0.22,
    "onion": 0.35,
    "tomato": 0.40,
}


class MarketTimingModel:
    """
    ML-based model for agricultural market timing and price forecasting
    """
    
    def __init__(self):
        """Initialize the market timing model"""
<<<<<<< HEAD
        logger.info("Initializing AgriMitr Market Timing Model")
=======
        logger.info("Initializing AgriSens Market Timing Model")
>>>>>>> upstream/main
        
    def forecast_price_trends(self, 
                            crop_type: str,
                            current_price: float,
                            months_ahead: int = 3,
                            ) -> Dict[str, Any]:
        """
        Forecast price trends for the specified crop
        
        Args:
            crop_type: Type of crop (rice, wheat, etc.)
            current_price: Current market price (₹ per quintal)
            months_ahead: Number of months to forecast (default: 3)
            
        Returns:
            Dictionary with price forecasts and confidence levels
        """
        crop_type = crop_type.lower()
        
        # Get seasonality pattern
        if crop_type not in PRICE_SEASONALITY:
            logger.warning(f"Crop type {crop_type} not found in seasonality data. Using generic pattern.")
            seasonality = [1.0 for _ in range(12)]
        else:
            seasonality = PRICE_SEASONALITY[crop_type]
        
        # Get volatility
        if crop_type not in PRICE_VOLATILITY:
            volatility = 0.10  # Default volatility
        else:
            volatility = PRICE_VOLATILITY[crop_type]
        
        # Current month (0-11)
        current_month = datetime.now().month - 1
        
        # Generate forecasts
        forecasts = []
        for i in range(months_ahead + 1):  # Include current month
            forecast_month = (current_month + i) % 12
            
            # Apply seasonal adjustment
            seasonal_factor = seasonality[forecast_month]
            
            # Calculate expected price
            expected_price = current_price * seasonal_factor
            
            # Add random noise based on volatility
            noise_factor = np.random.normal(0, volatility)
            price_with_noise = expected_price * (1 + noise_factor)
            
            # Calculate prediction interval
            lower_bound = expected_price * (1 - volatility * 1.96)  # 95% confidence interval
            upper_bound = expected_price * (1 + volatility * 1.96)
            
            forecasts.append({
                "month": (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m"),
                "expected_price": round(expected_price, 2),
                "predicted_price": round(price_with_noise, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "confidence": "medium"
            })
        
        return {
            "crop": crop_type,
            "current_price": current_price,
            "forecasts": forecasts,
            "seasonality_impact": "high" if max(seasonality) - min(seasonality) > 0.2 else "medium",
            "volatility": volatility,
            "price_trend": self._determine_trend(forecasts)
        }
    
    def _determine_trend(self, forecasts: List[Dict]) -> str:
        """Determine price trend direction from forecast data"""
        if len(forecasts) < 2:
            return "stable"
            
        first_price = forecasts[0]["expected_price"]
        last_price = forecasts[-1]["expected_price"]
        
        percent_change = (last_price - first_price) / first_price
        
        if percent_change > 0.05:
            return "increasing"
        elif percent_change < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def analyze_market_supply_demand(self, 
                                   crop_type: str,
                                   location_data: Dict,
                                   satellite_data: Optional[Dict] = None) -> Dict:
        """
        Analyze supply-demand dynamics based on satellite data and market information
        
        Args:
            crop_type: Type of crop
            location_data: Geographic location data
            satellite_data: Optional satellite imagery data
            
        Returns:
            Supply-demand analysis and market outlook
        """
        crop_type = crop_type.lower()
        
        # Default supply-demand balance (0 = perfectly balanced, positive = oversupply, negative = shortage)
        supply_demand_balance = 0.0
        
        # Extract location information
        region = location_data.get("region", "unknown")
        
        # Process satellite data if available
        satellite_supply_indicator = 0
        satellite_confidence = "low"
        
        if satellite_data:
            # Calculate regional supply indicator from satellite data
            ndvi_data = satellite_data.get("ndvi", {})
            ndvi_values = ndvi_data.get("values", [0.5])
            avg_ndvi = np.mean(ndvi_values) if ndvi_values else 0.5
            
            # Higher NDVI generally indicates better crop health and higher yields
            # Scale from -1.0 to 1.0 (shortage to surplus)
            satellite_supply_indicator = (avg_ndvi - 0.4) * 2.5
            satellite_supply_indicator = max(-1.0, min(1.0, satellite_supply_indicator))
            
            satellite_confidence = "medium" if len(ndvi_values) > 5 else "low"
            
            # Adjust supply-demand balance based on satellite data
            supply_demand_weight = 0.6  # Weight of satellite data in overall assessment
            supply_demand_balance += satellite_supply_indicator * supply_demand_weight
        
        # Apply seasonal adjustment based on current month
        current_month = datetime.now().month - 1
        if crop_type in PRICE_SEASONALITY:
            seasonal_factor = PRICE_SEASONALITY[crop_type][current_month]
            # Invert seasonal price factor to get supply indication
            # (higher prices usually indicate lower supply)
            seasonal_supply_indicator = -1 * (seasonal_factor - 1.0) * 2
            supply_demand_balance += seasonal_supply_indicator * 0.4
        
        # Determine market signals
        market_signals = []
        if supply_demand_balance > 0.3:
            market_signals.append("Regional oversupply likely")
        elif supply_demand_balance < -0.3:
            market_signals.append("Regional supply shortage possible")
            
        if crop_type in PRICE_VOLATILITY and PRICE_VOLATILITY[crop_type] > 0.15:
            market_signals.append("High historical price volatility")
        
        # Determine market outlook
        outlook = "neutral"
        if supply_demand_balance > 0.5:
            outlook = "bearish"  # Oversupply, prices likely to decrease
        elif supply_demand_balance < -0.5:
            outlook = "bullish"  # Shortage, prices likely to increase
        
        return {
            "crop": crop_type,
            "region": region,
            "supply_demand_balance": round(supply_demand_balance, 2),
            "satellite_supply_indicator": round(satellite_supply_indicator, 2) if satellite_data else None,
            "satellite_data_confidence": satellite_confidence if satellite_data else "none",
            "market_signals": market_signals,
            "market_outlook": outlook
        }
    
    def calculate_optimal_selling_window(self,
                                       crop_type: str,
                                       current_price: float,
                                       harvest_date: Optional[str] = None,
                                       storage_cost_monthly: float = 50.0,  # ₹ per quintal per month
                                       risk_tolerance: str = "moderate",
                                       satellite_data: Optional[Dict] = None) -> Dict:
        """
        Calculate the optimal selling window for maximizing returns
        
        Args:
            crop_type: Type of crop
            current_price: Current market price (₹ per quintal)
            harvest_date: Harvest date (YYYY-MM-DD) or None if already harvested
            storage_cost_monthly: Monthly storage cost per quintal
            risk_tolerance: Risk tolerance level (low, moderate, high)
            satellite_data: Optional satellite imagery data
            
        Returns:
            Optimal selling window recommendations
        """
        crop_type = crop_type.lower()
        
        # Set today as default harvest date if none provided
        if not harvest_date:
            harvest_date = datetime.now().strftime("%Y-%m-%d")
            
        harvest_date_obj = datetime.strptime(harvest_date, "%Y-%m-%d")
        current_date = datetime.now()
        
        # For crops not yet harvested, adjust start of selling window
        days_to_harvest = max(0, (harvest_date_obj - current_date).days)
        
        # Get price forecast
        forecast_months = 6
        price_forecast = self.forecast_price_trends(
            crop_type=crop_type,
            current_price=current_price,
            months_ahead=forecast_months
        )
        
        forecasts = price_forecast.get("forecasts", [])
        
        # Calculate expected value for each month considering storage costs
        selling_options = []
        cumulative_storage_cost = 0
        
        for i, forecast in enumerate(forecasts):
            if i * 30 < days_to_harvest:
                continue  # Skip months before harvest
                
            cumulative_storage_cost += storage_cost_monthly if i > 0 else 0
            
            expected_price = forecast["expected_price"]
            lower_bound = forecast["lower_bound"]
            
            # Calculate risk-adjusted price based on risk tolerance
            risk_factor = 0.3 if risk_tolerance == "low" else 0.1 if risk_tolerance == "high" else 0.2
            risk_adjusted_price = expected_price * (1 - risk_factor) + lower_bound * risk_factor
            
            # Calculate net return after storage costs
            net_return = risk_adjusted_price - cumulative_storage_cost
            
            # Calculate price volatility penalty
            if crop_type in PRICE_VOLATILITY:
                volatility = PRICE_VOLATILITY[crop_type]
                volatility_penalty = current_price * volatility * (i + 1) * 0.1
            else:
                volatility_penalty = current_price * 0.1 * (i + 1) * 0.1
            
            # Apply risk tolerance to volatility penalty
            if risk_tolerance == "low":
                volatility_penalty *= 2.0
            elif risk_tolerance == "high":
                volatility_penalty *= 0.5
                
            risk_adjusted_net_return = net_return - volatility_penalty
                
            selling_options.append({
                "month": forecast["month"],
                "expected_price": expected_price,
                "storage_cost": round(cumulative_storage_cost, 2),
                "net_return": round(net_return, 2),
                "risk_adjusted_return": round(risk_adjusted_net_return, 2),
                "price_volatility": "high" if volatility > 0.15 else "medium" if volatility > 0.08 else "low"
            })
        
        # Find month with highest expected return
        if not selling_options:
            optimal_month = {
                "month": datetime.now().strftime("%Y-%m"),
                "expected_price": current_price,
                "recommendation": "sell_immediately"
            }
        else:
            # Sort by risk-adjusted return
            selling_options.sort(key=lambda x: x["risk_adjusted_return"], reverse=True)
            optimal_month = selling_options[0]
            
            # Determine recommendation
            optimal_date = datetime.strptime(optimal_month["month"], "%Y-%m")
            months_to_optimal = (optimal_date.year - current_date.year) * 12 + optimal_date.month - current_date.month
            
            if months_to_optimal == 0:
                optimal_month["recommendation"] = "sell_immediately"
            else:
                optimal_month["recommendation"] = "hold_for_future_sale"
        
        return {
            "crop": crop_type,
            "current_price": current_price,
            "optimal_selling_month": optimal_month["month"],
            "expected_optimal_price": round(optimal_month["expected_price"], 2),
            "recommendation": optimal_month["recommendation"],
            "selling_options": selling_options,
            "risk_tolerance": risk_tolerance,
            "storage_cost_monthly": storage_cost_monthly,
            "price_trend": price_forecast["price_trend"],
            "confidence": "medium"
        }
    
    def analyze_satellite_yield_impact(self, satellite_data: Dict) -> Dict:
        """
        Analyze satellite data to assess yield potential and market impact
        
        Args:
            satellite_data: Dictionary containing satellite data
            
        Returns:
            Yield impact assessment and market implications
        """
        if not satellite_data:
            return {
                "yield_estimate": "average",
                "confidence": "very_low",
                "market_impact": "neutral"
            }
        
        # Extract NDVI (primary indicator of crop health)
        ndvi_data = satellite_data.get("ndvi", {})
        ndvi_values = ndvi_data.get("values", [])
        
        if not ndvi_values:
            return {
                "yield_estimate": "average",
                "confidence": "very_low",
                "market_impact": "neutral"
            }
        
        avg_ndvi = np.mean(ndvi_values)
        
        # Calculate yield potential based on NDVI
        # NDVI typically ranges from -0.1 to 0.9 for vegetation
        # Higher NDVI correlates with higher yield potential
        yield_potential = 0.0
        
        if avg_ndvi < 0.2:
            yield_potential = -0.3  # 30% below average
            yield_estimate = "very_poor"
        elif avg_ndvi < 0.4:
            yield_potential = -0.15  # 15% below average
            yield_estimate = "below_average"
        elif avg_ndvi < 0.5:
            yield_potential = 0.0  # average
            yield_estimate = "average"
        elif avg_ndvi < 0.65:
            yield_potential = 0.15  # 15% above average
            yield_estimate = "above_average"
        else:
            yield_potential = 0.3  # 30% above average
            yield_estimate = "excellent"
        
        # Determine market impact (inverse relationship to yield)
        # Higher yields tend to lower prices
        market_impact = -yield_potential
        
        impact_description = "neutral"
        if market_impact > 0.2:
            impact_description = "strongly_bullish"
        elif market_impact > 0.1:
            impact_description = "bullish"
        elif market_impact < -0.2:
            impact_description = "strongly_bearish"
        elif market_impact < -0.1:
            impact_description = "bearish"
            
        # Determine confidence level based on data quality
        confidence = "medium" if len(ndvi_values) > 10 else "low"
            
        return {
            "yield_estimate": yield_estimate,
            "yield_deviation": f"{round(yield_potential * 100, 1)}%",
            "confidence": confidence,
            "market_impact": impact_description,
            "ndvi_average": round(avg_ndvi, 2),
            "data_points": len(ndvi_values)
        }
    
    def generate_satellite_enhanced_market_timing(self,
                                               crop_type: str,
                                               location_data: Dict,
                                               current_price: float,
                                               harvest_date: Optional[str] = None,
                                               satellite_data: Dict = None) -> Dict:
        """
        Generate comprehensive market timing recommendations enhanced with satellite data
        
        Args:
            crop_type: Type of crop
            location_data: Geographic location data
            current_price: Current market price (₹ per quintal)
            harvest_date: Optional harvest date (YYYY-MM-DD)
            satellite_data: Optional satellite imagery data
            
        Returns:
            Complete market timing plan with forecasts, analysis and recommendations
        """
        results = {}
        
        # Generate price forecast
        results["price_forecast"] = self.forecast_price_trends(
            crop_type=crop_type,
            current_price=current_price
        )
        
        # Analyze supply-demand
        results["supply_demand_analysis"] = self.analyze_market_supply_demand(
            crop_type=crop_type,
            location_data=location_data,
            satellite_data=satellite_data
        )
        
        # Calculate optimal selling window
        results["selling_strategy"] = self.calculate_optimal_selling_window(
            crop_type=crop_type,
            current_price=current_price,
            harvest_date=harvest_date,
            satellite_data=satellite_data
        )
        
        # Add satellite yield impact analysis if data available
        if satellite_data:
            results["satellite_yield_assessment"] = self.analyze_satellite_yield_impact(satellite_data)
        
        # Generate key recommendations
        recommendations = []
        
        # Pricing recommendation
        if results["selling_strategy"]["recommendation"] == "sell_immediately":
            recommendations.append(
                "Current market conditions are favorable for selling. Consider selling your produce now "
                "to maximize returns."
            )
        else:
            optimal_month = results["selling_strategy"]["optimal_selling_month"]
            expected_price = results["selling_strategy"]["expected_optimal_price"]
            recommendations.append(
                f"Consider holding your produce until {optimal_month} when prices are expected to reach "
                f"₹{expected_price} per quintal, if storage facilities are available."
            )
        
        # Supply-demand based recommendation
        if results["supply_demand_analysis"]["market_outlook"] == "bullish":
            recommendations.append(
                "Regional supply indicators suggest potential shortages which may drive prices higher in the "
                "coming weeks. Consider a staged selling approach to benefit from potential price increases."
            )
        elif results["supply_demand_analysis"]["market_outlook"] == "bearish":
            recommendations.append(
                "Regional supply indicators suggest possible oversupply which may put downward pressure on prices. "
                "If you need to sell, consider doing so sooner rather than later."
            )
        
        # Satellite-based recommendation
        if satellite_data and "satellite_yield_assessment" in results:
            yield_assessment = results["satellite_yield_assessment"]
            if yield_assessment["market_impact"] in ["bullish", "strongly_bullish"]:
                recommendations.append(
                    "Satellite imagery indicates below-average crop yields in your region, which may create "
                    "upward pressure on local prices. Consider a patient selling approach."
                )
            elif yield_assessment["market_impact"] in ["bearish", "strongly_bearish"]:
                recommendations.append(
                    "Satellite imagery indicates above-average crop yields in your region, which may create "
                    "downward pressure on local prices. Consider selling earlier if storage costs are significant."
                )
        
        # Add volatility warning if applicable
        crop_type_lower = crop_type.lower()
        if crop_type_lower in PRICE_VOLATILITY and PRICE_VOLATILITY[crop_type_lower] > 0.2:
            recommendations.append(
                f"Warning: {crop_type} prices have historically shown high volatility. Consider hedging strategies "
                "or a staged selling approach to mitigate price risk."
            )
        
        results["recommendations"] = recommendations
        results["data_sources"] = {
            "market_data": "historical_trends",
            "satellite_data": "integrated" if satellite_data else "none"
        }
        
        return results

# Create a singleton instance
market_timing_model = MarketTimingModel()

def get_market_timing_model() -> MarketTimingModel:
    """Get the market timing model instance"""
    return market_timing_model
