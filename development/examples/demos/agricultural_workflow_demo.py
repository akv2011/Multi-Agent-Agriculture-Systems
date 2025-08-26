"""
Agricultural Workflow Demo

This script demonstrates how to use the agricultural workflow system to create and execute
different types of agricultural workflows, including irrigation scheduling, crop health monitoring,
and pest management.
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime, timedelta
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
import time

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflows.agricultural_workflow_service import (
    AgriculturalWorkflow,
    WorkflowStep,
    WorkflowExecutionEngine,
    WorkflowStatus,
    StepStatus
)

# Initialize rich console
console = Console()

# Workflow templates
WORKFLOW_TEMPLATES = {
    "irrigation": {
        "name": "Precision Irrigation Workflow",
        "description": "Schedule and execute precision irrigation based on soil moisture, weather forecast, and crop water needs",
        "steps": [
            {
                "name": "Collect Soil Moisture Data",
                "agent": "sensor-data-agent",
                "description": "Gather data from soil moisture sensors across fields",
                "parameters": {"sensorGroups": ["field_A", "field_B"], "depth": "30cm"}
            },
            {
                "name": "Fetch Weather Forecast",
                "agent": "weather-agent",
                "description": "Retrieve 5-day weather forecast with precipitation and temperature data",
                "parameters": {"daysAhead": 5, "includeHourly": True}
            },
            {
                "name": "Calculate Crop Water Requirements",
                "agent": "crop-analysis-agent",
                "description": "Determine water needs based on crop type, growth stage, and environmental conditions",
                "parameters": {"cropTypes": ["corn", "soybeans"], "growthStages": ["V6", "R2"]}
            },
            {
                "name": "Optimize Irrigation Schedule",
                "agent": "optimization-agent",
                "description": "Create an optimal irrigation schedule to maximize water efficiency",
                "parameters": {"optimizationGoal": "water_efficiency", "constraints": {"maxDuration": "8h"}}
            },
            {
                "name": "Generate Control Commands",
                "agent": "irrigation-control-agent",
                "description": "Generate specific commands for the irrigation system",
                "parameters": {"controllerType": "precision_sprinkler", "zoneMapping": {"A": [1, 2, 3], "B": [4, 5]}}
            },
            {
                "name": "Execute Irrigation Plan",
                "agent": "system-integration-agent",
                "description": "Send commands to the irrigation system and verify execution",
                "parameters": {"executionMode": "scheduled", "notification": True}
            }
        ]
    },
    "crop_health": {
        "name": "Crop Health Monitoring Workflow",
        "description": "Monitor crop health using satellite and drone imagery, combined with ground sensors",
        "steps": [
            {
                "name": "Collect Satellite Imagery",
                "agent": "satellite-data-agent",
                "description": "Obtain the latest satellite imagery for the farm",
                "parameters": {"sources": ["sentinel-2", "landsat-8"], "cloudCoverMax": 10}
            },
            {
                "name": "Deploy Drone Mission",
                "agent": "drone-fleet-agent",
                "description": "Plan and execute drone flights to capture detailed imagery",
                "parameters": {"flightPattern": "grid", "resolution": "high", "altitude": "30m"}
            },
            {
                "name": "Process Multispectral Data",
                "agent": "image-processing-agent",
                "description": "Process and combine satellite and drone imagery",
                "parameters": {"indices": ["NDVI", "NDRE", "MSAVI"], "resolution": "5m"}
            },
            {
                "name": "Analyze Vegetation Health",
                "agent": "crop-health-agent",
                "description": "Analyze vegetation indices to determine crop health status",
                "parameters": {"thresholds": {"NDVI": 0.7}, "zonify": True}
            },
            {
                "name": "Generate Health Maps",
                "agent": "mapping-agent",
                "description": "Create detailed crop health maps with recommendations",
                "parameters": {"mapTypes": ["health", "stress", "growth"], "format": "geojson"}
            },
            {
                "name": "Identify Management Zones",
                "agent": "zone-management-agent",
                "description": "Identify and characterize management zones for variable-rate applications",
                "parameters": {"minZoneSize": "0.25ha", "maxZones": 5}
            },
            {
                "name": "Create Treatment Recommendations",
                "agent": "recommendation-agent",
                "description": "Generate treatment recommendations for identified issues",
                "parameters": {"includeProducts": True, "costAnalysis": True}
            }
        ]
    },
    "pest_management": {
        "name": "Integrated Pest Management Workflow",
        "description": "Detect, identify, and manage pest issues with minimal environmental impact",
        "steps": [
            {
                "name": "Collect Trap Data",
                "agent": "sensor-data-agent",
                "description": "Collect data from insect monitoring traps",
                "parameters": {"trapIds": ["T001", "T002", "T003", "T004"], "timeframe": "72h"}
            },
            {
                "name": "Process Field Images",
                "agent": "image-processing-agent",
                "description": "Process images from field cameras and drone surveys",
                "parameters": {"imageTypes": ["RGB", "thermal"], "processingLevel": "detailed"}
            },
            {
                "name": "Detect Pest Presence",
                "agent": "pest-detection-agent",
                "description": "Analyze data to detect presence of pests",
                "parameters": {"detectionThreshold": 0.75, "pestTypes": ["aphids", "caterpillars", "beetles"]}
            },
            {
                "name": "Identify Pest Species",
                "agent": "species-identification-agent",
                "description": "Identify specific pest species present in the fields",
                "parameters": {"confidenceThreshold": 0.8, "useDatabase": True}
            },
            {
                "name": "Assess Infestation Severity",
                "agent": "assessment-agent",
                "description": "Determine the severity and distribution of the infestation",
                "parameters": {"severityLevels": ["low", "moderate", "high", "critical"]}
            },
            {
                "name": "Generate Treatment Options",
                "agent": "treatment-planning-agent",
                "description": "Create list of potential treatment strategies",
                "parameters": {"treatmentTypes": ["biological", "chemical", "cultural"], "organicPreference": True}
            },
            {
                "name": "Evaluate Environmental Impact",
                "agent": "environmental-agent",
                "description": "Assess environmental impact of each treatment option",
                "parameters": {"factors": ["water", "soil", "biodiversity", "residue"]}
            },
            {
                "name": "Select Optimal Strategy",
                "agent": "decision-agent",
                "description": "Select the optimal treatment strategy based on effectiveness and impact",
                "parameters": {"weightEffectiveness": 0.6, "weightEnvironmental": 0.4}
            },
            {
                "name": "Create Implementation Plan",
                "agent": "planning-agent",
                "description": "Create detailed implementation plan for the selected strategy",
                "parameters": {"timing": "optimal", "includeMaterials": True, "equipmentNeeds": True}
            }
        ]
    }
}


async def create_workflow(engine, workflow_type, field_id):
    """Create a workflow from a template."""
    if workflow_type not in WORKFLOW_TEMPLATES:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
        
    template = WORKFLOW_TEMPLATES[workflow_type]
    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"
    
    workflow = AgriculturalWorkflow(
        workflow_id=workflow_id,
        name=f"{template['name']} - {field_id}",
        description=template['description'],
        metadata={
            "type": workflow_type,
            "fieldId": field_id,
            "createdAt": datetime.now().isoformat(),
            "priority": random.choice(["low", "medium", "high"]),
            "requestedBy": random.choice(["Field Manager", "Agronomist", "Farm Owner"]),
        }
    )
    
    for i, step_template in enumerate(template['steps']):
        # Clone the parameters so we don't modify the template
        parameters = step_template['parameters'].copy()
        
        # Add field-specific information to parameters
        parameters["fieldId"] = field_id
        
        workflow.add_step(WorkflowStep(
            step_id=f"step-{i+1}",
            name=step_template['name'],
            agent=step_template['agent'],
            description=step_template['description'],
            parameters=parameters
        ))
    
    engine.register_workflow(workflow)
    return workflow


async def display_workflow_progress(engine, workflow_id):
    """Display workflow progress in a nice UI using rich."""
    workflow = engine.get_workflow(workflow_id)
    if not workflow:
        console.print(f"[bold red]Workflow {workflow_id} not found[/bold red]")
        return
    
    title = f"[bold cyan]{workflow.name}[/bold cyan]"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        # Overall workflow progress
        workflow_task = progress.add_task(f"[bold]Overall Progress[/bold]", total=100)
        
        # Step progress tasks
        step_tasks = {}
        for step in workflow.steps:
            description = f"Step {step.id}: {step.name}"
            step_task = progress.add_task(description, total=100, start=False)
            step_tasks[step.id] = step_task
            
        # Update progress while workflow is running
        while True:
            # Refresh workflow data
            workflow = engine.get_workflow(workflow_id)
            
            # Update overall progress
            progress.update(workflow_task, completed=int(workflow.progress * 100))
            
            # Update step progress
            for step in workflow.steps:
                step_progress = 0
                if step.status == StepStatus.COMPLETED:
                    step_progress = 100
                elif step.status == StepStatus.IN_PROGRESS:
                    step_progress = 50  # Simplistic but works for demo
                elif step.status == StepStatus.FAILED:
                    step_progress = 100  # Mark as complete even though it failed
                    
                if step_progress > 0 and not progress.started(step_tasks[step.id]):
                    progress.start_task(step_tasks[step.id])
                    
                progress.update(step_tasks[step.id], completed=step_progress)
            
            # Check if workflow is complete
            if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                break
                
            await asyncio.sleep(0.5)
        
    # Display workflow results
    console.print(Panel(f"Workflow {workflow.id} finished with status: [bold]{workflow.status}[/bold]"))
    
    # Display step details
    table = Table(title="Workflow Steps")
    table.add_column("Step", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="bold")
    table.add_column("Agent", style="blue")
    table.add_column("Duration", style="magenta")
    
    for i, step in enumerate(workflow.steps):
        status_style = {
            StepStatus.COMPLETED: "green",
            StepStatus.FAILED: "red",
            StepStatus.IN_PROGRESS: "yellow",
            StepStatus.PENDING: "dim",
            StepStatus.SKIPPED: "dim"
        }.get(step.status, "")
        
        duration = "N/A"
        if step.duration is not None:
            duration = f"{step.duration / 1000:.1f}s"
            
        table.add_row(
            str(i+1),
            step.name,
            f"[{status_style}]{step.status}[/{status_style}]",
            step.agent,
            duration
        )
    
    console.print(table)
    
    # If the workflow has outputs, display them
    has_outputs = any(step.output for step in workflow.steps)
    if has_outputs:
        console.print("\n[bold]Step Outputs:[/bold]")
        for step in workflow.steps:
            if step.output:
                console.print(Panel(
                    step.output,
                    title=f"[blue]{step.name}[/blue]",
                    border_style="green" if step.status == StepStatus.COMPLETED else "red"
                ))


async def run_demo():
    """Run the agricultural workflow demo."""
    console.print(Panel.fit(
        "[bold yellow]Agricultural Workflow System Demo[/bold yellow]\n"
        "This demo showcases the workflow system for agricultural operations",
        border_style="yellow"
    ))
    
    # Create workflow engine
    engine = WorkflowExecutionEngine()
    
    # Ask the user which workflow to run
    workflow_options = list(WORKFLOW_TEMPLATES.keys())
    console.print("\n[bold]Available workflow types:[/bold]")
    
    for i, wf_type in enumerate(workflow_options):
        template = WORKFLOW_TEMPLATES[wf_type]
        console.print(f"[green]{i+1}.[/green] {template['name']}")
        console.print(f"   {template['description']}")
        console.print(f"   [dim]Steps: {len(template['steps'])}[/dim]\n")
    
    try:
        choice = int(input("\nSelect workflow type (1-3): ")) - 1
        if choice < 0 or choice >= len(workflow_options):
            raise ValueError("Invalid selection")
        
        selected_workflow_type = workflow_options[choice]
        field_id = input("Enter field ID (e.g., Field-A-23): ")
        if not field_id:
            field_id = f"Field-{uuid.uuid4().hex[:4].upper()}"
            console.print(f"Using generated field ID: [bold]{field_id}[/bold]")
        
        console.print(f"\nCreating [bold cyan]{WORKFLOW_TEMPLATES[selected_workflow_type]['name']}[/bold cyan] for field [bold]{field_id}[/bold]")
        
        # Create the workflow
        workflow = await create_workflow(engine, selected_workflow_type, field_id)
        
        # Start workflow execution
        console.print(f"\nStarting workflow execution (ID: [bold]{workflow.id}[/bold])...")
        asyncio.create_task(engine.execute_workflow(workflow.id))
        
        # Display progress
        await display_workflow_progress(engine, workflow.id)
        
        # Get final workflow state
        final_workflow = engine.get_workflow(workflow.id)
        
        # Export workflow data to JSON file
        output_dir = os.path.join(os.path.dirname(__file__), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"workflow_{workflow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, "w") as f:
            json.dump(final_workflow.to_dict(), f, indent=2)
            
        console.print(f"\nWorkflow data exported to [bold]{output_file}[/bold]")
        
    except (ValueError, IndexError) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Demo cancelled by user[/bold yellow]")
        return


if __name__ == "__main__":
    asyncio.run(run_demo())
