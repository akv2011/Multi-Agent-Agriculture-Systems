#!/usr/bin/env python3
"""
Check AgriMitr Model Availability

This script checks for the existence and structure of key AgriMitr model files 
without actually importing them to avoid TensorFlow initialization issues.
"""

import os
import sys
import json
from datetime import datetime

def print_section(title):
    """Print a section title with decoration"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_file_exists(file_path, component_name):
    """Check if a file exists and report the result"""
    if os.path.exists(file_path):
        print(f"✅ {component_name} file exists: {file_path}")
        return True
    else:
        print(f"❌ {component_name} file NOT FOUND: {file_path}")
        return False

def check_directory_exists(dir_path, component_name):
    """Check if a directory exists and report the result"""
    if os.path.isdir(dir_path):
        print(f"✅ {component_name} directory exists: {dir_path}")
        return True
    else:
        print(f"❌ {component_name} directory NOT FOUND: {dir_path}")
        return False

def check_disease_prediction_agent():
    """Check disease prediction agent file existence"""
    print_section("Disease Prediction Agent")
    
    # Check agent file
    agent_path = os.path.join("src", "agents", "disease_identification_agent.py")
    agent_exists = check_file_exists(agent_path, "Disease identification agent")
    
    # Check model file
    model_path = os.path.join("src", "models", "AgriMitr_disease_identification.py")
    model_exists = check_file_exists(model_path, "Disease identification model")
    
    # Check test file
    test_path = os.path.join("tests", "test_disease_identification_integration.py")
    test_exists = check_file_exists(test_path, "Disease identification test")
    
    # Check disease dataset directory
    dataset_path = os.path.join("AgriMitr", "PLANT-DISEASE-IDENTIFICATION")
    dataset_exists = check_directory_exists(dataset_path, "Disease identification dataset")
    
    # Check sample images
    sample_path = os.path.join(dataset_path, "sample_images")
    samples_exist = check_directory_exists(sample_path, "Sample disease images")
    
    result = {
        "agent_file": agent_exists,
        "model_file": model_exists,
        "test_file": test_exists,
        "dataset_directory": dataset_exists,
        "sample_images": samples_exist
    }
    
    return result

def check_crop_recommendation_agent():
    """Check crop recommendation agent file existence"""
    print_section("Crop Recommendation Agent")
    
    # Check agent file
    agent_path = os.path.join("src", "agents", "crop_selection_agent.py")
    agent_exists = check_file_exists(agent_path, "Crop selection agent")
    
    # Check model file
    model_path = os.path.join("src", "models", "AgriMitr_crop_recommendation.py")
    model_exists = check_file_exists(model_path, "Crop recommendation model")
    
    # Check integration test
    test_path = os.path.join("tests", "test_AgriMitr_integration.py")
    test_exists = check_file_exists(test_path, "AgriMitr integration test")
    
    # Check crop dataset directory
    dataset_path = os.path.join("AgriMitr", "CROP-RECOMMENDATION")
    dataset_exists = check_directory_exists(dataset_path, "Crop recommendation dataset")
    
    # Check test data file
    data_path = os.path.join("data", "AgriMitr", "crop_recommendation_test.csv")
    data_exists = check_file_exists(data_path, "Crop recommendation test data")
    
    result = {
        "agent_file": agent_exists,
        "model_file": model_exists,
        "test_file": test_exists,
        "dataset_directory": dataset_exists,
        "test_data": data_exists
    }
    
    return result

def check_weather_forecast_agent():
    """Check weather forecast agent file existence"""
    print_section("Weather Forecast Agent")
    
    # Check agent file
    agent_path = os.path.join("src", "agents", "weather_forecast_agent.py")
    agent_exists = check_file_exists(agent_path, "Weather forecast agent")
    
    # Check test file (might be part of router integration)
    test_path = os.path.join("tests", "test_agent_router_integration.py")
    test_exists = check_file_exists(test_path, "Agent router integration test")
    
    # Check weather data
    weather_path = os.path.join("data", "AgriMitr", "weather_data_test.csv")
    weather_exists = check_file_exists(weather_path, "Weather test data")
    
    result = {
        "agent_file": agent_exists,
        "test_file": test_exists,
        "weather_data": weather_exists
    }
    
    return result

def check_irrigation_model():
    """Check irrigation model file existence"""
    print_section("Irrigation Model")
    
    # Check agent file
    agent_path = os.path.join("src", "agents", "irrigation_agent.py")
    agent_exists = check_file_exists(agent_path, "Irrigation agent")
    
    # Check model file
    model_path = os.path.join("src", "models", "AgriMitr_irrigation_scheduling.py")
    model_exists = check_file_exists(model_path, "Irrigation model")
    
    # Check test file
    test_path = os.path.join("tests", "test_irrigation_model_integration.py")
    test_exists = check_file_exists(test_path, "Irrigation model integration test")
    
    # Check irrigation data file
    data_path = os.path.join("data", "AgriMitr", "irrigation_data_test.csv")
    data_exists = check_file_exists(data_path, "Irrigation test data")
    
    result = {
        "agent_file": agent_exists,
        "model_file": model_exists,
        "test_file": test_exists,
        "test_data": data_exists
    }
    
    return result

def check_market_timing_model():
    """Check market timing model file existence"""
    print_section("Market Timing Model")
    
    # Check agent file
    agent_path = os.path.join("src", "agents", "market_timing_agent.py")
    agent_exists = check_file_exists(agent_path, "Market timing agent")
    
    # Check model file
    model_path = os.path.join("src", "models", "AgriMitr_market_timing.py")
    model_exists = check_file_exists(model_path, "Market timing model")
    
    # Check test file
    test_path = os.path.join("tests", "test_market_timing_model_integration.py")
    test_exists = check_file_exists(test_path, "Market timing integration test")
    
    # Check market data file
    data_path = os.path.join("data", "AgriMitr", "market_prices_test.csv")
    data_exists = check_file_exists(data_path, "Market prices test data")
    
    result = {
        "agent_file": agent_exists,
        "model_file": model_exists,
        "test_file": test_exists,
        "test_data": data_exists
    }
    
    return result

def generate_report(results):
    """Generate a summary report of all checks"""
    print_section("SUMMARY REPORT")
    
    components = [
        "Disease Prediction Agent",
        "Crop Recommendation Agent",
        "Weather Forecast Agent",
        "Irrigation Model",
        "Market Timing Model"
    ]
    
    all_files_exist = True
    
    for i, component in enumerate(components):
        component_results = results[i]
        files_exist = all(component_results.values())
        all_files_exist = all_files_exist and files_exist
        
        if files_exist:
            print(f"✅ {component}: All required files exist")
        else:
            print(f"❌ {component}: Missing some files")
            missing_files = [k for k, v in component_results.items() if not v]
            print(f"   Missing: {', '.join(missing_files)}")
    
    print("\nOVERALL STATUS:")
    if all_files_exist:
        print("✅ SUCCESS: All AgriMitr model and agent files are in place")
    else:
        print("❌ WARNING: Some AgriMitr model or agent files are missing")
    
    # Generate a complete report file
    report_path = "AgriMitr_status_report.json"
    report_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "components": {
            "disease_prediction": results[0],
            "crop_recommendation": results[1],
            "weather_forecast": results[2],
            "irrigation_model": results[3],
            "market_timing_model": results[4]
        },
        "all_files_exist": all_files_exist
    }
    
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")

def main():
    """Run all checks and generate report"""
    print("Checking AgriMitr model and agent files...")
    
    results = [
        check_disease_prediction_agent(),
        check_crop_recommendation_agent(),
        check_weather_forecast_agent(),
        check_irrigation_model(),
        check_market_timing_model()
    ]
    
    generate_report(results)
    
    return 0 if all(all(component.values()) for component in results) else 1

if __name__ == "__main__":
    sys.exit(main())
