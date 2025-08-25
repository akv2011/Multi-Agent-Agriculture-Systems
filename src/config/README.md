# Configuration Management System

This directory contains the comprehensive configuration management system for the Multi-Agent Agriculture Systems project.

## Overview

The configuration system provides a centralized way to manage all application settings, supporting:

1. **Environment-based configuration** (development, staging, production)
2. **Region-specific configuration** (different Indian states)
3. **Centralized access** through a singleton ConfigService

## Directory Structure

```
config/
├── __init__.py          # Exports the configuration components
├── README.md           # This documentation file
├── core.py             # Core Settings class and environment functionality
├── service.py          # ConfigService singleton implementation
├── settings.py         # Legacy settings implementation (will be phased out)
├── environments/       # Environment-specific configuration files
│   ├── development.json
│   ├── staging.json
│   └── production.json
└── regions/            # Region-specific configuration files
    ├── punjab.json
    ├── karnataka.json
    └── maharashtra.json
```

## Usage

### Basic Usage

```python
from src.config import get_config

# Get the configuration service
config = get_config()

# Access environment-based settings
api_host = config.get("API_HOST")
api_port = config.get("API_PORT")

# Access region-specific settings
region_name = config.get_region_name()
major_crops = config.get_region_data("agriculture_data.major_crops")

# Get convenience URLs
api_url = config.get_api_url()
ws_url = config.get_ws_url()

# Check environment
if config.is_development_mode():
    print("Running in development mode")
```

### Switching Regions

```python
from src.config import get_config

config = get_config()

# List available regions
regions = config.get_available_regions()
print(f"Available regions: {regions}")

# Switch to a different region
config.set_region("punjab")
print(f"Current region: {config.get_region_name()}")

# Get region-specific data
market_centers = config.get_region_data("market_centers")
```

### Direct Settings Access

For type-safe access to base settings:

```python
from src.config import get_config

config = get_config()

# Get the base settings object with type safety
settings = config.settings

# Access settings properties
base_dir = settings.BASE_DIR
data_dir = settings.DATA_DIR
```

## Environment Variables

The configuration system supports loading settings from environment variables:

- `APP_ENV`: The application environment (development, staging, production)
- `API_HOST`: The API server host
- `API_PORT`: The API server port
- `REGION`: The default region to load

## JSON Configuration Files

### Environment Files

Environment-specific JSON files contain settings for each environment:
- `environments/development.json`
- `environments/staging.json`
- `environments/production.json`

### Region Files

Region-specific JSON files contain agricultural data for each region:
- `regions/punjab.json`
- `regions/karnataka.json`
- `regions/maharashtra.json`

## Legacy Support

The system maintains backward compatibility with the older settings module:

```python
from src.config import settings

# Legacy settings access
database_url = settings.DATABASE_URL
```
