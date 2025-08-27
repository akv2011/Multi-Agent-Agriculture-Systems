import React, { useState } from 'react';
import './ReportsPage.css';

// Define types for report data
interface ReportData {
  id: string;
  title: string;
  description: string;
  createdAt: string;
  category: 'crop' | 'irrigation' | 'soil' | 'harvest' | 'market' | 'financial';
  status: 'generated' | 'pending' | 'failed';
  fileSize?: string;
  generatedBy?: string;
  lastViewed?: string;
  downloadUrl?: string;
  thumbnail?: string;
}

const ReportsPage: React.FC = () => {
  // Sample report data
  const sampleReports: ReportData[] = [
    {
      id: 'rep-001',
      title: 'Annual Crop Yield Analysis',
      description: 'Comprehensive analysis of crop yields across all fields with year-over-year comparison',
      createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'crop',
      status: 'generated',
      fileSize: '4.2 MB',
      generatedBy: 'Reporting Agent',
      lastViewed: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '📊'
    },
    {
      id: 'rep-002',
      title: 'Irrigation Efficiency Report',
      description: 'Analysis of water usage efficiency and irrigation system performance for Q2',
      createdAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'irrigation',
      status: 'generated',
      fileSize: '2.8 MB',
      generatedBy: 'Water Management Agent',
      lastViewed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '💧'
    },
    {
      id: 'rep-003',
      title: 'Soil Health Assessment',
      description: 'Detailed analysis of soil composition, nutrient levels, and pH balance across all fields',
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'soil',
      status: 'generated',
      fileSize: '5.7 MB',
      generatedBy: 'Soil Analysis Agent',
      lastViewed: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '🌱'
    },
    {
      id: 'rep-004',
      title: 'Market Price Forecast',
      description: 'Predictive analysis of market prices for primary crops over the next quarter',
      createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'market',
      status: 'generated',
      fileSize: '1.9 MB',
      generatedBy: 'Market Analysis Agent',
      lastViewed: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '📈'
    },
    {
      id: 'rep-005',
      title: 'Pest Control Effectiveness',
      description: 'Analysis of pest control measures and their impact on crop health',
      createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'crop',
      status: 'generated',
      fileSize: '3.5 MB',
      generatedBy: 'Pest Control Agent',
      lastViewed: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '🐞'
    },
    {
      id: 'rep-006',
      title: 'Financial Performance Q2',
      description: 'Financial analysis including expenses, revenue, and profit margins for Q2 2023',
      createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'financial',
      status: 'generated',
      fileSize: '2.2 MB',
      generatedBy: 'Financial Agent',
      lastViewed: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '💰'
    },
    {
      id: 'rep-007',
      title: 'Harvest Efficiency Report',
      description: 'Analysis of harvest timing, equipment efficiency, and crop quality assessment',
      createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
      category: 'harvest',
      status: 'generated',
      fileSize: '4.1 MB',
      generatedBy: 'Harvest Operations Agent',
      lastViewed: new Date(Date.now() - 85 * 24 * 60 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '🚜'
    },
    {
      id: 'rep-008',
      title: 'Weather Impact Analysis',
      description: 'Analysis of weather patterns and their impact on crop yields',
      createdAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      category: 'crop',
      status: 'generated',
      fileSize: '3.1 MB',
      generatedBy: 'Climate Analysis Agent',
      lastViewed: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '☁️'
    },
    {
      id: 'rep-009',
      title: 'Equipment Maintenance Report',
      description: 'Status report on agricultural equipment maintenance and repair needs',
      createdAt: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      category: 'harvest',
      status: 'generated',
      fileSize: '2.3 MB',
      generatedBy: 'Equipment Monitoring Agent',
      lastViewed: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      downloadUrl: '#',
      thumbnail: '🔧'
    }
  ];

  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('date');
  const [selectedReport, setSelectedReport] = useState<ReportData | null>(null);

  // Filter and sort reports
  const filteredReports = sampleReports
    .filter(report => {
      // Filter by category
      if (selectedCategory !== 'all' && report.category !== selectedCategory) {
        return false;
      }
      
      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!(report.title.toLowerCase().includes(query) ||
              report.description.toLowerCase().includes(query))) {
          return false;
        }
      }
      
      return true;
    })
    .sort((a, b) => {
      // Sort reports
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'name':
          return a.title.localeCompare(b.title);
        case 'category':
          return a.category.localeCompare(b.category);
        default:
          return 0;
      }
    });

  const handleReportClick = (report: ReportData) => {
    setSelectedReport(report);
  };

  const handleGenerateReport = () => {
    // Handle report generation
    alert('Report generation feature will be implemented soon!');
  };

  const handleDownloadReport = (e: React.MouseEvent<HTMLButtonElement>, report: ReportData) => {
    e.stopPropagation();
    // Handle report download
    alert(`Downloading report: ${report.title}`);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'crop': return '🌾';
      case 'irrigation': return '💧';
      case 'soil': return '🌱';
      case 'harvest': return '🚜';
      case 'market': return '📈';
      case 'financial': return '💰';
      default: return '📄';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getStatusClass = (status: ReportData['status']) => {
    switch (status) {
      case 'generated': return 'status-generated';
      case 'pending': return 'status-pending';
      case 'failed': return 'status-failed';
      default: return '';
    }
  };

  return (
    <div className="reports-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Reports</h1>
          <p>Generate and manage agricultural analytics reports</p>
        </div>
        <div className="header-actions">
          <button className="btn-primary" onClick={handleGenerateReport}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            Generate New Report
          </button>
        </div>
      </div>

      <div className="filter-section">
        <div className="search-container">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="search-icon">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
          <input 
            type="text" 
            placeholder="Search reports..." 
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-options">
          <div className="filter-group">
            <label>Category:</label>
            <select 
              className="filter-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              <option value="crop">Crop</option>
              <option value="irrigation">Irrigation</option>
              <option value="soil">Soil</option>
              <option value="harvest">Harvest</option>
              <option value="market">Market</option>
              <option value="financial">Financial</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Sort By:</label>
            <select 
              className="filter-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="date">Date (Newest)</option>
              <option value="name">Name (A-Z)</option>
              <option value="category">Category</option>
            </select>
          </div>
        </div>
      </div>

      <div className="reports-content">
        {/* Reports Grid */}
        <div className="reports-grid">
          {filteredReports.length > 0 ? (
            filteredReports.map(report => (
              <div 
                key={report.id}
                className={`report-card ${report.status === 'failed' ? 'failed' : ''} ${selectedReport?.id === report.id ? 'selected' : ''}`}
                onClick={() => handleReportClick(report)}
              >
                <div className="report-icon">
                  <span>{report.thumbnail || getCategoryIcon(report.category)}</span>
                </div>
                <div className="report-content">
                  <div className="report-header">
                    <h3>{report.title}</h3>
                    <span className={`report-status ${getStatusClass(report.status)}`}>
                      {report.status}
                    </span>
                  </div>
                  <p className="report-description">{report.description}</p>
                  <div className="report-meta">
                    <span className="report-category">
                      {getCategoryIcon(report.category)} {report.category}
                    </span>
                    <span className="report-date">
                      Generated: {formatDate(report.createdAt)}
                    </span>
                  </div>
                </div>
                <div className="report-actions">
                  {report.status === 'generated' && (
                    <button 
                      className="download-button"
                      onClick={(e) => handleDownloadReport(e, report)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Download
                    </button>
                  )}
                  {report.status === 'pending' && (
                    <div className="pending-indicator">
                      <div className="spinner"></div>
                      <span>Processing...</span>
                    </div>
                  )}
                  {report.status === 'failed' && (
                    <button className="retry-button">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clipRule="evenodd" />
                      </svg>
                      Retry
                    </button>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="no-reports">
              <div className="no-reports-icon">📄</div>
              <h3>No reports found</h3>
              <p>Try adjusting your filters or create a new report</p>
            </div>
          )}
        </div>

        {/* Report Detail Panel */}
        {selectedReport && (
          <div className="report-detail-panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="report-detail-icon">{selectedReport.thumbnail || getCategoryIcon(selectedReport.category)}</span>
                <h2>{selectedReport.title}</h2>
              </div>
              <div className={`status-badge ${getStatusClass(selectedReport.status)}`}>
                {selectedReport.status}
              </div>
            </div>

            <div className="report-detail-content">
              <div className="detail-section">
                <h3>Description</h3>
                <p>{selectedReport.description}</p>
              </div>

              <div className="detail-section">
                <h3>Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Report ID</span>
                    <span className="detail-value">{selectedReport.id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Category</span>
                    <span className="detail-value">
                      {getCategoryIcon(selectedReport.category)} {selectedReport.category}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Created On</span>
                    <span className="detail-value">{formatDate(selectedReport.createdAt)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Generated By</span>
                    <span className="detail-value">{selectedReport.generatedBy || 'Unknown'}</span>
                  </div>
                  {selectedReport.fileSize && (
                    <div className="detail-item">
                      <span className="detail-label">File Size</span>
                      <span className="detail-value">{selectedReport.fileSize}</span>
                    </div>
                  )}
                  {selectedReport.lastViewed && (
                    <div className="detail-item">
                      <span className="detail-label">Last Viewed</span>
                      <span className="detail-value">{formatDate(selectedReport.lastViewed)}</span>
                    </div>
                  )}
                </div>
              </div>

              {selectedReport.status === 'generated' && (
                <div className="detail-section">
                  <h3>Preview</h3>
                  <div className="report-preview">
                    {/* This would be a preview of the report content */}
                    <div className="report-placeholder">
                      <div className="placeholder-icon">📊</div>
                      <p>Report preview available</p>
                    </div>
                  </div>
                </div>
              )}

              {selectedReport.status === 'pending' && (
                <div className="detail-section">
                  <h3>Processing</h3>
                  <div className="report-processing">
                    <div className="processing-animation">
                      <div className="processing-spinner"></div>
                    </div>
                    <p>Your report is being generated. This may take a few minutes.</p>
                  </div>
                </div>
              )}

              {selectedReport.status === 'failed' && (
                <div className="detail-section">
                  <h3>Error Information</h3>
                  <div className="report-error">
                    <div className="error-icon">❌</div>
                    <div className="error-details">
                      <p className="error-message">Report generation failed. The system encountered an error while processing data.</p>
                      <p className="error-suggestion">You can try generating the report again or contact support if the issue persists.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="panel-actions">
              {selectedReport.status === 'generated' && (
                <>
                  <button className="action-button primary">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Download Report
                  </button>
                  <button className="action-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M3.75 2A1.75 1.75 0 002 3.75v3.5C2 8.216 2.784 9 3.75 9h3.5A1.75 1.75 0 009 7.25v-3.5A1.75 1.75 0 007.25 2h-3.5zM3.5 3.75a.25.25 0 01.25-.25h3.5a.25.25 0 01.25.25v3.5a.25.25 0 01-.25.25h-3.5a.25.25 0 01-.25-.25v-3.5zM3.75 11A1.75 1.75 0 002 12.75v3.5c0 .966.784 1.75 1.75 1.75h3.5A1.75 1.75 0 009 16.25v-3.5A1.75 1.75 0 007.25 11h-3.5zm-.25 1.75a.25.25 0 01.25-.25h3.5a.25.25 0 01.25.25v3.5a.25.25 0 01-.25.25h-3.5a.25.25 0 01-.25-.25v-3.5zm7.5-9a.25.25 0 01.25-.25h3.5a.25.25 0 01.25.25v3.5a.25.25 0 01-.25.25h-3.5a.25.25 0 01-.25-.25v-3.5zM11.75 2A1.75 1.75 0 0010 3.75v3.5A1.75 1.75 0 0011.75 9h3.5A1.75 1.75 0 0017 7.25v-3.5A1.75 1.75 0 0015.25 2h-3.5zm0 9A1.75 1.75 0 0010 12.75v3.5c0 .966.784 1.75 1.75 1.75h3.5A1.75 1.75 0 0017 16.25v-3.5A1.75 1.75 0 0015.25 11h-3.5zm-.25 1.75a.25.25 0 01.25-.25h3.5a.25.25 0 01.25.25v3.5a.25.25 0 01-.25.25h-3.5a.25.25 0 01-.25-.25v-3.5z" clipRule="evenodd" />
                    </svg>
                    View Full Screen
                  </button>
                  <button className="action-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                    Export as PDF
                  </button>
                </>
              )}
              
              {selectedReport.status === 'pending' && (
                <button className="action-button warning">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  Cancel Generation
                </button>
              )}
              
              {selectedReport.status === 'failed' && (
                <button className="action-button primary">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clipRule="evenodd" />
                  </svg>
                  Retry Generation
                </button>
              )}
              
              <button className="action-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Delete Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
