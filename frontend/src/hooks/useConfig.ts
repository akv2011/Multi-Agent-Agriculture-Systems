import { useState, useEffect, useCallback, useRef } from 'react';
import { configService, RegionConfig } from '../services/configService';

/**
 * Hook for accessing and managing application configuration
 */
export function useConfig() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [regions, setRegions] = useState<string[]>([]);
  const [currentRegion, setCurrentRegion] = useState<string>(configService.currentRegion);
  const [regionConfig, setRegionConfig] = useState<RegionConfig | null>(null);
  
  // Use refs to prevent unnecessary API calls during render cycles
  const initialLoadDone = useRef<boolean>(false);
  const loadingRef = useRef<boolean>(false);

  // Load available regions only once
  useEffect(() => {
    // Skip if already loaded or loading
    if (initialLoadDone.current || loadingRef.current) {
      return;
    }
    
    async function loadRegions() {
      loadingRef.current = true;
      try {
        const availableRegions = await configService.loadAvailableRegions();
        setRegions(availableRegions);
        setError(null);
        initialLoadDone.current = true;
      } catch (err) {
        setError('Failed to load available regions');
        console.error(err);
      } finally {
        loadingRef.current = false;
      }
    }

    loadRegions();
  }, []); // Empty dependency array ensures this runs once

  // Load region configuration when current region changes
  useEffect(() => {
    // Skip if loading is already in progress
    if (loadingRef.current) {
      return;
    }
    
    async function loadRegionConfig() {
      loadingRef.current = true;
      setLoading(true);
      try {
        const config = await configService.getRegionConfig();
        setRegionConfig(config);
        setError(null);
      } catch (err) {
        setError('Failed to load region configuration');
        console.error(err);
      } finally {
        setLoading(false);
        loadingRef.current = false;
      }
    }

    loadRegionConfig();
  }, [currentRegion]); // Only run when currentRegion changes

  // Function to change the current region
  const changeRegion = useCallback(async (regionName: string) => {
    // Skip if region is already current or loading is in progress
    if (regionName === currentRegion || loadingRef.current) {
      return;
    }
    
    loadingRef.current = true;
    setLoading(true);
    try {
      const success = await configService.setRegion(regionName);
      if (success) {
        setCurrentRegion(regionName);
        setError(null);
      } else {
        setError(`Failed to change to region: ${regionName}`);
      }
    } catch (err) {
      setError(`Error changing region: ${err}`);
      console.error(err);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  }, [currentRegion]);

  // Get a value from the region configuration using dot notation
  // This doesn't need to re-create on every render since we're using the service's function
  const getRegionValue = useCallback(
    <T,>(path: string, defaultValue: T): T => {
      return configService.getRegionValue(path, defaultValue);
    },
    [] // No dependencies since it uses the service method directly
  );

  return {
    loading,
    error,
    regions,
    currentRegion,
    regionConfig,
    changeRegion,
    getRegionValue,
  };
}
