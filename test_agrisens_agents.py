#!/usr/bin/env python
"""
AgriMitr Agent Testing Script
This script tests the functionality of the main AgriMitr agents:
- Disease Prediction Agent
- Crop Recommendation Agent  
- Weather Forecast Agent

The script will attempt to run sample queries for each agent and display the results.
"""

import sys
import os
import logging
from pathlib import Path
import json

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Import required modules
try:
    from src.agents.disease_identification_agent import DiseaseIdentificationAgent
    from src.agents.crop_selection_agent import CropSelectionAgent
    from src.agents.weather_forecast_agent import WeatherForecastAgent
    from src.agents.agriculture_router import AgricultureRouter
    logger.info("Successfully imported agent modules")
except ImportError as e:
    logger.error(f"Failed to import agent modules: {e}")
    sys.exit(1)

def test_disease_identification_agent():
    """Test the disease identification agent with text-based queries"""
    print("\n===== TESTING DISEASE IDENTIFICATION AGENT =====")
    
    try:
        agent = DiseaseIdentificationAgent()
        
        # Test queries
        test_queries = [
            "What disease is causing these yellow spots on my tomato leaves?",
            "My apple tree leaves have black spots, what disease could it be?",
            "How do I identify powdery mildew on my crops?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = agent.process_request({"message": query, "type": "text"})
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")
                
        print("\nNote: Full functionality requires image input which isn't supported in this test script")
    except Exception as e:
        print(f"Failed to initialize Disease Identification Agent: {e}")

def test_crop_selection_agent():
    """Test the crop selection agent"""
    print("\n===== TESTING CROP SELECTION AGENT =====")
    
    try:
        agent = CropSelectionAgent()
        
        # Test queries
        test_queries = [
            "What crops should I plant in sandy soil with nitrogen 40, phosphorus 45, potassium 50, temperature 25C, humidity 60%, pH 6.5, and rainfall 200mm?",
            "Which crops are suitable for clay soil in a humid climate?",
            "Recommend crops for my farm with soil pH 7.2, moderate rainfall, and warm temperatures"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = agent.process_request({"message": query})
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")
    except Exception as e:
        print(f"Failed to initialize Crop Selection Agent: {e}")

def test_weather_forecast_agent():
    """Test the weather forecast agent"""
    print("\n===== TESTING WEATHER FORECAST AGENT =====")
    
    try:
        agent = WeatherForecastAgent()
        
        # Test queries
        test_queries = [
            "What's the weather forecast for Delhi for the next 5 days?",
            "Will it rain tomorrow in Mumbai?",
            "What will be the temperature next week in Bangalore?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = agent.process_request({"message": query})
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")
    except Exception as e:
        print(f"Failed to initialize Weather Forecast Agent: {e}")

def test_router():
    """Test the agriculture router to ensure queries are routed to the correct agent"""
    print("\n===== TESTING AGRICULTURE ROUTER =====")
    
    try:
        router = AgricultureRouter()
        
        # Test queries for different agents
        test_queries = [
            "What crops should I plant in soil with pH 6.5?",  # Crop selection
            "My tomato leaves have yellow spots, what disease is it?",  # Disease identification
            "What's the weather forecast for Delhi next week?",  # Weather forecast
            "How much fertilizer should I apply to my rice crop?",  # Fertilizer recommendation
            "When should I irrigate my wheat field?",  # Irrigation
            "What are best practices for sustainable farming?"  # Smart farming guidance
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = router.route_request({"message": query})
                print(f"Routed to: {response.get('agent_type', 'Unknown')}")
                print(f"Response: {response.get('response', 'No response')}")
            except Exception as e:
                print(f"Error routing query: {e}")
    except Exception as e:
        print(f"Failed to initialize Agriculture Router: {e}")

def check_dependencies():
    """Check if required dependencies and files are present"""
    print("\n===== CHECKING DEPENDENCIES =====")
    
    required_files = [
        "src/agents/disease_identification_agent.py",
        "src/agents/crop_selection_agent.py",
        "src/agents/weather_forecast_agent.py",
        "src/agents/agriculture_router.py",
        "src/models/AgriMitr_disease_identification.py",
        "src/models/AgriMitr_crop_recommendation.py"
    ]
    
    all_present = True
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_present = False
    
    return all_present

if __name__ == "__main__":
    print("🌱 AgriMitr Agent Functionality Test 🌱")
    print("=======================================")
    
    if not check_dependencies():
        print("\n⚠️ Some required files are missing. Tests may fail.")
    
    try:
        test_disease_identification_agent()
        test_crop_selection_agent()
        test_weather_forecast_agent()
        test_router()
        
        print("\n✅ All tests completed. Check the output above for any errors.")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
