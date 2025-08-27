#!/usr/bin/env python3
"""
🌾👨‍🌾 Farmer Profile & Credit Score API
Like a credit score for farmers based on agricultural data
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
    title="🌾👨‍🌾 Farmer Profile & Credit Score API",
    description="Agricultural Credit Scoring System based on satellite data, farming history, and AgriSens ML",
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

# ==================== MODELS ====================

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
    credit_score_external: Optional[int] = None  # Traditional credit score if available
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
    smartphone_proficiency: int = Field(ge=1, le=5, default=3)  # 1-5 scale
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

# ==================== MOCK DATA ====================

# Sample farmer profiles
sample_farmers = []

# ==================== SCORING ALGORITHM ====================

def calculate_agriculture_credit_score(farmer: FarmerProfile) -> int:
    """
    Calculate Agriculture Credit Score (300-900 scale)
    Like a CIBIL score but for farmers based on agricultural performance
    """
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
            # Grade scoring
            grade_scores = {"A+": 20, "A": 18, "B+": 15, "B": 12, "C": 8}
            performance_score += grade_scores.get(crop.quality_grade, 10)
            
            # Yield scoring (normalized)
            if crop.yield_tons_per_hectare > 4.0:
                performance_score += 15
            elif crop.yield_tons_per_hectare > 3.0:
                performance_score += 10
            else:
                performance_score += 5
        
        # Average and scale
        avg_performance = performance_score / len(farmer.crop_performance_history)
        score += min(180, avg_performance * 2.5)
    
    # 3. Financial History (20% weight) - Max 180 points
    financial_score = 0
    financial_score += (farmer.financial_history.repayment_success_rate / 100) * 80  # Repayment history
    if farmer.financial_history.current_outstanding < 50000:
        financial_score += 40  # Low outstanding debt
    elif farmer.financial_history.current_outstanding < 100000:
        financial_score += 25
    else:
        financial_score += 10
    
    financial_score += min(60, (farmer.financial_history.subsidy_utilization_rate / 100) * 60)  # Subsidy utilization
    score += financial_score
    
    # 4. Market Performance (15% weight) - Max 135 points
    market_score = 0
    if farmer.market_activity.total_sales_volume > 0:
        market_score += min(50, farmer.market_activity.customer_satisfaction_score * 10)  # Customer satisfaction
        market_score += min(40, (farmer.market_activity.delivery_success_rate / 100) * 40)  # Delivery success
        market_score += min(45, farmer.market_activity.avg_selling_price_premium * 3)  # Price premium achievement
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
    
    # Generate satellite metrics
    satellite_metrics = SatelliteMetrics(
        ndvi_score=random.uniform(0.5, 0.85),
        soil_moisture=random.uniform(30, 80),
        environmental_score=random.uniform(60, 95),
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
        uses_digital_marketplace=True,  # Since they're using this system
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

# Create sample data
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

# In-memory database
farmers_db = {farmer.farmer_id: farmer for farmer in sample_farmers}

# ==================== SCORING ALGORITHM ====================

def calculate_agriculture_credit_score(farmer: FarmerProfile) -> int:
    """
    Calculate Agriculture Credit Score (300-900 scale)
    Like a CIBIL score but for farmers based on agricultural performance
    """
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
            # Grade scoring
            grade_scores = {"A+": 20, "A": 18, "B+": 15, "B": 12, "C": 8}
            performance_score += grade_scores.get(crop.quality_grade, 10)
            
            # Yield scoring (normalized)
            if crop.yield_tons_per_hectare > 4.0:
                performance_score += 15
            elif crop.yield_tons_per_hectare > 3.0:
                performance_score += 10
            else:
                performance_score += 5
        
        # Average and scale
        avg_performance = performance_score / len(farmer.crop_performance_history)
        score += min(180, avg_performance * 2.5)
    
    # 3. Financial History (20% weight) - Max 180 points
    financial_score = 0
    financial_score += (farmer.financial_history.repayment_success_rate / 100) * 80  # Repayment history
    if farmer.financial_history.current_outstanding < 50000:
        financial_score += 40  # Low outstanding debt
    elif farmer.financial_history.current_outstanding < 100000:
        financial_score += 25
    else:
        financial_score += 10
    
    financial_score += min(60, (farmer.financial_history.subsidy_utilization_rate / 100) * 60)  # Subsidy utilization
    score += financial_score
    
    # 4. Market Performance (15% weight) - Max 135 points
    market_score = 0
    if farmer.market_activity.total_sales_volume > 0:
        market_score += min(50, farmer.market_activity.customer_satisfaction_score * 10)  # Customer satisfaction
        market_score += min(40, (farmer.market_activity.delivery_success_rate / 100) * 40)  # Delivery success
        market_score += min(45, farmer.market_activity.avg_selling_price_premium * 3)  # Price premium achievement
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

def generate_credit_score_breakdown(farmer: FarmerProfile) -> CreditScoreBreakdown:
    """Generate detailed credit score breakdown with recommendations"""
    
    # Calculate component scores
    satellite_component = {
        "score": int((farmer.satellite_metrics.ndvi_score * 80 + 
                     (farmer.satellite_metrics.soil_moisture / 100) * 60 + 
                     (farmer.satellite_metrics.environmental_score / 100) * 85)),
        "weight": "25%",
        "status": "Excellent" if farmer.satellite_metrics.ndvi_score > 0.7 else "Good" if farmer.satellite_metrics.ndvi_score > 0.5 else "Needs Improvement",
        "details": {
            "ndvi_score": round(farmer.satellite_metrics.ndvi_score, 2),
            "soil_moisture": round(farmer.satellite_metrics.soil_moisture, 1),
            "environmental_score": round(farmer.satellite_metrics.environmental_score, 1)
        }
    }
    
    performance_score = 0
    if farmer.crop_performance_history:
        for crop in farmer.crop_performance_history:
            grade_scores = {"A+": 20, "A": 18, "B+": 15, "B": 12, "C": 8}
            performance_score += grade_scores.get(crop.quality_grade, 10)
        performance_score = int((performance_score / len(farmer.crop_performance_history)) * 2.5)
    
    performance_component = {
        "score": performance_score,
        "weight": "20%",
        "status": "Excellent" if performance_score > 150 else "Good" if performance_score > 120 else "Needs Improvement",
        "details": {
            "average_grade": calculate_average_grade(farmer.crop_performance_history),
            "seasons_tracked": len(farmer.crop_performance_history),
            "yield_consistency": calculate_yield_consistency(farmer.crop_performance_history)
        }
    }
    
    financial_component = {
        "score": int((farmer.financial_history.repayment_success_rate / 100) * 80 + 
                    (40 if farmer.financial_history.current_outstanding < 50000 else 25) +
                    min(60, (farmer.financial_history.subsidy_utilization_rate / 100) * 60)),
        "weight": "20%",
        "status": "Excellent" if farmer.financial_history.repayment_success_rate > 95 else "Good" if farmer.financial_history.repayment_success_rate > 85 else "Needs Improvement",
        "details": {
            "repayment_rate": round(farmer.financial_history.repayment_success_rate, 1),
            "current_outstanding": round(farmer.financial_history.current_outstanding, 0),
            "subsidy_utilization": round(farmer.financial_history.subsidy_utilization_rate, 1)
        }
    }
    
    components = {
        "satellite_performance": satellite_component,
        "crop_performance": performance_component,
        "financial_history": financial_component,
        "market_activity": {
            "score": int(min(50, farmer.market_activity.customer_satisfaction_score * 10) +
                        min(40, (farmer.market_activity.delivery_success_rate / 100) * 40) +
                        min(45, farmer.market_activity.avg_selling_price_premium * 3)),
            "weight": "15%",
            "status": "Good" if farmer.market_activity.customer_satisfaction_score > 4.0 else "Needs Improvement"
        },
        "technology_adoption": {
            "score": int((farmer.technology_adoption.technology_adoption_score / 100) * 90),
            "weight": "10%",
            "status": "Good" if farmer.technology_adoption.technology_adoption_score > 60 else "Needs Improvement"
        }
    }
    
    # Generate recommendations
    recommendations = []
    strengths = []
    improvement_areas = []
    
    if farmer.satellite_metrics.ndvi_score > 0.7:
        strengths.append("Excellent vegetation health management")
    else:
        improvement_areas.append("Improve crop health monitoring using satellite insights")
        recommendations.append("Use AgriSens AI recommendations to optimize crop health")
    
    if farmer.financial_history.repayment_success_rate > 95:
        strengths.append("Outstanding loan repayment history")
    else:
        improvement_areas.append("Improve financial discipline and loan repayment")
        recommendations.append("Consider financial planning with AgriSens Finance Policy Agent")
    
    if farmer.technology_adoption.technology_adoption_score < 50:
        improvement_areas.append("Low technology adoption")
        recommendations.append("Adopt precision agriculture tools and satellite monitoring")
    
    if farmer.market_activity.customer_satisfaction_score > 4.5:
        strengths.append("Excellent customer satisfaction in marketplace")
    
    if len(farmer.crop_performance_history) < 3:
        recommendations.append("Build more crop performance history for better scoring")
    
    return CreditScoreBreakdown(
        total_score=farmer.agriculture_credit_score,
        category=farmer.score_category,
        components=components,
        recommendations=recommendations,
        strengths=strengths,
        improvement_areas=improvement_areas,
        next_review_date=datetime.now() + timedelta(days=90)
    )

def calculate_average_grade(history: List[CropPerformanceHistory]) -> str:
    """Calculate average grade from crop performance history"""
    if not history:
        return "N/A"
    
    grade_values = {"A+": 4.0, "A": 3.7, "B+": 3.3, "B": 3.0, "C": 2.0}
    avg_value = sum(grade_values.get(crop.quality_grade, 2.5) for crop in history) / len(history)
    
    if avg_value >= 3.8:
        return "A+"
    elif avg_value >= 3.5:
        return "A"
    elif avg_value >= 3.2:
        return "B+"
    elif avg_value >= 2.8:
        return "B"
    else:
        return "C"

def calculate_yield_consistency(history: List[CropPerformanceHistory]) -> str:
    """Calculate yield consistency from crop performance history"""
    if len(history) < 2:
        return "Insufficient data"
    
    yields = [crop.yield_tons_per_hectare for crop in history]
    avg_yield = sum(yields) / len(yields)
    variance = sum((y - avg_yield) ** 2 for y in yields) / len(yields)
    coefficient_of_variation = (variance ** 0.5) / avg_yield if avg_yield > 0 else 1
    
    if coefficient_of_variation < 0.15:
        return "Very Consistent"
    elif coefficient_of_variation < 0.25:
        return "Consistent"
    elif coefficient_of_variation < 0.35:
        return "Moderately Consistent"
    else:
        return "Inconsistent"

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "🌾👨‍🌾 Farmer Profile & Agricultural Credit Score API",
        "description": "Credit scoring system for farmers based on satellite data and agricultural performance",
        "version": "1.0.0",
        "features": [
            "Agricultural Credit Score (300-900 scale)",
            "Satellite-based performance tracking",
            "Crop performance history analysis",
            "Financial and market activity scoring",
            "Technology adoption assessment",
            "Comprehensive recommendations"
        ]
    }

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

@app.get("/farmer-profile/{farmer_id}/credit-score", response_model=CreditScoreBreakdown)
async def get_farmer_credit_score_breakdown(farmer_id: str):
    """Get detailed credit score breakdown with recommendations"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer = farmers_db[farmer_id]
    return generate_credit_score_breakdown(farmer)

@app.post("/farmer-profile", response_model=FarmerProfile)
async def create_farmer_profile(
    name: str = Form(...),
    phone: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    village: str = Form(...),
    farm_size_hectares: float = Form(...),
    farming_experience: FarmingExperience = Form(...),
    primary_crops: str = Form(...)  # Comma-separated
):
    """Create a new farmer profile"""
    
    # Parse primary crops
    crops_list = [crop.strip() for crop in primary_crops.split(",")]
    
    # Create basic satellite metrics (will be updated with real data)
    satellite_metrics = SatelliteMetrics(
        ndvi_score=0.6,  # Default
        soil_moisture=50.0,  # Default
        environmental_score=60.0,  # Default
        yield_prediction_accuracy=75.0  # Default
    )
    
    # Create new farmer profile
    new_farmer = FarmerProfile(
        name=name,
        phone=phone,
        location={"state": state, "district": district, "village": village},
        farm_size_hectares=farm_size_hectares,
        farming_experience=farming_experience,
        primary_crops=crops_list,
        satellite_metrics=satellite_metrics
    )
    
    # Calculate initial score
    new_farmer.agriculture_credit_score = calculate_agriculture_credit_score(new_farmer)
    new_farmer.score_category = determine_score_category(new_farmer.agriculture_credit_score)
    new_farmer.profile_completeness = calculate_profile_completeness(new_farmer)
    
    # Store in database
    farmers_db[new_farmer.farmer_id] = new_farmer
    
    return new_farmer

@app.put("/farmer-profile/{farmer_id}/satellite-data")
async def update_satellite_data(farmer_id: str, satellite_data: SatelliteMetrics):
    """Update farmer's satellite data and recalculate score"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer = farmers_db[farmer_id]
    farmer.satellite_metrics = satellite_data
    
    # Recalculate score
    farmer.agriculture_credit_score = calculate_agriculture_credit_score(farmer)
    farmer.score_category = determine_score_category(farmer.agriculture_credit_score)
    farmer.score_last_updated = datetime.now()
    
    return {"message": "Satellite data updated", "new_score": farmer.agriculture_credit_score}

@app.post("/farmer-profile/{farmer_id}/crop-performance")
async def add_crop_performance(farmer_id: str, performance: CropPerformanceHistory):
    """Add crop performance record and recalculate score"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer = farmers_db[farmer_id]
    farmer.crop_performance_history.append(performance)
    
    # Recalculate score
    farmer.agriculture_credit_score = calculate_agriculture_credit_score(farmer)
    farmer.score_category = determine_score_category(farmer.agriculture_credit_score)
    farmer.score_last_updated = datetime.now()
    farmer.profile_completeness = calculate_profile_completeness(farmer)
    
    return {"message": "Crop performance added", "new_score": farmer.agriculture_credit_score}

@app.get("/credit-score-analytics")
async def get_credit_score_analytics():
    """Get comprehensive analytics about credit scores across all farmers"""
    if not farmers_db:
        return {"message": "No farmer data available"}
    
    scores = [farmer.agriculture_credit_score for farmer in farmers_db.values()]
    categories = [farmer.score_category for farmer in farmers_db.values()]
    
    # Calculate percentiles
    sorted_scores = sorted(scores)
    percentiles = {
        "25th": sorted_scores[len(sorted_scores) // 4] if sorted_scores else 0,
        "50th": sorted_scores[len(sorted_scores) // 2] if sorted_scores else 0,
        "75th": sorted_scores[3 * len(sorted_scores) // 4] if sorted_scores else 0,
        "90th": sorted_scores[9 * len(sorted_scores) // 10] if sorted_scores else 0
    }
    
    # State-wise distribution
    state_distribution = {}
    for farmer in farmers_db.values():
        state = farmer.location.get('state', 'Unknown')
        if state not in state_distribution:
            state_distribution[state] = {
                "count": 0,
                "avg_score": 0,
                "top_score": 0,
                "verified_count": 0
            }
        state_distribution[state]["count"] += 1
        state_distribution[state]["top_score"] = max(state_distribution[state]["top_score"], farmer.agriculture_credit_score)
        if farmer.verification_status == VerificationStatus.VERIFIED:
            state_distribution[state]["verified_count"] += 1
    
    # Calculate average scores for each state
    for state in state_distribution:
        state_farmers = [f for f in farmers_db.values() if f.location.get('state') == state]
        if state_farmers:
            state_distribution[state]["avg_score"] = sum(f.agriculture_credit_score for f in state_farmers) / len(state_farmers)
    
    analytics = {
        "total_farmers": len(farmers_db),
        "average_score": sum(scores) / len(scores),
        "median_score": percentiles["50th"],
        "score_distribution": {
            "excellent": len([s for s in scores if s >= 800]),
            "very_good": len([s for s in scores if 700 <= s < 800]),
            "good": len([s for s in scores if 600 <= s < 700]),
            "fair": len([s for s in scores if 500 <= s < 600]),
            "poor": len([s for s in scores if s < 500])
        },
        "percentiles": percentiles,
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "verified_farmers": len([f for f in farmers_db.values() if f.verification_status == VerificationStatus.VERIFIED]),
        "state_wise_distribution": state_distribution,
        "technology_adoption_stats": {
            "satellite_monitoring": len([f for f in farmers_db.values() if f.technology_adoption.uses_satellite_monitoring]),
            "ai_recommendations": len([f for f in farmers_db.values() if f.technology_adoption.uses_ai_recommendations]),
            "precision_agriculture": len([f for f in farmers_db.values() if f.technology_adoption.uses_precision_agriculture]),
            "digital_marketplace": len([f for f in farmers_db.values() if f.technology_adoption.uses_digital_marketplace])
        },
        "farming_experience_distribution": {
            "beginner": len([f for f in farmers_db.values() if f.farming_experience == FarmingExperience.BEGINNER]),
            "intermediate": len([f for f in farmers_db.values() if f.farming_experience == FarmingExperience.INTERMEDIATE]),
            "experienced": len([f for f in farmers_db.values() if f.farming_experience == FarmingExperience.EXPERIENCED]),
            "veteran": len([f for f in farmers_db.values() if f.farming_experience == FarmingExperience.VETERAN])
        }
    }
    
    return analytics

@app.get("/farmer-profile/{farmer_id}/insights")
async def get_farmer_insights(farmer_id: str):
    """Get detailed insights and recommendations for a specific farmer"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    farmer = farmers_db[farmer_id]
    all_scores = [f.agriculture_credit_score for f in farmers_db.values()]
    farmer_rank = sorted(all_scores, reverse=True).index(farmer.agriculture_credit_score) + 1
    percentile = round((len(all_scores) - farmer_rank + 1) / len(all_scores) * 100, 1)
    
    insights = {
        "farmer_id": farmer_id,
        "current_score": farmer.agriculture_credit_score,
        "rank": farmer_rank,
        "total_farmers": len(farmers_db),
        "percentile": percentile,
        "score_category": farmer.score_category,
        "points_to_next_category": calculate_points_to_next_category(farmer.agriculture_credit_score),
        "strengths": [],
        "improvement_areas": [],
        "recommendations": [],
        "comparison": {
            "state_average": 0,
            "national_average": sum(all_scores) / len(all_scores),
            "top_10_percent_threshold": sorted(all_scores, reverse=True)[len(all_scores) // 10] if len(all_scores) >= 10 else max(all_scores)
        }
    }
    
    # Calculate state average
    state_farmers = [f for f in farmers_db.values() if f.location.get('state') == farmer.location.get('state')]
    if state_farmers:
        insights["comparison"]["state_average"] = sum(f.agriculture_credit_score for f in state_farmers) / len(state_farmers)
    
    # Generate insights based on farmer data
    if farmer.satellite_metrics.ndvi_score > 0.7:
        insights["strengths"].append("Excellent vegetation health (NDVI > 0.7)")
    elif farmer.satellite_metrics.ndvi_score < 0.4:
        insights["improvement_areas"].append("Poor vegetation health - consider crop rotation or soil treatment")
    
    if farmer.technology_adoption.technology_adoption_score > 70:
        insights["strengths"].append("High technology adoption rate")
    else:
        insights["recommendations"].append("Consider adopting more agricultural technologies for better efficiency")
    
    if farmer.financial_history.repayment_success_rate > 90:
        insights["strengths"].append("Excellent loan repayment history")
    elif farmer.financial_history.repayment_success_rate < 70:
        insights["improvement_areas"].append("Improve loan repayment consistency")
    
    if farmer.profile_completeness < 70:
        insights["recommendations"].append("Complete your farmer profile to unlock better credit opportunities")
    
    return insights

def calculate_points_to_next_category(current_score: int) -> int:
    """Calculate points needed to reach the next credit score category"""
    if current_score >= 800:
        return 0  # Already at highest category
    elif current_score >= 700:
        return 800 - current_score  # Points to excellent
    elif current_score >= 600:
        return 700 - current_score  # Points to very good
    elif current_score >= 500:
        return 600 - current_score  # Points to good
    else:
        return 500 - current_score  # Points to fair

@app.get("/farmer-leaderboard")
async def get_farmer_leaderboard(limit: int = 20):
    """Get top farmers by credit score with enhanced details"""
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
            "verification_status": farmer.verification_status,
            "farm_size_hectares": farmer.farm_size_hectares,
            "profile_completeness": farmer.profile_completeness,
            "ndvi_score": farmer.satellite_metrics.ndvi_score,
            "last_active": farmer.last_active.isoformat()
        })
    
    return leaderboard

@app.get("/farmer-leaderboard/{farmer_id}/position")
async def get_farmer_leaderboard_position(farmer_id: str):
    """Get specific farmer's position in the leaderboard"""
    if farmer_id not in farmers_db:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    sorted_farmers = sorted(farmers_db.values(), key=lambda f: f.agriculture_credit_score, reverse=True)
    
    for i, farmer in enumerate(sorted_farmers):
        if farmer.farmer_id == farmer_id:
            return {
                "farmer_id": farmer_id,
                "rank": i + 1,
                "total_farmers": len(sorted_farmers),
                "percentile": round((len(sorted_farmers) - i) / len(sorted_farmers) * 100, 1),
                "agriculture_credit_score": farmer.agriculture_credit_score,
                "score_category": farmer.score_category,
                "improvement_needed": {
                    "points_to_next_category": calculate_points_to_next_category(farmer.agriculture_credit_score),
                    "farmers_ahead": i,
                    "closest_farmer_score": sorted_farmers[i-1].agriculture_credit_score if i > 0 else farmer.agriculture_credit_score
                }
            }
    
    return {"error": "Farmer not found in leaderboard"}

@app.get("/farmer-leaderboard/regional/{state}")
async def get_regional_leaderboard(state: str, limit: int = 10):
    """Get leaderboard for farmers in a specific state"""
    regional_farmers = [f for f in farmers_db.values() if f.location.get('state', '').lower() == state.lower()]
    
    if not regional_farmers:
        return {"message": f"No farmers found in {state}", "leaderboard": []}
    
    sorted_farmers = sorted(regional_farmers, key=lambda f: f.agriculture_credit_score, reverse=True)
    
    leaderboard = []
    for i, farmer in enumerate(sorted_farmers[:limit]):
        leaderboard.append({
            "rank": i + 1,
            "farmer_id": farmer.farmer_id,
            "name": farmer.name,
            "location": f"{farmer.location.get('district', '')}, {farmer.location.get('village', '')}",
            "agriculture_credit_score": farmer.agriculture_credit_score,
            "score_category": farmer.score_category,
            "farming_experience": farmer.farming_experience,
            "primary_crops": farmer.primary_crops,
            "verification_status": farmer.verification_status
        })
    
    return {
        "state": state,
        "total_farmers": len(regional_farmers),
        "leaderboard": leaderboard
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
