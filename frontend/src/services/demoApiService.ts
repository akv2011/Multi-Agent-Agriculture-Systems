/**
 * API Service for Multi-Agent Agriculture Systems Demo
 */

import apiClient from './apiClient.ts';

export interface DemoQueryRequest {
  query_text: string;
  language?: string;
  location?: string;
}

export interface DemoQueryResponse {
  status: string;
  query_id: string;
  original_query: string;
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
  timestamp: string;
}

export interface DemoCapabilities {
  system_status: string;
  completion_percentage: number;
  operational_agents: string[];
  capabilities: string[];
  satellite_features: string[];
  supported_languages: string[];
}

export interface DemoSession {
  session_id: string;
  start_time: string;
  total_queries: number;
  sample_queries: Array<{
    query: string;
    type: string;
    agent: string;
  }>;
}

class DemoApiService {
  async fetchCapabilities(): Promise<DemoCapabilities> {
    return apiClient.get<DemoCapabilities>('/demo/capabilities');
  }

  async fetchSession(): Promise<DemoSession> {
    return apiClient.get<DemoSession>('/demo/session');
  }

  async submitQuery(request: DemoQueryRequest): Promise<DemoQueryResponse> {
    return apiClient.post<DemoQueryResponse>('/demo/query', request);
  }

  async getSampleQueries() {
    return apiClient.get('/demo/sample-queries');
  }

  async getAvailableLocations() {
    return apiClient.get('/demo/satellite-data');
  }

  async healthCheck() {
    return apiClient.get('/demo/health');
  }
}

export const demoApiService = new DemoApiService();
export default demoApiService;
