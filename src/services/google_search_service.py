"""
Google Search Service for the Multi-Agent Agriculture System
Provides fallback search capabilities for queries that can't be answered by the AgriMitr models
"""

import logging
import os
import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    snippet: str
    link: str
    source: str
    relevance_score: float = 0.0
    date: Optional[str] = None


class GoogleSearchService:
    """Service for performing Google searches with result filtering and caching"""
    
    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        """Initialize the Google Search service"""
        self.api_key = api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cx = cx or os.getenv("GOOGLE_SEARCH_CX")
        
        if not self.api_key or not self.cx:
            logger.warning("Google Search API key or CX ID not provided. Google Search will not work.")
        
        self.search_url = "https://www.googleapis.com/customsearch/v1"
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)  # Cache results for 24 hours
    
    async def search(
        self, 
        query: str, 
        num_results: int = 5, 
        language: str = "en", 
        country: str = "in",
        filter_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Perform a Google search and return structured results
        
        Args:
            query: Search query string
            num_results: Number of results to return
            language: Search language (default: English)
            country: Country context (default: India)
            filter_domains: Optional list of domains to prioritize (e.g. ["gov.in", "icar.org.in"])
            
        Returns:
            List of SearchResult objects
        """
        # Check cache first
        cache_key = f"{query}:{language}:{country}:{num_results}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() - cache_entry["timestamp"] < self.cache_ttl:
                logger.info(f"Returning cached search results for query: {query}")
                return cache_entry["results"]
        
        if not self.api_key or not self.cx:
            logger.error("Cannot perform search: Google Search API key or CX ID not provided")
            return []
        
        try:
            # Prepare search parameters
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(num_results * 2, 10),  # Request more to filter later
                "hl": language,
                "gl": country,
                "safe": "active"
            }
            
            # Add agricultural context to improve results
            if "farm" not in query.lower() and "agriculture" not in query.lower():
                if re.search(r"(?i)\b(price|cost|market|finance|loan|subsidy|money)\b", query):
                    params["q"] += " agriculture finance India"
                else:
                    params["q"] += " agriculture farming"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Google Search API error: {response.status}")
                        return []
                    
                    search_data = await response.json()
                    
            # Process and filter results
            results = self._process_search_results(search_data, filter_domains)
            
            # Limit to requested number
            results = results[:num_results]
            
            # Cache the results
            self.cache[cache_key] = {
                "timestamp": datetime.now(),
                "results": results
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing Google search: {e}")
            return []
    
    def _process_search_results(self, search_data: Dict[str, Any], filter_domains: Optional[List[str]] = None) -> List[SearchResult]:
        """Process and filter raw Google search results"""
        results = []
        
        if "items" not in search_data:
            logger.warning("No search results found")
            return results
        
        for item in search_data["items"]:
            # Extract relevant fields
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            
            # Extract source domain
            source = link.split("//")[-1].split("/")[0]
            
            # Calculate relevance score (simple heuristic)
            relevance_score = 0.5  # Base score
            
            # Boost government and educational sites
            if source.endswith((".gov.in", ".nic.in", ".edu", ".ac.in")):
                relevance_score += 0.3
            
            # Boost agricultural domains
            if any(ag_term in source for ag_term in ["agri", "farm", "krishi"]):
                relevance_score += 0.2
            
            # Boost priority domains if provided
            if filter_domains and any(domain in source for domain in filter_domains):
                relevance_score += 0.4
            
            # Create structured result
            result = SearchResult(
                title=title,
                snippet=snippet,
                link=link,
                source=source,
                relevance_score=min(relevance_score, 1.0)
            )
            
            results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results
    
    def clear_cache(self):
        """Clear the search cache"""
        self.cache = {}
        logger.info("Search cache cleared")


# Factory function to create the search service
def create_google_search_service(api_key: Optional[str] = None, cx: Optional[str] = None) -> GoogleSearchService:
    """Create and return a GoogleSearchService instance"""
    return GoogleSearchService(api_key=api_key, cx=cx)


# Example usage
async def example_search():
    service = create_google_search_service()
    results = await service.search("current wheat MSP price India")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title}")
        print(f"   {result.snippet}")
        print(f"   Source: {result.source}, Relevance: {result.relevance_score:.2f}")
        print(f"   {result.link}\n")


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Run example search
    asyncio.run(example_search())
