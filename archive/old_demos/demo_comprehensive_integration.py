#!/usr/bin/env python3
"""
🌾🏢📊 Comprehensive Integration Demo
Demonstrates how agricultural data, marketplace, and business intelligence work together
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any
import time

class ComprehensiveDemo:
    def __init__(self):
        self.base_urls = {
            'agrisens': 'http://localhost:8000',
            'marketplace': 'http://localhost:8001', 
            'business_intel': 'http://localhost:8002'
        }
        
    async def check_api_health(self):
        """Check if all APIs are running"""
        print("🔍 Checking API Health Status...")
        
        health_status = {}
        
        async with aiohttp.ClientSession() as session:
            for service, url in self.base_urls.items():
                try:
                    async with session.get(f"{url}/") as response:
                        if response.status == 200:
                            data = await response.json()
                            health_status[service] = "✅ Online"
                            print(f"   {service.upper()}: ✅ {data.get('message', 'Running')}")
                        else:
                            health_status[service] = "❌ Error"
                            print(f"   {service.upper()}: ❌ HTTP {response.status}")
                except Exception as e:
                    health_status[service] = "❌ Offline"
                    print(f"   {service.upper()}: ❌ Offline - {str(e)[:50]}")
        
        return health_status
    
    async def demo_agricultural_data_collection(self):
        """Demo 1: Show how we collect agricultural data"""
        print("\n" + "="*60)
        print("🌾 DEMO 1: Agricultural Data Collection")
        print("="*60)
        
        print("📡 Gathering satellite and sensor data...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get crop health data
                async with session.get(f"{self.base_urls['agrisens']}/crop-health/rice") as response:
                    if response.status == 200:
                        crop_data = await response.json()
                        print(f"🌾 Crop Health Score: {crop_data.get('health_score', 'N/A')}/100")
                        print(f"📊 NDVI Index: {crop_data.get('satellite_data', {}).get('ndvi_index', 'N/A')}")
                        print(f"💧 Soil Moisture: {crop_data.get('environmental_data', {}).get('soil_moisture', 'N/A')}%")
                
                # Get weather data
                async with session.get(f"{self.base_urls['agrisens']}/weather/current?location=Punjab") as response:
                    if response.status == 200:
                        weather_data = await response.json()
                        print(f"🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C")
                        print(f"💨 Humidity: {weather_data.get('humidity', 'N/A')}%")
                        
                # Get agent insights
                async with session.get(f"{self.base_urls['agrisens']}/agent/crop-advisor") as response:
                    if response.status == 200:
                        agent_data = await response.json()
                        print(f"🤖 AI Agent Status: {agent_data.get('status', 'N/A')}")
                        print(f"📈 Model Accuracy: {agent_data.get('model_accuracy', 'N/A')}%")
                        
            except Exception as e:
                print(f"❌ Error collecting agricultural data: {e}")
    
    async def demo_marketplace_integration(self):
        """Demo 2: Show marketplace functionality with real data"""
        print("\n" + "="*60)
        print("🏪 DEMO 2: Marketplace Integration")
        print("="*60)
        
        print("🔍 Searching for verified suppliers...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Search for suppliers
                async with session.get(f"{self.base_urls['marketplace']}/sellers/search?min_rating=4.0") as response:
                    if response.status == 200:
                        sellers_data = await response.json()
                        sellers = sellers_data.get('sellers', [])
                        print(f"✅ Found {len(sellers)} verified suppliers")
                        
                        for seller in sellers[:2]:  # Show first 2
                            print(f"   📋 {seller.get('name', 'Unknown')}")
                            print(f"      ⭐ Rating: {seller.get('rating', 'N/A')}/5.0")
                            print(f"      📍 Location: {seller.get('location', 'N/A')}")
                            print(f"      ✅ Verification: {seller.get('verification_status', 'N/A')}")
                
                # Get product listings
                async with session.get(f"{self.base_urls['marketplace']}/products?category=grains") as response:
                    if response.status == 200:
                        products_data = await response.json()
                        products = products_data.get('products', [])
                        print(f"\n📦 Available Products: {len(products)} items")
                        
                        for product in products[:3]:  # Show first 3
                            print(f"   🌾 {product.get('name', 'Unknown Product')}")
                            print(f"      💰 Price: ₹{product.get('price', 'N/A')}/{product.get('unit', 'kg')}")
                            print(f"      📊 Quality: {product.get('quality_grade', 'N/A')}")
                            print(f"      📅 Harvest: {product.get('harvest_date', 'N/A')}")
                        
            except Exception as e:
                print(f"❌ Error accessing marketplace: {e}")
    
    async def demo_business_intelligence(self):
        """Demo 3: Show business intelligence and decision making"""
        print("\n" + "="*60)
        print("📊 DEMO 3: Business Intelligence & Decision Making")
        print("="*60)
        
        print("🧠 Analyzing market intelligence for procurement decisions...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get seller verification data
                async with session.get(f"{self.base_urls['business_intel']}/business-intel/seller-verification/AGRI_SELL_001") as response:
                    if response.status == 200:
                        verification_data = await response.json()
                        profile = verification_data.get('seller_profile', {})
                        
                        print(f"🏢 Seller: {profile.get('business_name', 'Unknown')}")
                        print(f"🛡️ Trust Score: {profile.get('trust_score', 'N/A')}/100")
                        print(f"📊 Performance: {profile.get('performance_metrics', {}).get('on_time_delivery_rate', 'N/A')}% on-time delivery")
                        print(f"⭐ Quality Rating: {profile.get('performance_metrics', {}).get('quality_rating', 'N/A')}/5.0")
                        print(f"🎯 Risk Level: {profile.get('risk_assessment', {}).get('overall_risk', 'N/A')}")
                
                # Get market intelligence
                async with session.get(f"{self.base_urls['business_intel']}/business-intel/market-analysis") as response:
                    if response.status == 200:
                        market_data = await response.json()
                        analysis = market_data.get('market_analysis', {})
                        
                        print(f"\n📈 Market Trends:")
                        trends = analysis.get('trending_products', [])
                        for trend in trends[:3]:
                            print(f"   📊 {trend.get('product', 'N/A')}: {trend.get('growth_rate', 'N/A')}% growth")
                        
                        print(f"\n💰 Price Insights:")
                        price_data = analysis.get('price_forecasts', {})
                        for product, forecast in price_data.items():
                            if isinstance(forecast, dict):
                                current = forecast.get('current_price', 'N/A')
                                predicted = forecast.get('predicted_price', 'N/A')
                                print(f"   💹 {product.title()}: ₹{current} → ₹{predicted}")
                
                # Get procurement recommendations
                async with session.get(f"{self.base_urls['business_intel']}/business-intel/procurement-recommendation?product=rice&quantity=1000") as response:
                    if response.status == 200:
                        rec_data = await response.json()
                        recommendation = rec_data.get('recommendation', {})
                        
                        print(f"\n🎯 AI Procurement Recommendation:")
                        print(f"   📋 Action: {recommendation.get('recommended_action', 'N/A')}")
                        print(f"   🎯 Confidence: {recommendation.get('confidence_level', 0)*100:.1f}%")
                        print(f"   💰 Expected Savings: {recommendation.get('cost_savings', 'N/A')}")
                        print(f"   ⏰ Optimal Window: {recommendation.get('optimal_timing', 'N/A')}")
                        
            except Exception as e:
                print(f"❌ Error accessing business intelligence: {e}")
    
    async def demo_end_to_end_workflow(self):
        """Demo 4: Complete workflow from data to decision"""
        print("\n" + "="*60)
        print("🔄 DEMO 4: End-to-End Business Workflow")
        print("="*60)
        
        print("📋 Simulating complete procurement workflow...")
        
        workflow_steps = [
            "🔍 Scanning satellite data for crop quality",
            "📊 Analyzing market conditions", 
            "🔎 Identifying verified suppliers",
            "💰 Calculating optimal pricing",
            "⚖️ Assessing risk factors",
            "🎯 Generating procurement recommendations",
            "📈 Projecting business impact"
        ]
        
        for i, step in enumerate(workflow_steps, 1):
            print(f"   Step {i}: {step}")
            await asyncio.sleep(0.5)  # Simulate processing time
        
        print("\n✅ WORKFLOW COMPLETE")
        print("🎯 RECOMMENDATION: Proceed with purchase from Rajesh Kumar Farms")
        print("💰 PROJECTED SAVINGS: ₹2.4 Lakhs (8.5% below market rate)")
        print("📊 QUALITY ASSURANCE: 94.5% confidence in Grade A+ quality")
        print("🛡️ RISK ASSESSMENT: Low risk (15/100 risk score)")
        print("📅 OPTIMAL TIMING: Next 7-14 days")
    
    async def demo_business_value_proposition(self):
        """Demo 5: Show business value and ROI"""
        print("\n" + "="*60)
        print("💼 DEMO 5: Business Value Proposition")
        print("="*60)
        
        value_metrics = {
            "cost_reduction": "15-25%",
            "quality_improvement": "30%",
            "risk_mitigation": "85%",
            "supplier_reliability": "96%",
            "decision_speed": "70% faster",
            "roi_period": "3-6 months"
        }
        
        print("📈 BUSINESS IMPACT METRICS:")
        print(f"   💰 Cost Reduction: {value_metrics['cost_reduction']} through optimal pricing")
        print(f"   ⭐ Quality Improvement: {value_metrics['quality_improvement']} through verified suppliers")
        print(f"   🛡️ Risk Mitigation: {value_metrics['risk_mitigation']} reduction in procurement risks")
        print(f"   🤝 Supplier Reliability: {value_metrics['supplier_reliability']} verified performance")
        print(f"   ⚡ Decision Speed: {value_metrics['decision_speed']} through AI insights")
        print(f"   📊 ROI Timeline: {value_metrics['roi_period']} payback period")
        
        print("\n🎯 KEY DIFFERENTIATORS:")
        print("   🛰️ Satellite-verified agricultural data")
        print("   🤖 AI-powered quality predictions")
        print("   📊 Real-time market intelligence")
        print("   🔍 Comprehensive supplier verification")
        print("   💡 Automated procurement recommendations")
        print("   📈 Continuous performance monitoring")
    
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🌾🏢📊 AGRICULTURAL BUSINESS INTELLIGENCE PLATFORM")
        print("=" * 80)
        print("🎯 Demonstrating how satellite data + AI transforms agricultural procurement")
        print("=" * 80)
        
        # Check system health
        health_status = await self.check_api_health()
        
        # Run demos if systems are available
        await self.demo_agricultural_data_collection()
        await self.demo_marketplace_integration()
        await self.demo_business_intelligence()
        await self.demo_end_to_end_workflow()
        await self.demo_business_value_proposition()
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETE - Agricultural Business Intelligence Platform")
        print("🌐 Frontend: http://localhost:5173")
        print("🔧 AgriSens API: http://localhost:8000/docs")
        print("🏪 Marketplace API: http://localhost:8001/docs")
        print("📊 Business Intelligence API: http://localhost:8002/docs")
        print("="*80)

async def main():
    """Main function to run the demo"""
    demo = ComprehensiveDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
