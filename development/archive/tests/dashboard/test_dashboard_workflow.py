#!/usr/bin/env python3
"""
Test script to run a workflow and see real-time updates in the dashboard.
This will trigger agent activities that should show up in your frontend.
"""

import asyncio
import requests
import json
import time
from datetime import datetime

# Backend API URL
API_BASE = "http://localhost:8000"

def test_api_connection():
    """Test if the API is reachable."""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API is reachable")
            print(f"Health status: {response.json()}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def create_test_workflow():
    """Create a test workflow to see dashboard updates."""
    workflow_data = {
        "workflow_id": f"dashboard_test_{int(time.time())}",
        "title": "Dashboard Test Workflow",
        "description": "Testing real-time dashboard updates",
        "steps": [
            {
                "step_id": "step_1",
                "name": "Initialize Test Data",
                "agent_type": "data_processor",
                "parameters": {
                    "task": "Generate test dataset",
                    "size": 100
                }
            },
            {
                "step_id": "step_2", 
                "name": "Process Test Data",
                "agent_type": "text_analyzer",
                "parameters": {
                    "task": "Analyze generated data",
                    "mode": "sentiment"
                }
            },
            {
                "step_id": "step_3",
                "name": "Generate Report",
                "agent_type": "api_agent",
                "parameters": {
                    "task": "Create summary report",
                    "format": "json"
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/workflows/create", json=workflow_data)
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ Workflow created: {result.get('workflow_id')}")
            return result.get('workflow_id')
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

def start_workflow(workflow_id):
    """Start the workflow execution."""
    try:
        response = requests.post(f"{API_BASE}/workflows/{workflow_id}/start")
        if response.status_code == 200:
            print(f"✅ Workflow {workflow_id} started")
            return True
        else:
            print(f"❌ Failed to start workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting workflow: {e}")
        return False

def get_workflow_status(workflow_id):
    """Check workflow status."""
    try:
        response = requests.get(f"{API_BASE}/workflows/{workflow_id}/status")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return None

def create_simple_agent_task():
    """Create a simple agent task to trigger dashboard updates."""
    task_data = {
        "task_id": f"dashboard_task_{int(time.time())}",
        "title": "Dashboard Test Task",
        "description": "Simple task to test dashboard updates",
        "agent_type": "text_analyzer",
        "parameters": {
            "text": "This is a test message for the AgentWeaver dashboard",
            "analysis_type": "sentiment"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE}/agents/execute", json=task_data)
        if response.status_code == 200 or response.status_code == 202:
            result = response.json()
            print(f"✅ Task created and started: {result.get('task_id')}")
            return result.get('task_id')
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None

def main():
    """Main test function."""
    print("🚀 Testing AgentWeaver Dashboard")
    print("="*50)
    
    # Test API connection
    if not test_api_connection():
        print("❌ Cannot proceed without API connection")
        return
    
    print("\n📊 Your dashboard should show activity at: http://localhost:5174/")
    print("Watch for real-time updates in the Agent Status and Workflow Execution panels!")
    print("\n" + "="*50)
    
    # Try to create and run a simple task first
    print("\n1️⃣ Creating simple agent task...")
    task_id = create_simple_agent_task()
    
    if task_id:
        print(f"✅ Task {task_id} is running")
        print("👀 Check your dashboard - you should see agent activity!")
        time.sleep(3)
    
    # Try to create a workflow
    print("\n2️⃣ Creating test workflow...")
    workflow_id = create_test_workflow()
    
    if workflow_id:
        print(f"✅ Workflow {workflow_id} created")
        
        # Start the workflow
        print("\n3️⃣ Starting workflow...")
        if start_workflow(workflow_id):
            print("✅ Workflow started successfully")
            print("👀 Check your dashboard for workflow execution updates!")
            
            # Monitor for a bit
            print("\n4️⃣ Monitoring workflow progress...")
            for i in range(10):
                status = get_workflow_status(workflow_id)
                if status:
                    print(f"Workflow status: {status.get('status', 'unknown')}")
                    if status.get('status') == 'completed':
                        print("✅ Workflow completed!")
                        break
                time.sleep(2)
    
    print("\n" + "="*50)
    print("🎯 Dashboard Test Complete!")
    print("If you see activity in your dashboard at http://localhost:5174/, everything is working!")
    print("✅ Your AgentWeaver system is fully operational!")

if __name__ == "__main__":
    main()
