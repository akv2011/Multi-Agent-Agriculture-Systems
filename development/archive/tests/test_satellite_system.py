"""
🧪 Satellite Data Acquisition System Tests
==========================================

Comprehensive tests for the satellite data pipeline including:
- Data simulation accuracy
- API endpoints
- Database operations
- Integration scenarios

Author: Multi-Agent Agriculture System
Created: 2025-01-XX
"""

import asyncio
import pytest
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.satellite_service import (
    SatelliteDataSimulator,
    SatelliteDataStorage,
    SatelliteDataPipeline,
    LocationData,
    create_satellite_pipeline
)

class TestSatelliteDataSimulator:
    """Test the satellite data simulation functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.simulator = SatelliteDataSimulator()
        self.test_location = LocationData(
            latitude=28.7041,
            longitude=77.1025,
            location_name="Delhi",
            region="NCR",
            elevation=216
        )
    
    def test_seasonal_patterns_initialization(self):
        """Test that seasonal patterns are properly initialized"""
        assert "north_india" in self.simulator.seasonal_patterns
        assert "south_india" in self.simulator.seasonal_patterns
        assert "west_india" in self.simulator.seasonal_patterns
        
        # Check structure
        north_pattern = self.simulator.seasonal_patterns["north_india"]
        assert "rabi_season" in north_pattern
        assert "kharif_season" in north_pattern
        assert "peak_months" in north_pattern["rabi_season"]
    
    def test_crop_calendars_initialization(self):
        """Test crop calendar initialization"""
        assert "wheat" in self.simulator.crop_calendars
        assert "rice" in self.simulator.crop_calendars
        assert "cotton" in self.simulator.crop_calendars
        
        wheat_calendar = self.simulator.crop_calendars["wheat"]
        assert "planting_months" in wheat_calendar
        assert "growing_months" in wheat_calendar
        assert "harvest_months" in wheat_calendar
        assert "peak_ndvi" in wheat_calendar
    
    def test_region_determination(self):
        """Test region determination based on coordinates"""
        # North India
        assert self.simulator._determine_region(30.0, 77.0) == "north_india"
        
        # South India
        assert self.simulator._determine_region(12.0, 77.0) == "south_india"
        
        # West India
        assert self.simulator._determine_region(20.0, 72.0) == "west_india"
    
    def test_ndvi_calculation(self):
        """Test NDVI calculation with seasonal patterns"""
        # Test winter wheat season (peak in Feb)
        winter_date = datetime(2025, 2, 15)
        ndvi = self.simulator._calculate_seasonal_ndvi(self.test_location, winter_date, "wheat")
        
        assert -1.0 <= ndvi <= 1.0
        assert ndvi > 0.3  # Should be reasonably high for growing season
        
        # Test monsoon season
        monsoon_date = datetime(2025, 8, 15)
        ndvi_monsoon = self.simulator._calculate_seasonal_ndvi(self.test_location, monsoon_date, "rice")
        
        assert -1.0 <= ndvi_monsoon <= 1.0
    
    def test_soil_moisture_calculation(self):
        """Test soil moisture calculation"""
        # High precipitation scenario
        high_precip_date = datetime(2025, 8, 15)
        moisture = self.simulator._calculate_soil_moisture(self.test_location, high_precip_date, 25.0)
        
        assert 0 <= moisture <= 100
        assert moisture > 30  # Should be higher during monsoon
        
        # Low precipitation scenario
        low_precip_date = datetime(2025, 12, 15)
        moisture_low = self.simulator._calculate_soil_moisture(self.test_location, low_precip_date, 2.0)
        
        assert 0 <= moisture_low <= 100
        assert moisture_low < moisture  # Should be lower in dry season
    
    def test_weather_data_generation(self):
        """Test weather data generation"""
        # Summer season
        summer_date = datetime(2025, 5, 15)
        temp, precip, cloud = self.simulator._generate_weather_data(self.test_location, summer_date)
        
        assert temp > 25  # Should be hot in summer
        assert precip < 10  # Should be relatively dry
        assert 0 <= cloud <= 100
        
        # Monsoon season
        monsoon_date = datetime(2025, 8, 15)
        temp_m, precip_m, cloud_m = self.simulator._generate_weather_data(self.test_location, monsoon_date)
        
        assert precip_m > precip  # More precipitation during monsoon
        assert cloud_m > cloud   # More cloud cover during monsoon
    
    def test_vegetation_health_assessment(self):
        """Test vegetation health assessment logic"""
        # Excellent conditions
        health, confidence = self.simulator._assess_vegetation_health(0.8, 50)
        assert health == "Excellent"
        assert confidence > 0.9
        
        # Poor conditions
        health_poor, confidence_poor = self.simulator._assess_vegetation_health(0.2, 10)
        assert health_poor in ["Poor", "Critical"]
        assert confidence_poor < 0.8
    
    def test_complete_simulation(self):
        """Test complete satellite data simulation"""
        test_date = datetime(2025, 3, 15)
        data_point = self.simulator.simulate_satellite_data(
            self.test_location, 
            test_date, 
            "wheat"
        )
        
        # Validate structure
        assert data_point.timestamp == test_date
        assert data_point.location.latitude == self.test_location.latitude
        assert data_point.location.longitude == self.test_location.longitude
        
        # Validate metrics
        metrics = data_point.metrics
        assert -1.0 <= metrics.ndvi <= 1.0
        assert 0 <= metrics.soil_moisture <= 100
        assert 0 <= metrics.cloud_cover <= 100
        assert 0.5 <= metrics.confidence_score <= 1.0
        assert metrics.vegetation_health in ["Excellent", "Good", "Fair", "Poor", "Critical"]

class TestSatelliteDataStorage:
    """Test satellite data storage functionality"""
    
    def setup_method(self):
        """Setup test environment with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_satellite.db")
        self.storage = SatelliteDataStorage(self.db_path)
        
        self.simulator = SatelliteDataSimulator()
        self.test_location = LocationData(
            latitude=28.7041,
            longitude=77.1025,
            location_name="Delhi Test",
            region="NCR",
            elevation=216
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_database_initialization(self):
        """Test database initialization"""
        assert os.path.exists(self.db_path)
        
        # Check table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='satellite_data'")
        result = cursor.fetchone()
        assert result is not None
        conn.close()
    
    def test_data_storage(self):
        """Test storing satellite data points"""
        # Generate test data
        test_date = datetime(2025, 3, 15)
        data_point = self.simulator.simulate_satellite_data(
            self.test_location,
            test_date,
            "wheat"
        )
        
        # Store data
        result = self.storage.store_data_point(data_point)
        assert result is True
        
        # Verify storage
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM satellite_data")
        count = cursor.fetchone()[0]
        assert count == 1
        conn.close()
    
    def test_data_retrieval(self):
        """Test retrieving satellite data"""
        # Store multiple data points using recent dates
        current_time = datetime.now()
        dates = [
            current_time - timedelta(days=1),
            current_time - timedelta(days=3),
            current_time - timedelta(days=5)
        ]
        
        stored_count = 0
        for date in dates:
            data_point = self.simulator.simulate_satellite_data(
                self.test_location,
                date,
                "wheat"
            )
            if self.storage.store_data_point(data_point):
                stored_count += 1
        
        assert stored_count == 3, f"Only {stored_count} of 3 data points were stored"
        
        # Retrieve data
        retrieved_data = self.storage.get_latest_data(
            self.test_location.latitude,
            self.test_location.longitude,
            days_back=10
        )
        
        assert len(retrieved_data) >= 3, f"Expected at least 3 data points, got {len(retrieved_data)}"
        
        # Should be sorted by timestamp descending
        if len(retrieved_data) >= 2:
            assert retrieved_data[0].timestamp >= retrieved_data[1].timestamp
    
    def test_historical_trends(self):
        """Test historical trends calculation"""
        # Generate historical data
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            data_point = self.simulator.simulate_satellite_data(
                self.test_location,
                date,
                "mixed"
            )
            success = self.storage.store_data_point(data_point)
            assert success, f"Failed to store data point for day {i}"
        
        # Get trends
        trends = self.storage.get_historical_trends(
            self.test_location.latitude,
            self.test_location.longitude,
            months_back=1
        )
        
        assert "trends" in trends
        assert "summary" in trends
        if trends["trends"]:  # Only check if we have trends data
            assert len(trends["trends"]) > 0
            assert "avg_ndvi" in trends["summary"]
            assert "trend_direction" in trends["summary"]

class TestSatelliteDataPipeline:
    """Test the complete satellite data pipeline"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create pipeline with temporary storage
        self.pipeline = SatelliteDataPipeline()
        self.pipeline.storage = SatelliteDataStorage(
            os.path.join(self.temp_dir, "test_pipeline.db")
        )
        
        self.test_location = LocationData(
            latitude=28.7041,
            longitude=77.1025,
            location_name="Pipeline Test",
            region="NCR",
            elevation=216
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_acquire_data_for_location(self):
        """Test acquiring data for a specific location"""
        test_date = datetime(2025, 3, 15)
        
        data_point = await self.pipeline.acquire_data_for_location(
            self.test_location,
            test_date,
            "wheat"
        )
        
        assert data_point.timestamp == test_date
        assert data_point.location.location_name == "Pipeline Test"
        assert data_point.metrics.ndvi is not None
    
    @pytest.mark.asyncio
    async def test_bulk_acquire_data(self):
        """Test bulk data acquisition"""
        # Use smaller dataset for testing
        original_locations = self.pipeline.monitoring_locations
        self.pipeline.monitoring_locations = [self.test_location]
        
        try:
            results = await self.pipeline.bulk_acquire_data(days_back=3)
            
            assert "successful" in results
            assert "failed" in results
            assert "total_data_points" in results
            assert results["successful"] > 0
            assert results["total_data_points"] == 3  # 1 location × 3 days
            
        finally:
            self.pipeline.monitoring_locations = original_locations
    
    def test_get_location_data(self):
        """Test comprehensive location data retrieval"""
        # First, add some test data using recent dates
        current_time = datetime.now()
        for i in range(5):
            date = current_time - timedelta(days=i)
            data_point = self.pipeline.simulator.simulate_satellite_data(
                self.test_location,
                date,
                "mixed"
            )
            self.pipeline.storage.store_data_point(data_point)
        
        # Get location data
        location_data = self.pipeline.get_location_data(
            self.test_location.latitude,
            self.test_location.longitude,
            days_back=7
        )
        
        assert "location" in location_data
        assert "latest_data" in location_data
        assert "trends" in location_data
        assert "summary" in location_data
        # Should have at least the 5 data points we added
        assert len(location_data["latest_data"]) >= 5

class TestSatelliteAPIIntegration:
    """Integration tests for satellite API"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_pipeline_creation(self):
        """Test pipeline creation function"""
        pipeline = create_satellite_pipeline()
        
        assert pipeline is not None
        assert hasattr(pipeline, 'simulator')
        assert hasattr(pipeline, 'storage')
        assert len(pipeline.monitoring_locations) == 10  # Default monitoring locations

def run_satellite_tests():
    """Run all satellite system tests"""
    print("🧪 RUNNING SATELLITE DATA SYSTEM TESTS")
    print("=" * 50)
    
    # Test simulator
    print("\n📡 Testing Satellite Data Simulator...")
    simulator_tests = TestSatelliteDataSimulator()
    simulator_tests.setup_method()
    
    try:
        simulator_tests.test_seasonal_patterns_initialization()
        simulator_tests.test_crop_calendars_initialization()
        simulator_tests.test_region_determination()
        simulator_tests.test_ndvi_calculation()
        simulator_tests.test_soil_moisture_calculation()
        simulator_tests.test_weather_data_generation()
        simulator_tests.test_vegetation_health_assessment()
        simulator_tests.test_complete_simulation()
        print("✅ Simulator tests passed!")
        
    except Exception as e:
        print(f"❌ Simulator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test storage
    print("\n💾 Testing Satellite Data Storage...")
    storage_tests = TestSatelliteDataStorage()
    storage_tests.setup_method()
    
    try:
        storage_tests.test_database_initialization()
        storage_tests.test_data_storage()
        storage_tests.test_data_retrieval()
        storage_tests.test_historical_trends()
        print("✅ Storage tests passed!")
        
    except Exception as e:
        print(f"❌ Storage tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        storage_tests.teardown_method()
    
    # Test pipeline
    print("\n🚀 Testing Satellite Data Pipeline...")
    pipeline_tests = TestSatelliteDataPipeline()
    pipeline_tests.setup_method()
    
    try:
        # Run async tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(pipeline_tests.test_acquire_data_for_location())
        loop.run_until_complete(pipeline_tests.test_bulk_acquire_data())
        pipeline_tests.test_get_location_data()
        
        loop.close()
        print("✅ Pipeline tests passed!")
        
    except Exception as e:
        print(f"❌ Pipeline tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pipeline_tests.teardown_method()
    
    # Test integration
    print("\n🔗 Testing Integration...")
    integration_tests = TestSatelliteAPIIntegration()
    integration_tests.setup_method()
    
    try:
        integration_tests.test_pipeline_creation()
        print("✅ Integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        integration_tests.teardown_method()
    
    print("\n🎉 ALL SATELLITE SYSTEM TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = run_satellite_tests()
    exit(0 if success else 1)
