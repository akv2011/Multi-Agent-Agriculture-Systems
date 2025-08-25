import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './SimpleDemoInterface.css';

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

  // Map-related state
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<L.Map | null>(null);
  const [currentMarker, setCurrentMarker] = useState<L.Marker | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<L.LatLng | null>(null);
  const [selectedCoords, setSelectedCoords] = useState<string>('Click on map to select analysis point');
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

  const selectAnalysisPoint = (latlng: L.LatLng, mapInstance?: L.Map) => {
    const activeMap = mapInstance || map;
    if (!activeMap) return;

    setSelectedPoint(latlng);

    // Remove ALL existing markers from the map to ensure only one marker exists
    activeMap.eachLayer((layer: any) => {
      if (layer instanceof L.Marker) {
        activeMap.removeLayer(layer);
      }
    });

    // Add new marker
    const newMarker = L.marker(latlng).addTo(activeMap);
    newMarker.bindPopup(`
      <b>Analysis Point</b><br>
      Lat: ${latlng.lat.toFixed(5)}<br>
      Lng: ${latlng.lng.toFixed(5)}<br>
      <button onclick="window.analyzeCurrentPoint()" style="background: #27ae60; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Analyze This Point</button>
    `).openPopup();

    setCurrentMarker(newMarker);

    // Update coordinates display
    setSelectedCoords(`Selected: ${latlng.lat.toFixed(5)}°N, ${latlng.lng.toFixed(5)}°E`);
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

      // Store results in localStorage
      const analysisResults = {
        coordinates: {
          lat: targetPoint.lat,
          lng: targetPoint.lng
        },
        vegetationIndices,
        analysisDate,
        satelliteSource,
        isAnalyzed: true,
        timestamp: Date.now()
      };

      localStorage.setItem('vegetationAnalysis', JSON.stringify(analysisResults));
      setAnalysisComplete(true);

      setAnalysisProgress('Analysis complete!');
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisProgress('');

      // Set a query based on the analysis
      setCurrentQuery(`Analyze agricultural conditions at coordinates ${targetPoint.lat.toFixed(5)}, ${targetPoint.lng.toFixed(5)}`);

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

  const submitQuery = async () => {
    if (!currentQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    setIsLoading(true);
    setError('');
    setDemoResponse(null);

    try {
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Simple response based on whether vegetation analysis has been done
      let responseText = '';
      const analysisData = localStorage.getItem('vegetationAnalysis');
      const parsedData = analysisData ? JSON.parse(analysisData) : null;

      if (parsedData && parsedData.isAnalyzed) {
        const { vegetationIndices, coordinates } = parsedData;
        responseText = `**Agricultural Analysis Complete**

Based on satellite analysis at coordinates ${coordinates?.lat.toFixed(5)}°N, ${coordinates?.lng.toFixed(5)}°E:

**Crop Health Status:**
• NDVI: ${vegetationIndices.ndvi?.toFixed(3)} - ${vegetationIndices.ndvi! >= 0.6 ? 'Excellent' : vegetationIndices.ndvi! >= 0.4 ? 'Good' : 'Moderate'}
• EVI: ${vegetationIndices.evi?.toFixed(3)} - Enhanced vegetation index
• SAVI: ${vegetationIndices.savi?.toFixed(3)} - Soil-adjusted index

**Moisture Status:**
• NDMI: ${vegetationIndices.ndmi?.toFixed(3)} - ${vegetationIndices.ndmi! >= 0.2 ? 'Good moisture' : 'Moderate moisture'}

**View detailed metrics in Agents → Crop Selection Agent → Metrics and Irrigation Controller → Metrics**`;
      } else {
        responseText = `**Query: "${currentQuery}"**

To get detailed analysis with vegetation indices:
1. Click on the map to select coordinates
2. Click "Analyze Point" to process satellite data
3. Then submit your query for detailed results

The analysis will provide NDVI, EVI, SAVI, and NDMI values that will appear in the Agents metrics.`;
      }

      const response = {
        response: responseText,
        agents_involved: (parsedData && parsedData.isAnalyzed) ? ['Crop Selection Agent', 'Irrigation Controller'] : ['Query Processing Agent'],
        confidence: 0.9,
        processing_time: 1.0
      };

      setDemoResponse(response);
    } catch (err) {
      setError('Query processing failed. Please try again.');
      console.error('Query error:', err);
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
                padding: '8px',
                borderRadius: '5px',
                margin: '10px 0',
                fontFamily: 'monospace',
                fontSize: '0.9rem'
              }}>
                {selectedCoords}
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
                  ✅ Analysis Complete! Check Agents → Metrics for vegetation indices
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

          <div className="ai-response">
            <h4>🌾 Satellite-Enhanced Response:</h4>
            <div 
              className="response-text"
              dangerouslySetInnerHTML={{ 
                __html: formatResponseText(demoResponse.response_text) 
              }}
            />
          </div>

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
    </div>
  );
};

export default SimpleDemoInterface;
