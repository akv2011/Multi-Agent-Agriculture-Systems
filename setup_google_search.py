#!/usr/bin/env python3
"""
Setup Google Custom Search Engine for Agricultural Ground Search

This script helps set up a Google Custom Search Engine optimized for agricultural content.
It provides instructions and generates the configuration needed for the ground search functionality.
"""

import os
import sys
import json
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def print_header():
    """Print the setup header"""
    print("=" * 80)
    print("  GOOGLE CUSTOM SEARCH ENGINE SETUP FOR AGRICULTURAL GROUND SEARCH")
    print("=" * 80)
    print()

def check_current_config():
    """Check current configuration"""
    print("📋 CURRENT CONFIGURATION:")
    print("-" * 40)
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if gemini_key:
        print(f"✅ Gemini API Key: {gemini_key[:10]}...{gemini_key[-4:]}")
    else:
        print("❌ Gemini API Key: Not configured")
    
    if search_key:
        print(f"✅ Google Search API Key: {search_key[:10]}...{search_key[-4:]}")
    else:
        print("❌ Google Search API Key: Not configured")
    
    if search_cx:
        print(f"✅ Google Search CX: {search_cx}")
    else:
        print("❌ Google Search CX: Not configured")
    
    print()
    return gemini_key, search_key, search_cx

def provide_setup_instructions():
    """Provide step-by-step setup instructions"""
    print("🔧 SETUP INSTRUCTIONS:")
    print("-" * 40)
    print()
    
    print("1. CREATE GOOGLE CUSTOM SEARCH ENGINE:")
    print("   • Go to: https://cse.google.com/cse/")
    print("   • Click 'New search engine'")
    print("   • Add these recommended sites for agricultural content:")
    print("     - icar.org.in")
    print("     - agricoop.nic.in")
    print("     - pib.gov.in")
    print("     - indiastat.com")
    print("     - agritech.tnau.ac.in")
    print("     - krishi.icar.gov.in")
    print("     - farmer.gov.in")
    print("   • Name it: 'Agriculture India Search'")
    print("   • Language: English (and Hindi if needed)")
    print("   • SafeSearch: On")
    print()
    
    print("2. CONFIGURE SEARCH ENGINE:")
    print("   • After creation, click 'Control Panel'")
    print("   • Go to 'Setup' tab")
    print("   • Under 'Basics', enable 'Search the entire web'")
    print("   • Under 'Advanced', set these preferences:")
    print("     - Country: India")
    print("     - Interface Language: English")
    print("     - Search Engine Keywords: agriculture, farming, crops, india")
    print()
    
    print("3. GET YOUR SEARCH ENGINE ID:")
    print("   • In the Control Panel, go to 'Setup' tab")
    print("   • Copy the 'Search engine ID' (cx parameter)")
    print("   • It looks like: 017576662512468239146:omuauf_lfve")
    print()
    
    print("4. ENABLE CUSTOM SEARCH API:")
    print("   • Go to: https://console.developers.google.com/")
    print("   • Create a new project or select existing one")
    print("   • Enable 'Custom Search API'")
    print("   • Create credentials (API key)")
    print("   • Restrict the API key to Custom Search API only")
    print()

def update_env_file(search_cx=None):
    """Update the .env file with the search CX"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ .env file not found at {env_file}")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add GOOGLE_SEARCH_CX
    cx_updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith("GOOGLE_SEARCH_CX="):
            if search_cx:
                new_lines.append(f"GOOGLE_SEARCH_CX={search_cx}\n")
                cx_updated = True
            else:
                new_lines.append(line)  # Keep existing
        else:
            new_lines.append(line)
    
    # Add GOOGLE_SEARCH_CX if not found and search_cx provided
    if not cx_updated and search_cx:
        new_lines.append(f"GOOGLE_SEARCH_CX={search_cx}\n")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated {env_file}")
    return True

def test_configuration():
    """Test the current configuration"""
    print("🧪 TESTING CONFIGURATION:")
    print("-" * 40)
    
    try:
        # Test Gemini API
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Test with a simple query
            response = model.generate_content("What is agriculture?")
            if response.text:
                print("✅ Gemini API: Working")
            else:
                print("❌ Gemini API: Not responding properly")
        else:
            print("❌ Gemini API: No API key configured")
    
    except Exception as e:
        print(f"❌ Gemini API: Error - {e}")
    
    # Test Google Search API (basic check)
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY") or gemini_key
    search_cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if search_key and search_cx:
        print("✅ Google Search API: Keys configured (use test script to verify)")
    elif not search_cx:
        print("❌ Google Search API: Missing CX ID")
    else:
        print("❌ Google Search API: Missing API key")
    
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check current configuration
    gemini_key, search_key, search_cx = check_current_config()
    
    if gemini_key and search_cx:
        print("🎉 Configuration appears complete!")
        test_configuration()
        
        # Offer to test the ground search
        print("You can now test the ground search functionality:")
        print("  ./ground_search_example.py 'What is the current wheat MSP in India?'")
        print()
        return 0
    
    # Provide setup instructions
    provide_setup_instructions()
    
    # Interactive setup
    print("5. INTERACTIVE SETUP:")
    print("-" * 40)
    
    if not search_cx:
        print("Enter your Google Custom Search Engine ID (cx parameter):")
        print("(Press Enter to skip and configure manually later)")
        user_cx = input("Search Engine ID: ").strip()
        
        if user_cx:
            update_env_file(search_cx=user_cx)
            print("✅ Configuration updated!")
            print()
            print("You can now test the ground search functionality:")
            print("  ./ground_search_example.py 'What is the current wheat MSP in India?'")
        else:
            print("⚠️  Skipped CX configuration. Please update .env file manually.")
    
    print()
    print("📋 NEXT STEPS:")
    print("1. Complete the Google Custom Search Engine setup if not done")
    print("2. Update your .env file with the correct GOOGLE_SEARCH_CX")
    print("3. Test the configuration with: ./ground_search_example.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
