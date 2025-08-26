# AgentWeaver Examples

This directory contains working example scripts and demonstrations for the AgentWeaver multi-agent system.

## Working Demos

All demos in this directory have been tested and are working with the current system:

### Dashboard Demos (Show Real-Time Updates)
- **`dashboard_demo.py`** - ⭐ **BEST DEMO** - Triggers multiple workflows to show live dashboard updates
- **`trigger_demo.py`** - Simple single workflow trigger for testing dashboard connectivity

### Agent System Demos  
- **`simple_agent_demo.py`** - Demonstrates real agent execution and workflow processing (works independently)

## Running the Examples

1. **Start your AgentWeaver server:**
   ```bash
   python main.py
   ```

2. **Start your frontend dashboard:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Run the main dashboard demo:**
   ```bash
   python examples/demos/dashboard_demo.py
   ```

4. **Watch your browser at `http://localhost:3000` for real-time updates!**

## What You'll See

When you run `dashboard_demo.py`, your dashboard will show:
- ✅ Agent status changes (idle → busy → idle)  
- ✅ Workflow progress bars moving
- ✅ Real-time WebSocket connectivity status
- ✅ Live agent data replacing mock data
- ✅ Multiple workflows executing in sequence

## Requirements

- AgentWeaver server running on `localhost:8000`
- Frontend dashboard running on `localhost:3000` 
- All dependencies from `requirements.txt` installed

## Troubleshooting

If demos fail:
- Make sure the server is running: `python main.py`
- Check the server responds: `curl http://localhost:8000/health`
- Verify frontend is running: Open `http://localhost:3000`
