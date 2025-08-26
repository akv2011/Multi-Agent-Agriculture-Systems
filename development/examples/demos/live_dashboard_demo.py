#!/usr/bin/env python3
"""
AgentWeaver demo that sends real-time updates to the dashboard via WebSocket
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def send_websocket_update(message):
    """Send an update to the WebSocket manager running on the main server"""
    try:
        # Send via HTTP to the main server which will broadcast via WebSocket
        async with aiohttp.ClientSession() as session:
            # Use a direct broadcast endpoint if available, or simulate agent updates
            url = "http://localhost:8000/api/test/broadcast"  # We'll need to create this endpoint
            async with session.post(url, json=message) as response:
                if response.status == 200:
                    print(f"📡 Sent update: {message['type']}")
                else:
                    print(f"⚠️  Failed to send update: {response.status}")
    except Exception as e:
        print(f"⚠️  Could not send WebSocket update: {e}")

async def run_demo_with_live_updates():
    print("🚀 AgentWeaver Live Dashboard Demo")
    print("=" * 50)
    print("This demo will send real-time updates to your dashboard!")
    print()
    
    # Simulate agent startup
    agents = [
        {"id": "text_analyzer", "name": "Text Analysis Agent", "status": "idle"},
        {"id": "data_processor", "name": "Data Processing Agent", "status": "idle"}, 
        {"id": "api_client", "name": "API Interaction Agent", "status": "idle"}
    ]
    
    print("📋 Starting agents...")
    for agent in agents:
        await send_websocket_update({
            "type": "agent_update",
            "event": "status_changed",
            "agent_id": agent["id"],
            "status": "running",
            "previous_status": "idle",
            "details": {
                "name": agent["name"],
                "current_task": "Initializing...",
                "started_at": datetime.now().isoformat()
            }
        })
        await asyncio.sleep(0.5)  # Stagger the startup
    
    # Simulate workflow execution
    workflow_id = f"demo_workflow_{int(time.time())}"
    
    print("🔄 Starting workflow execution...")
    await send_websocket_update({
        "type": "workflow_update", 
        "event": "workflow_started",
        "workflow_id": workflow_id,
        "status": "running",
        "current_step": "step_1_text_analysis",
        "progress": 0.0,
        "details": {
            "name": "Customer Review Analysis Pipeline",
            "started_at": datetime.now().isoformat(),
            "total_steps": 3,
            "steps_completed": 0
        }
    })
    
    # Step 1: Text Analysis
    print("   Step 1: Text Analysis...")
    await send_websocket_update({
        "type": "agent_update",
        "event": "status_changed", 
        "agent_id": "text_analyzer",
        "status": "busy",
        "previous_status": "running",
        "details": {
            "current_task": "Analyzing customer sentiment",
            "progress": 0.3
        }
    })
    
    await asyncio.sleep(2)  # Simulate processing time
    
    await send_websocket_update({
        "type": "workflow_update",
        "event": "step_completed", 
        "workflow_id": workflow_id,
        "status": "running",
        "current_step": "step_2_data_enrichment",
        "progress": 0.33,
        "details": {
            "name": "Customer Review Analysis Pipeline",
            "steps_completed": 1,
            "current_step_name": "Data Enrichment"
        }
    })
    
    # Step 2: Data Processing
    print("   Step 2: Data Enrichment...")
    await send_websocket_update({
        "type": "agent_update",
        "event": "status_changed",
        "agent_id": "data_processor", 
        "status": "busy",
        "previous_status": "running",
        "details": {
            "current_task": "Enriching customer data",
            "progress": 0.6
        }
    })
    
    await asyncio.sleep(2)
    
    await send_websocket_update({
        "type": "workflow_update",
        "event": "step_completed",
        "workflow_id": workflow_id, 
        "status": "running",
        "current_step": "step_3_api_integration",
        "progress": 0.66,
        "details": {
            "steps_completed": 2,
            "current_step_name": "API Integration"
        }
    })
    
    # Step 3: API Integration
    print("   Step 3: API Integration...")
    await send_websocket_update({
        "type": "agent_update",
        "event": "status_changed",
        "agent_id": "api_client",
        "status": "busy", 
        "previous_status": "running",
        "details": {
            "current_task": "Fetching external data",
            "progress": 0.9
        }
    })
    
    await asyncio.sleep(2)
    
    # Workflow completion
    print("✅ Workflow completed!")
    await send_websocket_update({
        "type": "workflow_update",
        "event": "workflow_completed",
        "workflow_id": workflow_id,
        "status": "completed", 
        "current_step": "completed",
        "progress": 1.0,
        "details": {
            "name": "Customer Review Analysis Pipeline", 
            "completed_at": datetime.now().isoformat(),
            "execution_time": 6.0,
            "steps_completed": 3,
            "total_steps": 3
        }
    })
    
    # Reset agents to idle
    for agent in agents:
        await send_websocket_update({
            "type": "agent_update",
            "event": "status_changed",
            "agent_id": agent["id"],
            "status": "idle",
            "previous_status": "busy",
            "details": {
                "current_task": None,
                "last_completed": datetime.now().isoformat()
            }
        })
    
    print()
    print("🎯 Demo completed! Check your dashboard for real-time updates!")
    print("   The agents and workflow should now show live data instead of mock data.")

if __name__ == "__main__":
    asyncio.run(run_demo_with_live_updates())
