"""
Stub Crop Recommendation Model for Testing
"""

class StubCropRecommendationModel:
    """A stub model that returns predefined recommendations"""
    
    def __init__(self):
        self.recommendations = {
            "sandy": ["groundnut", "cotton", "potato"],
            "loamy": ["wheat", "rice", "maize"],
            "clay": ["rice", "sugarcane", "cotton"],
            "default": ["wheat", "rice", "pulses"]
        }
    
    def predict(self, soil_type=None, nitrogen=None, phosphorus=None, 
                potassium=None, temperature=None, humidity=None, 
                ph=None, rainfall=None, **kwargs):
        """Return a stubbed prediction based on soil type"""
        if soil_type and soil_type.lower() in self.recommendations:
            return self.recommendations[soil_type.lower()]
        return self.recommendations["default"]

def get_model():
    """Return the stub model instance"""
    return StubCropRecommendationModel()
