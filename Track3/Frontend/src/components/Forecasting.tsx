import React, { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Activity, Calendar } from 'lucide-react';
import './Forecasting.css';
import './Dashboard.css';

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

interface BloodTypeTrend {
  dates: string[];
  donated_volume: number[];
  used_volume: number[];
  stock_volume: number[];
}

interface TrendsResponse {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  blood_types: string[];
  trends: {
    [bloodType: string]: BloodTypeTrend;
  };
}

interface DailyData {
  date: string;
  daily_donated: number;
  daily_used: number;
}

interface TotalVolumeResponse {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  daily_data: DailyData[];
}

interface UsageStatistics {
  avg_daily_usage: number;
  trend: number;
  data_points: number;
  variance: number;
}

interface BloodTypeRecommendation {
  blood_type: string;
  current_stock_ml: number;
  forecasted_daily_demand_ml: number;
  safety_stock_ml: number;
  recommended_order_ml: number;
  usage_statistics: UsageStatistics;
}

interface InventoryOptimizationResponse {
  parameters: {
    service_level: number;
    service_level_percentage: number;
    z_score: number;
    lead_time_days: number;
    max_order_limit: number;
  };
  blood_type_recommendations: BloodTypeRecommendation[];
  timestamp: string;
}

const Forecasting: React.FC = () => {
  const [volumeData, setVolumeData] = useState<VolumeResponse | null>(null);
  const [trendsData, setTrendsData] = useState<TrendsResponse | null>(null);
  const [totalVolumeData, setTotalVolumeData] = useState<TotalVolumeResponse | null>(null);
  const [inventoryData, setInventoryData] = useState<InventoryOptimizationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState<'welcome' | 'monitoring' | 'trends' | 'trendAnalysis' | 'predictive'>('welcome');
  const [selectedBloodTypes, setSelectedBloodTypes] = useState<string[]>(['A+', 'B+', 'AB+', 'O+']);
  const [days, setDays] = useState(90);
  const [forecastDays, setForecastDays] = useState(30);
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [leadTimeDays, setLeadTimeDays] = useState(14);
  const [maxOrderLimit, setMaxOrderLimit] = useState(1000);

  useEffect(() => {
    if (currentView === 'monitoring') {
      fetchVolumeData();
    } else if (currentView === 'trends') {
      fetchTrendsData();
    } else if (currentView === 'trendAnalysis') {
      fetchTotalVolumeData();
    } else if (currentView === 'predictive') {
      fetchInventoryOptimization();
    }
  }, [currentView, selectedBloodTypes, days, forecastDays, serviceLevel, leadTimeDays, maxOrderLimit]);

  // Initial load effect for predictive view
  useEffect(() => {
    if (currentView === 'predictive' && !inventoryData) {
      fetchInventoryOptimization();
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

  const fetchTrendsData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const bloodTypesQuery = selectedBloodTypes.map(type => `blood_types=${encodeURIComponent(type)}`).join('&');
      const response = await fetch(
        `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/daily-volume-trends?days=${days}&${bloodTypesQuery}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch trends data');
      }

      const data = await response.json();
      setTrendsData(data);
    } catch (error) {
      console.error('Error fetching trends data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load trends data');
    } finally {
      setLoading(false);
    }
  };

  const fetchTotalVolumeData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(
        `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/daily-total-volume?days=${days}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch total volume data');
      }

      const data = await response.json();
      setTotalVolumeData(data);
    } catch (error) {
      console.error('Error fetching total volume data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load total volume data');
    } finally {
      setLoading(false);
    }
  };

  const fetchInventoryOptimization = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(
        `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/inventory-optimization?forecast_days=${forecastDays}&service_level=${serviceLevel}&lead_time_days=${leadTimeDays}&max_order_limit=${maxOrderLimit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch inventory optimization data');
      }

      const data = await response.json();
      setInventoryData(data);
    } catch (error) {
      console.error('Error fetching inventory optimization data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load inventory optimization data');
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

  const navigateToForecasting = () => {
    window.location.href = '/forecasting';
  };

  const navigateToFeedbackAnalytics = () => {
    window.location.href = '/feedback-analytics';
  };

  const showMonitoringView = () => {
    setCurrentView('monitoring');
  };

  const showTrendsView = () => {
    setCurrentView('trends');
  };

  const showTrendAnalysisView = () => {
    setCurrentView('trendAnalysis');
  };

  const showPredictiveView = () => {
    setCurrentView('predictive');
  };

  const showWelcomeView = () => {
    setCurrentView('welcome');
  };

  const renderPredictiveView = () => {
    // Add debugging
    console.log('renderPredictiveView called, inventoryData:', inventoryData);
    console.log('loading:', loading, 'error:', error);
    
    return (
      <div className="predictive-view">
        {/* Header */}
        <div className="predictive-header">
          <button className="back-button" onClick={() => setCurrentView('welcome')}>
            ← Back to Overview
          </button>
          <div className="header-content">
            <h1>Inventory Optimization Dashboard</h1>
          </div>
        </div>

        {/* API Parameters Controls */}
        <div className="forecast-controls">
          <h3>Optimization Parameters</h3>
          
          <div className="parameters-row">
            <div className="parameter-group-inline">
              <label>Forecast (days):</label>
              <div className="inline-controls">
                <button 
                  className={`forecast-btn-small ${forecastDays === 7 ? 'active' : ''}`}
                  onClick={() => setForecastDays(7)}
                >
                  7
                </button>
                <button 
                  className={`forecast-btn-small ${forecastDays === 14 ? 'active' : ''}`}
                  onClick={() => setForecastDays(14)}
                >
                  14
                </button>
                <button 
                  className={`forecast-btn-small ${forecastDays === 30 ? 'active' : ''}`}
                  onClick={() => setForecastDays(30)}
                >
                  30
                </button>
                <input 
                  type="number" 
                  value={forecastDays} 
                  onChange={(e) => setForecastDays(Number(e.target.value))}
                  min="7" 
                  max="30"
                  className="parameter-input-small"
                />
              </div>
            </div>

            <div className="parameter-group-inline">
              <label>Service Level:</label>
              <div className="inline-controls">
                <button 
                  className={`forecast-btn-small ${serviceLevel === 0.9 ? 'active' : ''}`}
                  onClick={() => setServiceLevel(0.9)}
                >
                  90%
                </button>
                <button 
                  className={`forecast-btn-small ${serviceLevel === 0.95 ? 'active' : ''}`}
                  onClick={() => setServiceLevel(0.95)}
                >
                  95%
                </button>
                <button 
                  className={`forecast-btn-small ${serviceLevel === 0.99 ? 'active' : ''}`}
                  onClick={() => setServiceLevel(0.99)}
                >
                  99%
                </button>
                <input 
                  type="number" 
                  value={serviceLevel} 
                  onChange={(e) => setServiceLevel(Number(e.target.value))}
                  min="0.5" 
                  max="0.99"
                  step="0.01"
                  className="parameter-input-small"
                />
              </div>
            </div>

            <div className="parameter-group-inline">
              <label>Lead Time (days):</label>
              <div className="inline-controls">
                <button 
                  className={`forecast-btn-small ${leadTimeDays === 1 ? 'active' : ''}`}
                  onClick={() => setLeadTimeDays(1)}
                >
                  1
                </button>
                <button 
                  className={`forecast-btn-small ${leadTimeDays === 7 ? 'active' : ''}`}
                  onClick={() => setLeadTimeDays(7)}
                >
                  7
                </button>
                <button 
                  className={`forecast-btn-small ${leadTimeDays === 14 ? 'active' : ''}`}
                  onClick={() => setLeadTimeDays(14)}
                >
                  14
                </button>
                <input 
                  type="number" 
                  value={leadTimeDays} 
                  onChange={(e) => setLeadTimeDays(Number(e.target.value))}
                  min="1" 
                  max="14"
                  className="parameter-input-small"
                />
              </div>
            </div>

            <div className="parameter-group-inline">
              <label>Max Order (ml):</label>
              <div className="inline-controls">
                <button 
                  className={`forecast-btn-small ${maxOrderLimit === 500 ? 'active' : ''}`}
                  onClick={() => setMaxOrderLimit(500)}
                >
                  500
                </button>
                <button 
                  className={`forecast-btn-small ${maxOrderLimit === 1000 ? 'active' : ''}`}
                  onClick={() => setMaxOrderLimit(1000)}
                >
                  1K
                </button>
                <button 
                  className={`forecast-btn-small ${maxOrderLimit === 2000 ? 'active' : ''}`}
                  onClick={() => setMaxOrderLimit(2000)}
                >
                  2K
                </button>
                <input 
                  type="number" 
                  value={maxOrderLimit} 
                  onChange={(e) => setMaxOrderLimit(Number(e.target.value))}
                  min="100" 
                  max="10000"
                  step="100"
                  className="parameter-input-small"
                />
              </div>
            </div>
          </div>

          <div className="analysis-info-compact">
            <div className="parameter-summary">
              <span>Service Level: {(serviceLevel * 100).toFixed(0)}%</span>
              <span>Lead Time: {leadTimeDays} days</span>
              <span>Max Order: {maxOrderLimit.toLocaleString()} ml</span>
              <span>Forecast: {forecastDays} days</span>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>Loading inventory optimization data...</p>
          </div>
        ) : error ? (
          <div className="chart-error">
            <p>Error: {error}</p>
            <button onClick={fetchInventoryOptimization} className="retry-btn">Retry</button>
          </div>
        ) : !inventoryData ? (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>No inventory data available. Loading...</p>
            <button onClick={fetchInventoryOptimization} className="retry-btn">Load Data</button>
          </div>
        ) : (
          <>
            {/* Analysis Content */}
            {(() => {
              const recommendations = inventoryData.blood_type_recommendations;
              
              // Filter blood types that need orders
              const criticalBloodTypes = recommendations.filter(
                rec => rec.recommended_order_ml > 0
              );

              // Filter blood types with low stock (below safety level)
              const lowStockBloodTypes = recommendations.filter(
                rec => rec.current_stock_ml < rec.safety_stock_ml
              );

              // Calculate totals
              const totalCurrentStock = recommendations.reduce(
                (sum, rec) => sum + rec.current_stock_ml, 0
              );

              const totalRecommendedOrders = recommendations.reduce(
                (sum, rec) => sum + rec.recommended_order_ml, 0
              );

              const totalForecastedDemand = recommendations.reduce(
                (sum, rec) => sum + (rec.forecasted_daily_demand_ml * forecastDays), 0
              );

              // Calculate total estimated cost (assuming 0.85 frs per ml)
              const totalEstimatedCost = totalRecommendedOrders * 0.85;

              // Get critical blood types for display
              const criticalBloodTypesText = criticalBloodTypes.length > 0 
                ? criticalBloodTypes.map(r => r.blood_type).join(', ')
                : 'None';

              const getStatusColor = (recommendedOrder: number) => {
                if (recommendedOrder > 0) return 'text-red-600';
                return 'text-green-600';
              };

              const getStatusText = (rec: BloodTypeRecommendation) => {
                if (rec.recommended_order_ml > 0) return 'Order Required';
                if (rec.current_stock_ml < rec.safety_stock_ml) return 'Low Stock';
                return 'Adequate';
              };

              const getJustification = (rec: BloodTypeRecommendation) => {
                if (rec.recommended_order_ml > 0) {
                  const daysOfStock = rec.current_stock_ml / rec.forecasted_daily_demand_ml;
                  return `Current stock will last ${daysOfStock.toFixed(1)} days. Below safety level.`;
                }
                if (rec.current_stock_ml < rec.safety_stock_ml) {
                  return `Stock below safety threshold but demand is low.`;
                }
                return `Stock levels are adequate for current demand patterns.`;
              };

              return (
                <>
                  {/* Overview Section */}
                  <div className="overview-section">
                    <div className="overview-header">
                      <div className="overview-icon">⚠️</div>
                      <h2>Overview</h2>
                    </div>
                    
                    <div className="overview-cards">
                      <div className="overview-card">
                        <h3>Overall Stock Status</h3>
                        <div className="status-value">
                          {criticalBloodTypes.length > 0 ? 'Critical' : 'Good'}
                        </div>
                        <div className="status-detail">
                          Critical types: {criticalBloodTypesText}
                        </div>
                      </div>

                      <div className="overview-card">
                        <h3>Low Stock Alert</h3>
                        <div className="status-subtitle">
                          Below safety stock levels
                        </div>
                        <div className="status-detail">
                          {lowStockBloodTypes.length > 0 
                            ? lowStockBloodTypes.map(r => r.blood_type).join(', ')
                            : 'None'
                          }
                        </div>
                      </div>

                      <div className="overview-card">
                        <h3>Total Current Stock</h3>
                        <div className="status-subtitle">
                          All blood types combined
                        </div>
                        <div className="status-detail">
                          {Math.round(totalCurrentStock).toLocaleString()} ml
                        </div>
                      </div>

                      <div className="overview-card">
                        <h3>Recommended Order Cost</h3>
                        <div className="status-subtitle">
                          Total estimated cost ({Math.round(totalRecommendedOrders).toLocaleString()} ml)
                        </div>
                        <div className="cost-amount">
                          Est. cost: {totalEstimatedCost.toLocaleString()} frs
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Suggested Replenishment Orders Table */}
                  <div className="replenishment-section">
                    <h2>Blood Type Analysis & Recommendations</h2>
                    
                    <div className="table-container">
                      <table className="replenishment-table">
                        <thead>
                          <tr>
                            <th>Blood Type</th>
                            <th>Current Stock (ml)</th>
                            <th>Safety Level (ml)</th>
                            <th>Daily Demand (ml)</th>
                            <th>{forecastDays}-Day Forecast (ml)</th>
                            <th>Recommended Order (ml)</th>
                            <th>Status</th>
                            <th>Analysis</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recommendations.map((rec) => (
                            <tr key={rec.blood_type}>
                              <td className="blood-type-cell">
                                <span className="blood-type-badge">{rec.blood_type}</span>
                              </td>
                              <td>{Math.round(rec.current_stock_ml).toLocaleString()}</td>
                              <td>{Math.round(rec.safety_stock_ml).toLocaleString()}</td>
                              <td>{Math.round(rec.forecasted_daily_demand_ml).toLocaleString()}</td>
                              <td>{Math.round(rec.forecasted_daily_demand_ml * forecastDays).toLocaleString()}</td>
                              <td>
                                <span className={`order-quantity ${getStatusColor(rec.recommended_order_ml)}`}>
                                  {Math.round(rec.recommended_order_ml).toLocaleString()}
                                </span>
                              </td>
                              <td>
                                <span className={getStatusColor(rec.recommended_order_ml)}>
                                  {getStatusText(rec)}
                                </span>
                              </td>
                              <td className="justification-cell">
                                {getJustification(rec)}
                                <br />
                                <small>Trend: {rec.usage_statistics.trend > 0 ? '+' : ''}{rec.usage_statistics.trend.toFixed(1)} ml/day</small>
                              </td>
                              <td className="actions-cell">
                                {rec.recommended_order_ml > 0 ? (
                                  <div className="action-buttons">
                                    <button className="action-btn create-order">
                                      [Create Order]
                                    </button>
                                    <button className="action-btn ignore">
                                      [Ignore]
                                    </button>
                                  </div>
                                ) : (
                                  <span className="no-action">No action needed</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Summary Statistics */}
                  <div className="summary-section">
                    <h2>Forecast Summary</h2>
                    <div className="summary-stats">
                      <div className="stat-item">
                        <span className="stat-label">Analysis Timestamp:</span>
                        <span className="stat-value">{new Date(inventoryData.timestamp).toLocaleString()}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Total Current Stock:</span>
                        <span className="stat-value">{Math.round(totalCurrentStock).toLocaleString()} ml</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Total {forecastDays}-Day Demand:</span>
                        <span className="stat-value">{Math.round(totalForecastedDemand).toLocaleString()} ml</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Total Recommended Orders:</span>
                        <span className="stat-value">{Math.round(totalRecommendedOrders).toLocaleString()} ml</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Blood Types Needing Orders:</span>
                        <span className="stat-value">{criticalBloodTypes.length} of {recommendations.length}</span>
                      </div>
                    </div>
                  </div>
                </>
              );
            })()}
          </>
        )}
      </div>
    );
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

  const renderTrendAnalysisView = () => {
    if (!totalVolumeData || !totalVolumeData.daily_data) return null;
    
    const dailyData = totalVolumeData.daily_data;
    const chartWidth = 800;
    const chartHeight = 600;
    const padding = { top: 40, right: 60, bottom: 80, left: 80 };
    const plotWidth = chartWidth - padding.left - padding.right;
    const plotHeight = chartHeight - padding.top - padding.bottom;
    
    // Find min and max values for scaling
    const allVolumes = dailyData.flatMap(d => [d.daily_donated, d.daily_used]);
    const maxVolume = Math.max(...allVolumes);
    const minVolume = Math.min(...allVolumes);
    const volumeRange = maxVolume - minVolume;
    const yScale = (value: number) => padding.top + plotHeight - ((value - minVolume) / volumeRange) * plotHeight;
    
    // X-axis scaling
    const xScale = (index: number) => padding.left + (index / (dailyData.length - 1)) * plotWidth;
    
    // Create path data for donated blood line
    const donatedPath = dailyData.map((data, index) => {
      const x = xScale(index);
      const y = yScale(data.daily_donated);
      return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(' ');
    
    // Create path data for used blood line
    const usedPath = dailyData.map((data, index) => {
      const x = xScale(index);
      const y = yScale(data.daily_used);
      return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(' ');
    
    // Generate y-axis ticks
    const yTicks = [];
    const tickCount = 8;
    for (let i = 0; i <= tickCount; i++) {
      const value = minVolume + (volumeRange * i / tickCount);
      yTicks.push(value);
    }
    
    // Generate x-axis date labels (show every 7th day for readability)
    const dateLabels = dailyData.filter((_, index) => index % 7 === 0).map((data, index) => ({
      x: xScale(index * 7),
      date: new Date(data.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }));
    
    return (
      <div className="trend-analysis-view">
        <div className="chart-header">
          <button className="back-button" onClick={() => setCurrentView('welcome')}>
            ← Back to Overview
          </button>
          <div className="header-content">
            <h2>Trend Analysis - Daily Blood Volume</h2>
            <p>Analyze patterns in blood donation and usage over time</p>
          </div>
        </div>
        
        {/* Time Period Filter */}
        <div className="trends-controls">
          <div className="control-group">
            <label>Time Period:</label>
            <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={180}>Last 180 days</option>
              <option value={365}>Last 365 days</option>
            </select>
          </div>
        </div>
        
        {loading ? (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>Loading trend analysis data...</p>
          </div>
        ) : error ? (
          <div className="chart-error">
            <p>Error: {error}</p>
            <button onClick={fetchTotalVolumeData} className="retry-btn">Retry</button>
          </div>
        ) : totalVolumeData ? (
          <>
            <div className="chart-container" style={{ overflowX: 'auto', overflowY: 'auto', maxWidth: '100%', padding: '20px' }}>
              <svg 
                width={chartWidth} 
                height={chartHeight} 
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                className="line-chart" 
                style={{ minWidth: '800px', maxWidth: '100%' }}
                preserveAspectRatio="xMidYMid meet"
              >
                {/* Background */}
                <rect width={chartWidth} height={chartHeight} fill="#fafafa" />
                
                {/* Grid lines */}
                {yTicks.map(tick => (
                  <g key={tick}>
                    <line
                      x1={padding.left}
                      y1={yScale(tick)}
                      x2={padding.left + plotWidth}
                      y2={yScale(tick)}
                      stroke="#e5e5e5"
                      strokeWidth="1"
                    />
                    <text
                      x={padding.left - 10}
                      y={yScale(tick) + 4}
                      textAnchor="end"
                      fontSize="12"
                      fill="#666"
                    >
                      {Math.round(tick)}
                    </text>
                  </g>
                ))}
                
                {/* Vertical grid lines */}
                {dateLabels.map(label => (
                  <line
                    key={label.date}
                    x1={label.x}
                    y1={padding.top}
                    x2={label.x}
                    y2={padding.top + plotHeight}
                    stroke="#e5e5e5"
                    strokeWidth="1"
                  />
                ))}
                
                {/* Chart border */}
                <rect
                  x={padding.left}
                  y={padding.top}
                  width={plotWidth}
                  height={plotHeight}
                  fill="none"
                  stroke="#333"
                  strokeWidth="2"
                />
                
                {/* Data lines */}
                <path
                  d={donatedPath}
                  stroke="#10b981"
                  strokeWidth="3"
                  fill="none"
                  className="donation-line"
                />
                <path
                  d={usedPath}
                  stroke="#ef4444"
                  strokeWidth="3"
                  fill="none"
                  className="usage-line"
                />
                
                {/* Data points */}
                {dailyData.map((data, index) => (
                  <g key={index}>
                    <circle
                      cx={xScale(index)}
                      cy={yScale(data.daily_donated)}
                      r="4"
                      fill="#10b981"
                      stroke="white"
                      strokeWidth="2"
                    />
                    <circle
                      cx={xScale(index)}
                      cy={yScale(data.daily_used)}
                      r="4"
                      fill="#ef4444"
                      stroke="white"
                      strokeWidth="2"
                    />
                  </g>
                ))}
                
                {/* X-axis labels */}
                {dateLabels.map(label => (
                  <text
                    key={label.date}
                    x={label.x}
                    y={padding.top + plotHeight + 20}
                    textAnchor="middle"
                    fontSize="12"
                    fill="#666"
                  >
                    {label.date}
                  </text>
                ))}
                
                {/* Axis labels */}
                <text
                  x={padding.left + plotWidth / 2}
                  y={chartHeight - 20}
                  textAnchor="middle"
                  fontSize="14"
                  fontWeight="bold"
                  fill="#333"
                >
                  Date
                </text>
                <text
                  x={20}
                  y={padding.top + plotHeight / 2}
                  textAnchor="middle"
                  fontSize="14"
                  fontWeight="bold"
                  fill="#333"
                  transform={`rotate(-90 20 ${padding.top + plotHeight / 2})`}
                >
                  Volume (ml)
                </text>
                
                {/* Legend */}
                <g transform={`translate(${padding.left + plotWidth - 150}, ${padding.top + 20})`}>
                  <rect x="0" y="0" width="140" height="60" fill="white" stroke="#ddd" strokeWidth="1" />
                  <line x1="10" y1="20" x2="30" y2="20" stroke="#10b981" strokeWidth="3" />
                  <text x="35" y="24" fontSize="12" fill="#333">Daily Donated</text>
                  <line x1="10" y1="40" x2="30" y2="40" stroke="#ef4444" strokeWidth="3" />
                  <text x="35" y="44" fontSize="12" fill="#333">Daily Used</text>
                </g>
              </svg>
            </div>
            
            <div className="trend-summary">
              <div className="summary-card">
                <h3>Total Period</h3>
                <p>
                  <span className="metric-value">{totalVolumeData.period.days}</span> days
                </p>
              </div>
              <div className="summary-card">
                <h3>Total Donated</h3>
                <p>
                  <span className="metric-value">{totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_donated, 0).toLocaleString()}</span> ml
                </p>
              </div>
              <div className="summary-card">
                <h3>Total Used</h3>
                <p>
                  <span className="metric-value">{totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_used, 0).toLocaleString()}</span> ml
                </p>
              </div>
              <div className="summary-card">
                <h3>Net Balance</h3>
                <p>
                  <span className={`metric-value ${totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_donated, 0) - totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_used, 0) >= 0 ? 'positive' : 'negative'}`}>
                    {(totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_donated, 0) - totalVolumeData.daily_data.reduce((sum, d) => sum + d.daily_used, 0)).toLocaleString()}
                  </span> ml
                </p>
              </div>
            </div>
          </>
        ) : null}
      </div>
    );
  };

  const renderWelcomeView = () => (
    <div className="welcome-container">
      <div className="welcome-header">
        <TrendingUp size={48} className="welcome-icon" />
        <h1 className="welcome-title">Welcome to Blood Bank Analytics</h1>
        <p className="welcome-subtitle">
          Advanced analytics and predictions for blood bank inventory management
        </p>
      </div>
      
      <div className="feature-grid">
        <div className="feature-card clickable" onClick={showTrendsView}>
          <BarChart3 size={32} className="feature-icon" />
          <h3>Volume Analytics</h3>
          <p>Track donation and usage patterns by blood type</p>
          <div className="click-indicator">
            <span>Click to view trend charts →</span>
          </div>
        </div>
        
        <div className="feature-card clickable" onClick={showMonitoringView}>
          <Activity size={32} className="feature-icon" />
          <h3>Real-time Monitoring</h3>
          <p>Monitor current inventory levels and status</p>
          <div className="click-indicator">
            <span>Click to view detailed charts →</span>
          </div>
        </div>
        
        <div className="feature-card clickable" onClick={showPredictiveView}>
          <Calendar size={32} className="feature-icon" />
          <h3>Predictive Insights</h3>
          <p>Forecast future needs and optimize ordering</p>
          <div className="click-indicator">
            <span>Click to view inventory optimization →</span>
          </div>
        </div>
        
        <div className="feature-card clickable" onClick={showTrendAnalysisView}>
          <TrendingUp size={32} className="feature-icon" />
          <h3>Trend Analysis</h3>
          <p>Identify patterns and seasonal variations</p>
          <div className="click-indicator">
            <span>Click to view trend analysis →</span>
          </div>
        </div>
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

  const renderTrendsView = () => {
    const availableBloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
    
    const handleBloodTypeToggle = (bloodType: string) => {
      setSelectedBloodTypes(prev => 
        prev.includes(bloodType) 
          ? prev.filter(type => type !== bloodType)
          : [...prev, bloodType]
      );
    };

    const getLineColor = (bloodType: string): string => {
      const colors: { [key: string]: string } = {
        'A+': '#ef4444', 'A-': '#f87171',
        'B+': '#3b82f6', 'B-': '#60a5fa',
        'AB+': '#10b981', 'AB-': '#34d399',
        'O+': '#f59e0b', 'O-': '#fbbf24'
      };
      return colors[bloodType] || '#6b7280';
    };

    return (
      <div className="monitoring-view">
        <div className="monitoring-header">
          <button className="back-button" onClick={showWelcomeView}>
            ← Back to Overview
          </button>
          <div className="monitoring-title">
            <BarChart3 size={32} className="monitoring-icon" />
            <h1>Volume Trends Analysis</h1>
          </div>
        </div>

        <div className="monitoring-content">
          {/* Controls */}
          <div className="trends-controls">
            <div className="control-group">
              <label>Time Period:</label>
              <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={180}>Last 180 days</option>
                <option value={365}>Last 365 days</option>
              </select>
            </div>
            
            <div className="control-group">
              <label>Blood Types:</label>
              <div className="blood-type-filters">
                {availableBloodTypes.map(type => (
                  <button
                    key={type}
                    className={`filter-btn ${selectedBloodTypes.includes(type) ? 'active' : ''}`}
                    onClick={() => handleBloodTypeToggle(type)}
                    style={{
                      backgroundColor: selectedBloodTypes.includes(type) ? getLineColor(type) : '#f3f4f6',
                      color: selectedBloodTypes.includes(type) ? 'white' : '#374151'
                    }}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {loading ? (
            <div className="chart-loading">
              <div className="loading-spinner"></div>
              <p>Loading trends data...</p>
            </div>
          ) : error ? (
            <div className="chart-error">
              <p>Error: {error}</p>
              <button onClick={fetchTrendsData} className="retry-btn">Retry</button>
            </div>
          ) : trendsData ? (
            <>
              <div className="trends-chart-container">
                <div className="chart-header">
                  <h2>Daily Volume Trends - Donated Blood</h2>
                  <p>Period: {trendsData.period.start_date} to {trendsData.period.end_date}</p>
                </div>
              
              <div className="line-chart-container">
                <svg className="line-chart" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet">
                  {/* Chart background and grid */}
                  <defs>
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e5e7eb" strokeWidth="1"/>
                    </pattern>
                  </defs>
                  <rect width="800" height="400" fill="url(#grid)" />
                  
                  {/* Y-axis */}
                  <line x1="80" y1="50" x2="80" y2="350" stroke="#374151" strokeWidth="2" />
                  {/* X-axis */}
                  <line x1="80" y1="350" x2="750" y2="350" stroke="#374151" strokeWidth="2" />
                  
                  {/* Y-axis labels */}
                  {[0, 1000, 2000, 3000, 4000, 5000].map((value, index) => (
                    <g key={value}>
                      <line x1="75" y1={350 - (index * 50)} x2="85" y2={350 - (index * 50)} stroke="#374151" strokeWidth="1" />
                      <text x="70" y={355 - (index * 50)} textAnchor="end" fontSize="10" fill="#6b7280">
                        {value > 0 ? `${value/1000}K` : '0'}
                      </text>
                    </g>
                  ))}
                  
                  {/* Lines for each blood type */}
                  {trendsData.blood_types.filter(type => selectedBloodTypes.includes(type)).map(bloodType => {
                    const trend = trendsData.trends[bloodType];
                    const maxValue = 5000; // Max scale for Y-axis
                    const chartWidth = 670; // Available width for chart
                    const chartHeight = 300; // Available height for chart
                    
                    const points = trend.dates.map((_, index) => {
                      const x = 80 + (index / (trend.dates.length - 1)) * chartWidth;
                      const y = 350 - (trend.donated_volume[index] / maxValue) * chartHeight;
                        return `${x},${y}`;
                    }).join(' ');
                    
                    return (
                      <g key={bloodType}>
                        <polyline
                          points={points}
                          fill="none"
                          stroke={getLineColor(bloodType)}
                          strokeWidth="2"
                          strokeLinejoin="round"
                        />
                        {/* Data points */}
                        {trend.dates.map((date, index) => {
                          const x = 80 + (index / (trend.dates.length - 1)) * chartWidth;
                          const y = 350 - (trend.donated_volume[index] / maxValue) * chartHeight;
                          return (
                            <circle
                              key={index}
                              cx={x}
                              cy={y}
                              r="2"
                              fill={getLineColor(bloodType)}
                            >
                              <title>{`${bloodType} - ${date}: ${trend.donated_volume[index]}ml`}</title>
                            </circle>
                          );
                        })}
                      </g>
                    );
                  })}
                  
                  {/* Chart labels */}
                  <text x="400" y="30" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#1f2937">
                    Daily Donated Volume by Blood Type
                  </text>
                  <text x="30" y="200" textAnchor="middle" fontSize="12" fontWeight="600" fill="#1f2937" transform="rotate(-90, 30, 200)">
                    Volume (ml)
                  </text>
                  <text x="415" y="385" textAnchor="middle" fontSize="12" fontWeight="600" fill="#1f2937">
                    Date
                  </text>
                </svg>
              </div>

              {/* Legend */}
              <div className="chart-legend">
                {selectedBloodTypes.map(bloodType => (
                  <div key={bloodType} className="legend-item">
                    <div 
                      className="legend-box" 
                      style={{ backgroundColor: getLineColor(bloodType) }}
                    ></div>
                    <span>{bloodType}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="trends-chart-container" style={{ marginTop: '3rem' }}>
              <div className="chart-header">
                <h2>Daily Volume Trends - Used Blood</h2>
                <p>Period: {trendsData?.period.start_date} to {trendsData?.period.end_date}</p>
              </div>
              
              <div className="line-chart-container">
                <svg className="line-chart" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet">
                  {/* Chart background and grid */}
                  <defs>
                    <pattern id="grid-usage" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e5e7eb" strokeWidth="1"/>
                    </pattern>
                  </defs>
                  <rect width="800" height="400" fill="url(#grid-usage)" />
                  
                  {/* Y-axis */}
                  <line x1="80" y1="50" x2="80" y2="350" stroke="#374151" strokeWidth="2" />
                  {/* X-axis */}
                  <line x1="80" y1="350" x2="750" y2="350" stroke="#374151" strokeWidth="2" />
                  
                  {/* Y-axis labels */}
                  {[0, 1000, 2000, 3000, 4000, 5000].map((value, index) => (
                    <g key={value}>
                      <line x1="75" y1={350 - (index * 50)} x2="85" y2={350 - (index * 50)} stroke="#374151" strokeWidth="1" />
                      <text x="70" y={355 - (index * 50)} textAnchor="end" fontSize="10" fill="#6b7280">
                        {value > 0 ? `${value/1000}K` : '0'}
                      </text>
                    </g>
                  ))}
                  
                  {/* Lines for each blood type - Usage Data */}
                  {trendsData?.blood_types.filter(type => selectedBloodTypes.includes(type)).map(bloodType => {
                    const trend = trendsData?.trends[bloodType];
                    if (!trend) return null;
                    
                    const maxValue = 5000; // Max scale for Y-axis
                    const chartWidth = 670; // Available width for chart
                    const chartHeight = 300; // Available height for chart
                    
                    const points = trend.dates.map((_, index) => {
                      const x = 80 + (index / (trend.dates.length - 1)) * chartWidth;
                      const y = 350 - (trend.used_volume[index] / maxValue) * chartHeight;
                      return `${x},${y}`;
                    }).join(' ');
                    
                    return (
                      <g key={bloodType}>
                        <polyline
                          points={points}
                          fill="none"
                          stroke={getLineColor(bloodType)}
                          strokeWidth="2"
                          strokeLinejoin="round"
                        />
                        {/* Data points */}
                        {trend.dates.map((date, index) => {
                          const x = 80 + (index / (trend.dates.length - 1)) * chartWidth;
                          const y = 350 - (trend.used_volume[index] / maxValue) * chartHeight;
                          return (
                            <circle
                              key={index}
                              cx={x}
                              cy={y}
                              r="2"
                              fill={getLineColor(bloodType)}
                            >
                              <title>{`${bloodType} - ${date}: ${trend.used_volume[index]}ml`}</title>
                            </circle>
                          );
                        })}
                      </g>
                    );
                  })}
                  
                  {/* Chart labels */}
                  <text x="400" y="30" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#1f2937">
                    Daily Used Volume by Blood Type
                  </text>
                  <text x="30" y="200" textAnchor="middle" fontSize="12" fontWeight="600" fill="#1f2937" transform="rotate(-90, 30, 200)">
                    Volume (ml)
                  </text>
                  <text x="415" y="385" textAnchor="middle" fontSize="12" fontWeight="600" fill="#1f2937">
                    Date
                  </text>
                </svg>
              </div>

              {/* Legend for Usage Chart */}
              <div className="chart-legend">
                {selectedBloodTypes.map(bloodType => (
                  <div key={bloodType} className="legend-item">
                    <div 
                      className="legend-box" 
                      style={{ backgroundColor: getLineColor(bloodType) }}
                    ></div>
                    <span>{bloodType}</span>
                  </div>
                ))}
              </div>
            </div>
            </>
          ) : null}
        </div>
      </div>
    );
  };

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
          <div className="menu-item active" onClick={navigateToForecasting} title="Forecasting">
            <span className="menu-icon">📊</span>
          </div>
          <div className="menu-item" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
            <span className="menu-icon">📈</span>
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
        {currentView === 'welcome' ? renderWelcomeView() : 
         currentView === 'monitoring' ? renderMonitoringView() : 
         currentView === 'trendAnalysis' ? renderTrendAnalysisView() :
         currentView === 'predictive' ? renderPredictiveView() :
         renderTrendsView()}
      </div>
    </div>
  );
};

export default Forecasting;
