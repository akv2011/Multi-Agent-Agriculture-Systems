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
  // Mock current logged-in farmer ID (in real app, this would come from authentication)
  const currentFarmerId = 'FARMER_45690318'; // Rajesh Kumar Singh
  
  const [currentFarmer, setCurrentFarmer] = useState<FarmerProfile | null>(null);
  const [creditBreakdown, setCreditBreakdown] = useState<CreditScoreBreakdown | null>(null);
  const [leaderboard, setLeaderboard] = useState<FarmerLeaderboard[]>([]);
  const [activeTab, setActiveTab] = useState<'profiles' | 'leaderboard' | 'analytics'>('profiles');
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    fetchCurrentFarmer();
    fetchLeaderboard();
    fetchAnalytics();
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
      const response = await fetch('http://localhost:8000/farmer-leaderboard');
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

  const fetchCreditBreakdown = async (farmerId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/farmer-profile/${farmerId}/credit-score`);
      const data = await response.json();
      setCreditBreakdown(data);
    } catch (error) {
      console.error('Error fetching credit breakdown:', error);
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
