import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import Environment
from .service import get_config


def setup_cors(app: FastAPI) -> None:
    """Configure CORS for the FastAPI application based on settings."""
    config = get_config()
    
    origins = config.get_cors_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def generate_frontend_config(env: str = None) -> dict:
    """
    Generate frontend configuration based on environment.
    
    This creates a configuration object that can be exposed to the frontend
    through an API endpoint or embedded in HTML.
    """
    config = get_config()
    
    if env is None:
        # Use the current environment if not specified
        if config.is_development_mode():
            env = "development"
        elif config.is_staging_mode():
            env = "staging"
        else:
            env = "production"
    
    # Create a safe subset of configuration for frontend
    frontend_config = {
        "apiUrl": config.get_api_url(),
        "wsUrl": config.get_ws_url(),
        "environment": env,
        "version": config.legacy_settings.APP_VERSION,
        "demoMode": config.legacy_settings.DEMO_MODE,
        "regions": config.get_available_regions(),
        "currentRegion": config.get_region_name(),
        "features": {
            "satellite": True,
            "finance": True,
            "pests": True,
            "irrigation": True,
            "multilingual": True,
        }
    }
    
    return frontend_config


def save_frontend_config(output_dir: str = None, env: str = None) -> str:
    """
    Save frontend configuration to a JSON file for deployment.
    
    Args:
        output_dir: Directory to save the config file (default: frontend/public)
        env: Environment to generate config for (default: current environment)
        
    Returns:
        Path to the saved config file
    """
    config = get_config()
    
    if env is None:
        if config.is_production_mode():
            env = "production"
        elif config.is_staging_mode():
            env = "staging"
        else:
            env = "development"
    
    if output_dir is None:
        # Default to frontend/public directory
        base_dir = Path(config.settings.BASE_DIR)
        output_dir = base_dir / "frontend" / "public"
    else:
        output_dir = Path(output_dir)
    
    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate frontend config
    frontend_config = generate_frontend_config(env)
    
    # Save to file
    output_file = output_dir / f"config.{env}.json"
    with open(output_file, "w") as f:
        json.dump(frontend_config, f, indent=2)
    
    return str(output_file)
