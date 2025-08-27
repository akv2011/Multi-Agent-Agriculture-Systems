#!/usr/bin/env python3
"""
Simple test to check query processing without heavy dependencies
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_simple_import():
    """Test basic imports"""
    
    try:
        print("Testing imports...")
        from src.services.enhanced_query_processor import enhanced_processor
        print("✅ Enhanced query processor imported successfully")
        
        from src.models.agriculture import AgricultureQuery
        print("✅ Agriculture query model imported successfully")
        
        from src.services.response_formatter import ResponseFormatter
        print("✅ Response formatter imported successfully")
        
        # Test a simple query creation
        query = AgricultureQuery(
            text="Test query",
            location="Test location"
        )
        print("✅ Query object created successfully")
        
        # Test response formatter
        formatter = ResponseFormatter()
        print("✅ Response formatter instantiated successfully")
        
        print("\n🎯 All basic components are working correctly!")
        
    except Exception as e:
        print(f"❌ Error during import/initialization: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_import())
