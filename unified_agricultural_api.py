#!/usr/bin/env python3
"""
🌾💰👨‍🌾📊 Unified Agricultural Platform API
Integrated marketplace, farmer profiles, and business intelligence in one service
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
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🌾💰 Unified Agricultural Platform API",
    description="Complete agricultural ecosystem: Marketplace, Farmer Profiles, and Business Intelligence",
    version="2.0.0"
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

# ==================== MARKETPLACE MODELS ====================

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

# ==================== FARMER PROFILE MODELS ====================

class FarmingExperience(str, Enum):
    BEGINNER = "0-2 years"
    INTERMEDIATE = "3-7 years"
    EXPERIENCED = "8-15 years"
    VETERAN = "15+ years"

class CreditScoreCategory(str, Enum):
    EXCELLENT = "excellent"  # 800-900
    VERY_GOOD = "very_good"  # 700-799
    GOOD = "good"  # 600-699
    FAIR = "fair"  # 500-599
    POOR = "poor"  # 300-499

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"
    NOT_SUBMITTED = "not_submitted"

class SatelliteMetrics(BaseModel):
    ndvi_score: float = Field(ge=0.0, le=1.0, description="Vegetation health")
    soil_moisture: float = Field(ge=0.0, le=100.0, description="Soil moisture percentage")
    environmental_score: float = Field(ge=0.0, le=100.0, description="Overall environmental health")
    yield_prediction_accuracy: float = Field(ge=0.0, le=100.0, description="Historical yield prediction accuracy")
    last_updated: datetime = Field(default_factory=datetime.now)

class CropPerformanceHistory(BaseModel):
    crop_type: str
    season: str
    year: int
    yield_tons_per_hectare: float
    quality_grade: str  # A+, A, B+, B, C
    market_price_achieved: float
    satellite_ndvi_avg: float
    weather_challenges: List[str] = []

class FinancialHistory(BaseModel):
    total_loans_taken: int = 0
    total_amount_borrowed: float = 0.0
    repayment_success_rate: float = Field(ge=0.0, le=100.0, default=100.0)
    current_outstanding: float = 0.0
    credit_score_external: Optional[int] = None
    insurance_claims: int = 0
    subsidy_utilization_rate: float = Field(ge=0.0, le=100.0, default=0.0)

class MarketActivity(BaseModel):
    total_sales_volume: float = 0.0  # in tonnes
    total_revenue: float = 0.0
    avg_selling_price_premium: float = 0.0  # % above market price
    customer_satisfaction_score: float = Field(ge=0.0, le=5.0, default=3.0)
    repeat_customer_rate: float = Field(ge=0.0, le=100.0, default=0.0)
    delivery_success_rate: float = Field(ge=0.0, le=100.0, default=100.0)

class TechnologyAdoption(BaseModel):
    uses_satellite_monitoring: bool = False
    uses_ai_recommendations: bool = False
    uses_precision_agriculture: bool = False
    uses_digital_marketplace: bool = False
    smartphone_proficiency: int = Field(ge=1, le=5, default=3)
    technology_adoption_score: float = Field(ge=0.0, le=100.0, default=20.0)

class FarmerProfile(BaseModel):
    farmer_id: str = Field(default_factory=lambda: f"FARMER_{str(uuid.uuid4())[:8].upper()}")
    name: str
    phone: str
    location: Dict[str, str]  # state, district, village
    farm_size_hectares: float
    farming_experience: FarmingExperience
    primary_crops: List[str]
    verification_status: VerificationStatus = VerificationStatus.NOT_SUBMITTED
    
    # Core scoring components
    satellite_metrics: SatelliteMetrics
    crop_performance_history: List[CropPerformanceHistory] = []
    financial_history: FinancialHistory = Field(default_factory=FinancialHistory)
    market_activity: MarketActivity = Field(default_factory=MarketActivity)
    technology_adoption: TechnologyAdoption = Field(default_factory=TechnologyAdoption)
    
    # Calculated scores
    agriculture_credit_score: int = Field(ge=300, le=900, default=500)
    score_category: CreditScoreCategory = CreditScoreCategory.FAIR
    score_last_updated: datetime = Field(default_factory=datetime.now)
    
    # Profile metadata
    profile_created: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    profile_completeness: float = Field(ge=0.0, le=100.0, default=30.0)

class CreditScoreBreakdown(BaseModel):
    total_score: int
    category: CreditScoreCategory
    components: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    strengths: List[str]
    improvement_areas: List[str]
    next_review_date: datetime

# ==================== BUSINESS INTELLIGENCE MODELS ====================

class SellerVerificationScore(BaseModel):
    seller_id: str
    overall_score: float = Field(ge=0.0, le=100.0)
    verification_status: str
    risk_level: str
    components: Dict[str, float]
    recommendations: List[str]
    last_updated: datetime = Field(default_factory=datetime.now)

class MarketIntelligence(BaseModel):
    market_trend: str
    price_forecast: Dict[str, float]
    demand_analysis: Dict[str, str]
    supply_risk_assessment: Dict[str, str]
    competitive_analysis: Dict[str, Any]
    seasonal_insights: Dict[str, Any]

# ==================== SCORING ALGORITHMS ====================

def calculate_agriculture_credit_score(farmer: FarmerProfile) -> int:
    """Calculate Agriculture Credit Score (300-900 scale)"""
    score = 0
    
    # 1. Satellite Data Performance (25% weight) - Max 225 points
    satellite_score = 0
    satellite_score += farmer.satellite_metrics.ndvi_score * 80  # NDVI contribution
    satellite_score += (farmer.satellite_metrics.soil_moisture / 100) * 60  # Soil moisture
    satellite_score += (farmer.satellite_metrics.environmental_score / 100) * 85  # Environmental health
    score += satellite_score
    
    # 2. Crop Performance History (20% weight) - Max 180 points
    if farmer.crop_performance_history:
        performance_score = 0
        for crop in farmer.crop_performance_history:
            grade_scores = {"A+": 20, "A": 18, "B+": 15, "B": 12, "C": 8}
            performance_score += grade_scores.get(crop.quality_grade, 10)
            
            if crop.yield_tons_per_hectare > 4.0:
                performance_score += 15
            elif crop.yield_tons_per_hectare > 3.0:
                performance_score += 10
            else:
                performance_score += 5
        
        avg_performance = performance_score / len(farmer.crop_performance_history)
        score += min(180, avg_performance * 2.5)
    
    # 3. Financial History (20% weight) - Max 180 points
    financial_score = 0
    financial_score += (farmer.financial_history.repayment_success_rate / 100) * 80
    if farmer.financial_history.current_outstanding < 50000:
        financial_score += 40
    elif farmer.financial_history.current_outstanding < 100000:
        financial_score += 25
    else:
        financial_score += 10
    
    financial_score += min(60, (farmer.financial_history.subsidy_utilization_rate / 100) * 60)
    score += financial_score
    
    # 4. Market Performance (15% weight) - Max 135 points
    market_score = 0
    if farmer.market_activity.total_sales_volume > 0:
        market_score += min(50, farmer.market_activity.customer_satisfaction_score * 10)
        market_score += min(40, (farmer.market_activity.delivery_success_rate / 100) * 40)
        market_score += min(45, farmer.market_activity.avg_selling_price_premium * 3)
    score += market_score
    
    # 5. Technology Adoption (10% weight) - Max 90 points
    tech_score = (farmer.technology_adoption.technology_adoption_score / 100) * 90
    score += tech_score
    
    # 6. Experience Bonus (5% weight) - Max 45 points
    experience_scores = {
        FarmingExperience.BEGINNER: 15,
        FarmingExperience.INTERMEDIATE: 25,
        FarmingExperience.EXPERIENCED: 35,
        FarmingExperience.VETERAN: 45
    }
    score += experience_scores.get(farmer.farming_experience, 20)
    
    # 7. Verification Bonus (5% weight) - Max 45 points
    if farmer.verification_status == VerificationStatus.VERIFIED:
        score += 45
    elif farmer.verification_status == VerificationStatus.PENDING:
        score += 20
    
    # Normalize to 300-900 scale
    final_score = int(300 + (score / 900) * 600)
    return max(300, min(900, final_score))

def determine_score_category(score: int) -> CreditScoreCategory:
    """Determine credit score category"""
    if score >= 800:
        return CreditScoreCategory.EXCELLENT
    elif score >= 700:
        return CreditScoreCategory.VERY_GOOD
    elif score >= 600:
        return CreditScoreCategory.GOOD
    elif score >= 500:
        return CreditScoreCategory.FAIR
    else:
        return CreditScoreCategory.POOR

def calculate_profile_completeness(farmer: FarmerProfile) -> float:
    """Calculate profile completeness percentage"""
    total_fields = 10
    completed_fields = 0
    
    # Basic info
    if farmer.name and farmer.phone:
        completed_fields += 1
    if farmer.location and len(farmer.location) >= 3:
        completed_fields += 1
    if farmer.farm_size_hectares > 0:
        completed_fields += 1
    if farmer.primary_crops:
        completed_fields += 1
    
    # Performance data
    if farmer.crop_performance_history:
        completed_fields += 1
    if farmer.financial_history.total_loans_taken > 0:
        completed_fields += 1
    if farmer.market_activity.total_sales_volume > 0:
        completed_fields += 1
    
    # Technology & verification
    if farmer.technology_adoption.technology_adoption_score > 30:
        completed_fields += 1
    if farmer.verification_status in [VerificationStatus.VERIFIED, VerificationStatus.PENDING]:
        completed_fields += 1
    if farmer.satellite_metrics.ndvi_score > 0:
        completed_fields += 1
    
    return (completed_fields / total_fields) * 100

def create_sample_farmer(name: str, experience: FarmingExperience, location: Dict[str, str]) -> FarmerProfile:
    """Create a sample farmer with realistic data"""
    
    # Generate realistic satellite metrics
    base_ndvi = random.uniform(0.5, 0.85)
    base_moisture = random.uniform(30, 80)
    env_score = (base_ndvi * 100 + base_moisture) / 2 + random.uniform(-10, 10)
    env_score = max(0, min(100, env_score))
    
    satellite_metrics = SatelliteMetrics(
        ndvi_score=base_ndvi,
        soil_moisture=base_moisture,
        environmental_score=env_score,
        yield_prediction_accuracy=random.uniform(70, 95)
    )
    
    # Generate crop performance history
    crops = ["wheat", "rice", "cotton", "sugarcane", "soybean"]
    performance_history = []
    for i in range(random.randint(2, 5)):
        performance_history.append(CropPerformanceHistory(
            crop_type=random.choice(crops),
            season=random.choice(["kharif", "rabi"]),
            year=2024 - i,
            yield_tons_per_hectare=random.uniform(2.5, 6.0),
            quality_grade=random.choice(["A+", "A", "B+", "B"]),
            market_price_achieved=random.uniform(15000, 35000),
            satellite_ndvi_avg=random.uniform(0.5, 0.8),
            weather_challenges=random.sample(["drought", "flood", "pest", "disease", "hail"], random.randint(0, 2))
        ))
    
    # Generate financial history
    financial_history = FinancialHistory(
        total_loans_taken=random.randint(1, 8),
        total_amount_borrowed=random.uniform(50000, 500000),
        repayment_success_rate=random.uniform(85, 100),
        current_outstanding=random.uniform(0, 100000),
        insurance_claims=random.randint(0, 3),
        subsidy_utilization_rate=random.uniform(40, 90)
    )
    
    # Generate market activity
    market_activity = MarketActivity(
        total_sales_volume=random.uniform(10, 150),
        total_revenue=random.uniform(200000, 2000000),
        avg_selling_price_premium=random.uniform(-5, 15),
        customer_satisfaction_score=random.uniform(3.5, 5.0),
        repeat_customer_rate=random.uniform(20, 80),
        delivery_success_rate=random.uniform(85, 100)
    )
    
    # Technology adoption based on experience
    tech_base_score = {"0-2 years": 40, "3-7 years": 60, "8-15 years": 50, "15+ years": 35}
    technology_adoption = TechnologyAdoption(
        uses_satellite_monitoring=random.choice([True, False]),
        uses_ai_recommendations=random.choice([True, False]),
        uses_precision_agriculture=random.choice([True, False]),
        uses_digital_marketplace=True,
        smartphone_proficiency=random.randint(2, 5),
        technology_adoption_score=tech_base_score.get(experience, 50) + random.uniform(-10, 20)
    )
    
    farmer = FarmerProfile(
        name=name,
        phone=f"+91-{random.randint(7000000000, 9999999999)}",
        location=location,
        farm_size_hectares=random.uniform(1.0, 20.0),
        farming_experience=experience,
        primary_crops=random.sample(crops, random.randint(1, 3)),
        verification_status=random.choice([VerificationStatus.VERIFIED, VerificationStatus.PENDING]),
        satellite_metrics=satellite_metrics,
        crop_performance_history=performance_history,
        financial_history=financial_history,
        market_activity=market_activity,
        technology_adoption=technology_adoption
    )
    
    # Calculate the agriculture credit score
    farmer.agriculture_credit_score = calculate_agriculture_credit_score(farmer)
    farmer.score_category = determine_score_category(farmer.agriculture_credit_score)
    farmer.profile_completeness = calculate_profile_completeness(farmer)
    
    return farmer

# ==================== MOCK DATA ====================

# Sample marketplace data
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
        images=["/uploads/product_images/basmati-rice.jpg"],
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
        images=["/uploads/product_images/wheat-flour.jpg"],
        is_organic=True,
        harvest_date="2024-12-01",
        marketplace_type=MarketplaceType.B2C,
        specifications={
            "variety": "Sharbati Wheat",
            "grade": "Premium",
            "moisture": 10,
            "purity": 98
        }
    )
]

# Create sample farmers
sample_farmers = [
    create_sample_farmer("Rajesh Kumar Singh", FarmingExperience.EXPERIENCED, 
                        {"state": "Punjab", "district": "Ludhiana", "village": "Doraha"}),
    create_sample_farmer("Sunita Devi", FarmingExperience.INTERMEDIATE,
                        {"state": "Uttar Pradesh", "district": "Meerut", "village": "Kharkhauda"}),
    create_sample_farmer("Manoj Patil", FarmingExperience.VETERAN,
                        {"state": "Maharashtra", "district": "Nashik", "village": "Sinnar"}),
    create_sample_farmer("Kavita Sharma", FarmingExperience.BEGINNER,
                        {"state": "Haryana", "district": "Karnal", "village": "Assandh"}),
    create_sample_farmer("Ramesh Yadav", FarmingExperience.EXPERIENCED,
                        {"state": "Madhya Pradesh", "district": "Indore", "village": "Sanwer"})
]

# In-memory databases
products_db = {product.product_id: product for product in sample_products}
sellers_db = {seller.seller_id: seller for seller in sample_sellers}
farmers_db = {farmer.farmer_id: farmer for farmer in sample_farmers}

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "🌾💰👨‍🌾📊 Unified Agricultural Platform API",
        "description": "Complete agricultural ecosystem with marketplace, farmer profiles, and business intelligence",
        "version": "2.0.0",
        "services": {
            "marketplace": "Product listings and B2B/B2C marketplace",
            "farmer_profiles": "Agricultural credit scoring system",
            "business_intelligence": "Market analysis and supplier verification"
        },
        "endpoints": {
            "marketplace": "/marketplace/*",
            "farmer_profiles": "/farmer-profiles/*", 
            "business_intelligence": "/business-intel/*"
        }
    }

# ==================== MARKETPLACE ENDPOINTS ====================

@app.get("/marketplace/products")
async def get_products(
    marketplace_type: Optional[MarketplaceType] = None,
    category: Optional[ProductCategory] = None,
    search: Optional[str] = None
):
    """Get all products with optional filtering"""
    filtered_products = list(products_db.values())
    
    if marketplace_type:
        filtered_products = [p for p in filtered_products if p.marketplace_type == marketplace_type]
    
    if category:
        filtered_products = [p for p in filtered_products if p.category == category]
    
    if search:
        search_term = search.lower()
        filtered_products = [
            p for p in filtered_products 
            if search_term in p.name.lower() or search_term in p.description.lower()
        ]
    
    return {
        "status": "success",
        "products": filtered_products,
        "total": len(filtered_products)
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
    specifications: str = Form("{}"),
    images: List[UploadFile] = File([])
):
    """Create new product listing with image upload support"""
    try:
        product_id = str(uuid.uuid4())
        
        seller = sellers_db.get(seller_id)
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Handle image uploads
        image_urls = []
        if images and len(images) > 0 and images[0].filename:
            for image in images:
                if image.content_type and image.content_type.startswith('image/'):
                    file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
                    unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
                    file_path = PRODUCT_IMAGES_DIR / unique_filename
                    
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
        rating=4.0,
        verified=False,
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
        todays_orders=89,
        avg_price=52.5
    )
    
    return {
        "status": "success",
        "stats": stats
    }

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

# ==================== FARMER PROFILE ENDPOINTS ====================

@app.get("/farmer-profiles", response_model=List[Dict])
async def get_all_farmer_profiles():
    """Get all farmer profiles with basic information"""
    return [
        {
            "farmer_id": farmer.farmer_id,
            "name": farmer.name,
            "location": farmer.location,
            "agriculture_credit_score": farmer.agriculture_credit_score,
            "score_category": farmer.score_category,
            "verification_status": farmer.verification_status,
            "farming_experience": farmer.farming_experience,
            "primary_crops": farmer.primary_crops,
            "profile_completeness": farmer.profile_completeness
        }
        for farmer in farmers_db.values()
    ]

@app.get("/farmer-profile/{farmer_id}", response_model=FarmerProfile)
async def get_farmer_profile(farmer_id: str):
    """Get detailed farmer profile"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    return farmers_db[farmer_id]

@app.get("/farmer-profile/{farmer_id}/credit-score")
async def get_farmer_credit_score_breakdown(farmer_id: str):
    """Get detailed credit score breakdown with recommendations"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer = farmers_db[farmer_id]
    
    # Generate detailed breakdown
    satellite_component = {
        "score": int((farmer.satellite_metrics.ndvi_score * 80 + 
                     (farmer.satellite_metrics.soil_moisture / 100) * 60 + 
                     (farmer.satellite_metrics.environmental_score / 100) * 85)),
        "weight": "25%",
        "status": "Excellent" if farmer.satellite_metrics.ndvi_score > 0.7 else "Good" if farmer.satellite_metrics.ndvi_score > 0.5 else "Needs Improvement"
    }
    
    components = {
        "satellite_performance": satellite_component,
        "crop_performance": {
            "score": 120 if farmer.crop_performance_history else 60,
            "weight": "20%",
            "status": "Good" if farmer.crop_performance_history else "Needs Improvement"
        },
        "financial_history": {
            "score": int((farmer.financial_history.repayment_success_rate / 100) * 80),
            "weight": "20%",
            "status": "Excellent" if farmer.financial_history.repayment_success_rate > 95 else "Good"
        },
        "market_activity": {
            "score": int(farmer.market_activity.customer_satisfaction_score * 20),
            "weight": "15%",
            "status": "Good" if farmer.market_activity.customer_satisfaction_score > 4.0 else "Needs Improvement"
        },
        "technology_adoption": {
            "score": int((farmer.technology_adoption.technology_adoption_score / 100) * 90),
            "weight": "10%",
            "status": "Good" if farmer.technology_adoption.technology_adoption_score > 60 else "Needs Improvement"
        }
    }
    
    recommendations = []
    strengths = []
    improvement_areas = []
    
    if farmer.satellite_metrics.ndvi_score > 0.7:
        strengths.append("Excellent vegetation health management")
    else:
        improvement_areas.append("Improve crop health monitoring")
        recommendations.append("Use satellite-based crop monitoring tools")
    
    if farmer.financial_history.repayment_success_rate > 95:
        strengths.append("Outstanding loan repayment history")
    else:
        improvement_areas.append("Improve financial discipline")
        recommendations.append("Consider financial planning assistance")
    
    return {
        "total_score": farmer.agriculture_credit_score,
        "category": farmer.score_category,
        "components": components,
        "recommendations": recommendations,
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "next_review_date": datetime.now() + timedelta(days=90)
    }

@app.get("/farmer-leaderboard")
async def get_farmer_leaderboard(limit: int = 10):
    """Get top farmers by credit score"""
    sorted_farmers = sorted(farmers_db.values(), key=lambda f: f.agriculture_credit_score, reverse=True)
    
    leaderboard = []
    for i, farmer in enumerate(sorted_farmers[:limit]):
        leaderboard.append({
            "rank": i + 1,
            "farmer_id": farmer.farmer_id,
            "name": farmer.name,
            "location": f"{farmer.location.get('district', '')}, {farmer.location.get('state', '')}",
            "agriculture_credit_score": farmer.agriculture_credit_score,
            "score_category": farmer.score_category,
            "farming_experience": farmer.farming_experience,
            "primary_crops": farmer.primary_crops,
            "verification_status": farmer.verification_status
        })
    
    return leaderboard

@app.get("/credit-score-analytics")
async def get_credit_score_analytics():
    """Get analytics about credit scores across all farmers"""
    if not farmers_db:
        return {"message": "No farmer data available"}
    
    scores = [farmer.agriculture_credit_score for farmer in farmers_db.values()]
    
    analytics = {
        "total_farmers": len(farmers_db),
        "average_score": sum(scores) / len(scores),
        "score_distribution": {
            "excellent": len([s for s in scores if s >= 800]),
            "very_good": len([s for s in scores if 700 <= s < 800]),
            "good": len([s for s in scores if 600 <= s < 700]),
            "fair": len([s for s in scores if 500 <= s < 600]),
            "poor": len([s for s in scores if s < 500])
        },
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "verified_farmers": len([f for f in farmers_db.values() if f.verification_status == VerificationStatus.VERIFIED])
    }
    
    return analytics

# ==================== BUSINESS INTELLIGENCE ENDPOINTS ====================

@app.get("/business-intel/seller-verification/{seller_id}")
async def get_seller_verification_score(seller_id: str):
    """Get seller verification score and analysis"""
    
    # Mock verification analysis
    base_score = random.uniform(65, 95)
    
    components = {
        "financial_stability": random.uniform(70, 95),
        "delivery_performance": random.uniform(80, 98),
        "quality_consistency": random.uniform(75, 92),
        "customer_feedback": random.uniform(85, 96),
        "compliance_score": random.uniform(60, 90)
    }
    
    risk_level = "LOW" if base_score > 85 else "MEDIUM" if base_score > 70 else "HIGH"
    
    recommendations = []
    if components["financial_stability"] < 80:
        recommendations.append("Request additional financial documentation")
    if components["delivery_performance"] < 85:
        recommendations.append("Monitor delivery timelines closely")
    if components["quality_consistency"] < 80:
        recommendations.append("Implement quality assurance checks")
    
    verification_score = SellerVerificationScore(
        seller_id=seller_id,
        overall_score=base_score,
        verification_status="VERIFIED" if base_score > 80 else "PENDING",
        risk_level=risk_level,
        components=components,
        recommendations=recommendations
    )
    
    return {
        "status": "success",
        "verification_score": verification_score,
        "analysis_date": datetime.now().isoformat()
    }

@app.get("/business-intel/market-intelligence")
async def get_market_intelligence():
    """Get comprehensive market intelligence report"""
    
    intelligence = {
        "market_overview": {
            "total_market_size": "₹2.1 Trillion",
            "growth_rate": "12.5% YoY",
            "active_participants": 15420,
            "transaction_volume": "89.4K tonnes/month"
        },
        "price_trends": {
            "wheat": {"current": 2150, "trend": "up", "change": 8.5},
            "rice": {"current": 3200, "trend": "stable", "change": 1.2},
            "cotton": {"current": 65000, "trend": "down", "change": -3.8},
            "sugarcane": {"current": 350, "trend": "up", "change": 5.2}
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
        "intelligence": intelligence,
        "generated_at": datetime.now().isoformat(),
        "ai_powered": True
    }

@app.get("/business-intel/procurement-recommendations")
async def get_procurement_recommendations():
    """Get AI-powered procurement recommendations"""
    
    recommendations = {
        "priority_purchases": [
            {
                "product": "Organic Wheat",
                "reason": "High demand forecast for Q4",
                "suggested_quantity": "500 tonnes",
                "price_range": "₹28,000-32,000/tonne",
                "optimal_timing": "Next 2 weeks"
            },
            {
                "product": "Basmati Rice",
                "reason": "Export opportunity identified",
                "suggested_quantity": "200 tonnes",
                "price_range": "₹65,000-70,000/tonne",
                "optimal_timing": "Immediate"
            }
        ],
        "avoid_purchases": [
            {
                "product": "Regular Cotton",
                "reason": "Oversupply expected",
                "alternative": "Focus on premium varieties"
            }
        ],
        "market_conditions": {
            "buyer_market": ["Cotton", "Maize"],
            "seller_market": ["Organic Produce", "Spices"]
        }
    }
    
    return {
        "status": "success",
        "recommendations": recommendations,
        "confidence_level": "High",
        "generated_at": datetime.now().isoformat()
    }

@app.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "status": "operational",
        "api_version": "2.0.0",
        "uptime": "99.9%",
        "services": {
            "marketplace": "active",
            "farmer_profiles": "active", 
            "business_intelligence": "active",
            "image_upload": "active",
            "ai_recommendations": "active"
        },
        "statistics": {
            "total_products": len(products_db),
            "total_sellers": len(sellers_db),
            "total_farmers": len(farmers_db),
            "b2c_products": len([p for p in products_db.values() if p.marketplace_type == MarketplaceType.B2C]),
            "b2b_products": len([p for p in products_db.values() if p.marketplace_type == MarketplaceType.B2B]),
            "verified_farmers": len([f for f in farmers_db.values() if f.verification_status == VerificationStatus.VERIFIED])
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🌾💰👨‍🌾📊 Starting Unified Agricultural Platform API...")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("🛒 Marketplace: http://localhost:8000/marketplace/products")
    print("👨‍🌾 Farmer Profiles: http://localhost:8000/farmer-profiles")
    print("📈 Business Intel: http://localhost:8000/business-intel/market-intelligence")
    print("🔍 System Status: http://localhost:8000/system/status")
    uvicorn.run(app, host="0.0.0.0", port=8000)
