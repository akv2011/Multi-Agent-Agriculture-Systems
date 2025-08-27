#!/usr/bin/env python3
"""
Test Response Formatting
Tests the enhanced response formatter to ensure no markdown artifacts remain
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.response_formatter import ResponseFormatter

def test_irrigation_response_formatting():
    """Test irrigation response formatting to ensure no asterisks remain"""
    
    # Sample raw response with markdown formatting (similar to what we might get from AI)
    raw_response = """
    **Irrigation Analysis for Your Crops**
    
    Based on your query about irrigation for wheat crops, here's the comprehensive analysis:
    
    **Current Soil Conditions:**
    * **Moisture Level**: 45% - needs improvement
    * **pH Level**: 6.8 - optimal range  
    * **Nutrient Status**: *Nitrogen deficient*
    
    **Irrigation Recommendations:**
    1. **Immediate Actions:**
       - Apply 25mm of water within 2-3 days
       - Use *drip irrigation* for efficient water usage
       - Monitor soil moisture levels ***daily***
    
    2. **Long-term Strategy:**
       - Install moisture sensors for automated monitoring
       - Implement `precision irrigation` techniques
       - Schedule irrigation during **early morning hours**
    
    **Expected Benefits:**
    • Improved crop yield by 15-20%
    • Reduced water consumption by 30%
    • Better nutrient absorption
    
    **Important Warning:** Avoid over-irrigation as it can lead to root rot and nutrient leaching.
    """
    
    formatter = ResponseFormatter()
    
    # Test query analysis
    query_analysis = {
        "intent": "irrigation_management",
        "domain": "agriculture",
        "language": "en"
    }
    
    # Format the response
    formatted_result = formatter.format_comprehensive_response(raw_response, query_analysis)
    
    print("=== TESTING RESPONSE FORMATTING ===\n")
    
    # Check executive summary
    print("1. Executive Summary:")
    exec_summary = formatted_result["executive_summary"]
    print(f"   Query Type: {exec_summary['query_type']}")
    print(f"   Key Insight: {exec_summary['key_insight']}")
    print(f"   Primary Recommendation: {exec_summary['primary_recommendation']}")
    print()
    
    # Check detailed analysis (most important)
    print("2. Detailed Analysis:")
    detailed_analysis = formatted_result["detailed_analysis"]
    for i, section in enumerate(detailed_analysis, 1):
        print(f"   Section {i}: {section['title']}")
        print(f"   Content: {section['content'][:200]}...")
        # Check for markdown artifacts
        has_asterisks = '*' in section['content']
        has_backticks = '`' in section['content']
        has_underscores = section['content'].count('_') > 2  # Allow some underscores in normal text
        
        print(f"   ✓ No asterisks: {not has_asterisks}")
        print(f"   ✓ No backticks: {not has_backticks}")
        print(f"   ✓ No emphasis underscores: {not has_underscores}")
        print()
    
    # Check actionable recommendations
    print("3. Actionable Recommendations:")
    recommendations = formatted_result["actionable_recommendations"]
    for rec in recommendations[:3]:
        print(f"   Priority {rec['priority']}: {rec['action']}")
        # Check for markdown artifacts in recommendations
        has_asterisks = '*' in rec['action']
        print(f"   ✓ No asterisks: {not has_asterisks}")
    print()
    
    # Check formatted display
    print("4. Formatted Display:")
    formatted_display = formatted_result["formatted_display"]
    for section in formatted_display["sections"]:
        print(f"   {section['title']}:")
        print(f"   Content preview: {section['content'][:150]}...")
        # Check for markdown artifacts
        has_asterisks = '*' in section['content']
        has_backticks = '`' in section['content']
        print(f"   ✓ No asterisks: {not has_asterisks}")
        print(f"   ✓ No backticks: {not has_backticks}")
        print()
    
    # Overall assessment
    print("=== FORMATTING ASSESSMENT ===")
    
    # Check all sections for markdown artifacts
    all_content = []
    all_content.append(str(formatted_result["executive_summary"]))
    all_content.extend([section['content'] for section in formatted_result["detailed_analysis"]])
    all_content.extend([rec['action'] for rec in formatted_result["actionable_recommendations"]])
    all_content.extend([section['content'] for section in formatted_result["formatted_display"]["sections"]])
    
    full_text = ' '.join(all_content)
    
    asterisk_count = full_text.count('*')
    backtick_count = full_text.count('`')
    hash_count = full_text.count('#')
    
    print(f"Total asterisks found: {asterisk_count}")
    print(f"Total backticks found: {backtick_count}")
    print(f"Total hash symbols found: {hash_count}")
    
    success = asterisk_count == 0 and backtick_count == 0 and hash_count == 0
    print(f"\n🎯 FORMATTING SUCCESS: {success}")
    
    if not success:
        print("\n⚠️  Issues found in formatting. Markdown artifacts still present.")
        if asterisk_count > 0:
            print(f"   - {asterisk_count} asterisks remain")
        if backtick_count > 0:
            print(f"   - {backtick_count} backticks remain") 
        if hash_count > 0:
            print(f"   - {hash_count} hash symbols remain")
    else:
        print("\n✅ All markdown formatting successfully removed!")
    
    return success

if __name__ == "__main__":
    test_irrigation_response_formatting()
