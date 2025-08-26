"""
Integration test for Agricultural Workflow Service

This test verifies that the agricultural workflow execution engine works correctly
and properly executes the steps with the appropriate agents.
"""

import asyncio
import unittest
import json
import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflows.agricultural_workflow_service import (
    AgriculturalWorkflow,
    WorkflowStep,
    WorkflowExecutionEngine,
    WorkflowStatus,
    StepStatus
)


class MockAgent:
    """Mock agent class for testing"""
    
    def __init__(self, agent_id, behavior='normal'):
        self.agent_id = agent_id
        self.behavior = behavior  # 'normal', 'slow', 'error'
        self.execution_count = 0
    
    async def execute(self, parameters):
        self.execution_count += 1
        
        # Simulate processing time
        delay = 0.1  # Fast for testing
        if self.behavior == 'slow':
            delay = 0.5
            
        await asyncio.sleep(delay)
        
        # Simulate error if needed
        if self.behavior == 'error':
            raise Exception(f"Simulated error in agent {self.agent_id}")
            
        return {
            "output": f"Agent {self.agent_id} executed successfully (call #{self.execution_count})",
            "results": {
                "timestamp": datetime.now().isoformat(),
                "parameters_received": parameters,
                "agent_id": self.agent_id
            }
        }


class TestAgriculturalWorkflowService(unittest.TestCase):
    """Test cases for the Agricultural Workflow Service"""
    
    def setUp(self):
        # Create a workflow execution engine
        self.engine = WorkflowExecutionEngine()
        
        # Set up mock agents
        self.mock_agents = {
            "soil-sensor-agent": MockAgent("soil-sensor-agent"),
            "weather-agent": MockAgent("weather-agent"),
            "crop-analysis-agent": MockAgent("crop-analysis-agent"),
            "irrigation-planning-agent": MockAgent("irrigation-planning-agent", behavior='slow'),
            "error-agent": MockAgent("error-agent", behavior='error')
        }
        
        # Replace the _simulate_agent_execution method with our test version
        self.engine._simulate_agent_execution = self._mock_agent_execution
    
    async def _mock_agent_execution(self, agent_id, parameters):
        """Mock agent execution using our test agents"""
        if agent_id not in self.mock_agents:
            raise ValueError(f"Unknown agent: {agent_id}")
            
        return await self.mock_agents[agent_id].execute(parameters)
    
    async def _run_test_workflow(self, include_error=False):
        """Helper to create and run a test workflow"""
        # Create a test workflow
        workflow = AgriculturalWorkflow(
            workflow_id="test-workflow-1",
            name="Test Irrigation Workflow",
            description="Test workflow for irrigation scheduling",
            metadata={"test": True, "type": "irrigation"}
        )
        
        # Add workflow steps
        workflow.add_step(WorkflowStep(
            step_id="step-1",
            name="Read Soil Moisture Data",
            agent="soil-sensor-agent",
            parameters={"field_id": "F1", "depth_cm": 30}
        ))
        
        workflow.add_step(WorkflowStep(
            step_id="step-2",
            name="Fetch Weather Forecast",
            agent="weather-agent",
            parameters={"days": 5, "location": "Field-1-Center"}
        ))
        
        workflow.add_step(WorkflowStep(
            step_id="step-3",
            name="Calculate Crop Water Needs",
            agent="crop-analysis-agent",
            parameters={"crop": "corn", "stage": "vegetative", "field_id": "F1"}
        ))
        
        workflow.add_step(WorkflowStep(
            step_id="step-4",
            name="Generate Irrigation Schedule",
            agent="irrigation-planning-agent",
            parameters={"optimization": "water_efficiency"}
        ))
        
        if include_error:
            workflow.add_step(WorkflowStep(
                step_id="step-5",
                name="Error Step",
                agent="error-agent",
                parameters={"should_fail": True}
            ))
            
        # Register workflow
        self.engine.register_workflow(workflow)
        
        # Execute workflow
        task = asyncio.create_task(self.engine.execute_workflow(workflow.id))
        
        # Wait for completion (with timeout)
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            self.fail("Workflow execution timed out")
            
        # Return the completed workflow
        return self.engine.get_workflow(workflow.id)
    
    async def test_successful_workflow_execution(self):
        """Test that a workflow executes successfully"""
        workflow = await self._run_test_workflow(include_error=False)
        
        # Check workflow status
        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)
        self.assertEqual(workflow.progress, 1.0)
        self.assertIsNotNone(workflow.start_time)
        self.assertIsNotNone(workflow.end_time)
        self.assertIsNotNone(workflow.total_duration)
        
        # Check that all steps completed
        for step in workflow.steps:
            self.assertEqual(step.status, StepStatus.COMPLETED)
            self.assertIsNotNone(step.output)
            self.assertIsNone(step.error)
            self.assertIsNotNone(step.start_time)
            self.assertIsNotNone(step.end_time)
            self.assertIsNotNone(step.duration)
        
        # Verify step order
        steps_order = [step.name for step in workflow.steps]
        expected_order = [
            "Read Soil Moisture Data",
            "Fetch Weather Forecast",
            "Calculate Crop Water Needs",
            "Generate Irrigation Schedule"
        ]
        self.assertEqual(steps_order, expected_order)
        
        # Check agent execution
        self.assertEqual(self.mock_agents["soil-sensor-agent"].execution_count, 1)
        self.assertEqual(self.mock_agents["weather-agent"].execution_count, 1)
        self.assertEqual(self.mock_agents["crop-analysis-agent"].execution_count, 1)
        self.assertEqual(self.mock_agents["irrigation-planning-agent"].execution_count, 1)
    
    async def test_failed_workflow_execution(self):
        """Test that a workflow fails correctly when a step fails"""
        workflow = await self._run_test_workflow(include_error=True)
        
        # Check workflow status
        self.assertEqual(workflow.status, WorkflowStatus.FAILED)
        self.assertEqual(workflow.progress, 0.8)  # 4 out of 5 steps completed
        
        # Check that the error step failed
        error_step = workflow.steps[-1]
        self.assertEqual(error_step.status, StepStatus.FAILED)
        self.assertIsNotNone(error_step.error)
        self.assertIn("Simulated error", error_step.error)
        
        # Verify previous steps completed
        for step in workflow.steps[:-1]:
            self.assertEqual(step.status, StepStatus.COMPLETED)
    
    async def test_workflow_cancellation(self):
        """Test that a workflow can be cancelled"""
        # Create and register workflow
        workflow = AgriculturalWorkflow(
            workflow_id="test-cancel-workflow",
            name="Test Cancellation Workflow",
            description="Test workflow cancellation",
        )
        
        # Add multiple slow steps
        for i in range(5):
            workflow.add_step(WorkflowStep(
                step_id=f"step-{i+1}",
                name=f"Slow Step {i+1}",
                agent="irrigation-planning-agent",  # Using our slow agent
                parameters={"iteration": i}
            ))
        
        self.engine.register_workflow(workflow)
        
        # Start workflow execution
        task = asyncio.create_task(self.engine.execute_workflow(workflow.id))
        
        # Wait a moment for execution to begin
        await asyncio.sleep(0.3)
        
        # Cancel the workflow
        result = await self.engine.cancel_workflow(workflow.id)
        self.assertTrue(result)
        
        # Wait for the task to complete
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except asyncio.TimeoutError:
            self.fail("Workflow cancellation timed out")
        
        # Check workflow status
        workflow = self.engine.get_workflow(workflow.id)
        self.assertEqual(workflow.status, WorkflowStatus.CANCELLED)
        
        # Check that at least one step executed but not all
        completed_steps = [s for s in workflow.steps if s.status == StepStatus.COMPLETED]
        pending_steps = [s for s in workflow.steps if s.status == StepStatus.PENDING]
        
        self.assertGreater(len(completed_steps), 0)
        self.assertGreater(len(pending_steps), 0)
        
    async def test_workflow_serialization(self):
        """Test that workflows serialize to JSON correctly"""
        workflow = await self._run_test_workflow()
        
        # Convert to dict and then to JSON
        workflow_dict = workflow.to_dict()
        workflow_json = json.dumps(workflow_dict)
        
        # Parse back from JSON
        parsed_dict = json.loads(workflow_json)
        
        # Verify key properties
        self.assertEqual(parsed_dict["id"], workflow.id)
        self.assertEqual(parsed_dict["name"], workflow.name)
        self.assertEqual(parsed_dict["status"], workflow.status)
        self.assertEqual(len(parsed_dict["steps"]), len(workflow.steps))
        
        # Check step data
        for i, step in enumerate(workflow.steps):
            parsed_step = parsed_dict["steps"][i]
            self.assertEqual(parsed_step["id"], step.id)
            self.assertEqual(parsed_step["name"], step.name)
            self.assertEqual(parsed_step["status"], step.status)


def run_tests():
    """Run the tests using asyncio"""
    async def run_async_tests():
        test_cases = [
            TestAgriculturalWorkflowService("test_successful_workflow_execution"),
            TestAgriculturalWorkflowService("test_failed_workflow_execution"),
            TestAgriculturalWorkflowService("test_workflow_cancellation"),
            TestAgriculturalWorkflowService("test_workflow_serialization")
        ]
        
        for test_case in test_cases:
            print(f"Running test: {test_case._testMethodName}")
            await getattr(test_case, test_case._testMethodName)()
            print(f"✓ {test_case._testMethodName}")
    
    asyncio.run(run_async_tests())
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
