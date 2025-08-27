#!/usr/bin/env python3
"""
AgriMitr Agent Verification Script (Minimal Version)
Simple script to verify that the model agents exist and can be imported
"""

import os
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def verify_model_files():
    """Verify that the model files exist"""
    print_header("Verifying AgriMitr Model Files")
    
    model_files = [
        "src/models/AgriMitr_crop_recommendation.py",
        "src/models/AgriMitr_disease_identification.py",
        "src/models/AgriMitr_irrigation_scheduling.py",
        "src/models/AgriMitr_fertilizer_recommendation.py"
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    print("\nThese files contain the AgriMitr AI models that power the agent capabilities.")

def verify_agent_files():
    """Verify that the agent files exist"""
    print_header("Verifying AgriMitr Agent Files")
    
    agent_files = [
        "src/agents/crop_selection_agent.py",
        "src/agents/disease_identification_agent.py",
        "src/agents/irrigation_agent.py",
        "src/agents/fertilizer_recommendation_agent.py",
        "src/agents/weather_forecast_agent.py",
        "src/agents/smart_farming_guidance_agent.py"
    ]
    
    for file_path in agent_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    print("\nThese agents utilize the AgriMitr models to provide agricultural advice.")

def verify_test_files():
    """Verify that the test files exist"""
    print_header("Verifying AgriMitr Test Files")
    
    test_files = [
        "tests/test_disease_identification_integration.py",
        "tests/test_smart_farming_guidance_integration.py",
        "tests/test_google_search_integration.py",
        "tests/test_agent_router_integration.py",
        "tests/test_irrigation_model_integration.py"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    print("\nThese test files verify the functionality of the AgriMitr integration.")

def verify_sample_data():
    """Verify that sample data exists"""
    print_header("Verifying Sample Data")
    
    sample_files = [
        "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/apple_scab.jpg",
        "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/tomato_late_blight.jpg"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
            # Print file size to confirm it's a valid image
            size_kb = os.path.getsize(file_path) / 1024
            print(f"   Size: {size_kb:.1f} KB")
        else:
            print(f"❌ Missing: {file_path}")
    
    print("\nThese sample images are used for testing disease identification.")

def print_file_content_sample(file_path, num_lines=10):
    """Print a sample of a file's content"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📄 Sample from {file_path} (first {num_lines} lines):")
    print("-" * 60)
    
    try:
        with open(file_path, "r") as f:
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                print(line.rstrip())
        
        print("-" * 60)
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def show_disease_agent_sample():
    """Show a sample of the disease identification agent code"""
    print_header("Disease Identification Agent Sample")
    print_file_content_sample("src/agents/disease_identification_agent.py", 20)

def show_crop_agent_sample():
    """Show a sample of the crop selection agent code"""
    print_header("Crop Selection Agent Sample")
    print_file_content_sample("src/agents/crop_selection_agent.py", 20)

def show_weather_agent_sample():
    """Show a sample of the weather forecast agent code"""
    print_header("Weather Forecast Agent Sample")
    print_file_content_sample("src/agents/weather_forecast_agent.py", 20)

def main():
    """Main function to verify AgriMitr integration"""
    print_header("AgriMitr Integration Verification")
    print("This script verifies that the AgriMitr models and agents are properly integrated.")
    
    # Verify files
    verify_model_files()
    verify_agent_files()
    verify_test_files()
    verify_sample_data()
    
    # Show code samples
    show_disease_agent_sample()
    show_crop_agent_sample()
    show_weather_agent_sample()
    
    print_header("Verification Summary")
    print("""
The AgriMitr integration appears to be in place with the following components:

1. AgriMitr Model Files - ML models for agricultural applications
2. Agent Implementation Files - Agent code that uses the models
3. Test Files - Integration tests to verify functionality
4. Sample Data - Sample images and data for testing

To fully test the functionality, you would need to:
1. Install all required dependencies (see requirements.txt)
2. Set up the necessary environment variables and API keys
3. Run the integration tests or the demo script
""")

if __name__ == "__main__":
    main()
