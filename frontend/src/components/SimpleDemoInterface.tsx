import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './SimpleDemoInterface.css';
import DashboardUpdateService from '../services/dashboardUpdateService';

// Fix for default markers in React
// eslint-disable-next-line @typescript-eslint/no-explicit-any
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

// --- Added types for query classification & agent execution ---
type AgentId = 'disease_identification' | 'crop_recommendation' | 'irrigation_scheduling' | 'market_analysis';
interface QueryClassification {
  agentId: AgentId | 'general';
  confidence: number; // 0-1
  reasons: string[];
  usedImage: boolean;
}
interface AgentExecutionResult {
  agentId: AgentId | 'general';
  success: boolean;
  data?: JsonObject | JsonObject[] | string;
  fallbackUsed?: boolean;
  fallbackSource?: 'grounding_search' | 'local_mock';
  errorMessage?: string;
}
// ------------------------------------------------------------

export type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
export interface JsonObject { [k: string]: JsonValue }

const SimpleDemoInterface: React.FC = () => {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [demoResponse, setDemoResponse] = useState<DemoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);

  // Get dashboard service instance
  const dashboardService = DashboardUpdateService.getInstance();

  // Clear vegetation indices from agents on component mount
  React.useEffect(() => {
    localStorage.removeItem('vegetationAnalysis');
    
    // Start simulating real-time updates for demo
    const interval = setInterval(() => {
      dashboardService.simulateRealtimeUpdate();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [dashboardService]);

  // Map-related state
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<L.Map | null>(null);
  // (States are used throughout; suppress false positive for exhaustive-deps where intentional)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [currentMarker, setCurrentMarker] = useState<L.Marker | null>(null); // kept for potential future use
  const [selectedPoint, setSelectedPoint] = useState<L.LatLng | null>(null);
  const [selectedCoords, setSelectedCoords] = useState<string>('Click on map to select analysis point');
  const [selectedAddress, setSelectedAddress] = useState<string>('');
  const [analysisDate, setAnalysisDate] = useState<string>('');
  const [satelliteSource, setSatelliteSource] = useState<string>('sentinel2');
  const [cloudCoverage, setCloudCoverage] = useState<string>('20');
  const [analysisProgress, setAnalysisProgress] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // --- Added state for query classification & agent result ---
  const [classification, setClassification] = useState<QueryClassification | null>(null);
  const [agentResult, setAgentResult] = useState<AgentExecutionResult | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  // -------------------------------------------------------

  // Initialize map - moved after selectAnalysisPoint definition  
  useEffect(() => {
    if (mapRef.current && !map) {
      const mapInstance = L.map(mapRef.current).setView([10.7905, 78.7047], 11);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(mapInstance);
      mapInstance.on('click', (e: L.LeafletMouseEvent) => { selectAnalysisPoint(e.latlng, mapInstance); });
      setMap(mapInstance);
      setDefaultDate();
    }
    // selectAnalysisPoint is defined below, using it is safe after first render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map]);

  const setDefaultDate = () => {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
    setAnalysisDate(thirtyDaysAgo.toISOString().split('T')[0]);
  };

  const selectAnalysisPoint = React.useCallback(async (latlng: L.LatLng, mapInstance?: L.Map) => {
    const activeMap = mapInstance || map;
    if (!activeMap) return;

    setSelectedPoint(latlng);

    // Remove ALL existing markers from the map to ensure only one marker exists
    activeMap.eachLayer((layer: L.Layer) => {
      if (layer instanceof L.Marker) {
        activeMap.removeLayer(layer);
      }
    });

    // Show loading state while fetching address
    setSelectedCoords('Getting address...');
    setSelectedAddress('');

    // Get address from coordinates
    const address = await getAddressFromCoordinates(latlng.lat, latlng.lng);
    setSelectedAddress(address);

    // Add new marker
    const newMarker = L.marker(latlng).addTo(activeMap);
    newMarker.bindPopup(`
      <b>Analysis Point</b><br>
      <div style="max-width: 200px; word-wrap: break-word;">
        <strong>Address:</strong><br>
        ${address}<br><br>
        <small>Coordinates: ${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}</small>
      </div>
      <br>
      <button onclick="window.analyzeCurrentPoint()" style="background: #27ae60; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-top: 5px;">Analyze This Point</button>
    `).openPopup();

    setCurrentMarker(newMarker);

    // Update display to show address instead of just coordinates
    setSelectedCoords(`Selected: ${address}`);
  }, [map]);

  const analyzeSelectedPoint = React.useCallback(async (point?: L.LatLng) => {
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

      // Set a query based on the analysis - use address if available, otherwise coordinates
      const locationDesc = selectedAddress || `coordinates ${targetPoint.lat.toFixed(5)}, ${targetPoint.lng.toFixed(5)}`;
      setCurrentQuery(`Analyze agricultural conditions at ${locationDesc}`);

    } catch (error) {
      console.error('Analysis error:', error);
      setError('Analysis failed. Please try again.');
      setAnalysisProgress('');
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedPoint, analysisDate, satelliteSource, selectedAddress]);

  // Make analyzeCurrentPoint available globally for popup button
  useEffect(() => {
    (window as unknown as { analyzeCurrentPoint?: () => void }).analyzeCurrentPoint = () => analyzeSelectedPoint();
  }, [analyzeSelectedPoint]);

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

  // Image upload handler
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => setUploadedImage(ev.target?.result as string);
    reader.readAsDataURL(file);
  };

  // Simple rule-based classifier (client-side)
  const classifyQuery = (text: string, hasImage: boolean): QueryClassification => {
    const lower = text.toLowerCase();
    const reasons: string[] = [];
    let agentId: QueryClassification['agentId'] = 'general';
    let score = 0.35; // base

    const boost = (s: number, r: string) => { score = Math.min(1, score + s); reasons.push(r); };

    if (/(disease|blight|rust|spot|infection|leaf|pest)/.test(lower)) {
      agentId = 'disease_identification';
      boost(0.3, 'Disease related keyword detected');
    }
    if (/(recommend|which crop|best crop|grow|variety|fertiliz|soil|nutrient)/.test(lower)) {
      if (agentId === 'general') agentId = 'crop_recommendation';
      boost(0.25, 'Crop recommendation keyword detected');
    }
    if (/(irrigat|water|moisture|schedule)/.test(lower)) {
      agentId = 'irrigation_scheduling';
      boost(0.25, 'Irrigation / water management keywords');
    }
    if (/(price|market|sell|demand|forecast|rate)/.test(lower)) {
      agentId = 'market_analysis';
      boost(0.3, 'Market analytics keywords');
    }
    if (hasImage && agentId === 'general') {
      agentId = 'disease_identification';
      boost(0.2, 'Image provided – prioritizing disease detection');
    }
    if (hasImage && agentId === 'disease_identification') boost(0.1, 'Image supports disease classification');

    return { agentId, confidence: Math.min(1, score), reasons, usedImage: hasImage };
  };

  // Enhanced agent execution with new API
  const runAgentForQuery = async (cls: QueryClassification, query: string): Promise<AgentExecutionResult> => {
    const payload = {
      query_text: query,
      image_base64: uploadedImage,
      location: selectedPoint ? {
        lat: selectedPoint.lat,
        lng: selectedPoint.lng,
        address: selectedAddress
      } : null,
      vegetation_analysis: (() => { 
        try { 
          return JSON.parse(localStorage.getItem('mapAnalysis') || 'null'); 
        } catch { 
          return null; 
        } 
      })()
    };

    try {
      const resp = await fetch('/api/query/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!resp.ok) {
        throw new Error(`API returned ${resp.status}: ${resp.statusText}`);
      }
      
      const data = await resp.json();
      
      return { 
        agentId: data.classification.agent_id,
        success: data.status === 'success' || data.status === 'partial_success',
        // Prefer the inner agent domain result (data.agent_result.result) if present
        data: (data.agent_result && data.agent_result.result) ? data.agent_result.result : data.agent_result,
        fallbackUsed: data.fallback_used,
        fallbackSource: data.fallback_source,
        errorMessage: data.agent_result?.error
      };
      
    } catch (err) {
      console.error('Query processing failed:', err);
      
      // Ultimate fallback - local mock response
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      
      const mock = { 
        type: cls.agentId === 'general' ? 'general_advisory' : cls.agentId,
        source: 'local_mock', 
        note: 'API unavailable; providing heuristic suggestion.', 
        query, 
        tips: generateLocalFallbackTips(cls.agentId) 
      };
      
      return { 
        agentId: cls.agentId, 
        success: true, 
        data: mock, 
        fallbackUsed: true, 
        fallbackSource: 'local_mock',
        errorMessage: `API Error: ${errorMessage}`
      };
    }
  };

  const generateLocalFallbackTips = (agent: AgentId | 'general'): string[] => {
    switch (agent) {
      case 'disease_identification':
        return ['Capture clear close-up images of affected leaves', 'Check for uniform vs. patchy symptoms', 'Consider recent weather favoring fungal growth'];
      case 'crop_recommendation':
        return ['Test soil pH and macro nutrients', 'Rotate crops to prevent nutrient depletion', 'Match crop to rainfall pattern'];
      case 'irrigation_scheduling':
        return ['Measure current soil moisture at root depth', 'Irrigate early morning to reduce evaporation', 'Adjust schedule after significant rainfall'];
      case 'market_analysis':
        return ['Track daily mandi prices', 'Store produce properly to wait for favorable pricing', 'Diversify crops to hedge price volatility'];
      default:
        return ['Provide more context for better recommendations'];
    }
  };

  // --- Modified submitQuery to classify & run agent ---
  const submitQuery = async () => {
    if (!currentQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    const startTime = Date.now();
    setIsLoading(true);
    setAnalysisComplete(false);
    setError('');
    setDemoResponse(null);
    setClassification(null);
    setAgentResult(null);

    try {
      const cls = classifyQuery(currentQuery, !!uploadedImage);
      setClassification(cls);

      // Start workflow tracking
      const workflowId = `query_${Date.now()}`;
      dashboardService.startWorkflow(workflowId);
      
      // Update agent status to busy
      dashboardService.updateAgentStatus(cls.agentId, 'busy');

      // Simulate prior satellite analysis portion (retain existing behavior)
      await new Promise(r => setTimeout(r, 400));

      const agentExec = await runAgentForQuery(cls, currentQuery);
      setAgentResult(agentExec);

      const processingTime = Date.now() - startTime;
      
      // Update dashboard metrics
      dashboardService.updateQueryMetrics(
        cls.agentId,
        processingTime,
        agentExec.success,
        agentExec.fallbackSource || undefined
      );
      
      // Update agent status back to idle (or error if failed)
      dashboardService.updateAgentStatus(
        cls.agentId, 
        agentExec.success ? 'idle' : 'error'
      );
      
      // Complete workflow
      dashboardService.completeWorkflow(workflowId);

      // Build a DemoResponse wrapper (re-using existing UI sections) – lightweight mapping
      const responseText = agentExec.success
        ? renderReadableAgentResult(agentExec)
        : 'Agent execution failed.';

      const response: DemoResponse = {
        routing_analysis: {
          agent: cls.agentId === 'general' ? 'General Advisory' : cls.agentId,
          confidence: cls.confidence,
          reasoning: cls.reasons.join('; '),
          language_detected: 'auto'
        },
        satellite_data: {
          ndvi: 0.5,
            soil_moisture: 0.4,
            temperature: 30,
            humidity: 70,
            environmental_score: 70,
            risk_level: 'medium'
        },
        response_text: responseText,
        technical_metrics: {
          processing_time_ms: processingTime,
          confidence_level: cls.confidence,
          satellite_data_integrated: !!localStorage.getItem('mapAnalysis'),
          risk_assessment: 'Heuristic',
          agent: cls.agentId
        }
      };
      setDemoResponse(response);
      
    } catch (err) {
      const processingTime = Date.now() - startTime;
      
      setError('Query processing failed. Please try again.');
      console.error('Query error:', err);
      
      // Update metrics for failed query
      dashboardService.updateQueryMetrics('unknown', processingTime, false);
      
    } finally {
      setIsLoading(false);
    }
  };
  // -------------------------------------------------------

  const selectSampleQuery = (query: { query: string }) => {
    setCurrentQuery(query.query);
  };

  // Reverse geocoding function to get address from coordinates
  const getAddressFromCoordinates = async (lat: number, lng: number): Promise<string> => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`
      );
      
      if (!response.ok) {
        throw new Error('Geocoding service unavailable');
      }
      
      const data = await response.json();
      
      if (data && data.display_name) {
        // Parse address components for better formatting
        const address = data.address || {};
        const addressParts = [];
        
        // Add specific address components in order of preference
        if (address.house_number && address.road) {
          addressParts.push(`${address.house_number} ${address.road}`);
        } else if (address.road) {
          addressParts.push(address.road);
        }
        
        if (address.neighbourhood || address.suburb) {
          addressParts.push(address.neighbourhood || address.suburb);
        }
        
        if (address.village || address.town || address.city) {
          addressParts.push(address.village || address.town || address.city);
        }
        
        if (address.state_district && address.state_district !== (address.village || address.town || address.city)) {
          addressParts.push(address.state_district);
        }
        
        if (address.state) {
          addressParts.push(address.state);
        }
        
        if (address.country) {
          addressParts.push(address.country);
        }
        
        // If we have structured address parts, use them; otherwise use display_name
        return addressParts.length > 0 ? addressParts.join(', ') : data.display_name;
      } else {
        throw new Error('No address found');
      }
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      // Fallback to coordinates if geocoding fails
      return `${lat.toFixed(5)}°N, ${lng.toFixed(5)}°E`;
    }
  };

  // Helper to convert structured agent result into user-friendly markdown-like text
  const renderReadableAgentResult = (exec: AgentExecutionResult): string => {
    if (!exec || !exec.data) return 'No data returned.';
    // Support both direct domain object or wrapped structure
    // Define lightweight interfaces to avoid any
    interface IrrigationItem { day: string; time: string; duration: string; amount: string }
    interface DiseaseItem { name: string; probability: number; treatment: string }
    interface CropItem { name: string; suitability: number; season: string; yield_potential: string }
    interface PriceItem { crop: string; current_price: string; trend: string; change: string }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let d: any = exec.data;
    if (d && d.result && d.result.type) d = d.result; // unwrap if still wrapped

    const fallbackPrefix = exec.fallbackUsed ? `⚠️ Fallback (${exec.fallbackSource}) used.\n\n` : '';

    try {
      switch (d.type) {
        case 'irrigation_scheduling':
          return fallbackPrefix + [
            '💧 Irrigation Schedule Recommendation',
            '',
            ...((d.schedule || []) as IrrigationItem[]).map((s: IrrigationItem) => `• ${s.day}: ${s.time} – ${s.duration} (${s.amount})`),
            '',
            d.water_requirement ? `Weekly Requirement: ${d.water_requirement}` : null,
            d.efficiency_tips ? 'Efficiency Tips:\n' + d.efficiency_tips.map((t: string) => `  - ${t}`).join('\n') : null,
            d.location_considered ? 'Location factors considered ✅' : 'Location not provided'
          ].filter(Boolean).join('\n');
        case 'disease_identification':
          return fallbackPrefix + [
            '🦠 Disease Identification Summary',
            '',
            ...(d.detected_diseases || []).map((dis: DiseaseItem) => `• ${dis.name} (prob ${(dis.probability*100).toFixed(1)}%) – Treatment: ${dis.treatment}`),
            '',
            d.recommendations ? 'General Recommendations:\n' + d.recommendations.map((r: string) => `  - ${r}`).join('\n') : null,
            d.image_analyzed ? 'Image analyzed ✅' : 'No image provided'
          ].filter(Boolean).join('\n');
        case 'crop_recommendation':
          return fallbackPrefix + [
            '🌱 Crop Recommendation',
            '',
            ...(d.recommended_crops || []).map((c: CropItem) => `• ${c.name}: suitability ${(c.suitability*100).toFixed(0)}%, season ${c.season}, yield ${c.yield_potential}`),
            '',
            d.soil_factors ? `Soil Factors: pH ${d.soil_factors.ph_level}, Rainfall ${d.soil_factors.rainfall}, Temp ${d.soil_factors.temperature}` : null,
            d.location_considered ? 'Location data considered ✅' : null,
            d.satellite_data_used ? 'Satellite vegetation indices used ✅' : null
          ].filter(Boolean).join('\n');
        case 'market_analysis':
          return fallbackPrefix + [
            '📈 Market Analysis',
            '',
            ...(d.current_prices || []).map((p: PriceItem) => `• ${p.crop}: ${p.current_price} (${p.trend}, ${p.change})`),
            '',
            d.market_outlook ? `Outlook: ${d.market_outlook}` : null,
            d.selling_recommendations ? 'Recommendations:\n' + d.selling_recommendations.map((r: string) => `  - ${r}`).join('\n') : null
          ].filter(Boolean).join('\n');
        case 'general_advisory':
          return fallbackPrefix + [
            '🌾 General Advisory',
            '',
            d.response || '',
            d.tips ? 'Tips:\n' + d.tips.map((t: string) => `  - ${t}`).join('\n') : null
          ].filter(Boolean).join('\n');
        default: {
          // Provide graceful text fallback instead of raw JSON
          const keys = Object.keys(d || {});
          if (keys.length && !d.type) {
            return fallbackPrefix + [
              '📌 Result Summary',
              '',
              ...keys.slice(0, 8).map(k => `• ${k}: ${typeof d[k] === 'object' ? JSON.stringify(d[k]) : String(d[k])}`)
            ].join('\n');
          }
          try { return fallbackPrefix + JSON.stringify(d, null, 2); } catch { return 'Unformatted response.'; }
        }
      }
    } catch {
      try { return fallbackPrefix + JSON.stringify(d, null, 2); } catch { return 'Unable to render result.'; }
    }
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
                fontFamily: 'Arial, sans-serif',
                fontSize: '0.9rem'
              }}>
                <strong>📍 Location:</strong><br />
                {selectedCoords}
              </div>
              <div style={{
                background: '#f9f9f9',
                padding: '12px',
                borderRadius: '5px',
                margin: '10px 0',
                fontFamily: 'Arial, sans-serif',
                fontSize: '0.9rem',
                border: '1px solid #ddd'
              }}>
                <strong>📍 Address:</strong><br />
                {selectedAddress || 'Click on map to see address at selected location'}
              </div>
            </div>

            {/* Analysis Controls */}
            <div className="analysis-controls" style={{
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
                  className="analysis-date-input"
                  value={analysisDate}
                  onChange={(e) => setAnalysisDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontSize: '0.9rem',
                    color: '#333333',
                    backgroundColor: '#ffffff'
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
                    fontSize: '0.9rem',
                    color: '#333333',
                    backgroundColor: '#ffffff'
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
                    fontSize: '0.9rem',
                    color: '#333333',
                    backgroundColor: '#ffffff'
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
            style={{
              color: '#2c3e50',
              backgroundColor: '#ffffff',
              border: '2px solid #cbd5e0',
              borderRadius: '12px',
              padding: '15px',
              fontSize: '1rem',
              width: '100%',
              minHeight: '100px',
              fontWeight: '500',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
              transition: 'all 0.3s ease'
            }}
          />
          {/* Added image upload */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '8px', flexWrap: 'wrap' }}>
            <label style={{
              background: '#f1f5f9',
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #cbd5e1',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}>
              📷 Add Image
              <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleImageUpload} />
            </label>
            {uploadedImage && (
              <div style={{ position: 'relative' }}>
                <img src={uploadedImage} alt="query upload" style={{ width: 80, height: 60, objectFit: 'cover', borderRadius: 6, border: '1px solid #e2e8f0' }} />
                <button onClick={() => setUploadedImage(null)} style={{ position: 'absolute', top: -6, right: -6, background: '#ef4444', color: '#fff', border: 'none', borderRadius: '50%', width: 20, height: 20, cursor: 'pointer', fontSize: 12 }}>×</button>
              </div>
            )}
            {classification && (
              <div style={{ fontSize: '0.7rem', background: '#e0f2fe', padding: '4px 8px', borderRadius: 6, border: '1px solid #bae6fd', fontWeight: 600 }}>
                Routed → {classification.agentId} ({Math.round(classification.confidence * 100)}%)
              </div>
            )}
          </div>
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
          {/* Added agent execution summary */}
          {agentResult && (
            <div style={{ background: '#f1f5f9', padding: '10px 14px', borderRadius: 8, marginBottom: 16, border: '1px solid #e2e8f0', fontSize: '0.8rem' }}>
              <strong>Execution:</strong> {agentResult.agentId} – {agentResult.success ? 'Success' : 'Failed'} {agentResult.fallbackUsed ? `(Fallback: ${agentResult.fallbackSource})` : ''}
              {agentResult.errorMessage && <div style={{ color: '#dc2626' }}>{agentResult.errorMessage}</div>}
            </div>
          )}

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
