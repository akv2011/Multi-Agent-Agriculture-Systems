#!/usr/bin/env python3
"""
Ground Search Example

This script demonstrates how to use the ground search service directly,
without going through the agent system. It allows testing the ground search
functionality with different agricultural queries.

Usage:
  python ground_search_example.py "What is the current MSP for wheat in India?"

Requirements:
  - GEMINI_API_KEY or GOOGLE_API_KEY environment variable
  - GOOGLE_SEARCH_CX environment variable
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the ground search service
from src.services.ground_search_service import create_ground_search_service


def print_boxed(text, width=100):
    """Print text in a box"""
    print("┌" + "─" * width + "┐")
    
    # Split the text into lines and print each one
    lines = text.split("\n")
    for line in lines:
        # Print the line with padding
        if len(line) > width:
            # Wrap long lines
            while line:
                part = line[:width]
                print("│" + part.ljust(width) + "│")
                line = line[width:]
        else:
            print("│" + line.ljust(width) + "│")
    
    print("└" + "─" * width + "┘")


def print_sources(sources, width=100):
    """Print sources in a formatted way"""
    print("\n🔍 SOURCES:")
    print("─" * width)
    
    for i, source in enumerate(sources, 1):
        title = source.get('title', 'Unknown Source')
        link = source.get('link', 'No URL')
        source_name = source.get('source', '')
        note = source.get('note', '')
        
        print(f"{i}. {title}")
        print(f"   URL: {link}")
        if source_name:
            print(f"   Source: {source_name}")
        if note:
            print(f"   Note: {note}")
        print()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the ground search service with agricultural queries")
    
    parser.add_argument("query", type=str, help="Query to search for")
    parser.add_argument("--language", type=str, default="en", help="Language code (default: en)")
    parser.add_argument("--country", type=str, default="in", help="Country code (default: in)")
    parser.add_argument("--results", type=int, default=5, help="Number of search results to use (default: 5)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get API keys from environment
    gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    google_search_api_key = os.environ.get("GOOGLE_SEARCH_API_KEY") or gemini_api_key
    google_search_cx = os.environ.get("GOOGLE_SEARCH_CX")
    
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        return 1
    
    if not google_search_cx:
        print("ERROR: GOOGLE_SEARCH_CX environment variable must be set")
        return 1
    
    # Create the ground search service
    ground_service = create_ground_search_service(
        gemini_api_key=gemini_api_key,
        google_search_api_key=google_search_api_key,
        google_search_cx=google_search_cx
    )
    
    # Sample context for agricultural queries
    context = {
        "location": "India",
        "crop_type": "wheat",
        "soil_type": "black soil",
        "season": "rabi"
    }
    
    print(f"\n📋 QUERY: {args.query}")
    print(f"📍 Context: {context}")
    print(f"🔎 Searching with {args.results} results in {args.language} for {args.country}...\n")
    
    # Get the start time
    start_time = datetime.now()
    
    # Perform the grounded search
    result = await ground_service.ground_query(
        query=args.query,
        context=context,
        num_search_results=args.results,
        language=args.language,
        country=args.country
    )
    
    # Calculate execution time
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Print the result
    print("\n🌾 GROUNDED RESPONSE:")
    print_boxed(result.content)
    
    # Print sources
    print_sources(result.sources)
    
    # Print stats
    print(f"\n📊 STATS:")
    print(f"- Query: \"{args.query}\"")
    print(f"- Sources: {len(result.sources)}")
    print(f"- Confidence: {result.confidence_score:.2f}")
    print(f"- Time: {execution_time:.2f} seconds")
    print(f"- Timestamp: {result.timestamp}")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
