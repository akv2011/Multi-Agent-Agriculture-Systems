import React, { useState, useEffect, useRef } from 'react';
import './StatisticsPage.css';

// Define types for statistics data
interface StatisticCard {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: string;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
}

interface ComparisonData {
  title: string;
  current: number;
  previous: number;
  unit: string;
  change: number;
}

const StatisticsPage: React.FC = () => {
  // Dynamic state for statistics
  const [totalYield, setTotalYield] = useState(1254);
  const [waterUsage, setWaterUsage] = useState(34280);
  const [fieldEfficiency, setFieldEfficiency] = useState(87);
  const [operatingCosts, setOperatingCosts] = useState(42150);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDetailedView, setShowDetailedView] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [isUpdating, setIsUpdating] = useState(false);

  // Previous values for change calculation
  const prevValues = useRef({
    totalYield: 1254,
    waterUsage: 34280,
    fieldEfficiency: 87,
    operatingCosts: 42150
  });

  // Mock data service for realistic agricultural data
  const mockDataService = {
    // Base values for different time periods
    getBaseValues: (period: string) => {
      const periodMultipliers = {
        'Last 7 Days': { yield: 0.15, water: 0.2, cost: 0.15 },
        'Last 30 Days': { yield: 1.0, water: 1.0, cost: 1.0 },
        'This Month': { yield: 1.1, water: 1.05, cost: 1.08 },
        'Last Quarter': { yield: 3.2, water: 2.8, cost: 3.1 },
        'Year to Date': { yield: 8.5, water: 7.2, cost: 8.0 },
        'Custom': { yield: 2.5, water: 2.2, cost: 2.4 }
      };

      const multiplier = periodMultipliers[period as keyof typeof periodMultipliers] || periodMultipliers['Last 30 Days'];

      return {
        totalYield: Math.round(1254 * multiplier.yield),
        waterUsage: Math.round(34280 * multiplier.water),
        fieldEfficiency: Math.max(60, Math.min(95, 87 + (Math.random() - 0.5) * 10)),
        operatingCosts: Math.round(42150 * multiplier.cost)
      };
    },

    // Generate realistic incremental changes
    generateRealisticUpdate: (current: number, type: 'yield' | 'water' | 'efficiency' | 'cost') => {
      const changeRanges = {
        yield: { min: -2, max: 8 }, // Mostly positive growth
        water: { min: -50, max: 50 }, // Natural fluctuation
        efficiency: { min: -0.3, max: 0.5 }, // Small efficiency changes
        cost: { min: -20, max: 80 } // Mostly increasing costs
      };

      const range = changeRanges[type];
      const change = Math.random() * (range.max - range.min) + range.min;

      // Apply bounds based on type
      switch (type) {
        case 'yield':
          return Math.max(100, Math.min(15000, current + change));
        case 'water':
          return Math.max(5000, Math.min(200000, current + change));
        case 'efficiency':
          return Math.max(60, Math.min(95, current + change));
        case 'cost':
          return Math.max(10000, Math.min(500000, current + change));
        default:
          return current;
      }
    },

    // Calculate growth percentage
    calculateGrowthPercentage: (current: number, previous: number) => {
      if (previous === 0) return 0;
      return Math.round(((current - previous) / previous) * 1000) / 10; // Round to 1 decimal
    }
  };

  // Dynamic chart data state with mock data generators
  const [monthlyYieldData, setMonthlyYieldData] = useState<ChartData>(() => {
    const generateChartData = (period: string) => {
      const baseValues = {
        'Last 7 Days': { corn: 45, wheat: 28, soybeans: 18 },
        'Last 30 Days': { corn: 85, wheat: 55, soybeans: 35 },
        'This Month': { corn: 92, wheat: 62, soybeans: 42 },
        'Last Quarter': { corn: 125, wheat: 85, soybeans: 65 },
        'Year to Date': { corn: 180, wheat: 120, soybeans: 95 },
        'Custom': { corn: 110, wheat: 75, soybeans: 55 }
      };

      const values = baseValues[period as keyof typeof baseValues] || baseValues['Last 30 Days'];
      const labels = period === 'Last 7 Days' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] :
                    period === 'Last Quarter' ? ['Month 1', 'Month 2', 'Month 3'] :
                    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];

      return {
        labels,
        datasets: [
          {
            label: 'Corn',
            data: labels.map(() => values.corn + (Math.random() - 0.5) * 20),
            color: '#F59E0B'
          },
          {
            label: 'Wheat',
            data: labels.map(() => values.wheat + (Math.random() - 0.5) * 15),
            color: '#DFBA47'
          },
          {
            label: 'Soybeans',
            data: labels.map(() => values.soybeans + (Math.random() - 0.5) * 12),
            color: '#22C55E'
          }
        ]
      };
    };

    return generateChartData('Last 30 Days');
  });

  const [resourceUtilization, setResourceUtilization] = useState(() => {
    const generateResourceData = () => [
      { category: 'Water', value: 75 + (Math.random() - 0.5) * 10, color: '#3B82F6', target: 80, trend: 'stable' },
      { category: 'Fertilizer', value: 65 + (Math.random() - 0.5) * 8, color: '#22C55E', target: 70, trend: 'increasing' },
      { category: 'Electricity', value: 50 + (Math.random() - 0.5) * 12, color: '#F59E0B', target: 45, trend: 'decreasing' },
      { category: 'Fuel', value: 40 + (Math.random() - 0.5) * 8, color: '#EF4444', target: 35, trend: 'decreasing' },
      { category: 'Labor', value: 80 + (Math.random() - 0.5) * 6, color: '#8B5CF6', target: 85, trend: 'increasing' }
    ].map(item => ({ ...item, value: Math.max(20, Math.min(100, Math.round(item.value))) }));

    return generateResourceData();
  });

  const [fieldComparisons, setFieldComparisons] = useState<ComparisonData[]>([
    {
      title: 'North Field',
      current: 92,
      previous: 85,
      unit: 'bu/acre',
      change: 8.2
    },
    {
      title: 'South Field',
      current: 78,
      previous: 75,
      unit: 'bu/acre',
      change: 4.0
    },
    {
      title: 'East Field',
      current: 85,
      previous: 90,
      unit: 'bu/acre',
      change: -5.6
    },
    {
      title: 'West Field',
      current: 105,
      previous: 95,
      unit: 'bu/acre',
      change: 10.5
    }
  ]);

  // Seasonal trends data
  const [seasonalTrends, setSeasonalTrends] = useState({
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'This Year',
        data: [45, 52, 68, 78, 85, 92, 98, 95, 88, 75, 62, 48],
        color: '#22C55E'
      },
      {
        label: 'Previous Year',
        data: [42, 48, 65, 72, 80, 88, 94, 90, 82, 70, 58, 45],
        color: '#94A3B8'
      }
    ]
  });

  // Cost breakdown data with dynamic generation
  const [costBreakdown, setCostBreakdown] = useState(() => {
    const generateCostData = (totalCost: number) => {
      const basePercentages = [45, 30, 25];
      const variation = basePercentages.map(p => p + (Math.random() - 0.5) * 6);
      const total = variation.reduce((sum, p) => sum + p, 0);
      const normalized = variation.map(p => Math.round((p / total) * 100));

      return [
        { category: 'Labor', percentage: normalized[0], value: Math.round(totalCost * normalized[0] / 100), color: '#DFBA47' },
        { category: 'Materials', percentage: normalized[1], value: Math.round(totalCost * normalized[1] / 100), color: '#3B82F6' },
        { category: 'Equipment', percentage: normalized[2], value: Math.round(totalCost * normalized[2] / 100), color: '#EF4444' }
      ];
    };

    return generateCostData(42150);
  });

  // Helper function to generate bounded random changes
  const generateChange = (current: number, min: number, max: number, trend: 'increase' | 'decrease' | 'fluctuate' = 'fluctuate') => {
    let changePercent;

    switch (trend) {
      case 'increase':
        changePercent = Math.random() * 0.02 + 0.005; // 0.5% to 2.5% increase
        break;
      case 'decrease':
        changePercent = -(Math.random() * 0.015 + 0.005); // 0.5% to 2% decrease
        break;
      default:
        changePercent = (Math.random() - 0.5) * 0.03; // -1.5% to +1.5%
    }

    const newValue = current * (1 + changePercent);
    return Math.max(min, Math.min(max, newValue));
  };



  // Button handler functions
  const handleExportData = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      statistics: {
        totalYield,
        waterUsage,
        fieldEfficiency,
        operatingCosts
      },
      monthlyYield: monthlyYieldData,
      resourceUtilization,
      fieldComparisons,
      seasonalTrends,
      costBreakdown
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `agricultural-statistics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleViewDetails = () => {
    setShowDetailedView(!showDetailedView);
  };

  const handleRefreshData = () => {
    updateAllData();
  };

  const handleExpandView = () => {
    setIsExpanded(!isExpanded);
  };

  // Generate dynamic main stats with realistic growth percentages
  const mainStats: StatisticCard[] = [
    {
      title: 'Total Yield',
      value: `${totalYield.toLocaleString()} bu`,
      change: mockDataService.calculateGrowthPercentage(totalYield, prevValues.current.totalYield),
      changeType: totalYield >= prevValues.current.totalYield ? 'positive' : 'negative',
      icon: '🌾',
      color: '#22C55E'
    },
    {
      title: 'Water Usage',
      value: `${waterUsage.toLocaleString()} gal`,
      change: mockDataService.calculateGrowthPercentage(waterUsage, prevValues.current.waterUsage),
      changeType: waterUsage <= prevValues.current.waterUsage ? 'positive' : 'negative', // Lower water usage is positive
      icon: '💧',
      color: '#3B82F6'
    },
    {
      title: 'Field Efficiency',
      value: `${fieldEfficiency.toFixed(1)}%`,
      change: mockDataService.calculateGrowthPercentage(fieldEfficiency, prevValues.current.fieldEfficiency),
      changeType: fieldEfficiency >= prevValues.current.fieldEfficiency ? 'positive' : 'negative',
      icon: '📊',
      color: '#DFBA47'
    },
    {
      title: 'Operating Costs',
      value: `$${operatingCosts.toLocaleString()}`,
      change: mockDataService.calculateGrowthPercentage(operatingCosts, prevValues.current.operatingCosts),
      changeType: operatingCosts <= prevValues.current.operatingCosts ? 'positive' : 'negative', // Lower costs are positive
      icon: '💰',
      color: '#EF4444'
    }
  ];

  // Handle time period changes with realistic data scaling
  const handleTimePeriodChange = (newPeriod: string) => {
    setSelectedTimePeriod(newPeriod);

    // Get base values for the new time period
    const baseValues = mockDataService.getBaseValues(newPeriod);

    // Store current values as previous for change calculation
    prevValues.current = {
      totalYield,
      waterUsage,
      fieldEfficiency,
      operatingCosts
    };

    // Update main metrics to reflect the new time period
    setTotalYield(baseValues.totalYield);
    setWaterUsage(baseValues.waterUsage);
    setFieldEfficiency(baseValues.fieldEfficiency);
    setOperatingCosts(baseValues.operatingCosts);

    // Update chart data for the new time period
    const generateChartData = (period: string) => {
      const baseValues = {
        'Last 7 Days': { corn: 45, wheat: 28, soybeans: 18 },
        'Last 30 Days': { corn: 85, wheat: 55, soybeans: 35 },
        'This Month': { corn: 92, wheat: 62, soybeans: 42 },
        'Last Quarter': { corn: 125, wheat: 85, soybeans: 65 },
        'Year to Date': { corn: 180, wheat: 120, soybeans: 95 },
        'Custom': { corn: 110, wheat: 75, soybeans: 55 }
      };

      const values = baseValues[period as keyof typeof baseValues] || baseValues['Last 30 Days'];
      const labels = period === 'Last 7 Days' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] :
                    period === 'Last Quarter' ? ['Month 1', 'Month 2', 'Month 3'] :
                    period === 'Year to Date' ? ['Q1', 'Q2', 'Q3', 'Q4'] :
                    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];

      return {
        labels,
        datasets: [
          {
            label: 'Corn',
            data: labels.map(() => Math.max(10, values.corn + (Math.random() - 0.5) * 20)),
            color: '#F59E0B'
          },
          {
            label: 'Wheat',
            data: labels.map(() => Math.max(8, values.wheat + (Math.random() - 0.5) * 15)),
            color: '#DFBA47'
          },
          {
            label: 'Soybeans',
            data: labels.map(() => Math.max(5, values.soybeans + (Math.random() - 0.5) * 12)),
            color: '#22C55E'
          }
        ]
      };
    };

    setMonthlyYieldData(generateChartData(newPeriod));
  };

  // Initial loading simulation
  useEffect(() => {
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(loadingTimer);
  }, []);

  // Real-time data updates every 5 seconds
  useEffect(() => {
    if (isLoading) return;

    const interval = setInterval(() => {
      updateAllData();
    }, 5000);

    return () => clearInterval(interval);
  }, [isLoading, totalYield, waterUsage, fieldEfficiency, operatingCosts]);

  // Update data periodically
  useEffect(() => {
    if (isLoading) return;

    const interval = setInterval(() => {
      // Store previous values for change calculation
      prevValues.current = {
        totalYield,
        waterUsage,
        fieldEfficiency,
        operatingCosts
      };

      // Update main statistics with realistic trends
      setTotalYield(prev => Math.round(generateChange(prev, 1000, 2000, 'increase')));
      setWaterUsage(prev => Math.round(generateChange(prev, 25000, 45000, 'fluctuate')));
      setFieldEfficiency(prev => Math.round(generateChange(prev, 70, 100, 'fluctuate')));
      setOperatingCosts(prev => Math.round(generateChange(prev, 35000, 55000, 'increase')));

      // Update monthly yield chart data
      setMonthlyYieldData(prev => ({
        ...prev,
        datasets: prev.datasets.map(dataset => ({
          ...dataset,
          data: dataset.data.map(value =>
            Math.round(generateChange(value, 20, 120, 'fluctuate'))
          )
        }))
      }));

      // Update resource utilization with trends
      setResourceUtilization(prev =>
        prev.map(resource => {
          let trendType: 'increase' | 'decrease' | 'fluctuate' = 'fluctuate';
          if (resource.trend === 'increasing') trendType = 'increase';
          else if (resource.trend === 'decreasing') trendType = 'decrease';

          return {
            ...resource,
            value: Math.round(generateChange(resource.value, 20, 100, trendType))
          };
        })
      );

      // Update field comparisons
      setFieldComparisons(prev =>
        prev.map(field => {
          const newCurrent = Math.round(generateChange(field.current, 60, 120, 'fluctuate'));
          const newChange = ((newCurrent - field.previous) / field.previous) * 100;
          return {
            ...field,
            current: newCurrent,
            change: Math.round(newChange * 10) / 10 // Round to 1 decimal place
          };
        })
      );

      // Update seasonal trends
      setSeasonalTrends(prev => ({
        ...prev,
        datasets: prev.datasets.map(dataset => ({
          ...dataset,
          data: dataset.data.map(value =>
            Math.round(generateChange(value, 30, 110, 'fluctuate'))
          )
        }))
      }));

      // Update cost breakdown
      setCostBreakdown(prev => {
        const updatedCosts = prev.map(cost => ({
          ...cost,
          value: Math.round(generateChange(cost.value, cost.value * 0.8, cost.value * 1.2, 'fluctuate'))
        }));

        // Recalculate percentages to ensure they add up to 100%
        const total = updatedCosts.reduce((sum, cost) => sum + cost.value, 0);
        return updatedCosts.map(cost => ({
          ...cost,
          percentage: Math.round((cost.value / total) * 100)
        }));
      });
    }, 3000); // Update every 3 seconds

    return () => clearInterval(interval);
  }, [totalYield, waterUsage, fieldEfficiency, operatingCosts]);



  // Sample time periods
  const timePeriods = ['Last 7 Days', 'Last 30 Days', 'This Month', 'Last Quarter', 'Year to Date', 'Custom'];

  const [selectedTimePeriod, setSelectedTimePeriod] = useState('Last 30 Days');
  const [selectedMetric, setSelectedMetric] = useState('All Metrics');

  // Real-time data update service
  const updateAllData = () => {
    setIsUpdating(true);

    // Store previous values for change calculation
    prevValues.current = {
      totalYield,
      waterUsage,
      fieldEfficiency,
      operatingCosts
    };

    // Update main metrics with realistic incremental changes
    setTotalYield(prev => mockDataService.generateRealisticUpdate(prev, 'yield'));
    setWaterUsage(prev => mockDataService.generateRealisticUpdate(prev, 'water'));
    setFieldEfficiency(prev => mockDataService.generateRealisticUpdate(prev, 'efficiency'));
    setOperatingCosts(prev => mockDataService.generateRealisticUpdate(prev, 'cost'));

    // Update monthly yield chart with small variations
    setMonthlyYieldData(prev => ({
      ...prev,
      datasets: prev.datasets.map(dataset => ({
        ...dataset,
        data: dataset.data.map(value => {
          const change = (Math.random() - 0.5) * 8; // ±4 variation
          return Math.max(10, Math.min(200, value + change));
        })
      }))
    }));

    // Update resource utilization
    setResourceUtilization(prev =>
      prev.map(resource => {
        const trendMultiplier = resource.trend === 'increasing' ? 1.2 :
                              resource.trend === 'decreasing' ? 0.8 : 1.0;
        const change = (Math.random() - 0.5) * 3 * trendMultiplier;
        return {
          ...resource,
          value: Math.max(20, Math.min(100, Math.round(resource.value + change)))
        };
      })
    );

    // Update cost breakdown with current operating costs
    setCostBreakdown(prev => {
      const total = operatingCosts;
      return prev.map(cost => {
        const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
        const newPercentage = Math.max(15, Math.min(60, cost.percentage + variation * 100));
        return {
          ...cost,
          percentage: Math.round(newPercentage),
          value: Math.round(total * newPercentage / 100)
        };
      });
    });

    setLastRefresh(new Date());

    // Clear updating indicator after a brief delay
    setTimeout(() => setIsUpdating(false), 500);
  };

  // Sample metrics filter options
  const metricOptions = [
    'All Metrics',
    'Yield Performance',
    'Resource Usage',
    'Cost Analysis',
    'Efficiency Metrics',
    'Environmental Impact'
  ];

  // Helper function for displaying change with sign and color
  const renderChange = (change: number, changeType?: 'positive' | 'negative' | 'neutral') => {
    let displayType = changeType;
    
    // If changeType is not provided, determine based on change value
    if (!displayType) {
      displayType = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
    }
    
    const classes = `stat-change ${displayType}`;
    const prefix = change > 0 ? '+' : '';
    
    return (
      <span className={classes}>
        {prefix}{change}%
      </span>
    );
  };

  // Function to render enhanced charts with dynamic data
  const renderFakeChart = (type: 'bar' | 'line' | 'pie' | 'utilization' | 'seasonal') => {
    if (type === 'utilization') {
      return (
        <div className="utilization-chart">
          {resourceUtilization.map((item, index) => (
            <div className="utilization-item" key={index}>
              <div className="utilization-label">
                <span className="resource-name">{item.category}</span>
                <div className="resource-metrics">
                  <span className="current-value">{item.value}%</span>
                  <span className="target-value">Target: {item.target}%</span>
                </div>
              </div>
              <div className="utilization-bar-container">
                <div
                  className="utilization-bar"
                  style={{
                    width: `${item.value}%`,
                    backgroundColor: item.color,
                    transition: 'width 0.5s ease-in-out'
                  }}
                ></div>
                <div
                  className="target-line"
                  style={{
                    left: `${item.target}%`,
                    borderColor: item.color
                  }}
                ></div>
              </div>
              <div className={`trend-indicator ${item.trend}`}>
                {item.trend === 'increasing' ? '↗' : item.trend === 'decreasing' ? '↘' : '→'}
                <span>{item.trend}</span>
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (type === 'seasonal') {
      return (
        <div className="seasonal-chart">
          <div className="chart-grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="chart-grid-line"></div>
            ))}
          </div>
          <div className="seasonal-lines">
            {seasonalTrends.datasets.map((dataset, datasetIndex) => (
              <div key={datasetIndex} className="seasonal-line-container">
                <svg className="seasonal-line" viewBox="0 0 300 100">
                  <polyline
                    points={dataset.data.map((value, index) =>
                      `${(index / (dataset.data.length - 1)) * 300},${100 - (value / 110) * 100}`
                    ).join(' ')}
                    fill="none"
                    stroke={dataset.color}
                    strokeWidth="2"
                    style={{ transition: 'all 0.5s ease-in-out' }}
                  />
                  {dataset.data.map((value, index) => (
                    <circle
                      key={index}
                      cx={(index / (dataset.data.length - 1)) * 300}
                      cy={100 - (value / 110) * 100}
                      r="3"
                      fill={dataset.color}
                      style={{ transition: 'all 0.5s ease-in-out' }}
                    />
                  ))}
                </svg>
              </div>
            ))}
          </div>
          <div className="chart-labels">
            {seasonalTrends.labels.map((label, index) => (
              <span key={index} className="chart-label">{label}</span>
            ))}
          </div>
        </div>
      );
    }
  
    return (
      <div className={`fake-chart ${type}-chart`}>
        {type === 'bar' && (
          <div className="enhanced-bar-chart">
            <div className="chart-grid">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="chart-grid-line" style={{ bottom: `${i * 20}%` }}>
                  <span className="grid-label">{i * 25}</span>
                </div>
              ))}
            </div>
            <div className="chart-bars">
              {monthlyYieldData.labels.map((label, index) => (
                <div className="chart-month" key={index}>
                  <div className="bar-group">
                    {monthlyYieldData.datasets.map((dataset, datasetIndex) => (
                      <div
                        key={datasetIndex}
                        className="chart-bar"
                        style={{
                          height: `${(dataset.data[index] / 120) * 100}%`,
                          backgroundColor: dataset.color,
                          transition: 'all 0.5s ease-in-out',
                          animationDelay: `${datasetIndex * 0.1}s`
                        } as React.CSSProperties & { '--bar-color': string }}
                        title={`${dataset.label}: ${dataset.data[index]} bu/acre`}
                        data-crop={dataset.label}
                        data-value={dataset.data[index]}
                      >
                        <span className="bar-value">{dataset.data[index]}</span>
                        <div className="bar-tooltip">
                          <strong>{dataset.label}</strong><br/>
                          {dataset.data[index]} bu/acre
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="chart-label">{label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {type === 'line' && (
          <div className="chart-placeholder">
            <div className="chart-line"></div>
            <div className="chart-line secondary"></div>
            <div className="chart-grid">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="chart-grid-line"></div>
              ))}
            </div>
          </div>
        )}

        {type === 'pie' && (
          <div className="enhanced-pie-chart">
            <div className="pie-container">
              <svg viewBox="0 0 240 240" className="pie-svg">
                <defs>
                  {costBreakdown.map((segment, index) => (
                    <linearGradient key={index} id={`gradient-${index}`} x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor={segment.color} stopOpacity="1" />
                      <stop offset="100%" stopColor={segment.color} stopOpacity="0.8" />
                    </linearGradient>
                  ))}
                </defs>
                {costBreakdown.map((segment, index) => {
                  const total = costBreakdown.reduce((sum, s) => sum + s.percentage, 0);
                  const normalizedPercentage = (segment.percentage / total) * 100;
                  const startAngle = costBreakdown.slice(0, index).reduce((sum, s) => sum + ((s.percentage / total) * 360), 0);
                  const endAngle = startAngle + (normalizedPercentage * 3.6);
                  const largeArcFlag = normalizedPercentage > 50 ? 1 : 0;

                  const radius = 90;
                  const centerX = 120;
                  const centerY = 120;

                  const x1 = centerX + radius * Math.cos((startAngle - 90) * Math.PI / 180);
                  const y1 = centerY + radius * Math.sin((startAngle - 90) * Math.PI / 180);
                  const x2 = centerX + radius * Math.cos((endAngle - 90) * Math.PI / 180);
                  const y2 = centerY + radius * Math.sin((endAngle - 90) * Math.PI / 180);

                  // Calculate label position
                  const labelAngle = (startAngle + endAngle) / 2;
                  const labelRadius = radius * 0.7;
                  const labelX = centerX + labelRadius * Math.cos((labelAngle - 90) * Math.PI / 180);
                  const labelY = centerY + labelRadius * Math.sin((labelAngle - 90) * Math.PI / 180);

                  return (
                    <g key={index}>
                      <path
                        d={`M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                        fill={`url(#gradient-${index})`}
                        stroke="#fff"
                        strokeWidth="3"
                        style={{
                          transition: 'all 0.5s ease-in-out',
                          filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                        }}
                        className="pie-segment"
                      />
                      {normalizedPercentage > 8 && (
                        <text
                          x={labelX}
                          y={labelY}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className="pie-label"
                          fill="#fff"
                          fontSize="12"
                          fontWeight="600"
                        >
                          {Math.round(normalizedPercentage)}%
                        </text>
                      )}
                    </g>
                  );
                })}
                <circle cx="120" cy="120" r="35" fill="#fff" stroke="#e5e7eb" strokeWidth="2" />
                <text x="120" y="115" textAnchor="middle" className="pie-center-text" fontSize="10" fontWeight="600">
                  Total Cost
                </text>
                <text x="120" y="128" textAnchor="middle" className="pie-center-value" fontSize="12" fontWeight="700">
                  ${costBreakdown.reduce((sum, c) => sum + c.value, 0).toLocaleString()}
                </text>
              </svg>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="statistics-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>Loading Agricultural Analytics...</h2>
          <p>Gathering real-time data from your farm systems</p>
        </div>
      </div>
    );
  }

  return (
    <div className="statistics-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Statistics & Analytics</h1>
          <p>Key performance metrics and agricultural analytics</p>
          <div className="live-data-indicator">
            <span className="period-label">Current View:</span>
            <span className="period-value">{selectedTimePeriod}</span>
            <span className="period-description">Live data updates every 5 seconds</span>
            {isUpdating && (
              <div className="updating-indicator">
                <div className="updating-spinner"></div>
                <span>Updating...</span>
              </div>
            )}
          </div>
        </div>
        <div className="header-actions">
          <button className="btn-secondary" onClick={handleRefreshData} title="Refresh data">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Refresh
            <span className="refresh-time">Last: {lastRefresh.toLocaleTimeString()}</span>
          </button>
          <button className="btn-secondary" onClick={handleExportData} title="Export data as JSON">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Export Data
          </button>
          <button className="btn-secondary" onClick={handleExpandView} title={isExpanded ? "Collapse view" : "Expand view"}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              {isExpanded ? (
                <path fillRule="evenodd" d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clipRule="evenodd" />
              ) : (
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              )}
            </svg>
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
          <button className="btn-primary" onClick={handleViewDetails} title={showDetailedView ? "Hide details" : "Show detailed view"}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            {showDetailedView ? 'Hide Details' : 'View Details'}
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="time-filter">
          <label>Time Period:</label>
          <div className="time-buttons">
            {timePeriods.map((period) => (
              <button
                key={period}
                className={`time-button ${selectedTimePeriod === period ? 'active' : ''}`}
                onClick={() => handleTimePeriodChange(period)}
              >
                {period}
              </button>
            ))}
          </div>
        </div>
        <div className="metrics-filter">
          <label>Filter Metrics:</label>
          <select
            className="metric-select"
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            {metricOptions.map((metric) => (
              <option key={metric} value={metric}>{metric}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Statistics Cards */}
      <div className="stats-cards">
        {mainStats.map((stat, index) => (
          <div className="stat-card" key={index}>
            <div className="stat-icon" style={{ backgroundColor: `${stat.color}20` }}>
              <span style={{ color: stat.color }}>{stat.icon}</span>
            </div>
            <div className="stat-content">
              <h3 className="stat-title">{stat.title}</h3>
              <div className="stat-value-container">
                <span className="stat-value">{stat.value}</span>
                {stat.change !== undefined && renderChange(stat.change, stat.changeType)}
              </div>
              {showDetailedView && (
                <div className="stat-details">
                  <div className="detail-row">
                    <span className="detail-label">Previous Value:</span>
                    <span className="detail-value">
                      {index === 0 && prevValues.current.totalYield.toLocaleString()}
                      {index === 1 && prevValues.current.waterUsage.toLocaleString()}
                      {index === 2 && `${prevValues.current.fieldEfficiency}%`}
                      {index === 3 && `$${prevValues.current.operatingCosts.toLocaleString()}`}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Target:</span>
                    <span className="detail-value">
                      {index === 0 && '1,500'}
                      {index === 1 && '30,000'}
                      {index === 2 && '95%'}
                      {index === 3 && '$40,000'}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Last Updated:</span>
                    <span className="detail-value">{lastRefresh.toLocaleTimeString()}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Expanded View - Additional Metrics */}
      {isExpanded && (
        <div className="expanded-metrics">
          <h2>Additional Performance Metrics</h2>
          <div className="expanded-grid">
            <div className="metric-card">
              <h4>🌡️ Weather Impact</h4>
              <div className="metric-value">
                Temperature: {Math.round(Math.random() * 15 + 20)}°C
              </div>
              <div className="metric-value">
                Humidity: {Math.round(Math.random() * 30 + 50)}%
              </div>
              <div className="metric-value">
                Rainfall: {Math.round(Math.random() * 50 + 10)}mm
              </div>
            </div>
            <div className="metric-card">
              <h4>🚜 Equipment Status</h4>
              <div className="metric-value">
                Active Tractors: {Math.round(Math.random() * 5 + 3)}
              </div>
              <div className="metric-value">
                Maintenance Due: {Math.round(Math.random() * 2 + 1)}
              </div>
              <div className="metric-value">
                Fuel Level: {Math.round(Math.random() * 40 + 60)}%
              </div>
            </div>
            <div className="metric-card">
              <h4>👥 Workforce</h4>
              <div className="metric-value">
                Active Workers: {Math.round(Math.random() * 10 + 15)}
              </div>
              <div className="metric-value">
                Hours Worked: {Math.round(Math.random() * 20 + 160)}h
              </div>
              <div className="metric-value">
                Productivity: {Math.round(Math.random() * 20 + 80)}%
              </div>
            </div>
            <div className="metric-card">
              <h4>📊 Quality Metrics</h4>
              <div className="metric-value">
                Crop Quality: {Math.round(Math.random() * 15 + 85)}%
              </div>
              <div className="metric-value">
                Pest Control: {Math.round(Math.random() * 10 + 90)}%
              </div>
              <div className="metric-value">
                Soil Health: {Math.round(Math.random() * 20 + 75)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts and Detailed Statistics */}
      <div className="analytics-section">
        <div className="analytics-grid">
          {/* Monthly Yield Chart */}
          <div className="analytics-card wide">
            <div className="card-header">
              <h3>Monthly Yield Performance</h3>
              <div className="card-actions">
                <button className="card-action-btn" onClick={handleRefreshData} title="Refresh chart data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                </button>
                <button className="card-action-btn" onClick={() => {
                  const chartData = {
                    type: 'Monthly Yield Performance',
                    data: monthlyYieldData,
                    timestamp: new Date().toISOString()
                  };
                  const dataStr = JSON.stringify(chartData, null, 2);
                  const dataBlob = new Blob([dataStr], { type: 'application/json' });
                  const url = URL.createObjectURL(dataBlob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'monthly-yield-data.json';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                }} title="Export chart data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="card-content">
              {renderFakeChart('bar')}
              <div className="chart-legend">
                {monthlyYieldData.datasets.map((dataset, index) => (
                  <div className="legend-item" key={index}>
                    <div className="legend-color" style={{ backgroundColor: dataset.color }}></div>
                    <span>{dataset.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Resource Utilization */}
          <div className="analytics-card">
            <div className="card-header">
              <h3>Resource Utilization</h3>
              <div className="card-actions">
                <button className="card-action-btn" onClick={handleRefreshData} title="Refresh data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                </button>
                <button className="card-action-btn" onClick={() => {
                  const data = { type: 'Resource Utilization', data: resourceUtilization, timestamp: new Date().toISOString() };
                  const dataStr = JSON.stringify(data, null, 2);
                  const dataBlob = new Blob([dataStr], { type: 'application/json' });
                  const url = URL.createObjectURL(dataBlob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'resource-utilization-data.json';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                }} title="Export data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="card-content">
              {renderFakeChart('utilization')}
            </div>
          </div>
          
          {/* Cost Breakdown */}
          <div className="analytics-card">
            <div className="card-header">
              <h3>Cost Breakdown</h3>
              <div className="card-actions">
                <button className="card-action-btn" onClick={handleRefreshData} title="Refresh data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                  </svg>
                </button>
                <button className="card-action-btn" onClick={() => {
                  const data = { type: 'Cost Breakdown', data: costBreakdown, timestamp: new Date().toISOString() };
                  const dataStr = JSON.stringify(data, null, 2);
                  const dataBlob = new Blob([dataStr], { type: 'application/json' });
                  const url = URL.createObjectURL(dataBlob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'cost-breakdown-data.json';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                }} title="Export data">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="card-content">
              {renderFakeChart('pie')}
              <div className="chart-legend pie-legend">
                {costBreakdown.map((cost, index) => (
                  <div className="legend-item" key={index}>
                    <div className="legend-color" style={{ backgroundColor: cost.color }}></div>
                    <span>{cost.category} ({cost.percentage}%) - ${cost.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Field Comparison */}
          <div className="analytics-card wide">
            <div className="card-header">
              <h3>Field Performance Comparison</h3>
              <div className="card-actions">
                <button className="card-action-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="card-content">
              <div className="comparison-table">
                <table>
                  <thead>
                    <tr>
                      <th>Field Name</th>
                      <th>Current Yield</th>
                      <th>Previous Yield</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fieldComparisons.map((field, index) => (
                      <tr key={index}>
                        <td>{field.title}</td>
                        <td><strong>{field.current} {field.unit}</strong></td>
                        <td>{field.previous} {field.unit}</td>
                        <td className={field.change > 0 ? 'positive' : 'negative'}>
                          {field.change > 0 ? '+' : ''}{field.change}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          {/* Seasonal Trends */}
          <div className="analytics-card wide">
            <div className="card-header">
              <h3>Seasonal Trends</h3>
              <div className="card-actions">
                <button className="card-action-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="card-content">
              {renderFakeChart('seasonal')}
              <div className="chart-legend">
                {seasonalTrends.datasets.map((dataset, index) => (
                  <div className="legend-item" key={index}>
                    <div className="legend-color" style={{ backgroundColor: dataset.color }}></div>
                    <span>{dataset.label}</span>
                    <span className="dataset-stats">
                      Avg: {Math.round(dataset.data.reduce((a, b) => a + b, 0) / dataset.data.length)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;
