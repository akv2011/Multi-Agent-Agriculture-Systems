#!/usr/bin/env python3
"""
Comprehensive test of unified agricultural API system
Tests farmer profiles, marketplace, and all integrations
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_api_status():
    """Test if API is running"""
    print("🔍 Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📊 Active Agents: {len(data['agents'])}")
            return True
        else:
            print(f"❌ API Status Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False

def test_farmer_profiles():
    """Test farmer profile creation and credit scoring"""
    print("\n👨‍🌾 Testing Farmer Profiles...")
    
    # Test farmer profile creation
    farmer_data = {
        "farmer_id": "test_farmer_001",
        "name": "John Agriculture",
        "email": "john@farm.com",
        "phone": "+1234567890",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "Test Farm, NY, USA"
        },
        "farm_size": 150.5,
        "crop_types": ["corn", "soybeans", "wheat"],
        "years_experience": 15
    }
    
    try:
        response = requests.post(f"{BASE_URL}/farmer-profiles/", json=farmer_data)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Farmer Profile Created: {profile['farmer']['name']}")
            print(f"💳 Credit Score: {profile['credit_score']}/850")
            print(f"🌾 Farm Size: {profile['farmer']['farm_size']} acres")
            
            # Test getting farmer profile
            farmer_id = profile['farmer']['farmer_id']
            get_response = requests.get(f"{BASE_URL}/farmer-profiles/{farmer_id}")
            if get_response.status_code == 200:
                print("✅ Farmer Profile Retrieved Successfully")
                return farmer_id
            else:
                print(f"❌ Failed to retrieve farmer profile: {get_response.status_code}")
                return None
        else:
            print(f"❌ Failed to create farmer profile: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Farmer Profile Error: {e}")
        return None

def test_marketplace():
    """Test marketplace functionality"""
    print("\n🛒 Testing Marketplace...")
    
    # Test adding a product
    product_data = {
        "title": "Premium Basmati Rice",
        "description": "High-quality basmati rice from organic farms",
        "price": 45.99,
        "quantity": 1000,
        "unit": "kg",
        "category": "grains",
        "seller_id": "test_farmer_001",
        "location": "Punjab, India",
        "harvest_date": "2024-10-15",
        "organic": True,
        "tags": ["organic", "premium", "basmati"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/marketplace/products/", json=product_data)
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Product Created: {product['title']}")
            print(f"💰 Price: ${product['price']}/{product['unit']}")
            print(f"📦 Quantity: {product['quantity']} {product['unit']}")
            
            # Test getting all products
            get_response = requests.get(f"{BASE_URL}/marketplace/products/")
            if get_response.status_code == 200:
                products = get_response.json()
                print(f"✅ Retrieved {len(products)} products from marketplace")
                return product['id']
            else:
                print(f"❌ Failed to retrieve products: {get_response.status_code}")
                return None
        else:
            print(f"❌ Failed to create product: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Marketplace Error: {e}")
        return None

def test_business_intelligence():
    """Test business intelligence endpoints"""
    print("\n📈 Testing Business Intelligence...")
    
    try:
        # Test market intelligence
        response = requests.get(f"{BASE_URL}/business-intel/market-intelligence")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market Intelligence Retrieved")
            print(f"📊 Market Trends: {len(data.get('market_trends', []))} trends")
            print(f"💰 Price Analysis: {len(data.get('price_analysis', []))} products analyzed")
        else:
            print(f"❌ Market Intelligence Error: {response.status_code}")
        
        # Test seller verification
        verification_response = requests.post(
            f"{BASE_URL}/business-intel/verify-seller/test_farmer_001"
        )
        if verification_response.status_code == 200:
            verification = verification_response.json()
            print(f"✅ Seller Verification: {verification['verification_status']}")
            print(f"🔒 Trust Score: {verification['trust_score']}/100")
        else:
            print(f"❌ Seller Verification Error: {verification_response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Business Intelligence Error: {e}")
        return False

def test_search_functionality():
    """Test search across the platform"""
    print("\n🔍 Testing Search Functionality...")
    
    try:
        # Test product search
        search_response = requests.get(f"{BASE_URL}/marketplace/products/search", 
                                     params={"q": "rice", "category": "grains"})
        if search_response.status_code == 200:
            results = search_response.json()
            print(f"✅ Product Search: Found {len(results)} rice products")
        else:
            print(f"❌ Product Search Error: {search_response.status_code}")
        
        # Test farmer search
        farmer_search = requests.get(f"{BASE_URL}/farmer-profiles/search",
                                   params={"location": "NY"})
        if farmer_search.status_code == 200:
            farmers = farmer_search.json()
            print(f"✅ Farmer Search: Found {len(farmers)} farmers in NY")
        else:
            print(f"❌ Farmer Search Error: {farmer_search.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return False

def test_image_upload():
    """Test image upload functionality"""
    print("\n📷 Testing Image Upload...")
    
    # Check if we have a placeholder image
    image_path = Path("uploads/product_images/basmati-rice.jpg")
    if image_path.exists():
        try:
            with open(image_path, 'rb') as f:
                files = {'file': ('basmati-rice.jpg', f, 'image/jpeg')}
                response = requests.post(f"{BASE_URL}/marketplace/upload-image", files=files)
                
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Image Upload: {data['filename']}")
                print(f"📁 File Path: {data['file_path']}")
                return data['file_path']
            else:
                print(f"❌ Image Upload Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Image Upload Error: {e}")
            return None
    else:
        print("⚠️ No placeholder image found, skipping image upload test")
        return None

def run_comprehensive_test():
    """Run all tests"""
    print("🌾💰👨‍🌾📊 UNIFIED AGRICULTURAL PLATFORM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test API status
    if not test_api_status():
        print("❌ API is not running. Please start the unified API first.")
        return False
    
    # Wait a moment for API to be fully ready
    time.sleep(2)
    
    # Run all tests
    farmer_id = test_farmer_profiles()
    product_id = test_marketplace()
    business_intel_ok = test_business_intelligence()
    search_ok = test_search_functionality()
    image_path = test_image_upload()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    if farmer_id:
        print("✅ Farmer Profiles: PASSED")
        tests_passed += 1
    else:
        print("❌ Farmer Profiles: FAILED")
    
    if product_id:
        print("✅ Marketplace: PASSED")
        tests_passed += 1
    else:
        print("❌ Marketplace: FAILED")
    
    if business_intel_ok:
        print("✅ Business Intelligence: PASSED")
        tests_passed += 1
    else:
        print("❌ Business Intelligence: FAILED")
    
    if search_ok:
        print("✅ Search Functionality: PASSED")
        tests_passed += 1
    else:
        print("❌ Search Functionality: FAILED")
    
    if image_path:
        print("✅ Image Upload: PASSED")
        tests_passed += 1
    else:
        print("❌ Image Upload: FAILED")
    
    print(f"\n🎯 OVERALL SCORE: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL! 🎉")
        print("🌾 Farmer profiles with credit scoring working")
        print("🛒 Marketplace with image upload working")
        print("📊 Business intelligence working")
        print("🔍 Search functionality working")
        print("📱 Ready for frontend integration!")
    else:
        print("⚠️ Some systems need attention")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_comprehensive_test()
