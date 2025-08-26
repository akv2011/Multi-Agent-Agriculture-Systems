"""
Ground Search Service using Gemini API for the Multi-Agent Agriculture System
Provides enhanced search capabilities with Google's Gemini AI model to enrich agent responses
with grounded, up-to-date information from reliable sources.
"""

import logging
import os
import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

import google.generativeai as genai
from ..services.google_search_service import GoogleSearchService, SearchResult, create_google_search_service

logger = logging.getLogger(__name__)

@dataclass
class GroundedInfo:
    """Structured grounded information result"""
    content: str  # The grounded response content
    sources: List[Dict[str, str]]  # List of sources used
    query: str  # Original query
    confidence_score: float = 0.0  # Model's confidence in the answer
    timestamp: datetime = None  # When this grounded info was generated

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class GroundSearchService:
    """Service for performing grounded searches using Gemini API combined with Google Search"""
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None, 
                 google_search_api_key: Optional[str] = None,
                 google_search_cx: Optional[str] = None,
                 model_name: str = "gemini-1.5-flash"):
        """Initialize the Ground Search service with Gemini and Google Search API"""
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not self.gemini_api_key:
            logger.warning("Gemini API key not provided. Ground search will not work.")
        else:
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini model {model_name} initialized")
        
        # Initialize Google Search service
        self.search_service = create_google_search_service(
            api_key=google_search_api_key, 
            cx=google_search_cx
        )
        
        # Cache for grounded responses
        self.cache = {}
        self.cache_ttl = timedelta(hours=6)  # Cache results for 6 hours
    
    async def ground_query(self, 
                          query: str,
                          context: Optional[Dict[str, Any]] = None,
                          num_search_results: int = 5,
                          language: str = "en",
                          country: str = "in") -> GroundedInfo:
        """
        Perform a grounded search combining web search results with Gemini AI
        
        Args:
            query: User query to ground
            context: Additional context dictionary (location, crop type, etc.)
            num_search_results: Number of search results to use for grounding
            language: Search language (default: English)
            country: Country context (default: India)
            
        Returns:
            GroundedInfo object with grounded response and sources
        """
        # Check cache first
        cache_key = f"{query}:{language}:{country}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() - cache_entry["timestamp"] < self.cache_ttl:
                logger.info(f"Returning cached grounded results for query: {query}")
                return cache_entry["result"]
        
        if not self.gemini_api_key:
            logger.error("Cannot perform grounded search: Gemini API key not provided")
            return GroundedInfo(
                content="Grounding service unavailable. Please check API configuration.",
                sources=[],
                query=query,
                confidence_score=0.0
            )
        
        try:
            # Step 1: Get search results
            search_results = await self.search_service.search(
                query=query,
                num_results=num_search_results,
                language=language,
                country=country
            )
            
            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                # Fallback: Use Gemini without search results for grounding
                return await self._fallback_gemini_response(query, context)
            
            # Step 2: Construct context from search results
            search_context = self._format_search_results(search_results)
            
            # Step 3: Construct prompt with search results and context
            prompt = self._build_grounding_prompt(query, search_context, context)
            
            # Step 4: Get response from Gemini
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Step 5: Parse and structure the response
            grounded_info = self._parse_gemini_response(
                response.text, query, search_results
            )
            
            # Cache the result
            self.cache[cache_key] = {
                "timestamp": datetime.now(),
                "result": grounded_info
            }
            
            return grounded_info
            
        except Exception as e:
            logger.error(f"Error performing grounded search: {e}", exc_info=True)
            return GroundedInfo(
                content=f"Error in grounded search: {str(e)}",
                sources=[],
                query=query,
                confidence_score=0.0
            )
    
    def _format_search_results(self, search_results: List[SearchResult]) -> str:
        """Format search results for inclusion in the prompt"""
        if not search_results:
            return "No search results available."
        
        formatted_results = "SEARCH RESULTS:\n\n"
        
        for i, result in enumerate(search_results, 1):
            formatted_results += f"[Source {i}] {result.title}\n"
            formatted_results += f"URL: {result.link}\n"
            formatted_results += f"From: {result.source}\n"
            formatted_results += f"{result.snippet}\n\n"
        
        return formatted_results
    
    def _build_grounding_prompt(self, 
                               query: str, 
                               search_context: str, 
                               additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Build a prompt for the Gemini model with search results and context"""
        
        context_str = ""
        if additional_context:
            context_str = "Additional context:\n"
            for key, value in additional_context.items():
                if value:
                    context_str += f"- {key}: {value}\n"
        
        prompt = f"""You are an expert agricultural advisor for Indian farmers with access to recent information.
        
USER QUERY: {query}

{context_str}

{search_context}

Based on the search results above and your knowledge, provide a comprehensive, accurate, and helpful answer to the user's query.
Focus on being factual and informative rather than general. Favor information from credible agricultural sources.
Cite specific information from the search results by referring to the source numbers.

Your response should have two parts:
1. RESPONSE: A clear, well-structured answer to the user's query that synthesizes the information from the sources.
2. SOURCES: A numbered list of the most relevant sources you used, with brief notes on what information each source provided.

Make sure your answer is specific to Indian agriculture contexts when applicable. Include specific details like crop varieties, techniques, or policies that are relevant.
"""
        
        return prompt
    
    def _parse_gemini_response(self, 
                              response_text: str, 
                              original_query: str,
                              search_results: List[SearchResult]) -> GroundedInfo:
        """Parse the Gemini response into structured GroundedInfo"""
        
        # Extract response and sources sections
        parts = response_text.split("SOURCES:", 1)
        
        if len(parts) == 2:
            content = parts[0].replace("RESPONSE:", "").strip()
            sources_text = parts[1].strip()
        else:
            content = response_text.strip()
            sources_text = ""
        
        # Extract sources
        sources = []
        
        # Try to extract numbered sources
        source_pattern = r'\[?(\d+)\]?[.:]? *(.*?)(?=\n\[?\d+\]?|$)'
        source_matches = re.findall(source_pattern, sources_text, re.DOTALL)
        
        if source_matches:
            for idx, text in source_matches:
                source_num = int(idx) - 1
                if 0 <= source_num < len(search_results):
                    sources.append({
                        "title": search_results[source_num].title,
                        "link": search_results[source_num].link,
                        "source": search_results[source_num].source,
                        "note": text.strip()
                    })
        else:
            # Fallback to just including all search results
            for result in search_results:
                sources.append({
                    "title": result.title,
                    "link": result.link,
                    "source": result.source
                })
        
        return GroundedInfo(
            content=content,
            sources=sources,
            query=original_query,
            confidence_score=0.9 if sources else 0.7
        )
    
    async def _fallback_gemini_response(self, 
                                       query: str, 
                                       context: Optional[Dict[str, Any]] = None) -> GroundedInfo:
        """
        Fallback method when Google Search is not available.
        Uses Gemini directly with enhanced agricultural context.
        """
        logger.info("Using Gemini fallback mode (no search results)")
        
        context_str = ""
        if context:
            context_str = "Context:\n"
            for key, value in context.items():
                if value:
                    context_str += f"- {key}: {value}\n"
        
        fallback_prompt = f"""You are an expert agricultural advisor for Indian farmers with comprehensive knowledge of:
- Current agricultural policies, MSP rates, and government schemes
- Crop cultivation practices across different Indian states
- Plant disease identification and treatment methods
- Agricultural finance, loans, and subsidies
- Market trends, pricing, and best practices

{context_str}

Farmer's Question: {query}

Please provide a detailed, accurate response that includes:
1. Direct answer to the question with specific details
2. Current information (acknowledge if information might be outdated)
3. Regional considerations for Indian agriculture
4. Practical, actionable recommendations
5. Relevant government schemes or policies
6. Best practices and expert advice

Be as specific and factual as possible. If you mention prices, dates, or policies, 
indicate the timeframe and suggest verifying current information from official sources.
"""
        
        try:
            # Generate response using Gemini
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            response = self.model.generate_content(
                fallback_prompt,
                generation_config=generation_config
            )
            
            # Create grounded info with no external sources
            grounded_info = GroundedInfo(
                content=response.text,
                sources=[{
                    "title": "Gemini AI Agricultural Knowledge",
                    "link": "https://ai.google.dev/",
                    "source": "ai.google.dev",
                    "note": "Response generated using Gemini AI's agricultural knowledge base"
                }],
                query=query,
                confidence_score=0.7  # Lower confidence since no external sources
            )
            
            return grounded_info
            
        except Exception as e:
            logger.error(f"Error in Gemini fallback: {e}")
            return GroundedInfo(
                content=f"Unable to generate response: {str(e)}",
                sources=[],
                query=query,
                confidence_score=0.0
            )
    
    def clear_cache(self):
        """Clear the ground search cache"""
        self.cache = {}
        logger.info("Ground search cache cleared")


# Factory function to create the ground search service
def create_ground_search_service(
    gemini_api_key: Optional[str] = None,
    google_search_api_key: Optional[str] = None,
    google_search_cx: Optional[str] = None
) -> GroundSearchService:
    """Create and return a GroundSearchService instance"""
    return GroundSearchService(
        gemini_api_key=gemini_api_key,
        google_search_api_key=google_search_api_key,
        google_search_cx=google_search_cx
    )


# Example usage
async def example_ground_search():
    service = create_ground_search_service()
    
    test_queries = [
        "What is the current wheat MSP in India?",
        "Best practices for rice cultivation in Punjab",
        "Latest government schemes for organic farming"
    ]
    
    for query in test_queries:
        print(f"\n\n=== Testing grounded search for: {query} ===\n")
        
        result = await service.ground_query(
            query=query,
            context={"location": "Punjab, India", "crop_type": "wheat"}
        )
        
        print(f"🌾 Grounded Response:")
        print(f"{result.content}\n")
        
        print(f"📚 Sources Used:")
        for i, source in enumerate(result.sources, 1):
            print(f"{i}. {source.get('title', 'Unknown')}")
            print(f"   Link: {source.get('link', 'N/A')}")
            if source.get('note'):
                print(f"   Note: {source.get('note')}")
            print()


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example ground search
    asyncio.run(example_ground_search())
