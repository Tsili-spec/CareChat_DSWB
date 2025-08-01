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

const Forecasting: React.FC = () => {
  const [volumeData, setVolumeData] = useState<VolumeResponse | null>(null);
  const [trendsData, setTrendsData] = useState<TrendsResponse | null>(null);
  const [totalVolumeData, setTotalVolumeData] = useState<TotalVolumeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState<'welcome' | 'monitoring' | 'trends' | 'trendAnalysis'>('welcome');
  const [selectedBloodTypes, setSelectedBloodTypes] = useState<string[]>(['A+', 'B+', 'AB+', 'O+']);
  const [days, setDays] = useState(90);

  useEffect(() => {
    if (currentView === 'monitoring') {
      fetchVolumeData();
    } else if (currentView === 'trends') {
      fetchTrendsData();
    } else if (currentView === 'trendAnalysis') {
      fetchTotalVolumeData();
    }
  }, [currentView, selectedBloodTypes, days]);

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

  const showTrendsView = () => {
    setCurrentView('trends');
  };

  const showTrendAnalysisView = () => {
    setCurrentView('trendAnalysis');
  };

  const showWelcomeView = () => {
    setCurrentView('welcome');
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
        
        <div className="feature-card">
          <Calendar size={32} className="feature-icon" />
          <h3>Predictive Insights</h3>
          <p>Forecast future needs and optimize ordering</p>
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
        {currentView === 'welcome' ? renderWelcomeView() : 
         currentView === 'monitoring' ? renderMonitoringView() : 
         currentView === 'trendAnalysis' ? renderTrendAnalysisView() :
         renderTrendsView()}
      </div>
    </div>
  );
};

export default Forecasting;
