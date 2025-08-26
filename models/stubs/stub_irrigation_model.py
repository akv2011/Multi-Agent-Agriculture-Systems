"""
Stub Irrigation Scheduling Model for Testing
"""

class StubIrrigationModel:
    """A stub model that returns predefined irrigation schedules"""
    
    def __init__(self):
        self.irrigation_plans = {
            "wheat": {
                "days": [3, 7, 10, 14],
                "amounts": [8, 10, 8, 10],
                "method": "sprinkler"
            },
            "rice": {
                "days": [2, 5, 8, 11, 14],
                "amounts": [15, 15, 12, 15, 15],
                "method": "flood"
            },
            "cotton": {
                "days": [4, 9, 14],
                "amounts": [12, 15, 12],
                "method": "drip"
            },
            "default": {
                "days": [5, 10, 15],
                "amounts": [10, 10, 10],
                "method": "sprinkler"
            }
        }
    
    def generate_irrigation_plan(self, crop_type=None, soil_type=None, field_size=None, **kwargs):
        """Return a stubbed irrigation plan based on crop type"""
        crop = crop_type.lower() if crop_type else "default"
        if crop not in self.irrigation_plans:
            crop = "default"
            
        plan = self.irrigation_plans[crop].copy()
        plan["crop"] = crop
        plan["soil_type"] = soil_type or "loam"
        plan["field_size"] = field_size or 1.0
        plan["total_water"] = sum(plan["amounts"])
        
        return plan
    
    def generate_satellite_enhanced_irrigation_plan(self, *args, **kwargs):
        """Same as generate_irrigation_plan but with added satellite context"""
        plan = self.generate_irrigation_plan(*args, **kwargs)
        plan["satellite_enhanced"] = True
        plan["confidence"] = 0.85
        return plan

def get_model():
    """Return the stub model instance"""
    return StubIrrigationModel()
