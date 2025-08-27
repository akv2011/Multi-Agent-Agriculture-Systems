import React, { useState, useEffect } from 'react';
import './FarmerProfilePage.css';

interface FarmerProfile {
  farmer_id: string;
  name: string;
  location: {
    state: string;
    district: string;
    village: string;
  };
  agriculture_credit_score: number;
  score_category: string;
  verification_status: string;
  farming_experience: string;
  primary_crops: string[];
  profile_completeness: number;
  farm_size_hectares: number;
  phone: string;
}

interface CreditScoreBreakdown {
  total_score: number;
  category: string;
  components: {
    [key: string]: {
      score: number;
      weight: string;
      status: string;
      details?: any;
    };
  };
  recommendations: string[];
  strengths: string[];
  improvement_areas: string[];
  next_review_date: string;
}

interface FarmerLeaderboard {
  rank: number;
  farmer_id: string;
  name: string;
  location: string;
  agriculture_credit_score: number;
  score_category: string;
  farming_experience: string;
  primary_crops: string[];
  verification_status: string;
  farm_size_hectares: number;
  profile_completeness: number;
  ndvi_score: number;
  last_active: string;
}

interface FarmerPosition {
  farmer_id: string;
  rank: number;
  total_farmers: number;
  percentile: number;
  agriculture_credit_score: number;
  score_category: string;
  improvement_needed: {
    points_to_next_category: number;
    farmers_ahead: number;
    closest_farmer_score: number;
  };
}

interface FarmerInsights {
  farmer_id: string;
  current_score: number;
  rank: number;
  total_farmers: number;
  percentile: number;
  score_category: string;
  points_to_next_category: number;
  strengths: string[];
  improvement_areas: string[];
  recommendations: string[];
  comparison: {
    state_average: number;
    national_average: number;
    top_10_percent_threshold: number;
  };
}

const FarmerProfilePage: React.FC = () => {
  // Mock current logged-in farmer ID (in real app, this would come from authentication)
  const currentFarmerId = 'FARMER_45690318'; // Rajesh Kumar Singh
  
  const [currentFarmer, setCurrentFarmer] = useState<FarmerProfile | null>(null);
  const [creditBreakdown, setCreditBreakdown] = useState<CreditScoreBreakdown | null>(null);
  const [leaderboard, setLeaderboard] = useState<FarmerLeaderboard[]>([]);
  const [farmerPosition, setFarmerPosition] = useState<FarmerPosition | null>(null);
  const [farmerInsights, setFarmerInsights] = useState<FarmerInsights | null>(null);
  const [activeTab, setActiveTab] = useState<'profiles' | 'leaderboard' | 'analytics'>('profiles');
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [selectedState, setSelectedState] = useState<string>('');

  useEffect(() => {
    fetchCurrentFarmer();
    fetchLeaderboard();
    fetchAnalytics();
    fetchFarmerPosition();
    fetchFarmerInsights();
  }, []);

  const fetchCurrentFarmer = async () => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-profile/${currentFarmerId}`);
      if (!response.ok) {
        console.error(`API Error: ${response.status} - ${response.statusText}`);
        setLoading(false);
        return;
      }
      const data = await response.json();
      console.log('Farmer data received:', data);
      setCurrentFarmer(data);
      // Also fetch credit breakdown for the current farmer
      fetchCreditBreakdown(currentFarmerId);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching current farmer:', error);
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('http://localhost:8000/farmer-leaderboard?limit=20');
      if (!response.ok) {
        console.error(`Leaderboard API Error: ${response.status} - ${response.statusText}`);
        return;
      }
      const data = await response.json();
      console.log('Leaderboard data received:', data);
      setLeaderboard(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/credit-score-analytics');
      if (!response.ok) {
        console.error(`Analytics API Error: ${response.status} - ${response.statusText}`);
        return;
      }
      const data = await response.json();
      console.log('Analytics data received:', data);
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchFarmerPosition = async () => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-leaderboard/${currentFarmerId}/position`);
      if (!response.ok) {
        console.error(`Position API Error: ${response.status} - ${response.statusText}`);
        return;
      }
      const data = await response.json();
      console.log('Position data received:', data);
      setFarmerPosition(data);
    } catch (error) {
      console.error('Error fetching farmer position:', error);
    }
  };

  const fetchFarmerInsights = async () => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-profile/${currentFarmerId}/insights`);
      if (!response.ok) {
        console.error(`Insights API Error: ${response.status} - ${response.statusText}`);
        return;
      }
      const data = await response.json();
      console.log('Insights data received:', data);
      setFarmerInsights(data);
    } catch (error) {
      console.error('Error fetching farmer insights:', error);
    }
  };

  const fetchCreditBreakdown = async (farmerId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-profile/${farmerId}/credit-score`);
      const data = await response.json();
      setCreditBreakdown(data);
    } catch (error) {
      console.error('Error fetching credit breakdown:', error);
    }
  };

  const fetchRegionalLeaderboard = async (state: string) => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-leaderboard/regional/${state}`);
      if (!response.ok) {
        console.error(`Regional Leaderboard API Error: ${response.status} - ${response.statusText}`);
        return;
      }
      const data = await response.json();
      console.log('Regional leaderboard data received:', data);
      setLeaderboard(data.leaderboard || []);
    } catch (error) {
      console.error('Error fetching regional leaderboard:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 800) return '#27ae60';
    if (score >= 700) return '#2ecc71';
    if (score >= 600) return '#f39c12';
    if (score >= 500) return '#e67e22';
    return '#e74c3c';
  };

  const getScoreGrade = (score: number) => {
    if (score >= 800) return 'A+';
    if (score >= 700) return 'A';
    if (score >= 600) return 'B';
    if (score >= 500) return 'C';
    return 'D';
  };

  const getCategoryEmoji = (category: string) => {
    switch (category.toLowerCase()) {
      case 'excellent': return '🏆';
      case 'very_good': return '🥇';
      case 'good': return '🥈';
      case 'fair': return '🥉';
      case 'poor': return '🔴';
      default: return '📊';
    }
  };

  const getVerificationIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'verified': return '✅';
      case 'pending': return '⏳';
      case 'rejected': return '❌';
      case 'not_submitted': return '⚪';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="farmer-profile-page">
        <div className="loading-container">
          <div className="spinner-large"></div>
          <h3>Loading Farmer Profiles...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="farmer-profile-page">
      <div className="profile-header">
        <h1>🌾👨‍🌾 Farmer Credit Score System</h1>
        <p>Agricultural credit scoring based on satellite data, performance history, and farming practices</p>
        
        <div className="tab-navigation">
          <button 
            className={activeTab === 'profiles' ? 'tab-active' : 'tab-inactive'}
            onClick={() => setActiveTab('profiles')}
          >
            👥 Farmer Profiles
          </button>
          <button 
            className={activeTab === 'leaderboard' ? 'tab-active' : 'tab-inactive'}
            onClick={() => setActiveTab('leaderboard')}
          >
            🏆 Leaderboard
          </button>
          <button 
            className={activeTab === 'analytics' ? 'tab-active' : 'tab-inactive'}
            onClick={() => setActiveTab('analytics')}
          >
            📊 Analytics
          </button>
        </div>
      </div>

      <div className="profile-content">
        {activeTab === 'profiles' && (
          <div className="profiles-section">
            {currentFarmer ? (
              <div className="current-farmer-profile">
                <div className="farmer-profile-header">
                  <div className="farmer-basic-info">
                    <h3>👨‍🌾 My Farmer Profile</h3>
                    <h2>{currentFarmer.name}</h2>
                    <p className="farmer-location">📍 {currentFarmer.location.village}, {currentFarmer.location.district}, {currentFarmer.location.state}</p>
                    <div className="verification-badge">
                      {getVerificationIcon(currentFarmer.verification_status)} 
                      <span className={`verification-text ${currentFarmer.verification_status.toLowerCase()}`}>
                        {currentFarmer.verification_status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="credit-score-main">
                    <div 
                      className="score-circle-large"
                      style={{ borderColor: getScoreColor(currentFarmer.agriculture_credit_score) }}
                    >
                      <span className="score-number-large">{currentFarmer.agriculture_credit_score}</span>
                      <span className="score-grade-large">{getScoreGrade(currentFarmer.agriculture_credit_score)}</span>
                    </div>
                    <div className="score-category-main">
                      {getCategoryEmoji(currentFarmer.score_category)} {currentFarmer.score_category.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                </div>

                {/* Farmer Position Widget */}
                {farmerPosition && (
                  <div className="farmer-position-widget">
                    <h3>🏆 Your Leaderboard Position</h3>
                    <div className="position-stats">
                      <div className="position-card">
                        <span className="position-rank">#{farmerPosition.rank}</span>
                        <span className="position-text">out of {farmerPosition.total_farmers} farmers</span>
                      </div>
                      <div className="position-card">
                        <span className="position-rank">{farmerPosition.percentile}%</span>
                        <span className="position-text">percentile</span>
                      </div>
                      {farmerPosition.improvement_needed.points_to_next_category > 0 && (
                        <div className="position-card improvement">
                          <span className="position-rank">+{farmerPosition.improvement_needed.points_to_next_category}</span>
                          <span className="position-text">points to next category</span>
                        </div>
                      )}
                      {farmerPosition.improvement_needed.farmers_ahead > 0 && (
                        <div className="position-card">
                          <span className="position-rank">{farmerPosition.improvement_needed.farmers_ahead}</span>
                          <span className="position-text">farmers ahead</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Farmer Insights Section */}
                {farmerInsights && (
                  <div className="farmer-insights-section">
                    <h3>💡 Personalized Insights</h3>
                    
                    <div className="insights-grid">
                      <div className="insights-card comparison-card">
                        <h4>📊 Score Comparison</h4>
                        <div className="comparison-stats">
                          <div className="comparison-item">
                            <span className="comparison-label">National Average:</span>
                            <span className="comparison-value">{farmerInsights.comparison.national_average.toFixed(0)}</span>
                            <span className={`comparison-indicator ${currentFarmer.agriculture_credit_score > farmerInsights.comparison.national_average ? 'positive' : 'negative'}`}>
                              {currentFarmer.agriculture_credit_score > farmerInsights.comparison.national_average ? '↗️' : '↘️'}
                            </span>
                          </div>
                          <div className="comparison-item">
                            <span className="comparison-label">State Average:</span>
                            <span className="comparison-value">{farmerInsights.comparison.state_average.toFixed(0)}</span>
                            <span className={`comparison-indicator ${currentFarmer.agriculture_credit_score > farmerInsights.comparison.state_average ? 'positive' : 'negative'}`}>
                              {currentFarmer.agriculture_credit_score > farmerInsights.comparison.state_average ? '↗️' : '↘️'}
                            </span>
                          </div>
                          <div className="comparison-item">
                            <span className="comparison-label">Top 10% Threshold:</span>
                            <span className="comparison-value">{farmerInsights.comparison.top_10_percent_threshold.toFixed(0)}</span>
                            <span className={`comparison-indicator ${currentFarmer.agriculture_credit_score >= farmerInsights.comparison.top_10_percent_threshold ? 'positive' : 'negative'}`}>
                              {currentFarmer.agriculture_credit_score >= farmerInsights.comparison.top_10_percent_threshold ? '🏆' : '🎯'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {farmerInsights.strengths.length > 0 && (
                        <div className="insights-card strengths-card">
                          <h4>💪 Your Strengths</h4>
                          <ul>
                            {farmerInsights.strengths.map((strength, index) => (
                              <li key={index}>✅ {strength}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {farmerInsights.improvement_areas.length > 0 && (
                        <div className="insights-card improvement-card">
                          <h4>🎯 Improvement Areas</h4>
                          <ul>
                            {farmerInsights.improvement_areas.map((area, index) => (
                              <li key={index}>🔸 {area}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {farmerInsights.recommendations.length > 0 && (
                        <div className="insights-card recommendations-card">
                          <h4>💡 Recommendations</h4>
                          <ul>
                            {farmerInsights.recommendations.map((rec, index) => (
                              <li key={index}>💡 {rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="farmer-stats-grid">
                  <div className="stat-card">
                    <h4>🚜 Farm Details</h4>
                    <p><strong>Farm Size:</strong> {currentFarmer.farm_size_hectares.toFixed(1)} hectares</p>
                    <p><strong>Experience:</strong> {currentFarmer.farming_experience}</p>
                    <p><strong>Primary Crops:</strong> {currentFarmer.primary_crops.join(', ')}</p>
                    <p><strong>Phone:</strong> {currentFarmer.phone}</p>
                  </div>

                  <div className="stat-card">
                    <h4>📊 Profile Status</h4>
                    <div className="profile-completeness-large">
                      <span>Profile Completeness</span>
                      <div className="progress-bar-large">
                        <div 
                          className="progress-fill-large"
                          style={{ width: `${currentFarmer.profile_completeness}%` }}
                        ></div>
                      </div>
                      <span className="completeness-percentage">{currentFarmer.profile_completeness.toFixed(0)}%</span>
                    </div>
                  </div>
                </div>

                {creditBreakdown && (
                  <div className="credit-breakdown-detailed">
                    <h3>� Detailed Credit Score Analysis</h3>
                    
                    <div className="components-grid-large">
                      {Object.entries(creditBreakdown.components).map(([key, component]) => (
                        <div key={key} className="component-card-large">
                          <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                          <div className="component-details">
                            <div className="component-score-large">
                              <span className="score-value">{component.score}</span>
                              <span className="score-weight">Weight: {component.weight}</span>
                            </div>
                            <span className={`status-badge status-${component.status.toLowerCase().replace(' ', '-')}`}>
                              {component.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="recommendations-grid">
                      <div className="recommendations-card strengths-card">
                        <h4>💪 Your Strengths</h4>
                        <ul>
                          {creditBreakdown.strengths.map((strength, index) => (
                            <li key={index}>✅ {strength}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="recommendations-card improvements-card">
                        <h4>🎯 Areas for Improvement</h4>
                        <ul>
                          {creditBreakdown.improvement_areas.map((area, index) => (
                            <li key={index}>🔸 {area}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="recommendations-card recommendations-actions">
                        <h4>💡 Recommendations</h4>
                        <ul>
                          {creditBreakdown.recommendations.map((rec, index) => (
                            <li key={index}>💡 {rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="next-review">
                      <p><strong>📅 Next Review Date:</strong> {new Date(creditBreakdown.next_review_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-farmer-message">
                <h3>⚠️ No Farmer Profile Found</h3>
                <p>Please ensure you are logged in and your profile is set up correctly.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="leaderboard-section">
            <div className="leaderboard-header">
              <h3>🏆 Top Farmers by Credit Score</h3>
              <div className="leaderboard-controls">
                <select 
                  value={selectedState} 
                  onChange={(e) => {
                    setSelectedState(e.target.value);
                    if (e.target.value) {
                      fetchRegionalLeaderboard(e.target.value);
                    } else {
                      fetchLeaderboard();
                    }
                  }}
                  className="state-filter"
                >
                  <option value="">All States</option>
                  <option value="Punjab">Punjab</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Haryana">Haryana</option>
                  <option value="Madhya Pradesh">Madhya Pradesh</option>
                </select>
              </div>
            </div>
            
            <div className="leaderboard-grid">
              {leaderboard.map((farmer, index) => (
                <div key={farmer.farmer_id} className={`leaderboard-item rank-${index + 1} ${farmer.farmer_id === currentFarmerId ? 'current-farmer' : ''}`}>
                  <div className="rank-badge">
                    {index === 0 && '🥇'}
                    {index === 1 && '🥈'}
                    {index === 2 && '🥉'}
                    {index >= 3 && `#${index + 1}`}
                  </div>
                  
                  <div className="farmer-info-leaderboard">
                    <h4>{farmer.name} {farmer.farmer_id === currentFarmerId && '(You)'}</h4>
                    <p>📍 {farmer.location}</p>
                    
                    <div className={`leaderboard-verification-badge ${farmer.verification_status.toLowerCase()}`}>
                      {getVerificationIcon(farmer.verification_status)} 
                      <span className="verification-text">{farmer.verification_status.replace('_', ' ')}</span>
                    </div>
                    
                    <p>🚜 {farmer.farming_experience}</p>
                    <p>🌱 {farmer.primary_crops.join(', ')}</p>
                    <div className="farmer-extra-info">
                      <span className="farm-size">🏡 {farmer.farm_size_hectares?.toFixed(1)} ha</span>
                      <span className="ndvi-score">🌿 NDVI: {farmer.ndvi_score?.toFixed(2)}</span>
                      <span className="profile-completeness">📊 {farmer.profile_completeness?.toFixed(0)}% complete</span>
                    </div>
                  </div>

                  <div className="score-display-leaderboard">
                    <span 
                      className="score-large"
                      style={{ color: getScoreColor(farmer.agriculture_credit_score) }}
                    >
                      {farmer.agriculture_credit_score}
                    </span>
                    <span className="category-badge">
                      {getCategoryEmoji(farmer.score_category)} {farmer.score_category.replace('_', ' ')}
                    </span>
                    <span className="score-grade">{getScoreGrade(farmer.agriculture_credit_score)}</span>
                  </div>
                </div>
              ))}
            </div>
            
            {leaderboard.length === 0 && (
              <div className="no-data-message">
                <h3>📭 No farmers found</h3>
                <p>Try selecting a different state or check back later.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="analytics-section">
            <h3>📊 Comprehensive Credit Score Analytics</h3>
            
            <div className="analytics-grid">
              <div className="analytics-card">
                <h4>👥 Total Farmers</h4>
                <span className="analytics-number">{analytics.total_farmers}</span>
              </div>

              <div className="analytics-card">
                <h4>📈 Average Score</h4>
                <span className="analytics-number">{analytics.average_score.toFixed(0)}</span>
              </div>

              <div className="analytics-card">
                <h4>📊 Median Score</h4>
                <span className="analytics-number">{analytics.median_score}</span>
              </div>

              <div className="analytics-card">
                <h4>🏆 Highest Score</h4>
                <span className="analytics-number">{analytics.highest_score}</span>
              </div>

              <div className="analytics-card">
                <h4>✅ Verified Farmers</h4>
                <span className="analytics-number">{analytics.verified_farmers}</span>
                <span className="analytics-percentage">({((analytics.verified_farmers / analytics.total_farmers) * 100).toFixed(1)}%)</span>
              </div>

              <div className="analytics-card">
                <h4>📉 Lowest Score</h4>
                <span className="analytics-number">{analytics.lowest_score}</span>
              </div>
            </div>

            {/* Score Percentiles */}
            <div className="percentiles-section">
              <h4>📊 Score Percentiles</h4>
              <div className="percentiles-grid">
                <div className="percentile-card">
                  <span className="percentile-label">25th Percentile</span>
                  <span className="percentile-value">{analytics.percentiles['25th']}</span>
                </div>
                <div className="percentile-card">
                  <span className="percentile-label">50th Percentile (Median)</span>
                  <span className="percentile-value">{analytics.percentiles['50th']}</span>
                </div>
                <div className="percentile-card">
                  <span className="percentile-label">75th Percentile</span>
                  <span className="percentile-value">{analytics.percentiles['75th']}</span>
                </div>
                <div className="percentile-card">
                  <span className="percentile-label">90th Percentile</span>
                  <span className="percentile-value">{analytics.percentiles['90th']}</span>
                </div>
              </div>
            </div>

            {/* Score Distribution */}
            <div className="score-distribution">
              <h4>Score Distribution by Category</h4>
              <div className="distribution-bars">
                {Object.entries(analytics.score_distribution).map(([category, count]) => (
                  <div key={category} className="distribution-item">
                    <span className="category-name">
                      {getCategoryEmoji(category)} {category.replace('_', ' ').toUpperCase()}
                    </span>
                    <div className="distribution-bar">
                      <div 
                        className="distribution-fill"
                        style={{ 
                          width: `${(count as number / analytics.total_farmers) * 100}%`,
                          backgroundColor: getScoreColor(category === 'excellent' ? 850 : category === 'very_good' ? 750 : category === 'good' ? 650 : category === 'fair' ? 550 : 450)
                        }}
                      ></div>
                    </div>
                    <span className="distribution-count">{count as number} ({((count as number / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                  </div>
                ))}
              </div>
            </div>

            {/* State-wise Distribution */}
            {analytics.state_wise_distribution && (
              <div className="state-distribution">
                <h4>State-wise Distribution</h4>
                <div className="state-grid">
                  {Object.entries(analytics.state_wise_distribution).map(([state, data]: [string, any]) => (
                    <div key={state} className="state-card">
                      <h5>{state}</h5>
                      <div className="state-stats">
                        <span className="state-stat">
                          <strong>Farmers:</strong> {data.count}
                        </span>
                        <span className="state-stat">
                          <strong>Avg Score:</strong> {data.avg_score.toFixed(0)}
                        </span>
                        <span className="state-stat">
                          <strong>Top Score:</strong> {data.top_score}
                        </span>
                        <span className="state-stat">
                          <strong>Verified:</strong> {data.verified_count} ({((data.verified_count / data.count) * 100).toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Technology Adoption Stats */}
            {analytics.technology_adoption_stats && (
              <div className="technology-stats">
                <h4>🔬 Technology Adoption Statistics</h4>
                <div className="tech-stats-grid">
                  <div className="tech-stat-card">
                    <span className="tech-stat-icon">🛰️</span>
                    <span className="tech-stat-label">Satellite Monitoring</span>
                    <span className="tech-stat-value">{analytics.technology_adoption_stats.satellite_monitoring}</span>
                    <span className="tech-stat-percentage">({((analytics.technology_adoption_stats.satellite_monitoring / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                  </div>
                  <div className="tech-stat-card">
                    <span className="tech-stat-icon">🤖</span>
                    <span className="tech-stat-label">AI Recommendations</span>
                    <span className="tech-stat-value">{analytics.technology_adoption_stats.ai_recommendations}</span>
                    <span className="tech-stat-percentage">({((analytics.technology_adoption_stats.ai_recommendations / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                  </div>
                  <div className="tech-stat-card">
                    <span className="tech-stat-icon">🎯</span>
                    <span className="tech-stat-label">Precision Agriculture</span>
                    <span className="tech-stat-value">{analytics.technology_adoption_stats.precision_agriculture}</span>
                    <span className="tech-stat-percentage">({((analytics.technology_adoption_stats.precision_agriculture / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                  </div>
                  <div className="tech-stat-card">
                    <span className="tech-stat-icon">🏪</span>
                    <span className="tech-stat-label">Digital Marketplace</span>
                    <span className="tech-stat-value">{analytics.technology_adoption_stats.digital_marketplace}</span>
                    <span className="tech-stat-percentage">({((analytics.technology_adoption_stats.digital_marketplace / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                  </div>
                </div>
              </div>
            )}

            {/* Farming Experience Distribution */}
            {analytics.farming_experience_distribution && (
              <div className="experience-distribution">
                <h4>👨‍🌾 Farming Experience Distribution</h4>
                <div className="experience-bars">
                  {Object.entries(analytics.farming_experience_distribution).map(([experience, count]) => (
                    <div key={experience} className="distribution-item">
                      <span className="category-name">
                        {experience.charAt(0).toUpperCase() + experience.slice(1)}
                      </span>
                      <div className="distribution-bar">
                        <div 
                          className="distribution-fill"
                          style={{ 
                            width: `${(count as number / analytics.total_farmers) * 100}%`,
                            backgroundColor: experience === 'veteran' ? '#27ae60' : experience === 'experienced' ? '#2ecc71' : experience === 'intermediate' ? '#f39c12' : '#e67e22'
                          }}
                        ></div>
                      </div>
                      <span className="distribution-count">{count as number} ({((count as number / analytics.total_farmers) * 100).toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FarmerProfilePage;
