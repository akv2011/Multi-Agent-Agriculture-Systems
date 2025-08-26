"""
Test Disease Identification Integration with text-based and image-based identification
"""

import unittest
import os
import base64
import asyncio
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.disease_identification_agent import DiseaseIdentificationAgent
from src.models.AgriMitr_disease_identification import DiseaseIdentificationResult
from src.core.agriculture_models import AgricultureQuery, Location


class TestDiseaseIdentificationIntegration(unittest.TestCase):
    """Test integration of disease identification agent with AgriMitr model"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = DiseaseIdentificationAgent()
        
        # Sample test image paths
        self.test_images = {
            "apple_scab": "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/apple_scab.jpg",
            "tomato_late_blight": "AgriMitr/PLANT-DISEASE-IDENTIFICATION/sample_images/tomato_late_blight.jpg"
        }
        
        # Sample image data
        self.image_data = self._load_test_image("apple_scab")
        
    def _load_test_image(self, image_key):
        """Load a test image as base64"""
        if image_key not in self.test_images:
            return None
            
        try:
            with open(self.test_images[image_key], "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Warning: Test image {self.test_images[image_key]} not found")
            return None
    
    @patch('src.models.AgriMitr_disease_identification.load_disease_model')
    @patch('src.agents.disease_identification_agent.DiseaseIdentificationAgent._identify_disease')
    def test_image_based_identification(self, mock_identify, mock_load_model):
        """Test disease identification with image data"""
        # Setup mock
        mock_result = DiseaseIdentificationResult(
            disease_class="Apple___Apple_scab",
            crop_type="Apple",
            disease_name="Apple Scab",
            confidence=95.5,
            is_healthy=False,
            symptoms=["Dark olive-green spots on leaves", "Velvety texture on lesions"],
            treatment_recommendations=["Fungicide application", "Proper sanitation"],
            severity_assessment="Moderate",
            prevention_methods=["Plant resistant varieties", "Improve air circulation"]
        )
        mock_identify.return_value = mock_result
        
        # Create test query
        query = AgricultureQuery(
            query_text="What disease is affecting my apple tree?",
            image_data=self.image_data,
            crop_type="Apple",
            location=Location(latitude=30.7333, longitude=76.7794, state="Punjab", district="Chandigarh")
        )
        
        # Run test
        response = asyncio.run(self.agent.process_query(query))
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.data["disease"], "Apple Scab")
        self.assertEqual(response.data["identification_method"], "image_analysis")
        self.assertGreater(response.data["confidence"], 90)
    
    @patch('src.models.AgriMitr_disease_identification.identify_disease_from_symptoms')
    def test_text_based_identification(self, mock_identify_from_symptoms):
        """Test disease identification with text description"""
        # Setup mock
        mock_result = DiseaseIdentificationResult(
            disease_class="Tomato___Late_blight",
            crop_type="Tomato",
            disease_name="Tomato Late Blight",
            confidence=80.5,
            is_healthy=False,
            symptoms=["Dark brown spots on leaves", "White fungal growth underneath"],
            treatment_recommendations=["Copper fungicide", "Remove affected leaves"],
            severity_assessment="Moderate",
            prevention_methods=["Improve air circulation", "Water at the base"]
        )
        mock_identify_from_symptoms.return_value = mock_result
        
        # Create test query
        query = AgricultureQuery(
            query_text="My tomato plants have dark brown spots with white fungus underneath the leaves. What disease is this?",
            crop_type="Tomato",
        )
        
        # Run test
        response = asyncio.run(self.agent.process_query(query))
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.data["disease"], "Tomato Late Blight")
        self.assertEqual(response.data["identification_method"], "symptom_analysis")
        self.assertGreater(response.data["confidence"], 75)
        self.assertIn("recommendations", response.data)
    
    @patch('src.agents.agriculture_router.AgricultureRouter.classify_domains')
    def test_disease_query_routing(self, mock_classify_domains):
        """Test that disease queries are properly routed"""
        from src.agents.agriculture_router import AgricultureRouter
        from src.core.agriculture_models import QueryDomain
        
        # Setup mock
        mock_classify_domains.return_value = ([QueryDomain.DISEASE_IDENTIFICATION], 0.9)
        
        # Create router
        router = AgricultureRouter()
        
        # Create test queries
        text_query = "My rice plants have brown spots on the leaves. What disease is this?"
        image_query = "Can you identify this disease on my wheat crop?"
        
        # Test routing for text query
        domains, _ = router.classify_domains(text_query)
        self.assertIn(QueryDomain.DISEASE_IDENTIFICATION, domains)
        
        # Test routing for image query with image flag
        domains, _ = router.classify_domains(image_query, has_image=True)
        self.assertIn(QueryDomain.DISEASE_IDENTIFICATION, domains)
        
        # Test agent selection
        agents = router.select_agents([QueryDomain.DISEASE_IDENTIFICATION])
        self.assertIn("disease_specialist", agents)


if __name__ == '__main__':
    unittest.main()
