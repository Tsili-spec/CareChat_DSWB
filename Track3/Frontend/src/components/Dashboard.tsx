import React, { useState, useEffect } from 'react';
import './Dashboard.css';

interface BloodInventoryItem {
  blood_group: string;
  total_available: number;
  total_near_expiry: number;
  total_expired: number;
  available_units: number;
  last_updated: string;
}

const Dashboard: React.FC = () => {
  const [inventory, setInventory] = useState<BloodInventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/inventory', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch inventory data');
      }

      const data = await response.json();
      setInventory(data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
      setError(error instanceof Error ? error.message : 'Failed to load inventory');
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

  const navigateToForecasting = () => {
    window.location.href = '/forecasting';
  };

  const navigateToDashboard = () => {
    window.location.href = '/dashboard';
  };

  const navigateToFeedbackAnalytics = () => {
    window.location.href = '/feedback-analytics';
  };


  const getTimeToExpiryPercentage = (nearExpiry: number, total: number): number => {
    if (total === 0) return 0;
    return Math.round(((total - nearExpiry) / total) * 100);
  };

  const getBloodTypeIcon = (): string => {
    return '🩸'; // Blood drop emoji for all types
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo" onClick={navigateToDashboard} style={{ cursor: 'pointer' }} title="Dashboard Home">
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
          <div className="menu-item active" onClick={navigateToDashboard} title="Dashboard">
            <span className="menu-icon">🏠</span>
          </div>
          <div className="menu-item" onClick={navigateToForecasting} title="Forecasting">
            <span className="menu-icon">📊</span>
          </div>
          <div className="menu-item" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
            <span className="menu-icon">📈</span>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="menu-item logout" onClick={handleLogout}>
            <span className="menu-icon">🚪</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <div className="header">
          <div className="search-container">
            <input 
              type="text" 
              placeholder="Search..." 
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
          
          <div className="header-actions">
            <div className="language-selector">
              <span className="flag">🇺🇸</span>
              <span>English</span>
              <span className="dropdown-arrow">▼</span>
            </div>
            <div className="settings-icon">⚙️</div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-container">
          <div className="filter-group">
            <select className="filter-select">
              <option>Date Range</option>
            </select>
            <span className="filter-arrow">▼</span>
          </div>
          
          <div className="filter-group">
            <select className="filter-select">
              <option>Blood Type</option>
            </select>
            <span className="filter-arrow">▼</span>
          </div>
          
          <div className="filter-group">
            <select className="filter-select">
              <option>Location</option>
            </select>
            <span className="filter-arrow">▼</span>
          </div>
          
          <button className="reset-filters">Reset Filters</button>
          <button className="export-report">Export Report</button>
        </div>

        {/* Stock Overview */}
        <div className="content">
          <h2 className="page-title">Stock Overview</h2>
          
          <div className="blood-cards-grid">
            {inventory.map((item) => (
              <div key={item.blood_group} className="blood-card">
                <div className="blood-card-header">
                  <div className="blood-icon">
                    {getBloodTypeIcon()}
                  </div>
                  <div className="blood-type">
                    {item.blood_group}
                  </div>
                </div>
                
                <div className="units-info">
                  <div className="total-units">{item.available_units} UNITS</div>
                </div>
                
                <div className="status-bars">
                  <div className="status-item available">
                    <span className="status-count">{Math.round(item.total_available / 1000)}k Available</span>
                    <span className="status-count reserved">{Math.round(item.total_near_expiry / 1000)}k reserved</span>
                  </div>
                </div>
                
                <div className="status-bars">
                  <div className="status-item near-expiry">
                    <span className="status-count">{Math.round(item.total_near_expiry / 1000)}k Near Expiry</span>
                    <span className="status-count expired">{Math.round(item.total_expired / 1000)}k Expired</span>
                  </div>
                </div>
                
                <div className="expiry-info">
                  <div className="expiry-label">Time to Expiry</div>
                  <div className="expiry-percentage">{getTimeToExpiryPercentage(item.total_near_expiry, item.total_available)}%</div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${getTimeToExpiryPercentage(item.total_near_expiry, item.total_available)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
