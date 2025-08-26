"""
Test agriculture models specifically
"""

def test_agriculture_models():
    print("Testing Agriculture Models...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test step by step
        print("1. Testing enum imports...")
        from src.core.agriculture_models import CropType, SeasonType, Language
        print("✓ Enums imported")
        
        print("2. Testing query domain...")
        from src.core.agriculture_models import QueryDomain
        print("✓ QueryDomain imported")
        
        print("3. Testing agriculture capability...")
        from src.core.agriculture_models import AgricultureCapability
        print("✓ AgricultureCapability imported")
        
        print("4. Testing dataclasses...")
        from src.core.agriculture_models import Location, FarmProfile
        print("✓ Dataclasses imported")
        
        print("5. Testing main query model...")
        from src.core.agriculture_models import AgricultureQuery
        print("✓ AgricultureQuery imported")
        
        print("6. Creating test query...")
        query = AgricultureQuery(
            query_text="Test query",
            query_language=Language.ENGLISH,
            user_id="test_user"
        )
        print(f"✓ Query created: {query.query_text}")
        
        print("\n🎉 ALL AGRICULTURE MODELS WORK!")
        return True
        
    except Exception as e:
        print(f"✗ Agriculture models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agriculture_models()
    exit(0 if success else 1)
