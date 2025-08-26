"""
Gemini AI-powered agriculture agent using the latest Google GenAI SDK.
Integrates with the Multi-Agent Agriculture Advisory System.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Latest Google GenAI imports
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our agriculture models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.agriculture_models import (
        AgricultureQuery, AgentResponse, QueryDomain, Language, 
        AgricultureCapability, CropType, SoilType, SeasonType
    )
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.agriculture_models import (
        AgricultureQuery, AgentResponse, QueryDomain, Language, 
        AgricultureCapability, CropType, SoilType, SeasonType
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GeminiAgricultureAgent:
    """
    Advanced agriculture agent powered by Google's Gemini 2.5 models.
    Leverages the latest GenAI SDK for enhanced agricultural intelligence.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini agriculture agent"""
        
        # Load API key from environment or parameter
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable, "
                "or pass it as a parameter. Get your API key from: https://aistudio.google.com/apikey"
            )
        
        # Initialize Gemini client with latest SDK
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("✓ Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
        
        # Agent configuration
        self.agent_id = "gemini_agriculture_agent"
        self.agent_name = "Gemini Agriculture Expert"
        self.model_name = "gemini-2.5-flash"  # Latest recommended model
        self.capabilities = [
            AgricultureCapability.CROP_RECOMMENDATION,
            AgricultureCapability.PEST_IDENTIFICATION,
            AgricultureCapability.IRRIGATION_PLANNING,
            AgricultureCapability.YIELD_PREDICTION,
            AgricultureCapability.WEATHER_ANALYSIS,
            AgricultureCapability.MULTILINGUAL_NLP
        ]
        
        # Setup system instructions for agriculture domain
        self.system_instruction = self._create_agriculture_system_prompt()
        
        logger.info(f"✓ Gemini Agriculture Agent initialized with model: {self.model_name}")
    
    def _create_agriculture_system_prompt(self) -> str:
        """Create comprehensive system instructions for structured agricultural analysis"""
        
        return """You are a professional Agricultural Expert Agent providing structured analysis for Indian farmers.

RESPONSE FORMAT REQUIREMENTS:
You must ALWAYS respond in this exact structured format:

## ANALYSIS
[Provide technical analysis of the agricultural situation/query]

## RECOMMENDATIONS
1. [Primary recommendation with specific details]
2. [Secondary recommendation with implementation steps] 
3. [Additional recommendation if relevant]

## AGENT TYPE
[Specify: Crop Selection | Pest Management | Irrigation | Market Analysis | General Agriculture]

## PRIORITY
[Specify: High | Medium | Low]

## ACTION ITEMS
• [Immediate action required]
• [Short-term action (1-7 days)]
• [Long-term action (1-4 weeks)]

AGRICULTURAL EXPERTISE:
- Expert knowledge of Indian agriculture, crops, pests, irrigation, and farming practices
- Consider regional climate, soil conditions, and seasonal factors
- Provide cost-effective, practical solutions suitable for Indian farming conditions
- Include both traditional and modern agricultural techniques
- Focus on yield optimization and sustainable practices

LANGUAGE RULES:
- Respond in the same language as the farmer's question
- If Hindi/Hinglish: Use appropriate agricultural terminology in Hindi
- If English: Use clear, farmer-friendly English
- Always maintain the structured format regardless of language

RESPONSE QUALITY:
- Be specific with quantities, timing, and methods
- Include cost estimates when relevant (in Indian Rupees)
- Mention specific varieties, brands, or techniques when applicable
- Consider local availability of resources and inputs
- Provide weather-dependent advice when relevant

Remember: Always follow the exact format above. Do not add conversational elements or chat-like responses."""

    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """
        Process an agriculture query using Gemini AI
        
        Args:
            query: AgricultureQuery object containing the user's question
            
        Returns:
            AgentResponse with Gemini-generated agricultural advice
        """
        
        try:
            # Prepare the query for Gemini
            enhanced_prompt = self._enhance_query_with_context(query)
            
            # Configure generation parameters
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                max_output_tokens=2000,
                temperature=0.7,  # Balanced creativity and accuracy
                candidate_count=1,
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    ),
                ]
            )
            
            # Generate response using Gemini
            start_time = datetime.now()
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=enhanced_prompt,
                config=config
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Parse and structure the response
            agricultural_response = self._parse_gemini_response(
                response, query, processing_time
            )
            
            logger.info(
                f"✓ Gemini query processed in {processing_time:.2f}s "
                f"with confidence: {agricultural_response.confidence:.2f}"
            )
            
            return agricultural_response
            
        except Exception as e:
            logger.error(f"Error processing query with Gemini: {e}")
            
            # Return error response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text=f"Error processing your agriculture query: {str(e)}",
                confidence_score=0.0,
                recommendations=[],
                metadata={
                    "error": str(e),
                    "model": self.model_name
                }
            )
    
    def _enhance_query_with_context(self, query: AgricultureQuery) -> str:
        """Create a simple, effective prompt that leverages Gemini's native multilingual capabilities"""
        
        # Simple agricultural context prompt that works in any language
        prompt = f"""You are an expert agricultural advisor helping Indian farmers. Please provide practical, actionable advice.

Farmer's Question: {query.query_text}

Please respond in the same language as the question. If the farmer asks in Hindi, respond in Hindi. If they ask in English, respond in English. If they mix languages (Hinglish), you can respond accordingly.

Focus on:
- Practical, implementable solutions
- Indian agricultural context
- Cost-effective methods
- Seasonal considerations (current month: {datetime.now().strftime('%B')})"""

        # Add farm context if available
        if query.farm_profile:
            context_details = []
            if query.farm_profile.farm_size:
                context_details.append(f"Farm size: {query.farm_profile.farm_size} hectares")
            if query.farm_profile.soil_type:
                context_details.append(f"Soil type: {query.farm_profile.soil_type}")
            if query.farm_profile.location:
                context_details.append(f"Location: {query.farm_profile.location}")
            
            if context_details:
                prompt += f"\n\nFarm Context: {', '.join(context_details)}"
        
        # Add location if available
        if query.location:
            prompt += f"\nLocation: {query.location}"
            
        return prompt
        
        if hasattr(query, 'query_domain') and query.query_domain in domain_instructions:
            enhanced_parts.append(f"FOCUS AREA: {domain_instructions[query.query_domain]}")
        
        # Combine all parts
        return "\n\n".join(enhanced_parts)
    
    def _parse_gemini_response(self, gemini_response, query: AgricultureQuery, processing_time: float) -> AgentResponse:
        """Parse Gemini response and convert to structured AgentResponse format"""
        
        try:
            response_text = gemini_response.text
            
            # Parse structured sections from the response
            structured_data = self._parse_structured_response(response_text)
            
            # Extract recommendations from the structured format
            recommendations = self._extract_structured_recommendations(structured_data)
            
            # Calculate confidence based on response quality and structure
            confidence = self._calculate_confidence(gemini_response, response_text, structured_data)
            
            # Extract metadata including structured sections
            metadata = {
                "model": self.model_name,
                "processing_time": processing_time,
                "response_length": len(response_text),
                "recommendations_count": len(recommendations),
                "structured_format": True,
                "analysis_section": structured_data.get("analysis", ""),
                "agent_type": structured_data.get("agent_type", "General Agriculture"),
                "priority": structured_data.get("priority", "Medium"),
                "action_items": structured_data.get("action_items", [])
            }
            
            # Add safety ratings if available
            if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    metadata["safety_ratings"] = {
                        rating.category: rating.probability for rating in candidate.safety_ratings
                    }
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text=response_text,
                confidence_score=confidence,
                recommendations=recommendations,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text="Error parsing the AI response",
                confidence_score=0.0,
                recommendations=[],
                metadata={"error": str(e)}
            )
    
    def _parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the structured response format into components"""
        
        structured_data = {
            "analysis": "",
            "recommendations": [],
            "agent_type": "General Agriculture",
            "priority": "Medium",
            "action_items": []
        }
        
        if not response_text:
            return structured_data
        
        # Split into sections based on markdown headers
        sections = response_text.split('##')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split('\n')
            header = lines[0].strip().upper()
            content_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            if 'ANALYSIS' in header:
                structured_data["analysis"] = '\n'.join(content_lines)
            
            elif 'RECOMMENDATIONS' in header:
                for line in content_lines:
                    if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                        structured_data["recommendations"].append(line[2:].strip())
            
            elif 'AGENT TYPE' in header:
                if content_lines:
                    structured_data["agent_type"] = content_lines[0]
            
            elif 'PRIORITY' in header:
                if content_lines:
                    structured_data["priority"] = content_lines[0]
            
            elif 'ACTION ITEMS' in header:
                for line in content_lines:
                    if line.startswith('•'):
                        structured_data["action_items"].append(line[1:].strip())
        
        return structured_data
    
    def _extract_structured_recommendations(self, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract recommendations from structured data"""
        
        recommendations = []
        
        # Process recommendations from the structured format
        for i, rec_text in enumerate(structured_data.get("recommendations", []), 1):
            recommendations.append({
                "id": f"rec_{i}",
                "text": rec_text,
                "type": "structured_recommendation",
                "priority": structured_data.get("priority", "Medium").lower(),
                "category": structured_data.get("agent_type", "General Agriculture")
            })
        
        # Add action items as additional recommendations
        for i, action in enumerate(structured_data.get("action_items", []), len(recommendations) + 1):
            recommendations.append({
                "id": f"action_{i}",
                "text": action,
                "type": "action_item", 
                "priority": "high" if "immediate" in action.lower() else "medium",
                "category": "Implementation"
            })
        
        return recommendations
    
    def _extract_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from Gemini response"""
        
        recommendations = []
        
        # Common recommendation indicators
        recommendation_markers = [
            "recommended", "suggest", "advice", "should", "consider",
            "सुझाव", "सिफारिश", "करना चाहिए", "उपयोग करें"
        ]
        
        # Split response into sentences
        sentences = response_text.replace('\n', ' ').split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short sentences
                # Check if sentence contains recommendation indicators
                if any(marker.lower() in sentence.lower() for marker in recommendation_markers):
                    recommendations.append({
                        "id": f"rec_{i+1}",
                        "text": sentence,
                        "type": "suggestion",
                        "priority": "medium"
                    })
                
                # Check for numbered/bulleted recommendations
                if sentence.startswith(('1.', '2.', '3.', '•', '-', '*')):
                    clean_rec = sentence.lstrip('123456789.-•* ')
                    if len(clean_rec) > 15:
                        recommendations.append({
                            "id": f"rec_{i+1}",
                            "text": clean_rec,
                            "type": "action_item",
                            "priority": "high"
                        })
        
        # Limit to top 10 recommendations to avoid overwhelming
        return recommendations[:10]
    
    def _calculate_confidence(self, gemini_response, response_text: str, structured_data: Dict[str, Any] = None) -> float:
        """Calculate confidence score based on response quality and structure indicators"""
        
        confidence = 0.5  # Base confidence
        
        # Check if response follows structured format (major confidence boost)
        if structured_data:
            # Boost confidence for having structured sections
            if structured_data.get("analysis"):
                confidence += 0.15
            if structured_data.get("recommendations"):
                confidence += 0.15
            if structured_data.get("agent_type"):
                confidence += 0.05
            if structured_data.get("priority"):
                confidence += 0.05
            if structured_data.get("action_items"):
                confidence += 0.10
        
        # Response length indicates detail (longer = higher confidence)
        if len(response_text) > 200:
            confidence += 0.1
        if len(response_text) > 500:
            confidence += 0.05
        
        # Check for specific agricultural terms (indicates domain relevance)
        agricultural_terms = [
            'crop', 'soil', 'fertilizer', 'irrigation', 'pest', 'disease',
            'variety', 'yield', 'harvest', 'sowing', 'farming', 'seed',
            'फसल', 'मिट्टी', 'खाद', 'सिंचाई', 'कीट', 'रोग', 'बीज'
        ]
        
        term_count = sum(1 for term in agricultural_terms if term.lower() in response_text.lower())
        confidence += min(term_count * 0.01, 0.1)  # Max 0.1 boost from terms
        
        # Check for specific recommendations (actionable advice)
        if "recommend" in response_text.lower() or "सुझाव" in response_text:
            confidence += 0.05
        
        # Check for quantitative information (specific measurements, costs, etc.)
        import re
        numbers_pattern = r'\d+(?:\.\d+)?(?:\s*(?:kg|gram|liter|rupee|₹|acre|hectare))'
        if re.search(numbers_pattern, response_text, re.IGNORECASE):
            confidence += 0.05
        
        # Check if response was blocked by safety filters
        if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
            candidate = gemini_response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                if candidate.finish_reason == "SAFETY":
                    confidence -= 0.3
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    async def process_multimodal_query(self, query: AgricultureQuery, image_path: Optional[str] = None) -> AgentResponse:
        """
        Process a query with optional image input (for crop/pest identification)
        
        Args:
            query: AgricultureQuery object
            image_path: Optional path to image file
            
        Returns:
            AgentResponse with multimodal analysis
        """
        
        try:
            # Prepare content list
            contents = []
            
            # Add text query
            enhanced_prompt = self._enhance_query_with_context(query)
            contents.append(enhanced_prompt)
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                from PIL import Image
                image = Image.open(image_path)
                contents.append(image)
                contents.append("Please analyze this image in the context of the agricultural question above.")
            
            # Configure generation
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                max_output_tokens=2500,  # More tokens for image analysis
                temperature=0.6,
            )
            
            # Generate response
            start_time = datetime.now()
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Parse response
            agricultural_response = self._parse_gemini_response(
                response, query, processing_time
            )
            
            # Add multimodal metadata
            agricultural_response.metadata["multimodal"] = True
            if image_path:
                agricultural_response.metadata["image_analyzed"] = True
                agricultural_response.metadata["image_path"] = image_path
            
            logger.info(f"✓ Multimodal query processed in {processing_time:.2f}s")
            
            return agricultural_response
            
        except Exception as e:
            logger.error(f"Error in multimodal processing: {e}")
            return await self.process_query(query)  # Fallback to text-only
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        
        return {
            "agent_id": self.agent_id,
            "model": self.model_name,
            "capabilities": [cap.value for cap in self.capabilities],
            "supported_languages": ["English", "Hindi", "Mixed (Hinglish)"],
            "multimodal_support": True,
            "api_provider": "Google Gemini",
            "sdk_version": "google-genai 1.29.0+",
            "specialization": "Indian Agriculture Advisory"
        }
    
    async def process_query_async(self, query: AgricultureQuery) -> AgentResponse:
        """
        Async wrapper for process_query method
        """
        # For now, call the synchronous method
        # In a full implementation, this would use proper async Gemini calls
        return await asyncio.create_task(
            asyncio.to_thread(self.process_query, query)
        )


async def test_gemini_agent():
    """Test function for the Gemini Agriculture Agent"""
    
    print("🌾 Testing Gemini Agriculture Agent...")
    
    try:
        # Initialize agent (will fail gracefully if no API key)
        agent = GeminiAgricultureAgent()
        
        # Test queries
        test_queries = [
            {
                "text": "What wheat variety is best for Punjab soil in Rabi season?",
                "lang": Language.ENGLISH,
                "description": "Crop recommendation query"
            },
            {
                "text": "मेरे गेहूं की फसल पर पीले धब्बे हैं, क्या करूं?",
                "lang": Language.HINDI,
                "description": "Pest management query in Hindi"
            },
            {
                "text": "Cotton की crop में कितना पानी लगता है per acre?",
                "lang": Language.MIXED,
                "description": "Irrigation query in Hinglish"
            }
        ]
        
        print(f"Agent Info: {agent.get_agent_info()}")
        print("\n" + "="*60)
        
        for i, test in enumerate(test_queries, 1):
            print(f"\nTest {i}: {test['description']}")
            print(f"Query: {test['text']}")
            
            # Create query object
            query = AgricultureQuery(
                query_text=test['text'],
                query_language=test['lang'],
                user_id=f"test_user_{i}"
            )
            
            # Process query
            response = await agent.process_query(query)
            
            # Display results
            print(f"Status: {response.status}")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Processing Time: {response.processing_time:.2f}s")
            print(f"Response Length: {len(response.response_text)} chars")
            print(f"Recommendations: {len(response.recommendations)}")
            
            if response.status == "completed":
                print("✓ Query processed successfully")
                # Show first 200 chars of response
                preview = response.response_text[:200] + "..." if len(response.response_text) > 200 else response.response_text
                print(f"Response Preview: {preview}")
            else:
                print(f"✗ Query failed: {response.response_text}")
            
            print("-" * 40)
        
        print("\n🎉 Gemini Agriculture Agent testing completed!")
        return True
        
    except ValueError as e:
        if "API key not found" in str(e):
            print("⚠️  Gemini API key not configured.")
            print("To use Gemini agent, set your API key:")
            print("1. Get API key from: https://aistudio.google.com/apikey")
            print("2. Set environment variable: GOOGLE_API_KEY=your_api_key")
            print("3. Or create .env file with: GOOGLE_API_KEY=your_api_key")
            return False
        else:
            print(f"✗ Error: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_gemini_agent())
