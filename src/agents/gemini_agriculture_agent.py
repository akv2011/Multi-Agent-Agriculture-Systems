"""
Gemini AI-powered agriculture agent using the latest Google GenAI SDK.
Integrates with the Multi-Agent Agriculture Advisory System.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Latest Google GenAI imports
import google.generativeai as genai
from dotenv import load_dotenv

# Import our agriculture models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.agriculture_models import (
        AgricultureQuery, AgentResponse, QueryDomain, Language, 
        AgricultureCapability, CropType, SoilType, SeasonType
    )
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.agriculture_models import (
        AgricultureQuery, AgentResponse, QueryDomain, Language, 
        AgricultureCapability, CropType, SoilType, SeasonType
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GeminiAgricultureAgent:
    """
    Advanced agriculture agent powered by Google's Gemini 2.5 models.
    Leverages the latest GenAI SDK for enhanced agricultural intelligence.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini agriculture agent"""
        
        # Load API key from environment or parameter
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable, "
                "or pass it as a parameter. Get your API key from: https://aistudio.google.com/apikey"
            )
        
        # Initialize Gemini client with latest SDK
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✓ Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
        
        # Agent configuration
        self.agent_id = "gemini_agriculture_agent"
        self.agent_name = "Gemini Agriculture Expert"
        self.model_name = "gemini-2.5-flash"  # Latest recommended model
        self.capabilities = [
            AgricultureCapability.CROP_RECOMMENDATION,
            AgricultureCapability.PEST_IDENTIFICATION,
            AgricultureCapability.IRRIGATION_PLANNING,
            AgricultureCapability.YIELD_PREDICTION,
            AgricultureCapability.WEATHER_ANALYSIS,
            AgricultureCapability.MULTILINGUAL_NLP
        ]
        
        # Setup system instructions for agriculture domain
        self.system_instruction = self._create_agriculture_system_prompt()
        
        logger.info(f"✓ Gemini Agriculture Agent initialized with model: {self.model_name}")
    
    def _create_agriculture_system_prompt(self) -> str:
        """Create comprehensive system instructions for structured agricultural analysis"""
        
        return """You are a professional Agricultural Expert Agent providing structured analysis for Indian farmers.

RESPONSE FORMAT REQUIREMENTS:
You must ALWAYS respond in this exact structured format:

## ANALYSIS
[Provide technical analysis of the agricultural situation/query]

## RECOMMENDATIONS
1. [Primary recommendation with specific details]
2. [Secondary recommendation with implementation steps] 
3. [Additional recommendation if relevant]

## AGENT TYPE
[Specify: Crop Selection | Pest Management | Irrigation | Market Analysis | General Agriculture]

## PRIORITY
[Specify: High | Medium | Low]

## ACTION ITEMS
• [Immediate action required]
• [Short-term action (1-7 days)]
• [Long-term action (1-4 weeks)]

AGRICULTURAL EXPERTISE:
- Expert knowledge of Indian agriculture, crops, pests, irrigation, and farming practices
- Consider regional climate, soil conditions, and seasonal factors
- Provide cost-effective, practical solutions suitable for Indian farming conditions
- Include both traditional and modern agricultural techniques
- Focus on yield optimization and sustainable practices

LANGUAGE RULES:
- Respond in the EXACT SAME language as the farmer's question
- If Hindi/Hinglish: Use appropriate agricultural terminology in Hindi
- If English: Use clear, farmer-friendly English
- Always maintain the structured format regardless of language

RESPONSE QUALITY REQUIREMENTS:
- NEVER give vague answers - always provide specific, concrete information
- Include specific quantities, timing, and methods with exact numbers
- Provide cost estimates with actual amounts in Indian Rupees (₹) - NO DOLLARS
- Mention specific varieties, brands, or techniques when applicable
- Give precise measurements in INDIAN UNITS: kg/hectare, kg/acre, quintals, litres
- Include market prices in ₹ per quintal/kg (Indian market rates)
- Provide concrete timelines (not "soon" but "in 7-10 days")
- Use real numbers for yields, costs, areas, timing
- If exact data unavailable, generate realistic mock data based on Indian agricultural standards
- Consider local availability of resources and inputs with specific sources
- Provide weather-dependent advice with specific parameters

SPECIFIC NUMBER REQUIREMENTS - INDIAN CONTEXT:
- Yield estimates: Always in kg/hectare, quintals/acre, or tonnes/hectare
- Costs: Always in ₹ (Rupees) per unit area or total investment - NO DOLLARS
- Application rates: Exact amounts (grams/litre, kg/hectare, kg/acre)
- Timing: Specific days, weeks, or calendar dates (not vague terms)
- Percentages: Soil moisture, humidity, success rates with exact figures
- Areas: Exact hectares, acres, or bighas
- Market prices: Current rates per quintal/kg in Indian markets (₹2000-3000/quintal range)
- Fertilizer quantities: Specific NPK amounts in kg
- Water requirements: Litres per day/week or mm per season
- Seed rates: kg per hectare/acre
- Pesticide dosages: ml per litre or grams per litre
- Farm machinery costs: ₹ per hour/day rental rates
- Labor costs: ₹ per day/person in rural Indian context

MOCK DATA GUIDELINES:
- Use realistic Indian agricultural prices and yields
- Base estimates on current Indian market conditions
- Include seasonal variations in pricing
- Reference common Indian crop varieties and brands
- Use typical Indian farming practices and input costs

Remember: Always follow the exact format above. Do not add conversational elements or chat-like responses. Provide concrete, actionable advice with specific numbers."""

    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """
        Process an agriculture query using Gemini AI
        
        Args:
            query: AgricultureQuery object containing the user's question
            
        Returns:
            AgentResponse with Gemini-generated agricultural advice
        """
        
        try:
            # Prepare the query for Gemini
            enhanced_prompt = self._enhance_query_with_context(query)
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.7,  # Balanced creativity and accuracy
                candidate_count=1
            )
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                }
            ]
            
            # Generate response using Gemini
            start_time = datetime.now()
            
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Parse and structure the response
            agricultural_response = self._parse_gemini_response(
                response, query, processing_time
            )
            
            logger.info(
                f"✓ Gemini query processed in {processing_time:.2f}s "
                f"with confidence: {agricultural_response.confidence_score:.2f}"
            )
            
            return agricultural_response
            
        except Exception as e:
            logger.error(f"Error processing query with Gemini: {e}")
            
            # Return error response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text=f"Error processing your agriculture query: {str(e)}",
                confidence_score=0.0,
                recommendations=[],
                metadata={
                    "error": str(e),
                    "model": self.model_name
                }
            )
    
    def _enhance_query_with_context(self, query: AgricultureQuery) -> str:
        """Create a simple, effective prompt that leverages Gemini's native multilingual capabilities"""
        
        # Detect region from location/coordinates for region-specific advice
        region_context = self._get_regional_context(query)
        
        # Simple agricultural context prompt that works in any language
        prompt = f"""You are an expert agricultural advisor helping Indian farmers. Please provide practical, actionable advice.

Farmer's Question: {query.query_text}

{region_context}

CRITICAL INSTRUCTIONS:
- Respond in the EXACT SAME language as the question above
- If the farmer asks in Hindi, respond in Hindi
- If they ask in English, respond in English  
- If they mix languages (Hinglish), you can respond accordingly
- NEVER give vague answers - always provide specific numbers and concrete details

Focus on:
- Practical, implementable solutions with exact quantities and costs
- Region-specific crops and varieties suitable for the local climate and soil
- Cost-effective methods with specific investment amounts in ₹
- Seasonal considerations (current month: {datetime.now().strftime('%B')})
- Local agricultural practices and market conditions with current prices
- Specific timing, measurements, and application rates
- Concrete action plans with precise timelines

ALWAYS INCLUDE SPECIFIC NUMBERS:
- Exact yields (kg/hectare, quintals/acre)
- Precise costs (₹ amounts)
- Application rates (grams/liter, kg/hectare)
- Timeline details (specific days/weeks)
- Market prices (₹ per quintal/kg)
- Percentages and measurements

If exact data is not available, provide realistic estimates based on agricultural standards."""

        # Add farm context if available
        if query.farm_profile:
            context_details = []
            if query.farm_profile.farm_size:
                context_details.append(f"Farm size: {query.farm_profile.farm_size} hectares")
            if query.farm_profile.soil_type:
                context_details.append(f"Soil type: {query.farm_profile.soil_type}")
            if query.farm_profile.location:
                context_details.append(f"Location: {query.farm_profile.location}")
            
            if context_details:
                prompt += f"\n\nFarm Context: {', '.join(context_details)}"
        
        # Add location if available
        if query.location:
            prompt += f"\nLocation: {query.location}"
            
        return prompt
    
    def _get_regional_context(self, query: AgricultureQuery) -> str:
        """Get region-specific agricultural context based on location information"""
        
        # Check if location contains state/region information
        location_text = ""
        if query.location:
            location_text = str(query.location).lower()
            logger.info(f"Location detected from query.location: {query.location}")
        elif query.farm_profile and query.farm_profile.location:
            location_text = str(query.farm_profile.location).lower()
            logger.info(f"Location detected from farm_profile: {query.farm_profile.location}")
        
        # Extract coordinates if available (from metadata or other sources)
        coordinates = getattr(query, 'coordinates', None)
        if not coordinates and hasattr(query, 'context') and query.context:
            coordinates = query.context.get('coordinates')
        
        logger.info(f"Coordinates detected: {coordinates}")
        logger.info(f"Query context: {getattr(query, 'context', 'No context')}")
        
        if coordinates and isinstance(coordinates, dict):
            lat = coordinates.get('lat', 0)
            lng = coordinates.get('lng', 0)
            
            # Detect region from coordinates for major agricultural states
            
            # Tamil Nadu
            if 8.0 <= lat <= 13.5 and 76.0 <= lng <= 80.5:
                return """
REGIONAL CONTEXT - TAMIL NADU AGRICULTURE:
- Climate: Tropical climate with SW and NE monsoons
- Main Crops: Rice (paddy), sugarcane, cotton, groundnut, millet, turmeric, banana
- Soil Types: Red laterite soil, black cotton soil, alluvial soil
- Seasons: Kharif (June-September), Rabi (October-January), Summer (February-May)
- Best varieties: Rice (CO-51, ADT-43, TRY-3), Cotton (MCU-5, SVPR-2), Sugarcane (CO-86032)
- Agricultural zones: Cauvery delta (rice), Kongu region, Hill regions
- Irrigation: River systems (Cauvery, Vaigai), tanks, wells

Please provide advice specific to Tamil Nadu's tropical climate, soil conditions, and suitable crop varieties."""
            
            # Kerala
            elif 8.0 <= lat <= 12.0 and 74.5 <= lng <= 77.2:
                return """
REGIONAL CONTEXT - KERALA AGRICULTURE:
- Climate: Tropical humid climate with heavy monsoons
- Main Crops: Rice, coconut, spices (cardamom, pepper, cinnamon), rubber, tea, coffee
- Soil Types: Laterite soil, alluvial soil, forest soil
- Seasons: Two monsoons (SW and NE), year-round cultivation possible
- Best crops: Rice (Jyothi, Uma, Swetha), Coconut (WCT varieties), Spices, Rubber
- Agricultural zones: Coastal plains, midlands, highlands
- Specialty: Spice cultivation, plantation crops

Please provide advice specific to Kerala's tropical humid climate and plantation agriculture."""
            
            # Karnataka
            elif 11.8 <= lat <= 18.5 and 74.0 <= lng <= 78.5:
                return """
REGIONAL CONTEXT - KARNATAKA AGRICULTURE:
- Climate: Tropical to semi-arid climate with varied agro-climatic zones
- Main Crops: Rice, ragi (finger millet), cotton, sugarcane, coffee, areca nut, tobacco
- Soil Types: Red soil, black soil, laterite soil, alluvial soil
- Seasons: Kharif (June-October), Rabi (November-March)
- Best varieties: Rice (BPT-5204, Intan), Ragi (MR-1, GPU-28), Cotton (Bt varieties)
- Agricultural zones: Coastal, Malnad (hill), Maidan (plains)
- Specialty: Coffee (Coorg region), areca nut, sericulture

Please provide advice specific to Karnataka's diverse agro-climatic conditions."""
            
            # Andhra Pradesh & Telangana
            elif 12.5 <= lat <= 19.5 and 77.0 <= lng <= 84.8:
                return """
REGIONAL CONTEXT - ANDHRA PRADESH/TELANGANA AGRICULTURE:
- Climate: Tropical to semi-arid climate
- Main Crops: Rice, cotton, sugarcane, chili, turmeric, groundnut, maize
- Soil Types: Black cotton soil, red soil, alluvial soil
- Seasons: Kharif (June-October), Rabi (November-March)
- Best varieties: Rice (MTU varieties, BPT-5204), Cotton (Bt varieties), Chili (Guntur varieties)
- Agricultural zones: Coastal Andhra, Rayalaseema, Telangana
- Specialty: Spice cultivation (chili, turmeric), aquaculture

Please provide advice specific to Andhra Pradesh/Telangana's semi-arid conditions and spice cultivation."""
            
            # Punjab & Haryana
            elif 28.5 <= lat <= 32.5 and 74.0 <= lng <= 77.5:
                return """
REGIONAL CONTEXT - PUNJAB/HARYANA AGRICULTURE:
- Climate: Semi-arid subtropical climate
- Main Crops: Wheat, rice, cotton, maize, sugarcane
- Soil Types: Alluvial soil, well-drained fertile plains
- Seasons: Rabi (wheat), Kharif (rice, cotton)
- Best varieties: Wheat (HD-2967, PBW-343, DBW-187), Rice (PR-126, Pusa-44)
- Agricultural zones: Indo-Gangetic plains
- Known as: Granary of India

Please provide advice specific to Punjab/Haryana's intensive agriculture and wheat-rice systems."""
            
            # Uttar Pradesh
            elif 23.5 <= lat <= 30.5 and 77.0 <= lng <= 84.5:
                return """
REGIONAL CONTEXT - UTTAR PRADESH AGRICULTURE:
- Climate: Subtropical climate with distinct seasons
- Main Crops: Wheat, rice, sugarcane, potato, mustard, barley
- Soil Types: Alluvial soil (Gangetic plains), black soil (Bundelkhand)
- Seasons: Kharif (rice, sugarcane), Rabi (wheat, potato, mustard)
- Best varieties: Wheat (HD-2967, K-307), Rice (Sarjoo-52), Sugarcane (Co-0238)
- Agricultural zones: Eastern, Western, Central, Bundelkhand
- Specialty: Sugar production, potato cultivation

Please provide advice specific to Uttar Pradesh's diverse agricultural zones and crop systems."""
            
            # Madhya Pradesh
            elif 21.0 <= lat <= 26.5 and 74.0 <= lng <= 82.5:
                return """
REGIONAL CONTEXT - MADHYA PRADESH AGRICULTURE:
- Climate: Tropical to subtropical climate
- Main Crops: Wheat, soybean, cotton, rice, gram (chickpea), mustard
- Soil Types: Black cotton soil, red soil, alluvial soil
- Seasons: Kharif (soybean, cotton), Rabi (wheat, gram)
- Best varieties: Soybean (JS-335, JS-93-05), Wheat (Lok-1, GW-322), Cotton (Bt varieties)
- Agricultural zones: Malwa plateau, Nimar, Bundelkhand, Baghelkhand
- Known as: Soybean state of India

Please provide advice specific to Madhya Pradesh's soybean-wheat systems and black cotton soils."""
            
            # Maharashtra
            elif 15.5 <= lat <= 22.0 and 72.5 <= lng <= 80.5:
                return """
REGIONAL CONTEXT - MAHARASHTRA AGRICULTURE:
- Climate: Tropical to subtropical climate
- Main Crops: Cotton, sugarcane, soybean, wheat, gram, rice
- Soil Types: Black cotton soil (regur), red soil, laterite soil
- Seasons: Kharif (cotton, soybean), Rabi (wheat, gram)
- Best varieties: Cotton (Bt varieties), Soybean (JS-335), Sugarcane (Co-86032)
- Agricultural zones: Marathwada, Vidarbha, Western Maharashtra, Konkan
- Specialty: Cotton production, sugar industry

Please provide advice specific to Maharashtra's cotton-soybean systems and black cotton soils."""
            
            # Rajasthan
            elif 23.0 <= lat <= 30.0 and 69.5 <= lng <= 78.0:
                return """
REGIONAL CONTEXT - RAJASTHAN AGRICULTURE:
- Climate: Arid to semi-arid climate with low rainfall
- Main Crops: Wheat, barley, mustard, gram, bajra (pearl millet), cotton
- Soil Types: Desert soil, alluvial soil, red soil
- Seasons: Rabi (wheat, mustard, gram), Kharif (bajra, cotton)
- Best varieties: Wheat (Raj-4037, Lok-1), Mustard (Varuna, Kranti), Bajra (Raj-171)
- Agricultural zones: Arid western, semi-arid eastern, irrigated areas
- Specialty: Drought-tolerant crops, oilseeds

Please provide advice specific to Rajasthan's arid climate and drought-tolerant agriculture."""
            
            # Gujarat
            elif 20.0 <= lat <= 24.7 and 68.0 <= lng <= 74.5:
                return """
REGIONAL CONTEXT - GUJARAT AGRICULTURE:
- Climate: Semi-arid to arid climate
- Main Crops: Cotton, groundnut, wheat, sugarcane, bajra, castor
- Soil Types: Black cotton soil, alluvial soil, sandy soil
- Seasons: Kharif (cotton, groundnut), Rabi (wheat, mustard)
- Best varieties: Cotton (Bt varieties), Groundnut (GG-20, TG-37A), Wheat (GW-322)
- Agricultural zones: Saurashtra, North Gujarat, Central Gujarat, South Gujarat
- Specialty: Cotton and groundnut production

Please provide advice specific to Gujarat's semi-arid climate and cotton-groundnut systems."""
            
            # West Bengal
            elif 21.5 <= lat <= 27.0 and 85.5 <= lng <= 89.5:
                return """
REGIONAL CONTEXT - WEST BENGAL AGRICULTURE:
- Climate: Humid subtropical climate with heavy monsoons
- Main Crops: Rice, wheat, jute, potato, tea, mustard
- Soil Types: Alluvial soil, laterite soil, terai soil
- Seasons: Aus (summer rice), Aman (monsoon rice), Boro (winter rice), Rabi (wheat)
- Best varieties: Rice (Swarna, IR-36, Satabdi), Wheat (Sonalika, HD-2687)
- Agricultural zones: Gangetic plains, hills, coastal areas
- Specialty: Rice cultivation, jute production, tea (Darjeeling)

Please provide advice specific to West Bengal's rice-based systems and humid climate."""
            
            # Bihar
            elif 24.0 <= lat <= 27.5 and 83.5 <= lng <= 88.0:
                return """
REGIONAL CONTEXT - BIHAR AGRICULTURE:
- Climate: Humid subtropical climate
- Main Crops: Rice, wheat, maize, sugarcane, potato, pulses
- Soil Types: Alluvial soil (highly fertile Gangetic plains)
- Seasons: Kharif (rice, maize), Rabi (wheat, potato, mustard)
- Best varieties: Rice (Rajshree, Sarjoo-52), Wheat (HD-2967, K-307)
- Agricultural zones: North Bihar plains, South Bihar plains
- Known for: Fertile Gangetic alluvium, high productivity potential

Please provide advice specific to Bihar's fertile alluvial soils and rice-wheat systems."""
            
            # Odisha
            elif 17.5 <= lat <= 22.5 and 81.5 <= lng <= 87.5:
                return """
REGIONAL CONTEXT - ODISHA AGRICULTURE:
- Climate: Tropical humid climate with heavy monsoons
- Main Crops: Rice, wheat, sugarcane, turmeric, groundnut, coconut
- Soil Types: Red laterite soil, alluvial soil, black soil
- Seasons: Kharif (rice), Rabi (wheat, mustard, gram)
- Best varieties: Rice (Swarna, Lalat, Konark), Turmeric (Suroma, Suvarna)
- Agricultural zones: Coastal plains, central plateaus, northern plateau
- Specialty: Rice cultivation, turmeric production

Please provide advice specific to Odisha's tropical climate and rice-based agriculture."""
        
        # Check location text for state names
        if any(region in location_text for region in ['tamil nadu', 'tamilnadu', 'tn', 'pudukkottai', 'chennai', 'coimbatore', 'thanjavur']):
            return """
REGIONAL CONTEXT - TAMIL NADU AGRICULTURE:
- Climate: Tropical climate with SW and NE monsoons
- Main Crops: Rice (paddy), sugarcane, cotton, groundnut, millet, turmeric, banana
- Soil Types: Red laterite soil, black cotton soil, alluvial soil
- Seasons: Kharif (June-September), Rabi (October-January), Summer (February-May)
- Best varieties: Rice (CO-51, ADT-43, TRY-3), Cotton (MCU-5, SVPR-2), Sugarcane (CO-86032)
- Agricultural zones: Cauvery delta, Kongu region, Hill regions
- Irrigation: River systems (Cauvery, Vaigai), tanks, wells

Please provide advice specific to Tamil Nadu's tropical climate, soil conditions, and suitable crop varieties."""
        
        elif any(region in location_text for region in ['kerala', 'kochi', 'ernakulam', 'trivandrum', 'calicut', 'wayanad']):
            return """
REGIONAL CONTEXT - KERALA AGRICULTURE:
- Climate: Tropical humid climate with heavy monsoons
- Main Crops: Rice, coconut, spices (cardamom, pepper, cinnamon), rubber, tea, coffee
- Soil Types: Laterite soil, alluvial soil, forest soil
- Seasons: Two monsoons (SW and NE), year-round cultivation possible
- Best crops: Rice (Jyothi, Uma, Swetha), Coconut (WCT varieties), Spices, Rubber
- Agricultural zones: Coastal plains, midlands, highlands
- Specialty: Spice cultivation, plantation crops

Please provide advice specific to Kerala's tropical humid climate and plantation agriculture."""
        
        elif any(region in location_text for region in ['karnataka', 'bangalore', 'mysore', 'kodagu', 'coorg', 'belgaum', 'dharwad']):
            return """
REGIONAL CONTEXT - KARNATAKA AGRICULTURE:
- Climate: Tropical to semi-arid climate with varied agro-climatic zones
- Main Crops: Rice, ragi (finger millet), cotton, sugarcane, coffee, areca nut, tobacco
- Soil Types: Red soil, black soil, laterite soil, alluvial soil
- Seasons: Kharif (June-October), Rabi (November-March)
- Best varieties: Rice (BPT-5204, Intan), Ragi (MR-1, GPU-28), Cotton (Bt varieties)
- Agricultural zones: Coastal, Malnad (hill), Maidan (plains)
- Specialty: Coffee (Coorg region), areca nut, sericulture

Please provide advice specific to Karnataka's diverse agro-climatic conditions."""
        
        elif any(region in location_text for region in ['andhra pradesh', 'telangana', 'hyderabad', 'vijayawada', 'guntur', 'warangal']):
            return """
REGIONAL CONTEXT - ANDHRA PRADESH/TELANGANA AGRICULTURE:
- Climate: Tropical to semi-arid climate
- Main Crops: Rice, cotton, sugarcane, chili, turmeric, groundnut, maize
- Soil Types: Black cotton soil, red soil, alluvial soil
- Seasons: Kharif (June-October), Rabi (November-March)
- Best varieties: Rice (MTU varieties, BPT-5204), Cotton (Bt varieties), Chili (Guntur varieties)
- Agricultural zones: Coastal Andhra, Rayalaseema, Telangana
- Specialty: Spice cultivation (chili, turmeric), aquaculture

Please provide advice specific to Andhra Pradesh/Telangana's semi-arid conditions and spice cultivation."""
        
        elif any(region in location_text for region in ['punjab', 'haryana', 'ludhiana', 'chandigarh', 'amritsar', 'patiala']):
            return """
REGIONAL CONTEXT - PUNJAB/HARYANA AGRICULTURE:
- Climate: Semi-arid subtropical
- Main Crops: Wheat, rice, cotton, maize
- Best varieties: Wheat (HD-2967, PBW-343), Rice (PR-126)
- Soil: Alluvial, well-drained
- Known as India's granary

Please provide advice for Punjab/Haryana agricultural conditions."""
        
        elif any(region in location_text for region in ['uttar pradesh', 'up', 'lucknow', 'kanpur', 'agra', 'meerut', 'varanasi']):
            return """
REGIONAL CONTEXT - UTTAR PRADESH AGRICULTURE:
- Climate: Subtropical climate with distinct seasons
- Main Crops: Wheat, rice, sugarcane, potato, mustard, barley
- Soil Types: Alluvial soil (Gangetic plains), black soil (Bundelkhand)
- Seasons: Kharif (rice, sugarcane), Rabi (wheat, potato, mustard)
- Best varieties: Wheat (HD-2967, K-307), Rice (Sarjoo-52), Sugarcane (Co-0238)
- Specialty: Sugar production, potato cultivation

Please provide advice specific to Uttar Pradesh's diverse agricultural zones."""
        
        elif any(region in location_text for region in ['madhya pradesh', 'mp', 'bhopal', 'indore', 'gwalior', 'jabalpur']):
            return """
REGIONAL CONTEXT - MADHYA PRADESH AGRICULTURE:
- Climate: Tropical to subtropical climate
- Main Crops: Wheat, soybean, cotton, rice, gram (chickpea), mustard
- Soil Types: Black cotton soil, red soil, alluvial soil
- Seasons: Kharif (soybean, cotton), Rabi (wheat, gram)
- Best varieties: Soybean (JS-335, JS-93-05), Wheat (Lok-1, GW-322), Cotton (Bt varieties)
- Known as: Soybean state of India

Please provide advice specific to Madhya Pradesh's soybean-wheat systems."""
        
        elif any(region in location_text for region in ['maharashtra', 'nagpur', 'pune', 'mumbai', 'nashik', 'aurangabad']):
            return """
REGIONAL CONTEXT - MAHARASHTRA AGRICULTURE:
- Climate: Tropical to subtropical
- Main Crops: Cotton, soybean, sugarcane, wheat
- Best varieties: Cotton (Bt varieties), Soybean (JS-335)
- Soil: Black cotton soil (regur)

Please provide advice for Maharashtra's agricultural conditions."""
        
        elif any(region in location_text for region in ['rajasthan', 'jaipur', 'jodhpur', 'kota', 'udaipur', 'bikaner']):
            return """
REGIONAL CONTEXT - RAJASTHAN AGRICULTURE:
- Climate: Arid to semi-arid climate with low rainfall
- Main Crops: Wheat, barley, mustard, gram, bajra (pearl millet), cotton
- Soil Types: Desert soil, alluvial soil, red soil
- Best varieties: Wheat (Raj-4037, Lok-1), Mustard (Varuna, Kranti), Bajra (Raj-171)
- Specialty: Drought-tolerant crops, oilseeds

Please provide advice specific to Rajasthan's arid climate and drought-tolerant agriculture."""
        
        elif any(region in location_text for region in ['gujarat', 'ahmedabad', 'surat', 'rajkot', 'vadodara', 'gandhinagar']):
            return """
REGIONAL CONTEXT - GUJARAT AGRICULTURE:
- Climate: Semi-arid to arid climate
- Main Crops: Cotton, groundnut, wheat, sugarcane, bajra, castor
- Soil Types: Black cotton soil, alluvial soil, sandy soil
- Best varieties: Cotton (Bt varieties), Groundnut (GG-20, TG-37A), Wheat (GW-322)
- Specialty: Cotton and groundnut production

Please provide advice specific to Gujarat's semi-arid climate."""
        
        return "Please provide advice considering Indian agricultural conditions and practices."
        
        if hasattr(query, 'query_domain') and query.query_domain in domain_instructions:
            enhanced_parts.append(f"FOCUS AREA: {domain_instructions[query.query_domain]}")
        
        # Combine all parts
        return "\n\n".join(enhanced_parts)
    
    def _parse_gemini_response(self, gemini_response, query: AgricultureQuery, processing_time: float) -> AgentResponse:
        """Parse Gemini response and convert to structured AgentResponse format"""
        
        try:
            response_text = gemini_response.text
            
            # Parse structured sections from the response
            structured_data = self._parse_structured_response(response_text)
            
            # Extract recommendations from the structured format
            recommendations = self._extract_structured_recommendations(structured_data)
            
            # Calculate confidence based on response quality and structure
            confidence = self._calculate_confidence(gemini_response, response_text, structured_data)
            
            # Extract metadata including structured sections
            metadata = {
                "model": self.model_name,
                "processing_time": processing_time,
                "response_length": len(response_text),
                "recommendations_count": len(recommendations),
                "structured_format": True,
                "analysis_section": structured_data.get("analysis", ""),
                "agent_type": structured_data.get("agent_type", "General Agriculture"),
                "priority": structured_data.get("priority", "Medium"),
                "action_items": structured_data.get("action_items", [])
            }
            
            # Add safety ratings if available
            if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    metadata["safety_ratings"] = {
                        rating.category: rating.probability for rating in candidate.safety_ratings
                    }
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text=response_text,
                confidence_score=confidence,
                recommendations=recommendations,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                query_id=query.query_id,
                response_text="Error parsing the AI response",
                confidence_score=0.0,
                recommendations=[],
                metadata={"error": str(e)}
            )
    
    def _parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the structured response format into components"""
        
        structured_data = {
            "analysis": "",
            "recommendations": [],
            "agent_type": "General Agriculture",
            "priority": "Medium",
            "action_items": []
        }
        
        if not response_text:
            return structured_data
        
        # Split into sections based on markdown headers
        sections = response_text.split('##')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split('\n')
            header = lines[0].strip().upper()
            content_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            if 'ANALYSIS' in header:
                structured_data["analysis"] = '\n'.join(content_lines)
            
            elif 'RECOMMENDATIONS' in header:
                for line in content_lines:
                    if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                        structured_data["recommendations"].append(line[2:].strip())
            
            elif 'AGENT TYPE' in header:
                if content_lines:
                    structured_data["agent_type"] = content_lines[0]
            
            elif 'PRIORITY' in header:
                if content_lines:
                    structured_data["priority"] = content_lines[0]
            
            elif 'ACTION ITEMS' in header:
                for line in content_lines:
                    if line.startswith('•'):
                        structured_data["action_items"].append(line[1:].strip())
        
        return structured_data
    
    def _extract_structured_recommendations(self, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract recommendations from structured data"""
        
        recommendations = []
        
        # Process recommendations from the structured format
        for i, rec_text in enumerate(structured_data.get("recommendations", []), 1):
            recommendations.append({
                "id": f"rec_{i}",
                "text": rec_text,
                "type": "structured_recommendation",
                "priority": structured_data.get("priority", "Medium").lower(),
                "category": structured_data.get("agent_type", "General Agriculture")
            })
        
        # Add action items as additional recommendations
        for i, action in enumerate(structured_data.get("action_items", []), len(recommendations) + 1):
            recommendations.append({
                "id": f"action_{i}",
                "text": action,
                "type": "action_item", 
                "priority": "high" if "immediate" in action.lower() else "medium",
                "category": "Implementation"
            })
        
        return recommendations
    
    def _extract_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from Gemini response"""
        
        recommendations = []
        
        # Common recommendation indicators
        recommendation_markers = [
            "recommended", "suggest", "advice", "should", "consider",
            "सुझाव", "सिफारिश", "करना चाहिए", "उपयोग करें"
        ]
        
        # Split response into sentences
        sentences = response_text.replace('\n', ' ').split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short sentences
                # Check if sentence contains recommendation indicators
                if any(marker.lower() in sentence.lower() for marker in recommendation_markers):
                    recommendations.append({
                        "id": f"rec_{i+1}",
                        "text": sentence,
                        "type": "suggestion",
                        "priority": "medium"
                    })
                
                # Check for numbered/bulleted recommendations
                if sentence.startswith(('1.', '2.', '3.', '•', '-', '*')):
                    clean_rec = sentence.lstrip('123456789.-•* ')
                    if len(clean_rec) > 15:
                        recommendations.append({
                            "id": f"rec_{i+1}",
                            "text": clean_rec,
                            "type": "action_item",
                            "priority": "high"
                        })
        
        # Limit to top 10 recommendations to avoid overwhelming
        return recommendations[:10]
    
    def _calculate_confidence(self, gemini_response, response_text: str, structured_data: Dict[str, Any] = None) -> float:
        """Calculate confidence score based on response quality and structure indicators"""
        
        confidence = 0.5  # Base confidence
        
        # Check if response follows structured format (major confidence boost)
        if structured_data:
            # Boost confidence for having structured sections
            if structured_data.get("analysis"):
                confidence += 0.15
            if structured_data.get("recommendations"):
                confidence += 0.15
            if structured_data.get("agent_type"):
                confidence += 0.05
            if structured_data.get("priority"):
                confidence += 0.05
            if structured_data.get("action_items"):
                confidence += 0.10
        
        # Response length indicates detail (longer = higher confidence)
        if len(response_text) > 200:
            confidence += 0.1
        if len(response_text) > 500:
            confidence += 0.05
        
        # Check for specific agricultural terms (indicates domain relevance)
        agricultural_terms = [
            'crop', 'soil', 'fertilizer', 'irrigation', 'pest', 'disease',
            'variety', 'yield', 'harvest', 'sowing', 'farming', 'seed',
            'फसल', 'मिट्टी', 'खाद', 'सिंचाई', 'कीट', 'रोग', 'बीज'
        ]
        
        term_count = sum(1 for term in agricultural_terms if term.lower() in response_text.lower())
        confidence += min(term_count * 0.01, 0.1)  # Max 0.1 boost from terms
        
        # Check for specific recommendations (actionable advice)
        if "recommend" in response_text.lower() or "सुझाव" in response_text:
            confidence += 0.05
        
        # Check for quantitative information (specific measurements, costs, etc.)
        import re
        numbers_pattern = r'\d+(?:\.\d+)?(?:\s*(?:kg|gram|liter|rupee|₹|acre|hectare))'
        if re.search(numbers_pattern, response_text, re.IGNORECASE):
            confidence += 0.05
        
        # Check if response was blocked by safety filters
        if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
            candidate = gemini_response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                if candidate.finish_reason == "SAFETY":
                    confidence -= 0.3
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    async def process_multimodal_query(self, query: AgricultureQuery, image_path: Optional[str] = None) -> AgentResponse:
        """
        Process a query with optional image input (for crop/pest identification)
        
        Args:
            query: AgricultureQuery object
            image_path: Optional path to image file
            
        Returns:
            AgentResponse with multimodal analysis
        """
        
        try:
            # Prepare content list
            contents = []
            
            # Add text query
            enhanced_prompt = self._enhance_query_with_context(query)
            contents.append(enhanced_prompt)
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                from PIL import Image
                image = Image.open(image_path)
                contents.append(image)
                contents.append("Please analyze this image in the context of the agricultural question above.")
            
            # Configure generation
            generation_config = genai.GenerationConfig(
                max_output_tokens=2500,  # More tokens for image analysis
                temperature=0.6,
            )
            
            # Generate response
            start_time = datetime.now()
            
            response = self.model.generate_content(
                contents,
                generation_config=generation_config
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Parse response
            agricultural_response = self._parse_gemini_response(
                response, query, processing_time
            )
            
            # Add multimodal metadata
            agricultural_response.metadata["multimodal"] = True
            if image_path:
                agricultural_response.metadata["image_analyzed"] = True
                agricultural_response.metadata["image_path"] = image_path
            
            logger.info(f"✓ Multimodal query processed in {processing_time:.2f}s")
            
            return agricultural_response
            
        except Exception as e:
            logger.error(f"Error in multimodal processing: {e}")
            return await self.process_query(query)  # Fallback to text-only
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        
        return {
            "agent_id": self.agent_id,
            "model": self.model_name,
            "capabilities": [cap.value for cap in self.capabilities],
            "supported_languages": ["English", "Hindi", "Mixed (Hinglish)"],
            "multimodal_support": True,
            "api_provider": "Google Gemini",
            "sdk_version": "google-genai 1.29.0+",
            "specialization": "Indian Agriculture Advisory"
        }
    
    async def process_query_async(self, query: AgricultureQuery) -> AgentResponse:
        """
        Async wrapper for process_query method
        """
        # For now, call the synchronous method
        # In a full implementation, this would use proper async Gemini calls
        return await asyncio.create_task(
            asyncio.to_thread(self.process_query, query)
        )


async def test_gemini_agent():
    """Test function for the Gemini Agriculture Agent"""
    
    print("🌾 Testing Gemini Agriculture Agent...")
    
    try:
        # Initialize agent (will fail gracefully if no API key)
        agent = GeminiAgricultureAgent()
        
        # Test queries
        test_queries = [
            {
                "text": "What wheat variety is best for Punjab soil in Rabi season?",
                "lang": Language.ENGLISH,
                "description": "Crop recommendation query"
            },
            {
                "text": "मेरे गेहूं की फसल पर पीले धब्बे हैं, क्या करूं?",
                "lang": Language.HINDI,
                "description": "Pest management query in Hindi"
            },
            {
                "text": "Cotton की crop में कितना पानी लगता है per acre?",
                "lang": Language.MIXED,
                "description": "Irrigation query in Hinglish"
            }
        ]
        
        print(f"Agent Info: {agent.get_agent_info()}")
        print("\n" + "="*60)
        
        for i, test in enumerate(test_queries, 1):
            print(f"\nTest {i}: {test['description']}")
            print(f"Query: {test['text']}")
            
            # Create query object
            query = AgricultureQuery(
                query_text=test['text'],
                query_language=test['lang'],
                user_id=f"test_user_{i}"
            )
            
            # Process query
            response = await agent.process_query(query)
            
            # Display results
            print(f"Agent ID: {response.agent_id}")
            print(f"Confidence: {response.confidence_score:.2f}")
            print(f"Processing Time: {response.processing_time_ms or 0}ms")
            print(f"Response Length: {len(response.response_text)} chars")
            print(f"Recommendations: {len(response.recommendations)}")
            
            if response.confidence_score > 0.0:
                print("✓ Query processed successfully")
                # Show first 200 chars of response
                preview = response.response_text[:200] + "..." if len(response.response_text) > 200 else response.response_text
                print(f"Response Preview: {preview}")
            else:
                print(f"✗ Query failed: {response.response_text}")
            
            print("-" * 40)
        
        print("\n🎉 Gemini Agriculture Agent testing completed!")
        return True
        
    except ValueError as e:
        if "API key not found" in str(e):
            print("⚠️  Gemini API key not configured.")
            print("To use Gemini agent, set your API key:")
            print("1. Get API key from: https://aistudio.google.com/apikey")
            print("2. Set environment variable: GOOGLE_API_KEY=your_api_key")
            print("3. Or create .env file with: GOOGLE_API_KEY=your_api_key")
            return False
        else:
            print(f"✗ Error: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_gemini_agent())
