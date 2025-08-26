#!/usr/bin/env python
"""
AgriMitr Irrigation Model Integration Test
This script tests the irrigation model integration to verify proper functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def test_irrigation_model_manually():
    """Test the irrigation model functionality directly"""
    print("\n===== TESTING IRRIGATION MODEL DIRECTLY =====")
    
    try:
        # Import the model
        from src.models.AgriMitr_irrigation_scheduling import IrrigationSchedulingModel
        
        # Initialize the model
        irrigation_model = IrrigationSchedulingModel()
        
        # Test sample data
        test_data = {
            "crop_type": "wheat",
            "soil_type": "loam",
            "field_size_hectares": 5,
            "current_soil_moisture": 30,  # percentage
            "temperature": 28,  # Celsius
            "humidity": 65,  # percentage
            "precipitation_forecast": [0, 0, 5, 10, 0],  # mm for next 5 days
            "evapotranspiration": 4.5,  # mm/day
            "growth_stage": "vegetative"
        }
        
        # Generate irrigation recommendation
        recommendation = irrigation_model.generate_recommendation(test_data)
        
        print("\nTest Data:")
        for key, value in test_data.items():
            print(f"  {key}: {value}")
        
        print("\nIrrigation Recommendation:")
        if recommendation:
            for key, value in recommendation.items():
                print(f"  {key}: {value}")
        else:
            print("  No recommendation generated")
            
    except ImportError as e:
        print(f"Failed to import irrigation model: {e}")
    except Exception as e:
        print(f"Error testing irrigation model: {e}")

def test_irrigation_agent():
    """Test the irrigation agent functionality"""
    print("\n===== TESTING IRRIGATION AGENT =====")
    
    try:
        # Import the agent
        from src.agents.irrigation_agent import IrrigationAgent
        
        # Initialize the agent
        irrigation_agent = IrrigationAgent()
        
        # Test queries
        test_queries = [
            "When should I irrigate my wheat field given soil moisture is 30% and temperature is 28C?",
            "How much water should I apply to my tomato plants?",
            "Create an irrigation schedule for my 5-hectare corn field with loamy soil."
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = irrigation_agent.process_request({"message": query})
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")
                
    except ImportError as e:
        print(f"Failed to import irrigation agent: {e}")
    except Exception as e:
        print(f"Error testing irrigation agent: {e}")

if __name__ == "__main__":
    print("💧 AgriMitr Irrigation Model Integration Test 💧")
    print("===============================================")
    
    try:
        test_irrigation_model_manually()
        test_irrigation_agent()
        
        print("\n✅ All tests completed. Check the output above for any errors.")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
