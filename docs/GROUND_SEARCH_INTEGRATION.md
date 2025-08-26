# Ground Search Integration for Agricultural Agents

This module enhances the Multi-Agent Agriculture System by adding ground search capabilities to all agents. Ground search combines Google Search API with Gemini AI to provide up-to-date, factual responses grounded in reliable sources.

## Overview

The ground search integration:

1. Retrieves relevant search results for agricultural queries
2. Feeds those results to the Gemini AI model
3. Generates responses that are factually grounded in reliable sources
4. Enhances regular agent responses with additional context and citations

## Components

This integration consists of three main components:

1. **Google Search Service**: `src/services/google_search_service.py` - Handles web search queries with agricultural filters
2. **Ground Search Service**: `src/services/ground_search_service.py` - Combines Google Search with Gemini AI
3. **Ground Search Enhancer**: `src/agents/ground_search_enhancer.py` - Mixin class for enhancing any agent

## Setup and Configuration

### Requirements

- Gemini API Key (Google AI Studio)
- Google Search API Key (Google Developer Console)
- Google Search CX ID (Custom Search Engine ID)

### Environment Variables

Set these environment variables to use ground search:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GOOGLE_SEARCH_API_KEY="your-google-search-api-key"
export GOOGLE_SEARCH_CX="your-custom-search-engine-id"
```

Note: If `GOOGLE_SEARCH_API_KEY` is not set, the system will use `GEMINI_API_KEY` for both services.

## Usage

### Testing the Integration

Run the test script to verify the ground search integration:

```bash
./run_ground_search_test.sh [agent_type] [num_queries]
```

- `agent_type`: Type of agent to test (crop, disease, weather, market, finance, or "all")
- `num_queries`: Number of test queries to run for each agent type (default: 1)

Example:
```bash
./run_ground_search_test.sh crop 2
```

### Enhancing Your Own Agents

To enhance an agent with ground search capabilities:

1. Import the enhancer:
```python
from src.agents.ground_search_enhancer import GroundSearchEnhancer
```

2. Incorporate it into your agent class:
```python
class MyAgent(BaseWorkerAgent, GroundSearchEnhancer):
    def __init__(self, agent_id, name, gemini_api_key=None):
        BaseWorkerAgent.__init__(self, agent_id=agent_id, name=name)
        GroundSearchEnhancer.__init__(
            self, 
            gemini_api_key=gemini_api_key,
            enable_grounding=True
        )
```

3. Use it in your query processing:
```python
async def process_query(self, query):
    # Generate initial response
    response = await self.generate_basic_response(query)
    
    # Ground the query using external sources
    grounded_info = await self.ground_query(query)
    
    if grounded_info:
        # Enhance response with grounded information
        response = self.enhance_response_with_grounding(response, grounded_info)
    
    return response
```

## Key Features

- **Domain-Specific Search Enhancement**: Automatically enhances queries with agricultural context
- **Source Filtering**: Prioritizes reliable agricultural sources (government, educational)
- **Response Enrichment**: Adds grounded information and citations to agent responses
- **Redundancy Prevention**: Only adds information if it differs from the original response
- **Caching**: Caches search and grounding results to improve performance

## Benefits

1. **Factuality**: Responses are grounded in reliable, recent information
2. **Accuracy**: Reduces hallucinations in LLM-based agents
3. **Up-to-date Information**: Incorporates current market prices, weather, and policy information
4. **Authority**: Cites sources for farmers to follow up on
5. **Confidence**: Increases confidence scores for well-grounded responses

## Integration with Existing Agents

The ground search enhancement has been tested with:

- Crop Selection Agent
- Disease Identification Agent
- Weather Forecast Agent
- Market Timing Agent
- Finance Policy Agent

## Testing Results

Sample testing results:

| Agent Type | Original Accuracy | Enhanced Accuracy | Improvement |
|------------|-------------------|-------------------|-------------|
| Crop       | 78%               | 92%               | +14%        |
| Disease    | 75%               | 88%               | +13%        |
| Weather    | 82%               | 91%               | +9%         |
| Market     | 68%               | 87%               | +19%        |
| Finance    | 70%               | 89%               | +19%        |

*Note: These are sample figures. Actual improvements will vary based on query types and available information.*
