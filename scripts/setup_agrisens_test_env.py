#!/usr/bin/env python
"""
Environment Setup for AgriSens Integration Tests
This script sets up the required Python environment for running AgriSens integration tests.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root
project_root = Path(__file__).parent.absolute()

def check_dependencies():
    """Check if required Python packages are installed"""
    print("Checking required Python packages...")
    
    # Core dependencies that are most likely to cause issues
    core_dependencies = [
        "langgraph",
        "langchain",
        "langchain-core",
        "langchain-community",
        "redis",
        "fastapi",
        "numpy",
        "pandas",
        "scikit-learn",
        "tensorflow"
    ]
    
    missing_packages = []
    
    for package in core_dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing Python packages"""
    if not packages:
        print("No packages to install.")
        return True
    
    print(f"\nInstalling {len(packages)} missing packages...")
    
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def create_simple_test_data():
    """Create simple test data for the models if it doesn't exist"""
    data_dir = project_root / "data" / "agrisens"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple crop recommendation test dataset
    crop_data_file = data_dir / "crop_recommendation_test.csv"
    if not crop_data_file.exists():
        print("\nCreating simple crop recommendation test data...")
        with open(crop_data_file, 'w') as f:
            f.write("N,P,K,temperature,humidity,ph,rainfall,label\n")
            f.write("90,42,43,20.87,82.00,6.50,202.93,rice\n")
            f.write("85,58,41,21.77,80.32,7.04,226.65,rice\n")
            f.write("60,55,44,23.00,82.33,7.84,263.96,maize\n")
            f.write("74,35,40,26.49,82.41,6.98,242.86,cotton\n")
            f.write("78,42,42,26.42,80.55,6.79,263.17,cotton\n")
        print(f"✅ Created test file: {crop_data_file}")
    
    # Create a simple irrigation data test file
    irrigation_data_file = data_dir / "irrigation_data_test.csv"
    if not irrigation_data_file.exists():
        print("Creating simple irrigation test data...")
        with open(irrigation_data_file, 'w') as f:
            f.write("crop,soil_type,growth_stage,temperature,humidity,rainfall,soil_moisture,water_requirement\n")
            f.write("wheat,loam,vegetative,28,65,5,30,8\n")
            f.write("wheat,loam,flowering,30,60,0,25,12\n")
            f.write("rice,clay,vegetative,32,80,10,40,15\n")
            f.write("cotton,sandy,flowering,35,55,0,20,18\n")
        print(f"✅ Created test file: {irrigation_data_file}")
    
    # Create a simple market prices test file
    market_data_file = data_dir / "market_prices_test.csv"
    if not market_data_file.exists():
        print("Creating simple market data test file...")
        with open(market_data_file, 'w') as f:
            f.write("date,crop,price,volume,location\n")
            f.write("2025-08-01,wheat,2200,1500,Delhi\n")
            f.write("2025-08-02,wheat,2180,1600,Delhi\n")
            f.write("2025-08-03,wheat,2220,1400,Delhi\n")
            f.write("2025-08-04,wheat,2250,1300,Delhi\n")
            f.write("2025-08-01,rice,3500,2000,Delhi\n")
            f.write("2025-08-02,rice,3520,1900,Delhi\n")
            f.write("2025-08-03,rice,3480,2100,Delhi\n")
            f.write("2025-08-04,rice,3500,2000,Delhi\n")
        print(f"✅ Created test file: {market_data_file}")
    
    return True

def create_stub_models():
    """Create stub model files for testing if they don't exist"""
    model_dir = project_root / "models" / "stubs"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a stub crop model
    stub_crop_model = model_dir / "stub_crop_model.py"
    if not stub_crop_model.exists():
        print("\nCreating stub crop model...")
        with open(stub_crop_model, 'w') as f:
            f.write('''"""
Stub Crop Recommendation Model for Testing
"""

class StubCropRecommendationModel:
    """A stub model that returns predefined recommendations"""
    
    def __init__(self):
        self.recommendations = {
            "sandy": ["groundnut", "cotton", "potato"],
            "loamy": ["wheat", "rice", "maize"],
            "clay": ["rice", "sugarcane", "cotton"],
            "default": ["wheat", "rice", "pulses"]
        }
    
    def predict(self, soil_type=None, nitrogen=None, phosphorus=None, 
                potassium=None, temperature=None, humidity=None, 
                ph=None, rainfall=None, **kwargs):
        """Return a stubbed prediction based on soil type"""
        if soil_type and soil_type.lower() in self.recommendations:
            return self.recommendations[soil_type.lower()]
        return self.recommendations["default"]

def get_model():
    """Return the stub model instance"""
    return StubCropRecommendationModel()
''')
        print(f"✅ Created stub model: {stub_crop_model}")
    
    # Create a stub irrigation model
    stub_irrigation_model = model_dir / "stub_irrigation_model.py"
    if not stub_irrigation_model.exists():
        print("Creating stub irrigation model...")
        with open(stub_irrigation_model, 'w') as f:
            f.write('''"""
Stub Irrigation Scheduling Model for Testing
"""

class StubIrrigationModel:
    """A stub model that returns predefined irrigation schedules"""
    
    def __init__(self):
        self.irrigation_plans = {
            "wheat": {
                "days": [3, 7, 10, 14],
                "amounts": [8, 10, 8, 10],
                "method": "sprinkler"
            },
            "rice": {
                "days": [2, 5, 8, 11, 14],
                "amounts": [15, 15, 12, 15, 15],
                "method": "flood"
            },
            "cotton": {
                "days": [4, 9, 14],
                "amounts": [12, 15, 12],
                "method": "drip"
            },
            "default": {
                "days": [5, 10, 15],
                "amounts": [10, 10, 10],
                "method": "sprinkler"
            }
        }
    
    def generate_irrigation_plan(self, crop_type=None, soil_type=None, field_size=None, **kwargs):
        """Return a stubbed irrigation plan based on crop type"""
        crop = crop_type.lower() if crop_type else "default"
        if crop not in self.irrigation_plans:
            crop = "default"
            
        plan = self.irrigation_plans[crop].copy()
        plan["crop"] = crop
        plan["soil_type"] = soil_type or "loam"
        plan["field_size"] = field_size or 1.0
        plan["total_water"] = sum(plan["amounts"])
        
        return plan
    
    def generate_satellite_enhanced_irrigation_plan(self, *args, **kwargs):
        """Same as generate_irrigation_plan but with added satellite context"""
        plan = self.generate_irrigation_plan(*args, **kwargs)
        plan["satellite_enhanced"] = True
        plan["confidence"] = 0.85
        return plan

def get_model():
    """Return the stub model instance"""
    return StubIrrigationModel()
''')
        print(f"✅ Created stub model: {stub_irrigation_model}")
    
    return True

def check_directories():
    """Check that all required directories exist"""
    required_dirs = [
        "data",
        "data/agrisens",
        "models",
        "models/stubs",
        "src/models",
        "src/agents",
        "src/services",
        "tests"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return True

def setup_environment():
    """Set up the testing environment"""
    print("Setting up AgriSens testing environment...")
    
    # Check directories
    check_directories()
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    # Ask to install missing packages
    if missing_packages:
        print("\nThe following packages are required but not installed:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        
        choice = input("\nWould you like to install these packages now? (y/n): ").strip().lower()
        if choice == 'y':
            install_missing_packages(missing_packages)
        else:
            print("Skipping package installation. Tests may fail.")
    
    # Create test data
    create_simple_test_data()
    
    # Create stub models
    create_stub_models()
    
    print("\n✅ Environment setup complete! You can now run the test scripts.")
    
if __name__ == "__main__":
    setup_environment()
