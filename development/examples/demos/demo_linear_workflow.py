
import sys
import os
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.linear_workflow import LinearWorkflowOrchestrator


def run_demo_workflow():
    print("🚀 AgentWeaver Linear Workflow Demo")
    print("=" * 60)
    
    # Initialize the orchestrator
    print("📋 Initializing workflow orchestrator...")
    orchestrator = LinearWorkflowOrchestrator()
    
    # Check orchestrator status
    status = orchestrator.get_workflow_status()
    print(f"✅ Orchestrator ready: {status['available_agents']} agents available")
    print(f"   Agents: {list(status['agent_status'].keys())}")
    print()
    
    # Demo data - realistic content analysis scenario
    demo_input = {
        "numbers": [87, 92, 89, 94, 91, 88, 95, 90, 93, 86, 89, 92],  # Customer satisfaction scores
        "metadata": {
            "source": "customer_feedback_q1_2024",
            "domain": "product_analysis",
            "priority": "high",
            "analyst": "demo_system"
        }
    }
    
    print("📊 Demo Input Summary:")
    print(f"   • Text length: {len(demo_input['text'])} characters")
    print(f"   • Satisfaction scores: {len(demo_input['numbers'])} data points")
    print(f"   • Average score: {sum(demo_input['numbers'])/len(demo_input['numbers']):.1f}%")
    print()
    
    # Execute the workflow
    print("🔄 Executing linear workflow...")
    print("   Step 1: Text Analysis → Step 2: Data Enrichment → Step 3: Statistical Processing")
    print()
    
    start_time = datetime.utcnow()
    result = orchestrator.execute_workflow(demo_input, "demo_workflow_2024")
    end_time = datetime.utcnow()
    
    # Display results
    execution_time = (end_time - start_time).total_seconds()
    print(f"⏱️  Workflow completed in {execution_time:.2f} seconds")
    print()
    
    if result.get("status") == "completed":
        print("✅ Workflow executed successfully!")
        print()
        
        # Show workflow summary
        final_result = result.get("final_result", {})
        workflow_summary = final_result.get("workflow_summary", {})
        
        # Text Analysis Results
        print("📝 Step 1 - Text Analysis Results:")
        text_analysis = workflow_summary.get("text_analysis", {})
        if text_analysis:
            print(f"   • Analysis type: {text_analysis.get('analysis_type', 'N/A')}")
            if 'word_count' in text_analysis:
                print(f"   • Word count: {text_analysis['word_count']}")
            if 'summary' in text_analysis:
                print(f"   • Summary: {text_analysis['summary'][:100]}...")
        print()
        
        # Data Enrichment Results
        print("🌐 Step 2 - Data Enrichment Results:")
        enrichment = workflow_summary.get("data_enrichment", {})
        if enrichment.get("external_data"):
            ext_data = enrichment["external_data"]
            print(f"   • API call successful: {ext_data.get('success', False)}")
            print(f"   • Response time: {ext_data.get('execution_time', 0):.3f}s")
            print(f"   • Status code: {ext_data.get('status_code', 'N/A')}")
        print()
        
        # Statistical Analysis Results
        print("📈 Step 3 - Statistical Analysis Results:")
        statistics = workflow_summary.get("statistical_analysis", {})
        if statistics.get("statistics"):
            stats = statistics["statistics"]
            print(f"   • Mean satisfaction: {stats.get('mean', 0):.1f}%")
            print(f"   • Median satisfaction: {stats.get('median', 0):.1f}%")
            print(f"   • Standard deviation: {stats.get('std_dev', 0):.2f}")
            print(f"   • Min/Max: {stats.get('min', 0):.1f}% / {stats.get('max', 0):.1f}%")
        print()
        
        # Execution Metrics
        print("📊 Execution Metrics:")
        execution_metrics = final_result.get("execution_metrics", {})
        if execution_metrics:
            print(f"   • Total steps completed: {execution_metrics.get('steps_completed', 0)}")
            print(f"   • Workflow execution time: {execution_metrics.get('total_execution_time', 0):.2f}s")
            print(f"   • Final status: {execution_metrics.get('workflow_status', 'unknown')}")
        
        # Step completion details
        completed_steps = result.get("completed_steps", [])
        print(f"   • Completed workflow steps: {', '.join(completed_steps)}")
        print()
        
        # Save results to file
        output_file = "demo_workflow_results.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"💾 Results saved to {output_file}")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
    
    else:
        print("❌ Workflow failed!")
        print(f"   Error: {result.get('error_message', 'Unknown error')}")
        print(f"   Failed at step: {result.get('error_step', 'Unknown step')}")
        
        # Show partial results if available
        if result.get("final_result", {}).get("partial_data"):
            print("   📋 Partial results available:")
            partial = result["final_result"]["partial_data"]
            if partial.get("step1_data"):
                print("     • Step 1 (Text Analysis): ✅ Completed")
            if partial.get("step2_data"):
                print("     • Step 2 (Data Enrichment): ✅ Completed")
    
    print()
    print("=" * 60)
    print("🎯 Demo completed! This showcases:")
    print("   • Multi-agent coordination through LangGraph")
    print("   • Comprehensive error handling and recovery")
    print("   • Data flow between specialized worker agents")
    print("   • End-to-end workflow orchestration")
    print("   • Real-time monitoring and result tracking")


def run_error_handling_demo():
    print("\n🚨 Error Handling Demo")
    print("=" * 40)
    
    orchestrator = LinearWorkflowOrchestrator()
    
    # Test with minimal input that might cause issues
    error_input = {
        "text": "x",  # Too short for analysis
        "numbers": [],  # Empty data
        "metadata": {"test": "error_scenario"}
    }
    
    print("🧪 Testing with problematic input:")
    print("   • Text: Very short (1 character)")
    print("   • Numbers: Empty array")
    print()
    
    result = orchestrator.execute_workflow(error_input, "error_demo")
    
    if result.get("status") == "failed":
        print("✅ Error handling working correctly!")
        print(f"   • Error detected at: {result.get('error_step')}")
        print(f"   • Error message: {result.get('error_message')}")
        
        # Show what was completed before the error
        completed = result.get("completed_steps", [])
        if completed:
            print(f"   • Steps completed before error: {', '.join(completed)}")
    else:
        print("🤔 Workflow completed despite problematic input")
        print("   (This shows robust input handling)")


if __name__ == "__main__":
    # Run the main demo
    run_demo_workflow()
    
    # Run error handling demo
    run_error_handling_demo()
    
    print("\n🏁 All demos completed!")
    print("Check the AgentWeaver linear workflow implementation in src/linear_workflow.py")
    print("Run tests with: python test_linear_workflow.py")
