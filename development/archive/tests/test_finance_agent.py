"""
Test script for Finance and Policy Agent
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

# Mock the base classes for testing
class Language(Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    MIXED = "mixed"

class CropType(Enum):
    WHEAT = "wheat"
    RICE = "rice"

class SoilType(Enum):
    ALLUVIAL = "alluvial"

@dataclass
class Location:
    state: str
    district: str

@dataclass
class FarmProfile:
    farm_id: str
    farmer_name: str
    location: Location
    total_area: float
    soil_type: SoilType
    current_crops: List[CropType]
    irrigation_type: str
    farm_type: str

@dataclass
class AgricultureQuery:
    query_text: str
    query_language: Language
    user_id: str
    location: Optional[Location] = None
    farm_profile: Optional[FarmProfile] = None

@dataclass
class AgentResponse:
    agent_id: str
    agent_name: str
    query_id: str
    response_text: str
    response_language: Language
    confidence_score: float
    reasoning: str = ""
    recommendations: List[Dict[str, Any]] = None
    sources: List[str] = None
    next_steps: List[str] = None
    timestamp: datetime = None
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = None
    warnings: List[str] = None

# Mock base agent
class BaseAgent:
    def __init__(self):
        self.agent_id = "base"
        self.capabilities = []

# Now test the finance agent components
print("🏦 Testing Finance and Policy Agent Components")

# Import and test the actual classes
import importlib.util
spec = importlib.util.spec_from_file_location("finance_policy_agent", "src/agents/finance_policy_agent.py")
finance_module = importlib.util.module_from_spec(spec)

# Mock the missing imports within the module
import types
base_agent_mock = types.ModuleType('base_agent')
base_agent_mock.BaseAgent = BaseAgent

agriculture_models_mock = types.ModuleType('agriculture_models')
agriculture_models_mock.AgricultureQuery = AgricultureQuery
agriculture_models_mock.AgentResponse = AgentResponse
agriculture_models_mock.CropType = CropType
agriculture_models_mock.SoilType = SoilType
agriculture_models_mock.Location = Location
agriculture_models_mock.FarmProfile = FarmProfile
agriculture_models_mock.Language = Language

sys.modules['src.agents.base_agent'] = base_agent_mock
sys.modules['src.core.agriculture_models'] = agriculture_models_mock

# Now execute the module
spec.loader.exec_module(finance_module)

# Create agent instance
agent = finance_module.FinancePolicyAgent()
print(f"✅ Agent created with {len(agent.loan_schemes)} loan schemes")
print(f"✅ Agent has {len(agent.subsidy_schemes)} subsidy schemes")

# Test loan scheme analysis
print("\n📋 Available Loan Schemes:")
for scheme_id, scheme in list(agent.loan_schemes.items())[:3]:
    print(f"- {scheme.scheme_name}: Max ₹{scheme.max_amount:,} at {scheme.interest_rate}%")

print("\n💰 Available Subsidy Schemes:")
for scheme_id, scheme in list(agent.subsidy_schemes.items())[:3]:
    print(f"- {scheme.scheme_name}: Up to {scheme.subsidy_percentage}% subsidy")

# Test query analysis
test_queries = [
    "मुझे ट्रैक्टर के लिए लोन चाहिए",
    "What subsidies are available for drip irrigation?",
    "MSP rate for wheat",
    "Documents needed for loan application"
]

print("\n🔍 Testing Query Analysis:")
for query in test_queries:
    analysis = agent._analyze_finance_query(query)
    print(f"Query: '{query}' → Type: {analysis['type']}")

print("\n🎉 Finance and Policy Agent components working successfully!")
print(f"📊 Agent ready with {len(agent.capabilities)} capabilities")
