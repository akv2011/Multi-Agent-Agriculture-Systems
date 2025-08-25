/**
 * API Client for Multi-Agent Agriculture Systems
 * 
 * Centralized client for making API requests to the backend server
 * Uses environment-specific configuration for base URL
 */

import config from '../config';

interface ApiResponse<T = any> {
  [key: string]: any;
}

interface ApiErrorResponse {
  detail?: string;
  message?: string;
  errors?: any[];
  [key: string]: any;
}

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: any;
}

const API_BASE_URL = config.api.baseUrl;

/**
 * Create headers for API requests
 */
const getHeaders = (): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add authorization if available
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  
  return headers;
};

/**
 * Fetch API wrapper with error handling
 */
const fetchWithErrorHandling = async <T>(url: string, options: RequestOptions = {}): Promise<T> => {
  try {
    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...getHeaders(),
        ...options.headers,
      },
      // Convert body to JSON string if it's an object
      body: options.body ? JSON.stringify(options.body) : undefined,
    };
    
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      // Handle HTTP errors
      const errorData = await response.json().catch(() => ({
        detail: `HTTP error! Status: ${response.status}`,
      })) as ApiErrorResponse;
      
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }
    
    return await response.json() as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * API client methods
 */
const apiClient = {
  /**
   * Get the base URL from environment configuration
   */
  getBaseUrl: (): string => API_BASE_URL,
  
  /**
   * Make a GET request to the API
   */
  get: <T = ApiResponse>(endpoint: string): Promise<T> => {
    // Ensure we don't duplicate slashes when joining URLs
    const url = endpoint.startsWith('/')
      ? `${API_BASE_URL}${endpoint}` 
      : `${API_BASE_URL}/${endpoint}`;
    return fetchWithErrorHandling<T>(url);
  },
  
  /**
   * Make a POST request to the API
   */
  post: <T = ApiResponse>(endpoint: string, data?: any): Promise<T> => {
    // Ensure we don't duplicate slashes when joining URLs
    const url = endpoint.startsWith('/')
      ? `${API_BASE_URL}${endpoint}` 
      : `${API_BASE_URL}/${endpoint}`;
    return fetchWithErrorHandling<T>(url, {
      method: 'POST',
      body: data,
    });
  },
  
  /**
   * Make a PUT request to the API
   */
  put: <T = ApiResponse>(endpoint: string, data?: any): Promise<T> => {
    // Ensure we don't duplicate slashes when joining URLs
    const url = endpoint.startsWith('/')
      ? `${API_BASE_URL}${endpoint}` 
      : `${API_BASE_URL}/${endpoint}`;
    return fetchWithErrorHandling<T>(url, {
      method: 'PUT',
      body: data,
    });
  },
  
  /**
   * Make a DELETE request to the API
   */
  delete: <T = ApiResponse>(endpoint: string): Promise<T> => {
    // Ensure we don't duplicate slashes when joining URLs
    const url = endpoint.startsWith('/')
      ? `${API_BASE_URL}${endpoint}` 
      : `${API_BASE_URL}/${endpoint}`;
    return fetchWithErrorHandling<T>(url, {
      method: 'DELETE',
    });
  },
};

export default apiClient;
