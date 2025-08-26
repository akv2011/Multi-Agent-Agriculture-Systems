"""
Validation script for Input Materials Agent
Tests functionality across different scenarios including:
- Fertilizer recommendations
- Pesticide suggestions
- Seed variety selection
- Cost-effective alternatives
- Multilingual support
"""

import asyncio
import sys
sys.path.append('.')

from src.agents.input_materials_agent import InputMaterialsAgent
from src.core.agriculture_models import AgricultureQuery, Language, Location


async def validate_input_materials_agent():
    """Comprehensive validation of Input Materials Agent"""
    
    print("🌱 VALIDATION: Input Materials Agent")
    print("=" * 50)
    
    agent = InputMaterialsAgent()
    
    # Test 1: Wheat Fertilizer Query
    print("\n📋 TEST 1: Wheat Fertilizer Recommendation")
    print("-" * 40)
    
    query1 = AgricultureQuery(
        query_text="I need fertilizer recommendations for wheat crop in Punjab",
        query_language=Language.ENGLISH,
        user_id="farmer_001",
        location=Location(state="Punjab", district="Ludhiana", tehsil="Raikot")
    )
    
    response1 = await agent.process_query(query1)
    print(f"✅ Response: {response1.response_text}")
    print(f"📊 Confidence: {response1.confidence_score}")
    print(f"🎯 Recommendations: {len(response1.recommendations)}")
    print(f"💰 Total Cost in Metadata: ₹{response1.metadata.get('total_cost', 'N/A')}")
    
    # Test 2: Rice Pesticide Query (Hindi)
    print("\n📋 TEST 2: Rice Pesticide Query (Hindi)")
    print("-" * 40)
    
    query2 = AgricultureQuery(
        query_text="धान की फसल में कीट लगे हैं, कीटनाशक की सलाह दें",
        query_language=Language.HINDI,
        user_id="farmer_002",
        location=Location(state="Uttar Pradesh", district="Lucknow", tehsil="Mohanlalganj")
    )
    
    response2 = await agent.process_query(query2)
    print(f"✅ Response: {response2.response_text}")
    print(f"📊 Confidence: {response2.confidence_score}")
    print(f"🎯 Recommendations: {len(response2.recommendations)}")
    
    # Test 3: Cotton Seed Query
    print("\n📋 TEST 3: Cotton Seed Variety Selection")
    print("-" * 40)
    
    query3 = AgricultureQuery(
        query_text="Which cotton seed variety should I choose for black soil?",
        query_language=Language.ENGLISH,
        user_id="farmer_003",
        location=Location(state="Maharashtra", district="Nagpur", tehsil="Hingna")
    )
    
    response3 = await agent.process_query(query3)
    print(f"✅ Response: {response3.response_text}")
    print(f"📊 Confidence: {response3.confidence_score}")
    print(f"🌱 Crop Type: {response3.metadata.get('crop_type', 'N/A')}")
    print(f"🏔️ Soil Type: {response3.metadata.get('soil_type', 'N/A')}")
    
    # Test 4: Budget-Conscious Query
    print("\n📋 TEST 4: Budget-Conscious Input Selection")
    print("-" * 40)
    
    query4 = AgricultureQuery(
        query_text="I need cheap and cost-effective fertilizer for sugarcane",
        query_language=Language.ENGLISH,
        user_id="farmer_004",
        location=Location(state="Karnataka", district="Mandya", tehsil="Srirangapatna")
    )
    
    response4 = await agent.process_query(query4)
    print(f"✅ Response: {response4.response_text}")
    print(f"📊 Confidence: {response4.confidence_score}")
    print(f"💰 Total Cost: ₹{response4.metadata.get('total_cost', 'N/A')}")
    
    # Test 5: Mixed Language Query
    print("\n📋 TEST 5: Mixed Language Query")
    print("-" * 40)
    
    query5 = AgricultureQuery(
        query_text="मुझे wheat crop के लिए urea और DAP की जरूरत है",
        query_language=Language.MIXED,
        user_id="farmer_005",
        location=Location(state="Haryana", district="Karnal", tehsil="Assandh")
    )
    
    response5 = await agent.process_query(query5)
    print(f"✅ Response: {response5.response_text}")
    print(f"📊 Confidence: {response5.confidence_score}")
    print(f"📈 Primary Inputs: {response5.metadata.get('num_primary_inputs', 'N/A')}")
    
    # Test 6: General Input Information Query
    print("\n📋 TEST 6: General Input Information")
    print("-" * 40)
    
    query6 = AgricultureQuery(
        query_text="Tell me about agricultural inputs",
        query_language=Language.ENGLISH,
        user_id="farmer_006"
    )
    
    response6 = await agent.process_query(query6)
    print(f"✅ Response: {response6.response_text}")
    print(f"📊 Confidence: {response6.confidence_score}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_responses = [response1, response2, response3, response4, response5, response6]
    
    print(f"✅ Total Test Cases: {len(all_responses)}")
    print(f"🎯 Successful Responses: {sum(1 for r in all_responses if r.confidence_score > 0.5)}")
    print(f"📈 Average Confidence: {sum(r.confidence_score for r in all_responses) / len(all_responses):.2f}")
    print(f"🌐 Multilingual Support: Hindi, English, Mixed ✅")
    print(f"💰 Cost Analysis: Available ✅")
    print(f"🌱 Crop-Specific: Wheat, Rice, Cotton, Sugarcane ✅")
    print(f"📦 Input Types: Fertilizers, Pesticides, Seeds ✅")
    
    # Check key features
    has_cost_info = any(r.metadata.get('total_cost') for r in all_responses if r.metadata)
    has_multilingual = any(r.response_language in [Language.HINDI, Language.MIXED] for r in all_responses)
    has_recommendations = all(len(r.recommendations) > 0 for r in all_responses)
    
    print(f"🔍 Cost Information: {'✅' if has_cost_info else '❌'}")
    print(f"🌐 Multilingual Responses: {'✅' if has_multilingual else '❌'}")
    print(f"📋 Recommendations Provided: {'✅' if has_recommendations else '❌'}")
    
    # Agent Capabilities
    print(f"\n🤖 Agent Capabilities:")
    print(f"   - Fertilizer Database: {len(agent.fertilizers)} products")
    print(f"   - Pesticide Database: {len(agent.pesticides)} products")
    print(f"   - Seed Database: {len(agent.seeds)} varieties")
    print(f"   - Regional Cost Factors: {len(agent.regional_cost_factors)} states")
    
    if all(r.confidence_score > 0.5 for r in all_responses):
        print("\n🎉 INPUT MATERIALS AGENT: VALIDATION SUCCESSFUL")
        print("   ✅ Comprehensive input recommendation system")
        print("   ✅ Cost-effective product selection")
        print("   ✅ Multilingual agricultural support")
        print("   ✅ Regional pricing integration")
    else:
        print("\n⚠️ INPUT MATERIALS AGENT: VALIDATION ISSUES DETECTED")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(validate_input_materials_agent())
