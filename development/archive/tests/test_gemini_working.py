"""
Test Gemini AI with Agriculture System
"""

import os
import asyncio
import sys
from datetime import datetime

# Set API key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyACHvqkA6UHMcZwSnhSuB50lhrnJzxOAjg'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_gemini_with_agriculture():
    print("🧪 Testing Gemini AI with Agriculture System...")
    
    try:
        # Import Gemini
        import google.generativeai as genai
        print("✅ Gemini SDK imported")
        
        # Configure
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
        print("✅ API key configured")
        
        # Create model
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Model created")
        
        # Import agriculture models
        from core.agriculture_models import AgricultureQuery, Language, AgentResponse
        print("✅ Agriculture models imported")
        
        # Test query
        query = AgricultureQuery(
            query_text="मेरे पास 2 हेक्टेयर खेत है। गेहूं की बुआई के लिए सबसे अच्छी किस्म कौन सी है?",
            query_language=Language.MIXED,
            user_id="test_farmer"
        )
        print("✅ Test query created")
        
        # Generate response
        prompt = f"""
        आप एक भारतीय कृषि विशेषज्ञ हैं।
        
        किसान का सवाल: {query.query_text}
        
        कृपया व्यावहारिक सलाह दें:
        - भारतीय मिट्टी और जलवायु के अनुसार
        - क्षेत्रीय किस्में
        - लागत प्रभावी समाधान
        - बाजार की मांग
        
        संक्षिप्त और स्पष्ट उत्तर दें।
        """
        
        response = model.generate_content(prompt)
        print("✅ Gemini response generated")
        
        # Create structured response
        agent_response = AgentResponse(
            agent_id="gemini_agriculture_agent",
            agent_name="Gemini Agriculture Expert",
            query_id=query.query_id,
            response_text=response.text,
            response_language=Language.MIXED,
            confidence_score=0.90,
            recommendations=[{
                "title": "गेहूं की किस्म सुझाव",
                "description": response.text,
                "priority": "high"
            }],
            timestamp=datetime.now(),
            metadata={"model": "gemini-1.5-flash", "language": "mixed"}
        )
        
        print("\n🎉 SUCCESS! Gemini AI working with agriculture system")
        print(f"Response preview: {response.text[:300]}...")
        print(f"Confidence: {agent_response.confidence_score}")
        print(f"Agent: {agent_response.agent_name}")
        print(f"Language: {agent_response.response_language}")
        print(f"Response length: {len(agent_response.response_text)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_with_agriculture())
    exit(0 if success else 1)
