"""
Configuration API routes for Multi-Agent Agriculture Systems.
Provides endpoints for accessing configuration data.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional

from ..config.service import get_config, ConfigService
from ..config.frontend import generate_frontend_config

router = APIRouter(
    prefix="/api/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", summary="Get frontend configuration")
async def get_frontend_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """Get frontend configuration based on current environment."""
    return generate_frontend_config(environment)


@router.get("/regions", summary="Get available regions")
async def get_regions(config: ConfigService = Depends(get_config)) -> List[str]:
    """Get list of available regions."""
    return config.get_available_regions()


@router.get("/regions/{region_name}", summary="Get region configuration")
async def get_region_config(
    region_name: str, config: ConfigService = Depends(get_config)
) -> Dict[str, Any]:
    """Get configuration for a specific region."""
    # Save current region
    current_region = config.get_region_name()
    
    try:
        # Temporarily switch to requested region
        if region_name != current_region:
            if region_name not in config.get_available_regions():
                raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
            config.set_region(region_name)
        
        # Get region data
        region_data = config.get_region_data()
        return region_data
    finally:
        # Switch back to original region
        if region_name != current_region:
            config.set_region(current_region)


@router.put("/regions/{region_name}", summary="Set current region")
async def set_region(
    region_name: str, config: ConfigService = Depends(get_config)
) -> Dict[str, Any]:
    """Set the current region and return its configuration."""
    if region_name not in config.get_available_regions():
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    # Set the new region
    config.set_region(region_name)
    
    # Return the new configuration
    return {
        "region": region_name,
        "config": config.get_region_data()
    }
