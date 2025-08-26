"""
AgriSens Crop Recommendation Integration
High-accuracy Random Forest model with NPK analysis (99.55% accuracy)
"""

import pandas as pd
import numpy as np
import joblib
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class NPKAnalysis:
    """NPK soil analysis results"""
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    rainfall: float
    npk_recommendation: str
    soil_health_score: float

@dataclass
class AgriSensRecommendation:
    """AgriSens ML crop recommendation"""
    crop: str
    confidence: float
    npk_analysis: NPKAnalysis
    model_used: str
    accuracy: float
    satellite_enhancement: Optional[Dict[str, Any]] = None

class AgriSensCropModel:
    """AgriSens crop recommendation model wrapper"""
    
    def __init__(self):
        self.models = {}
        self.model_accuracies = {
            'RandomForest': 0.9955,
            'NBClassifier': 0.9909,
            'XGBoost': 0.9909,
            'KNeighborsClassifier': 0.975,
            'DecisionTree': 0.90
        }
        self.crop_mapping = {
            'rice': 'Rice',
            'wheat': 'Wheat',
            'cotton': 'Cotton',
            'maize': 'Maize',
            'sugarcane': 'Sugarcane',
            'jute': 'Jute',
            'coconut': 'Coconut',
            'apple': 'Apple',
            'banana': 'Banana',
            'grapes': 'Grapes',
            'chickpea': 'Chickpea',
            'kidneybeans': 'Kidney Beans',
            'blackgram': 'Black Gram',
            'coffee': 'Coffee'
        }
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained AgriSens ML models"""
        model_path = "/home/hari/Music/Multi-Agent-Agriculture-Systems/models/agrisens/CROP-RECOMMENDATION"
        
        model_files = {
            'RandomForest': 'RF.pkl',
            'NBClassifier': 'NBClassifier.pkl',
            'XGBoost': 'XGBoost.pkl',
            'KNeighborsClassifier': 'KNeighborsClassifier.pkl',
            'DecisionTree': 'DecisionTree.pkl'
        }
        
        for model_name, file_name in model_files.items():
            model_file = os.path.join(model_path, file_name)
            try:
                self.models[model_name] = joblib.load(model_file)
                logger.info(f"Loaded {model_name} model with {self.model_accuracies[model_name]:.2%} accuracy")
            except Exception as e:
                logger.warning(f"Could not load {model_name}: {e}")
    
    def predict_crop(self, npk_data: Dict[str, float], use_ensemble: bool = True) -> AgriSensRecommendation:
        """
        Predict optimal crop using AgriSens ML models
        
        Args:
            npk_data: Dict with keys: N, P, K, temperature, humidity, ph, rainfall
            use_ensemble: Whether to use ensemble of models or just RandomForest
        
        Returns:
            AgriSensRecommendation with crop prediction and analysis
        """
        # Prepare input data
        features = np.array([[
            npk_data['N'],
            npk_data['P'], 
            npk_data['K'],
            npk_data['temperature'],
            npk_data['humidity'],
            npk_data['ph'],
            npk_data['rainfall']
        ]])
        
        if use_ensemble:
            return self._ensemble_prediction(features, npk_data)
        else:
            return self._single_model_prediction(features, npk_data, 'RandomForest')
    
    def _ensemble_prediction(self, features: np.ndarray, npk_data: Dict[str, float]) -> AgriSensRecommendation:
        """Use ensemble of models for prediction"""
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                pred = model.predict(features)[0]
                # Get prediction probabilities if available
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features)[0]
                    confidence = np.max(proba)
                else:
                    confidence = self.model_accuracies[model_name]
                
                predictions[model_name] = {
                    'crop': pred,
                    'confidence': confidence,
                    'accuracy': self.model_accuracies[model_name]
                }
            except Exception as e:
                logger.warning(f"Error with {model_name}: {e}")
        
        # Weight predictions by model accuracy
        crop_votes = {}
        total_weight = 0
        
        for model_name, pred_data in predictions.items():
            crop = pred_data['crop']
            weight = pred_data['accuracy'] * pred_data['confidence']
            
            if crop not in crop_votes:
                crop_votes[crop] = 0
            crop_votes[crop] += weight
            total_weight += weight
        
        # Get the highest weighted prediction
        best_crop = max(crop_votes.items(), key=lambda x: x[1])
        final_crop = best_crop[0]
        final_confidence = best_crop[1] / total_weight if total_weight > 0 else 0.0
        
        # Perform NPK analysis
        npk_analysis = self._analyze_npk(npk_data, final_crop)
        
        return AgriSensRecommendation(
            crop=self.crop_mapping.get(final_crop, final_crop.title()),
            confidence=final_confidence,
            npk_analysis=npk_analysis,
            model_used="Ensemble (Weighted)",
            accuracy=max(self.model_accuracies.values())
        )
    
    def _single_model_prediction(self, features: np.ndarray, npk_data: Dict[str, float], model_name: str) -> AgriSensRecommendation:
        """Use single model for prediction"""
        model = self.models[model_name]
        prediction = model.predict(features)[0]
        
        # Get confidence
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            confidence = np.max(proba)
        else:
            confidence = self.model_accuracies[model_name]
        
        # Perform NPK analysis
        npk_analysis = self._analyze_npk(npk_data, prediction)
        
        return AgriSensRecommendation(
            crop=self.crop_mapping.get(prediction, prediction.title()),
            confidence=confidence,
            npk_analysis=npk_analysis,
            model_used=model_name,
            accuracy=self.model_accuracies[model_name]
        )
    
    def _analyze_npk(self, npk_data: Dict[str, float], crop: str) -> NPKAnalysis:
        """Analyze NPK values and provide recommendations"""
        # NPK optimal ranges for different crops
        npk_requirements = {
            'rice': {'N': (80, 120), 'P': (40, 60), 'K': (40, 60)},
            'wheat': {'N': (80, 120), 'P': (40, 60), 'K': (40, 60)},
            'cotton': {'N': (120, 150), 'P': (60, 80), 'K': (60, 80)},
            'maize': {'N': (120, 180), 'P': (60, 80), 'K': (40, 60)},
            'sugarcane': {'N': (200, 250), 'P': (50, 75), 'K': (100, 150)},
            'default': {'N': (80, 120), 'P': (40, 60), 'K': (40, 60)}
        }
        
        requirements = npk_requirements.get(crop.lower(), npk_requirements['default'])
        
        # Analyze each nutrient
        n_status = self._analyze_nutrient_status(npk_data['N'], requirements['N'])
        p_status = self._analyze_nutrient_status(npk_data['P'], requirements['P'])
        k_status = self._analyze_nutrient_status(npk_data['K'], requirements['K'])
        
        # Generate recommendation
        recommendations = []
        if n_status != 'optimal':
            recommendations.append(f"Nitrogen: {n_status}")
        if p_status != 'optimal':
            recommendations.append(f"Phosphorus: {p_status}")
        if k_status != 'optimal':
            recommendations.append(f"Potassium: {k_status}")
        
        npk_recommendation = "; ".join(recommendations) if recommendations else "NPK levels are optimal"
        
        # Calculate soil health score
        n_score = self._calculate_nutrient_score(npk_data['N'], requirements['N'])
        p_score = self._calculate_nutrient_score(npk_data['P'], requirements['P'])
        k_score = self._calculate_nutrient_score(npk_data['K'], requirements['K'])
        ph_score = self._calculate_ph_score(npk_data['ph'])
        
        soil_health_score = (n_score + p_score + k_score + ph_score) / 4
        
        return NPKAnalysis(
            nitrogen=npk_data['N'],
            phosphorus=npk_data['P'],
            potassium=npk_data['K'],
            ph=npk_data['ph'],
            temperature=npk_data['temperature'],
            humidity=npk_data['humidity'],
            rainfall=npk_data['rainfall'],
            npk_recommendation=npk_recommendation,
            soil_health_score=soil_health_score
        )
    
    def _analyze_nutrient_status(self, value: float, optimal_range: Tuple[float, float]) -> str:
        """Analyze nutrient status against optimal range"""
        min_val, max_val = optimal_range
        if value < min_val * 0.8:
            return "severely deficient"
        elif value < min_val:
            return "deficient"
        elif value <= max_val:
            return "optimal"
        elif value <= max_val * 1.2:
            return "slightly high"
        else:
            return "excessive"
    
    def _calculate_nutrient_score(self, value: float, optimal_range: Tuple[float, float]) -> float:
        """Calculate nutrient score (0-1)"""
        min_val, max_val = optimal_range
        if min_val <= value <= max_val:
            return 1.0
        elif value < min_val:
            return max(0.0, value / min_val)
        else:
            return max(0.0, 1.0 - (value - max_val) / max_val)
    
    def _calculate_ph_score(self, ph: float) -> float:
        """Calculate pH score (optimal range 6.0-7.5)"""
        if 6.0 <= ph <= 7.5:
            return 1.0
        elif ph < 6.0:
            return max(0.0, ph / 6.0)
        else:
            return max(0.0, 1.0 - (ph - 7.5) / 2.5)

# Global instance
_agrisens_crop_model = None

def get_agrisens_crop_model() -> AgriSensCropModel:
    """Get singleton instance of AgriSens crop model"""
    global _agrisens_crop_model
    if _agrisens_crop_model is None:
        _agrisens_crop_model = AgriSensCropModel()
    return _agrisens_crop_model

def enhance_crop_selection_with_agrisens(
    location_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    satellite_data: Optional[Dict[str, Any]] = None
) -> AgriSensRecommendation:
    """
    Enhance crop selection using AgriSens ML models
    
    Args:
        location_data: Location information (lat, lon, etc.)
        soil_data: Soil parameters including NPK, pH
        weather_data: Weather parameters (temp, humidity, rainfall)
        satellite_data: Optional satellite data for enhancement
    
    Returns:
        AgriSensRecommendation with ML-based crop recommendation
    """
    model = get_agrisens_crop_model()
    
    # Prepare NPK data for prediction
    npk_data = {
        'N': soil_data.get('nitrogen', 80),
        'P': soil_data.get('phosphorus', 50),
        'K': soil_data.get('potassium', 50),
        'temperature': weather_data.get('temperature', 25),
        'humidity': weather_data.get('humidity', 75),
        'ph': soil_data.get('ph', 6.5),
        'rainfall': weather_data.get('rainfall', 200)
    }
    
    # Get ML prediction
    recommendation = model.predict_crop(npk_data, use_ensemble=True)
    
    # Enhance with satellite data if available
    if satellite_data:
        recommendation.satellite_enhancement = {
            'ndvi': satellite_data.get('ndvi'),
            'soil_moisture': satellite_data.get('soil_moisture'),
            'temperature_anomaly': satellite_data.get('temperature_anomaly'),
            'vegetation_health': satellite_data.get('vegetation_health')
        }
        
        # Adjust confidence based on satellite data
        if satellite_data.get('vegetation_health', 0) > 0.7:
            recommendation.confidence *= 1.1  # Boost confidence for healthy areas
        elif satellite_data.get('vegetation_health', 0) < 0.4:
            recommendation.confidence *= 0.9  # Reduce confidence for poor areas
    
    logger.info(f"AgriSens prediction: {recommendation.crop} (confidence: {recommendation.confidence:.2%})")
    
    return recommendation
