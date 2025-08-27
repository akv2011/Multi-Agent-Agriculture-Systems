#!/usr/bin/env python3
"""
🌾💰 Standalone Agricultural Marketplace API
B2B and B2C marketplace with mock data for demonstration
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from pathlib import Path
import shutil
import json

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
    B2C = "b2c"
    B2B = "b2b"

class ProductCategory(str, Enum):
    GRAINS = "grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    SPICES = "spices"
    PULSES = "pulses"
    ORGANIC = "organic"

class SellerProfile(BaseModel):
    seller_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    rating: float = Field(ge=0.0, le=5.0)
    verified: bool = False
    total_sales: int = 0

class ProductListing(BaseModel):
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: ProductCategory
    price: float
    unit: str
    stock: int
    seller: SellerProfile
    images: List[str] = []
    is_organic: bool = False
    harvest_date: Optional[str] = None
    marketplace_type: MarketplaceType
    specifications: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)

class MarketStats(BaseModel):
    total_products: int
    active_sellers: int
    todays_orders: int
    avg_price: float

# ==================== MOCK DATABASE ====================

# Sample data
sample_sellers = [
    SellerProfile(
        seller_id="seller_1",
        name="Rajesh Kumar",
        location="Ludhiana, Punjab",
        rating=4.8,
        verified=True,
        total_sales=150
    ),
    SellerProfile(
        seller_id="seller_2", 
        name="Sunita Farms",
        location="Meerut, UP",
        rating=4.9,
        verified=True,
        total_sales=89
    ),
    SellerProfile(
        seller_id="seller_3",
        name="Green Valley Farm",
        location="Nashik, Maharashtra", 
        rating=4.6,
        verified=True,
        total_sales=200
    ),
    SellerProfile(
        seller_id="seller_4",
        name="Maharashtra Cotton Co-op",
        location="Aurangabad, Maharashtra",
        rating=4.7,
        verified=True,
        total_sales=50
    )
]

sample_products = [
    ProductListing(
        product_id="prod_1",
        name="Premium Basmati Rice",
        description="High-quality aged Basmati rice from Punjab fields",
        category=ProductCategory.GRAINS,
        price=85.0,
        unit="kg",
        stock=500,
        seller=sample_sellers[0],
        images=["/images/basmati-rice.jpg", "/images/rice-field.jpg"],
        is_organic=False,
        harvest_date="2024-11-15",
        marketplace_type=MarketplaceType.B2C,
        specifications={
            "variety": "Pusa Basmati 1121",
            "grade": "Grade A",
            "moisture": 12,
            "purity": 99
        }
    ),
    ProductListing(
        product_id="prod_2",
        name="Organic Wheat Flour",
        description="Freshly ground organic wheat flour, pesticide-free",
        category=ProductCategory.GRAINS,
        price=45.0,
        unit="kg",
        stock=200,
        seller=sample_sellers[1],
        images=["/images/wheat-field.jpg", "/images/wheat-flour.jpg"],
        is_organic=True,
        harvest_date="2024-12-01",
        marketplace_type=MarketplaceType.B2C,
        specifications={
            "variety": "Sharbati Wheat",
            "grade": "Premium",
            "moisture": 10,
            "purity": 98
        }
    ),
    ProductListing(
        product_id="prod_3",
        name="Fresh Tomatoes",
        description="Farm-fresh tomatoes, perfect for cooking and salads",
        category=ProductCategory.VEGETABLES,
        price=35.0,
        unit="kg",
        stock=150,
        seller=sample_sellers[2],
        images=["/images/tomatoes.jpg", "/images/tomato-farm.jpg"],
        is_organic=False,
        harvest_date="2024-12-20",
        marketplace_type=MarketplaceType.B2C,
        specifications={
            "variety": "Hybrid Tomato",
            "grade": "Grade A"
        }
    ),
    ProductListing(
        product_id="prod_4",
        name="Bulk Cotton",
        description="Premium quality cotton for textile manufacturing",
        category=ProductCategory.GRAINS,
        price=65000.0,
        unit="tonne",
        stock=50,
        seller=sample_sellers[3],
        images=["/images/cotton-bulk.jpg", "/images/cotton-field.jpg"],
        is_organic=False,
        harvest_date="2024-11-30",
        marketplace_type=MarketplaceType.B2B,
        specifications={
            "variety": "Bt Cotton",
            "grade": "Premium",
            "moisture": 8,
            "purity": 96
        }
    )
]

# In-memory storage
products_db = {product.product_id: product for product in sample_products}
sellers_db = {seller.seller_id: seller for seller in sample_sellers}

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "🌾💰 Agricultural Marketplace API",
        "version": "1.0.0",
        "status": "operational",
        "features": ["B2B Marketplace", "B2C Marketplace", "AI Recommendations", "Image Upload"]
    }

@app.get("/marketplace/products")
async def get_products(
    marketplace_type: Optional[str] = None,
    category: Optional[str] = None,
    organic_only: Optional[bool] = False,
    search: Optional[str] = None
):
    """Get marketplace products with filtering"""
    filtered_products = list(products_db.values())
    
    # Apply filters
    if marketplace_type:
        filtered_products = [p for p in filtered_products if p.marketplace_type.value == marketplace_type]
    
    if category:
        filtered_products = [p for p in filtered_products if p.category.value == category]
    
    if organic_only:
        filtered_products = [p for p in filtered_products if p.is_organic]
    
    if search:
        search_lower = search.lower()
        filtered_products = [
            p for p in filtered_products 
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    
    return {
        "status": "success",
        "products": filtered_products,
        "total": len(filtered_products),
        "filters_applied": {
            "marketplace_type": marketplace_type,
            "category": category,
            "organic_only": organic_only,
            "search": search
        }
    }

@app.get("/marketplace/products/{product_id}")
async def get_product(product_id: str):
    """Get specific product details"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "status": "success",
        "product": products_db[product_id]
    }

@app.post("/marketplace/products")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    category: ProductCategory = Form(...),
    price: float = Form(...),
    unit: str = Form(...),
    stock: int = Form(...),
    seller_id: str = Form(...),
    is_organic: bool = Form(False),
    harvest_date: Optional[str] = Form(None),
    marketplace_type: MarketplaceType = Form(MarketplaceType.B2C),
    specifications: str = Form("{}"),  # JSON string
    images: List[UploadFile] = File([])
):
    """Create new product listing with image upload support"""
    try:
        # Generate product ID
        product_id = str(uuid.uuid4())
        
        # Get seller information
        seller = sellers_db.get(seller_id)
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Handle image uploads
        image_urls = []
        if images and len(images) > 0 and images[0].filename:  # Check if files were actually uploaded
            for image in images:
                if image.content_type and image.content_type.startswith('image/'):
                    # Generate unique filename
                    file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
                    unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
                    file_path = PRODUCT_IMAGES_DIR / unique_filename
                    
                    # Save file
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(image.file, buffer)
                    
                    image_urls.append(f"/uploads/product_images/{unique_filename}")
        
        # Parse specifications
        try:
            specs_dict = json.loads(specifications) if specifications != "{}" else {}
        except json.JSONDecodeError:
            specs_dict = {}
        
        # Create product listing
        product = ProductListing(
            product_id=product_id,
            name=name,
            description=description,
            category=category,
            price=price,
            unit=unit,
            stock=stock,
            seller=seller,
            images=image_urls,
            is_organic=is_organic,
            harvest_date=harvest_date,
            marketplace_type=marketplace_type,
            specifications=specs_dict
        )
        
        # Store in database
        products_db[product_id] = product
        
        return {
            "status": "success",
            "message": "Product created successfully",
            "product_id": product_id,
            "product": product,
            "images_uploaded": len(image_urls)
        }
    
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.get("/marketplace/sellers")
async def get_sellers():
    """Get all sellers"""
    return {
        "status": "success",
        "sellers": list(sellers_db.values())
    }

@app.post("/marketplace/sellers")
async def create_seller(
    name: str = Form(...),
    location: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None)
):
    """Create new seller profile"""
    seller_id = f"seller_{uuid.uuid4().hex[:8]}"
    
    seller = SellerProfile(
        seller_id=seller_id,
        name=name,
        location=location,
        rating=4.0,  # Default rating
        verified=False,  # Will be verified later
        total_sales=0
    )
    
    sellers_db[seller_id] = seller
    
    return {
        "status": "success",
        "message": "Seller created successfully",
        "seller_id": seller_id,
        "seller": seller
    }

@app.get("/marketplace/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    stats = MarketStats(
        total_products=len(products_db),
        active_sellers=len(sellers_db),
        todays_orders=89,  # Mock data
        avg_price=52.5  # Mock data
    )
    
    return {
        "status": "success",
        "stats": stats
    }

@app.post("/marketplace/upload-image")
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

@app.get("/marketplace/categories")
async def get_categories():
    """Get available product categories"""
    categories = {
        "grains": {
            "name": "Grains & Cereals",
            "icon": "🌾",
            "examples": ["Rice", "Wheat", "Barley", "Maize"]
        },
        "vegetables": {
            "name": "Vegetables",
            "icon": "🥬",
            "examples": ["Tomato", "Onion", "Potato", "Cauliflower"]
        },
        "fruits": {
            "name": "Fruits",
            "icon": "🍎",
            "examples": ["Apple", "Mango", "Banana", "Orange"]
        },
        "spices": {
            "name": "Spices & Herbs",
            "icon": "🌶️",
            "examples": ["Turmeric", "Chili", "Coriander", "Cumin"]
        },
        "pulses": {
            "name": "Pulses & Legumes",
            "icon": "🫘",
            "examples": ["Chickpea", "Lentil", "Black Gram"]
        },
        "organic": {
            "name": "Organic Products",
            "icon": "🌱",
            "examples": ["Organic Rice", "Organic Vegetables"]
        }
    }
    
    return {
        "status": "success",
        "categories": categories
    }

@app.get("/marketplace/search")
async def search_products(
    q: str,
    marketplace_type: Optional[str] = None,
    limit: int = 20
):
    """Search products with AI-powered recommendations"""
    # Simple text search
    search_lower = q.lower()
    results = []
    
    for product in products_db.values():
        if (search_lower in product.name.lower() or 
            search_lower in product.description.lower() or
            search_lower in product.category.value):
            
            if marketplace_type and product.marketplace_type.value != marketplace_type:
                continue
                
            results.append({
                "product": product,
                "match_score": 0.85,  # Mock score
                "reasons": ["Name match", "Category match"]
            })
    
    # Limit results
    results = results[:limit]
    
    return {
        "status": "success",
        "query": q,
        "results": results,
        "total_found": len(results),
        "ai_powered": True
    }

@app.post("/marketplace/bulk-inquiry")
async def create_bulk_inquiry(inquiry_data: Dict[str, Any]):
    """Create B2B bulk purchase inquiry"""
    inquiry_id = str(uuid.uuid4())
    
    # Mock matching logic
    matched_products = []
    for product in products_db.values():
        if product.marketplace_type == MarketplaceType.B2B:
            matched_products.append({
                "product": product,
                "match_score": 0.9,
                "available_quantity": product.stock,
                "estimated_price": product.price
            })
    
    inquiry = {
        "inquiry_id": inquiry_id,
        "buyer_requirements": inquiry_data,
        "matched_products": matched_products[:5],
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "inquiry": inquiry,
        "matched_sellers": len(matched_products)
    }

@app.get("/marketplace/market-insights")
async def get_market_insights():
    """Get AI-powered market insights"""
    insights = {
        "price_trends": {
            "trending_up": ["Tomato", "Onion", "Rice"],
            "trending_down": ["Wheat", "Cotton"],
            "stable": ["Pulses", "Spices"]
        },
        "demand_forecast": {
            "high_demand": ["Organic Vegetables", "Premium Rice"],
            "moderate_demand": ["Cotton", "Spices"],
            "low_demand": ["Basic Grains"]
        },
        "seasonal_insights": {
            "current_season": "Rabi Harvesting",
            "recommended_actions": [
                "Sell wheat before market saturation",
                "Stock up on organic produce for urban markets"
            ]
        },
        "market_alerts": [
            "Premium pricing opportunity for organic vegetables",
            "Increased demand for pulses in urban markets"
        ]
    }
    
    return {
        "status": "success",
        "insights": insights,
        "generated_at": datetime.now().isoformat(),
        "ai_powered": True
    }

@app.get("/marketplace/status")
async def get_system_status():
    """Get marketplace system status"""
    return {
        "status": "operational",
        "api_version": "1.0.0",
        "uptime": "99.9%",
        "features": {
            "product_management": "active",
            "image_upload": "active",
            "search_engine": "active",
            "ai_recommendations": "active",
            "bulk_inquiries": "active"
        },
        "statistics": {
            "total_products": len(products_db),
            "total_sellers": len(sellers_db),
            "b2c_products": len([p for p in products_db.values() if p.marketplace_type == MarketplaceType.B2C]),
            "b2b_products": len([p for p in products_db.values() if p.marketplace_type == MarketplaceType.B2B])
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🌾💰 Starting Agricultural Marketplace API...")
    print("📊 Dashboard: http://localhost:8001/docs")
    print("🔍 Products: http://localhost:8001/marketplace/products")
    print("📈 Status: http://localhost:8001/marketplace/status")
    uvicorn.run(app, host="0.0.0.0", port=8001)
