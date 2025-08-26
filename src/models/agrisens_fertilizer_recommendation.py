"""
AgriSens Fertilizer Recommendation Integration
Soil quality analysis and crop-specific nutrient optimization
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FertilizerType(Enum):
    """Types of fertilizers"""
    UREA = "Urea"
    DAP = "DAP"
    MOP = "MOP"
    COMPLEX = "Complex"
    ORGANIC = "Organic"
    BIOFERTILIZER = "Biofertilizer"

@dataclass
class SoilAnalysis:
    """Comprehensive soil analysis results"""
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_matter: float
    moisture_content: float
    soil_type: str
    deficiencies: List[str]
    excesses: List[str]
    health_score: float  # 0-100

@dataclass
class FertilizerRecommendation:
    """Detailed fertilizer recommendation"""
    primary_fertilizer: FertilizerType
    secondary_fertilizers: List[FertilizerType]
    npk_ratio: str
    application_rate: float  # kg/hectare
    application_timing: List[str]
    application_method: str
    cost_estimate: float  # rupees/hectare
    expected_yield_increase: float  # percentage
    environmental_impact: str
    organic_alternatives: List[str]

@dataclass
class NutrientPlan:
    """Complete nutrient management plan"""
    crop_type: str
    growth_stage: str
    nutrient_requirements: Dict[str, float]
    current_status: SoilAnalysis
    recommendations: List[FertilizerRecommendation]
    monitoring_schedule: List[str]
    total_cost: float
    expected_roi: float

class AgriSensFertilizerModel:
    """AgriSens fertilizer recommendation model"""
    
    def __init__(self):
        self.fertilizer_database = self._load_fertilizer_database()
        self.crop_requirements = self._load_crop_requirements()
        self.soil_standards = self._load_soil_standards()
        logger.info("AgriSens Fertilizer Model initialized")
    
    def _load_fertilizer_database(self) -> Dict[str, Dict[str, Any]]:
        """Load fertilizer database with properties and costs"""
        return {
            "Urea": {
                "npk": (46, 0, 0),
                "cost_per_kg": 6.50,
                "solubility": "high",
                "best_for": ["nitrogen_deficiency"],
                "application_methods": ["broadcasting", "side_dressing", "foliar"],
                "environmental_impact": "moderate",
                "organic": False
            },
            "DAP": {
                "npk": (18, 46, 0),
                "cost_per_kg": 24.00,
                "solubility": "medium",
                "best_for": ["phosphorus_deficiency", "startup_growth"],
                "application_methods": ["broadcasting", "drilling"],
                "environmental_impact": "low",
                "organic": False
            },
            "MOP": {
                "npk": (0, 0, 60),
                "cost_per_kg": 17.50,
                "solubility": "high",
                "best_for": ["potassium_deficiency", "fruit_development"],
                "application_methods": ["broadcasting", "side_dressing"],
                "environmental_impact": "low",
                "organic": False
            },
            "NPK_10-26-26": {
                "npk": (10, 26, 26),
                "cost_per_kg": 22.00,
                "solubility": "medium",
                "best_for": ["balanced_nutrition", "root_development"],
                "application_methods": ["broadcasting", "drilling"],
                "environmental_impact": "moderate",
                "organic": False
            },
            "Vermicompost": {
                "npk": (1.5, 1.0, 1.5),
                "cost_per_kg": 8.00,
                "solubility": "slow",
                "best_for": ["soil_health", "organic_matter"],
                "application_methods": ["broadcasting", "incorporation"],
                "environmental_impact": "positive",
                "organic": True
            },
            "Neem_Cake": {
                "npk": (5.2, 1.0, 1.4),
                "cost_per_kg": 25.00,
                "solubility": "slow",
                "best_for": ["organic_nitrogen", "pest_deterrent"],
                "application_methods": ["broadcasting", "incorporation"],
                "environmental_impact": "positive", 
                "organic": True
            }
        }
    
    def _load_crop_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load crop-specific nutrient requirements"""
        return {
            "Rice": {
                "npk_requirements": {"N": 120, "P": 60, "K": 40},
                "critical_stages": ["tillering", "panicle_initiation", "grain_filling"],
                "deficiency_sensitivity": {"N": "high", "P": "medium", "K": "medium"},
                "optimal_ph": (5.5, 6.5),
                "growth_duration": 120
            },
            "Wheat": {
                "npk_requirements": {"N": 120, "P": 60, "K": 40},
                "critical_stages": ["crown_root_initiation", "jointing", "grain_filling"],
                "deficiency_sensitivity": {"N": "high", "P": "high", "K": "medium"},
                "optimal_ph": (6.0, 7.5),
                "growth_duration": 150
            },
            "Cotton": {
                "npk_requirements": {"N": 150, "P": 75, "K": 75},
                "critical_stages": ["squaring", "flowering", "boll_development"],
                "deficiency_sensitivity": {"N": "high", "P": "medium", "K": "high"},
                "optimal_ph": (5.8, 8.0),
                "growth_duration": 180
            },
            "Maize": {
                "npk_requirements": {"N": 150, "P": 75, "K": 60},
                "critical_stages": ["v6_stage", "tasseling", "grain_filling"],
                "deficiency_sensitivity": {"N": "very_high", "P": "high", "K": "medium"},
                "optimal_ph": (6.0, 6.8),
                "growth_duration": 110
            },
            "Sugarcane": {
                "npk_requirements": {"N": 200, "P": 75, "K": 150},
                "critical_stages": ["tillering", "grand_growth", "maturation"],
                "deficiency_sensitivity": {"N": "high", "P": "medium", "K": "very_high"},
                "optimal_ph": (6.5, 7.5),
                "growth_duration": 365
            },
            "Tomato": {
                "npk_requirements": {"N": 100, "P": 50, "K": 100},
                "critical_stages": ["transplanting", "flowering", "fruit_development"],
                "deficiency_sensitivity": {"N": "high", "P": "high", "K": "very_high"},
                "optimal_ph": (6.0, 6.8),
                "growth_duration": 120
            }
        }
    
    def _load_soil_standards(self) -> Dict[str, Dict[str, Any]]:
        """Load soil nutrient standards for classification"""
        return {
            "nitrogen": {
                "very_low": (0, 150),
                "low": (150, 300),
                "medium": (300, 450),
                "high": (450, 600),
                "very_high": (600, float('inf'))
            },
            "phosphorus": {
                "very_low": (0, 10),
                "low": (10, 20),
                "medium": (20, 40),
                "high": (40, 60),
                "very_high": (60, float('inf'))
            },
            "potassium": {
                "very_low": (0, 100),
                "low": (100, 200),
                "medium": (200, 350),
                "high": (350, 500),
                "very_high": (500, float('inf'))
            },
            "ph": {
                "very_acidic": (0, 5.0),
                "acidic": (5.0, 6.0),
                "slightly_acidic": (6.0, 6.5),
                "neutral": (6.5, 7.5),
                "slightly_alkaline": (7.5, 8.0),
                "alkaline": (8.0, 9.0),
                "very_alkaline": (9.0, 14.0)
            }
        }
    
    def analyze_soil(self, soil_data: Dict[str, float]) -> SoilAnalysis:
        """Comprehensive soil analysis"""
        # Extract soil parameters
        nitrogen = soil_data.get('nitrogen', 0)
        phosphorus = soil_data.get('phosphorus', 0)
        potassium = soil_data.get('potassium', 0)
        ph = soil_data.get('ph', 7.0)
        organic_matter = soil_data.get('organic_matter', 2.0)
        moisture = soil_data.get('moisture_content', 50.0)
        
        # Classify nutrient levels
        n_level = self._classify_nutrient_level('nitrogen', nitrogen)
        p_level = self._classify_nutrient_level('phosphorus', phosphorus)
        k_level = self._classify_nutrient_level('potassium', potassium)
        ph_level = self._classify_nutrient_level('ph', ph)
        
        # Identify deficiencies and excesses
        deficiencies = []
        excesses = []
        
        if n_level in ['very_low', 'low']:
            deficiencies.append('nitrogen')
        elif n_level == 'very_high':
            excesses.append('nitrogen')
            
        if p_level in ['very_low', 'low']:
            deficiencies.append('phosphorus')
        elif p_level == 'very_high':
            excesses.append('phosphorus')
            
        if k_level in ['very_low', 'low']:
            deficiencies.append('potassium')
        elif k_level == 'very_high':
            excesses.append('potassium')
        
        if ph_level in ['very_acidic', 'acidic']:
            deficiencies.append('ph_low')
        elif ph_level in ['alkaline', 'very_alkaline']:
            deficiencies.append('ph_high')
        
        # Calculate soil health score
        health_score = self._calculate_soil_health_score(
            n_level, p_level, k_level, ph_level, organic_matter
        )
        
        return SoilAnalysis(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph=ph,
            organic_matter=organic_matter,
            moisture_content=moisture,
            soil_type=soil_data.get('soil_type', 'loamy'),
            deficiencies=deficiencies,
            excesses=excesses,
            health_score=health_score
        )
    
    def recommend_fertilizer(
        self, 
        crop_type: str, 
        soil_analysis: SoilAnalysis,
        growth_stage: str = "planting",
        budget_constraint: Optional[float] = None,
        organic_preference: bool = False
    ) -> NutrientPlan:
        """Generate comprehensive fertilizer recommendations"""
        
        # Get crop requirements
        crop_info = self.crop_requirements.get(crop_type, self.crop_requirements["Rice"])
        
        # Calculate nutrient needs
        nutrient_needs = self._calculate_nutrient_needs(crop_info, soil_analysis, growth_stage)
        
        # Generate fertilizer recommendations
        recommendations = self._generate_fertilizer_recommendations(
            nutrient_needs, soil_analysis, organic_preference, budget_constraint
        )
        
        # Calculate costs and ROI
        total_cost = sum(rec.cost_estimate for rec in recommendations)
        expected_yield_increase = self._estimate_yield_increase(recommendations)
        expected_roi = self._calculate_roi(total_cost, expected_yield_increase, crop_type)
        
        # Create monitoring schedule
        monitoring_schedule = self._create_monitoring_schedule(crop_info, growth_stage)

        # Return complete nutrient plan
        return NutrientPlan(
            crop_type=crop_type,
            growth_stage=growth_stage,
            nutrient_requirements=nutrient_needs,
            current_status=soil_analysis,
            recommendations=recommendations,
            monitoring_schedule=monitoring_schedule,
            total_cost=total_cost,
            expected_roi=expected_roi
        )
    
    def _classify_nutrient_level(self, nutrient: str, value: float) -> str:
        """Classify nutrient level based on standards"""
        standards = self.soil_standards.get(nutrient, {})
        
        for level, (min_val, max_val) in standards.items():
            if min_val <= value < max_val:
                return level
                
        # Default if no match found
        return "medium"
    
    def _calculate_soil_health_score(self, n_level: str, p_level: str, k_level: str, ph_level: str, organic_matter: float) -> float:
        """Calculate overall soil health score (0-100)"""
        # Base score starts at 60
        score = 60
        
        # Add or subtract based on nutrient levels
        nutrient_scores = {
            'very_low': -20,
            'low': -10,
            'medium': 0,
            'high': 5,
            'very_high': -5
        }
        
        # Add nutrient level scores
        score += nutrient_scores.get(n_level, 0)
        score += nutrient_scores.get(p_level, 0)
        score += nutrient_scores.get(k_level, 0)
        
        # Add pH level scores
        ph_scores = {
            'very_acidic': -15,
            'acidic': -10,
            'slightly_acidic': 0,
            'neutral': 15,
            'slightly_alkaline': 0,
            'alkaline': -10,
            'very_alkaline': -15
        }
        score += ph_scores.get(ph_level, 0)
        
        # Add organic matter score (0-20 points)
        # Ideal organic matter is 3-5%
        if organic_matter < 1:
            score += 0
        elif organic_matter < 2:
            score += 5
        elif organic_matter < 3:
            score += 10
        elif organic_matter <= 5:
            score += 20
        elif organic_matter <= 8:
            score += 10
        else:
            score += 5
            
        # Ensure score is in valid range
        return max(0, min(100, score))
    
    def _calculate_nutrient_needs(self, crop_info: Dict, soil_analysis: SoilAnalysis, growth_stage: str) -> Dict[str, float]:
        """Calculate nutrient needs based on crop requirements and soil analysis"""
        # Get crop requirements
        npk_requirements = crop_info.get('npk_requirements', {'N': 100, 'P': 50, 'K': 50})
        
        # Adjust based on growth stage
        critical_stages = crop_info.get('critical_stages', [])
        stage_adjustments = {
            # Planting/early stages need more P
            'planting': {'N': 0.5, 'P': 1.0, 'K': 0.5},
            'germination': {'N': 0.5, 'P': 1.0, 'K': 0.5},
            'seedling': {'N': 0.7, 'P': 0.7, 'K': 0.5},
            
            # Vegetative stages need more N
            'vegetative': {'N': 1.0, 'P': 0.5, 'K': 0.7},
            'tillering': {'N': 1.0, 'P': 0.5, 'K': 0.7},
            'stem_elongation': {'N': 1.0, 'P': 0.5, 'K': 0.7},
            
            # Flowering/fruiting needs more K
            'flowering': {'N': 0.5, 'P': 0.7, 'K': 1.0},
            'fruit_development': {'N': 0.5, 'P': 0.7, 'K': 1.0},
            'grain_filling': {'N': 0.4, 'P': 0.4, 'K': 1.0},
            
            # Default is balanced
            'default': {'N': 0.7, 'P': 0.7, 'K': 0.7}
        }
        
        # Get adjustments for current growth stage
        adjustments = stage_adjustments.get(growth_stage.lower(), stage_adjustments['default'])
        
        # Calculate needs based on requirements, soil status, and growth stage
        n_need = self._calculate_single_nutrient_need('N', npk_requirements['N'], 
                                                    soil_analysis.nitrogen, adjustments['N'])
        p_need = self._calculate_single_nutrient_need('P', npk_requirements['P'], 
                                                    soil_analysis.phosphorus, adjustments['P'])
        k_need = self._calculate_single_nutrient_need('K', npk_requirements['K'], 
                                                    soil_analysis.potassium, adjustments['K'])
        
        return {
            'N': n_need,
            'P': p_need,
            'K': k_need
        }
    
    def _calculate_single_nutrient_need(self, nutrient: str, requirement: float, 
                                      soil_level: float, stage_factor: float) -> float:
        """Calculate need for a single nutrient"""
        # Base calculation: required - existing (soil)
        base_need = max(0, requirement - soil_level)
        
        # Apply growth stage factor
        return base_need * stage_factor
    
    def _generate_fertilizer_recommendations(
        self, 
        nutrient_needs: Dict[str, float], 
        soil_analysis: SoilAnalysis,
        organic_preference: bool,
        budget_constraint: Optional[float]
    ) -> List[FertilizerRecommendation]:
        """Generate optimal fertilizer recommendations based on needs"""
        recommendations = []
        
        # Filter fertilizers based on organic preference
        available_fertilizers = {}
        for name, data in self.fertilizer_database.items():
            if organic_preference and not data.get('organic', False):
                continue
            available_fertilizers[name] = data
        
        # If no fertilizers match the organic preference, use all
        if not available_fertilizers:
            available_fertilizers = self.fertilizer_database
        
        # Generate primary fertilizer recommendation based on greatest need
        primary_fertilizer = self._select_primary_fertilizer(nutrient_needs, available_fertilizers)
        
        # Generate secondary recommendations to balance nutrients
        secondary_fertilizers = self._select_secondary_fertilizers(
            nutrient_needs, primary_fertilizer, available_fertilizers
        )
        
        # Create recommendation for primary fertilizer
        primary_data = self.fertilizer_database.get(primary_fertilizer, {})
        primary_npk = primary_data.get('npk', (0, 0, 0))
        
        # Calculate application rate
        main_nutrient = 'N'  # Default
        if primary_npk[1] > primary_npk[0] and primary_npk[1] > primary_npk[2]:
            main_nutrient = 'P'
        elif primary_npk[2] > primary_npk[0] and primary_npk[2] > primary_npk[1]:
            main_nutrient = 'K'
            
        application_rate = self._calculate_application_rate(
            nutrient_needs.get(main_nutrient, 0), 
            primary_npk[{'N': 0, 'P': 1, 'K': 2}[main_nutrient]]
        )
        
        # Calculate cost
        cost_estimate = application_rate * primary_data.get('cost_per_kg', 10) / 100
        
        # Create recommendation object
        primary_rec = FertilizerRecommendation(
            primary_fertilizer=FertilizerType(primary_fertilizer),
            secondary_fertilizers=[FertilizerType(f) for f in secondary_fertilizers],
            npk_ratio=f"{primary_npk[0]}-{primary_npk[1]}-{primary_npk[2]}",
            application_rate=application_rate,
            application_timing=self._determine_application_timing(primary_fertilizer),
            application_method=primary_data.get('application_methods', ['broadcasting'])[0],
            cost_estimate=cost_estimate,
            expected_yield_increase=self._estimate_yield_increase_for_fertilizer(primary_fertilizer, application_rate),
            environmental_impact=primary_data.get('environmental_impact', 'moderate'),
            organic_alternatives=self._find_organic_alternatives(primary_fertilizer) if not primary_data.get('organic', False) else []
        )
        
        recommendations.append(primary_rec)
        
        # Create recommendations for secondary fertilizers if needed
        for fert in secondary_fertilizers[:2]:  # Limit to top 2 secondary fertilizers
            fert_data = self.fertilizer_database.get(fert, {})
            fert_npk = fert_data.get('npk', (0, 0, 0))
            
            # Create simplified recommendation
            sec_rec = FertilizerRecommendation(
                primary_fertilizer=FertilizerType(fert),
                secondary_fertilizers=[],
                npk_ratio=f"{fert_npk[0]}-{fert_npk[1]}-{fert_npk[2]}",
                application_rate=application_rate * 0.5,  # Half the primary rate
                application_timing=self._determine_application_timing(fert),
                application_method=fert_data.get('application_methods', ['broadcasting'])[0],
                cost_estimate=application_rate * 0.5 * fert_data.get('cost_per_kg', 10) / 100,
                expected_yield_increase=self._estimate_yield_increase_for_fertilizer(fert, application_rate * 0.5),
                environmental_impact=fert_data.get('environmental_impact', 'moderate'),
                organic_alternatives=[]
            )
            recommendations.append(sec_rec)
        
        # Check budget constraint if provided
        if budget_constraint:
            total_cost = sum(rec.cost_estimate for rec in recommendations)
            if total_cost > budget_constraint:
                # Scale down recommendations to fit budget
                scale_factor = budget_constraint / total_cost
                for rec in recommendations:
                    rec.application_rate *= scale_factor
                    rec.cost_estimate *= scale_factor
                    rec.expected_yield_increase *= (0.5 + 0.5 * scale_factor)  # Adjust yield increase
        
        return recommendations
        
    def _select_primary_fertilizer(self, nutrient_needs: Dict[str, float], available_fertilizers: Dict) -> str:
        """Select primary fertilizer based on greatest need"""
        # Find the most needed nutrient
        max_need = 0
        primary_need = 'N'
        
        for nutrient, need in nutrient_needs.items():
            if need > max_need:
                max_need = need
                primary_need = nutrient
        
        # Find fertilizer that best addresses this need
        best_score = 0
        best_fertilizer = next(iter(available_fertilizers))  # Default
        
        for name, data in available_fertilizers.items():
            npk = data.get('npk', (0, 0, 0))
            
            # Score based on matching the primary need
            if primary_need == 'N':
                score = npk[0]
            elif primary_need == 'P':
                score = npk[1]
            elif primary_need == 'K':
                score = npk[2]
            
            if score > best_score:
                best_score = score
                best_fertilizer = name
        
        return best_fertilizer
    
    def _select_secondary_fertilizers(self, nutrient_needs: Dict[str, float], primary: str, available_fertilizers: Dict) -> List[str]:
        """Select secondary fertilizers to complement primary"""
        # Remove primary fertilizer from available
        available = {k: v for k, v in available_fertilizers.items() if k != primary}
        
        # Get primary fertilizer's NPK
        primary_npk = available_fertilizers.get(primary, {}).get('npk', (0, 0, 0))
        
        # Calculate remaining needs after primary
        remaining_needs = nutrient_needs.copy()
        
        # Update remaining needs based on primary
        remaining_needs['N'] = max(0, remaining_needs['N'] - primary_npk[0])
        remaining_needs['P'] = max(0, remaining_needs['P'] - primary_npk[1])
        remaining_needs['K'] = max(0, remaining_needs['K'] - primary_npk[2])
        
        # Score secondary fertilizers based on remaining needs
        scores = {}
        for name, data in available.items():
            npk = data.get('npk', (0, 0, 0))
            
            # Score based on how well it addresses remaining needs
            score = (npk[0] * remaining_needs['N'] + 
                     npk[1] * remaining_needs['P'] + 
                     npk[2] * remaining_needs['K'])
            
            scores[name] = score
        
        # Sort by score and return top 3
        return [name for name, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)][:3]
    
    def _calculate_application_rate(self, nutrient_need: float, nutrient_percent: float) -> float:
        """Calculate application rate in kg/hectare"""
        if nutrient_percent <= 0:
            return 100  # Default rate if no nutrient
        
        # Convert percent to decimal (e.g., 46% -> 0.46)
        nutrient_decimal = nutrient_percent / 100
        
        # Calculate rate: need (kg/ha) / nutrient content
        return nutrient_need / nutrient_decimal
        
    def _determine_application_timing(self, fertilizer: str) -> List[str]:
        """Determine optimal application timing"""
        fert_data = self.fertilizer_database.get(fertilizer, {})
        
        # Basic timings based on fertilizer type
        if "nitrogen" in fertilizer.lower() or fertilizer == "Urea":
            return ["Pre-planting", "Vegetative stage"]
        elif "phosphorus" in fertilizer.lower() or fertilizer == "DAP":
            return ["Pre-planting"]
        elif "potassium" in fertilizer.lower() or fertilizer == "MOP":
            return ["Pre-planting", "Before flowering"]
        elif "organic" in fertilizer.lower():
            return ["2-4 weeks before planting"]
        else:
            return ["Pre-planting", "Mid-season as needed"]
    
    def _estimate_yield_increase_for_fertilizer(self, fertilizer: str, application_rate: float) -> float:
        """Estimate yield increase percentage for fertilizer application"""
        # Base yield increase from 5-15% depending on fertilizer and rate
        fert_data = self.fertilizer_database.get(fertilizer, {})
        
        # Base increase factors for different types
        if fertilizer == "Urea" or "nitrogen" in fertilizer.lower():
            base = 10
        elif fertilizer == "DAP" or "phosphorus" in fertilizer.lower():
            base = 8
        elif fertilizer == "MOP" or "potassium" in fertilizer.lower():
            base = 7
        elif "organic" in fertilizer.lower():
            base = 5
        else:
            base = 6
        
        # Adjust based on application rate (diminishing returns)
        rate_factor = min(1.5, application_rate / 100)
        
        return base * rate_factor
    
    def _estimate_yield_increase(self, recommendations: List[FertilizerRecommendation]) -> float:
        """Estimate overall yield increase from fertilizer recommendations"""
        # Base increase from primary recommendation
        if not recommendations:
            return 0.0
            
        primary_increase = recommendations[0].expected_yield_increase
        
        # Add diminishing returns from secondary recommendations
        secondary_increase = sum(rec.expected_yield_increase * 0.5 for rec in recommendations[1:])
        
        # Combined increase with cap
        return min(25.0, primary_increase + secondary_increase)
    
    def _calculate_roi(self, total_cost: float, yield_increase: float, crop_type: str) -> float:
        """Calculate ROI for fertilizer application"""
        # Approximate crop values per hectare in rupees
        crop_values = {
            "Rice": 75000,
            "Wheat": 65000,
            "Cotton": 90000,
            "Maize": 60000,
            "Sugarcane": 120000,
            "Tomato": 150000,
            "default": 70000
        }
        
        # Get base value for crop
        base_value = crop_values.get(crop_type, crop_values["default"])
        
        # Calculate expected increase in value
        value_increase = base_value * (yield_increase / 100)
        
        # Calculate ROI
        if total_cost <= 0:
            return 0.0
            
        roi = ((value_increase - total_cost) / total_cost) * 100
        return max(0.0, roi)
    
    def _find_organic_alternatives(self, chemical_fertilizer: str) -> List[str]:
        """Find organic alternatives to chemical fertilizers"""
        if chemical_fertilizer == "Urea":
            return ["Vermicompost", "Blood Meal", "Fish Emulsion"]
        elif chemical_fertilizer == "DAP":
            return ["Bone Meal", "Rock Phosphate", "Fish Bone Meal"]
        elif chemical_fertilizer == "MOP":
            return ["Wood Ash", "Seaweed Extract", "Banana Peels"]
        else:
            return ["Compost", "Farm Yard Manure"]
    
    def _create_monitoring_schedule(self, crop_info: Dict, growth_stage: str) -> List[str]:
        """Create a monitoring schedule based on crop and growth stage"""
        # Get crop growth duration
        duration = crop_info.get('growth_duration', 120)  # Default 120 days
        
        # Get critical stages
        critical_stages = crop_info.get('critical_stages', [])
        
        # Create monitoring points
        schedule = []
        
        # Initial monitoring
        schedule.append("Initial soil testing before planting")
        
        # Add monitoring at critical stages
        for stage in critical_stages:
            schedule.append(f"Monitor during {stage.replace('_', ' ')} stage")
        
        # Add midseason monitoring if not covered by critical stages
        if duration > 60 and not any("mid" in s.lower() for s in schedule):
            schedule.append(f"Mid-season monitoring (around day {duration//2})")
            
        # Add final monitoring
        schedule.append("Post-harvest soil testing for next season planning")
        
        return schedule

# Global instance
_agrisens_fertilizer_model = None

def get_agrisens_fertilizer_model() -> AgriSensFertilizerModel:
    """Get singleton instance of AgriSens fertilizer model"""
    global _agrisens_fertilizer_model
    if _agrisens_fertilizer_model is None:
        _agrisens_fertilizer_model = AgriSensFertilizerModel()
        logger.info("AgriSens Fertilizer Model initialized successfully")
    return _agrisens_fertilizer_model

def enhance_input_materials_with_fertilizer_recommendation(
    crop_type: str,
    soil_data: Dict[str, float],
    growth_stage: str = "planting",
    budget_constraint: Optional[float] = None,
    organic_preference: bool = False,
    location_data: Optional[Dict[str, Any]] = None
) -> NutrientPlan:
    """
    Enhance input materials agent with AgriSens fertilizer recommendations
    
    Args:
        crop_type: Type of crop being grown
        soil_data: Soil analysis data (NPK, pH, etc.)
        growth_stage: Current growth stage
        budget_constraint: Maximum budget for fertilizers
        organic_preference: Prefer organic fertilizers
        location_data: Location for regional adjustments
    
    Returns:
        NutrientPlan with comprehensive fertilizer recommendations
    """
    model = get_agrisens_fertilizer_model()
    
    # Analyze soil
    soil_analysis = model.analyze_soil(soil_data)
    
    # Get fertilizer recommendations
    nutrient_plan = model.recommend_fertilizer(
        crop_type=crop_type,
        soil_analysis=soil_analysis,
        growth_stage=growth_stage,
        budget_constraint=budget_constraint,
        organic_preference=organic_preference
    )
    
    logger.info(f"Fertilizer recommendations for {crop_type}: {len(nutrient_plan.recommendations)} options")
    logger.info(f"Soil health score: {soil_analysis.health_score}/100")
    logger.info(f"Expected ROI: {nutrient_plan.expected_roi}%")
    
    return nutrient_plan
