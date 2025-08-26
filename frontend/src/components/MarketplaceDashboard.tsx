import React, { useState, useEffect } from 'react';
import './MarketplaceDashboard.css';

interface ProductListing {
  listing_id: string;
  product_name: string;
  category: string;
  quantity_available: number;
  price_per_unit: number;
  quality_grade: string;
  location: {
    state: string;
    district: string;
  };
  marketplace_type: string;
  organic_certified: boolean;
  satellite_quality_score?: number;
  recommended_selling_price?: number;
}

interface MarketAnalytics {
  market_summary: {
    total_listings: number;
    active_orders: number;
    average_price_trend: string;
    market_confidence: number;
  };
  ai_predictions: {
    price_forecast_7d: string;
    demand_forecast: string;
    optimal_selling_window: string;
    satellite_crop_health: string;
  };
}

const MarketplaceDashboard: React.FC = () => {
  const [listings, setListings] = useState<ProductListing[]>([]);
  const [analytics, setAnalytics] = useState<MarketAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('listings');
  const [filters, setFilters] = useState({
    category: '',
    marketplace_type: '',
    location_state: '',
    organic_only: false
  });

  // Mock data for demonstration
  const mockListings: ProductListing[] = [
    {
      listing_id: '1',
      product_name: 'Premium Wheat',
      category: 'grains',
      quantity_available: 500,
      price_per_unit: 2200,
      quality_grade: 'premium',
      location: { state: 'Punjab', district: 'Ludhiana' },
      marketplace_type: 'b2b',
      organic_certified: false,
      satellite_quality_score: 92,
      recommended_selling_price: 2300
    },
    {
      listing_id: '2',
      product_name: 'Organic Tomatoes',
      category: 'vegetables',
      quantity_available: 200,
      price_per_unit: 35,
      quality_grade: 'premium',
      location: { state: 'Maharashtra', district: 'Pune' },
      marketplace_type: 'b2c',
      organic_certified: true,
      satellite_quality_score: 88,
      recommended_selling_price: 38
    },
    {
      listing_id: '3',
      product_name: 'Basmati Rice',
      category: 'grains',
      quantity_available: 1000,
      price_per_unit: 2800,
      quality_grade: 'premium',
      location: { state: 'Haryana', district: 'Karnal' },
      marketplace_type: 'b2b',
      organic_certified: false,
      satellite_quality_score: 95,
      recommended_selling_price: 2950
    }
  ];

  const mockAnalytics: MarketAnalytics = {
    market_summary: {
      total_listings: 156,
      active_orders: 43,
      average_price_trend: 'rising',
      market_confidence: 0.85
    },
    ai_predictions: {
      price_forecast_7d: 'stable_to_rising',
      demand_forecast: 'increasing',
      optimal_selling_window: 'next_2_weeks',
      satellite_crop_health: 'good'
    }
  };

  useEffect(() => {
    // Load mock data
    setListings(mockListings);
    setAnalytics(mockAnalytics);
  }, []);

  const searchListings = async () => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      let filteredListings = mockListings;
      
      if (filters.category) {
        filteredListings = filteredListings.filter(l => l.category === filters.category);
      }
      if (filters.marketplace_type) {
        filteredListings = filteredListings.filter(l => l.marketplace_type === filters.marketplace_type);
      }
      if (filters.location_state) {
        filteredListings = filteredListings.filter(l => 
          l.location.state.toLowerCase().includes(filters.location_state.toLowerCase())
        );
      }
      if (filters.organic_only) {
        filteredListings = filteredListings.filter(l => l.organic_certified);
      }
      
      setListings(filteredListings);
      setLoading(false);
    }, 1000);
  };

  const getQualityBadgeColor = (score?: number) => {
    if (!score) return 'gray';
    if (score >= 90) return 'green';
    if (score >= 80) return 'yellow';
    return 'red';
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="marketplace-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>🌾💰 Agricultural Marketplace</h1>
        <p>AI-Powered B2B & B2C Agricultural Trading Platform</p>
      </div>

      {/* Navigation Tabs */}
      <div className="nav-tabs">
        <button 
          className={`tab ${activeTab === 'listings' ? 'active' : ''}`}
          onClick={() => setActiveTab('listings')}
        >
          🛒 Product Listings
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 Market Analytics
        </button>
        <button 
          className={`tab ${activeTab === 'ai-insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai-insights')}
        >
          🤖 AI Insights
        </button>
      </div>

      {/* Listings Tab */}
      {activeTab === 'listings' && (
        <div className="listings-section">
          {/* Search Filters */}
          <div className="search-filters">
            <h3>🔍 Search Filters</h3>
            <div className="filter-grid">
              <div className="filter-item">
                <label>Category:</label>
                <select 
                  value={filters.category} 
                  onChange={(e) => setFilters({...filters, category: e.target.value})}
                >
                  <option value="">All Categories</option>
                  <option value="grains">Grains</option>
                  <option value="vegetables">Vegetables</option>
                  <option value="fruits">Fruits</option>
                  <option value="spices">Spices</option>
                </select>
              </div>
              
              <div className="filter-item">
                <label>Marketplace:</label>
                <select 
                  value={filters.marketplace_type} 
                  onChange={(e) => setFilters({...filters, marketplace_type: e.target.value})}
                >
                  <option value="">Both B2B & B2C</option>
                  <option value="b2b">B2B (Business)</option>
                  <option value="b2c">B2C (Consumer)</option>
                </select>
              </div>
              
              <div className="filter-item">
                <label>State:</label>
                <input 
                  type="text" 
                  placeholder="e.g., Punjab" 
                  value={filters.location_state}
                  onChange={(e) => setFilters({...filters, location_state: e.target.value})}
                />
              </div>
              
              <div className="filter-item">
                <label>
                  <input 
                    type="checkbox" 
                    checked={filters.organic_only}
                    onChange={(e) => setFilters({...filters, organic_only: e.target.checked})}
                  />
                  Organic Only
                </label>
              </div>
            </div>
            
            <button className="search-btn" onClick={searchListings} disabled={loading}>
              {loading ? '🔄 Searching...' : '🔍 Search Products'}
            </button>
          </div>

          {/* Product Listings */}
          <div className="products-grid">
            {listings.map((listing) => (
              <div key={listing.listing_id} className="product-card">
                <div className="product-header">
                  <h4>{listing.product_name}</h4>
                  <span className={`marketplace-badge ${listing.marketplace_type}`}>
                    {listing.marketplace_type.toUpperCase()}
                  </span>
                </div>
                
                <div className="product-details">
                  <p><strong>📍 Location:</strong> {listing.location.district}, {listing.location.state}</p>
                  <p><strong>📦 Quantity:</strong> {listing.quantity_available} kg</p>
                  <p><strong>💰 Price:</strong> {formatPrice(listing.price_per_unit)}/kg</p>
                  <p><strong>⭐ Quality:</strong> {listing.quality_grade}</p>
                  
                  {listing.organic_certified && (
                    <span className="organic-badge">🌱 Organic Certified</span>
                  )}
                </div>
                
                {/* AI-Enhanced Information */}
                <div className="ai-info">
                  {listing.satellite_quality_score && (
                    <div className="quality-score">
                      <span 
                        className={`quality-badge ${getQualityBadgeColor(listing.satellite_quality_score)}`}
                      >
                        🛰️ Satellite Quality: {listing.satellite_quality_score}%
                      </span>
                    </div>
                  )}
                  
                  {listing.recommended_selling_price && (
                    <div className="price-recommendation">
                      <p><strong>🤖 AI Recommended:</strong> {formatPrice(listing.recommended_selling_price)}/kg</p>
                      {listing.recommended_selling_price > listing.price_per_unit && (
                        <span className="price-opportunity">📈 Price Opportunity Available!</span>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="product-actions">
                  <button className="btn-primary">📞 Contact Seller</button>
                  <button className="btn-secondary">📋 View Details</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div className="analytics-section">
          <h3>📊 Market Analytics Dashboard</h3>
          
          <div className="analytics-grid">
            {/* Market Summary */}
            <div className="analytics-card">
              <h4>📈 Market Summary</h4>
              <div className="metric">
                <span className="metric-label">Total Listings:</span>
                <span className="metric-value">{analytics.market_summary.total_listings}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Active Orders:</span>
                <span className="metric-value">{analytics.market_summary.active_orders}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Price Trend:</span>
                <span className={`metric-value trend-${analytics.market_summary.average_price_trend}`}>
                  {analytics.market_summary.average_price_trend}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Market Confidence:</span>
                <span className="metric-value">
                  {(analytics.market_summary.market_confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* AI Predictions */}
            <div className="analytics-card">
              <h4>🤖 AI Predictions</h4>
              <div className="prediction">
                <span className="prediction-label">7-Day Price Forecast:</span>
                <span className="prediction-value">{analytics.ai_predictions.price_forecast_7d}</span>
              </div>
              <div className="prediction">
                <span className="prediction-label">Demand Forecast:</span>
                <span className="prediction-value">{analytics.ai_predictions.demand_forecast}</span>
              </div>
              <div className="prediction">
                <span className="prediction-label">Optimal Selling Window:</span>
                <span className="prediction-value">{analytics.ai_predictions.optimal_selling_window}</span>
              </div>
              <div className="prediction">
                <span className="prediction-label">Crop Health (Satellite):</span>
                <span className="prediction-value">{analytics.ai_predictions.satellite_crop_health}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights Tab */}
      {activeTab === 'ai-insights' && (
        <div className="ai-insights-section">
          <h3>🤖 AI-Powered Market Insights</h3>
          
          <div className="insights-grid">
            <div className="insight-card">
              <h4>🎯 Price Optimization</h4>
              <p>Our AI agents analyze satellite data, market trends, and demand patterns to provide optimal pricing recommendations.</p>
              <ul>
                <li>🛰️ Satellite quality assessment increases pricing accuracy by 15%</li>
                <li>📊 Market timing predictions help maximize profits</li>
                <li>🔄 Real-time price adjustments based on supply-demand</li>
              </ul>
            </div>
            
            <div className="insight-card">
              <h4>🌾 Quality Prediction</h4>
              <p>Satellite-enhanced crop quality scoring helps buyers make informed decisions and farmers price appropriately.</p>
              <ul>
                <li>🛰️ NDVI analysis for vegetation health</li>
                <li>🌡️ Environmental condition monitoring</li>
                <li>📈 Yield forecasting with 85%+ accuracy</li>
              </ul>
            </div>
            
            <div className="insight-card">
              <h4>📅 Market Timing</h4>
              <p>Advanced algorithms determine the optimal time to sell based on market conditions and predictions.</p>
              <ul>
                <li>📊 Supply-demand balance analysis</li>
                <li>🌦️ Weather impact on market prices</li>
                <li>📈 Seasonal trend identification</li>
              </ul>
            </div>
            
            <div className="insight-card">
              <h4>🔗 Integration Benefits</h4>
              <p>Seamlessly integrated with your existing agricultural advisory system for comprehensive farming solutions.</p>
              <ul>
                <li>🤝 Unified farmer dashboard</li>
                <li>🌐 Multi-language support (Hindi/English)</li>
                <li>📱 Mobile-friendly interface</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketplaceDashboard;
