"""
<<<<<<< HEAD
AgriMitr Integration Tests
Test suite for validating the integration of AgriMitr models with our agent system.
=======
AgriSens Integration Tests
Test suite for validating the integration of AgriSens models with our agent system.
>>>>>>> upstream/main
"""

import unittest
import asyncio
import os
import json
import sys
import base64
from unittest.mock import patch, MagicMock
from io import BytesIO
from datetime import datetime
from PIL import Image
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.irrigation_agent import IrrigationAgent
from src.agents.disease_identification_agent import DiseaseIdentificationAgent
from src.core.agriculture_models import AgricultureQuery, Location, SoilType, CropType
<<<<<<< HEAD
from src.models.AgriMitr_crop_recommendation import AgriMitrCropModel
from src.models.AgriMitr_disease_identification import AgriMitrDiseaseModel
from src.models.AgriMitr_irrigation_scheduling import IrrigationModel


class TestAgriMitrIntegration(unittest.TestCase):
    """Test suite for AgriMitr model integration"""
=======
from src.models.agrisens_crop_recommendation import AgriSensCropModel
from src.models.agrisens_disease_identification import AgriSensDiseaseModel
from src.models.agrisens_irrigation_scheduling import IrrigationModel


class TestAgriSensIntegration(unittest.TestCase):
    """Test suite for AgriSens model integration"""
>>>>>>> upstream/main
    
    def setUp(self):
        """Set up test environment"""
        # Create a sample test image
        self.test_image = self._create_test_image()
        
        # Initialize agents
        self.crop_agent = CropSelectionAgent("crop-agent-1", "Crop Selection Agent")
        self.irrigation_agent = IrrigationAgent("irrigation-agent-1", "Irrigation Agent")
        self.disease_agent = DiseaseIdentificationAgent("disease-agent-1", "Disease Identification Agent")
        
        # Test query
        self.test_query = AgricultureQuery(
            query_id="test-query-1",
            query_text="What crops should I plant?",
            query_domain="crop_selection",
            location=Location(
                latitude=28.6139,  # New Delhi
                longitude=77.2090,
                address="New Delhi, India",
                region="Delhi"
            ),
            crop_type=CropType.WHEAT.value,
            soil_type=SoilType.LOAM.value,
            timestamp=datetime.now(),
            farm_size_acres=5.0
        )
        
    def _create_test_image(self):
        """Create a simple test image for disease testing"""
        # Create a 100x100 green image with some brown spots
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :] = [0, 128, 0]  # Green background
        
        # Add some brown spots (simulating disease)
        for i in range(20):
            x = np.random.randint(0, 100)
            y = np.random.randint(0, 100)
            radius = np.random.randint(2, 5)
            cv2 = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2 = cv2.circle(img, (x, y), radius, (42, 42, 165), -1)
        
        # Convert to bytes
        img_bytes = BytesIO()
        Image.fromarray(img).save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return base64.b64encode(img_bytes.read()).decode('utf-8')
        
<<<<<<< HEAD
    @patch('src.models.AgriMitr_crop_recommendation.get_crop_recommendation_model')
    def test_crop_selection_agent_with_AgriMitr(self, mock_get_model):
        """Test that crop selection agent uses AgriMitr models"""
=======
    @patch('src.models.agrisens_crop_recommendation.get_crop_recommendation_model')
    def test_crop_selection_agent_with_agrisens(self, mock_get_model):
        """Test that crop selection agent uses AgriSens models"""
>>>>>>> upstream/main
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            'crop': 'rice',
            'confidence': 0.95,
            'npk_analysis': {
                'nitrogen': 80,
                'phosphorus': 45,
                'potassium': 60,
                'ph': 6.5,
                'temperature': 24,
                'humidity': 80,
                'rainfall': 200,
                'npk_recommendation': 'Optimal for rice',
                'soil_health_score': 0.85
            },
            'model_used': 'RandomForest',
            'accuracy': 0.9955
        }
        mock_get_model.return_value = mock_model
        
        # Run the agent
        response = asyncio.run(self.crop_agent.process_query(self.test_query))
        
        # Verify results
        self.assertTrue(response.success)
        self.assertEqual(response.response_type, "crop_selection")
        self.assertIn('recommendations', response.data)
        
<<<<<<< HEAD
        # Check if AgriMitr model was used
        mock_get_model.assert_called_once()
        
    @patch('src.models.AgriMitr_irrigation_scheduling.get_irrigation_model')
    def test_irrigation_agent_with_AgriMitr(self, mock_get_model):
        """Test that irrigation agent uses AgriMitr models"""
=======
        # Check if AgriSens model was used
        mock_get_model.assert_called_once()
        
    @patch('src.models.agrisens_irrigation_scheduling.get_irrigation_model')
    def test_irrigation_agent_with_agrisens(self, mock_get_model):
        """Test that irrigation agent uses AgriSens models"""
>>>>>>> upstream/main
        # Mock the model
        mock_model = MagicMock()
        mock_model.optimize_schedule.return_value = {
            'schedule': [
                {
                    'date': '2025-08-26',
                    'amount': 25.5,
                    'duration_minutes': 60
                },
                {
                    'date': '2025-08-30',
                    'amount': 22.0,
                    'duration_minutes': 55
                }
            ],
            'total_water': 47.5,
            'efficiency': 0.85
        }
        mock_get_model.return_value = mock_model
        
        # Modify query for irrigation
        irrigation_query = self.test_query
        irrigation_query.query_domain = "irrigation"
        irrigation_query.query_text = "Create an irrigation schedule for my wheat crop"
        
        # Run the agent
        response = asyncio.run(self.irrigation_agent.process_query(irrigation_query))
        
        # Verify results
        self.assertTrue(response.success)
        self.assertEqual(response.response_type, "irrigation_schedule")
        self.assertIn('schedule', response.data)
        
<<<<<<< HEAD
        # Check if AgriMitr model was used
        mock_get_model.assert_called_once()
        
    @patch('src.models.AgriMitr_disease_identification.load_disease_model')
    def test_disease_identification_agent(self, mock_load_model):
        """Test disease identification with AgriMitr model"""
=======
        # Check if AgriSens model was used
        mock_get_model.assert_called_once()
        
    @patch('src.models.agrisens_disease_identification.load_disease_model')
    def test_disease_identification_agent(self, mock_load_model):
        """Test disease identification with AgriSens model"""
>>>>>>> upstream/main
        # Mock the model
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.01, 0.02, 0.85, 0.05, 0.07]])  # Mostly class 2
        mock_model.interpret_prediction.return_value = MagicMock(
            disease_name="Wheat Leaf Rust",
            confidence=85.0,
            affected_area_percentage=15.0,
            severity="moderate",
            disease_details={
                "symptoms": ["Reddish-brown pustules", "Yellowing leaves"],
                "treatments": ["Fungicide application", "Remove infected plants"],
                "prevention": ["Resistant varieties", "Crop rotation"]
            }
        )
        mock_load_model.return_value = mock_model
        
        # Modify query for disease identification
        disease_query = self.test_query
        disease_query.query_domain = "disease_identification"
        disease_query.query_text = "What disease is affecting my crop?"
        disease_query.image_data = self.test_image
        
        # Run the agent
        response = asyncio.run(self.disease_agent.process_query(disease_query))
        
        # Verify results
        self.assertTrue(response.success)
        self.assertEqual(response.response_type, "disease_identification")
        self.assertIn('disease', response.data)
        self.assertIn('recommendations', response.data)
        
<<<<<<< HEAD
        # Check if AgriMitr model was used
        mock_load_model.assert_called_once()

    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    @patch('src.models.AgriMitr_crop_recommendation.get_crop_recommendation_model')
    def test_satellite_data_integration(self, mock_get_crop_model, mock_get_satellite):
        """Test that satellite data is properly integrated with AgriMitr models"""
=======
        # Check if AgriSens model was used
        mock_load_model.assert_called_once()

    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    @patch('src.models.agrisens_crop_recommendation.get_crop_recommendation_model')
    def test_satellite_data_integration(self, mock_get_crop_model, mock_get_satellite):
        """Test that satellite data is properly integrated with AgriSens models"""
>>>>>>> upstream/main
        # Mock satellite data
        mock_get_satellite.return_value = {
            'soil_moisture': {'value': 65.0, 'unit': '%'},
            'precipitation': {'recent_mm': 25.0, 'forecast_mm': 15.0},
            'ndvi': {'value': 0.75, 'interpretation': 'healthy vegetation'},
            'temperature': {'current': 28.0, 'min': 22.0, 'max': 32.0, 'unit': 'C'}
        }
        
        # Mock crop model
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            'crop': 'rice',
            'confidence': 0.95,
        }
        mock_get_crop_model.return_value = mock_model
        
        # Run the agent
        response = asyncio.run(self.crop_agent.process_query(self.test_query))
        
        # Verify satellite data was used
        mock_get_satellite.assert_called_once_with(
            self.test_query.location.latitude, 
            self.test_query.location.longitude
        )
        
        # Check if satellite data is in response
        self.assertIn('satellite_data', response.data)


if __name__ == '__main__':
    unittest.main()
