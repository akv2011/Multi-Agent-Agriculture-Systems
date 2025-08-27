#!/usr/bin/env python3
"""
AgriMitr Query Examples
This script demonstrates example queries for each AgriMitr agent and how they would be processed.
"""

import os
import sys
import json
from typing import Dict, Any

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def print_query_example(agent_type, query_text, expected_output):
    """Print an example query and expected output"""
    print(f"\n🧠 Agent Type: {agent_type}")
    print(f"❓ Query: \"{query_text}\"")
    print("\n✅ Expected Response:")
    print(json.dumps(expected_output, indent=2))

def disease_identification_examples():
    """Examples for disease identification queries"""
    print_header("Disease Identification Examples")
    
    # Image-based example
    print_query_example(
        "Disease Identification Agent (Image-based)",
        "What disease is affecting my tomato plant? [with attached image]",
        {
            "disease": "Tomato Late Blight",
            "confidence": 95.8,
            "severity": "Moderate",
            "recommendations": [
                "Apply copper-based fungicide as soon as possible",
                "Remove and destroy infected plant parts",
                "Improve air circulation between plants",
                "Avoid overhead watering to keep foliage dry"
            ],
            "identification_method": "image_analysis"
        }
    )
    
    # Text-based example
    print_query_example(
        "Disease Identification Agent (Text-based)",
        "My rice plants have yellow leaves with brown spots and the leaf tips are drying",
        {
            "disease": "Rice Blast",
            "confidence": 82.5,
            "symptoms_detected": ["yellow leaves", "brown spots", "dry leaf tips"],
            "recommendations": [
                "Apply fungicide containing tricyclazole",
                "Maintain proper water management",
                "Use resistant rice varieties in next planting"
            ],
            "identification_method": "symptom_analysis"
        }
    )

def crop_recommendation_examples():
    """Examples for crop recommendation queries"""
    print_header("Crop Recommendation Examples")
    
    # Basic recommendation
    print_query_example(
        "Crop Selection Agent",
        "What crops should I plant in Punjab this season?",
        {
            "recommendations": [
                {
                    "crop_type": "Wheat",
                    "variety": "HD-3086",
                    "suitability_score": 0.95,
                    "expected_yield": "5200 kg/hectare",
                    "reason": "Optimal soil and climate conditions, aligned with seasonal patterns"
                },
                {
                    "crop_type": "Mustard",
                    "variety": "NRCHB-101",
                    "suitability_score": 0.87,
                    "expected_yield": "1800 kg/hectare",
                    "reason": "Good fit for current soil conditions and market demand"
                }
            ],
            "npk_analysis": {
                "nitrogen": "Medium (45 kg/hectare)",
                "phosphorus": "Adequate (32 kg/hectare)",
                "potassium": "High (72 kg/hectare)"
            },
            "AgriMitr_confidence": 99.55,
            "satellite_data": {
                "vegetation_index": "Healthy",
                "soil_moisture": "Adequate (35%)"
            }
        }
    )
    
    # Advanced recommendation with NPK data
    print_query_example(
        "Crop Selection Agent with NPK Data",
        "Suggest crops for soil with N=40, P=30, K=60 in Maharashtra",
        {
            "recommendations": [
                {
                    "crop_type": "Cotton",
                    "variety": "Bt Cotton MCH-6301",
                    "suitability_score": 0.93,
                    "expected_yield": "2800 kg/hectare",
                    "reason": "Ideal NPK ratio for cotton cultivation in this region"
                },
                {
                    "crop_type": "Soybean",
                    "variety": "JS-335",
                    "suitability_score": 0.88,
                    "expected_yield": "2200 kg/hectare",
                    "reason": "Well-suited to the soil composition and climate"
                }
            ],
            "npk_analysis": {
                "summary": "Balanced nitrogen and phosphorus with high potassium",
                "recommendation": "Consider adding nitrogen supplement for non-legume crops"
            },
            "AgriMitr_confidence": 99.55
        }
    )

def fertilizer_recommendation_examples():
    """Examples for fertilizer recommendation queries"""
    print_header("Fertilizer Recommendation Examples")
    
    print_query_example(
        "Fertilizer Recommendation Agent",
        "What fertilizer should I use for my wheat crop with soil test results N=80, P=45, K=60?",
        {
            "recommendation": {
                "fertilizer_name": "NPK 10-26-26",
                "npk_ratio": "10:26:26",
                "application_rate": 250,
                "application_method": "Band placement 5cm below and 5cm to the side of seed row",
                "application_timing": "Split application: 50% at sowing, 50% at tillering stage",
                "cost_estimate": 4500,
                "environmental_impact": "Moderate - consider incorporating organic amendments",
                "alternatives": [
                    "DAP with potash supplement",
                    "Organic compost with rock phosphate"
                ]
            },
            "soil_analysis": {
                "nitrogen": 80,
                "phosphorus": 45,
                "potassium": 60,
                "ph": 7.2
            }
        }
    )

def weather_forecast_examples():
    """Examples for weather forecast queries"""
    print_header("Weather Forecast Examples")
    
    print_query_example(
        "Weather Forecast Agent",
        "What will the weather be like next week in Punjab?",
        {
            "forecast": [
                {
                    "date": "2025-08-26",
                    "temperature_max": 32,
                    "temperature_min": 25,
                    "precipitation_mm": 0.5,
                    "conditions": "Mostly sunny",
                    "humidity": 65
                },
                {
                    "date": "2025-08-27",
                    "temperature_max": 33,
                    "temperature_min": 26,
                    "precipitation_mm": 12.5,
                    "conditions": "Scattered thunderstorms",
                    "humidity": 80
                }
            ],
            "agricultural_impact": {
                "summary": "Light to moderate rainfall expected mid-week; beneficial for standing crops",
                "recommendations": [
                    "Consider delaying irrigation scheduled for August 27-28",
                    "Monitor for fungal disease risk following rainfall",
                    "Good conditions for fertilizer application on August 26"
                ]
            },
            "satellite_enhanced": True
        }
    )

def smart_farming_examples():
    """Examples for smart farming guidance queries"""
    print_header("Smart Farming Guidance Examples")
    
    print_query_example(
        "Smart Farming Guidance Agent",
        "What are sustainable ways to control pests in cotton?",
        {
            "title": "Integrated Pest Management for Cotton",
            "guidance_type": "sustainable_pest_management",
            "recommendations": [
                "Implement trap crops like marigold or okra around cotton fields",
                "Release natural predators such as ladybugs for bollworm control",
                "Use neem-based organic pesticides for early pest management",
                "Practice regular scouting to detect pest populations early",
                "Use pheromone traps to monitor and disrupt pest mating cycles"
            ],
            "crop_specific": True,
            "location_specific": False,
            "satellite_data": {
                "pest_pressure_risk": "Moderate",
                "vegetation_health": "Good"
            }
        }
    )
    
    print_query_example(
        "Smart Farming Guidance Agent",
        "What crop rotation system should I use for rice fields in Tamil Nadu?",
        {
            "title": "Rice-based Crop Rotation Systems for Tamil Nadu",
            "guidance_type": "crop_rotation",
            "recommendations": [
                "Rice-Pulses-Rice: Plant rice in monsoon, followed by pulses in winter, then rice again",
                "Rice-Vegetables-Rice: Incorporate leafy greens or okra between rice seasons",
                "Rice-Green Manure-Rice: Use dhaincha or sesbania as green manure crop",
                "Rice-Wheat-Mung Bean: Three-crop rotation for soil fertility and income diversification"
            ],
            "benefits": [
                "Breaks pest and disease cycles",
                "Improves soil fertility through nitrogen fixation",
                "Reduces fertilizer requirements by 15-30%",
                "Diversifies income sources"
            ],
            "crop_specific": True,
            "location_specific": True
        }
    )

def router_examples():
    """Examples for intelligent query routing"""
    print_header("Intelligent Query Routing Examples")
    
    # Example 1: Disease identification query with image
    print_query_example(
        "Agriculture Router",
        "What disease is affecting my tomato plant? [with image]",
        {
            "routing_decision": {
                "detected_domains": ["disease_identification"],
                "detected_language": "english",
                "confidence": 0.95,
                "selected_agents": ["disease_specialist"],
                "execution_plan": "sequential"
            }
        }
    )
    
    # Example 2: Financial query with Google Search fallback
    print_query_example(
        "Agriculture Router with Google Search Fallback",
        "What is the current MSP for wheat in India?",
        {
            "routing_decision": {
                "detected_domains": ["finance_policy", "market_timing"],
                "detected_language": "english",
                "confidence": 0.87,
                "selected_agents": ["finance_policy_agent"],
                "execution_plan": "sequential"
            },
            "use_google_search_fallback": True
        }
    )
    
    # Example 3: Hindi language query
    print_query_example(
        "Agriculture Router with Multi-language Support",
        "मेरे धान के पौधों पर पीले धब्बे हैं, क्या बीमारी है?",
        {
            "routing_decision": {
                "detected_domains": ["disease_identification"],
                "detected_language": "hindi",
                "confidence": 0.91,
                "selected_agents": ["disease_specialist"],
                "execution_plan": "sequential"
            }
        }
    )

def main():
    """Main function to show examples for all agents"""
    print_header("AgriMitr Agent Query Examples")
    print("This script demonstrates example queries for each AgriMitr agent and how they would be processed.")
    
    disease_identification_examples()
    crop_recommendation_examples()
    fertilizer_recommendation_examples()
    weather_forecast_examples()
    smart_farming_examples()
    router_examples()
    
    print_header("AgriMitr Integration Summary")
    print("""
The AgriMitr integration provides comprehensive AI-powered agricultural advisory services
through specialized agents that can handle a wide range of queries related to:

1. Crop Selection (with 99.55% accuracy model)
2. Disease Identification (both image and text-based)
3. Fertilizer Recommendation (based on soil NPK analysis)
4. Weather Forecasting (with agricultural impact analysis)
5. Smart Farming Guidance (sustainable practices)

All queries are intelligently routed to the appropriate agents through the Agriculture Router,
with support for both Hindi and English languages, and Google Search fallback for financial
and general queries.
""")

if __name__ == "__main__":
    main()
