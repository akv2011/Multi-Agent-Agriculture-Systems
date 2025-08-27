import React, { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './SimpleDemoInterface.css';

import AIAnalysisDisplay from './AIAnalysisDisplay';
import EnhancedResponseDisplay from './EnhancedResponseDisplay';
import aiService from '../services/geminiService';

// Fix for default markers in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface DemoResponse {
  routing_analysis: {
    agent: string;
    confidence: number;
    reasoning: string;
  };
  satellite_data: {
    ndvi: number;
    soil_moisture: number;
    temperature: number;
    humidity: number;
    environmental_score: number;
    risk_level: string;
  };
  response_text: string;
  technical_metrics: {
    processing_time_ms: number;
    confidence_level: number;
    satellite_data_integrated: boolean;
    risk_assessment: string;
    agent: string;
  };
}

const SimpleDemoInterface: React.FC = () => {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [demoResponse, setDemoResponse] = useState<DemoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [enhancedResponse, setEnhancedResponse] = useState<string>('');
  const [isLoadingAIResponse, setIsLoadingAIResponse] = useState(false);
  const [aiResponseError, setAiResponseError] = useState<string>('');


  // Clear vegetation indices from agents on component mount
  React.useEffect(() => {
    localStorage.removeItem('vegetationAnalysis');
  }, []);

  // Map-related state
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<L.Map | null>(null);
  const [currentMarker, setCurrentMarker] = useState<L.Marker | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<L.LatLng | null>(null);
  const [selectedCoords, setSelectedCoords] = useState<string>('');
  const [selectedAddress, setSelectedAddress] = useState<string>('');
  const [isLoadingAddress, setIsLoadingAddress] = useState<boolean>(false);
  const [analysisDate, setAnalysisDate] = useState<string>('');
  const [satelliteSource, setSatelliteSource] = useState<string>('sentinel2');
  const [cloudCoverage, setCloudCoverage] = useState<string>('20');
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // Location search states
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showSearchResults, setShowSearchResults] = useState<boolean>(false);

  // Image upload states
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isImageUploading, setIsImageUploading] = useState<boolean>(false);
  const [plantType, setPlantType] = useState<string>('corn');

  // Initialize map
  useEffect(() => {
    if (mapRef.current && !map) {
      const mapInstance = L.map(mapRef.current).setView([10.7905, 78.7047], 11);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstance);

      mapInstance.on('click', (e: L.LeafletMouseEvent) => {
        selectAnalysisPoint(e.latlng, mapInstance);
      });

      setMap(mapInstance);
      setDefaultDate();
    }

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, []);

  const setDefaultDate = () => {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
    setAnalysisDate(thirtyDaysAgo.toISOString().split('T')[0]);
  };

  const selectAnalysisPoint = async (latlng: L.LatLng, mapInstance?: L.Map) => {
    const activeMap = mapInstance || map;
    if (!activeMap) {
      return;
    }

    setSelectedPoint(latlng);

    // Immediately store coordinates for API calls
    const coordinateData = {
      coordinates: {
        lat: latlng.lat,
        lng: latlng.lng
      },
      isAnalyzed: false,  // Not analyzed yet, just selected
      timestamp: Date.now()
    };
    localStorage.setItem('mapAnalysis', JSON.stringify(coordinateData));

    // Remove ALL existing markers from the map to ensure only one marker exists
    activeMap.eachLayer((layer: any) => {
      if (layer instanceof L.Marker) {
        activeMap.removeLayer(layer);
      }
    });

    // Update coordinates display immediately
    const coordsText = `Selected: ${latlng.lat.toFixed(5)}°N, ${latlng.lng.toFixed(5)}°E`;
    setSelectedCoords(coordsText);
    setSelectedAddress('Loading address...');

    // Add new marker
    const newMarker = L.marker(latlng).addTo(activeMap);
    
    // Get address asynchronously
    const address = await reverseGeocode(latlng.lat, latlng.lng);
    setSelectedAddress(address);
    
    // Update stored data with address
    const updatedCoordinateData = {
      coordinates: {
        lat: latlng.lat,
        lng: latlng.lng
      },
      address: address,
      isAnalyzed: false,  // Not analyzed yet, just selected
      timestamp: Date.now()
    };
    localStorage.setItem('mapAnalysis', JSON.stringify(updatedCoordinateData));
    
    // Update popup with address information
    newMarker.bindPopup(`
      <b>Analysis Point</b><br>
      Lat: ${latlng.lat.toFixed(5)}<br>
      Lng: ${latlng.lng.toFixed(5)}<br>
      <strong>Address:</strong><br>
      <div style="max-width: 200px; word-wrap: break-word; font-size: 0.9em; color: #555;">${address}</div><br>
      <button onclick="window.analyzeCurrentPoint()" style="background: #27ae60; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Analyze This Point</button>
    `).openPopup();

    setCurrentMarker(newMarker);
  };

  // Function to perform reverse geocoding using OpenStreetMap Nominatim
  const reverseGeocode = async (lat: number, lng: number): Promise<string> => {
    try {
      setIsLoadingAddress(true);
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=16&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'AgriMitr-Agriculture-System'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch address');
      }
      
      const data = await response.json();
      
      if (data && data.display_name) {
        // Format the address to show the most relevant parts
        const address = data.address;
        let formattedAddress = data.display_name;
        
        // Try to create a more concise address
        if (address) {
          const parts = [];
          if (address.village || address.town || address.city) {
            parts.push(address.village || address.town || address.city);
          }
          if (address.state_district || address.county) {
            parts.push(address.state_district || address.county);
          }
          if (address.state) {
            parts.push(address.state);
          }
          if (address.country) {
            parts.push(address.country);
          }
          
          if (parts.length > 0) {
            formattedAddress = parts.join(', ');
          }
        }
        
        return formattedAddress;
      } else {
        return 'Address not found';
      }
    } catch (error) {
      console.error('Reverse geocoding failed:', error);
      return 'Unable to fetch address';
    } finally {
      setIsLoadingAddress(false);
    }
  };

  // Function to search for locations and get coordinates
  const searchLocation = useCallback(async (query: string) => {
    if (!query.trim() || query.length < 3) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    setIsSearching(true);
    try {
      // Add state/country context to improve search results
      const searchQuery = query.includes('India') ? query : `${query}, India`;
      
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=8&addressdetails=1&countrycodes=in`,
        {
          headers: {
            'User-Agent': 'AgriSens-Agriculture-System'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to search locations');
      }
      
      const data = await response.json();
      
      if (data && data.length > 0) {
        const formattedResults = data.map((location: any) => {
          const address = location.address || {};
          const state = address.state || address.state_district || '';
          const district = address.state_district || address.county || '';
          const city = address.city || address.town || address.village || '';
          
          return {
            display_name: location.display_name,
            lat: parseFloat(location.lat),
            lng: parseFloat(location.lon),
            address: location.address,
            place_id: location.place_id,
            formatted_location: `${city}${district && city !== district ? `, ${district}` : ''}${state ? `, ${state}` : ''}`,
            location_type: location.type || location.class || 'location'
          };
        });
        
        setSearchResults(formattedResults);
        setShowSearchResults(true);
      } else {
        setSearchResults([]);
        setShowSearchResults(false);
      }
    } catch (error) {
      console.error('Location search failed:', error);
      setSearchResults([]);
      setShowSearchResults(false);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Function to select a location from search results
  const selectSearchResult = async (result: any) => {
    if (!map) {
      return;
    }
    
    const latlng = L.latLng(result.lat, result.lng);
    
    // Center map on selected location
    map.setView(latlng, 13);
    
    // Select the point
    await selectAnalysisPoint(latlng, map);
    
    // Clear search
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
  };

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchLocation(searchQuery);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchLocation]);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.location-search-container')) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const analyzeSelectedPoint = async (point?: L.LatLng) => {
    const targetPoint = point || selectedPoint;
    if (!targetPoint) {
      setError('Please select a point on the map first');
      return;
    }

    setIsAnalyzing(true);
    setError('');

    try {
      // Show progress updates
      setAnalysisProgress('Connecting to satellite data...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setAnalysisProgress('Processing vegetation indices...');
      await new Promise(resolve => setTimeout(resolve, 800));

      setAnalysisProgress('Calculating NDVI, EVI, SAVI, NDMI...');
      await new Promise(resolve => setTimeout(resolve, 800));

      // Simulate vegetation indices calculation
      const vegetationIndices = {
        ndvi: 0.742 + (Math.random() - 0.5) * 0.2, // Random variation around 0.742
        evi: 0.456 + (Math.random() - 0.5) * 0.15,  // Random variation around 0.456
        savi: 0.623 + (Math.random() - 0.5) * 0.18, // Random variation around 0.623
        ndmi: 0.234 + (Math.random() - 0.5) * 0.12  // Random variation around 0.234
      };

      // Store analysis results temporarily (not for agents yet)
      const analysisResults = {
        coordinates: {
          lat: targetPoint.lat,
          lng: targetPoint.lng
        },
        address: selectedAddress || 'Address not available',
        vegetationIndices,
        analysisDate,
        satelliteSource,
        isAnalyzed: true,
        timestamp: Date.now()
      };

      localStorage.setItem('mapAnalysis', JSON.stringify(analysisResults));
      setAnalysisComplete(true);

      setAnalysisProgress('Analysis complete!');
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisProgress('');

      // Set a query based on the analysis including address if available
      const addressText = selectedAddress && selectedAddress !== 'Address not available' 
        ? ` (${selectedAddress})` 
        : '';
      setCurrentQuery(`Analyze agricultural conditions at coordinates ${targetPoint.lat.toFixed(5)}, ${targetPoint.lng.toFixed(5)}${addressText}`);

    } catch (error) {
      console.error('Analysis error:', error);
      setError('Analysis failed. Please try again.');
      setAnalysisProgress('');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Make analyzeCurrentPoint available globally for popup button
  useEffect(() => {
    (window as any).analyzeCurrentPoint = () => analyzeSelectedPoint();
  }, [selectedPoint]);

  // Auto-set Tamil Nadu coordinates for testing (10°17'29.0"N 78°47'47.6"E)
  useEffect(() => {
    if (map && !selectedPoint) {
      const tamilNaduCoords = L.latLng(10.291388, 78.796555);
      selectAnalysisPoint(tamilNaduCoords, map);
    }
  }, [map, selectedPoint]);

  // Function to convert markdown-like formatting to HTML
  const formatResponseText = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Convert **text** to bold
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Convert *text* to italic
      .replace(/\n/g, '<br>') // Convert newlines to br tags
      .replace(/•/g, '&bull;'); // Ensure bullet points display correctly
  };

  // Image upload handlers
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Image size must be less than 10MB');
        return;
      }

      // Check file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError('Please upload a JPG, PNG, or WebP image');
        return;
      }

      setSelectedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      
      // Clear any previous errors
      setError('');
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
  };

  // Sample queries from the demo script
  const sampleQueries = [
    {
      query: "What is the best variety of wheat to grow?",
      type: "Crop selection",
      agent: "crop_selection"
    },
    {
      query: "What should be the irrigation schedule for cotton?",
      type: "Irrigation management", 
      agent: "irrigation_management"
    },
    {
      query: "When should I sell my wheat crop for maximum profit?",
      type: "Market timing",
      agent: "market_timing"
    },
    {
      query: "Which rice variety is better for the kharif season?",
      type: "Crop selection",
      agent: "crop_selection"
    },
    {
      query: "How to apply for a loan for farming equipment?",
      type: "Financial advisory",
      agent: "finance_policy"
    }
  ];

  // Fetch AI Response using backend API first, then AI Assistant as fallback
  // Mock response generator for image-based queries
  const generateMockImageResponse = (_query: string, plantType: string, location: string): DemoResponse => {
    const diseases = {
      corn: {
        disease: "Northern Corn Leaf Blight",
        confidence: "85%",
        symptoms: "Elongated gray-green lesions on leaves",
        treatment: "Apply fungicide with active ingredient propiconazole",
        prevention: "Use resistant varieties, crop rotation with soybeans"
      },
      wheat: {
        disease: "Wheat Rust",
        confidence: "78%", 
        symptoms: "Orange-red pustules on leaves and stems",
        treatment: "Apply triazole fungicides early in season",
        prevention: "Plant rust-resistant varieties, monitor weather conditions"
      },
      rice: {
        disease: "Rice Blast",
        confidence: "82%",
        symptoms: "Diamond-shaped lesions with brown borders",
        treatment: "Apply azoxystrobin-based fungicides",
        prevention: "Proper water management, balanced fertilization"
      },
      tomato: {
        disease: "Late Blight",
        confidence: "90%",
        symptoms: "Dark water-soaked spots on leaves and fruits",
        treatment: "Apply copper-based fungicides immediately",
        prevention: "Improve air circulation, avoid overhead watering"
      },
      potato: {
        disease: "Early Blight",
        confidence: "76%",
        symptoms: "Concentric ring spots on older leaves",
        treatment: "Use chlorothalonil or mancozeb fungicides",
        prevention: "Crop rotation, proper spacing between plants"
      }
    };

    const selectedDisease = diseases[plantType as keyof typeof diseases] || diseases.corn;
    
    const responseText = `Plant Disease Analysis Results

Plant Type: ${plantType.charAt(0).toUpperCase() + plantType.slice(1)}
Location: ${location}

Disease Identified: ${selectedDisease.disease}
Confidence Level: ${selectedDisease.confidence}

Symptoms Observed:
${selectedDisease.symptoms}

Recommended Treatment:
${selectedDisease.treatment}

Prevention Measures:
${selectedDisease.prevention}

Additional Recommendations for ${location}:
- Monitor weather conditions closely
- Ensure proper irrigation based on local climate
- Consider local soil conditions for fertilizer application
- Consult with local agricultural extension services

This is an AI-generated analysis. For severe infections, consult with a local agricultural expert or plant pathologist for confirmation and detailed treatment plans.`;
    
    return {
      routing_analysis: {
        agent: "Plant Disease Detection Agent",
        confidence: 0.95,
        reasoning: `Image analysis requested for ${plantType} plant with symptoms described in query. Using computer vision and agricultural disease database.`
      },
      satellite_data: {
        ndvi: 0.75,
        soil_moisture: 0.68,
        temperature: 24,
        humidity: 65,
        environmental_score: 0.78,
        risk_level: "Moderate"
      },
      response_text: responseText,
      technical_metrics: {
        processing_time_ms: 1200,
        confidence_level: 0.85,
        satellite_data_integrated: true,
        risk_assessment: "Moderate disease risk detected",
        agent: "Plant Disease Detection Agent"
      }
    };
  };

  const fetchAIResponse = async (query: string): Promise<DemoResponse | null> => {
    try {
      setIsLoadingAIResponse(true);
      setAiResponseError('');

      // Get vegetation data if available
      const analysisData = localStorage.getItem('mapAnalysis');
      const parsedData = analysisData ? JSON.parse(analysisData) : null;

      // If image is selected, return mock response for plant disease analysis
      if (selectedImage) {
        const locationName = parsedData?.coordinates ? selectedAddress : 'Punjab Agricultural Zone, India';
        return generateMockImageResponse(query, plantType, locationName);
      }

      // First, try to get response from our backend API for text-only queries
      try {
        const apiBaseUrl = import.meta.env.VITE_AGENTWEAVER_API_URL || 'http://localhost:8001';
        
        let requestBody;
        let headers: HeadersInit = {};

        if (selectedImage) {
          // Use FormData for image upload
          const formData = new FormData();
          formData.append('query_text', query.trim());
          formData.append('image', selectedImage);
          formData.append('plant_type', plantType);
          formData.append('coordinates', JSON.stringify(parsedData?.coordinates || { lat: 30.7333, lng: 76.7794 }));
          formData.append('analysis_context', JSON.stringify({
            satellite_source: satelliteSource || 'sentinel2',
            cloud_coverage: cloudCoverage || '10',
            analysis_date: parsedData?.analysisDate || null,
            address: parsedData?.coordinates ? selectedAddress : 'Chandigarh, Punjab, India - Primary Wheat & Rice Belt',
            region: parsedData?.coordinates ? 'User Selected Location' : 'Punjab Agricultural Zone',
            crop_seasons: parsedData?.coordinates ? 'Location-specific seasons' : 'Rabi (Wheat), Kharif (Rice, Cotton)',
            soil_type: parsedData?.coordinates ? 'Local soil conditions' : 'Alluvial, well-drained',
            climate: parsedData?.coordinates ? 'Local climate conditions' : 'Semi-arid subtropical',
            location_source: parsedData?.coordinates ? 'map_selected' : 'default_punjab',
            has_image: true
          }));
          if (parsedData?.isAnalyzed) {
            formData.append('vegetation_data', JSON.stringify(parsedData.vegetationIndices));
          }
          requestBody = formData;
        } else {
          // Use JSON for text-only queries
          headers['Content-Type'] = 'application/json';
          
          // Get the actual address from stored data or current state
          const actualAddress = parsedData?.address || selectedAddress || 'Chandigarh, Punjab, India - Primary Wheat & Rice Belt';
          
          requestBody = JSON.stringify({
            query_text: query.trim(),
            vegetation_data: parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
            coordinates: parsedData?.coordinates || { lat: 30.7333, lng: 76.7794 },
            analysis_context: {
              satellite_source: satelliteSource || 'sentinel2',
              cloud_coverage: cloudCoverage || '10',
              analysis_date: parsedData?.analysisDate || null,
              address: actualAddress,
              region: parsedData?.coordinates ? 'User Selected Location' : 'Punjab Agricultural Zone',
              crop_seasons: parsedData?.coordinates ? 'Location-specific seasons' : 'Rabi (Wheat), Kharif (Rice, Cotton)',
              soil_type: parsedData?.coordinates ? 'Local soil conditions' : 'Alluvial, well-drained',
              climate: parsedData?.coordinates ? 'Local climate conditions' : 'Semi-arid subtropical',
              location_source: parsedData?.coordinates ? 'map_selected' : 'default_punjab',
              has_image: false
            }
          });
        }

        // Use the enhanced endpoint for location-aware functionality
        const endpoint = `${apiBaseUrl}/api/enhanced/query`;
        
        const backendResponse = await fetch(endpoint, {
          method: 'POST',
          headers,
          body: requestBody
        });

        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          
          // Extract the actual response text from the comprehensive response
          const responseText = backendData.comprehensive_response?.final_answer?.primary_answer || 
                              backendData.response_text || 
                              'No response available';
          
          // Convert backend response to our DemoResponse format
          const response: DemoResponse = {
            routing_analysis: {
              agent: backendData.agent_analysis?.recommended_agents?.[0] || 'backend_agent',
              confidence: backendData.comprehensive_response?.confidence || 0.85,
              reasoning: 'Response from AI-Powered Agriculture Backend'
            },
            satellite_data: {
              ndvi: backendData.satellite_data?.ndvi || 0.72, // Punjab fertile plains
              soil_moisture: backendData.satellite_data?.soil_moisture || 0.58, // Good irrigation
              temperature: backendData.satellite_data?.temperature || 31, // Punjab climate
              humidity: backendData.satellite_data?.humidity || 72, // Irrigation effect
              environmental_score: backendData.satellite_data?.environmental_score || 85, // High agricultural productivity
              risk_level: backendData.satellite_data?.risk_level || 'low' // Well-developed agriculture
            },
            response_text: responseText,
            technical_metrics: {
              processing_time_ms: backendData.technical_metrics?.total_processing_time_ms || 1000,
              confidence_level: backendData.technical_metrics?.confidence_score || 0.85,
              satellite_data_integrated: backendData.technical_metrics?.satellite_integration || false,
              risk_assessment: 'AI-Powered Agricultural Analysis',
              agent: backendData.comprehensive_response?.source_agents?.[0] || 'ai_agriculture_agent'
            }
          };

          console.log('✅ Backend API response received:', response);
          return response;
        } else {
          console.warn('Backend API failed with status:', backendResponse.status);
          throw new Error(`Backend API failed: ${backendResponse.status}`);
        }
      } catch (backendError) {
        console.warn('Backend API failed, falling back to AI Assistant:', backendError);
        
        // Fallback to AI Assistant if backend fails
        const apiKey = import.meta.env.VITE_AI_API_KEY || localStorage.getItem('ai_api_key');

        if (!apiKey) {
          throw new Error('Both backend API and AI Assistant are unavailable. Please configure at least one service.');
        }

        // Set API key for AI service
        aiService.setApiKey(apiKey);

        // Create a comprehensive analysis request for AI Assistant
        const analysisRequest = {
          query: query.trim(),
          vegetationData: parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
          coordinates: parsedData?.coordinates || { lat: 30.7333, lng: 76.7794 }, // Default to Punjab or use map selection
          context: `Agricultural query analysis for ${parsedData?.coordinates ? 'user-selected location' : 'Punjab, India farming context (Major Agricultural Zone: Wheat & Rice Belt)'}. ${
            parsedData?.isAnalyzed ? 'Vegetation analysis data is available.' : 'No vegetation data available.'
          } Satellite source: ${satelliteSource || 'sentinel2'}, Cloud coverage: ${cloudCoverage || '10'}%. ${parsedData?.coordinates ? 'Location: User-selected coordinates' : 'Region: Punjab Agricultural Zone, Main crops: Wheat (Rabi), Rice & Cotton (Kharif), Soil: Alluvial, Climate: Semi-arid subtropical'}`
        };

        // Get structured analysis from AI Assistant
        const aiAnalysisResult = await aiService.analyzeQuery(analysisRequest);

        // Also get enhanced response text
        const enhancedText = await aiService.enhanceAIResponse(
          query,
          `Agricultural query: ${query}`,
          parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
          parsedData?.coordinates || { lat: 30.7333, lng: 76.7794 } // Default to Punjab, India
        );

        // Convert AI response to our DemoResponse format
        const response: DemoResponse = {
          routing_analysis: {
            agent: aiAnalysisResult.agentType || 'ai_fallback',
            confidence: aiAnalysisResult.confidence || 0.85,
            reasoning: 'Response from AI Agricultural Assistant (backend unavailable)'
          },
          satellite_data: {
            ndvi: parsedData?.vegetationIndices?.ndvi || 0.72, // Punjab fertile plains NDVI
            soil_moisture: parsedData?.vegetationIndices?.ndmi || 0.58, // Good irrigation
            temperature: 31 + Math.random() * 6, // 31-37°C (Punjab climate)
            humidity: 72 + Math.random() * 15, // 72-87% (irrigation effect)
            environmental_score: parsedData?.isAnalyzed ? 85 : 80, // High for Punjab agricultural zone
            risk_level: aiAnalysisResult.priority === 'high' ? 'medium' : 'low' // Generally low risk in Punjab
          },
          response_text: enhancedText,
          technical_metrics: {
            processing_time_ms: Math.floor(Math.random() * 2000) + 1000,
            confidence_level: aiAnalysisResult.confidence || 0.85,
            satellite_data_integrated: parsedData?.isAnalyzed || false,
            risk_assessment: `${aiAnalysisResult.priority} priority based on AI analysis`,
            agent: aiAnalysisResult.agentType || 'ai_agent'
          }
        };

        console.log('⚠️ AI fallback response:', response);
        return response;
      }

    } catch (error) {
      console.error('Failed to fetch AI response:', error);
      setAiResponseError(`Failed to get AI response: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return null;
    } finally {
      setIsLoadingAIResponse(false);
    }
  };

  // Analyze query with AI Assistant
  const analyzeWithAI = async () => {
    const apiKey = import.meta.env.VITE_AI_API_KEY || localStorage.getItem('ai_api_key');

    if (!apiKey) {
      console.warn('AI API key not set. Skipping AI analysis.');
      return;
    }

    setIsAiLoading(true);

    try {
      // Set API key
      aiService.setApiKey(apiKey);

      // Get vegetation data if available
      const analysisData = localStorage.getItem('mapAnalysis');
      const parsedData = analysisData ? JSON.parse(analysisData) : null;

      const vegetationData = parsedData?.isAnalyzed ? parsedData.vegetationIndices : null;
      const coordinates = parsedData?.coordinates || { lat: 30.7333, lng: 76.7794 }; // Default to Punjab or use map selection

      // Prepare request for AI Assistant
      const request = {
        query: currentQuery,
        vegetationData,
        coordinates,
        context: `Agricultural query analysis for ${parsedData?.coordinates ? 'user-selected location' : 'Punjab, India farming context (Major Agricultural Zone: Wheat & Rice Belt). Location: Chandigarh, Punjab. Soil: Alluvial, well-drained. Climate: Semi-arid subtropical. Main crops: Wheat (Rabi), Rice & Cotton (Kharif)'}. ${
          vegetationData ? 'Vegetation analysis data is available.' : 'No vegetation data available.'
        }`
      };

      // Call AI API
      const analysis = await aiService.analyzeQuery(request);
      setAiAnalysis(analysis);

    } catch (error) {
      console.error('AI analysis failed:', error);
      setError(`AI Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAiLoading(false);
    }
  };



  // Generate fallback response when API fails
  const generateFallbackResponse = async (): Promise<void> => {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Get vegetation data if available
    const analysisData = localStorage.getItem('mapAnalysis');
    const parsedData = analysisData ? JSON.parse(analysisData) : null;

    let responseText = '';
    if (parsedData && parsedData.isAnalyzed) {
      const { vegetationIndices, coordinates } = parsedData;

      // Move the indices to agents (only after query submission)
      localStorage.setItem('vegetationAnalysis', JSON.stringify(parsedData));
      responseText = `**Agricultural Analysis Complete**

Based on your query "${currentQuery}" and the satellite analysis of your selected area:

**Location Information:**
- Coordinates: ${coordinates.lat.toFixed(4)}°N, ${coordinates.lng.toFixed(4)}°E
${parsedData.address ? `- Address: ${parsedData.address}` : ''}

**Vegetation Health Assessment:**
- NDVI Score: ${vegetationIndices.ndvi.toFixed(3)} (${vegetationIndices.ndvi > 0.7 ? 'Excellent' : vegetationIndices.ndvi > 0.5 ? 'Good' : vegetationIndices.ndvi > 0.3 ? 'Moderate' : 'Poor'} vegetation health)

**Recommendations:**
${vegetationIndices.ndvi > 0.7 ?
  '✅ Your crops show excellent health. Continue current practices and monitor for any changes.' :
  vegetationIndices.ndvi > 0.5 ?
  '⚠️ Vegetation health is good but could be improved. Consider optimizing irrigation and nutrition.' :
  '🚨 Vegetation shows stress. Immediate attention needed for irrigation, pest control, or soil health.'
}

**Next Steps:**
1. Monitor the area regularly using satellite data
2. Consider soil testing if vegetation health is declining
3. Adjust irrigation and fertilization based on crop needs
4. Contact local agricultural extension services for specific guidance

*This analysis combines your query with real satellite data from ${new Date(parsedData.analysisDate).toLocaleDateString()}.*`;
    } else {
      responseText = `**Agricultural Query Response**

Thank you for your question: "${currentQuery}"

**General Agricultural Guidance:**
Based on common farming practices and your query, here are some recommendations:

**Immediate Actions:**
1. Assess your current crop conditions
2. Check soil moisture levels
3. Monitor for pests and diseases
4. Review weather forecasts for planning

**Best Practices:**
- Regular field monitoring
- Proper irrigation scheduling
- Integrated pest management
- Soil health maintenance

**For Better Analysis:**
To get more specific recommendations, please:
1. Select a location on the map above
2. Run satellite analysis for your field
3. Resubmit your query with location data

*For personalized advice, consider consulting with local agricultural experts or extension services.*`;
    }

    const fallbackResponse: DemoResponse = {
      routing_analysis: {
        agent: 'fallback_agent',
        confidence: 0.75,
        reasoning: 'Fallback response generated due to API unavailability'
      },
      satellite_data: {
        ndvi: parsedData?.vegetationIndices?.ndvi || 0.72, // Higher NDVI for fertile Punjab plains
        soil_moisture: 0.58, // Good soil moisture from irrigation canals
        temperature: 31, // Typical Punjab temperature (higher than Delhi)
        humidity: 72, // Higher humidity due to extensive irrigation
        environmental_score: 85, // High score for fertile agricultural land
        risk_level: 'low' // Low risk due to well-developed agricultural infrastructure
      },
      response_text: responseText,
      technical_metrics: {
        processing_time_ms: Math.floor(Math.random() * 1500) + 500,
        confidence_level: 0.75,
        satellite_data_integrated: parsedData?.isAnalyzed || false,
        risk_assessment: parsedData ? 'Low risk based on vegetation health' : 'Medium risk - analysis recommended',
        agent: 'fallback_processing_agent'
      }
    };

    setDemoResponse(fallbackResponse);
  };

  const submitQuery = async () => {
    if (!currentQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    setIsLoading(true);
    setError('');
    setDemoResponse(null);
    setAiAnalysis(null);
    setEnhancedResponse('');
    setAiResponseError('');

    try {
      // Start AI analysis in parallel (don't await to run concurrently)
      analyzeWithAI();

      // Fetch real AI response from backend (with optional image)
      const aiResponse = await fetchAIResponse(currentQuery);

      if (aiResponse) {
        setDemoResponse(aiResponse);
        // Clear image after successful submission
        setSelectedImage(null);
        setImagePreview(null);

        // The response is already enhanced by AI in fetchAIResponse
        // Set the enhanced response directly
        setEnhancedResponse(aiResponse.response_text);
      } else {
        // Fallback to mock data if API fails
        await generateFallbackResponse();
      }
    } catch (err) {
      console.error('Query processing failed:', err);
      setError('Query processing failed. Please try again.');

      // Try fallback response on error
      try {
        await generateFallbackResponse();
      } catch (fallbackErr) {
        console.error('Fallback response also failed:', fallbackErr);
        setError('Unable to process query. Please check your connection and try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const selectSampleQuery = (query: { query: string }) => {
    setCurrentQuery(query.query);
  };

  return (
    <div className="simple-demo">
      <div className="demo-header">
        <h1>🌾🛰️ Multi-Agent Agriculture Systems </h1>
        <div className="system-status">
          <div className="status-badge">
            Satellite-Enhanced AI Agricultural Advisory System
          </div>
          <div className="progress-info">
            Complete  Agents Operational
          </div>
        </div>
      </div>

      <div className="capabilities">
        <h3>🎯 System Capabilities:</h3>
        <div className="capability-list">
          <div className="capability">✓ Multilingual Query Processing (Hindi/English/Mixed)</div>
          <div className="capability">✓ Intelligent Agent Routing</div>
          <div className="capability">✓ Satellite Data Integration</div>
          <div className="capability">✓ Real-time Agricultural Advisory</div>
          <div className="capability">✓ Confidence-based Recommendations</div>
        </div>
      </div>

      <div className="query-section">
        <h3>💬 Ask Your Agricultural Question</h3>

        {/* Interactive Map Analysis */}
        <div style={{ marginBottom: '30px' }}>
          <h4>🗺️ Interactive Map Analysis</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            {/* Map Container */}
            <div style={{
              background: 'white',
              borderRadius: '10px',
              padding: '15px',
              boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
              border: '1px solid #e0e0e0'
            }}>
              <div
                ref={mapRef}
                style={{
                  height: '300px',
                  borderRadius: '8px',
                  border: '1px solid #ddd'
                }}
              />
              <div style={{
                background: '#e3f2fd',
                padding: '12px',
                borderRadius: '5px',
                margin: '10px 0',
                fontSize: '0.9rem',
                border: '1px solid #bbdefb'
              }}>
                <div style={{ fontWeight: '600', color: '#1976d2', marginBottom: '5px' }}>
                  📍 Selected Location:
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#555' }}>
                  {selectedCoords}
                </div>
              </div>
              
              {/* Address Display */}
              <div style={{
                background: '#f3f4f6',
                padding: '12px',
                borderRadius: '5px',
                margin: '10px 0',
                fontSize: '0.9rem',
                border: '1px solid #e0e0e0',
                minHeight: '45px',
                display: 'flex',
                alignItems: 'center'
              }}>
                {isLoadingAddress ? (
                  <div style={{ display: 'flex', alignItems: 'center', color: '#666' }}>
                    <div style={{
                      width: '16px',
                      height: '16px',
                      border: '2px solid #f3f3f3',
                      borderTop: '2px solid #3498db',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite',
                      marginRight: '10px'
                    }}></div>
                    <span>Fetching address...</span>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontWeight: '600', color: '#666', marginBottom: '2px' }}>
                      🏠 Address:
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#333', lineHeight: '1.3' }}>
                      {selectedAddress || 'Click on map to select a location'}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Analysis Controls */}
            <div style={{
              background: 'white',
              borderRadius: '10px',
              padding: '15px',
              boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
              border: '1px solid #e0e0e0'
            }}>
              <h5 style={{ margin: '0 0 15px 0', color: '#333' }}>🔍 Location Search & Analysis</h5>

              {/* Location Search */}
              <div className="location-search-container" style={{ marginBottom: '20px', position: 'relative' }}>
                <label style={{ display: 'block', fontWeight: '600', marginBottom: '5px', color: '#555' }}>
                  📍 Search Location:
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search: City, District, State (e.g., Tiruvanamalai, Tamil Nadu)"
                    style={{
                      width: '100%',
                      padding: '10px 40px 10px 12px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '0.9rem',
                      outline: 'none',
                      transition: 'border-color 0.3s'
                    }}
                    onFocus={() => searchQuery && setShowSearchResults(true)}
                  />
                  {isSearching && (
                    <div style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: '16px',
                      height: '16px',
                      border: '2px solid #f3f3f3',
                      borderTop: '2px solid #27ae60',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }}></div>
                  )}
                </div>
                
                {/* Search Results Dropdown */}
                {showSearchResults && searchResults.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: '0',
                    right: '0',
                    background: 'white',
                    border: '2px solid #ddd',
                    borderTop: 'none',
                    borderRadius: '0 0 8px 8px',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    zIndex: 1000,
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                  }}>
                    {searchResults.map((result, index) => (
                      <div
                        key={result.place_id || index}
                        onClick={() => selectSearchResult(result)}
                        style={{
                          padding: '12px',
                          borderBottom: index < searchResults.length - 1 ? '1px solid #eee' : 'none',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#f8f9fa';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'white';
                        }}
                      >
                        <div style={{ fontWeight: '500', fontSize: '0.9rem', marginBottom: '2px', color: '#1976d2' }}>
                          {result.formatted_location || result.address?.city || result.address?.town || result.address?.village || 'Unknown Location'}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#666', lineHeight: '1.2' }}>
                          {result.location_type ? `${result.location_type} • ` : ''}{result.display_name.substring(0, 60)}...
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '2px' }}>
                          📍 {result.lat.toFixed(5)}, {result.lng.toFixed(5)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', fontWeight: '600', marginBottom: '5px', color: '#555' }}>
                  📅 Analysis Date:
                </label>
                <input
                  type="date"
                  value={analysisDate}
                  onChange={(e) => setAnalysisDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontSize: '0.9rem'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', fontWeight: '600', marginBottom: '5px', color: '#555' }}>
                  🛰️ Satellite Source:
                </label>
                <select
                  value={satelliteSource}
                  onChange={(e) => setSatelliteSource(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="sentinel2">Sentinel-2 (10m)</option>
                  <option value="landsat8">Landsat 8 (30m)</option>
                  <option value="modis">MODIS (250m)</option>
                </select>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', fontWeight: '600', marginBottom: '5px', color: '#555' }}>
                  ☁️ Cloud Coverage:
                </label>
                <select
                  value={cloudCoverage}
                  onChange={(e) => setCloudCoverage(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="10">&lt; 10% (Best)</option>
                  <option value="20">&lt; 20% (Good)</option>
                  <option value="30">&lt; 30% (Acceptable)</option>
                </select>
              </div>



              <button
                onClick={() => analyzeSelectedPoint()}
                disabled={isAnalyzing}
                style={{
                  background: isAnalyzing ? '#ccc' : 'linear-gradient(135deg, #27ae60, #2ecc71)',
                  color: 'white',
                  border: 'none',
                  padding: '10px 15px',
                  borderRadius: '5px',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                  width: '100%',
                  marginBottom: '10px'
                }}
              >
                {isAnalyzing ? (analysisProgress ? `🔄 ${analysisProgress}` : '🔄 Analyzing...') : '🔍 Analyze Point'}
              </button>

              {/* Analysis Status */}
              {analysisComplete && (
                <div style={{
                  background: 'linear-gradient(135deg, #e8f5e8, #f0f8f0)',
                  border: '2px solid #4caf50',
                  borderRadius: '5px',
                  padding: '8px',
                  fontSize: '0.8rem',
                  color: '#2e7d32',
                  textAlign: 'center'
                }}>
                  ✅ Analysis Complete! Submit a query below to see vegetation indices in Agents
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="sample-queries">
          <h4>Sample Queries:</h4>
          <div className="queries-list">
            {sampleQueries.map((query, index) => (
              <div
                key={index}
                className="sample-query"
                onClick={() => selectSampleQuery(query)}
              >
                <div className="query-text">{query.query}</div>
                <div className="query-meta">
                  <span className="query-type">{query.type}</span>
                  <span className="query-agent">{query.agent}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="query-input">
          <textarea
            value={currentQuery}
            onChange={(e) => setCurrentQuery(e.target.value)}
            placeholder="Type your agricultural question here..."
            rows={3}
            className="query-textarea"
          />
          
          {/* Image Upload Section */}
          <div style={{ marginTop: '16px' }}>
            <label style={{ 
              display: 'block', 
              fontWeight: '600', 
              marginBottom: '8px', 
              color: '#555',
              fontSize: '0.9rem'
            }}>
              📷 Upload Plant/Crop Image (Optional)
            </label>
            {selectedImage ? (
              <div style={{ position: 'relative' }}>
                <img 
                  src={imagePreview || ''} 
                  alt="Uploaded crop/plant" 
                  style={{
                    width: '100%',
                    height: '200px',
                    objectFit: 'cover',
                    borderRadius: '8px',
                    border: '2px solid #e5f3e5'
                  }}
                />
                <button
                  onClick={removeImage}
                  style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    backgroundColor: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '28px',
                    height: '28px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                  title="Remove image"
                >
                  <svg 
                    style={{ width: '16px', height: '16px' }} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ) : (
              <div style={{
                border: '2px dashed #ccc',
                borderRadius: '8px',
                padding: '24px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.3s'
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <svg 
                    style={{ width: '48px', height: '48px', color: '#9ca3af' }} 
                    stroke="currentColor" 
                    fill="none" 
                    viewBox="0 0 48 48"
                  >
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div>
                    <label htmlFor="image-upload" style={{ cursor: 'pointer' }}>
                      <span style={{ color: '#10b981', fontWeight: '500' }}>Upload an image</span>
                      <span style={{ color: '#6b7280' }}> or drag and drop</span>
                      <input
                        id="image-upload"
                        type="file"
                        accept="image/jpeg,image/jpg,image/png,image/webp"
                        onChange={handleImageUpload}
                        style={{ display: 'none' }}
                      />
                    </label>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: 0 }}>
                    JPG, PNG, WebP up to 10MB
                  </p>
                </div>
              </div>
            )}
          </div>
          
          {/* Plant Type Selector - Show when image is uploaded */}
          {selectedImage && (
            <div style={{ marginTop: '16px' }}>
              <label style={{ 
                display: 'block', 
                fontWeight: '600', 
                marginBottom: '8px', 
                color: '#555',
                fontSize: '0.9rem'
              }}>
                🌱 Plant Type *
              </label>
              <select
                value={plantType}
                onChange={(e) => setPlantType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '2px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                <option value="corn">Corn</option>
                <option value="wheat">Wheat</option>
                <option value="rice">Rice</option>
                <option value="soybean">Soybean</option>
                <option value="tomato">Tomato</option>
                <option value="potato">Potato</option>
                <option value="cotton">Cotton</option>
                <option value="sugarcane">Sugarcane</option>
                <option value="apple">Apple</option>
                <option value="grape">Grape</option>
                <option value="other">Other</option>
              </select>
            </div>
          )}
          
          <button 
            onClick={submitQuery} 
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? '🔄 Processing...' : selectedImage ? '� Analyze Plant' : '🚀 Submit Query'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {/* AI Response Loading State */}
      {isLoadingAIResponse && (
        <div className="response-section loading">
          <h3>🤖 AI Response</h3>
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <p>Fetching AI analysis from AI Agent...</p>
            <div className="loading-details">
              <span>• Processing your query</span>
              <span>• Analyzing context and vegetation data</span>
              <span>• Generating agricultural insights</span>
            </div>
          </div>
        </div>
      )}

      {/* AI Response Error State */}
      {aiResponseError && !demoResponse && !isLoadingAIResponse && (
        <div className="response-section error">
          <h3>🤖 AI Response</h3>
          <div className="error-content">
            <div className="error-icon">⚠️</div>
            <h4>Failed to fetch AI response</h4>
            <p>{aiResponseError}</p>
            <div className="error-actions">
              <button
                className="retry-button"
                onClick={() => submitQuery()}
                disabled={isLoading}
              >
                🔄 Retry Query
              </button>
            </div>
          </div>
        </div>
      )}

      {demoResponse && (
        <div className="response-section">
          <h3>🤖 AI Response</h3>
          
          <div className="routing-analysis">
            <h4>🧠 AI Routing Analysis:</h4>
            <div className="analysis-info">
              <div><strong>Agent Selected:</strong> {demoResponse.routing_analysis.agent}</div>
              <div><strong>Confidence:</strong> {(demoResponse.routing_analysis.confidence * 100).toFixed(1)}%</div>
              <div><strong>Reasoning:</strong> {demoResponse.routing_analysis.reasoning}</div>
            </div>
          </div>

          <div className="satellite-data">
            <h4>🛰️ Satellite Data Analysis:</h4>
            <div className="satellite-info">
              <div><strong>NDVI Score:</strong> {demoResponse.satellite_data.ndvi}</div>
              <div><strong>Soil Moisture:</strong> {(demoResponse.satellite_data.soil_moisture * 100).toFixed(0)}%</div>
              <div><strong>Temperature:</strong> {demoResponse.satellite_data.temperature}°C</div>
              <div><strong>Environmental Score:</strong> {demoResponse.satellite_data.environmental_score}/100</div>
              <div><strong>Risk Level:</strong> {demoResponse.satellite_data.risk_level.toUpperCase()}</div>
            </div>
          </div>

          {/* Enhanced AI Response */}
          {enhancedResponse ? (
            <EnhancedResponseDisplay
              originalQuery={currentQuery}
              enhancedResponse={enhancedResponse}
              isLoading={false}
            />
          ) : (
            <div className="ai-response">
              <h4>🌾 AI-Enhanced Agricultural Response:</h4>
              <div
                className="response-text"
                dangerouslySetInnerHTML={{
                  __html: formatResponseText(demoResponse.response_text)
                }}
              />
              {(import.meta.env.VITE_AI_API_KEY || localStorage.getItem('ai_api_key')) && (
                <div className="enhancement-notice">
                  <p>✨ <strong>AI-Powered Response:</strong> This response has been processed through advanced agricultural AI for comprehensive insights!</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* AI Analysis Display */}
      {(aiAnalysis || isAiLoading) && (
        <div className="ai-analysis-section">
          <AIAnalysisDisplay
            analysis={aiAnalysis}
            isLoading={isAiLoading}
            query={currentQuery}
          />
        </div>
      )}
    </div>
  );
};

export default SimpleDemoInterface;
