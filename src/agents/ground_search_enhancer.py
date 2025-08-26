"""
Ground Search Enhancement for Agricultural Agents
This module provides a mixin class to enhance any agricultural agent with ground search capabilities.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..core.agriculture_models import (
    AgricultureQuery, AgentResponse, QueryDomain,
    Location, CropType, SoilType
)
from ..services.ground_search_service import (
    GroundSearchService, create_ground_search_service, GroundedInfo
)

logger = logging.getLogger(__name__)


class GroundSearchEnhancer:
    """
    A mixin class to enhance agents with ground search capabilities.
    This can be added to any agent to provide grounding with Gemini and Google Search.
    """
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None,
                 google_search_api_key: Optional[str] = None,
                 google_search_cx: Optional[str] = None,
                 enable_grounding: bool = True):
        """Initialize the ground search enhancer"""
        self.enable_grounding = enable_grounding
        
        if self.enable_grounding:
            self.ground_search_service = create_ground_search_service(
                gemini_api_key=gemini_api_key,
                google_search_api_key=google_search_api_key,
                google_search_cx=google_search_cx
            )
            logger.info("Ground search enhancer initialized")
        else:
            self.ground_search_service = None
            logger.info("Ground search enhancer disabled")
    
    async def ground_query(self, query: AgricultureQuery) -> Optional[GroundedInfo]:
        """
        Ground a query using external sources
        
        Args:
            query: The agriculture query to ground
            
        Returns:
            GroundedInfo if successful, None otherwise
        """
        if not self.enable_grounding or not self.ground_search_service:
            logger.info("Grounding skipped - service disabled")
            return None
        
        try:
            # Extract context from query
            context = self._extract_context_from_query(query)
            
            # Determine the query domain for better search context
            domain_context = self._get_domain_specific_context(query.query_domain)
            if domain_context:
                context.update(domain_context)
            
            # Enhance the query for better search results
            enhanced_query = self._enhance_query_for_search(
                query.query_text, query.query_domain
            )
            
            # Perform the grounded search
            grounded_info = await self.ground_search_service.ground_query(
                query=enhanced_query,
                context=context,
                language=query.query_language.value.lower() if query.query_language else "en",
                country="in"  # Default to India
            )
            
            logger.info(f"Query grounded successfully with {len(grounded_info.sources)} sources")
            return grounded_info
            
        except Exception as e:
            logger.error(f"Error during query grounding: {e}", exc_info=True)
            return None
    
    def _extract_context_from_query(self, query: AgricultureQuery) -> Dict[str, Any]:
        """Extract relevant context from the query for better grounding"""
        context = {}
        
        # Add location information
        if query.location:
            location_str = []
            if query.location.state:
                location_str.append(query.location.state)
            if query.location.district:
                location_str.append(query.location.district)
            if query.location.village:
                location_str.append(query.location.village)
            
            if location_str:
                context["location"] = ", ".join(location_str)
            
            # Add coordinates if available
            if query.location.latitude and query.location.longitude:
                context["coordinates"] = f"{query.location.latitude}, {query.location.longitude}"
        
        # Add soil information
        if query.soil_type:
            context["soil_type"] = query.soil_type.value
        
        # Add crop information
        if query.crop_type:
            context["crop"] = query.crop_type.value
        
        # Add farm information
        if query.farm_profile:
            if query.farm_profile.farm_size:
                context["farm_size"] = f"{query.farm_profile.farm_size} acres"
            if query.farm_profile.farming_method:
                context["farming_method"] = query.farm_profile.farming_method
            
        return context
    
    def _get_domain_specific_context(self, domain: Optional[str]) -> Dict[str, str]:
        """Get domain-specific context to improve search results"""
        context = {}
        
        if not domain:
            return context
        
        domain_mappings = {
            QueryDomain.CROP_SELECTION: "crop varieties cultivation India",
            QueryDomain.PEST_MANAGEMENT: "pest management agricultural diseases India",
            QueryDomain.IRRIGATION: "irrigation methods water management agriculture India",
            QueryDomain.FINANCE_POLICY: "agricultural finance policy subsidy India",
            QueryDomain.MARKET_TIMING: "agricultural commodity markets prices India",
            QueryDomain.HARVEST_PLANNING: "harvest management techniques agriculture India",
            QueryDomain.DISEASE_IDENTIFICATION: "plant disease identification agriculture India"
        }
        
        if domain in domain_mappings:
            context["domain"] = domain_mappings[domain]
        
        return context
    
    def _enhance_query_for_search(self, query_text: str, query_domain: Optional[str]) -> str:
        """Enhance the query for better search results based on domain"""
        enhanced_query = query_text
        
        # Add India context if not present
        if "india" not in query_text.lower():
            enhanced_query += " India"
        
        # Add agriculture context if not present
        if not any(term in query_text.lower() for term in ["agriculture", "farming", "crop", "farm"]):
            enhanced_query += " agriculture"
        
        # Add domain-specific keywords for better results
        if query_domain == QueryDomain.FINANCE_POLICY:
            if not any(term in query_text.lower() for term in ["msp", "subsidy", "loan", "policy"]):
                enhanced_query += " agricultural policy"
                
        elif query_domain == QueryDomain.MARKET_TIMING:
            if not any(term in query_text.lower() for term in ["price", "market", "sell", "buy"]):
                enhanced_query += " market prices"
                
        elif query_domain == QueryDomain.DISEASE_IDENTIFICATION:
            if not any(term in query_text.lower() for term in ["disease", "symptom", "infection"]):
                enhanced_query += " plant disease symptoms"
        
        return enhanced_query
    
    def enhance_response_with_grounding(self, 
                                       response: AgentResponse, 
                                       grounded_info: GroundedInfo) -> AgentResponse:
        """
        Enhance an agent response with grounded information
        
        Args:
            response: Original agent response
            grounded_info: Grounded information to incorporate
            
        Returns:
            Enhanced agent response
        """
        if not grounded_info:
            return response
        
        # Create a marker to show where grounded information begins
        grounding_marker = "\n\n---\n📚 Additional Information from External Sources:\n\n"
        
        # Combine original response with grounded content
        enhanced_text = response.response_text
        
        # Only append grounded info if it's substantively different from the original response
        if self._is_substantially_different(enhanced_text, grounded_info.content):
            enhanced_text += grounding_marker + grounded_info.content
            
            # Add sources at the end
            if grounded_info.sources:
                enhanced_text += "\n\nSources:\n"
                for i, source in enumerate(grounded_info.sources[:3], 1):  # Limit to top 3 sources
                    enhanced_text += f"{i}. {source.get('title', 'Unknown Source')}"
                    if source.get('link'):
                        enhanced_text += f" - {source.get('link')}"
                    enhanced_text += "\n"
        
        # Update response with enhanced content
        response.response_text = enhanced_text
        
        # Add grounding metadata
        response.metadata = response.metadata or {}
        response.metadata["grounded"] = True
        response.metadata["num_sources"] = len(grounded_info.sources)
        response.metadata["grounding_confidence"] = grounded_info.confidence_score
        
        # Potentially increase confidence score if grounding was successful
        if grounded_info.confidence_score > 0.7 and response.confidence_score < 0.9:
            response.confidence_score = min(0.9, response.confidence_score + 0.1)
        
        return response
    
    def _is_substantially_different(self, original_text: str, new_text: str) -> bool:
        """
        Check if the new text provides substantial new information compared to original text
        Uses simple heuristics to avoid redundancy
        """
        # If original text is very short, always add grounding
        if len(original_text) < 100:
            return True
            
        # If new text is very short, don't add it
        if len(new_text) < 50:
            return False
            
        # Compare lengths - if grounding is much longer, likely has new info
        if len(new_text) > len(original_text) * 1.5:
            return True
            
        # Check for significant new content by checking sentences in new text
        # that don't appear in original
        
        # Simple approach: count sentences in new text that aren't in original
        original_sentences = set([s.strip() for s in original_text.split('.') if len(s.strip()) > 20])
        new_sentences = set([s.strip() for s in new_text.split('.') if len(s.strip()) > 20])
        
        # If at least 30% of sentences in new text aren't in original, consider it substantial
        if len(new_sentences) == 0:
            return False
            
        unique_ratio = len(new_sentences - original_sentences) / len(new_sentences)
        return unique_ratio > 0.3


# Example showing how to integrate this enhancer with an agent
"""
class MyAgent(BaseWorkerAgent, GroundSearchEnhancer):
    def __init__(self, agent_id, name, gemini_api_key=None):
        BaseWorkerAgent.__init__(self, agent_id=agent_id, name=name)
        GroundSearchEnhancer.__init__(
            self, 
            gemini_api_key=gemini_api_key,
            enable_grounding=True
        )
    
    async def process_query(self, query):
        # Generate initial response
        response = self.generate_basic_response(query)
        
        # Ground the query using external sources
        grounded_info = await self.ground_query(query)
        
        if grounded_info:
            # Enhance response with grounded information
            response = self.enhance_response_with_grounding(response, grounded_info)
        
        return response
"""
