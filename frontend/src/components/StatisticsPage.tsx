import React, { useState, useEffect } from 'react';
import './StatisticsPage.css';

type TimePeriod = 'weekly' | 'monthly' | 'yearly';
type MetricType = 'all' | 'agricultural' | 'financial' | 'environmental';

interface StatisticData {
  id: string;
  title: string;
  value: string;
  change: {
    value: string;
    type: 'positive' | 'negative' | 'neutral';
  };
  icon: string;
  iconColor: string;
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    color: string;
  }>;
}

interface ComparisonData {
  title: string;
  current: number;
  previous: number;
  unit: string;
  change: number;
}

const StatisticsPage: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('monthly');
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('all');
  const [currentData, setCurrentData] = useState<StatisticData[]>([]);
  const [chartData, setChartData] = useState<ChartData>({ 
    labels: [], 
    datasets: [{ label: '', data: [], color: '#22C55E' }] 
  });
  const [updateTime, setUpdateTime] = useState(new Date());
  
  // Base values for realistic variations
  const baseValues = {
    totalYield: { weekly: 39, monthly: 154, yearly: 1847 },
    revenue: { weekly: 11472, monthly: 45890, yearly: 550680 },
    waterUsage: { weekly: 8570, monthly: 34280, yearly: 411360 },
    fieldEfficiency: 87.5,
    cropHealth: 92.1,
    operatingCosts: { weekly: 10537, monthly: 42150, yearly: 505800 }
  };
  
  // Helper function to format numbers
  const formatNumber = (value: number, unit: string): string => {
    if (unit === '$') {
      if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(1)}M`;
      } else if (value >= 1000) {
        return `$${(value / 1000).toFixed(1)}K`;
      }
      return `$${value.toLocaleString()}`;
    } else {
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M ${unit}`;
      } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K ${unit}`;
      }
      return `${value.toLocaleString()} ${unit}`;
    }
  };
  
  // Generate dynamic mock data with realistic variations
  const generateDynamicMockData = (period: TimePeriod, metric: MetricType, timestamp: Date): StatisticData[] => {
    // Use timestamp to create consistent but changing values
    const timeVariation = Math.sin(timestamp.getTime() / 10000) * 0.1; // 10% variation based on time
    const randomVariation = () => (Math.random() - 0.5) * 0.05; // 2.5% random variation
    
    const getVariedValue = (baseValue: number) => {
      return Math.round(baseValue * (1 + timeVariation + randomVariation()));
    };
    
    const getVariedPercentage = (baseValue: number) => {
      return (baseValue * (1 + timeVariation + randomVariation())).toFixed(1);
    };
    
    const getChangeValue = () => {
      const change = (timeVariation * 20 + (Math.random() - 0.5) * 10).toFixed(1);
      return parseFloat(change) >= 0 ? `+${change}%` : `${change}%`;
    };
    
    const getChangeType = (changeStr: string): 'positive' | 'negative' | 'neutral' => {
      const value = parseFloat(changeStr.replace('%', ''));
      if (value > 0) return 'positive';
      if (value < 0) return 'negative';
      return 'neutral';
    };

    const allStats: StatisticData[] = [
      {
        id: 'total-yield',
        title: 'Total Yield',
        value: `${getVariedValue(baseValues.totalYield[period]).toLocaleString()} tons`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '🌾',
        iconColor: '#22C55E'
      },
      {
        id: 'revenue',
        title: 'Revenue',
        value: `$${getVariedValue(baseValues.revenue[period]).toLocaleString()}`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '💰',
        iconColor: '#10B981'
      },
      {
        id: 'water-usage',
        title: 'Water Usage',
        value: `${getVariedValue(baseValues.waterUsage[period]).toLocaleString()} L`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '💧',
        iconColor: '#3B82F6'
      },
      {
        id: 'field-efficiency',
        title: 'Field Efficiency',
        value: `${getVariedPercentage(baseValues.fieldEfficiency)}%`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '⚡',
        iconColor: '#8B5CF6'
      },
      {
        id: 'crop-health',
        title: 'Crop Health',
        value: `${getVariedPercentage(baseValues.cropHealth)}%`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '🌱',
        iconColor: '#10B981'
      },
      {
        id: 'operating-costs',
        title: 'Operating Costs',
        value: `$${getVariedValue(baseValues.operatingCosts[period]).toLocaleString()}`,
        change: {
          value: getChangeValue(),
          type: getChangeType(getChangeValue())
        },
        icon: '💼',
        iconColor: '#EF4444'
      }
    ];

    // Filter by metric type
    if (metric === 'agricultural') {
      return allStats.filter(stat => ['total-yield', 'field-efficiency', 'crop-health'].includes(stat.id));
    } else if (metric === 'financial') {
      return allStats.filter(stat => ['revenue', 'operating-costs'].includes(stat.id));
    } else if (metric === 'environmental') {
      return allStats.filter(stat => ['water-usage'].includes(stat.id));
    }
    
    return allStats;
  };

  // Generate chart data with dynamic variations
  const generateDynamicChartData = (period: TimePeriod, timestamp: Date): ChartData => {
    const timeVariation = Math.sin(timestamp.getTime() / 15000) * 0.2; // Slower variation for charts
    
    let labels: string[];
    let baseData: number[];

    if (period === 'weekly') {
      labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      baseData = [45, 52, 48, 61, 55, 67, 43];
    } else if (period === 'monthly') {
      labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      baseData = [120, 135, 145, 165, 180, 195, 210, 205, 190, 175, 160, 140];
    } else {
      labels = ['2020', '2021', '2022', '2023', '2024'];
      baseData = [1650, 1780, 1920, 1854, 2100];
    }

    // Apply dynamic variations to chart data
    const dynamicData = baseData.map(value => 
      Math.round(value * (1 + timeVariation + (Math.random() - 0.5) * 0.1))
    );

    return {
      labels,
      datasets: [{
        label: 'Yield (tons)',
        data: dynamicData,
        color: '#22C55E'
      }]
    };
  };

  // Generate comparison data
  const generateComparisonData = (period: TimePeriod): ComparisonData[] => {
    const multiplier = period === 'yearly' ? 12 : period === 'monthly' ? 1 : 0.25;
    
    return [
      {
        title: 'Crop Yield',
        current: Math.round(154 * multiplier),
        previous: Math.round(142 * multiplier),
        unit: 'tons',
        change: 8.5
      },
      {
        title: 'Water Usage',
        current: Math.round(34280 * multiplier),
        previous: Math.round(37150 * multiplier),
        unit: 'L',
        change: -7.7
      },
      {
        title: 'Revenue',
        current: Math.round(45890 * multiplier),
        previous: Math.round(40850 * multiplier),
        unit: '$',
        change: 12.3
      },
      {
        title: 'Energy Usage',
        current: Math.round(12500 * multiplier),
        previous: Math.round(13200 * multiplier),
        unit: 'kWh',
        change: -5.3
      }
    ];
  };

  // Update data when period or metric changes, or every 5 seconds
  useEffect(() => {
    const updateData = () => {
      const now = new Date();
      setUpdateTime(now);
      setCurrentData(generateDynamicMockData(selectedPeriod, selectedMetric, now));
      setChartData(generateDynamicChartData(selectedPeriod, now));
    };

    // Initial update
    updateData();

    // Set up interval for updates every 5 seconds
    const interval = setInterval(updateData, 5000);

    // Cleanup interval on unmount or dependency change
    return () => clearInterval(interval);
  }, [selectedPeriod, selectedMetric]);

  const comparisonData = generateComparisonData(selectedPeriod);

  return (
    <div className="statistics-page">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <h1>Agricultural Statistics</h1>
          <p>Real-time analytics and performance metrics (Updates every 5 seconds)</p>
          <small>Last updated: {updateTime.toLocaleTimeString()}</small>
        </div>
        <div className="header-actions">
          <button className="btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Export Data
          </button>
          <button className="btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/>
              <circle cx="6" cy="12" r="3"/>
              <path d="M18 9v2.5a3.5 3.5 0 0 1-3.5 3.5H9"/>
            </svg>
            Generate Report
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="time-filter">
          <label>Time Period:</label>
          <div className="time-buttons">
            {(['weekly', 'monthly', 'yearly'] as TimePeriod[]).map((period) => (
              <button
                key={period}
                className={`time-button ${selectedPeriod === period ? 'active' : ''}`}
                onClick={() => setSelectedPeriod(period)}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="metrics-filter">
          <label>Metrics:</label>
          <select
            className="metric-select"
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
          >
            <option value="all">All Metrics</option>
            <option value="agricultural">Agricultural</option>
            <option value="financial">Financial</option>
            <option value="environmental">Environmental</option>
          </select>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-cards">
        {currentData.map((stat) => (
          <div key={stat.id} className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: stat.iconColor + '20', color: stat.iconColor }}>
              {stat.icon}
            </div>
            <div className="stat-content">
              <h3 className="stat-title">{stat.title}</h3>
              <div className="stat-value-container">
                <span className="stat-value">{stat.value}</span>
                <span className={`stat-change ${stat.change.type}`}>
                  {stat.change.value}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts and Analytics */}
      <div className="analytics-section">
        <div className="analytics-grid">
          {/* Chart Card */}
          <div className="analytics-card wide">
            <div className="card-header">
              <h3>Dynamic Yield Trends - {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1)}</h3>
              <div className="card-actions">
                <button className="card-action-btn">View Details</button>
              </div>
            </div>
            <div className="card-content">
              <div className="chart-container">
                <div className="chart-placeholder">
                  <div className="chart-grid">
                    {(chartData.labels || []).map((_, index) => (
                      <div key={index} className="chart-grid-line"></div>
                    ))}
                  </div>
                  <div className="chart-bars">
                    {chartData.datasets[0]?.data?.map((value, index) => (
                      <div 
                        key={index} 
                        className="chart-bar"
                        style={{ 
                          height: `${(value / Math.max(...(chartData.datasets[0]?.data || [1]))) * 100}%`,
                          backgroundColor: '#22C55E'
                        }}
                      ></div>
                    )) || []}
                  </div>
                </div>
                <div className="chart-labels">
                  {(chartData.labels || []).map((label, index) => (
                    <span key={index} className="chart-label">{label}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Comparison Table */}
          <div className="analytics-card">
            <div className="card-header">
              <h3>Period Comparison</h3>
            </div>
            <div className="card-content">
              <div className="comparison-table">
                <table>
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Current</th>
                      <th>Previous</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData.map((item, index) => (
                      <tr key={index}>
                        <td>{item.title}</td>
                        <td>{formatNumber(item.current, item.unit)}</td>
                        <td>{formatNumber(item.previous, item.unit)}</td>
                        <td className={item.change > 0 ? 'positive' : 'negative'}>
                          {item.change > 0 ? '+' : ''}{item.change.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Environmental Metrics */}
          <div className="analytics-card wide">
            <div className="card-header">
              <h3>Environmental Impact</h3>
            </div>
            <div className="card-content">
              <div className="environmental-metrics">
                <div className="metric-item">
                  <div className="metric-icon">🌱</div>
                  <div className="metric-info">
                    <h4>Carbon Footprint</h4>
                    <span className="metric-value">2.3 tons CO₂</span>
                    <span className="metric-change positive">-12%</span>
                  </div>
                </div>
                <div className="metric-item">
                  <div className="metric-icon">💧</div>
                  <div className="metric-info">
                    <h4>Water Conservation</h4>
                    <span className="metric-value">15,420 L saved</span>
                    <span className="metric-change positive">+8%</span>
                  </div>
                </div>
                <div className="metric-item">
                  <div className="metric-icon">⚡</div>
                  <div className="metric-info">
                    <h4>Energy Efficiency</h4>
                    <span className="metric-value">87.3%</span>
                    <span className="metric-change positive">+3.3%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;
