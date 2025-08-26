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
}

const FarmerProfilePage: React.FC = () => {
  const [farmers, setFarmers] = useState<FarmerProfile[]>([]);
  const [selectedFarmer, setSelectedFarmer] = useState<FarmerProfile | null>(null);
  const [creditBreakdown, setCreditBreakdown] = useState<CreditScoreBreakdown | null>(null);
  const [leaderboard, setLeaderboard] = useState<FarmerLeaderboard[]>([]);
  const [activeTab, setActiveTab] = useState<'profiles' | 'leaderboard' | 'analytics'>('profiles');
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    fetchFarmers();
    fetchLeaderboard();
    fetchAnalytics();
  }, []);

  const fetchFarmers = async () => {
    try {
      const response = await fetch('http://localhost:8003/farmer-profiles');
      const data = await response.json();
      setFarmers(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching farmers:', error);
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('http://localhost:8003/farmer-leaderboard');
      const data = await response.json();
      setLeaderboard(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8003/credit-score-analytics');
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchCreditBreakdown = async (farmerId: string) => {
    try {
      const response = await fetch(`http://localhost:8003/farmer-profile/${farmerId}/credit-score`);
      const data = await response.json();
      setCreditBreakdown(data);
    } catch (error) {
      console.error('Error fetching credit breakdown:', error);
    }
  };

  const handleFarmerSelect = (farmer: FarmerProfile) => {
    setSelectedFarmer(farmer);
    fetchCreditBreakdown(farmer.farmer_id);
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
            <div className="farmers-grid">
              <div className="farmers-list">
                <h3>All Farmers ({farmers.length})</h3>
                <div className="farmer-cards">
                  {farmers.map(farmer => (
                    <div 
                      key={farmer.farmer_id}
                      className={`farmer-card ${selectedFarmer?.farmer_id === farmer.farmer_id ? 'selected' : ''}`}
                      onClick={() => handleFarmerSelect(farmer)}
                    >
                      <div className="farmer-card-header">
                        <h4>{farmer.name}</h4>
                        <span className="verification-status">
                          {getVerificationIcon(farmer.verification_status)}
                        </span>
                      </div>
                      
                      <div className="credit-score-display">
                        <div 
                          className="score-circle"
                          style={{ borderColor: getScoreColor(farmer.agriculture_credit_score) }}
                        >
                          <span className="score-number">{farmer.agriculture_credit_score}</span>
                          <span className="score-grade">{getScoreGrade(farmer.agriculture_credit_score)}</span>
                        </div>
                        <div className="score-info">
                          <span className="score-category">
                            {getCategoryEmoji(farmer.score_category)} {farmer.score_category.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                      </div>

                      <div className="farmer-info">
                        <p>📍 {farmer.location.district}, {farmer.location.state}</p>
                        <p>🌾 {farmer.farming_experience}</p>
                        <p>🚜 {farmer.farm_size_hectares} hectares</p>
                        <p>🌱 {farmer.primary_crops.join(', ')}</p>
                      </div>

                      <div className="profile-completeness">
                        <span>Profile: {farmer.profile_completeness.toFixed(0)}% complete</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill"
                            style={{ width: `${farmer.profile_completeness}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="farmer-details">
                {selectedFarmer ? (
                  <div className="farmer-detail-card">
                    <h3>📋 Detailed Credit Analysis</h3>
                    <h4>{selectedFarmer.name}</h4>
                    
                    <div className="score-breakdown-header">
                      <div className="main-score">
                        <span className="large-score">{selectedFarmer.agriculture_credit_score}</span>
                        <span className="score-category-text">
                          {getCategoryEmoji(selectedFarmer.score_category)} {selectedFarmer.score_category.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {creditBreakdown && (
                      <div className="credit-breakdown">
                        <h5>📊 Score Components</h5>
                        <div className="components-grid">
                          {Object.entries(creditBreakdown.components).map(([key, component]) => (
                            <div key={key} className="component-card">
                              <h6>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
                              <div className="component-score">
                                <span className="component-value">{component.score}</span>
                                <span className="component-weight">Weight: {component.weight}</span>
                              </div>
                              <span className={`component-status status-${component.status.toLowerCase().replace(' ', '-')}`}>
                                {component.status}
                              </span>
                            </div>
                          ))}
                        </div>

                        <div className="recommendations-section">
                          <div className="strengths">
                            <h6>💪 Strengths</h6>
                            <ul>
                              {creditBreakdown.strengths.map((strength, index) => (
                                <li key={index}>✅ {strength}</li>
                              ))}
                            </ul>
                          </div>

                          <div className="improvements">
                            <h6>🎯 Areas for Improvement</h6>
                            <ul>
                              {creditBreakdown.improvement_areas.map((area, index) => (
                                <li key={index}>🔸 {area}</li>
                              ))}
                            </ul>
                          </div>

                          <div className="recommendations">
                            <h6>💡 Recommendations</h6>
                            <ul>
                              {creditBreakdown.recommendations.map((rec, index) => (
                                <li key={index}>🚀 {rec}</li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        <div className="next-review">
                          <p>📅 Next Review: {new Date(creditBreakdown.next_review_date).toLocaleDateString()}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="no-selection">
                    <h3>👈 Select a farmer to view detailed credit analysis</h3>
                    <p>Click on any farmer card to see their complete agricultural credit score breakdown, including satellite performance metrics, crop history, and personalized recommendations.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="leaderboard-section">
            <h3>🏆 Top Farmers by Credit Score</h3>
            <div className="leaderboard-grid">
              {leaderboard.map((farmer, index) => (
                <div key={farmer.farmer_id} className={`leaderboard-item rank-${index + 1}`}>
                  <div className="rank-badge">
                    {index === 0 && '🥇'}
                    {index === 1 && '🥈'}
                    {index === 2 && '🥉'}
                    {index >= 3 && `#${index + 1}`}
                  </div>
                  
                  <div className="farmer-info-leaderboard">
                    <h4>{farmer.name}</h4>
                    <p>📍 {farmer.location}</p>
                    <p>🌾 {farmer.farming_experience}</p>
                    <p>🌱 {farmer.primary_crops.join(', ')}</p>
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
                  </div>

                  <div className="verification-badge">
                    {getVerificationIcon(farmer.verification_status)} {farmer.verification_status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="analytics-section">
            <h3>📊 Credit Score Analytics</h3>
            
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
                <h4>🏆 Highest Score</h4>
                <span className="analytics-number">{analytics.highest_score}</span>
              </div>

              <div className="analytics-card">
                <h4>✅ Verified Farmers</h4>
                <span className="analytics-number">{analytics.verified_farmers}</span>
              </div>
            </div>

            <div className="score-distribution">
              <h4>Score Distribution</h4>
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
                    <span className="distribution-count">{count as number}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FarmerProfilePage;
