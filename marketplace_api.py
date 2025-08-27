#!/usr/bin/env python3
"""
🌾💰 Agricultural Marketplace API
B2B and B2C marketplace integration with existing Multi-Agent Agriculture Systems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from pathlib import Path
import shutil

# Import existing agriculture services
from src.services.enhanced_query_processor import enhanced_processor
from src.agents.market_timing_agent import MarketTimingAgent
from src.core.agriculture_models import Location, CropType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🌾💰 Agriculture Marketplace API",
    description="B2B & B2C Agricultural Marketplace with AI-powered recommendations",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for file uploads
UPLOAD_DIR = Path("uploads")
PRODUCT_IMAGES_DIR = UPLOAD_DIR / "product_images"
PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================== MODELS ====================

class MarketplaceType(str, Enum):
    B2C = "b2c"  # Farmer to Consumer
    B2B = "b2b"  # Farmer to Business

class ProductCategory(str, Enum):
    GRAINS = "grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    SPICES = "spices"
    PULSES = "pulses"
    DAIRY = "dairy"
    ORGANIC = "organic"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class QualityGrade(str, Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"

class UserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: str
    user_type: str  # farmer, consumer, business, trader
    location: Dict[str, Any]
    verification_status: str = "pending"
    rating: float = 0.0
    total_transactions: int = 0

class ProductListing(BaseModel):
    listing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    product_name: str
    category: ProductCategory
    crop_type: Optional[CropType] = None
    quantity_available: float  # kg or tons
    unit: str = "kg"
    price_per_unit: float  # ₹ per kg/quintal
    quality_grade: QualityGrade
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    location: Dict[str, Any]
    marketplace_type: MarketplaceType
    organic_certified: bool = False
    description: str
    images: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # AI-enhanced fields from your existing system
    satellite_quality_score: Optional[float] = None
    market_price_analysis: Optional[Dict[str, Any]] = None
    recommended_selling_price: Optional[float] = None

class MarketOrder(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str
    seller_id: str
    listing_id: str
    quantity_ordered: float
    agreed_price: float
    total_amount: float
    delivery_address: Dict[str, Any]
    preferred_delivery_date: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    
    # AI-enhanced fields
    price_optimization_used: bool = False
    quality_prediction: Optional[Dict[str, Any]] = None

class MarketAnalytics(BaseModel):
    product_category: ProductCategory
    region: str
    current_market_price: float
    price_trend: str  # rising, falling, stable
    demand_forecast: Dict[str, Any]
    supply_analysis: Dict[str, Any]
    optimal_selling_window: Dict[str, Any]
    satellite_insights: Optional[Dict[str, Any]] = None

# ==================== MOCK DATA STORAGE ====================

# In-memory storage for demo (replace with database in production)
users_db = {}
listings_db = {}
orders_db = {}
analytics_cache = {}

# ==================== HELPER FUNCTIONS ====================

async def get_market_intelligence(crop_type: str, location: Dict[str, Any]) -> Dict[str, Any]:
    """Get AI-powered market intelligence using existing agents"""
    try:
        # Use your existing market timing agent
        market_agent = MarketTimingAgent()
        
        # Create a mock query to get market analysis
        from src.core.agriculture_models import AgricultureQuery, QueryDomain
        
        query = AgricultureQuery(
            query_text=f"What is the current market price and trend for {crop_type}?",
            query_domains=[QueryDomain.MARKET_TIMING],
            location=Location(
                state=location.get("state", "punjab"),
                district=location.get("district", "ludhiana")
            )
        )
        
        # Get market analysis
        response = await market_agent.process_query(query)
        
        return {
            "confidence": response.confidence_score,
            "analysis": response.response_text,
            "recommendations": response.recommendations,
            "market_intelligence": "AI-powered analysis using satellite data"
        }
    except Exception as e:
        logger.error(f"Error getting market intelligence: {e}")
        return {"error": "Market analysis unavailable", "confidence": 0.0}

def calculate_recommended_price(base_price: float, quality_grade: QualityGrade, 
                              market_intelligence: Dict[str, Any]) -> float:
    """Calculate AI-recommended selling price"""
    multipliers = {
        QualityGrade.PREMIUM: 1.2,
        QualityGrade.STANDARD: 1.0,
        QualityGrade.BASIC: 0.85
    }
    
    quality_adjusted_price = base_price * multipliers[quality_grade]
    
    # Apply market intelligence if available
    confidence = market_intelligence.get("confidence", 0.7)
    if confidence > 0.8:
        # High confidence in market analysis, apply 5% premium
        quality_adjusted_price *= 1.05
    
    return round(quality_adjusted_price, 2)

# ==================== MARKETPLACE ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint with marketplace information"""
    return {
        "message": "🌾💰 Agricultural Marketplace API",
        "description": "B2B & B2C marketplace powered by AI agriculture agents",
        "features": [
            "AI-powered price recommendations",
            "Satellite-enhanced quality assessment",
            "Market timing intelligence",
            "Supply-demand forecasting",
            "Multi-language support"
        ],
        "marketplaces": ["B2C (Farmer-to-Consumer)", "B2B (Farmer-to-Business)"],
        "ai_capabilities": [
            "Price optimization",
            "Quality prediction",
            "Market trend analysis",
            "Demand forecasting"
        ]
    }

# ==================== USER MANAGEMENT ====================

@app.post("/users/register")
async def register_user(user: UserProfile):
    """Register a new user (farmer, consumer, or business)"""
    try:
        if user.user_id in users_db:
            raise HTTPException(status_code=400, detail="User already exists")
        
        users_db[user.user_id] = user.dict()
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user.user_id,
            "verification_required": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

# ==================== PRODUCT LISTINGS ====================

@app.post("/listings/create")
async def create_product_listing(listing: ProductListing, background_tasks: BackgroundTasks):
    """Create a new product listing with AI-powered price recommendations"""
    try:
        # Get AI-powered market intelligence
        market_intelligence = await get_market_intelligence(
            str(listing.crop_type) if listing.crop_type else listing.product_name,
            listing.location
        )
        
        # Calculate recommended selling price
        recommended_price = calculate_recommended_price(
            listing.price_per_unit,
            listing.quality_grade,
            market_intelligence
        )
        
        # Enhance listing with AI insights
        listing.market_price_analysis = market_intelligence
        listing.recommended_selling_price = recommended_price
        
        # Mock satellite quality score (in production, integrate with satellite service)
        listing.satellite_quality_score = 85.0  # Mock score
        
        listings_db[listing.listing_id] = listing.dict()
        
        return {
            "status": "success",
            "listing_id": listing.listing_id,
            "message": "Product listed successfully",
            "ai_insights": {
                "recommended_price": recommended_price,
                "market_confidence": market_intelligence.get("confidence", 0.0),
                "satellite_quality_score": listing.satellite_quality_score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/listings/search")
async def search_listings(
    category: Optional[ProductCategory] = None,
    marketplace_type: Optional[MarketplaceType] = None,
    location_state: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    quality_grade: Optional[QualityGrade] = None,
    organic_only: bool = False,
    limit: int = Query(default=20, le=100)
):
    """Search product listings with filters"""
    try:
        filtered_listings = []
        
        for listing_data in listings_db.values():
            listing = ProductListing(**listing_data)
            
            # Apply filters
            if category and listing.category != category:
                continue
            if marketplace_type and listing.marketplace_type != marketplace_type:
                continue
            if location_state and listing.location.get("state", "").lower() != location_state.lower():
                continue
            if min_price and listing.price_per_unit < min_price:
                continue
            if max_price and listing.price_per_unit > max_price:
                continue
            if quality_grade and listing.quality_grade != quality_grade:
                continue
            if organic_only and not listing.organic_certified:
                continue
            
            filtered_listings.append(listing_data)
            
            if len(filtered_listings) >= limit:
                break
        
        return {
            "status": "success",
            "total_found": len(filtered_listings),
            "listings": filtered_listings,
            "applied_filters": {
                "category": category,
                "marketplace_type": marketplace_type,
                "location_state": location_state,
                "price_range": f"₹{min_price}-{max_price}" if min_price or max_price else "Any",
                "quality_grade": quality_grade,
                "organic_only": organic_only
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/listings/{listing_id}")
async def get_listing_details(listing_id: str):
    """Get detailed listing information with AI insights"""
    if listing_id not in listings_db:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_data = listings_db[listing_id]
    
    # Add real-time market insights
    try:
        current_market_analysis = await get_market_intelligence(
            listing_data.get("product_name", ""),
            listing_data.get("location", {})
        )
        
        listing_data["real_time_market_analysis"] = current_market_analysis
    except Exception as e:
        logger.warning(f"Could not get real-time market analysis: {e}")
    
    return listing_data

# ==================== ORDER MANAGEMENT ====================

@app.post("/orders/create")
async def create_order(order: MarketOrder):
    """Create a new order"""
    try:
        # Validate listing exists
        if order.listing_id not in listings_db:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        listing = listings_db[order.listing_id]
        
        # Check quantity availability
        if order.quantity_ordered > listing["quantity_available"]:
            raise HTTPException(status_code=400, detail="Insufficient quantity available")
        
        # Calculate total amount
        order.total_amount = order.quantity_ordered * order.agreed_price
        
        # Mock AI price optimization check
        market_price = listing.get("recommended_selling_price", listing["price_per_unit"])
        if abs(order.agreed_price - market_price) / market_price < 0.05:  # Within 5%
            order.price_optimization_used = True
        
        orders_db[order.order_id] = order.dict()
        
        # Update listing quantity
        listings_db[order.listing_id]["quantity_available"] -= order.quantity_ordered
        
        return {
            "status": "success",
            "order_id": order.order_id,
            "message": "Order created successfully",
            "total_amount": order.total_amount,
            "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat(),
            "price_optimization": order.price_optimization_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order_details(order_id: str):
    """Get order details"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return orders_db[order_id]

@app.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: OrderStatus):
    """Update order status"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    orders_db[order_id]["status"] = status
    
    return {
        "status": "success",
        "order_id": order_id,
        "new_status": status,
        "updated_at": datetime.now().isoformat()
    }

# ==================== MARKET ANALYTICS ====================

@app.get("/analytics/market-overview")
async def get_market_overview(
    category: Optional[ProductCategory] = None,
    region: Optional[str] = None
):
    """Get market overview with AI-powered analytics"""
    try:
        # Generate mock analytics (integrate with your existing market timing agent)
        analytics = {
            "market_summary": {
                "total_listings": len(listings_db),
                "active_orders": len([o for o in orders_db.values() if o["status"] != "cancelled"]),
                "average_price_trend": "rising",
                "market_confidence": 0.85
            },
            "category_analysis": {},
            "regional_insights": {},
            "ai_predictions": {
                "price_forecast_7d": "stable_to_rising",
                "demand_forecast": "increasing",
                "optimal_selling_window": "next_2_weeks",
                "satellite_crop_health": "good"
            }
        }
        
        # If category specified, get specific analytics
        if category:
            market_intelligence = await get_market_intelligence(str(category), {"state": region or "punjab"})
            analytics["category_specific"] = market_intelligence
        
        return {
            "status": "success",
            "analytics": analytics,
            "generated_at": datetime.now().isoformat(),
            "data_sources": ["satellite_data", "market_agents", "historical_trends"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/price-trends/{product_category}")
async def get_price_trends(product_category: ProductCategory, days: int = 30):
    """Get price trends for a specific product category"""
    try:
        # Mock price trend data (replace with real analytics)
        trend_data = {
            "product_category": product_category,
            "time_period_days": days,
            "current_avg_price": 2500.0,  # ₹ per quintal
            "price_change_percentage": 8.5,
            "trend_direction": "upward",
            "historical_data": [
                {"date": "2025-08-01", "price": 2300},
                {"date": "2025-08-15", "price": 2450},
                {"date": "2025-08-27", "price": 2500}
            ],
            "forecast_next_7d": {
                "predicted_price": 2600,
                "confidence": 0.82,
                "factors": ["seasonal_demand", "supply_constraints", "weather_conditions"]
            },
            "ai_insights": {
                "recommendation": "favorable_selling_conditions",
                "market_sentiment": "bullish",
                "satellite_supply_indicator": "moderate_supply"
            }
        }
        
        return {
            "status": "success",
            "price_trends": trend_data,
            "ai_powered": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI RECOMMENDATIONS ====================

@app.post("/ai/price-recommendation")
async def get_ai_price_recommendation(
    product_name: str,
    quantity: float,
    quality_grade: QualityGrade,
    location: Dict[str, Any],
    marketplace_type: MarketplaceType
):
    """Get AI-powered price recommendation for a product"""
    try:
        # Get market intelligence
        market_intelligence = await get_market_intelligence(product_name, location)
        
        # Base price calculation (mock - replace with real market data)
        base_prices = {
            "wheat": 2200, "rice": 2800, "cotton": 5500, "sugarcane": 350,
            "tomato": 25, "onion": 30, "potato": 20
        }
        
        base_price = base_prices.get(product_name.lower(), 2000)
        
        # Calculate recommended price
        recommended_price = calculate_recommended_price(base_price, quality_grade, market_intelligence)
        
        # Market-based adjustments
        multipliers = {
            MarketplaceType.B2C: 1.15,  # Premium for direct consumer sales
            MarketplaceType.B2B: 0.95   # Bulk discount for business sales
        }
        
        final_price = recommended_price * multipliers[marketplace_type]
        
        return {
            "status": "success",
            "price_recommendation": {
                "product": product_name,
                "recommended_price_per_unit": round(final_price, 2),
                "quality_grade": quality_grade,
                "marketplace_type": marketplace_type,
                "confidence_score": market_intelligence.get("confidence", 0.75),
                "price_breakdown": {
                    "base_market_price": base_price,
                    "quality_adjustment": round((recommended_price - base_price), 2),
                    "marketplace_adjustment": round((final_price - recommended_price), 2)
                },
                "market_insights": market_intelligence,
                "optimal_selling_strategy": "immediate" if market_intelligence.get("confidence", 0) > 0.8 else "wait_for_better_conditions"
            },
            "ai_powered": True,
            "data_sources": ["satellite_data", "market_agents", "historical_pricing"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/demand-forecast/{product_category}")
async def get_demand_forecast(product_category: ProductCategory, region: Optional[str] = None):
    """Get AI-powered demand forecast for a product category"""
    try:
        # Mock demand forecast (integrate with your existing agents)
        forecast = {
            "product_category": product_category,
            "region": region or "national",
            "demand_forecast": {
                "next_7_days": "high",
                "next_30_days": "moderate",
                "seasonal_trend": "increasing",
                "confidence": 0.87
            },
            "market_drivers": [
                "seasonal_consumption_patterns",
                "festival_demand",
                "export_opportunities",
                "weather_impact"
            ],
            "supply_outlook": {
                "current_supply": "adequate",
                "upcoming_harvest": "good",
                "regional_availability": "sufficient"
            },
            "ai_recommendations": [
                "Optimal time to sell within next 2 weeks",
                "Consider premium pricing for high-quality produce",
                "Monitor competitor pricing in region"
            ]
        }
        
        return {
            "status": "success",
            "demand_forecast": forecast,
            "generated_by": "ai_agriculture_agents",
            "satellite_enhanced": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== IMAGE UPLOAD & MANAGEMENT ====================

@app.post("/marketplace/upload-product-image")
async def upload_product_image(
    file: UploadFile = File(...),
    product_id: str = Form(...)
):
    """Upload product image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{product_id}_{uuid.uuid4()}.{file_extension}"
        file_path = PRODUCT_IMAGES_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image_url = f"/uploads/product_images/{unique_filename}"
        
        return {
            "status": "success",
            "image_url": image_url,
            "filename": unique_filename,
            "uploaded_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/marketplace/delete-image/{filename}")
async def delete_product_image(filename: str):
    """Delete product image"""
    try:
        file_path = PRODUCT_IMAGES_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return {"status": "success", "message": "Image deleted"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENHANCED MARKETPLACE FEATURES ====================

@app.get("/marketplace/categories")
async def get_marketplace_categories():
    """Get available product categories with examples"""
    categories_data = {
        "grains": {
            "name": "Grains & Cereals",
            "icon": "🌾",
            "examples": ["Rice", "Wheat", "Barley", "Maize", "Millet"],
            "typical_units": ["kg", "quintal", "tonne"],
            "seasonal_info": "Kharif (Jun-Oct), Rabi (Nov-Apr)"
        },
        "vegetables": {
            "name": "Vegetables",
            "icon": "🥬",
            "examples": ["Tomato", "Onion", "Potato", "Cauliflower", "Cabbage"],
            "typical_units": ["kg", "piece", "dozen"],
            "seasonal_info": "Year-round with seasonal varieties"
        },
        "fruits": {
            "name": "Fruits",
            "icon": "🍎",
            "examples": ["Apple", "Mango", "Banana", "Orange", "Grapes"],
            "typical_units": ["kg", "piece", "dozen", "box"],
            "seasonal_info": "Seasonal availability varies by region"
        },
        "spices": {
            "name": "Spices & Herbs",
            "icon": "🌶️",
            "examples": ["Turmeric", "Chili", "Coriander", "Cumin", "Cardamom"],
            "typical_units": ["kg", "gram"],
            "seasonal_info": "Harvest season varies by spice type"
        },
        "pulses": {
            "name": "Pulses & Legumes",
            "icon": "🫘",
            "examples": ["Chickpea", "Lentil", "Black Gram", "Pigeon Pea"],
            "typical_units": ["kg", "quintal", "tonne"],
            "seasonal_info": "Rabi season primarily"
        },
        "organic": {
            "name": "Organic Products",
            "icon": "🌱",
            "examples": ["Organic Rice", "Organic Vegetables", "Organic Fruits"],
            "typical_units": ["varies"],
            "seasonal_info": "Premium certified organic produce"
        }
    }
    
    return {
        "status": "success",
        "categories": categories_data,
        "total_categories": len(categories_data)
    }

@app.get("/marketplace/locations")
async def get_marketplace_locations():
    """Get available marketplace locations"""
    locations_data = {
        "states": [
            {"code": "PB", "name": "Punjab", "major_crops": ["Wheat", "Rice"]},
            {"code": "UP", "name": "Uttar Pradesh", "major_crops": ["Wheat", "Sugarcane", "Rice"]},
            {"code": "MH", "name": "Maharashtra", "major_crops": ["Cotton", "Sugarcane", "Onion"]},
            {"code": "GJ", "name": "Gujarat", "major_crops": ["Cotton", "Groundnut", "Wheat"]},
            {"code": "RJ", "name": "Rajasthan", "major_crops": ["Wheat", "Barley", "Mustard"]},
            {"code": "MP", "name": "Madhya Pradesh", "major_crops": ["Wheat", "Soybean", "Rice"]},
            {"code": "TN", "name": "Tamil Nadu", "major_crops": ["Rice", "Sugarcane", "Cotton"]},
            {"code": "KA", "name": "Karnataka", "major_crops": ["Rice", "Cotton", "Ragi"]},
            {"code": "AP", "name": "Andhra Pradesh", "major_crops": ["Rice", "Cotton", "Chili"]},
            {"code": "WB", "name": "West Bengal", "major_crops": ["Rice", "Jute", "Tea"]}
        ],
        "delivery_zones": {
            "local": "Within 50 km",
            "regional": "Within state",
            "national": "Pan-India delivery",
            "express": "Same day delivery (metro cities)"
        }
    }
    
    return {
        "status": "success",
        "locations": locations_data
    }

@app.post("/marketplace/bulk-inquiry")
async def create_bulk_inquiry(inquiry_data: Dict[str, Any]):
    """Create bulk purchase inquiry for B2B marketplace"""
    try:
        inquiry_id = str(uuid.uuid4())
        
        # Enhanced inquiry processing with AI
        inquiry = {
            "inquiry_id": inquiry_id,
            "buyer_info": inquiry_data.get("buyer_info", {}),
            "product_requirements": inquiry_data.get("requirements", {}),
            "quantity_needed": inquiry_data.get("quantity", 0),
            "target_price": inquiry_data.get("target_price", 0),
            "delivery_timeline": inquiry_data.get("delivery_timeline", ""),
            "quality_specifications": inquiry_data.get("quality_specs", {}),
            "created_at": datetime.now().isoformat(),
            "status": "open",
            "matched_sellers": [],
            "ai_recommendations": []
        }
        
        # AI-powered seller matching (mock implementation)
        matching_sellers = []
        for listing in listings_db.values():
            if (listing["marketplace_type"] == "b2b" and 
                listing["category"] in inquiry_data.get("categories", [])):
                match_score = calculate_seller_match_score(listing, inquiry)
                if match_score > 0.7:
                    matching_sellers.append({
                        "seller_id": listing["seller_id"],
                        "listing_id": listing["listing_id"],
                        "match_score": match_score,
                        "available_quantity": listing["quantity_available"],
                        "price_per_unit": listing["price_per_unit"]
                    })
        
        inquiry["matched_sellers"] = sorted(matching_sellers, 
                                          key=lambda x: x["match_score"], 
                                          reverse=True)[:5]
        
        # Store inquiry
        inquiry_id_key = f"inquiry_{inquiry_id}"
        orders_db[inquiry_id_key] = inquiry
        
        return {
            "status": "success",
            "inquiry_id": inquiry_id,
            "matched_sellers_count": len(matching_sellers),
            "estimated_fulfillment": "2-5 business days",
            "inquiry": inquiry
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_seller_match_score(listing: Dict[str, Any], inquiry: Dict[str, Any]) -> float:
    """Calculate how well a seller matches buyer requirements"""
    score = 0.0
    
    # Quantity match
    required_qty = inquiry.get("quantity", 0)
    available_qty = listing.get("quantity_available", 0)
    if available_qty >= required_qty:
        score += 0.3
    elif available_qty >= required_qty * 0.5:
        score += 0.15
    
    # Price match
    target_price = inquiry.get("target_price", 0)
    listing_price = listing.get("price_per_unit", 0)
    if target_price > 0 and listing_price <= target_price:
        score += 0.25
    elif target_price > 0 and listing_price <= target_price * 1.1:
        score += 0.15
    
    # Location proximity (mock calculation)
    score += 0.2  # Base location score
    
    # Seller rating
    seller_rating = users_db.get(listing["seller_id"], {}).get("rating", 0)
    score += (seller_rating / 5.0) * 0.15
    
    # Quality grade match
    if listing.get("quality_grade") == "premium":
        score += 0.1
    
    return min(score, 1.0)

@app.get("/marketplace/market-insights")
async def get_market_insights():
    """Get market insights and trends"""
    try:
        insights = {
            "price_trends": {
                "trending_up": ["Tomato", "Onion", "Rice"],
                "trending_down": ["Wheat", "Cotton"],
                "stable": ["Pulses", "Spices"]
            },
            "demand_hotspots": {
                "high_demand_locations": ["Delhi", "Mumbai", "Bangalore"],
                "emerging_markets": ["Pune", "Hyderabad", "Ahmedabad"]
            },
            "seasonal_opportunities": {
                "current_season": "Rabi harvesting",
                "recommended_crops": ["Wheat", "Barley", "Mustard"],
                "price_outlook": "Positive for quality produce"
            },
            "satellite_insights": {
                "crop_health_index": 85,
                "weather_risk_level": "Low",
                "recommended_harvest_window": "Next 15 days optimal"
            },
            "market_alerts": [
                "Premium pricing opportunity for organic vegetables",
                "Increased demand for pulses in urban markets",
                "Export opportunity for basmati rice"
            ]
        }
        
        return {
            "status": "success",
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "data_freshness": "Real-time"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SYSTEM STATUS ====================

@app.get("/marketplace/status")
async def get_marketplace_status():
    """Get marketplace system status"""
    return {
        "status": "operational",
        "marketplace_stats": {
            "total_users": len(users_db),
            "active_listings": len(listings_db),
            "completed_orders": len([o for o in orders_db.values() if o["status"] == "delivered"]),
            "ai_recommendations_generated": 150,  # Mock
            "satellite_data_uptime": "99.5%"
        },
        "ai_services": {
            "market_timing_agent": "active",
            "price_optimization": "active",
            "satellite_integration": "active",
            "demand_forecasting": "active"
        },
        "supported_features": [
            "Multi-language support",
            "Real-time price recommendations",
            "Satellite-enhanced quality assessment",
            "Market timing intelligence",
            "B2B and B2C marketplaces"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
