#!/usr/bin/env python3
"""
Live dashboard test - sends real WebSocket updates to test your dashboard.
This will trigger actual agent activities visible in your frontend.
"""

import asyncio
import websockets
import json
import time
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.services.websocket_integration import integration_service

def test_websocket_updates():
    """Send test updates through the WebSocket system."""
    print("🚀 Testing Dashboard with Live WebSocket Updates")
    print("="*60)
    print("📊 Open your dashboard at: http://localhost:5174/")
    print("👀 Watch for real-time updates!")
    print("="*60)
    
    # Test 1: Agent status updates
    print("\n1️⃣ Sending agent status updates...")
    
    agent_updates = [
        {
            "type": "agent_update",
            "event": "status_changed",
            "agent_id": "agent-001",
            "status": "busy",
            "previous_status": "idle",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "current_task": "Processing customer reviews",
                "progress": 25
            }
        },
        {
            "type": "agent_update", 
            "event": "status_changed",
            "agent_id": "agent-002",
            "status": "running",
            "previous_status": "idle",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "current_task": "Data preprocessing",
                "progress": 60
            }
        },
        {
            "type": "agent_update",
            "event": "status_changed", 
            "agent_id": "agent-003",
            "status": "completed",
            "previous_status": "running",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "current_task": "API data fetch completed",
                "progress": 100
            }
        }
    ]
    
    for update in agent_updates:
        print(f"📤 Sending agent update: {update['agent_id']} -> {update['status']}")
        integration_service.broadcast_agent_update(
            agent_id=update['agent_id'],
            event=update['event'], 
            status=update['status'],
            previous_status=update['previous_status'],
            details=update['details']
        )
        time.sleep(2)
    
    # Test 2: Workflow updates
    print("\n2️⃣ Sending workflow updates...")
    
    workflow_updates = [
        {
            "workflow_id": "wf-dashboard-test",
            "event": "workflow_started",
            "status": "running",
            "current_step": "Initialize Data Source",
            "progress": 0,
            "details": {
                "total_steps": 5,
                "estimated_duration": "2 minutes"
            }
        },
        {
            "workflow_id": "wf-dashboard-test", 
            "event": "step_completed",
            "status": "running",
            "current_step": "Text Preprocessing",
            "progress": 40,
            "details": {
                "completed_step": "Initialize Data Source",
                "next_step": "Sentiment Analysis"
            }
        },
        {
            "workflow_id": "wf-dashboard-test",
            "event": "step_completed", 
            "status": "running",
            "current_step": "Sentiment Analysis",
            "progress": 80,
            "details": {
                "completed_step": "Text Preprocessing",
                "next_step": "Generate Report"
            }
        },
        {
            "workflow_id": "wf-dashboard-test",
            "event": "workflow_completed",
            "status": "completed", 
            "current_step": "Generate Report",
            "progress": 100,
            "details": {
                "completed_step": "Generate Report",
                "total_duration": "1m 23s",
                "success": True
            }
        }
    ]
    
    for update in workflow_updates:
        print(f"📤 Sending workflow update: {update['current_step']} ({update['progress']}%)")
        integration_service.broadcast_workflow_update(
            workflow_id=update['workflow_id'],
            event=update['event'],
            status=update['status'],
            current_step=update['current_step'],
            progress=update['progress'],
            details=update['details']
        )
        time.sleep(3)
    
    # Test 3: System notifications
    print("\n3️⃣ Sending system notifications...")
    
    notifications = [
        {
            "event_type": "agent_performance",
            "message": "Agent performance metrics updated",
            "level": "info",
            "details": {
                "agents_active": 3,
                "avg_response_time": "1.2s",
                "success_rate": "96%"
            }
        },
        {
            "event_type": "workflow_milestone",
            "message": "100 workflows completed successfully",
            "level": "success", 
            "details": {
                "milestone": 100,
                "period": "last 24 hours"
            }
        },
        {
            "event_type": "system_health",
            "message": "All systems operational",
            "level": "info",
            "details": {
                "cpu_usage": "23%",
                "memory_usage": "67%",
                "active_connections": 7
            }
        }
    ]
    
    for notification in notifications:
        print(f"📤 Sending notification: {notification['message']}")
        integration_service.broadcast_system_notification(
            event_type=notification['event_type'],
            message=notification['message'],
            level=notification['level'],
            details=notification['details']
        )
        time.sleep(2)
    
    print("\n" + "="*60)
    print("✅ Dashboard test complete!")
    print("🎯 Your dashboard should have shown:")
    print("   • Agent status changes (busy, running, completed)")
    print("   • Workflow progress (0% → 100%)")
    print("   • System notifications") 
    print("📊 Dashboard URL: http://localhost:5174/")
    print("="*60)

def main():
    """Main test function."""
    try:
        test_websocket_updates()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
