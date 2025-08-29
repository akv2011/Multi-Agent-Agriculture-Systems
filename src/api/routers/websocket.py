
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

from src.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Global WebSocket manager instance
ws_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    global ws_manager
    if ws_manager is None:
        # This will be set from the main app
        from main import app
        ws_manager = app.state.ws_manager
    return ws_manager


@router.websocket("/updates")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="Unique client identifier"),
    filters: Optional[str] = Query(None, description="Comma-separated event filters")
):
    manager = get_websocket_manager()
    
    # Parse filters
    subscription_filters = []
    if filters:
        subscription_filters = [f.strip() for f in filters.split(",")]
    
    # Prepare client info
    client_info = {
        "client_id": client_id or f"client_{id(websocket)}",
        "subscription_filters": subscription_filters,
        "connected_at": datetime.now().isoformat(),
        "user_agent": websocket.headers.get("user-agent", "unknown"),
        "origin": websocket.headers.get("origin", "unknown")
    }
    
    try:
        # Accept the WebSocket connection
        await manager.connect(websocket, client_info)
        logger.info(f"WebSocket client connected: {client_info['client_id']}")
        
        # Send initial system status
        await manager.send_to_client(websocket, {
            "type": "system_status",
            "message": "Connected to AgentWeaver real-time updates",
            "system_info": {
                "version": "1.0.0",
                "active_connections": len(manager.active_connections),
                "available_events": [
                    "agent_updates",
                    "workflow_updates", 
                    "system_notifications",
                    "error_events",
                    "performance_metrics"
                ]
            },
            "client_info": client_info
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                logger.debug(f"Received message from {client_info['client_id']}: {message}")
                
                # Handle different message types
                await handle_client_message(websocket, message, manager)
                
            except WebSocketDisconnect:
                # Client disconnected, exit the loop
                logger.info(f"Client {client_info['client_id']} disconnected during message receive")
                break
            except json.JSONDecodeError:
                try:
                    await manager.send_to_client(websocket, {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    # Connection might be closed
                    break
            except Exception as e:
                logger.error(f"Error processing client message: {e}")
                try:
                    await manager.send_to_client(websocket, {
                        "type": "error", 
                        "message": f"Error processing message: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    # Connection might be closed
                    break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_info['client_id']}")
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, message: Dict[str, Any], manager: WebSocketManager):
    try:
        message_type = message.get("type", "unknown")
        
        if message_type == "ping":
            # Respond to ping with pong
            await manager.send_to_client(websocket, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "subscribe":
            # Update subscription filters
            filters = message.get("filters", [])
            if websocket in manager.connection_info:
                manager.connection_info[websocket]["subscription_filters"] = filters
                await manager.send_to_client(websocket, {
                    "type": "subscription_updated",
                    "filters": filters,
                    "message": f"Subscribed to {len(filters)} event types",
                    "timestamp": datetime.now().isoformat()
                })
            
        elif message_type == "get_stats":
            # Send connection statistics
            stats = manager.get_connection_stats()
            await manager.send_to_client(websocket, {
                "type": "connection_stats",
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "get_system_status":
            # Send current system status
            await manager.send_to_client(websocket, {
                "type": "system_status",
                "status": {
                    "active_connections": len(manager.active_connections),
                    "server_time": datetime.now().isoformat(),
                    "uptime": "unknown",  # TODO: Calculate actual uptime
                    "version": "1.0.0"
                },
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            # Unknown message type
            await manager.send_to_client(websocket, {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "supported_types": ["ping", "subscribe", "get_stats", "get_system_status"],
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error handling client message: {e}")
        await manager.send_to_client(websocket, {
            "type": "error",
            "message": f"Error handling message: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


@router.get("/test", response_class=HTMLResponse)
async def websocket_test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test Page</h1>
        <p>Use this page to test WebSocket connections.</p>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
        
        <script>
            const ws = new WebSocket('ws://localhost:8001/ws/chat');
            const messages = document.getElementById('messages');
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                messages.innerHTML += '<div>' + message.content + '</div>';
            };
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                ws.send(JSON.stringify({content: input.value}));
                input.value = '';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/stats")
async def get_websocket_stats():
    try:
        manager = get_websocket_manager()
        stats = manager.get_connection_stats()
        
        return {
            "websocket_stats": stats,
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "version": "1.0.0",
                "uptime": "unknown"  # TODO: Calculate actual uptime
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        return {
            "error": f"Failed to get WebSocket stats: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# Helper functions for broadcasting updates (to be used by other parts of the system)
async def broadcast_agent_update(agent_id: str, status: str, details: Dict[str, Any] = None):
    try:
        manager = get_websocket_manager()
        await manager.send_agent_update(agent_id, status, details)
        logger.debug(f"Broadcasted agent update: {agent_id} -> {status}")
    except Exception as e:
        logger.error(f"Error broadcasting agent update: {e}")


async def broadcast_workflow_update(workflow_id: str, status: str, step: str = None, details: Dict[str, Any] = None):
    try:
        manager = get_websocket_manager()
        await manager.send_workflow_update(workflow_id, status, step, details)
        logger.debug(f"Broadcasted workflow update: {workflow_id} -> {status}")
    except Exception as e:
        logger.error(f"Error broadcasting workflow update: {e}")


async def broadcast_system_notification(notification_type: str, message: str, level: str = "info"):
    try:
        manager = get_websocket_manager()
        await manager.send_system_notification(notification_type, message, level)
        logger.debug(f"Broadcasted system notification: {notification_type}")
    except Exception as e:
        logger.error(f"Error broadcasting system notification: {e}")


@router.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat functionality"""
    manager = get_websocket_manager()
    
    await websocket.accept()
    connection_id = f"chat_{id(websocket)}"
    
    # Add to active connections
    if not hasattr(manager, 'chat_connections'):
        manager.chat_connections = {}
    manager.chat_connections[connection_id] = websocket
    
    logger.info(f"Chat WebSocket connected: {connection_id}")
    
    # Send welcome message
    await websocket.send_json({
        "type": "chat_message",
        "message_id": f"welcome_{connection_id}",
        "content": "Hello! I'm your AgriHelper assistant. How can I help you today?",
        "timestamp": datetime.now().isoformat(),
        "sender": "assistant"
    })
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                logger.info(f"Received chat message: {message}")
                
                # Echo back for now (can be enhanced with actual chat processing)
                response = {
                    "type": "chat_message",
                    "message_id": f"response_{datetime.now().timestamp()}",
                    "content": f"I received your message: {message.get('content', 'No content')}",
                    "timestamp": datetime.now().isoformat(),
                    "sender": "assistant"
                }
                
                await websocket.send_json(response)
                
            except json.JSONDecodeError:
                logger.warning(f"Received invalid JSON from chat client: {data}")
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected: {connection_id}")
        if hasattr(manager, 'chat_connections') and connection_id in manager.chat_connections:
            del manager.chat_connections[connection_id]
    except Exception as e:
        logger.error(f"Error in chat WebSocket: {e}")
        if hasattr(manager, 'chat_connections') and connection_id in manager.chat_connections:
            del manager.chat_connections[connection_id]
