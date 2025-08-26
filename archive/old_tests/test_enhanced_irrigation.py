#!/usr/bin/env python3
"""
Test Enhanced System with Irrigation Query
Tests the complete enhanced system with a real irrigation query to verify formatting
"""

import requests
import json
import time

def test_irrigation_query():
    """Test the enhanced system with an irrigation query"""
    
    base_url = "http://localhost:8000"
    
    # Test query about irrigation
    irrigation_query = {
        "query_text": "I need irrigation advice for my wheat crop. My farm is located at latitude 10.81, longitude 78.69. The soil moisture is low and I want to know when and how much to irrigate.",
        "location": "latitude 10.81, longitude 78.69",
        "language": "en",
        "include_satellite": True,
        "priority_level": "high",
        "context": {
            "crop_type": "wheat",
            "soil_moisture": "low",
            "latitude": 10.81,
            "longitude": 78.69
        }
    }
    
    print("=== TESTING ENHANCED IRRIGATION QUERY ===")
    print(f"Query: {irrigation_query['query_text']}")
    print(f"Location: {irrigation_query['location']}")
    print(f"Context: {irrigation_query['context']}")
    print()
    
    try:
        # Submit the query
        print("1. Submitting query to enhanced API...")
        response = requests.post(
            f"{base_url}/api/enhanced/query",
            json=irrigation_query,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query submitted successfully!")
            
            # Check the formatted response
            formatted_response = result.get("formatted_response", {})
            
            print("\n2. Checking Executive Summary:")
            exec_summary = formatted_response.get("executive_summary", {})
            print(f"   Query Type: {exec_summary.get('query_type', 'N/A')}")
            print(f"   Key Insight: {exec_summary.get('key_insight', 'N/A')[:100]}...")
            print(f"   Primary Recommendation: {exec_summary.get('primary_recommendation', 'N/A')[:100]}...")
            
            print("\n3. Checking Detailed Analysis:")
            detailed_analysis = formatted_response.get("detailed_analysis", [])
            print(f"   Number of sections: {len(detailed_analysis)}")
            
            for i, section in enumerate(detailed_analysis[:3], 1):
                print(f"   Section {i}: {section.get('title', 'N/A')}")
                content = section.get('content', '')
                print(f"   Content preview: {content[:150]}...")
                
                # Check for markdown artifacts
                has_asterisks = '*' in content
                has_backticks = '`' in content
                has_hashes = '#' in content
                
                print(f"   ✓ No asterisks: {not has_asterisks}")
                print(f"   ✓ No backticks: {not has_backticks}")
                print(f"   ✓ No hashes: {not has_hashes}")
                print()
            
            print("4. Checking Recommendations:")
            recommendations = formatted_response.get("actionable_recommendations", [])
            print(f"   Number of recommendations: {len(recommendations)}")
            
            for rec in recommendations[:3]:
                action = rec.get('action', '')
                print(f"   Priority {rec.get('priority', 'N/A')}: {action[:100]}...")
                
                # Check for markdown artifacts
                has_asterisks = '*' in action
                print(f"   ✓ No asterisks: {not has_asterisks}")
            
            print("\n5. Checking Formatted Display:")
            formatted_display = formatted_response.get("formatted_display", {})
            sections = formatted_display.get("sections", [])
            print(f"   Number of display sections: {len(sections)}")
            
            for section in sections[:3]:
                title = section.get('title', '')
                content = section.get('content', '')
                print(f"   Section: {title}")
                print(f"   Content preview: {content[:100]}...")
                
                # Check for markdown artifacts in display content
                has_asterisks = '*' in content
                has_backticks = '`' in content
                print(f"   ✓ No asterisks in display: {not has_asterisks}")
                print(f"   ✓ No backticks in display: {not has_backticks}")
                print()
            
            # Overall assessment
            print("=== FORMATTING ASSESSMENT ===")
            
            # Check all formatted content for markdown artifacts
            all_content = []
            all_content.append(str(formatted_response.get("executive_summary", {})))
            all_content.extend([section.get('content', '') for section in detailed_analysis])
            all_content.extend([rec.get('action', '') for rec in recommendations])
            all_content.extend([section.get('content', '') for section in sections])
            
            full_text = ' '.join(all_content)
            
            asterisk_count = full_text.count('*')
            backtick_count = full_text.count('`')
            hash_count = full_text.count('#')
            
            print(f"Total asterisks found: {asterisk_count}")
            print(f"Total backticks found: {backtick_count}")
            print(f"Total hash symbols found: {hash_count}")
            
            success = asterisk_count == 0 and backtick_count == 0 and hash_count == 0
            print(f"\n🎯 SYSTEM FORMATTING SUCCESS: {success}")
            
            if success:
                print("✅ Enhanced system successfully formats all AI responses!")
                print("✅ No markdown artifacts found in irrigation analysis!")
            else:
                print("⚠️  Some markdown artifacts still present in system responses.")
                
        else:
            print(f"❌ Query failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to enhanced API server.")
        print("Make sure the enhanced API server is running on port 8000.")
        print("You can start it with: python enhanced_demo_api.py")
        
    except Exception as e:
        print(f"❌ Error testing enhanced system: {e}")

if __name__ == "__main__":
    test_irrigation_query()
