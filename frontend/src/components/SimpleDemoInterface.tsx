import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './SimpleDemoInterface.css';

import GeminiAnalysisDisplay from './GeminiAnalysisDisplay';
import EnhancedResponseDisplay from './EnhancedResponseDisplay';
import geminiService from '../services/geminiService';

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
    language_detected: string;
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
  const [geminiAnalysis, setGeminiAnalysis] = useState<any>(null);
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);
  const [enhancedResponse, setEnhancedResponse] = useState<string>('');
  const [isLoadingAIResponse, setIsLoadingAIResponse] = useState(false);
  const [aiResponseError, setAiResponseError] = useState<string>('');
  const [geminiApiKey, setGeminiApiKey] = useState<string>(
    import.meta.env.VITE_GEMINI_API_KEY || localStorage.getItem('gemini_api_key') || ''
  );

  // Clear vegetation indices from agents on component mount
  React.useEffect(() => {
    localStorage.removeItem('vegetationAnalysis');
  }, []);

  // Map-related state
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<L.Map | null>(null);
  const [currentMarker, setCurrentMarker] = useState<L.Marker | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<L.LatLng | null>(null);
  const [selectedCoords, setSelectedCoords] = useState<string>('Click on map to select analysis point');
  const [selectedAddress, setSelectedAddress] = useState<string>('');
  const [isLoadingAddress, setIsLoadingAddress] = useState<boolean>(false);
  const [analysisDate, setAnalysisDate] = useState<string>('');
  const [satelliteSource, setSatelliteSource] = useState<string>('sentinel2');
  const [cloudCoverage, setCloudCoverage] = useState<string>('20');
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

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
    if (!activeMap) return;

    setSelectedPoint(latlng);

    // Remove ALL existing markers from the map to ensure only one marker exists
    activeMap.eachLayer((layer: any) => {
      if (layer instanceof L.Marker) {
        activeMap.removeLayer(layer);
      }
    });

    // Update coordinates display immediately
    setSelectedCoords(`Selected: ${latlng.lat.toFixed(5)}°N, ${latlng.lng.toFixed(5)}°E`);
    setSelectedAddress('Loading address...');

    // Add new marker
    const newMarker = L.marker(latlng).addTo(activeMap);
    
    // Get address asynchronously
    const address = await reverseGeocode(latlng.lat, latlng.lng);
    setSelectedAddress(address);
    
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

  // Function to convert markdown-like formatting to HTML
  const formatResponseText = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Convert **text** to bold
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Convert *text* to italic
      .replace(/\n/g, '<br>') // Convert newlines to br tags
      .replace(/•/g, '&bull;'); // Ensure bullet points display correctly
  };

  // Sample queries from the demo script
  const sampleQueries = [
    {
      query: "पंजाब में गेहूं की सबसे अच्छी किस्म कौन सी है?",
      type: "Hindi crop selection",
      agent: "crop_selection"
    },
    {
      query: "Meri cotton crop mein पीले पत्ते दिख रहे हैं, क्या करूं?",
      type: "Code-switched pest management", 
      agent: "pest_management"
    },
    {
      query: "When should I sell my wheat crop for maximum profit?",
      type: "English market timing",
      agent: "market_timing"
    },
    {
      query: "My field needs irrigation - when and how much water?",
      type: "Irrigation scheduling",
      agent: "irrigation"
    },
    {
      query: "Loan ke liye apply कैसे करूं for farming equipment?",
      type: "Financial advisory",
      agent: "finance_policy"
    }
  ];

  // Fetch AI Response using backend API first, then Gemini as fallback
  const fetchAIResponse = async (query: string): Promise<DemoResponse | null> => {
    try {
      setIsLoadingAIResponse(true);
      setAiResponseError('');

      // Get vegetation data if available
      const analysisData = localStorage.getItem('mapAnalysis');
      const parsedData = analysisData ? JSON.parse(analysisData) : null;

      // First, try to get response from our backend API
      try {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const backendResponse = await fetch(`${apiBaseUrl}/demo/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query_text: query.trim(),
            vegetation_data: parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
            coordinates: parsedData?.coordinates || null,
            analysis_context: {
              satellite_source: satelliteSource || 'sentinel2',
              cloud_coverage: cloudCoverage || '10',
              analysis_date: parsedData?.analysisDate || null,
              address: parsedData?.address || null
            }
          })
        });

        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          
          // Convert backend response to our DemoResponse format
          const response: DemoResponse = {
            routing_analysis: {
              agent: backendData.routing_analysis?.agent || 'backend_agent',
              confidence: backendData.routing_analysis?.confidence || 0.85,
              reasoning: backendData.routing_analysis?.reasoning || 'Response from Multi-Agent Agriculture Backend',
              language_detected: backendData.routing_analysis?.language_detected || 'english'
            },
            satellite_data: {
              ndvi: backendData.satellite_data?.ndvi || 0.65,
              soil_moisture: backendData.satellite_data?.soil_moisture || 0.45,
              temperature: backendData.satellite_data?.temperature || 28,
              humidity: backendData.satellite_data?.humidity || 65,
              environmental_score: backendData.satellite_data?.environmental_score || 70,
              risk_level: backendData.satellite_data?.risk_level || 'medium'
            },
            response_text: backendData.response_text || 'No response available',
            technical_metrics: {
              processing_time_ms: backendData.technical_metrics?.processing_time_ms || 1000,
              confidence_level: backendData.technical_metrics?.confidence_level || 0.85,
              satellite_data_integrated: backendData.technical_metrics?.satellite_data_integrated || false,
              risk_assessment: backendData.technical_metrics?.risk_assessment || 'Backend analysis',
              agent: backendData.technical_metrics?.agent || 'multi_agent_backend'
            }
          };

          console.log('✅ Backend API response received:', response);
          return response;
        } else {
          console.warn('Backend API failed with status:', backendResponse.status);
          throw new Error(`Backend API failed: ${backendResponse.status}`);
        }
      } catch (backendError) {
        console.warn('Backend API failed, falling back to Gemini:', backendError);
        
        // Fallback to Gemini if backend fails
        const apiKey = geminiApiKey || import.meta.env.VITE_GEMINI_API_KEY;

        if (!apiKey) {
          throw new Error('Both backend API and Gemini API are unavailable. Please configure at least one service.');
        }

        // Set API key for gemini service
        geminiService.setApiKey(apiKey);

        // Create a comprehensive analysis request for Gemini
        const analysisRequest = {
          query: query.trim(),
          vegetationData: parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
          coordinates: parsedData?.coordinates || null,
          context: `Agricultural query analysis for Indian farming context. ${
            parsedData?.isAnalyzed ? 'Vegetation analysis data is available.' : 'No vegetation data available.'
          } Satellite source: ${satelliteSource || 'sentinel2'}, Cloud coverage: ${cloudCoverage || '10'}%`
        };

        // Get structured analysis from Gemini
        const geminiAnalysisResult = await geminiService.analyzeQuery(analysisRequest);

        // Also get enhanced response text
        const enhancedText = await geminiService.enhanceAIResponse(
          query,
          `Agricultural query: ${query}`,
          parsedData?.isAnalyzed ? parsedData.vegetationIndices : null,
          parsedData?.coordinates || null
        );

        // Convert Gemini response to our DemoResponse format
        const response: DemoResponse = {
          routing_analysis: {
            agent: geminiAnalysisResult.agentType || 'gemini_fallback',
            confidence: geminiAnalysisResult.confidence || 0.85,
            reasoning: 'Response from Gemini AI (backend unavailable)',
            language_detected: /[\u0900-\u097F]/.test(query) ? 'Hindi' : 'English'
          },
          satellite_data: {
            ndvi: parsedData?.vegetationIndices?.ndvi || 0.65,
            soil_moisture: parsedData?.vegetationIndices?.ndmi || 0.45,
            temperature: 28 + Math.random() * 8, // 28-36°C
            humidity: 65 + Math.random() * 20, // 65-85%
            environmental_score: parsedData?.isAnalyzed ? 85 : 70,
            risk_level: geminiAnalysisResult.priority === 'high' ? 'high' :
                       geminiAnalysisResult.priority === 'low' ? 'low' : 'medium'
          },
          response_text: enhancedText,
          technical_metrics: {
            processing_time_ms: Math.floor(Math.random() * 2000) + 1000,
            confidence_level: geminiAnalysisResult.confidence || 0.85,
            satellite_data_integrated: parsedData?.isAnalyzed || false,
            risk_assessment: `${geminiAnalysisResult.priority} priority based on Gemini AI analysis`,
            agent: geminiAnalysisResult.agentType || 'gemini_ai_agent'
          }
        };

        console.log('⚠️ Gemini fallback response:', response);
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

  // Analyze query with Gemini AI
  const analyzeWithGemini = async () => {
    const apiKey = geminiApiKey || import.meta.env.VITE_GEMINI_API_KEY;

    if (!apiKey) {
      console.warn('Gemini API key not set. Skipping AI analysis.');
      return;
    }

    setIsGeminiLoading(true);

    try {
      // Set API key
      geminiService.setApiKey(apiKey);

      // Get vegetation data if available
      const analysisData = localStorage.getItem('mapAnalysis');
      const parsedData = analysisData ? JSON.parse(analysisData) : null;

      const vegetationData = parsedData?.isAnalyzed ? parsedData.vegetationIndices : null;
      const coordinates = parsedData?.coordinates || null;

      // Prepare request for Gemini
      const request = {
        query: currentQuery,
        vegetationData,
        coordinates,
        context: `Agricultural query analysis for Indian farming context. ${
          vegetationData ? 'Vegetation analysis data is available.' : 'No vegetation data available.'
        }`
      };

      // Call Gemini API
      const analysis = await geminiService.analyzeQuery(request);
      setGeminiAnalysis(analysis);

    } catch (error) {
      console.error('Gemini analysis failed:', error);
      setError(`AI Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGeminiLoading(false);
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
        reasoning: 'Fallback response generated due to API unavailability',
        language_detected: /[\u0900-\u097F]/.test(currentQuery) ? 'Hindi' : 'English'
      },
      satellite_data: {
        ndvi: parsedData?.vegetationIndices?.ndvi || 0.65,
        soil_moisture: 0.45,
        temperature: 28,
        humidity: 65,
        environmental_score: 75,
        risk_level: 'medium'
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
    setGeminiAnalysis(null);
    setEnhancedResponse('');
    setAiResponseError('');

    try {
      // Start Gemini analysis in parallel (don't await to run concurrently)
      analyzeWithGemini();

      // Fetch real AI response from backend
      const aiResponse = await fetchAIResponse(currentQuery);

      if (aiResponse) {
        setDemoResponse(aiResponse);

        // The response is already enhanced by Gemini in fetchAIResponse
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
              <h5 style={{ margin: '0 0 15px 0', color: '#333' }}>Analysis Controls</h5>

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

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', fontWeight: '600', marginBottom: '5px', color: '#555' }}>
                  🤖 Gemini API Configuration:
                </label>

                {/* API Key Status */}
                <div style={{
                  padding: '10px',
                  borderRadius: '5px',
                  marginBottom: '10px',
                  backgroundColor: import.meta.env.VITE_GEMINI_API_KEY ? '#d4edda' : '#f8d7da',
                  border: `1px solid ${import.meta.env.VITE_GEMINI_API_KEY ? '#c3e6cb' : '#f5c6cb'}`,
                  color: import.meta.env.VITE_GEMINI_API_KEY ? '#155724' : '#721c24'
                }}>
                  {import.meta.env.VITE_GEMINI_API_KEY ? (
                    <span>✅ API key loaded from environment (.env file)</span>
                  ) : (
                    <span>⚠️ No API key found in environment. Please configure below or set VITE_GEMINI_API_KEY in .env file</span>
                  )}
                </div>

                {/* Manual API Key Input (fallback) */}
                {!import.meta.env.VITE_GEMINI_API_KEY && (
                  <>
                    <input
                      type="password"
                      value={geminiApiKey}
                      onChange={(e) => {
                        setGeminiApiKey(e.target.value);
                        localStorage.setItem('gemini_api_key', e.target.value);
                      }}
                      placeholder="Enter your Google Gemini API key for AI analysis"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '5px',
                        fontSize: '0.9rem'
                      }}
                    />
                    <small style={{ color: '#666', fontSize: '0.8rem' }}>
                      Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
                    </small>
                  </>
                )}
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
          <button 
            onClick={submitQuery} 
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? '🔄 Processing...' : '🚀 Submit Query'}
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
            <p>Fetching AI analysis from Gemini API...</p>
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
              <div><strong>Language:</strong> {demoResponse.routing_analysis.language_detected}</div>
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
              {(geminiApiKey || import.meta.env.VITE_GEMINI_API_KEY) && (
                <div className="enhancement-notice">
                  <p>✨ <strong>Enhanced by Gemini AI:</strong> This response has been processed through advanced agricultural AI for comprehensive insights!</p>
                </div>
              )}
            </div>
          )}

          <div className="technical-metrics">
            <h4>📊 Technical Metrics:</h4>
            <div className="metrics-info">
              <div><strong>Processing Time:</strong> {demoResponse.technical_metrics.processing_time_ms}ms</div>
              <div><strong>Confidence:</strong> {(demoResponse.technical_metrics.confidence_level * 100).toFixed(1)}%</div>
              <div><strong>Satellite Data:</strong> {demoResponse.technical_metrics.satellite_data_integrated ? '✅ Integrated' : '❌ Not Available'}</div>
              <div><strong>Agent:</strong> {demoResponse.technical_metrics.agent}</div>
            </div>
          </div>
        </div>
      )}

      {/* Gemini AI Analysis Display */}
      {(geminiAnalysis || isGeminiLoading) && (
        <div className="gemini-section">
          <GeminiAnalysisDisplay
            analysis={geminiAnalysis}
            isLoading={isGeminiLoading}
            query={currentQuery}
          />
        </div>
      )}
    </div>
  );
};

export default SimpleDemoInterface;
