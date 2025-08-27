import React, { useState, useEffect } from 'react';
import './BusinessIntelligencePage.css';

interface SellerProfile {
  seller_id: string;
  business_name: string;
  owner_name: string;
  business_type: string;
  verification_status: string;
  overall_rating: number;
  total_reviews: number;
  profile_completeness: number;
  financial_profile: {
    credit_score: number;
    annual_turnover: number;
    payment_history_score: number;
  };
  quality_metrics: {
    consistency_score: number;
    rejection_rate: number;
    customer_satisfaction: number;
    satellite_quality_index: number;
  };
  market_performance: {
    delivery_performance: number;
    customer_retention_rate: number;
    total_sales_volume: number;
  };
  certifications: Array<{
    certification_type: string;
    certification_number: string;
    verification_status: string;
  }>;
  satellite_monitoring: {
    current_ndvi: number;
    soil_moisture: number;
    crop_health_index: number;
    weather_risk: string;
  };
  ai_risk_assessment: {
    overall_risk: string;
    recommendation: string;
  };
}

interface FarmerProfile {
  farmer_id: string;
  name: string;
  business_type: string;
  verification_status: string;
  location: {
    state: string;
    district: string;
    village: string;
  };
  business_score: number;
  risk_level: string;
  agriculture_credit_score: number;
  score_category: string;
  profile_completeness: number;
  farming_experience: string;
  primary_crops: string[];
  farm_size_hectares: number;
  satellite_metrics: {
    ndvi_score: number;
    soil_moisture: number;
    environmental_score: number;
    crop_health_status: string;
  };
  financial_profile: {
    repayment_success_rate: number;
    current_outstanding: number;
    total_loans_taken: number;
    financial_stability: string;
  };
  market_performance: {
    total_sales_volume: number;
    customer_satisfaction_score: number;
    delivery_success_rate: number;
    repeat_customer_rate: number;
  };
  technology_adoption: {
    adoption_score: number;
    uses_satellite_monitoring: boolean;
    uses_ai_recommendations: boolean;
    uses_precision_agriculture: boolean;
  };
  production_capacity: {
    estimated_annual_production: number;
    crop_diversity_score: number;
    seasonal_availability: boolean;
  };
}

interface MarketAnalysis {
  market_overview: {
    total_market_size: string;
    growth_rate: string;
    active_suppliers: number;
    verified_suppliers_percentage: number;
  };
  quality_insights: {
    average_consistency_score: number;
    average_rejection_rate: number;
    satellite_quality_average: number;
  };
  financial_health: {
    average_credit_score: number;
    low_risk_suppliers: number;
  };
  performance_metrics: {
    average_delivery_performance: number;
    average_customer_satisfaction: number;
    high_performance_suppliers: number;
  };
}

const BusinessIntelligencePage: React.FC = () => {
  const [sellers, setSellers] = useState<SellerProfile[]>([]);
  const [farmers, setFarmers] = useState<FarmerProfile[]>([]);
  const [marketAnalysis, setMarketAnalysis] = useState<MarketAnalysis | null>(null);
  const [selectedSeller, setSelectedSeller] = useState<SellerProfile | null>(null);
  const [selectedFarmer, setSelectedFarmer] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'sellers' | 'farmers' | 'reports'>('overview');
  const [supplierView, setSupplierView] = useState<'sellers' | 'farmers'>('farmers');

  const [filters, setFilters] = useState({
    verification_status: '',
    business_type: '',
    min_rating: 0,
    location: ''
  });

  const [farmerFilters, setFarmerFilters] = useState({
    verified_only: false,
    min_credit_score: 300,
    experience_level: '',
    location_state: ''
  });

  useEffect(() => {
    fetchBusinessIntelligenceData();
  }, [filters, farmerFilters]);

  const fetchBusinessIntelligenceData = async () => {
    try {
      setLoading(true);
      
      // Fetch seller profiles
      const sellersParams = new URLSearchParams();
      if (filters.verification_status) sellersParams.append('verification_status', filters.verification_status);
      if (filters.business_type) sellersParams.append('business_type', filters.business_type);
      if (filters.min_rating > 0) sellersParams.append('min_rating', filters.min_rating.toString());
      if (filters.location) sellersParams.append('location', filters.location);

      const sellersResponse = await fetch(`http://localhost:8000/business-intel/seller-profiles?${sellersParams}`);
      const sellersData = await sellersResponse.json();

      // Fetch farmer profiles for business intelligence
      const farmerParams = new URLSearchParams();
      if (farmerFilters.verified_only) farmerParams.append('verified_only', 'true');
      if (farmerFilters.min_credit_score > 300) farmerParams.append('min_credit_score', farmerFilters.min_credit_score.toString());
      if (farmerFilters.experience_level) farmerParams.append('experience_level', farmerFilters.experience_level);
      if (farmerFilters.location_state) farmerParams.append('location_state', farmerFilters.location_state);

      const farmersResponse = await fetch(`http://localhost:8000/business-intel/farmer-profiles?${farmerParams}`);
      const farmersData = await farmersResponse.json();

      // Fetch market analysis
      const analysisResponse = await fetch('http://localhost:8000/business-intel/market-analysis');
      const analysisData = await analysisResponse.json();

      if (sellersData.status === 'success') {
        setSellers(sellersData.sellers);
      }

      if (farmersData.status === 'success') {
        setFarmers(farmersData.farmer_profiles);
      }

      if (analysisData.status === 'success') {
        setMarketAnalysis(analysisData.analysis);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch business intelligence data:', error);
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low':
      case 'very low':
        return 'text-green-600 bg-green-100';
      case 'medium':
      case 'low-medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getVerificationBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified':
        return '✅ Verified';
      case 'pending':
        return '⏳ Pending';
      case 'rejected':
        return '❌ Rejected';
      default:
        return '❓ Unknown';
    }
  };

  if (loading) {
    return (
      <div className="business-intel-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading Business Intelligence Data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="business-intel-page">
      <div className="page-header">
        <h1>🏢📊 Business Intelligence Dashboard</h1>
        <p>Comprehensive supplier analysis and market insights for informed purchasing decisions</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Market Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'sellers' ? 'active' : ''}`}
          onClick={() => setActiveTab('sellers')}
        >
          🏢 Verified Suppliers
        </button>
        <button 
          className={`tab-btn ${activeTab === 'farmers' ? 'active' : ''}`}
          onClick={() => setActiveTab('farmers')}
        >
          👨‍🌾 Verified Farmers
        </button>
        <button 
          className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          📋 BI Reports
        </button>
      </div>

      {/* Market Overview Tab */}
      {activeTab === 'overview' && marketAnalysis && (
        <div className="overview-section">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-value">{marketAnalysis.market_overview.total_market_size}</div>
                <div className="metric-label">Market Size</div>
                <div className="metric-trend">+{marketAnalysis.market_overview.growth_rate} Growth</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">✅</div>
              <div className="metric-content">
                <div className="metric-value">{marketAnalysis.market_overview.verified_suppliers_percentage}%</div>
                <div className="metric-label">Verified Suppliers</div>
                <div className="metric-trend">High Trust Score</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-content">
                <div className="metric-value">{marketAnalysis.quality_insights.average_consistency_score}</div>
                <div className="metric-label">Avg Quality Score</div>
                <div className="metric-trend">Excellent Standard</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">💳</div>
              <div className="metric-content">
                <div className="metric-value">{marketAnalysis.financial_health.average_credit_score}</div>
                <div className="metric-label">Avg Credit Score</div>
                <div className="metric-trend">Strong Financial Health</div>
              </div>
            </div>
          </div>

          <div className="insights-section">
            <h3>🎯 Key Market Insights</h3>
            <div className="insights-grid">
              <div className="insight-card">
                <h4>🛡️ Risk Assessment</h4>
                <p>78% of suppliers show low-risk profiles with strong financial health and consistent quality delivery.</p>
              </div>
              <div className="insight-card">
                <h4>📈 Growth Opportunity</h4>
                <p>Direct sourcing from verified suppliers offers 15-25% cost savings compared to traditional channels.</p>
              </div>
              <div className="insight-card">
                <h4>🛰️ Technology Edge</h4>
                <p>Satellite monitoring provides 95% accuracy in quality prediction, reducing purchase risks significantly.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Verified Suppliers Tab */}
      {activeTab === 'sellers' && (
        <div className="sellers-section">
          {/* Filters */}
          <div className="filters-section">
            <h3>🔍 Filter Suppliers</h3>
            <div className="filters-grid">
              <select 
                value={filters.verification_status}
                onChange={(e) => setFilters({...filters, verification_status: e.target.value})}
                className="filter-select"
              >
                <option value="">All Verification Status</option>
                <option value="verified">Verified Only</option>
                <option value="pending">Pending</option>
              </select>

              <select 
                value={filters.business_type}
                onChange={(e) => setFilters({...filters, business_type: e.target.value})}
                className="filter-select"
              >
                <option value="">All Business Types</option>
                <option value="individual_farmer">Individual Farmers</option>
                <option value="agricultural_enterprise">Enterprises</option>
                <option value="farmer_collective">Collectives</option>
              </select>

              <input
                type="number"
                placeholder="Min Rating (0-5)"
                value={filters.min_rating || ''}
                onChange={(e) => setFilters({...filters, min_rating: parseFloat(e.target.value) || 0})}
                className="filter-input"
                min="0"
                max="5"
                step="0.1"
              />

              <input
                type="text"
                placeholder="Location (State)"
                value={filters.location}
                onChange={(e) => setFilters({...filters, location: e.target.value})}
                className="filter-input"
              />
            </div>
          </div>

          {/* Suppliers Grid */}
          <div className="suppliers-grid">
            {loading ? (
              <div className="loading-message">Loading suppliers...</div>
            ) : sellers.length > 0 ? (
              sellers.map(seller => (
                <div key={seller.seller_id} className="supplier-card">
                  <div className="supplier-header">
                    <h4>{seller.business_name}</h4>
                    <span className={`verification-badge ${seller.verification_status}`}>
                      {getVerificationBadge(seller.verification_status)}
                    </span>
                  </div>

                  <div className="supplier-info">
                    <div className="info-row">
                      <span className="label">Owner:</span>
                      <span>{seller.owner_name}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Type:</span>
                      <span>{seller.business_type.replace('_', ' ')}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Rating:</span>
                      <span>⭐ {seller.overall_rating} ({seller.total_reviews} reviews)</span>
                    </div>
                  </div>

                  <div className="performance-metrics">
                    <div className="metric-row">
                      <span>Credit Score:</span>
                      <span className={seller.financial_profile.credit_score > 700 ? 'text-green-600' : 'text-yellow-600'}>
                        {seller.financial_profile.credit_score}
                      </span>
                    </div>
                    <div className="metric-row">
                      <span>Quality Consistency:</span>
                      <span>{seller.quality_metrics.consistency_score}%</span>
                    </div>
                    <div className="metric-row">
                      <span>Delivery Performance:</span>
                      <span>{seller.market_performance.delivery_performance}%</span>
                    </div>
                    <div className="metric-row">
                      <span>Satellite Quality:</span>
                      <span>{seller.quality_metrics.satellite_quality_index}</span>
                    </div>
                  </div>

                  <div className="risk-assessment">
                    <span className={`risk-badge ${getRiskColor(seller.ai_risk_assessment.overall_risk)}`}>
                      Risk: {seller.ai_risk_assessment.overall_risk}
                    </span>
                  </div>

                  <div className="supplier-actions">
                    <button 
                      className="btn-primary"
                      onClick={() => setSelectedSeller(seller)}
                    >
                      📊 View Full Profile
                    </button>
                    <button className="btn-secondary">💬 Contact Supplier</button>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data-message">
                <h3>🔍 No Verified Suppliers Found</h3>
                <p>Try adjusting your filters or check back later for new supplier registrations.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Verified Farmers Tab */}
      {activeTab === 'farmers' && (
        <div className="farmers-section">
          {/* Farmer Filters */}
          <div className="filters-section">
            <h3>🔍 Filter Farmers</h3>
            <div className="filters-grid">
              <label className="filter-checkbox">
                <input
                  type="checkbox"
                  checked={farmerFilters.verified_only}
                  onChange={(e) => setFarmerFilters({...farmerFilters, verified_only: e.target.checked})}
                />
                Verified Only
              </label>

              <input
                type="number"
                placeholder="Min Credit Score (300-900)"
                value={farmerFilters.min_credit_score || ''}
                onChange={(e) => setFarmerFilters({...farmerFilters, min_credit_score: parseInt(e.target.value) || 300})}
                className="filter-input"
                min="300"
                max="900"
              />

              <select 
                value={farmerFilters.experience_level}
                onChange={(e) => setFarmerFilters({...farmerFilters, experience_level: e.target.value})}
                className="filter-select"
              >
                <option value="">All Experience Levels</option>
                <option value="0-2 years">Beginner (0-2 years)</option>
                <option value="3-7 years">Intermediate (3-7 years)</option>
                <option value="8-15 years">Experienced (8-15 years)</option>
                <option value="15+ years">Veteran (15+ years)</option>
              </select>

              <input
                type="text"
                placeholder="Location (State)"
                value={farmerFilters.location_state}
                onChange={(e) => setFarmerFilters({...farmerFilters, location_state: e.target.value})}
                className="filter-input"
              />
            </div>
          </div>

          {/* Farmers Grid */}
          <div className="farmers-grid">
            {farmers.map(farmer => (
              <div key={farmer.farmer_id} className="farmer-card">
                <div className="farmer-header">
                  <h4>{farmer.name}</h4>
                  <span className={`verification-badge ${farmer.verification_status}`}>
                    {getVerificationBadge(farmer.verification_status)}
                  </span>
                </div>

                <div className="farmer-info">
                  <div className="info-row">
                    <span className="label">Location:</span>
                    <span>{farmer.location.district}, {farmer.location.state}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Experience:</span>
                    <span>{farmer.farming_experience.replace('_', ' ')}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Farm Size:</span>
                    <span>{farmer.farm_size_hectares.toFixed(1)} hectares</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Primary Crops:</span>
                    <span>{farmer.primary_crops.join(', ')}</span>
                  </div>
                </div>

                <div className="farmer-metrics">
                  <div className="metric-row">
                    <span>Credit Score:</span>
                    <span className={farmer.agriculture_credit_score > 700 ? 'text-green-600' : farmer.agriculture_credit_score > 600 ? 'text-yellow-600' : 'text-red-600'}>
                      {farmer.agriculture_credit_score}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span>Business Score:</span>
                    <span>{farmer.business_score}/100</span>
                  </div>
                  <div className="metric-row">
                    <span>Profile Complete:</span>
                    <span>{farmer.profile_completeness.toFixed(1)}%</span>
                  </div>
                  <div className="metric-row">
                    <span>Crop Health:</span>
                    <span className={farmer.satellite_metrics.crop_health_status === 'Excellent' ? 'text-green-600' : 'text-yellow-600'}>
                      {farmer.satellite_metrics.crop_health_status}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span>Financial Stability:</span>
                    <span className={farmer.financial_profile.financial_stability === 'High' ? 'text-green-600' : 'text-yellow-600'}>
                      {farmer.financial_profile.financial_stability}
                    </span>
                  </div>
                </div>

                <div className="risk-assessment">
                  <span className={`risk-badge ${getRiskColor(farmer.risk_level)}`}>
                    Risk: {farmer.risk_level}
                  </span>
                </div>

                <div className="technology-indicators">
                  <div className="tech-icons">
                    {farmer.technology_adoption.uses_satellite_monitoring && <span title="Uses Satellite Monitoring">🛰️</span>}
                    {farmer.technology_adoption.uses_ai_recommendations && <span title="Uses AI Recommendations">🤖</span>}
                    {farmer.technology_adoption.uses_precision_agriculture && <span title="Uses Precision Agriculture">🎯</span>}
                  </div>
                </div>

                <div className="farmer-actions">
                  <button 
                    className="btn-primary"
                    onClick={() => setSelectedFarmer(farmer)}
                  >
                    📊 View Full Profile
                  </button>
                  <button className="btn-secondary">💬 Contact Farmer</button>
                </div>
              </div>
            ))}
          </div>

          {/* Farmer Business Intelligence Summary */}
          <div className="farmer-bi-summary">
            <h3>📈 Farmer Intelligence Summary</h3>
            <div className="summary-grid">
              <div className="summary-card">
                <div className="summary-icon">👨‍🌾</div>
                <div className="summary-content">
                  <div className="summary-value">{farmers.length}</div>
                  <div className="summary-label">Total Farmers</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">✅</div>
                <div className="summary-content">
                  <div className="summary-value">{farmers.filter(f => f.verification_status === 'verified').length}</div>
                  <div className="summary-label">Verified Farmers</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">🏆</div>
                <div className="summary-content">
                  <div className="summary-value">{farmers.filter(f => f.agriculture_credit_score > 700).length}</div>
                  <div className="summary-label">High Credit Score</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">🛡️</div>
                <div className="summary-content">
                  <div className="summary-value">{farmers.filter(f => f.risk_level === 'LOW').length}</div>
                  <div className="summary-label">Low Risk Farmers</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Business Intelligence Reports Tab */}
      {activeTab === 'reports' && (
        <div className="reports-section">
          <h3>📋 Generate Business Intelligence Report</h3>
          <div className="report-generator">
            <div className="report-options">
              <h4>📊 Report Parameters</h4>
              <div className="options-grid">
                <label>
                  <input type="checkbox" defaultChecked />
                  Supplier Risk Assessment
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Market Price Analysis
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Quality Benchmarking
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Satellite Quality Insights
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Financial Health Check
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Performance Analytics
                </label>
              </div>
            </div>

            <button className="generate-report-btn">
              📄 Generate Comprehensive BI Report
            </button>
          </div>

          <div className="sample-report">
            <h4>📊 Sample Business Intelligence Insights</h4>
            <div className="insights-list">
              <div className="insight-item">
                <span className="insight-icon">🛰️</span>
                <span>Satellite data shows excellent crop quality this season with 91% health index</span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">✅</span>
                <span>Verified sellers show 23% lower rejection rates than unverified suppliers</span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">💰</span>
                <span>Current market conditions favor bulk purchasing with 15-20% potential savings</span>
              </div>
              <div className="insight-item">
                <span className="insight-icon">📈</span>
                <span>Organic produce demand increasing by 15% in urban markets</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Seller Modal */}
      {selectedSeller && (
        <div className="modal-overlay" onClick={() => setSelectedSeller(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📊 {selectedSeller.business_name} - Detailed Profile</h3>
              <button className="modal-close" onClick={() => setSelectedSeller(null)}>×</button>
            </div>

            <div className="modal-body">
              <div className="profile-sections">
                <div className="profile-section">
                  <h4>🏢 Business Information</h4>
                  <div className="info-grid">
                    <div>Owner: {selectedSeller.owner_name}</div>
                    <div>Type: {selectedSeller.business_type}</div>
                    <div>Status: {getVerificationBadge(selectedSeller.verification_status)}</div>
                    <div>Profile: {selectedSeller.profile_completeness}% Complete</div>
                  </div>
                </div>

                <div className="profile-section">
                  <h4>💰 Financial Profile</h4>
                  <div className="info-grid">
                    <div>Credit Score: {selectedSeller.financial_profile.credit_score}</div>
                    <div>Annual Turnover: ₹{(selectedSeller.financial_profile.annual_turnover / 100000).toFixed(1)}L</div>
                    <div>Payment History: {selectedSeller.financial_profile.payment_history_score}%</div>
                  </div>
                </div>

                <div className="profile-section">
                  <h4>🎯 Quality Metrics</h4>
                  <div className="info-grid">
                    <div>Consistency Score: {selectedSeller.quality_metrics.consistency_score}%</div>
                    <div>Rejection Rate: {selectedSeller.quality_metrics.rejection_rate}%</div>
                    <div>Customer Satisfaction: {selectedSeller.quality_metrics.customer_satisfaction}/5</div>
                    <div>Satellite Quality: {selectedSeller.quality_metrics.satellite_quality_index}</div>
                  </div>
                </div>

                <div className="profile-section">
                  <h4>🛰️ Satellite Monitoring</h4>
                  <div className="info-grid">
                    <div>NDVI: {selectedSeller.satellite_monitoring.current_ndvi}</div>
                    <div>Soil Moisture: {selectedSeller.satellite_monitoring.soil_moisture}%</div>
                    <div>Crop Health: {selectedSeller.satellite_monitoring.crop_health_index}</div>
                    <div>Weather Risk: {selectedSeller.satellite_monitoring.weather_risk}</div>
                  </div>
                </div>

                <div className="profile-section">
                  <h4>📜 Certifications</h4>
                  <div className="certifications-list">
                    {selectedSeller.certifications.map((cert, index) => (
                      <div key={index} className="certification-item">
                        <span className="cert-type">{cert.certification_type}</span>
                        <span className="cert-number">{cert.certification_number}</span>
                        <span className={`cert-status ${cert.verification_status}`}>
                          {getVerificationBadge(cert.verification_status)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="profile-section">
                  <h4>🔍 AI Risk Assessment</h4>
                  <div className="risk-analysis">
                    <div className={`risk-level ${getRiskColor(selectedSeller.ai_risk_assessment.overall_risk)}`}>
                      Overall Risk: {selectedSeller.ai_risk_assessment.overall_risk}
                    </div>
                    <div className="recommendation">
                      {selectedSeller.ai_risk_assessment.recommendation}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-primary">🤝 Initiate Partnership</button>
              <button className="btn-secondary">💬 Contact Supplier</button>
              <button className="btn-secondary">📄 Generate Report</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BusinessIntelligencePage;
