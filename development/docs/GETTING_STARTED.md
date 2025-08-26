# 🚀 Getting Started Guide

## Prerequisites

Before setting up the Multi-Agent Agriculture Systems, ensure you have:

- **Python 3.9+** installed
- **Node.js 16+** (for frontend development)
- **Git** for version control
- **Gemini API Key** for AI processing

## Quick Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/akv2011/Multi-Agent-Agriculture-Systems.git
cd Multi-Agent-Agriculture-Systems

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp config/.env.example .env

# Edit .env file with your API keys
# Required: GEMINI_API_KEY
# Optional: Other service API keys
```

### 3. Run the Application

```bash
# Start the main API server
python main.py

# In a separate terminal, test the system
python tests/test_integrated_system.py
```

### 4. Access the Application

- **Main API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Development Workflow

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific agent tests
python tests/test_agriculture_agents.py
python tests/test_satellite_integration.py

# Run integration tests
python tests/test_integrated_system.py
```

### Using the Agents

```bash
# Test individual agents
python tests/test_market_timing_agent.py
python tests/test_finance_agent.py

# Test satellite integration
python tests/test_satellite_system.py
```

### Development Demos

```bash
# Run demonstration scripts
python scripts/demos/satellite_demo.py
python scripts/demos/simple_agent_demo.py
```

## Project Structure Overview

```
Multi-Agent-Agriculture-Systems/
├── src/                    # Core application code
│   ├── agents/            # AI agricultural agents
│   ├── api/               # FastAPI routes and models
│   ├── core/              # Core utilities and models
│   ├── services/          # External service integrations
│   └── workflows/         # Agent orchestration
├── tests/                 # Test suite
├── docs/                  # Documentation
├── frontend/              # Web interface (React)
├── scripts/               # Utilities and demos
├── config/                # Configuration files
└── main.py               # Application entry point
```

## Next Steps

1. **Test the System**: Run the test suite to verify everything works
2. **Explore Agents**: Try different agricultural queries with the agents
3. **Review Documentation**: Check out the detailed docs in `/docs/`
4. **Contribute**: See the main README for contribution guidelines

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the project root and virtual environment is activated
2. **API Key Errors**: Verify your `.env` file has the correct API keys
3. **Port Conflicts**: Default port is 8000, change in `main.py` if needed

### Getting Help

- Check the [comprehensive documentation](PROJECT_STATUS_COMPREHENSIVE_SUMMARY.md)
- Review [satellite system details](SATELLITE_SYSTEM_SUMMARY.md)
- See [Gemini integration guide](GEMINI_INTEGRATION_SUMMARY.md)
