import React, { useMemo, useCallback } from 'react';
import { useConfig } from '../../hooks/useConfig';

/**
 * Component for selecting and displaying region information
 */
export const RegionSelector: React.FC = () => {
  const { 
    loading, 
    error, 
    regions, 
    currentRegion, 
    regionConfig, 
    changeRegion,
    getRegionValue
  } = useConfig();

  // Handle region change - memoize to prevent re-renders
  const handleRegionChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    const newRegion = event.target.value;
    if (newRegion !== currentRegion) {
      changeRegion(newRegion);
    }
  }, [currentRegion, changeRegion]);
  
  // Memoize values to prevent recalculation on every render
  const majorCrops = useMemo(() => 
    getRegionValue<string[]>('agriculture_data.major_crops', []), 
    [getRegionValue, regionConfig]
  );
  
  const markets = useMemo(() => 
    getRegionValue<string[]>('market_centers', []), 
    [getRegionValue, regionConfig]
  );
  
  const avgRainfall = useMemo(() => 
    getRegionValue('agriculture_data.avg_rainfall', 0), 
    [getRegionValue, regionConfig]
  );
  
  const summerTemp = useMemo(() => 
    getRegionValue('agriculture_data.avg_temperature.summer', 0), 
    [getRegionValue, regionConfig]
  );
  
  const winterTemp = useMemo(() => 
    getRegionValue('agriculture_data.avg_temperature.winter', 0), 
    [getRegionValue, regionConfig]
  );

  if (loading && !regionConfig) {
    return <div className="text-center p-4">Loading region information...</div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">Error: {error}</div>;
  }

  return (
    <div className="border rounded-md p-4 mb-4">
      <div className="mb-4">
        <label htmlFor="region-select" className="block text-sm font-medium mb-1">
          Select Region:
        </label>
        <select
          id="region-select"
          value={currentRegion}
          onChange={handleRegionChange}
          className="w-full p-2 border rounded"
          disabled={loading}
        >
          {regions.map((region) => (
            <option key={region} value={region}>
              {region.charAt(0).toUpperCase() + region.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {regionConfig && (
        <div className="mt-4">
          <h3 className="font-medium text-lg mb-2">
            {regionConfig.region_name} Agriculture Information
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium">Major Crops:</h4>
              <ul className="list-disc list-inside">
                {majorCrops.map((crop) => (
                  <li key={crop}>{crop}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium">Market Centers:</h4>
              <ul className="list-disc list-inside">
                {markets.map((market) => (
                  <li key={market}>{market}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-4">
            <h4 className="font-medium">Climate Information:</h4>
            <p>
              Average Rainfall: {avgRainfall} mm
            </p>
            <p>
              Summer Temperature: {summerTemp}°C
            </p>
            <p>
              Winter Temperature: {winterTemp}°C
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
