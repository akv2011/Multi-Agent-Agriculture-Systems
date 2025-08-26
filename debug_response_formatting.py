#!/usr/bin/env python3
"""
Debug Response Formatting
Debug the response formatter to see what's happening with content extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.response_formatter import ResponseFormatter

def debug_response_formatting():
    """Debug response formatting to see content extraction"""
    
    # Sample raw response with markdown formatting
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
    
    print("=== RAW RESPONSE ===")
    print(raw_response)
    print()
    
    # Step 1: Clean the response
    cleaned = formatter._clean_raw_response(raw_response)
    print("=== AFTER _clean_raw_response ===")
    print(cleaned)
    print()
    
    # Step 2: Comprehensive cleaning
    comprehensive_cleaned = formatter._comprehensive_text_cleaning(cleaned)
    print("=== AFTER _comprehensive_text_cleaning ===")
    print(comprehensive_cleaned)
    print()
    
    # Step 3: Extract components
    components = formatter._extract_structured_components(comprehensive_cleaned)
    
    # Debug section header detection
    print("=== SECTION HEADER DETECTION DEBUG ===")
    lines = comprehensive_cleaned.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            is_header = formatter._is_section_header(line)
            print(f"Line {i}: '{line}' -> Header: {is_header}")
    print()
    
    print("=== EXTRACTED COMPONENTS ===")
    print(f"Sections found: {len(components['sections'])}")
    for i, section in enumerate(components['sections']):
        print(f"  Section {i+1}: '{section['title']}'")
        print(f"    Content: {section['content'][:100]}...")
    print()
    print(f"Recommendations found: {len(components['recommendations'])}")
    for i, rec in enumerate(components['recommendations'][:3]):
        print(f"  {i+1}: {rec}")
    print()
    print(f"Warnings found: {len(components['warnings'])}")
    for warning in components['warnings']:
        print(f"  Warning: {warning}")
    print()
    print(f"Data points found: {len(components['data_points'])}")
    for dp in components['data_points'][:3]:
        print(f"  Data: {dp['text']} -> {dp['values']}")

if __name__ == "__main__":
    debug_response_formatting()
