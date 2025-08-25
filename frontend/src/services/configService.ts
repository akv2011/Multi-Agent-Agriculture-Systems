import config from '../config';
import { apiClient } from './apiClient';

/**
 * Region configuration type definition
 */
export interface RegionConfig {
  region_name: string;
  agriculture_data: {
    major_crops: string[];
    growing_seasons: {
      [key: string]: {
        start_month: number;
        end_month: number;
      };
    };
    irrigation_systems: string[];
    soil_types: string[];
    avg_rainfall: number;
    avg_temperature: {
      summer: number;
      winter: number;
    };
    agricultural_zones: string[];
  };
  market_centers: string[];
  government_schemes: string[];
}

/**
 * Frontend configuration service that provides access to server configuration and regions
 */
class ConfigService {
  private _currentRegion: string = '';
  private _availableRegions: string[] = [];
  private _regionConfig: RegionConfig | null = null;
  private _configData: any = null;
  private _regionsLoaded: boolean = false;
  private _configLoaded: boolean = false;
  private _regionConfigsCache: Record<string, RegionConfig> = {};
  private _loadingPromises: Record<string, Promise<any>> = {};

  /**
   * Initialize the configuration service
   */
  constructor() {
    // Set default region from config
    this._currentRegion = config.region || 'maharashtra';
    // Don't load in constructor to avoid immediate API calls
  }

  /**
   * Get the current configuration
   */
  public async getConfig(environment?: string): Promise<any> {
    const cacheKey = `config_${environment || 'default'}`;
    
    // Return cached promise if a request is already in progress
    if (this._loadingPromises[cacheKey]) {
      return this._loadingPromises[cacheKey];
    }
    
    // Return cached data if available
    if (this._configData && !environment) {
      return Promise.resolve(this._configData);
    }
    
    // Make the API call and cache the promise
    try {
      const promise = apiClient.get('/config', { params: { environment } })
        .then(response => {
          this._configData = response.data;
          this._configLoaded = true;
          delete this._loadingPromises[cacheKey];
          return response.data;
        })
        .catch(error => {
          console.error('Failed to fetch config:', error);
          delete this._loadingPromises[cacheKey];
          return null;
        });
        
      this._loadingPromises[cacheKey] = promise;
      return promise;
    } catch (error) {
      console.error('Failed to fetch config:', error);
      return null;
    }
  }

  /**
   * Load available regions from server
   */
  public async loadAvailableRegions(): Promise<string[]> {
    // Return cached data if available
    if (this._regionsLoaded && this._availableRegions.length > 0) {
      return Promise.resolve(this._availableRegions);
    }
    
    // Return cached promise if a request is already in progress
    if (this._loadingPromises['regions']) {
      return this._loadingPromises['regions'];
    }
    
    // Make the API call and cache the promise
    try {
      const promise = apiClient.get('/config/regions')
        .then(response => {
          this._availableRegions = response.data;
          this._regionsLoaded = true;
          delete this._loadingPromises['regions'];
          return this._availableRegions;
        })
        .catch(error => {
          console.error('Failed to fetch regions:', error);
          delete this._loadingPromises['regions'];
          return [];
        });
        
      this._loadingPromises['regions'] = promise;
      return promise;
    } catch (error) {
      console.error('Failed to fetch regions:', error);
      return [];
    }
  }

  /**
   * Get list of available regions
   */
  public get availableRegions(): string[] {
    return this._availableRegions;
  }

  /**
   * Get the current region name
   */
  public get currentRegion(): string {
    return this._currentRegion;
  }

  /**
   * Set the current region and load its configuration
   */
  public async setRegion(regionName: string): Promise<boolean> {
    // Don't make API call if region hasn't changed
    if (regionName === this._currentRegion && this._regionConfig) {
      return true;
    }
    
    // Use cached config if available
    if (this._regionConfigsCache[regionName]) {
      this._currentRegion = regionName;
      this._regionConfig = this._regionConfigsCache[regionName];
      return true;
    }
    
    // Return cached promise if a request is already in progress
    const cacheKey = `setRegion_${regionName}`;
    if (this._loadingPromises[cacheKey]) {
      return this._loadingPromises[cacheKey] as Promise<boolean>;
    }
    
    try {
      const promise = apiClient.put(`/config/regions/${regionName}`)
        .then(response => {
          this._currentRegion = regionName;
          this._regionConfig = response.data.config;
          // Cache the config
          if (response.data.config) {
            this._regionConfigsCache[regionName] = response.data.config;
          }
          delete this._loadingPromises[cacheKey];
          return true;
        })
        .catch(error => {
          console.error(`Failed to set region ${regionName}:`, error);
          delete this._loadingPromises[cacheKey];
          return false;
        });
        
      this._loadingPromises[cacheKey] = promise;
      return promise;
    } catch (error) {
      console.error(`Failed to set region ${regionName}:`, error);
      return false;
    }
  }

  /**
   * Get region configuration for a specific region
   */
  public async getRegionConfig(regionName?: string): Promise<RegionConfig | null> {
    const region = regionName || this._currentRegion;
    
    // Return cached config if available
    if (!regionName && this._regionConfig) {
      return Promise.resolve(this._regionConfig);
    }
    
    if (this._regionConfigsCache[region]) {
      if (!regionName) {
        this._regionConfig = this._regionConfigsCache[region];
      }
      return Promise.resolve(this._regionConfigsCache[region]);
    }
    
    // Return cached promise if a request is already in progress
    const cacheKey = `regionConfig_${region}`;
    if (this._loadingPromises[cacheKey]) {
      return this._loadingPromises[cacheKey] as Promise<RegionConfig>;
    }
    
    try {
      const promise = apiClient.get(`/config/regions/${region}`)
        .then(response => {
          // Update cache
          this._regionConfigsCache[region] = response.data;
          
          if (!regionName) {
            // If getting the current region, update current config
            this._regionConfig = response.data;
          }
          
          delete this._loadingPromises[cacheKey];
          return response.data;
        })
        .catch(error => {
          console.error(`Failed to fetch region config for ${region}:`, error);
          delete this._loadingPromises[cacheKey];
          return null;
        });
        
      this._loadingPromises[cacheKey] = promise;
      return promise;
    } catch (error) {
      console.error(`Failed to fetch region config for ${region}:`, error);
      return null;
    }
  }
  
  /**
   * Get cached region configuration
   */
  public get regionConfig(): RegionConfig | null {
    return this._regionConfig;
  }
  
  /**
   * Get data from region configuration using dot notation path
   * @param path Dot notation path (e.g., "agriculture_data.major_crops")
   * @param defaultValue Default value if path not found
   */
  public getRegionValue<T>(path: string, defaultValue: T): T {
    if (!this._regionConfig) return defaultValue;
    
    const parts = path.split('.');
    let current: any = this._regionConfig;
    
    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return defaultValue;
      }
    }
    
    return current as T;
  }
}

// Export singleton instance
export const configService = new ConfigService();
