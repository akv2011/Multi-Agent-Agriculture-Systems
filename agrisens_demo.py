#!/usr/bin/env python3
"""
AgriMitr Integration Demo
Demonstrates the AgriMitr models integrated with the Multi-Agent Agriculture Systems
"""

import sys
import os
import json
import base64
from datetime import datetime
import asyncio
from typing import Dict, Any, List
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agent classes
from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.irrigation_agent import IrrigationAgent
from src.agents.disease_identification_agent import DiseaseIdentificationAgent

# Import models
from src.core.agriculture_models import (
    AgricultureQuery, Location, SoilType, CropType, SeasonType
)

print("🌾🔍 AgriMitr AI Models Integration Demo")
print("=" * 60)
print("Demonstrating the integration of advanced AgriMitr AI models")
print("with the Multi-Agent Agriculture Systems")

# Initialize agents
crop_agent = CropSelectionAgent("crop-agent-1", "AgriMitr Crop Selection")
irrigation_agent = IrrigationAgent("irrigation-agent-1", "AgriMitr Irrigation Scheduling")
disease_agent = DiseaseIdentificationAgent("disease-agent-1", "AgriMitr Disease Identification")

# Initialize agents
print("\n🚀 Initializing AgriMitr-powered agents...")
crop_agent.initialize()
irrigation_agent.initialize()
disease_agent.initialize()
print("✅ All agents initialized successfully")


async def demo_crop_recommendation():
    """Demonstrate crop recommendation with AgriMitr ML model"""
    print("\n\n🌱 DEMO 1: AgriMitr Crop Recommendation (99.55% accuracy)")
    print("-" * 60)
    
    locations = [
        {
            "name": "Punjab, India",
            "lat": 30.9010,
            "lng": 75.8573,
            "soil": SoilType.CLAY_LOAM.value,
            "description": "Northern Indian agricultural heartland"
        },
        {
            "name": "Maharashtra, India",
            "lat": 19.7515,
            "lng": 75.7139,
            "soil": SoilType.BLACK_SOIL.value,
            "description": "Western Indian cotton belt"
        }
    ]
    
    for location_data in locations:
        print(f"\n📍 Location: {location_data['name']} ({location_data['description']})")
        
        query = AgricultureQuery(
            query_id=f"crop-query-{location_data['name'].split(',')[0].lower()}",
            query_text=f"What crops should I plant in {location_data['name']}?",
            query_domain="crop_selection",
            location=Location(
                latitude=location_data['lat'],
                longitude=location_data['lng'],
                address=location_data['name'],
                region=location_data['name'].split(',')[0]
            ),
            soil_type=location_data['soil'],
            timestamp=datetime.now(),
            farm_size_acres=5.0
        )
        
        print("   🔍 Analyzing soil, climate, and satellite data...")
        response = await crop_agent.process_query(query)
        
        print(f"   ✅ AgriMitr ML model confidence: {response.data.get('AgriMitr_confidence', 'N/A')}%")
        print(f"   🧪 NPK Analysis: {response.data.get('npk_analysis', {}).get('summary', 'N/A')}")
        
        if 'recommendations' in response.data and response.data['recommendations']:
            print("\n   📊 Top crop recommendations:")
            for i, rec in enumerate(response.data['recommendations'][:3], 1):
                print(f"   {i}. {rec.get('crop_type', 'Unknown')} ({rec.get('variety', 'Standard')})")
                print(f"      - Suitability: {rec.get('suitability_score', 0)*100:.1f}%")
                print(f"      - Expected yield: {rec.get('expected_yield', 'N/A')} kg/hectare")
                print(f"      - Reason: {rec.get('reason', 'No reason provided')}")
        
        if 'satellite_data' in response.data and response.data['satellite_data']:
            print("\n   🛰️ Satellite insights:")
            sat_data = response.data['satellite_data']
            if isinstance(sat_data, str):
                print(f"   {sat_data}")
            else:
                for key, value in sat_data.items():
                    print(f"   - {key}: {value}")
                    
        print("\n" + "-" * 40)


async def demo_irrigation_scheduling():
    """Demonstrate irrigation scheduling with AgriMitr model"""
    print("\n\n💧 DEMO 2: AgriMitr Irrigation Scheduling")
    print("-" * 60)
    
    crops = [
        {
            "name": "Rice",
            "type": CropType.RICE.value,
            "location_name": "Bihar, India",
            "lat": 25.0961,
            "lng": 85.3131,
            "soil": SoilType.CLAY.value
        },
        {
            "name": "Wheat",
            "type": CropType.WHEAT.value,
            "location_name": "Punjab, India",
            "lat": 30.9010,
            "lng": 75.8573,
            "soil": SoilType.LOAM.value
        }
    ]
    
    for crop_data in crops:
        print(f"\n🌾 Crop: {crop_data['name']} in {crop_data['location_name']}")
        
        query = AgricultureQuery(
            query_id=f"irrigation-{crop_data['name'].lower()}",
            query_text=f"Create an irrigation schedule for my {crop_data['name'].lower()} crop",
            query_domain="irrigation",
            crop_type=crop_data['type'],
            location=Location(
                latitude=crop_data['lat'],
                longitude=crop_data['lng'],
                address=crop_data['location_name'],
                region=crop_data['location_name'].split(',')[0]
            ),
            soil_type=crop_data['soil'],
            timestamp=datetime.now()
        )
        
        print("   💧 Calculating optimal irrigation schedule...")
        response = await irrigation_agent.process_query(query)
        
        if response.success:
            print("   ✅ Irrigation schedule generated successfully")
            
            if 'water_requirement' in response.data:
                print(f"   📊 Total water requirement: {response.data['water_requirement']} mm")
                
            if 'efficiency' in response.data:
                print(f"   🔍 System efficiency: {response.data['efficiency']*100:.1f}%")
            
            if 'schedule' in response.data and response.data['schedule']:
                print("\n   📅 Irrigation schedule for next 14 days:")
                for i, entry in enumerate(response.data['schedule'][:5], 1):
                    print(f"   {i}. {entry.get('date', 'Unknown date')}: {entry.get('amount', 0)} mm")
                    print(f"      Duration: {entry.get('duration_minutes', 0)} minutes")
                    print(f"      Water saved: {entry.get('water_saving_percentage', 0):.1f}%")
            
            if 'satellite_enhanced' in response.data and response.data['satellite_enhanced']:
                print("\n   🛰️ Schedule enhanced with satellite data")
                if 'soil_moisture_data' in response.data:
                    print(f"   💧 Current soil moisture: {response.data['soil_moisture_data'].get('value', 'N/A')}%")
        else:
            print(f"   ❌ Error: {response.message}")
            
        print("\n" + "-" * 40)


async def demo_disease_identification():
    """Demonstrate disease identification with AgriMitr CNN model"""
    print("\n\n🔍 DEMO 3: AgriMitr Disease Identification")
    print("-" * 60)
    
    # In a real scenario, we would load actual plant disease images
    # For this demo, we'll simulate image data
    
    test_cases = [
        {
            "name": "Healthy Tomato Plant",
            "crop": CropType.TOMATO.value,
            "image_path": "AgriMitr/Datasets/PlantVillage/Tomato___healthy/0a8e7508-7777-4fe1-ad2f-246632afe65f___RS_HL 9782.JPG",
            "location_name": "Karnataka, India",
            "lat": 12.9716,
            "lng": 77.5946
        },
        {
            "name": "Apple with Cedar Apple Rust",
            "crop": CropType.APPLE.value,
            "image_path": "AgriMitr/Datasets/PlantVillage/Apple___Cedar_apple_rust/0040591c-ae02-4274-a777-3919cc1c7700___FREC_C.Rust 3847.JPG",
            "location_name": "Himachal Pradesh, India",
            "lat": 31.1048,
            "lng": 77.1734
        }
    ]
    
    for test in test_cases:
        print(f"\n📸 Sample: {test['name']}")
        
        # Try to load the image if it exists, otherwise use a placeholder
        image_data = None
        try:
            if os.path.exists(test["image_path"]):
                with open(test["image_path"], "rb") as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
                    print("   ✅ Loaded sample image successfully")
            else:
                print(f"   ⚠️ Sample image not found at {test['image_path']}")
                print("   ⚠️ Using simulated disease image data")
                # Create a placeholder 1x1 pixel
                image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"
        except Exception as e:
            print(f"   ❌ Error loading image: {e}")
            continue
            
        query = AgricultureQuery(
            query_id=f"disease-{test['crop'].lower()}",
            query_text=f"What disease is affecting my {test['crop'].lower()} plant?",
            query_domain="disease_identification",
            crop_type=test['crop'],
            location=Location(
                latitude=test['lat'],
                longitude=test['lng'],
                address=test['location_name'],
                region=test['location_name'].split(',')[0]
            ),
            timestamp=datetime.now(),
            image_data=image_data
        )
        
        print("   🔬 Analyzing plant image...")
        response = await disease_agent.process_query(query)
        
        if response.success:
            print("   ✅ Analysis complete")
            print(f"   📊 Detected: {response.data.get('disease', 'Unknown')}")
            print(f"   🔍 Confidence: {response.data.get('confidence', 0):.1f}%")
            
            if 'severity' in response.data:
                print(f"   ⚠️ Severity: {response.data['severity'].upper()}")
                
            if 'affected_area_percentage' in response.data:
                print(f"   📏 Affected area: {response.data['affected_area_percentage']}% of plant")
                
            if 'recommendations' in response.data and response.data['recommendations']:
                print("\n   💊 Treatment recommendations:")
                for treatment in response.data['recommendations'].get('treatment', [])[:3]:
                    print(f"   - {treatment}")
                    
                print("\n   🛡️ Prevention strategies:")
                for prevention in response.data['recommendations'].get('prevention', [])[:3]:
                    print(f"   - {prevention}")
        else:
            print(f"   ❌ Error: {response.message}")
            
        print("\n" + "-" * 40)


async def main():
    """Run all demos"""
    print("\nRunning demos to showcase AgriMitr model integration...")
    
    try:
        await demo_crop_recommendation()
        await demo_irrigation_scheduling()
        await demo_disease_identification()
        
        print("\n✨ AgriMitr Integration Demo Complete ✨")
        print("Advanced AI models are now enhancing your agricultural system's capabilities!")
        
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
        print(f"\n❌ Error running demo: {e}")


if __name__ == "__main__":
    asyncio.run(main())
