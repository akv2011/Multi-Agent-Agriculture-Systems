"""
Enhanced Query Processing Service
Provides structured, comprehensive query processing with real-time dashboard updates
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging

from src.core.agriculture_models import AgricultureQuery, AgentResponse
from src.services.agriculture_integration import AgricultureIntegrationService
from src.services.websocket_integration import integration_service
from src.services.response_formatter import response_formatter
from src.agents.base_agent import BaseWorkerAgent

logger = logging.getLogger(__name__)

class EnhancedQueryResponse:
    """Structured response model for enhanced query processing"""
    
    def __init__(self):
        self.status = "processing"
        self.query_id = ""
        self.original_query = ""
        self.processing_timeline = []
        self.agent_analysis = {}
        self.comprehensive_response = {}
        self.technical_metrics = {}
        self.satellite_integration = {}
        self.confidence_breakdown = {}
        self.recommendations = []
        self.workflow_status = {}
        self.dashboard_updates = {}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "query_id": self.query_id,
            "original_query": self.original_query,
            "processing_timeline": self.processing_timeline,
            "agent_analysis": self.agent_analysis,
            "comprehensive_response": self.comprehensive_response,
            "technical_metrics": self.technical_metrics,
            "satellite_integration": self.satellite_integration,
            "confidence_breakdown": self.confidence_breakdown,
            "recommendations": self.recommendations,
            "workflow_status": self.workflow_status,
            "dashboard_updates": self.dashboard_updates,
            "timestamp": datetime.now().isoformat()
        }

class EnhancedQueryProcessor:
    """Enhanced query processor with comprehensive workflow and dashboard integration"""
    
    def __init__(self):
        # Initialize agriculture service with fallback
        try:
            from src.services.agriculture_integration import get_agriculture_service
            self.agriculture_service = get_agriculture_service()
            
            # If no global service available, create a minimal one
            if not self.agriculture_service:
                logger.warning("No global agriculture service found, creating minimal instance")
                from src.services.agriculture_integration import AgricultureIntegrationService
                from src.orchestration.supervisor import SupervisorNode
                
                # Create minimal supervisor for agriculture service
                supervisor = SupervisorNode("enhanced_query_supervisor")
                self.agriculture_service = AgricultureIntegrationService(supervisor)
        except Exception as e:
            logger.error(f"Failed to initialize agriculture service: {e}")
            self.agriculture_service = None
        
        self.active_workflows = {}
        self.agent_metrics = {}
        
    async def process_comprehensive_query(
        self, 
        query_text: str, 
        location: Optional[str] = None,
        include_satellite: bool = True,
        agent_preferences: Optional[List[str]] = None
    ) -> EnhancedQueryResponse:
        """
        Process query with comprehensive analysis and real-time updates
        """
        start_time = time.time()
        response = EnhancedQueryResponse()
        
        # Generate unique query ID
        response.query_id = f"enhanced_query_{int(time.time())}_{hash(query_text) % 10000}"
        response.original_query = query_text
        
        try:
            # Phase 1: Initialize workflow
            await self._initialize_workflow(response)
            
            # Phase 2: Query analysis and routing
            await self._analyze_and_route_query(response, query_text, location)
            
            # Phase 3: Agent coordination and execution
            await self._coordinate_agent_execution(response, include_satellite, agent_preferences)
            
            # Phase 4: Response synthesis and enhancement
            await self._synthesize_comprehensive_response(response)
            
            # Phase 5: Dashboard and metrics update
            await self._update_dashboard_metrics(response, time.time() - start_time)
            
            response.status = "completed"
            
        except Exception as e:
            logger.error(f"Error in comprehensive query processing: {e}")
            response.status = "error"
            response.comprehensive_response = {
                "error": str(e),
                "fallback_message": "We encountered an issue processing your query. Please try rephrasing or contact support."
            }
            
        return response
    
    async def _initialize_workflow(self, response: EnhancedQueryResponse):
        """Initialize workflow with dashboard notifications"""
        workflow_id = f"workflow_{response.query_id}"
        
        # Create workflow entry
        workflow_data = {
            "id": workflow_id,
            "query_id": response.query_id,
            "status": "initializing",
            "start_time": datetime.now().isoformat(),
            "estimated_steps": 5,
            "current_step": 1
        }
        
        self.active_workflows[workflow_id] = workflow_data
        response.workflow_status = workflow_data
        
        # Notify dashboard
        await integration_service.notify_workflow_started(workflow_id, {
            "query": response.original_query,
            "estimated_duration": 15,  # seconds
            "steps": ["Analysis", "Routing", "Agent Execution", "Synthesis", "Completion"]
        })
        
        response.processing_timeline.append({
            "step": "workflow_initialized",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
    
    async def _analyze_and_route_query(
        self, 
        response: EnhancedQueryResponse, 
        query_text: str, 
        location: Optional[str]
    ):
        """Comprehensive query analysis with multiple agent routing"""
        
        # Update workflow status
        await integration_service.notify_workflow_step_update(
            response.workflow_status["id"], 
            1, 
            "Query Analysis & Routing"
        )
        
        # Language detection and query classification
        query_analysis = {
            "language": self._detect_language(query_text),
            "intent": self._classify_intent(query_text),
            "complexity": self._assess_complexity(query_text),
            "entities": self._extract_entities(query_text),
            "location_context": location,
            "text": query_text  # Include original text for analysis
        }
        
        # Multi-agent routing decision
        routing_decisions = self._determine_agent_routing(query_analysis)
        
        response.agent_analysis = {
            "query_analysis": query_analysis,
            "routing_decisions": routing_decisions,
            "recommended_agents": [decision["agent_id"] for decision in routing_decisions],
            "confidence_scores": {decision["agent_id"]: decision["confidence"] for decision in routing_decisions}
        }
        
        response.processing_timeline.append({
            "step": "query_analyzed",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": {
                "agents_selected": len(routing_decisions),
                "primary_intent": query_analysis["intent"],
                "language": query_analysis["language"]
            }
        })
    
    async def _coordinate_agent_execution(
        self, 
        response: EnhancedQueryResponse, 
        include_satellite: bool,
        agent_preferences: Optional[List[str]]
    ):
        """Coordinate execution across multiple agents with real-time updates"""
        
        # Update workflow status
        await integration_service.notify_workflow_step_update(
            response.workflow_status["id"], 
            2, 
            "Agent Coordination & Execution"
        )
        
        # Create agriculture query object
        agriculture_query = AgricultureQuery(
            query_text=response.original_query,
            query_id=response.query_id,
            query_language=response.agent_analysis["query_analysis"]["language"]
        )
        
        # Execute agents in parallel with progress tracking
        agent_tasks = []
        selected_agents = response.agent_analysis["recommended_agents"]
        
        # Filter agents based on preferences if provided
        if agent_preferences:
            selected_agents = [agent for agent in selected_agents if agent in agent_preferences]
        
        for agent_id in selected_agents:
            task = self._execute_agent_with_tracking(agent_id, agriculture_query, response)
            agent_tasks.append(task)
        
        # Execute all agents concurrently
        agent_responses = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Process agent responses
        successful_responses = []
        failed_responses = []
        
        for i, agent_response in enumerate(agent_responses):
            agent_id = selected_agents[i]
            
            if isinstance(agent_response, Exception):
                failed_responses.append({
                    "agent_id": agent_id,
                    "error": str(agent_response)
                })
            else:
                successful_responses.append(agent_response)
                
                # Update agent metrics
                self._update_agent_metrics(agent_id, agent_response)
        
        response.comprehensive_response["agent_responses"] = successful_responses
        response.comprehensive_response["failed_agents"] = failed_responses
        
        response.processing_timeline.append({
            "step": "agents_executed",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": {
                "successful_agents": len(successful_responses),
                "failed_agents": len(failed_responses),
                "total_agents": len(selected_agents)
            }
        })
    
    async def _execute_agent_with_tracking(
        self, 
        agent_id: str, 
        query: AgricultureQuery, 
        response: EnhancedQueryResponse
    ) -> AgentResponse:
        """Execute single agent with progress tracking"""
        
        start_time = time.time()
        
        try:
            # Notify dashboard of agent execution start
            await integration_service.notify_agent_status_update(agent_id, "busy", {
                "current_task": f"Processing query {response.query_id}",
                "start_time": datetime.now().isoformat()
            })
            
            # Check if agriculture service is available
            if not self.agriculture_service:
                logger.warning(f"Agriculture service not available for agent {agent_id}")
                return self._create_fallback_agent_response(agent_id, query)
            
            # Execute agent through agriculture service
            agent_response = await self.agriculture_service.process_query_with_agent(
                query, agent_id
            )
            
            execution_time = time.time() - start_time
            
            # Notify dashboard of completion
            await integration_service.notify_agent_status_update(agent_id, "idle", {
                "last_task": f"Completed query {response.query_id}",
                "execution_time": execution_time,
                "success": True
            })
            
            return agent_response
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Notify dashboard of failure
            await integration_service.notify_agent_status_update(agent_id, "error", {
                "last_task": f"Failed query {response.query_id}",
                "execution_time": execution_time,
                "error": str(e),
                "success": False
            })
            
            # Return fallback response instead of raising exception
            logger.warning(f"Agent {agent_id} failed, returning fallback response: {e}")
            return self._create_fallback_agent_response(agent_id, query)
    
    def _create_fallback_agent_response(self, agent_id: str, query: AgricultureQuery) -> AgentResponse:
        """Create a fallback response when agent execution fails"""
        
        fallback_messages = {
            "crop_selection": "For crop selection advice, I recommend consulting local agricultural extension services who can provide guidance based on your specific soil conditions, climate, and market factors in your region.",
            "pest_management": "For pest and disease management, please consult with local agricultural experts who can identify specific issues and recommend appropriate treatments for your area.",
            "irrigation_optimization": "For irrigation planning, consider consulting with irrigation specialists who can assess your field conditions, water availability, and crop requirements.",
            "input_materials": "For fertilizer and input recommendations, please consult with local agricultural input dealers or extension services who can provide guidance based on soil testing and crop requirements.",
            "market_timing": "For market analysis and timing, I recommend checking local agricultural market reports and consulting with agricultural commodity experts in your region.",
            "finance_policy": "For agricultural finance and policy information, please contact your local agricultural extension office or relevant government agricultural departments.",
            "weather_forecast": "For weather information, please check local meteorological services or weather applications for accurate forecasts in your area.",
            "gemini_agriculture": "I apologize, but I'm currently unable to process your agricultural query. Please try rephrasing your question or consult with local agricultural experts for personalized advice."
        }
        
        message = fallback_messages.get(agent_id, fallback_messages["gemini_agriculture"])
        
        return AgentResponse(
            agent_id=agent_id,
            query_id=query.query_id,
            response_text=message,
            confidence_score=0.3,
            status="completed",
            recommendations=[
                "Consult local agricultural extension services",
                "Contact experienced farmers in your area",
                "Check with relevant agricultural departments"
            ],
            metadata={"fallback": True, "type": "service_unavailable"}
        )
    
    async def _synthesize_comprehensive_response(self, response: EnhancedQueryResponse):
        """Synthesize responses from multiple agents into comprehensive answer"""
        
        # Update workflow status
        await integration_service.notify_workflow_step_update(
            response.workflow_status["id"], 
            3, 
            "Response Synthesis & Enhancement"
        )
        
        agent_responses = response.comprehensive_response.get("agent_responses", [])
        
        if not agent_responses:
            response.comprehensive_response["final_answer"] = {
                "message": "I apologize, but I couldn't process your query with the available agents. Please try rephrasing your question or contact support.",
                "confidence": 0.1,
                "source": "system_fallback",
                "formatted_response": {
                    "executive_summary": {
                        "query_type": "System Error",
                        "key_insight": "No agent responses available",
                        "primary_recommendation": "Please try rephrasing your question",
                        "confidence_level": "Low",
                        "urgency": "Normal"
                    }
                }
            }
            return
        
        # Synthesize raw responses
        synthesis_result = self._perform_response_synthesis(agent_responses)
        
        # Clean and format the primary response text from AI agents
        raw_response_text = synthesis_result.get("primary_answer", "")
        
        # Apply comprehensive cleaning for AI responses
        if synthesis_result.get("primary_agent") == "gemini_agriculture":
            # Apply comprehensive cleaning for AI responses
            raw_response_text = self._clean_ai_response(raw_response_text)
            synthesis_result["primary_answer"] = raw_response_text
            
            # Use structured formatting for AI responses
            primary_agent_response = None
            for resp in agent_responses:
                if resp.agent_id == "gemini_agriculture":
                    primary_agent_response = {
                        "response_text": resp.response_text,
                        "confidence_score": resp.confidence_score,
                        "recommendations": resp.recommendations,
                        "metadata": resp.metadata
                    }
                    break
            
            if primary_agent_response:
                formatted_response = response_formatter.format_structured_ai_response(
                    primary_agent_response, 
                    response.agent_analysis.get("query_analysis", {})
                )
            else:
                # Fallback to regular formatting
                formatted_response = response_formatter.format_comprehensive_response(
                    raw_response_text, 
                    response.agent_analysis.get("query_analysis", {})
                )
        else:
            # Use regular formatting for specialist agents
            formatted_response = response_formatter.format_comprehensive_response(
                raw_response_text, 
                response.agent_analysis.get("query_analysis", {})
            )
        
        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(agent_responses)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(agent_responses)
        
        response.comprehensive_response.update({
            "final_answer": synthesis_result,
            "formatted_response": formatted_response,
            "confidence": overall_confidence,
            "source_agents": [resp.agent_id for resp in agent_responses],
            "synthesis_method": "weighted_priority_confidence_with_formatting"
        })
        
        response.recommendations = recommendations
        response.confidence_breakdown = {
            "overall": overall_confidence,
            "agent_confidences": {resp.agent_id: resp.confidence_score for resp in agent_responses},
            "synthesis_confidence": synthesis_result.get("confidence", 0.5),
            "formatting_applied": True
        }
        
        response.processing_timeline.append({
            "step": "response_synthesized_and_formatted",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": {
                "confidence": overall_confidence,
                "recommendations_count": len(recommendations),
                "source_agents": len(agent_responses),
                "formatting_sections": len(formatted_response.get("detailed_analysis", [])),
                "formatted_recommendations": len(formatted_response.get("actionable_recommendations", []))
            }
        })
    
    async def _update_dashboard_metrics(self, response: EnhancedQueryResponse, total_time: float):
        """Update dashboard with comprehensive metrics"""
        
        # Update workflow status
        await integration_service.notify_workflow_step_update(
            response.workflow_status["id"], 
            4, 
            "Dashboard & Metrics Update"
        )
        
        # Calculate technical metrics
        technical_metrics = {
            "total_processing_time_ms": total_time * 1000,
            "agent_execution_times": {},
            "satellite_integration": response.satellite_integration.get("enabled", False),
            "confidence_score": response.confidence_breakdown.get("overall", 0.0),
            "agents_used": len(response.comprehensive_response.get("agent_responses", [])),
            "workflow_efficiency": self._calculate_workflow_efficiency(response),
            "query_complexity": response.agent_analysis["query_analysis"]["complexity"],
            "success_rate": 1.0 if response.status == "completed" else 0.0
        }
        
        response.technical_metrics = technical_metrics
        
        # Update dashboard statistics
        dashboard_update = {
            "query_processed": True,
            "processing_time": total_time * 1000,
            "success": response.status == "completed",
            "agents_involved": response.agent_analysis["recommended_agents"],
            "confidence": response.confidence_breakdown.get("overall", 0.0),
            "complexity": response.agent_analysis["query_analysis"]["complexity"]
        }
        
        response.dashboard_updates = dashboard_update
        
        # Notify dashboard service
        await integration_service.notify_statistics_update(dashboard_update)
        
        # Complete workflow
        await integration_service.notify_workflow_completed(
            response.workflow_status["id"], 
            {
                "total_time": total_time,
                "success": response.status == "completed",
                "metrics": technical_metrics
            }
        )
        
        response.processing_timeline.append({
            "step": "dashboard_updated",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": technical_metrics
        })
    
    # Helper methods for query processing
    
    def _detect_language(self, text: str) -> str:
        """Enhanced language detection"""
        hindi_chars = any('\u0900' <= char <= '\u097F' for char in text)
        english_words = len([word for word in text.split() if word.isalpha() and all(ord(c) < 128 for c in word)])
        
        if hindi_chars and english_words > 0:
            return "hinglish"
        elif hindi_chars:
            return "hindi"
        else:
            return "english"
    
    def _classify_intent(self, text: str) -> str:
        """Classify query intent with higher accuracy"""
        lower_text = text.lower()
        
        intent_patterns = {
            "crop_recommendation": ["what crop", "which crop", "recommend crop", "best crop", "कौन सी फसल"],
            "disease_identification": ["disease", "pest", "insect", "spot", "blight", "कीड़े", "बीमारी"],
            "irrigation_planning": ["water", "irrigation", "moisture", "सिंचाई", "पानी"],
            "fertilizer_advice": ["fertilizer", "npk", "nutrient", "खाद", "उर्वरक"],
            "market_analysis": ["price", "market", "sell", "mandi", "कीमत", "बाजार"],
            "weather_forecast": ["weather", "rain", "temperature", "मौसम", "बारिश"],
            "general_guidance": ["help", "advice", "guidance", "suggest", "सलाह"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in lower_text for pattern in patterns):
                return intent
        
        return "general_guidance"
    
    def _assess_complexity(self, text: str) -> str:
        """Assess query complexity"""
        word_count = len(text.split())
        question_marks = text.count('?')
        keywords = len([word for word in text.lower().split() if word in [
            'how', 'what', 'when', 'where', 'why', 'which', 'कैसे', 'क्या', 'कब', 'कहाँ'
        ]])
        
        complexity_score = word_count * 0.1 + question_marks * 2 + keywords * 1.5
        
        if complexity_score > 10:
            return "high"
        elif complexity_score > 5:
            return "medium"
        else:
            return "low"
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract agricultural entities from text"""
        lower_text = text.lower()
        
        crops = ["wheat", "rice", "corn", "cotton", "soybean", "गेहूं", "चावल", "मक्का", "कपास"]
        diseases = ["blight", "rust", "spot", "wilt", "मरंड", "झुलसा"]
        locations = ["punjab", "haryana", "uttar pradesh", "maharashtra", "पंजाब", "हरियाणा"]
        
        entities = {
            "crops": [crop for crop in crops if crop in lower_text],
            "diseases": [disease for disease in diseases if disease in lower_text],
            "locations": [loc for loc in locations if loc in lower_text]
        }
        
        return entities
    
    def _determine_agent_routing(self, query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine which agents should process the query based on intent and content"""
        intent = query_analysis["intent"]
        complexity = query_analysis["complexity"]
        entities = query_analysis["entities"]
        
        routing_decisions = []
        
        # Primary agent based on intent - these are the actual specialized agents
        primary_agents = {
            "crop_recommendation": ("crop_selection", 0.9),
            "disease_identification": ("pest_management", 0.85),
            "irrigation_planning": ("irrigation_optimization", 0.8),
            "fertilizer_advice": ("input_materials", 0.85),
            "market_analysis": ("market_timing", 0.8),
            "weather_forecast": ("weather_forecast", 0.9),
            # Only use AI agent for general guidance or when no specific domain matches
            "general_guidance": ("gemini_agriculture", 0.7)
        }
        
        # Add primary agent if intent matches
        if intent in primary_agents:
            agent_id, confidence = primary_agents[intent]
            routing_decisions.append({
                "agent_id": agent_id,
                "confidence": confidence,
                "priority": 1,
                "reason": f"Primary agent for {intent}"
            })
        
        # For high complexity queries, add secondary specialized agents if relevant
        if complexity == "high":
            # Only add relevant secondary agents, not AI agent unless needed
            secondary_mapping = {
                "crop_recommendation": [("input_materials", 0.6, "Fertilizer recommendations for selected crops")],
                "disease_identification": [("input_materials", 0.5, "Treatment materials for identified diseases")],
                "irrigation_planning": [("crop_selection", 0.5, "Crop-specific water requirements")],
                "market_analysis": [("crop_selection", 0.4, "Crop profitability analysis")]
            }
            
            if intent in secondary_mapping:
                for agent_id, confidence, reason in secondary_mapping[intent]:
                    if agent_id not in [decision["agent_id"] for decision in routing_decisions]:
                        routing_decisions.append({
                            "agent_id": agent_id,
                            "confidence": confidence,
                            "priority": 2,
                            "reason": reason
                        })
        
        # Add finance agent if policy/subsidy related keywords detected
        query_text = query_analysis.get("text", "").lower()
        finance_keywords = ["loan", "subsidy", "scheme", "policy", "insurance", "ऋण", "योजना", "बीमा"]
        if any(keyword in query_text for keyword in finance_keywords):
            routing_decisions.append({
                "agent_id": "finance_policy",
                "confidence": 0.75,
                "priority": 1,
                "reason": "Financial/policy query detected"
            })
        
        # If no specific agents selected, use AI agent as fallback
        if not routing_decisions:
            routing_decisions.append({
                "agent_id": "gemini_agriculture",
                "confidence": 0.6,
                "priority": 1,
                "reason": "Fallback for unclassified query"
            })
        
        return routing_decisions
    
    def _perform_response_synthesis(self, agent_responses: List[AgentResponse]) -> Dict[str, Any]:
        """Synthesize multiple agent responses into comprehensive answer"""
        if not agent_responses:
            return {"message": "No responses available", "confidence": 0.0}
        
        # Sort by confidence and priority
        sorted_responses = sorted(
            agent_responses, 
            key=lambda x: x.confidence_score, 
            reverse=True
        )
        
        # Primary response from highest confidence agent
        primary_response = sorted_responses[0]
        
        # Combine insights from all agents
        combined_insights = []
        for response in sorted_responses:
            if response.response_text and len(response.response_text.strip()) > 10:
                combined_insights.append({
                    "agent": response.agent_id,
                    "insight": response.response_text[:200] + "..." if len(response.response_text) > 200 else response.response_text,
                    "confidence": response.confidence_score
                })
        
        synthesized_response = {
            "primary_answer": primary_response.response_text,
            "primary_agent": primary_response.agent_id,
            "confidence": primary_response.confidence_score,
            "supporting_insights": combined_insights[1:],  # Exclude primary
            "synthesis_timestamp": datetime.now().isoformat()
        }
        
        return synthesized_response
    
    def _generate_comprehensive_recommendations(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations from agent responses"""
        all_recommendations = []
        
        for response in agent_responses:
            if hasattr(response, 'recommendations') and response.recommendations:
                for rec in response.recommendations:
                    if isinstance(rec, dict):
                        all_recommendations.append({
                            **rec,
                            "source_agent": response.agent_id,
                            "confidence": response.confidence_score
                        })
        
        # Sort by priority and confidence
        all_recommendations.sort(
            key=lambda x: (x.get("priority", "medium") == "high", x.get("confidence", 0)), 
            reverse=True
        )
        
        return all_recommendations[:10]  # Top 10 recommendations
    
    def _calculate_overall_confidence(self, agent_responses: List[AgentResponse]) -> float:
        """Calculate overall confidence score"""
        if not agent_responses:
            return 0.0
        
        confidences = [resp.confidence_score for resp in agent_responses]
        
        # Weighted average with diminishing returns for additional agents
        weights = [1.0, 0.8, 0.6, 0.4, 0.2]
        
        weighted_sum = sum(
            conf * weights[min(i, len(weights)-1)] 
            for i, conf in enumerate(confidences)
        )
        
        weight_sum = sum(weights[:len(confidences)])
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _update_agent_metrics(self, agent_id: str, response: AgentResponse):
        """Update agent performance metrics"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {
                "total_queries": 0,
                "successful_queries": 0,
                "total_time": 0.0,
                "avg_confidence": 0.0
            }
        
        metrics = self.agent_metrics[agent_id]
        metrics["total_queries"] += 1
        
        if hasattr(response, 'processing_time') and response.processing_time:
            metrics["total_time"] += response.processing_time
        
        if response.confidence_score > 0.5:
            metrics["successful_queries"] += 1
        
        # Update average confidence
        metrics["avg_confidence"] = (
            (metrics["avg_confidence"] * (metrics["total_queries"] - 1) + response.confidence_score) 
            / metrics["total_queries"]
        )
    
    def _calculate_workflow_efficiency(self, response: EnhancedQueryResponse) -> float:
        """Calculate workflow efficiency score"""
        total_agents = len(response.agent_analysis.get("recommended_agents", []))
        successful_agents = len(response.comprehensive_response.get("agent_responses", []))
        overall_confidence = response.confidence_breakdown.get("overall", 0.0)
        
        if total_agents == 0:
            return 0.0
        
        success_ratio = successful_agents / total_agents
        efficiency = (success_ratio * 0.6) + (overall_confidence * 0.4)
        
        return min(efficiency, 1.0)
    
    def _clean_ai_response(self, response_text: str) -> str:
        """
        Clean AI response by removing markdown formatting and ensuring proper structure
        """
        if not response_text:
            return "I apologize, but I couldn't generate a proper response for your query."
        
        import re
        
        # Remove all asterisks used for bold/italic
        cleaned = re.sub(r'\*{1,}', '', response_text)
        
        # Remove hash symbols used for headers
        cleaned = re.sub(r'#{1,}\s*', '', cleaned)
        
        # Remove backticks
        cleaned = re.sub(r'`{1,}', '', cleaned)
        
        # Remove underscores used for emphasis
        cleaned = re.sub(r'_{1,}', '', cleaned)
        
        # Clean up bullet points
        cleaned = re.sub(r'^[\s]*[-\*\+•·]\s*', '• ', cleaned, flags=re.MULTILINE)
        
        # Fix excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        # Clean up HTML tags if any
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Convert markdown links to plain text
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
        
        # Ensure proper sentence structure
        cleaned = cleaned.strip()
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
        
        return cleaned

# Global instance
enhanced_processor = EnhancedQueryProcessor()
