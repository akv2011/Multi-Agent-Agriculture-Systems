"""
Multi-Agent Router for Agricultural Advisory System.
This router analyzes user queries and routes them to appropriate specialist agents.
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from langchain_core.tools import tool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..agents.base_agent import BaseWorkerAgent
from ..core.agriculture_models import (
    AgricultureQuery, QueryDomain, Language, RoutingDecision, 
    AgricultureCapability, AgricultureTask, Location, FarmProfile
)
from ..core.models import Task, TaskPriority, TaskStatus


logger = logging.getLogger(__name__)


class AgricultureRouter(BaseWorkerAgent):
    """
    Central router that analyzes agricultural queries and routes them to specialist agents.
    Uses LLM for intelligent query classification and agent selection.
    """
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        super().__init__(
            name="Agriculture Router",
            capabilities=[
                AgricultureCapability.QUERY_ROUTING,
                AgricultureCapability.MULTILINGUAL_NLP
            ],
            agent_type="router"
        )
        
        # Initialize LLM (default to Gemini for cost-effectiveness)
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.1,
            max_tokens=2048
        )
        
        # Agent registry mapping
        self.agent_registry: Dict[str, List[str]] = {
            QueryDomain.CROP_SELECTION: ["crop_selection_agent"],
            QueryDomain.PEST_MANAGEMENT: ["pest_forecaster_agent"],
            QueryDomain.IRRIGATION: ["irrigation_scheduler_agent"],
            QueryDomain.FINANCE_POLICY: ["finance_policy_agent"],
            QueryDomain.MARKET_TIMING: ["market_timing_agent"],
            QueryDomain.HARVEST_PLANNING: ["harvest_planning_agent"],
            QueryDomain.INPUT_MATERIALS: ["input_materials_agent"]
        }
        
        # Query classification patterns (Hindi/English)
        self.domain_patterns = {
            QueryDomain.CROP_SELECTION: [
                # English patterns
                r"(?i)\b(crop|seed|variety|plant|sow|grow|cultivation|fasal|boya)\b",
                r"(?i)\b(which crop|what to grow|recommend|suggest)\b",
                # Hindi patterns (Devanagari and Roman)
                r"(?i)\b(fasal|beej|ugana|bojana|kheti|kya|kaun|sa)\b",
                r"कौन सी फसल|क्या उगाएं|फसल की सिफारिश"
            ],
            QueryDomain.PEST_MANAGEMENT: [
                # English patterns
                r"(?i)\b(pest|insect|bug|disease|fungus|keet|keeda|bimari)\b",
                r"(?i)\b(spray|pesticide|treatment|medicine|dawai)\b",
                # Hindi patterns
                r"(?i)\b(keet|keeda|bimari|rog|spray|dawai|upchar)\b",
                r"कीट|कीड़े|बीमारी|रोग|स्प्रे|दवाई"
            ],
            QueryDomain.IRRIGATION: [
                # English patterns
                r"(?i)\b(water|irrigation|watering|sinchana|pani)\b",
                r"(?i)\b(when to water|how much water|schedule)\b",
                # Hindi patterns
                r"(?i)\b(pani|sinchana|sinchai|kab|kitna)\b",
                r"पानी|सिंचाई|कब पानी|कितना पानी"
            ],
            QueryDomain.FINANCE_POLICY: [
                # English patterns
                r"(?i)\b(loan|credit|subsidy|insurance|scheme|yojana|paisa)\b",
                r"(?i)\b(bank|finance|money|cost|price|kharcha)\b",
                # Hindi patterns
                r"(?i)\b(karza|rin|subsidy|bima|yojana|paisa|kharcha)\b",
                r"ऋण|कर्ज़|सब्सिडी|बीमा|योजना|पैसा"
            ],
            QueryDomain.MARKET_TIMING: [
                # English patterns
                r"(?i)\b(sell|market|price|mandi|rate|bechana)\b",
                r"(?i)\b(when to sell|market price|best time)\b",
                # Hindi patterns
                r"(?i)\b(bechana|mandi|bhav|rate|kab|bechna)\b",
                r"बेचना|मंडी|भाव|रेट|कब बेचें"
            ],
            QueryDomain.HARVEST_PLANNING: [
                # English patterns
                r"(?i)\b(harvest|cut|katana|ready|mature|pakana)\b",
                r"(?i)\b(when to harvest|cutting time|maturity)\b",
                # Hindi patterns
                r"(?i)\b(katana|katat|fasal|pakana|taiyar|kab)\b",
                r"कटाई|काटना|फसल|पकना|तैयार|कब काटें"
            ],
            QueryDomain.INPUT_MATERIALS: [
                # English patterns
                r"(?i)\b(fertilizer|manure|khad|seed|beej|urvarak)\b",
                r"(?i)\b(NPK|DAP|urea|compost|organic)\b",
                # Hindi patterns
                r"(?i)\b(khad|urvarak|beej|khad|gobar)\b",
                r"खाद|उर्वरक|बीज|गोबर|कंपोस्ट"
            ]
        }
        
        # Language detection patterns
        self.hindi_patterns = [
            r"[\u0900-\u097F]",  # Devanagari script
            r"(?i)\b(hai|he|ka|ki|ke|ko|me|se|kya|kaun|kab|kaise|kahan)\b",
            r"(?i)\b(fasal|pani|kheti|khet|kisan|bimari|dawai)\b"
        ]
        
        self.setup_prompts()
    
    def setup_prompts(self):
        """Setup LLM prompts for query analysis"""
        
        self.classification_prompt = ChatPromptTemplate.from_template("""
You are an expert agricultural advisor for Indian farmers. Analyze the following query and determine:

1. Primary agricultural domain(s) from: crop_selection, pest_management, irrigation, finance_policy, market_timing, harvest_planning, input_materials
2. Language: hindi, english, or mixed (if code-switched)
3. Confidence level (0.0 to 1.0)
4. Key information needed to answer the query

Query: "{query}"
Context: {context}

Respond in JSON format:
{{
    "primary_domains": ["domain1", "domain2"],
    "language": "detected_language",
    "confidence": 0.85,
    "key_info_needed": ["location", "crop_type", "season"],
    "reasoning": "Brief explanation of classification",
    "requires_clarification": false,
    "clarification_questions": []
}}
""")
        
        self.translation_prompt = ChatPromptTemplate.from_template("""
Translate the following agricultural query from {source_lang} to {target_lang}.
Maintain agricultural terminology and context.

Original query: "{query}"
Translated query:
""")
    
    def detect_language(self, text: str) -> Language:
        """Detect query language using pattern matching"""
        
        # Check for Devanagari script
        if any(re.search(pattern, text) for pattern in self.hindi_patterns[:1]):
            return Language.HINDI
        
        # Check for Hindi words in Roman script
        hindi_matches = sum(1 for pattern in self.hindi_patterns[1:] if re.search(pattern, text))
        
        # Check for English agricultural terms
        english_pattern = r"(?i)\b(crop|water|pest|farm|seed|harvest|plant|grow)\b"
        english_matches = len(re.findall(english_pattern, text))
        
        if hindi_matches > 0 and english_matches > 0:
            return Language.MIXED
        elif hindi_matches > english_matches:
            return Language.HINDI
        else:
            return Language.ENGLISH
    
    def classify_domains(self, query: str) -> Tuple[List[QueryDomain], float]:
        """Classify query into agricultural domains using pattern matching"""
        
        domain_scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query))
                score += matches
            
            if score > 0:
                domain_scores[domain] = score / len(patterns)
        
        if not domain_scores:
            return [QueryDomain.GENERAL], 0.3
        
        # Sort by score and take top domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take domains with score >= 50% of top score
        top_score = sorted_domains[0][1]
        threshold = top_score * 0.5
        
        selected_domains = [domain for domain, score in sorted_domains if score >= threshold]
        avg_confidence = sum(score for _, score in sorted_domains[:len(selected_domains)]) / len(selected_domains)
        
        return selected_domains, min(avg_confidence, 1.0)
    
    async def analyze_query_with_llm(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for advanced query analysis"""
        
        try:
            prompt = self.classification_prompt.format(
                query=query,
                context=str(context)
            )
            
            response = await self.llm.ainvoke(prompt)
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON: {response.content}")
                return {}
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {}
    
    def extract_location_info(self, query: str, context: Dict[str, Any]) -> Optional[Location]:
        """Extract location information from query"""
        
        # Check context first
        if "location" in context:
            return context["location"]
        
        # Simple pattern matching for Indian locations
        state_pattern = r"(?i)\b(" + "|".join([
            "punjab", "haryana", "rajasthan", "gujarat", "maharashtra",
            "andhra pradesh", "telangana", "karnataka", "kerala", "tamil nadu",
            "west bengal", "bihar", "uttar pradesh", "madhya pradesh", "odisha"
        ]) + r")\b"
        
        state_match = re.search(state_pattern, query)
        if state_match:
            return Location(
                state=state_match.group(1).title(),
                district="Unknown"
            )
        
        return None
    
    def select_agents(self, domains: List[QueryDomain]) -> List[str]:
        """Select appropriate agents based on classified domains"""
        
        selected_agents = []
        
        for domain in domains:
            if domain in self.agent_registry:
                selected_agents.extend(self.agent_registry[domain])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(selected_agents))
    
    def determine_execution_plan(self, domains: List[QueryDomain], agents: List[str]) -> str:
        """Determine how to execute multiple agents"""
        
        if len(agents) <= 1:
            return "single"
        
        # If domains are independent, use parallel execution
        independent_domains = {
            QueryDomain.CROP_SELECTION, QueryDomain.PEST_MANAGEMENT,
            QueryDomain.FINANCE_POLICY, QueryDomain.MARKET_TIMING
        }
        
        dependent_domains = {
            QueryDomain.IRRIGATION, QueryDomain.HARVEST_PLANNING,
            QueryDomain.INPUT_MATERIALS
        }
        
        has_independent = any(d in independent_domains for d in domains)
        has_dependent = any(d in dependent_domains for d in domains)
        
        if has_independent and has_dependent:
            return "hierarchical"  # Independent first, then dependent
        elif len(agents) <= 3:
            return "parallel"
        else:
            return "sequential"
    
    async def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main routing execution logic"""
        
        try:
            # Extract query from task
            if isinstance(task, AgricultureTask) and task.query_data:
                agriculture_query = task.query_data
            else:
                # Create AgricultureQuery from task description
                agriculture_query = AgricultureQuery(
                    query_text=task.description,
                    query_language=Language.ENGLISH,
                    context=context
                )
            
            query_text = agriculture_query.query_text
            
            logger.info(f"Processing query: {query_text[:100]}...")
            
            # Step 1: Language detection
            detected_language = self.detect_language(query_text)
            
            # Step 2: Domain classification (pattern-based)
            domains, pattern_confidence = self.classify_domains(query_text)
            
            # Step 3: Enhanced analysis with LLM (if available)
            llm_analysis = await self.analyze_query_with_llm(query_text, context)
            
            # Combine pattern-based and LLM analysis
            if llm_analysis:
                llm_domains = [QueryDomain(d) for d in llm_analysis.get("primary_domains", [])]
                if llm_domains:
                    domains = llm_domains
                
                llm_confidence = llm_analysis.get("confidence", pattern_confidence)
                final_confidence = (pattern_confidence + llm_confidence) / 2
            else:
                final_confidence = pattern_confidence
            
            # Step 4: Extract location information
            location = self.extract_location_info(query_text, context)
            
            # Step 5: Select appropriate agents
            selected_agents = self.select_agents(domains)
            
            # Step 6: Determine execution plan
            execution_plan = self.determine_execution_plan(domains, selected_agents)
            
            # Step 7: Create routing decision
            routing_decision = RoutingDecision(
                query_id=agriculture_query.query_id,
                detected_domains=domains,
                detected_language=detected_language,
                confidence=final_confidence,
                selected_agents=selected_agents,
                execution_plan=execution_plan,
                reasoning=f"Pattern-based classification detected {len(domains)} domain(s). "
                         f"Selected {len(selected_agents)} agent(s) for {execution_plan} execution.",
                requires_clarification=final_confidence < 0.6 or not selected_agents
            )
            
            # Add clarification questions if needed
            if routing_decision.requires_clarification:
                routing_decision.clarification_questions = [
                    "Could you please specify your location (state/district)?",
                    "What type of farming question do you have (crop selection, pest control, irrigation, etc.)?",
                    "Are you asking about a specific crop or farming in general?"
                ]
            
            logger.info(f"Routing decision: {len(selected_agents)} agents, {execution_plan} execution, confidence: {final_confidence:.2f}")
            
            return {
                "routing_decision": routing_decision,
                "agriculture_query": agriculture_query,
                "detected_location": location,
                "processing_time_ms": 500,  # Placeholder
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Router execution failed: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def can_handle_task(self, task: Task) -> bool:
        """Check if this router can handle the task"""
        return AgricultureCapability.QUERY_ROUTING in self.capabilities


# Utility functions for router integration
def create_agriculture_router(llm: Optional[BaseLanguageModel] = None) -> AgricultureRouter:
    """Factory function to create agriculture router"""
    return AgricultureRouter(llm=llm)


def register_agriculture_agents(router: AgricultureRouter, agent_mapping: Dict[str, str]):
    """Register agricultural agents with the router"""
    for domain_str, agent_id in agent_mapping.items():
        try:
            domain = QueryDomain(domain_str)
            if domain not in router.agent_registry:
                router.agent_registry[domain] = []
            router.agent_registry[domain].append(agent_id)
        except ValueError:
            logger.warning(f"Unknown domain: {domain_str}")


# Example usage for testing
if __name__ == "__main__":
    # Test the router
    async def test_router():
        router = create_agriculture_router()
        
        test_queries = [
            "Mujhe kya fasal ugani chahiye Punjab mein?",
            "My wheat crop has yellow spots, what should I spray?",
            "When should I irrigate my cotton field?",
            "Where can I get loan for buying tractor?",
            "Best time to sell rice in mandi?"
        ]
        
        for query in test_queries:
            task = AgricultureTask(
                task_id=f"test_{datetime.now().timestamp()}",
                description=query,
                task_type="routing",
                priority=TaskPriority.MEDIUM,
                required_capabilities=[AgricultureCapability.QUERY_ROUTING]
            )
            
            result = await router.execute(task, {})
            print(f"\nQuery: {query}")
            print(f"Result: {result}")
    
    # Run test
    asyncio.run(test_router())
