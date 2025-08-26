#!/usr/bin/env python3
"""
AgriSens Agent Testing Script
Tests specific agents with sample queries to verify functionality
"""

import os
import sys
import asyncio
import base64
import json
from datetime import datetime
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agents
from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.disease_identification_agent import DiseaseIdentificationAgent
from src.agents.weather_forecast_agent import WeatherForecastAgent
from src.agents.fertilizer_recommendation_agent import FertilizerRecommendationAgent

# Import models
from src.core.agriculture_models import (
    AgricultureQuery, Location, SoilType, CropType
)

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def print_result(title, data):
    """Print formatted result data"""
    print(f"\n--- {title} ---")
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            elif isinstance(value, list):
                print(f"{key}:")
                for i, item in enumerate(value[:3], 1):
                    print(f"  {i}. {item}")
                if len(value) > 3:
                    print(f"  ... and {len(value) - 3} more")
            else:
                print(f"{key}: {value}")
    else:
        print(data)

async def test_crop_recommendation_agent():
    """Test the crop recommendation agent with sample queries"""
    print_header("Testing Crop Recommendation Agent")
    
    # Initialize agent
    agent = CropSelectionAgent("crop-test-agent", "Crop Recommendation Test Agent")
    agent.initialize()
    
    # Sample query locations
    test_queries = [
        {
            "location": "Punjab, India",
            "soil_type": SoilType.LOAM,
            "query_text": "What crops should I grow in Punjab?"
        },
        {
            "location": "Karnataka, India", 
            "soil_type": SoilType.RED_SOIL,
            "query_text": "Suggest suitable crops for Karnataka region"
        }
    ]
    
    for query_data in test_queries:
        print(f"\n\nTesting query: '{query_data['query_text']}'")
        
        # Create query object
        query = AgricultureQuery(
            query_text=query_data["query_text"],
            soil_type=query_data["soil_type"],
            location=Location(
                state=query_data["location"].split(",")[0],
                district="Unknown"
            )
        )
        
        # Process query
        response = await agent.process_query(query)
        
        # Print results
        if response.success:
            print_result("AgriSens model confidence", f"{response.data.get('agrisens_confidence', 'N/A')}%")
            
            if 'recommendations' in response.data:
                recommendations = response.data['recommendations']
                print_result("Top crop recommendations", recommendations[:3] if isinstance(recommendations, list) else recommendations)
            
            if 'npk_analysis' in response.data:
                print_result("NPK Analysis", response.data['npk_analysis'])
            
            if 'satellite_data' in response.data:
                print_result("Satellite Data", response.data['satellite_data'])
        else:
            print(f"❌ Error: {response.message}")

async def test_disease_identification_agent():
    """Test the disease identification agent with sample queries"""
    print_header("Testing Disease Identification Agent")
    
    # Initialize agent
    agent = DiseaseIdentificationAgent()
    agent.initialize()
    
    # Sample image paths for testing
    sample_images = [
        "AgriSens/PLANT-DISEASE-IDENTIFICATION/sample_images/apple_scab.jpg",
        "AgriSens/PLANT-DISEASE-IDENTIFICATION/sample_images/tomato_late_blight.jpg"
    ]
    
    # Test image-based identification
    for image_path in sample_images:
        if not os.path.exists(image_path):
            print(f"⚠️ Sample image not found: {image_path}")
            continue
        
        print(f"\n\nTesting image-based identification: {os.path.basename(image_path)}")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create query
        query = AgricultureQuery(
            query_text="What disease is affecting my plant?",
            image_data=image_data
        )
        
        # Process query
        response = await agent.process_query(query)
        
        # Print results
        if response.success:
            print_result("Detected Disease", response.data.get('disease', 'Unknown'))
            print_result("Confidence", f"{response.data.get('confidence', 0):.1f}%")
            print_result("Severity", response.data.get('severity', 'Unknown'))
            
            if 'recommendations' in response.data:
                print_result("Treatment Recommendations", response.data['recommendations'])
        else:
            print(f"❌ Error: {response.message}")
    
    # Test text-based symptom analysis
    symptom_queries = [
        "My tomato plants have dark brown spots with white fungus underneath the leaves",
        "My rice plants have yellow and brown spots, and the leaves are curling"
    ]
    
    for symptom_text in symptom_queries:
        print(f"\n\nTesting text-based symptom analysis: '{symptom_text}'")
        
        # Create query
        query = AgricultureQuery(
            query_text=symptom_text
        )
        
        # Process query
        response = await agent.process_query(query)
        
        # Print results
        if response.success:
            print_result("Identified Disease", response.data.get('disease', 'Unknown'))
            print_result("Confidence", f"{response.data.get('confidence', 0):.1f}%")
            
            if 'recommendations' in response.data:
                print_result("Treatment Recommendations", response.data['recommendations'])
        else:
            print(f"❌ Error: {response.message}")

async def test_weather_forecast_agent():
    """Test the weather forecast agent with sample queries"""
    print_header("Testing Weather Forecast Agent")
    
    # Initialize agent
    agent = WeatherForecastAgent("weather-test-agent", "Weather Forecast Test Agent")
    agent.initialize()
    
    # Sample queries
    test_queries = [
        {
            "location": "Punjab, India",
            "query_text": "What is the weather forecast for Punjab next week?"
        },
        {
            "location": "Maharashtra, India",
            "query_text": "Will it rain in Maharashtra in the next 3 days?"
        }
    ]
    
    for query_data in test_queries:
        print(f"\n\nTesting query: '{query_data['query_text']}'")
        
        # Create query object
        query = AgricultureQuery(
            query_text=query_data["query_text"],
            location=Location(
                state=query_data["location"].split(",")[0],
                district="Unknown",
                latitude=30.0, # Placeholder values
                longitude=75.0  # Should be replaced with actual coordinates
            )
        )
        
        # Process query
        response = await agent.process_query(query)
        
        # Print results
        if response.success:
            print_result("Weather Forecast", response.data)
            
            if 'forecast' in response.data:
                print_result("Forecast Details", response.data['forecast'])
            
            if 'agricultural_impact' in response.data:
                print_result("Agricultural Impact", response.data['agricultural_impact'])
        else:
            print(f"❌ Error: {response.message}")

async def test_fertilizer_recommendation_agent():
    """Test the fertilizer recommendation agent with sample queries"""
    print_header("Testing Fertilizer Recommendation Agent")
    
    # Initialize agent
    agent = FertilizerRecommendationAgent("fertilizer-test-agent", "Fertilizer Recommendation Test Agent")
    agent.initialize()
    
    # Sample queries with NPK values
    test_queries = [
        {
            "location": "Punjab, India",
            "crop_type": "wheat",
            "nitrogen": 80,
            "phosphorus": 45,
            "potassium": 60,
            "ph": 7.2,
            "query_text": "Recommend fertilizer for my wheat crop in Punjab"
        },
        {
            "location": "Karnataka, India",
            "crop_type": "rice",
            "nitrogen": 40,
            "phosphorus": 30,
            "potassium": 35,
            "ph": 6.5,
            "query_text": "What fertilizer should I use for my rice with N=40, P=30, K=35?"
        }
    ]
    
    for query_data in test_queries:
        print(f"\n\nTesting query: '{query_data['query_text']}'")
        
        # Create query object
        query = AgricultureQuery(
            query_text=query_data["query_text"],
            crop_type=query_data["crop_type"],
            location=Location(
                state=query_data["location"].split(",")[0],
                district="Unknown"
            ),
            soil_data={
                "nitrogen": query_data["nitrogen"],
                "phosphorus": query_data["phosphorus"],
                "potassium": query_data["potassium"],
                "ph": query_data["ph"]
            }
        )
        
        # Process query
        response = await agent.process_query(query)
        
        # Print results
        if response.success:
            if 'recommendation' in response.data:
                rec = response.data['recommendation']
                print_result("Recommended Fertilizer", rec.get('fertilizer_name', 'Unknown'))
                print_result("NPK Ratio", rec.get('npk_ratio', 'Unknown'))
                print_result("Application Rate", f"{rec.get('application_rate', 0)} kg/hectare")
                print_result("Application Method", rec.get('application_method', 'Unknown'))
                
                if 'environmental_impact' in rec:
                    print_result("Environmental Impact", rec['environmental_impact'])
                
                if 'alternatives' in rec:
                    print_result("Alternative Options", rec['alternatives'])
            else:
                print_result("Response Data", response.data)
        else:
            print(f"❌ Error: {response.message}")

async def run_all_tests():
    """Run all agent tests"""
    try:
        await test_crop_recommendation_agent()
        await test_disease_identification_agent()
        await test_weather_forecast_agent()
        await test_fertilizer_recommendation_agent()
        print("\n\n✅ All tests completed!")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Starting AgriSens Agent Testing")
    print("This script will test if the AgriSens model agents are working as expected")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test AgriSens agents')
    parser.add_argument('--agent', type=str, choices=['crop', 'disease', 'weather', 'fertilizer', 'all'],
                        default='all', help='Specify which agent to test')
    args = parser.parse_args()
    
    # Run tests based on arguments
    if args.agent == 'crop':
        asyncio.run(test_crop_recommendation_agent())
    elif args.agent == 'disease':
        asyncio.run(test_disease_identification_agent())
    elif args.agent == 'weather':
        asyncio.run(test_weather_forecast_agent())
    elif args.agent == 'fertilizer':
        asyncio.run(test_fertilizer_recommendation_agent())
    else:
        asyncio.run(run_all_tests())
