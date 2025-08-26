# Archive Directory

This directory contains archived files from the Multi-Agent Agriculture Systems project that are no longer actively used but kept for reference.

## Structure

### old_apis/
Contains legacy API implementations that have been superseded by the unified API:
- business_intelligence_api.py - Old standalone business intelligence API
- farmer_profile_api.py - Old standalone farmer profile API  
- marketplace_api.py - Old standalone marketplace API
- enhanced_demo_api.py - Enhanced demo API (deprecated)
- simple_demo_api.py - Simple demo API (deprecated)
- marketplace_api_standalone.py - Standalone marketplace implementation

### old_demos/
Contains old demo files and examples:
- agrisens_demo.py - Original AgriSens demonstration
- demo.py - General system demo
- demo_ground_search.py - Ground search demo
- Various other demo and example files

### old_tests/
Contains legacy test files and verification scripts:
- Multiple test_*.py files for various components
- check_*.py files for system verification
- verify_*.py files for integration testing

## Current Active Files

The main project now uses:
- unified_agricultural_api.py - Single unified API server
- main.py - Main application entry point
- setup.py - Project setup configuration

## Migration Notes

All functionality from the archived APIs has been consolidated into the unified API system. The archived files are kept for reference and potential future features extraction.
