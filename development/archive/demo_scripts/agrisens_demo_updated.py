#!/usr/bin/env python3
"""
AgriMitr Integration Demo - Updated
Demonstrates all integrated AgriMitr models with the Multi-Agent Agriculture Systems
"""

import sys
import os
import json
import base64
from datetime import datetime
import asyncio
from typing import Dict, Any, List
import logging
import argparse

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
from src.agents.fertilizer_recommendation_agent import FertilizerRecommendationAgent
from src.agents.weather_forecast_agent import WeatherForecastAgent
from src.agents.smart_farming_guidance_agent import SmartFarmingGuidanceAgent
from src.agents.agriculture_router import AgricultureRouter

# Import Google Search Service
from src.services.google_search_service import create_google_search_service

# Import models
from src.core.agriculture_models import (
    AgricultureQuery, Location, SoilType, CropType, SeasonType, 
    AgricultureTask, TaskPriority
)

def print_header(title, width=60):
    """Print a formatted header"""
    print("\n\n" + "=" * width)
    print(f"{title}")
    print("=" * width)
    
def print_section(title, width=60):
    """Print a formatted section header"""
    print("\n" + "-" * width)
    print(f"{title}")
    print("-" * width)

def print_result(label, value):
    """Print a formatted result"""
    print(f"   {label}: {value}")

class AgriMitrDemo:
    """Demo class for showcasing AgriMitr integration"""
    
    def __init__(self):
        """Initialize the demo"""
        print("🌾🔍 AgriMitr AI Models Integration Demo")
        print("=" * 60)
        print("Demonstrating the integration of advanced AgriMitr AI models")
        print("with the Multi-Agent Agriculture Systems")
        
        # Initialize agents
        self.crop_agent = CropSelectionAgent("crop-agent-1", "AgriMitr Crop Selection")
        self.irrigation_agent = IrrigationAgent("irrigation-agent-1", "AgriMitr Irrigation Scheduling")
        self.disease_agent = DiseaseIdentificationAgent("disease-agent-1", "AgriMitr Disease Identification")
        self.fertilizer_agent = FertilizerRecommendationAgent("fertilizer-agent-1", "AgriMitr Fertilizer Recommendation")
        self.weather_agent = WeatherForecastAgent("weather-agent-1", "AgriMitr Weather Forecast")
        self.guidance_agent = SmartFarmingGuidanceAgent("guidance-agent-1", "AgriMitr Smart Farming Guide")
        
        # Initialize router
        self.router = AgricultureRouter()
        
        # Initialize Google Search Service
        self.search_service = create_google_search_service()
        
        # Initialize agents
        print("\n🚀 Initializing AgriMitr-powered agents...")
        self.crop_agent.initialize()
        self.irrigation_agent.initialize()
        self.disease_agent.initialize()
        self.fertilizer_agent.initialize()
        self.weather_agent.initialize()
        print("✅ All agents initialized successfully")

    async def demo_crop_recommendation(self):
        """Demonstrate crop recommendation with AgriMitr ML model"""
        print_header("🌱 DEMO 1: AgriMitr Crop Recommendation (99.55% accuracy)")
        
        locations = [
            {
                "name": "Punjab, India",
                "lat": 30.9010,
                "lng": 75.8573,
                "soil": SoilType.CLAY_LOAM,
                "description": "Northern Indian agricultural heartland"
            },
            {
                "name": "Maharashtra, India",
                "lat": 19.7515,
                "lng": 75.7139,
                "soil": SoilType.BLACK_SOIL,
                "description": "Western Indian cotton belt"
            }
        ]
        
        for location_data in locations:
            print_section(f"📍 Location: {location_data['name']} ({location_data['description']})")
            
            query = AgricultureQuery(
                query_text=f"What crops should I plant in {location_data['name']}?",
                location=Location(
                    latitude=location_data['lat'],
                    longitude=location_data['lng'],
                    state=location_data['name'].split(',')[0],
                    district="Unknown"
                ),
                soil_type=location_data['soil']
            )
            
            print("   🔍 Analyzing soil, climate, and satellite data...")
            response = await self.crop_agent.process_query(query)
            
            print_result("✅ AgriMitr ML model confidence", f"{response.data.get('AgriMitr_confidence', 'N/A')}%")
            if 'npk_analysis' in response.data:
                print_result("🧪 NPK Analysis", response.data['npk_analysis'].get('summary', 'N/A'))
            
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

    async def demo_disease_identification(self):
        """Demonstrate disease identification with AgriMitr CNN model"""
        print_header("🔍 DEMO 2: AgriMitr Disease Identification")
        
        # Demo image-based disease identification
        print_section("📷 Image-based Disease Identification")
        
        # Paths to sample disease images
        sample_images = {
            "apple_scab": "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/apple_scab.jpg",
            "tomato_late_blight": "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/tomato_late_blight.jpg",
        }
        
        # Process each sample image
        for disease_name, image_path in sample_images.items():
            if not os.path.exists(image_path):
                print(f"   ⚠️ Sample image not found: {image_path}")
                continue
                
            print(f"\n   🌿 Processing sample image: {disease_name}")
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Create query
            query = AgricultureQuery(
                query_text=f"What disease is affecting my plant?",
                image_data=image_data
            )
            
            # Process query
            print("   🔍 Analyzing image with AgriMitr CNN model...")
            response = await self.disease_agent.process_query(query)
            
            if response.success:
                print_result("🔬 Detected Disease", response.data.get('disease', 'Unknown'))
                print_result("✅ Confidence", f"{response.data.get('confidence', 0):.1f}%")
                print_result("🚨 Severity", response.data.get('severity', 'Unknown'))
                
                if 'recommendations' in response.data:
                    print("\n   💊 Treatment recommendations:")
                    for i, rec in enumerate(response.data['recommendations'][:3], 1):
                        print(f"   {i}. {rec}")
            else:
                print(f"   ❌ Error: {response.message}")
        
        # Demo text-based symptom analysis
        print_section("📝 Text-based Symptom Analysis")
        
        symptom_queries = [
            "My tomato plants have dark brown spots with white fungus underneath the leaves",
            "My rice plants have yellow and brown spots, and the leaves are curling"
        ]
        
        for symptom_text in symptom_queries:
            print(f"\n   🌿 Processing symptom description:")
            print(f"   \"{symptom_text}\"")
            
            # Create query
            query = AgricultureQuery(
                query_text=symptom_text
            )
            
            # Process query
            print("   🔍 Analyzing symptoms with AgriMitr disease model...")
            response = await self.disease_agent.process_query(query)
            
            if response.success:
                print_result("🔬 Likely Disease", response.data.get('disease', 'Unknown'))
                print_result("✅ Confidence", f"{response.data.get('confidence', 0):.1f}%")
                
                if 'recommendations' in response.data:
                    print("\n   💊 Treatment recommendations:")
                    for i, rec in enumerate(response.data['recommendations'][:3], 1):
                        print(f"   {i}. {rec}")
            else:
                print(f"   ❌ Error: {response.message}")

    async def demo_fertilizer_recommendation(self):
        """Demonstrate fertilizer recommendation with AgriMitr model"""
        print_header("🧪 DEMO 3: AgriMitr Fertilizer Recommendation")
        
        soil_samples = [
            {
                "location": "Punjab, India",
                "crop": "wheat",
                "nitrogen": 80,
                "phosphorus": 45,
                "potassium": 60,
                "ph": 7.2,
                "soil_type": SoilType.LOAM
            },
            {
                "location": "Karnataka, India",
                "crop": "rice",
                "nitrogen": 40,
                "phosphorus": 30,
                "potassium": 35,
                "ph": 6.5,
                "soil_type": SoilType.CLAY
            }
        ]
        
        for sample in soil_samples:
            print_section(f"📍 Soil Sample from {sample['location']} for {sample['crop']}")
            
            # Create query
            query = AgricultureQuery(
                query_text=f"Recommend fertilizer for my {sample['crop']} crop with N={sample['nitrogen']}, P={sample['phosphorus']}, K={sample['potassium']}, pH={sample['ph']}",
                crop_type=sample['crop'],
                soil_type=sample['soil_type'],
                location=Location(
                    state=sample['location'].split(',')[0],
                    district="Unknown"
                ),
                soil_data={
                    "nitrogen": sample['nitrogen'],
                    "phosphorus": sample['phosphorus'],
                    "potassium": sample['potassium'],
                    "ph": sample['ph']
                }
            )
            
            print("   🔍 Analyzing soil nutrient levels...")
            response = await self.fertilizer_agent.process_query(query)
            
            if response.success:
                print_result("✅ Recommended Fertilizer", response.data['recommendation']['fertilizer_name'])
                print_result("📊 NPK Ratio", response.data['recommendation']['npk_ratio'])
                print_result("⚖️ Application Rate", f"{response.data['recommendation']['application_rate']} kg/hectare")
                print_result("🌱 Application Method", response.data['recommendation']['application_method'])
                print_result("🌍 Environmental Impact", response.data['recommendation']['environmental_impact'])
                
                if 'alternatives' in response.data['recommendation']:
                    print("\n   🔄 Alternative fertilizers:")
                    for alt in response.data['recommendation']['alternatives'][:2]:
                        print(f"   - {alt}")
                
                if 'expected_benefits' in response.data['recommendation']:
                    print("\n   🌿 Expected benefits:")
                    for benefit in response.data['recommendation']['expected_benefits'][:3]:
                        print(f"   - {benefit}")
            else:
                print(f"   ❌ Error: {response.message}")

    async def demo_smart_farming_guidance(self):
        """Demonstrate smart farming guidance"""
        print_header("🌿 DEMO 4: Smart Farming Guidance")
        
        guidance_queries = [
            {
                "text": "What crop rotation system should I use for cotton?",
                "crop": "cotton",
                "location": "Gujarat, India"
            },
            {
                "text": "How can I conserve water in my rice fields?",
                "crop": "rice",
                "location": "Tamil Nadu, India"
            },
            {
                "text": "What are sustainable pest management practices for vegetables?",
                "crop": "vegetables",
                "location": "Kerala, India"
            }
        ]
        
        for query_data in guidance_queries:
            print_section(f"❓ Query: {query_data['text']}")
            
            # Create query
            query = AgricultureQuery(
                query_text=query_data['text'],
                crop_type=query_data['crop'],
                location=Location(
                    state=query_data['location'].split(',')[0],
                    district="Unknown"
                )
            )
            
            print("   🔍 Generating smart farming guidance...")
            response = await self.guidance_agent.process_query(query)
            
            if response.success:
                print_result("📚 Guidance Category", response.data.get('title', 'General guidance'))
                
                if 'recommendations' in response.data:
                    print("\n   🌱 Top recommendations:")
                    for i, rec in enumerate(response.data['recommendations'][:4], 1):
                        print(f"   {i}. {rec}")
                
                if response.data.get('crop_specific'):
                    print("\n   🌾 Crop-specific guidance provided")
                    
                if response.data.get('location_specific'):
                    print("   📍 Location-specific guidance provided")
                    
                if 'satellite_data' in response.data and response.data['satellite_data']:
                    print("\n   🛰️ Satellite-enhanced recommendations")
            else:
                print(f"   ❌ Error: {response.message}")

    async def demo_query_routing_with_fallback(self):
        """Demonstrate router with Google Search fallback"""
        print_header("🔄 DEMO 5: Intelligent Query Routing with Google Search Fallback")
        
        test_queries = [
            "Which crop is best to grow in Maharashtra during monsoon?",
            "My tomato plants have brown spots with white fungus underneath",
            "What fertilizer should I use for soil with low nitrogen?",
            "What is the current MSP for wheat in India?",
            "How can I implement sustainable farming practices for cotton?",
            "Will it rain next week in Punjab?",
            "मेरे धान के पौधों पर पीले धब्बे हैं, क्या बीमारी है?"  # Hindi: My rice plants have yellow spots, what disease is it?
        ]
        
        for query_text in test_queries:
            print_section(f"❓ User Query: {query_text}")
            
            # Create task
            task = AgricultureTask(
                task_id=f"test_{datetime.now().timestamp()}",
                description=query_text,
                task_type="routing",
                priority=TaskPriority.MEDIUM
            )
            
            # Process with router
            print("   🧠 Analyzing query with Agriculture Router...")
            result = await self.router.execute(task, {})
            
            if result.get("status") == "success":
                routing_decision = result.get("routing_decision")
                
                print_result("🔍 Detected Domains", ", ".join([d.value for d in routing_decision.detected_domains]))
                print_result("🌐 Detected Language", routing_decision.detected_language.value)
                print_result("🤖 Selected Agents", ", ".join(routing_decision.selected_agents))
                print_result("📊 Confidence", f"{routing_decision.confidence:.2f}")
                
                # Check if Google Search fallback is triggered
                if result.get("use_google_search_fallback"):
                    print("\n   🔎 Google Search Fallback Activated")
                    print("   📊 This query would use Google Search API to enhance response")
                    
                if routing_decision.requires_clarification:
                    print("\n   ❓ Clarification needed:")
                    for question in routing_decision.clarification_questions:
                        print(f"   - {question}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
    async def run_all_demos(self):
        """Run all demos"""
        await self.demo_crop_recommendation()
        await self.demo_disease_identification()
        await self.demo_fertilizer_recommendation()
        await self.demo_smart_farming_guidance()
        await self.demo_query_routing_with_fallback()
        
        print("\n\n✅ All demos completed successfully!")
        print("=" * 60)
        print("AgriMitr models have been successfully integrated with the")
        print("Multi-Agent Agriculture Systems platform!")


async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="AgriMitr Integration Demo")
    parser.add_argument('--demo', type=str, choices=[
        'all', 'crop', 'disease', 'fertilizer', 'guidance', 'router'
    ], default='all', help="Specify which demo to run (default: all)")
    
    args = parser.parse_args()
    demo = AgriMitrDemo()
    
    if args.demo == 'all':
        await demo.run_all_demos()
    elif args.demo == 'crop':
        await demo.demo_crop_recommendation()
    elif args.demo == 'disease':
        await demo.demo_disease_identification()
    elif args.demo == 'fertilizer':
        await demo.demo_fertilizer_recommendation()
    elif args.demo == 'guidance':
        await demo.demo_smart_farming_guidance()
    elif args.demo == 'router':
        await demo.demo_query_routing_with_fallback()


if __name__ == "__main__":
    asyncio.run(main())
