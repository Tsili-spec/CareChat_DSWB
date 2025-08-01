import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Activity, Calendar } from 'lucide-react';
import './Forecasting.css';

interface BloodTypeVolume {
  blood_type: string;
  donated_volume: number;
  used_volume: number;
}

interface VolumeResponse {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  summary: {
    total_donated: number;
    total_used: number;
  };
  blood_types: BloodTypeVolume[];
}

const Forecasting: React.FC = () => {
  const [volumeData, setVolumeData] = useState<VolumeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState<'welcome' | 'monitoring'>('welcome');

  useEffect(() => {
    if (currentView === 'monitoring') {
      fetchVolumeData();
    }
  }, [currentView]);

  const fetchVolumeData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(
        'https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/volume-by-blood-type?days=365',
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch volume data');
      }

      const data = await response.json();
      setVolumeData(data);
    } catch (error) {
      console.error('Error fetching volume data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load volume data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userData');
    window.location.href = '/';
  };

  const navigateToAddSample = () => {
    window.location.href = '/add-sample';
  };

  const navigateToBloodUsage = () => {
    window.location.href = '/blood-usage';
  };

  const navigateToDashboard = () => {
    window.location.href = '/dashboard';
  };

  const showMonitoringView = () => {
    setCurrentView('monitoring');
  };

  const showWelcomeView = () => {
    setCurrentView('welcome');
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return Math.round(num).toString();
  };

  const renderWelcomeView = () => (
    <div className="welcome-container">
      <div className="welcome-header">
        <TrendingUp size={48} className="welcome-icon" />
        <h1 className="welcome-title">Welcome to Forecasting</h1>
        <p className="welcome-subtitle">
          Advanced analytics and predictions for blood bank inventory management
        </p>
      </div>
      
      <div className="feature-grid">
        <div className="feature-card">
          <BarChart3 size={32} className="feature-icon" />
          <h3>Volume Analytics</h3>
          <p>Track donation and usage patterns by blood type</p>
        </div>
        
        <div className="feature-card clickable" onClick={showMonitoringView}>
          <Activity size={32} className="feature-icon" />
          <h3>Real-time Monitoring</h3>
          <p>Monitor current inventory levels and status</p>
          <div className="click-indicator">
            <span>Click to view detailed charts →</span>
          </div>
        </div>
        
        <div className="feature-card">
          <Calendar size={32} className="feature-icon" />
          <h3>Predictive Insights</h3>
          <p>Forecast future needs and optimize ordering</p>
        </div>
        
        <div className="feature-card">
          <TrendingUp size={32} className="feature-icon" />
          <h3>Trend Analysis</h3>
          <p>Identify patterns and seasonal variations</p>
        </div>
      </div>
      
      <div className="coming-soon">
        <p>🚀 Advanced forecasting features coming soon!</p>
      </div>
    </div>
  );

  const renderMonitoringView = () => (
    <div className="monitoring-view">
      <div className="monitoring-header">
        <button className="back-button" onClick={showWelcomeView}>
          ← Back to Overview
        </button>
        <div className="monitoring-title">
          <Activity size={32} className="monitoring-icon" />
          <h1>Real-time Blood Bank Monitoring</h1>
        </div>
      </div>

      <div className="monitoring-content">
        {loading ? (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>Loading monitoring data...</p>
          </div>
        ) : error ? (
          <div className="chart-error">
            <p>Error: {error}</p>
            <button onClick={fetchVolumeData} className="retry-btn">Retry</button>
          </div>
        ) : volumeData ? (
          <div className="blood-volume-chart">
            <div className="chart-header">
              <h2>Total Volume by Blood Type (Donation vs Usage)</h2>
            </div>
            
            <div className="chart-summary">
              <div className="summary-item">
                <span className="summary-label">Total Donated:</span>
                <span className="summary-value donated">{formatNumber(volumeData.summary.total_donated)} ml</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Total Used:</span>
                <span className="summary-value used">{formatNumber(volumeData.summary.total_used)} ml</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Net Balance:</span>
                <span className={`summary-value ${volumeData.summary.total_donated >= volumeData.summary.total_used ? 'positive' : 'negative'}`}>
                  {formatNumber(volumeData.summary.total_donated - volumeData.summary.total_used)} ml
                </span>
              </div>
            </div>
            
            <div className="chart-bars">
              <div className="y-axis-title">Volume (ml)</div>
              
              {volumeData.blood_types.map((bloodType) => {
                // Calculate bar heights based on larger chart height (500px available for bars)
                const chartHeight = 500;
                const maxVolume = 2000000; // 2M as max scale
                
                return (
                  <div key={bloodType.blood_type} className="bar-group">
                    <div className="bar-pair">
                      <div 
                        className="bar donation"
                        style={{ 
                          height: `${Math.min((bloodType.donated_volume / maxVolume) * chartHeight, chartHeight)}px`
                        }}
                        title={`Donated: ${formatNumber(bloodType.donated_volume)} ml`}
                      ></div>
                      <div 
                        className="bar usage"
                        style={{ 
                          height: `${Math.min((bloodType.used_volume / maxVolume) * chartHeight, chartHeight)}px`
                        }}
                        title={`Used: ${formatNumber(bloodType.used_volume)} ml`}
                      ></div>
                    </div>
                    <div className="blood-type-label">
                      {bloodType.blood_type}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-box legend-donated"></div>
                Donation Volume
              </div>
              <div className="legend-item">
                <div className="legend-box legend-used"></div>
                Usage Volume
              </div>
            </div>

            <div className="x-axis-title">blood_type</div>
          </div>
        ) : null}
      </div>
    </div>
  );

  return (
    <div className="forecasting-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            🏠
          </div>
        </div>
        
        <div className="sidebar-menu">
          <div className="menu-item" onClick={navigateToAddSample} title="Add Sample">
            <span className="menu-icon">+</span>
          </div>
          <div className="menu-item" onClick={navigateToBloodUsage} title="Blood Usage">
            <span className="menu-icon">🩸</span>
          </div>
          <div className="menu-item" onClick={navigateToDashboard} title="Dashboard">
            <span className="menu-icon">🏠</span>
          </div>
          <div className="menu-item active" title="Forecasting">
            <TrendingUp className="menu-icon" size={20} />
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="menu-item logout" onClick={handleLogout} title="Logout">
            <span className="menu-icon">🚪</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {currentView === 'welcome' ? renderWelcomeView() : renderMonitoringView()}
      </div>
    </div>
  );
};

export default Forecasting;
