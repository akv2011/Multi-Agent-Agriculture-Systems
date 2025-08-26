import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketIntegrationService:
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.active_workflows = {}
        self.agent_states = {}
        
    def set_websocket_manager(self, manager):
        self.websocket_manager = manager
        
    async def notify_workflow_started(self, workflow_id: str, workflow_data: Dict[str, Any]):
        if not self.websocket_manager:
            return
            
        try:
            # Track workflow
            self.active_workflows[workflow_id] = {
                "id": workflow_id,
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "steps_completed": 0,
                "total_steps": workflow_data.get("estimated_steps", 5),
                "current_step": "initializing",
                "input_data": workflow_data.get("input_data", {}),
                "metadata": workflow_data.get("metadata", {})
            }
            
            message = {
                "type": "workflow_update",
                "event": "workflow_started",
                "workflow_id": workflow_id,
                "status": "running",
                "current_step": "initializing",
                "progress": 0.0,
                "details": {
                    "started_at": self.active_workflows[workflow_id]["started_at"],
                    "estimated_steps": self.active_workflows[workflow_id]["total_steps"],
                    "input_summary": self._summarize_input(workflow_data.get("input_data", {}))
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.info(f"Broadcasted workflow start notification for {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting workflow start for {workflow_id}: {e}")
    
    async def notify_workflow_step(self, workflow_id: str, step_name: str, step_data: Dict[str, Any] = None):
        if not self.websocket_manager:
            return
            
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["steps_completed"] += 1
                workflow["current_step"] = step_name
                workflow["progress"] = workflow["steps_completed"] / workflow["total_steps"]
                
                message = {
                    "type": "workflow_update",
                    "event": "step_completed",
                    "workflow_id": workflow_id,
                    "status": "running",
                    "current_step": step_name,
                    "progress": min(workflow["progress"], 1.0),
                    "details": {
                        "step_data": step_data or {},
                        "steps_completed": workflow["steps_completed"],
                        "total_steps": workflow["total_steps"]
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket_manager.broadcast(message)
                logger.info(f"Broadcasted step completion for {workflow_id}: {step_name}")
                
        except Exception as e:
            logger.error(f"Error broadcasting workflow step for {workflow_id}: {e}")
    
    async def notify_workflow_completed(self, workflow_id: str, result: Dict[str, Any]):
        if not self.websocket_manager:
            return
            
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["status"] = "completed"
                workflow["completed_at"] = datetime.now().isoformat()
                workflow["progress"] = 1.0
                workflow["result"] = result
                
                execution_time = None
                if "started_at" in workflow:
                    start_time = datetime.fromisoformat(workflow["started_at"])
                    execution_time = (datetime.now() - start_time).total_seconds()
                
                message = {
                    "type": "workflow_update",
                    "event": "workflow_completed",
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "current_step": "completed",
                    "progress": 1.0,
                    "details": {
                        "completed_at": workflow["completed_at"],
                        "execution_time": execution_time,
                        "result_summary": self._summarize_result(result),
                        "total_steps": workflow["steps_completed"]
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket_manager.broadcast(message)
                logger.info(f"Broadcasted workflow completion for {workflow_id}")
                
                # Keep completed workflows for a while, then clean up
                asyncio.create_task(self._cleanup_workflow(workflow_id, delay=300))  # 5 minutes
                
        except Exception as e:
            logger.error(f"Error broadcasting workflow completion for {workflow_id}: {e}")
    
    async def notify_workflow_failed(self, workflow_id: str, error: str, error_details: Dict[str, Any] = None):
        if not self.websocket_manager:
            return
            
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["status"] = "failed"
                workflow["failed_at"] = datetime.now().isoformat()
                workflow["error"] = error
                workflow["error_details"] = error_details or {}
                
                message = {
                    "type": "workflow_update",
                    "event": "workflow_failed",
                    "workflow_id": workflow_id,
                    "status": "failed",
                    "current_step": workflow.get("current_step", "unknown"),
                    "progress": workflow.get("progress", 0.0),
                    "details": {
                        "failed_at": workflow["failed_at"],
                        "error": error,
                        "error_details": error_details or {},
                        "steps_completed": workflow.get("steps_completed", 0)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket_manager.broadcast(message)
                logger.info(f"Broadcasted workflow failure for {workflow_id}")
                
                # Clean up failed workflow after delay
                asyncio.create_task(self._cleanup_workflow(workflow_id, delay=600))  # 10 minutes
                
        except Exception as e:
            logger.error(f"Error broadcasting workflow failure for {workflow_id}: {e}")
    
    async def notify_agent_status_change(self, agent_id: str, old_status: str, new_status: str, details: Dict[str, Any] = None):
        if not self.websocket_manager:
            return
            
        try:
            # Update agent state tracking
            if agent_id not in self.agent_states:
                self.agent_states[agent_id] = {}
            
            self.agent_states[agent_id].update({
                "status": new_status,
                "last_status_change": datetime.now().isoformat(),
                "previous_status": old_status,
                "details": details or {}
            })
            
            message = {
                "type": "agent_update",
                "event": "status_changed",
                "agent_id": agent_id,
                "status": new_status,
                "previous_status": old_status,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.info(f"Broadcasted agent status change for {agent_id}: {old_status} -> {new_status}")
            
        except Exception as e:
            logger.error(f"Error broadcasting agent status change for {agent_id}: {e}")
    
    async def notify_system_event(self, event_type: str, message: str, level: str = "info", details: Dict[str, Any] = None):
        if not self.websocket_manager:
            return
            
        try:
            notification = {
                "type": "system_notification",
                "event_type": event_type,
                "message": message,
                "level": level,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(notification)
            logger.info(f"Broadcasted system event: {event_type} - {message}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system event {event_type}: {e}")
    
    async def notify_priority_query(self, query_id: str, priority_data: Dict[str, Any]):
        """Notify dashboard of high priority query processing"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "priority_query",
                "event": "high_priority_query_received",
                "query_id": query_id,
                "priority": priority_data.get("priority", "high"),
                "query_preview": priority_data.get("query", "")[:100] + "...",
                "timestamp": priority_data.get("timestamp", datetime.now().isoformat()),
                "alert_level": "warning"
            }
            
            await self.websocket_manager.broadcast(message)
            logger.info(f"Priority query notification sent: {query_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify priority query: {e}")

    async def notify_system_metric_update(self, metric_data: Dict[str, Any]):
        """Notify dashboard of system-wide metric updates"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "system_metrics",
                "event": "metrics_updated",
                "metrics": {
                    "queries_processed": metric_data.get("queries_processed", 0),
                    "avg_confidence": metric_data.get("avg_confidence", 0.0),
                    "system_efficiency": metric_data.get("system_efficiency", 0.0),
                    "active_agents": len(self.agent_states),
                    "running_workflows": len(self.active_workflows)
                },
                "performance": {
                    "cpu_usage": metric_data.get("cpu_usage", 0.0),
                    "memory_usage": metric_data.get("memory_usage", 0.0),
                    "response_time": metric_data.get("response_time", 0.0)
                },
                "timestamp": metric_data.get("timestamp", datetime.now().isoformat())
            }
            
            await self.websocket_manager.broadcast(message)
            logger.debug(f"System metrics update sent")
            
        except Exception as e:
            logger.error(f"Failed to notify system metrics: {e}")

    async def notify_feedback_received(self, feedback_data: Dict[str, Any]):
        """Notify dashboard of user feedback"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "user_feedback",
                "event": "feedback_received",
                "query_id": feedback_data.get("query_id"),
                "rating": feedback_data.get("rating", 0),
                "sentiment": self._analyze_feedback_sentiment(feedback_data.get("comments", "")),
                "timestamp": feedback_data.get("timestamp", datetime.now().isoformat())
            }
            
            await self.websocket_manager.broadcast(message)
            logger.info(f"Feedback notification sent for query: {feedback_data.get('query_id')}")
            
        except Exception as e:
            logger.error(f"Failed to notify feedback: {e}")

    async def notify_agent_performance_update(self, agent_id: str, performance_data: Dict[str, Any]):
        """Notify dashboard of agent performance changes"""
        if not self.websocket_manager:
            return
            
        try:
            # Update agent state
            if agent_id not in self.agent_states:
                self.agent_states[agent_id] = {}
            
            self.agent_states[agent_id].update({
                "performance": performance_data,
                "last_updated": datetime.now().isoformat()
            })
            
            message = {
                "type": "agent_performance",
                "event": "performance_updated",
                "agent_id": agent_id,
                "performance": performance_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.debug(f"Agent performance update sent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify agent performance: {e}")

    async def notify_query_analytics(self, analytics_data: Dict[str, Any]):
        """Notify dashboard of query analytics updates"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "query_analytics",
                "event": "analytics_updated",
                "analytics": {
                    "hourly_trend": analytics_data.get("hourly_trend", []),
                    "language_distribution": analytics_data.get("language_distribution", {}),
                    "intent_classification": analytics_data.get("intent_classification", {}),
                    "success_rates": analytics_data.get("success_rates", {}),
                    "processing_times": analytics_data.get("processing_times", [])
                },
                "insights": analytics_data.get("insights", []),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.info("Query analytics update sent")
            
        except Exception as e:
            logger.error(f"Failed to notify query analytics: {e}")

    async def notify_workflow_step_update(self, workflow_id: str, step_number: int, step_name: str):
        """Notify dashboard of workflow step progress"""
        if not self.websocket_manager:
            return
            
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["steps_completed"] = step_number
                workflow["current_step"] = step_name
                
                progress = (step_number / workflow["total_steps"]) * 100
                
                message = {
                    "type": "workflow_update",
                    "event": "step_completed",
                    "workflow_id": workflow_id,
                    "step_number": step_number,
                    "step_name": step_name,
                    "progress": progress,
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket_manager.broadcast(message)
                logger.debug(f"Workflow step update sent: {workflow_id} - Step {step_number}")
                
        except Exception as e:
            logger.error(f"Failed to notify workflow step: {e}")

    async def notify_error_alert(self, error_data: Dict[str, Any]):
        """Notify dashboard of system errors"""
        if not self.websocket_manager:
            return
            
        try:
            severity = error_data.get("severity", "warning")
            
            message = {
                "type": "error_alert",
                "event": "system_error",
                "severity": severity,
                "component": error_data.get("component", "unknown"),
                "error_message": error_data.get("message", "Unknown error"),
                "error_code": error_data.get("code", "UNKNOWN"),
                "affected_services": error_data.get("affected_services", []),
                "resolution_steps": error_data.get("resolution_steps", []),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.warning(f"Error alert sent: {severity} - {error_data.get('message', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to notify error alert: {e}")

    async def notify_agent_coordination_update(self, coordination_data: Dict[str, Any]):
        """Notify dashboard of agent coordination activities"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "agent_coordination",
                "event": "coordination_update",
                "coordination": {
                    "active_collaborations": coordination_data.get("active_collaborations", 0),
                    "task_distribution": coordination_data.get("task_distribution", {}),
                    "load_balancing": coordination_data.get("load_balancing", {}),
                    "efficiency_score": coordination_data.get("efficiency_score", 0.0)
                },
                "participating_agents": coordination_data.get("participating_agents", []),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.debug("Agent coordination update sent")
            
        except Exception as e:
            logger.error(f"Failed to notify agent coordination: {e}")

    async def notify_statistics_update(self, stats_data: Dict[str, Any]):
        """Notify dashboard of statistics updates"""
        if not self.websocket_manager:
            return
            
        try:
            message = {
                "type": "statistics_update",
                "event": "dashboard_stats_updated",
                "statistics": {
                    "total_queries": stats_data.get("total_queries", 0),
                    "success_rate": stats_data.get("success_rate", 0.0),
                    "average_processing_time": stats_data.get("average_processing_time", 0.0),
                    "active_workflows": stats_data.get("active_workflows", 0),
                    "agent_utilization": stats_data.get("agent_utilization", {}),
                    "system_load": stats_data.get("system_load", 0.0)
                },
                "trend_data": stats_data.get("trend_data", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.debug("Statistics update notification sent")
            
        except Exception as e:
            logger.error(f"Failed to notify statistics update: {e}")

    async def notify_agent_status_update(self, agent_id: str, status: str, details: Dict[str, Any] = None):
        """Notify dashboard of agent status changes"""
        if not self.websocket_manager:
            return
            
        try:
            # Update internal agent tracking
            if agent_id not in self.agent_states:
                self.agent_states[agent_id] = {}
            
            previous_status = self.agent_states[agent_id].get("status", "unknown")
            self.agent_states[agent_id].update({
                "status": status,
                "last_updated": datetime.now().isoformat(),
                "details": details or {}
            })
            
            message = {
                "type": "agent_status",
                "event": "agent_status_updated",
                "agent_id": agent_id,
                "status": status,
                "previous_status": previous_status,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_manager.broadcast(message)
            logger.debug(f"Agent status update sent: {agent_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Failed to notify agent status update: {e}")

    def _summarize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        summary = {}
        
        if "text" in input_data:
            text = input_data["text"]
            summary["text_length"] = len(text) if isinstance(text, str) else 0
            summary["text_preview"] = text[:100] + "..." if isinstance(text, str) and len(text) > 100 else text
        
        if "metadata" in input_data:
            summary["metadata_keys"] = list(input_data["metadata"].keys()) if isinstance(input_data["metadata"], dict) else []
        
        summary["total_keys"] = len(input_data)
        return summary
    
    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        summary = {}
        
        if "status" in result:
            summary["status"] = result["status"]
        
        if "sentiment_score" in result:
            summary["sentiment_score"] = result["sentiment_score"]
        
        if "routing_decision" in result:
            summary["routing_decision"] = result["routing_decision"]
        
        if "completed_steps" in result:
            summary["steps_executed"] = len(result["completed_steps"])
        
        summary["result_keys"] = len(result)
        return summary
    
    async def _cleanup_workflow(self, workflow_id: str, delay: int = 300):
        await asyncio.sleep(delay)
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            logger.info(f"Cleaned up workflow data for {workflow_id}")
    
    def get_system_status(self) -> Dict[str, Any]:
        active_workflows = [w for w in self.active_workflows.values() if w.get("status") in ["running", "pending"]]
        completed_workflows = [w for w in self.active_workflows.values() if w.get("status") == "completed"]
        failed_workflows = [w for w in self.active_workflows.values() if w.get("status") == "failed"]
        
        active_agents = [a for a in self.agent_states.values() if a.get("status") in ["active", "busy"]]
        
        return {
            "workflows": {
                "total": len(self.active_workflows),
                "active": len(active_workflows),
                "completed": len(completed_workflows),
                "failed": len(failed_workflows)
            },
            "agents": {
                "total": len(self.agent_states),
                "active": len(active_agents)
            },
            "websocket_connections": len(self.websocket_manager.active_connections) if self.websocket_manager else 0
        }


# Global instance
integration_service = WebSocketIntegrationService()
