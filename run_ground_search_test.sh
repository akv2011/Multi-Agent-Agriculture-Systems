#!/usr/bin/env bash
# Run Ground Search Integration Tests
# This script sets up the necessary environment variables and runs the ground search integration tests

# Set bold text formatting
BOLD=$(tput bold)
NORMAL=$(tput sgr0)
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "${BOLD}${GREEN}=== GROUND SEARCH INTEGRATION TEST ===${NC}${NORMAL}"
echo "This script will test the ground search integration with agricultural agents."

# Check if API keys are provided as arguments or in environment
if [ -z "$GEMINI_API_KEY" ]; then
    echo "${YELLOW}GEMINI_API_KEY not found in environment.${NC}"
    read -p "Please enter your Gemini API key: " GEMINI_API_KEY
    export GEMINI_API_KEY=$GEMINI_API_KEY
    echo "GEMINI_API_KEY has been set for this session."
else
    echo "Using GEMINI_API_KEY from environment."
fi

if [ -z "$GOOGLE_SEARCH_CX" ]; then
    echo "${YELLOW}GOOGLE_SEARCH_CX not found in environment.${NC}"
    read -p "Please enter your Google Search CX ID: " GOOGLE_SEARCH_CX
    export GOOGLE_SEARCH_CX=$GOOGLE_SEARCH_CX
    echo "GOOGLE_SEARCH_CX has been set for this session."
else
    echo "Using GOOGLE_SEARCH_CX from environment."
fi

# Set Google Search API key to same as Gemini if not provided
if [ -z "$GOOGLE_SEARCH_API_KEY" ]; then
    export GOOGLE_SEARCH_API_KEY=$GEMINI_API_KEY
    echo "Using GEMINI_API_KEY for GOOGLE_SEARCH_API_KEY."
fi

echo ""
echo "${BOLD}Configuration:${NORMAL}"
echo "- GEMINI_API_KEY: ${GEMINI_API_KEY:0:5}...${GEMINI_API_KEY:(-5)}"
echo "- GOOGLE_SEARCH_CX: ${GOOGLE_SEARCH_CX:0:5}...${GOOGLE_SEARCH_CX:(-5)}"
echo ""

# Determine which agents to test
if [ -z "$1" ]; then
    # Default to testing one agent with one query for quick testing
    AGENT_ARG="crop"
    QUERIES=1
    echo "No agent specified. Testing crop agent with 1 query."
else
    AGENT_ARG="$1"
    # Get number of queries from the second argument or default to 1
    QUERIES="${2:-1}"
    echo "Testing $AGENT_ARG agent(s) with $QUERIES queries each."
fi

echo ""
echo "${BOLD}${GREEN}Running test...${NC}${NORMAL}"
echo ""

# Make the test script executable if it isn't already
chmod +x test_ground_search_integration.py

# Run the test script
./test_ground_search_integration.py --agents $AGENT_ARG --queries $QUERIES --output "results_ground_search_$(date +%Y%m%d%H%M%S).json"

# Check the result
if [ $? -eq 0 ]; then
    echo ""
    echo "${BOLD}${GREEN}Test completed successfully!${NC}${NORMAL}"
    echo "Results have been saved to a JSON file in the project root."
else
    echo ""
    echo "${BOLD}${YELLOW}Test encountered errors.${NC}${NORMAL}"
    echo "Please check the log output above for details."
fi
