#!/usr/bin/env python
"""
Market Timing Model Integration Test
This script tests the market timing model integration to verify proper functionality.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def test_market_timing_model():
    """Test the market timing model functionality directly"""
    print("\n===== TESTING MARKET TIMING MODEL =====")
    
    try:
        # Import the model
        from src.models.market_timing_model import MarketTimingModel
        
        # Initialize the model
        model = MarketTimingModel()
        
        # Test data - current date and crop
        current_date = datetime.now()
        crop_type = "wheat"
        
        # Generate pricing forecast
        print(f"\nGenerating price forecast for {crop_type}")
        forecast = model.predict_optimal_timing(
            crop_type=crop_type,
            harvest_date=(current_date - timedelta(days=5)).strftime("%Y-%m-%d"),  # 5 days ago
            current_date=current_date.strftime("%Y-%m-%d"),
            forecast_days=30
        )
        
        print("\nPrice Forecast:")
        if forecast:
            for key, value in forecast.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  No forecast generated")
        
        # Test optimal selling date calculation
        print("\nCalculating optimal selling date")
        optimal_date = model.calculate_optimal_selling_date(crop_type=crop_type)
        print(f"Optimal selling date for {crop_type}: {optimal_date}")
            
    except ImportError as e:
        print(f"Failed to import market timing model: {e}")
    except Exception as e:
        print(f"Error testing market timing model: {e}")

def test_market_timing_agent():
    """Test the market timing agent functionality"""
    print("\n===== TESTING MARKET TIMING AGENT =====")
    
    try:
        # Import the agent
        from src.agents.market_timing_agent import MarketTimingAgent
        
        # Initialize the agent
        agent = MarketTimingAgent()
        
        # Test queries
        test_queries = [
            "When should I sell my wheat crop for the best price?",
            "What will be the price of rice next month?",
            "Is it a good time to sell my tomatoes now or should I wait?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            try:
                response = agent.process_request({"message": query})
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error processing query: {e}")
                
    except ImportError as e:
        print(f"Failed to import market timing agent: {e}")
    except Exception as e:
        print(f"Error testing market timing agent: {e}")

def test_satellite_integration():
    """Test the satellite data integration with market timing"""
    print("\n===== TESTING MARKET TIMING SATELLITE INTEGRATION =====")
    
    try:
        # Import the satellite integration module
        from src.services.satellite_data_service import SatelliteDataService
        
        # Initialize the service
        satellite_service = SatelliteDataService()
        
        # Test data retrieval
        print("\nRetrieving satellite data for crop yield estimation")
        satellite_data = satellite_service.get_recent_data(
            region="Punjab",
            data_type="vegetation_index",
            days=30
        )
        
        print("\nSatellite Data Sample:")
        if satellite_data:
            if isinstance(satellite_data, list) and len(satellite_data) > 0:
                for i, data_point in enumerate(satellite_data[:3]):
                    print(f"  Data point {i+1}:")
                    for key, value in data_point.items():
                        print(f"    {key}: {value}")
                if len(satellite_data) > 3:
                    print(f"  ... {len(satellite_data) - 3} more data points")
            else:
                print(f"  {satellite_data}")
        else:
            print("  No satellite data retrieved")
        
        # Test integration with market timing
        print("\nIntegrating satellite data with market timing model")
        
        # Import the market timing model
        from src.models.market_timing_model import MarketTimingModel
        
        # Initialize the model
        model = MarketTimingModel()
        
        # Test satellite data integration
        crop_type = "wheat"
        region = "Punjab"
        
        # Check if the model has the method for satellite data integration
        if hasattr(model, 'integrate_satellite_data') and callable(getattr(model, 'integrate_satellite_data')):
            enhanced_forecast = model.integrate_satellite_data(crop_type=crop_type, region=region)
            print(f"\nEnhanced forecast with satellite data for {crop_type} in {region}:")
            if enhanced_forecast:
                for key, value in enhanced_forecast.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"    {sub_key}: {sub_value}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("  No enhanced forecast generated")
        else:
            print("  Model does not support satellite data integration")
            
    except ImportError as e:
        print(f"Failed to import satellite integration modules: {e}")
    except Exception as e:
        print(f"Error testing satellite integration: {e}")

if __name__ == "__main__":
    print("📊 Market Timing Model Integration Test 📊")
    print("=========================================")
    
    try:
        test_market_timing_model()
        test_market_timing_agent()
        test_satellite_integration()
        
        print("\n✅ All tests completed. Check the output above for any errors.")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
