# 📖 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. This is suitable for development and demo purposes.

## Response Format
All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message",
  "timestamp": "2025-08-27T01:52:33.014245"
}
```

## System Status API

### GET /system/status
Get overall system health and statistics.

**Response:**
```json
{
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
    "total_products": 2,
    "total_sellers": 3,
    "total_farmers": 5,
    "b2c_products": 2,
    "b2b_products": 0,
    "verified_farmers": 1
  }
}
```

## Marketplace APIs

### GET /marketplace/products
List all products in the marketplace.

**Query Parameters:**
- `category` (optional): Filter by product category
- `seller_id` (optional): Filter by seller ID
- `marketplace_type` (optional): "b2c" or "b2b"

**Response:**
```json
{
  "status": "success",
  "products": [
    {
      "product_id": "prod_1",
      "name": "Premium Basmati Rice",
      "description": "High-quality aged Basmati rice from Punjab fields",
      "category": "grains",
      "price": 85.0,
      "unit": "kg",
      "stock": 500,
      "seller": {
        "seller_id": "seller_1",
        "name": "Rajesh Kumar",
        "location": "Ludhiana, Punjab",
        "rating": 4.8,
        "verified": true,
        "total_sales": 150
      },
      "images": ["/uploads/product_images/basmati-rice.jpg"],
      "is_organic": false,
      "harvest_date": "2024-11-15",
      "marketplace_type": "b2c",
      "specifications": {
        "variety": "Pusa Basmati 1121",
        "grade": "Grade A",
        "moisture": 12,
        "purity": 99
      },
      "created_at": "2025-08-27T01:51:50.001921"
    }
  ],
  "total": 2
}
```

### POST /marketplace/products
Add a new product to the marketplace.

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `name` (required): Product name
- `description` (required): Product description
- `category` (required): Product category
- `price` (required): Product price
- `unit` (required): Price unit (kg, ton, piece, etc.)
- `stock` (required): Available stock
- `seller_id` (required): Seller ID
- `is_organic` (optional): Boolean, default false
- `harvest_date` (optional): Date string
- `marketplace_type` (optional): "b2c" or "b2b", default "b2c"
- `specifications` (optional): JSON string with product specifications
- `images` (optional): Multiple image files

**Response:**
```json
{
  "status": "success",
  "message": "Product added successfully",
  "product": {
    "product_id": "prod_new",
    "name": "New Product",
    ...
  }
}
```

### GET /marketplace/sellers
List all sellers in the marketplace.

**Response:**
```json
{
  "status": "success",
  "sellers": [
    {
      "seller_id": "seller_1",
      "name": "Rajesh Kumar",
      "location": "Ludhiana, Punjab",
      "contact": "+91-9876543210",
      "rating": 4.8,
      "verified": true,
      "total_sales": 150,
      "specialties": ["Basmati Rice", "Wheat"],
      "joined_date": "2024-01-15"
    }
  ],
  "total": 3
}
```

### POST /marketplace/sellers
Add a new seller to the marketplace.

**Request Body:**
```json
{
  "name": "New Seller",
  "location": "City, State",
  "contact": "+91-1234567890",
  "specialties": ["Product1", "Product2"]
}
```

### GET /marketplace/stats
Get marketplace statistics.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_products": 2,
    "total_sellers": 3,
    "categories": {
      "grains": 2,
      "vegetables": 0,
      "fruits": 0
    },
    "marketplace_types": {
      "b2c": 2,
      "b2b": 0
    },
    "verified_sellers": 2,
    "average_rating": 4.85
  }
}
```

### GET /marketplace/categories
Get all product categories.

**Response:**
```json
{
  "categories": [
    {
      "id": "grains",
      "name": "Grains & Cereals",
      "description": "Rice, wheat, corn, barley, etc.",
      "product_count": 2
    },
    {
      "id": "vegetables",
      "name": "Vegetables",
      "description": "Fresh vegetables and produce",
      "product_count": 0
    }
  ]
}
```

## Farmer Profile APIs

### GET /farmer-profiles
List all farmer profiles.

**Query Parameters:**
- `verified_only` (optional): Boolean, show only verified farmers
- `min_score` (optional): Minimum credit score filter
- `experience` (optional): Filter by farming experience

**Response:**
```json
[
  {
    "farmer_id": "FARMER_5277C446",
    "name": "Rajesh Kumar Singh",
    "location": {
      "state": "Punjab",
      "district": "Ludhiana",
      "village": "Doraha"
    },
    "agriculture_credit_score": 639,
    "score_category": "good",
    "verification_status": "verified",
    "farming_experience": "8-15 years",
    "primary_crops": ["rice"],
    "profile_completeness": 100.0
  }
]
```

### GET /farmer-profile/{farmer_id}
Get detailed farmer profile.

**Response:**
```json
{
  "farmer_id": "FARMER_5277C446",
  "name": "Rajesh Kumar Singh",
  "phone": "+91-9876543210",
  "location": {
    "state": "Punjab",
    "district": "Ludhiana",
    "village": "Doraha"
  },
  "farm_size_hectares": 12.5,
  "primary_crops": ["rice", "wheat"],
  "farming_experience": "8-15 years",
  "registration_date": "2024-03-15T10:30:00",
  "verification_status": "verified",
  "agriculture_credit_score": 639,
  "score_category": "good",
  "profile_completeness": 100.0,
  "satellite_metrics": {
    "ndvi_score": 0.72,
    "soil_moisture": 65.4,
    "environmental_score": 78.9,
    "yield_prediction_accuracy": 89.2
  },
  "crop_performance_history": [...],
  "financial_history": {...},
  "market_activity": {...},
  "technology_adoption": {...}
}
```

### GET /farmer-profile/{farmer_id}/credit-score
Get detailed credit score breakdown.

**Response:**
```json
{
  "farmer_id": "FARMER_5277C446",
  "credit_score": 639,
  "score_category": "good",
  "breakdown": {
    "satellite_performance": {
      "score": 158,
      "weight": "25%",
      "factors": {
        "ndvi_contribution": 57.6,
        "soil_moisture_contribution": 39.2,
        "environmental_contribution": 67.1
      }
    },
    "crop_performance": {
      "score": 142,
      "weight": "20%",
      "average_grade": "B+",
      "yield_performance": "Above Average"
    },
    "financial_history": {
      "score": 156,
      "weight": "20%",
      "repayment_rate": 94.5,
      "outstanding_debt": "Low"
    },
    "market_performance": {
      "score": 89,
      "weight": "15%",
      "customer_satisfaction": 4.2,
      "delivery_success": 92.1
    },
    "technology_adoption": {
      "score": 56,
      "weight": "10%",
      "adoption_rate": 62.3
    },
    "experience_bonus": {
      "score": 35,
      "weight": "5%",
      "level": "Experienced"
    },
    "verification_bonus": {
      "score": 45,
      "weight": "5%",
      "status": "Verified"
    }
  },
  "recommendations": [
    "Consider adopting more precision agriculture tools",
    "Maintain excellent repayment history",
    "Explore organic certification for premium pricing"
  ]
}
```

### GET /farmer-leaderboard
Get farmer credit score rankings.

**Query Parameters:**
- `limit` (optional): Number of farmers to return, default 10
- `state` (optional): Filter by state

**Response:**
```json
[
  {
    "rank": 1,
    "farmer_id": "FARMER_59061BBC",
    "name": "Manoj Patil",
    "location": "Nashik, Maharashtra",
    "agriculture_credit_score": 691,
    "score_category": "good",
    "farming_experience": "15+ years",
    "primary_crops": ["cotton", "sugarcane"],
    "verification_status": "verified"
  }
]
```

### GET /credit-score-analytics
Get overall credit score analytics.

**Response:**
```json
{
  "status": "success",
  "analytics": {
    "distribution": {
      "excellent": 0,
      "very_good": 0,
      "good": 5,
      "fair": 0,
      "poor": 0
    },
    "average_score": 668.8,
    "score_trends": {
      "improving": 3,
      "stable": 2,
      "declining": 0
    },
    "regional_averages": {
      "Punjab": 639,
      "Maharashtra": 691,
      "Uttar Pradesh": 658,
      "Haryana": 687,
      "Madhya Pradesh": 669
    },
    "top_performers": [...],
    "insights": [
      "Maharashtra farmers show highest average scores",
      "Technology adoption correlates with higher scores",
      "Verified farmers average 50 points higher"
    ]
  }
}
```

## Business Intelligence APIs

### GET /business-intel/market-intelligence
Get comprehensive market intelligence.

**Response:**
```json
{
  "status": "success",
  "intelligence": {
    "market_overview": {
      "total_market_size": "₹2.1 Trillion",
      "growth_rate": "12.5% YoY",
      "active_participants": 15420,
      "transaction_volume": "89.4K tonnes/month"
    },
    "price_trends": {
      "wheat": {
        "current": 2150,
        "trend": "up",
        "change": 8.5
      },
      "rice": {
        "current": 3200,
        "trend": "stable",
        "change": 1.2
      }
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
  },
  "generated_at": "2025-08-27T01:52:33.014245",
  "ai_powered": true
}
```

### GET /business-intel/seller-verification/{seller_id}
Get seller verification and risk assessment.

**Response:**
```json
{
  "seller_id": "seller_1",
  "verification_status": "verified",
  "risk_level": "low",
  "trust_score": 8.9,
  "verification_details": {
    "identity_verified": true,
    "business_registration": true,
    "bank_account_verified": true,
    "references_checked": true,
    "quality_certifications": ["ISO 9001", "Organic Certification"]
  },
  "performance_metrics": {
    "delivery_success_rate": 96.8,
    "customer_satisfaction": 4.8,
    "dispute_resolution_time": "2.3 days",
    "return_rate": 1.2
  },
  "recommendations": [
    "Excellent seller with consistent quality",
    "Recommended for bulk purchases",
    "Strong track record in organic products"
  ]
}
```

### GET /business-intel/procurement-recommendations
Get AI-powered procurement recommendations.

**Response:**
```json
{
  "status": "success",
  "recommendations": {
    "seasonal_opportunities": [
      {
        "product": "Organic Wheat",
        "reason": "Post-harvest surplus, 15% below market price",
        "action": "Bulk purchase recommended",
        "timeframe": "Next 2 weeks",
        "potential_savings": "12-18%"
      }
    ],
    "supplier_recommendations": [
      {
        "seller_id": "seller_1",
        "name": "Rajesh Kumar",
        "specialty": "Premium Basmati Rice",
        "trust_score": 8.9,
        "avg_discount": "8%",
        "delivery_reliability": "98%"
      }
    ],
    "market_timing": {
      "best_buy_period": "March-April (Post Rabi harvest)",
      "avoid_period": "August-September (Monsoon impact)",
      "bulk_discounts_available": true
    },
    "quality_alerts": [
      "Premium grade rice available from Punjab region",
      "Organic certification surge in Maharashtra"
    ]
  },
  "ai_confidence": 0.87,
  "generated_at": "2025-08-27T01:52:33.014245"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server internal error
- `INVALID_FILE`: File upload validation failed

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

## File Upload Specifications

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

### File Size Limits
- Maximum file size: 10MB per image
- Maximum files per request: 5 images

### Image Processing
- Automatic resizing for thumbnails
- Compression for web optimization
- Validation for malicious content

---

**API Version:** 2.0.0  
**Last Updated:** August 27, 2025
