import { useState, useEffect } from 'react'
import './Dashboard.css'
import { 
  LineChart, 
  BarChart, 
  DoughnutChart, 
  AreaChart, 
  PieChart, 
  RadarChart, 
  PolarAreaChart, 
  ScatterChart, 
  BubbleChart 
} from './charts'
import { apiService, BloodBankAnalytics, BloodCollection, BloodCollectionParams, BloodUsage, BloodUsageParams, BloodInventoryItem } from '../services/api'

interface DashboardProps {
  activeSection: string
}

const Dashboard = ({ activeSection }: DashboardProps) => {
  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <BloodBankAnalyticsDashboard />
      case 'collections':
        return <BloodCollectionsView />
      case 'usage':
        return <BloodUsageView />
      case 'inventory':
        return <BloodInventoryView />
      case 'low-stock':
        return <LowStockAlertsView />
      case 'donors':
        return <DonorManagementView />
      case 'settings':
        return <SettingsView />
      default:
        return <BloodBankAnalyticsDashboard />
    }
  }

  return <div className="dashboard-content">{renderContent()}</div>
}

const BloodBankAnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState<BloodBankAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await apiService.getBloodBankAnalytics(30)
        setAnalytics(data)
      } catch (err: any) {
        setError('Failed to load analytics data')
        console.error('Analytics error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="section-view">
        <div className="loading-spinner">Loading analytics...</div>
      </div>
    )
  }

  if (error || !analytics) {
    return (
      <div className="section-view">
        <div className="error-message">
          {error || 'No analytics data available'}
        </div>
      </div>
    )
  }

  const stats = [
    { 
      label: 'Total Collections', 
      value: analytics.total_collections.toString(), 
      change: '+12.5%', 
      trend: 'up',
      icon: '🩸'
    },
    { 
      label: 'Total Usage', 
      value: analytics.total_usage.toString(), 
      change: '+8.3%', 
      trend: 'up',
      icon: '💉'
    },
    { 
      label: 'Current Inventory', 
      value: analytics.current_inventory.toString(), 
      change: '-2.1%', 
      trend: 'down',
      icon: '🏥'
    },
    { 
      label: 'Low Stock Alerts', 
      value: analytics.low_stock_alerts.toString(), 
      change: analytics.low_stock_alerts > 0 ? '+15%' : '0%', 
      trend: analytics.low_stock_alerts > 0 ? 'down' : 'up',
      icon: '⚠️'
    },
  ]

  // Blood type distribution chart data
  const bloodTypeData = {
    labels: analytics.blood_type_distribution.map(item => item.blood_type),
    datasets: [
      {
        data: analytics.blood_type_distribution.map(item => item.units),
        backgroundColor: [
          '#dc2626', // Red for blood
          '#b91c1c',
          '#991b1b',
          '#7f1d1d',
          '#ef4444',
          '#f87171',
          '#fca5a5',
          '#fecaca',
        ],
        borderWidth: 2,
      },
    ],
  }

  // Collection trends chart data
  const collectionTrendsData = {
    labels: analytics.collection_trends.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Collections',
        data: analytics.collection_trends.map(item => item.collections),
        borderColor: '#dc2626',
        backgroundColor: 'rgba(220, 38, 38, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // Usage trends chart data
  const usageTrendsData = {
    labels: analytics.usage_trends.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Usage',
        data: analytics.usage_trends.map(item => item.usage),
        borderColor: '#059669',
        backgroundColor: 'rgba(5, 150, 105, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // Combined collection vs usage chart
  const collectionVsUsageData = {
    labels: analytics.collection_trends.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Collections',
        data: analytics.collection_trends.map(item => item.collections),
        borderColor: '#dc2626',
        backgroundColor: 'rgba(220, 38, 38, 0.8)',
      },
      {
        label: 'Usage',
        data: analytics.usage_trends.map(item => item.usage),
        borderColor: '#059669',
        backgroundColor: 'rgba(5, 150, 105, 0.8)',
      },
    ],
  }

  return (
    <div className="section-view">
      <div className="dashboard-header">
        <h2>Blood Bank Analytics Dashboard</h2>
        <p>Comprehensive overview of blood collection, usage, and inventory management</p>
      </div>

      {/* Key Statistics */}
      <div className="dashboard-grid">
        {stats.map((stat, index) => (
          <div key={index} className="dashboard-card stat-card blood-bank-stat">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <h3>{stat.label}</h3>
              <div className="stat-number">{stat.value}</div>
              <div className={`stat-change ${stat.trend}`}>
                {stat.trend === 'up' ? '↗️' : '↘️'} {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Blood Type Distribution</h3>
          <PieChart data={bloodTypeData} height={300} />
        </div>

        <div className="dashboard-card chart-card">
          <h3>Collection vs Usage Trends</h3>
          <BarChart data={collectionVsUsageData} height={300} />
        </div>

        <div className="dashboard-card chart-card">
          <h3>Collection Trends (30 Days)</h3>
          <AreaChart data={collectionTrendsData} height={300} />
        </div>
      </div>

      {/* Inventory Status */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Inventory Status by Blood Type</h3>
          <div className="inventory-grid">
            {analytics.inventory_levels.map((item, index) => (
              <div key={index} className={`inventory-item ${item.status}`}>
                <div className="blood-type">{item.blood_type}</div>
                <div className="stock-info">
                  <div className="current-stock">{item.current_stock} units</div>
                  <div className="min-required">Min: {item.minimum_required}</div>
                </div>
                <div className={`status-badge ${item.status}`}>
                  {item.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Donor Statistics</h3>
          <div className="donor-stats">
            <div className="donor-stat-item">
              <div className="donor-stat-icon">👥</div>
              <div className="donor-stat-content">
                <div className="donor-stat-number">{analytics.donor_statistics.total_donors}</div>
                <div className="donor-stat-label">Total Donors</div>
              </div>
            </div>
            <div className="donor-stat-item">
              <div className="donor-stat-icon">✅</div>
              <div className="donor-stat-content">
                <div className="donor-stat-number">{analytics.donor_statistics.active_donors}</div>
                <div className="donor-stat-label">Active Donors</div>
              </div>
            </div>
            <div className="donor-stat-item">
              <div className="donor-stat-icon">🆕</div>
              <div className="donor-stat-content">
                <div className="donor-stat-number">{analytics.donor_statistics.new_donors_this_month}</div>
                <div className="donor-stat-label">New This Month</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Expiry Alerts */}
      {analytics.expiry_alerts.length > 0 && (
        <div className="dashboard-grid">
          <div className="dashboard-card alert-card">
            <h3>⏰ Expiry Alerts</h3>
            <div className="expiry-alerts">
              {analytics.expiry_alerts.map((alert, index) => (
                <div key={index} className="expiry-alert-item">
                  <div className="alert-blood-type">{alert.blood_type}</div>
                  <div className="alert-details">
                    <div className="alert-units">{alert.units_expiring} units expiring</div>
                    <div className="alert-date">
                      {new Date(alert.expiry_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const BloodCollectionsView = () => {
  const [collections, setCollections] = useState<BloodCollection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState<BloodCollectionParams>({
    limit: 100,
    offset: 0
  })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

  useEffect(() => {
    const fetchCollections = async () => {
      setLoading(true)
      try {
        const data = await apiService.getBloodCollections(filters)
        setCollections(data)
      } catch (err: any) {
        setError('Failed to load collections data')
        console.error('Collections error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCollections()
  }, [filters])

  const handleFilterChange = (key: keyof BloodCollectionParams, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === '' ? undefined : value
    }))
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setFilters({
      limit: 100,
      offset: 0
    })
    setCurrentPage(1)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getExpiryStatus = (expiryDate: string) => {
    const today = new Date()
    const expiry = new Date(expiryDate)
    const daysUntilExpiry = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysUntilExpiry < 0) return { status: 'expired', text: 'Expired', class: 'expired' }
    if (daysUntilExpiry <= 7) return { status: 'critical', text: `${daysUntilExpiry}d left`, class: 'critical' }
    if (daysUntilExpiry <= 30) return { status: 'warning', text: `${daysUntilExpiry}d left`, class: 'warning' }
    return { status: 'good', text: `${daysUntilExpiry}d left`, class: 'good' }
  }

  // Pagination
  const totalPages = Math.ceil(collections.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentCollections = collections.slice(startIndex, endIndex)

  if (loading) {
    return (
      <div className="section-view">
        <div className="loading-spinner">Loading collections...</div>
      </div>
    )
  }

  return (
    <div className="section-view">
      <div className="dashboard-header">
        <h2>🩸 Blood Collections</h2>
        <p>Manage and track all blood donation records</p>
      </div>

      {/* Filters Section */}
      <div className="dashboard-card filters-card">
        <h3>Filters</h3>
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="blood-type-filter">Blood Type</label>
            <select
              id="blood-type-filter"
              value={filters.blood_type || ''}
              onChange={(e) => handleFilterChange('blood_type', e.target.value)}
            >
              <option value="">All Blood Types</option>
              {bloodTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="date-from">Collection Date From</label>
            <input
              type="date"
              id="date-from"
              value={filters.collection_date_from || ''}
              onChange={(e) => handleFilterChange('collection_date_from', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label htmlFor="date-to">Collection Date To</label>
            <input
              type="date"
              id="date-to"
              value={filters.collection_date_to || ''}
              onChange={(e) => handleFilterChange('collection_date_to', e.target.value)}
            />
          </div>

          <div className="filter-actions">
            <button onClick={clearFilters} className="clear-filters-btn">
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Collections Table */}
      <div className="dashboard-card table-card">
        <div className="table-header">
          <h3>Collections ({collections.length} records)</h3>
          <div className="table-actions">
            <button className="export-btn">📊 Export</button>
            <button className="add-btn">➕ Add Collection</button>
          </div>
        </div>

        {error ? (
          <div className="error-message">{error}</div>
        ) : (
          <>
            <div className="table-container">
              <table className="collections-table">
                <thead>
                  <tr>
                    <th>Blood Type</th>
                    <th>Donor Info</th>
                    <th>Collection Site</th>
                    <th>Volume (ml)</th>
                    <th>Hemoglobin</th>
                    <th>Collection Date</th>
                    <th>Expiry Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {currentCollections.map((collection) => {
                    const expiryStatus = getExpiryStatus(collection.expiry_date)
                    return (
                      <tr key={collection.donation_record_id}>
                        <td>
                          <span className={`blood-type-badge ${collection.blood_type.replace('+', 'pos').replace('-', 'neg')}`}>
                            {collection.blood_type}
                          </span>
                        </td>
                        <td>
                          <div className="donor-info">
                            <div className="donor-details">
                              {collection.donor_gender}, {collection.donor_age}y
                            </div>
                            <div className="donor-occupation">
                              {collection.donor_occupation}
                            </div>
                          </div>
                        </td>
                        <td>{collection.collection_site}</td>
                        <td className="volume">{collection.collection_volume_ml}ml</td>
                        <td className="hemoglobin">{collection.hemoglobin_g_dl.toFixed(1)} g/dL</td>
                        <td>{formatDate(collection.donation_date)}</td>
                        <td>
                          <span className={`expiry-status ${expiryStatus.class}`}>
                            {expiryStatus.text}
                          </span>
                        </td>
                        <td>
                          <div className="action-buttons">
                            <button className="view-btn" title="View Details">👁️</button>
                            <button className="edit-btn" title="Edit">✏️</button>
                            <button className="delete-btn" title="Delete">🗑️</button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="pagination-btn"
                >
                  ← Previous
                </button>
                
                <div className="pagination-info">
                  Page {currentPage} of {totalPages} 
                  ({startIndex + 1}-{Math.min(endIndex, collections.length)} of {collections.length})
                </div>
                
                <button 
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="pagination-btn"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

const BloodUsageView = () => {
  const [usageData, setUsageData] = useState<BloodUsage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState<BloodUsageParams>({
    limit: 100,
    offset: 0
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDepartment, setSelectedDepartment] = useState('')
  const [selectedBloodGroup, setSelectedBloodGroup] = useState('')
  const [dateRange, setDateRange] = useState({ from: '', to: '' })

  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        setLoading(true)
        const params: BloodUsageParams = {
          ...filters,
          blood_group: selectedBloodGroup || undefined,
          usage_date_from: dateRange.from || undefined,
          usage_date_to: dateRange.to || undefined,
          patient_location: filters.patient_location || undefined
        }
        const data = await apiService.getBloodUsage(params)
        setUsageData(data)
      } catch (err: any) {
        setError('Failed to load blood usage data')
        console.error('Blood usage error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchUsageData()
  }, [filters, selectedBloodGroup, dateRange])

  const handleFilterChange = (key: keyof BloodUsageParams, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleSearch = (term: string) => {
    setSearchTerm(term)
  }

  const filteredData = usageData.filter(item => {
    const matchesSearch = !searchTerm || 
      item.individual_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.patient_location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.purpose.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesDepartment = !selectedDepartment || item.department === selectedDepartment
    
    return matchesSearch && matchesDepartment
  })

  const departments = [...new Set(usageData.map(item => item.department))]
  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

  const totalVolume = filteredData.reduce((sum, item) => sum + item.volume_given_out, 0)
  const totalTransfusions = filteredData.length
  const departmentStats = departments.map(dept => ({
    department: dept,
    count: filteredData.filter(item => item.department === dept).length,
    volume: filteredData.filter(item => item.department === dept).reduce((sum, item) => sum + item.volume_given_out, 0)
  }))

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPurposeIcon = (purpose: string) => {
    switch (purpose.toLowerCase()) {
      case 'transfusion': return '🩸'
      case 'surgery': return '🏥'
      case 'emergency': return '🚨'
      case 'research': return '🔬'
      default: return '💉'
    }
  }

  const getDepartmentColor = (department: string) => {
    const colors = {
      'emergency': '#ef4444',
      'surgery': '#3b82f6',
      'maternity': '#ec4899',
      'pediatrics': '#10b981',
      'oncology': '#8b5cf6',
      'cardiology': '#f59e0b',
      'icu': '#dc2626',
      'general': '#6b7280'
    }
    return colors[department.toLowerCase() as keyof typeof colors] || '#6b7280'
  }

  if (loading) {
    return (
      <div className="section-view">
        <div className="loading-container">
          <div className="loading-spinner-large">
            <div className="spinner"></div>
            <p>Loading blood usage data...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="section-view">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h3>Unable to Load Data</h3>
          <p>{error}</p>
          <button className="retry-btn" onClick={() => window.location.reload()}>
            🔄 Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="section-view">
      <div className="usage-header">
        <div className="header-content">
          <h2>💉 Blood Usage & Transfusions</h2>
          <p>Comprehensive tracking of blood usage across all departments</p>
        </div>
        <div className="header-actions">
          <button className="action-btn export-btn">
            <span className="btn-icon">📊</span>
            <span className="btn-text">Export Report</span>
          </button>
          <button className="action-btn add-btn">
            <span className="btn-icon">➕</span>
            <span className="btn-text">New Record</span>
          </button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="usage-stats-grid">
        <div className="usage-stat-card primary">
          <div className="stat-icon">💉</div>
          <div className="stat-content">
            <div className="stat-number">{totalTransfusions}</div>
            <div className="stat-label">Total Transfusions</div>
            <div className="stat-period">This period</div>
          </div>
        </div>
        <div className="usage-stat-card secondary">
          <div className="stat-icon">🩸</div>
          <div className="stat-content">
            <div className="stat-number">{totalVolume.toLocaleString()}</div>
            <div className="stat-label">Total Volume (ml)</div>
            <div className="stat-period">Blood used</div>
          </div>
        </div>
        <div className="usage-stat-card tertiary">
          <div className="stat-icon">🏥</div>
          <div className="stat-content">
            <div className="stat-number">{departments.length}</div>
            <div className="stat-label">Active Departments</div>
            <div className="stat-period">Using blood</div>
          </div>
        </div>
        <div className="usage-stat-card quaternary">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-number">{Math.round(totalVolume / totalTransfusions) || 0}</div>
            <div className="stat-label">Avg Volume (ml)</div>
            <div className="stat-period">Per transfusion</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="usage-filters-card">
        <div className="filters-header">
          <h3>🔍 Search & Filter</h3>
          <button className="clear-filters-btn" onClick={() => {
            setSearchTerm('')
            setSelectedDepartment('')
            setSelectedBloodGroup('')
            setDateRange({ from: '', to: '' })
            setFilters({ limit: 100, offset: 0 })
          }}>
            Clear All
          </button>
        </div>
        
        <div className="filters-grid">
          <div className="filter-group">
            <label>Search Records</label>
            <div className="search-input-container">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Search by patient, location, or purpose..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
          
          <div className="filter-group">
            <label>Department</label>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="filter-select"
            >
              <option value="">All Departments</option>
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept.charAt(0).toUpperCase() + dept.slice(1)}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>Blood Group</label>
            <select
              value={selectedBloodGroup}
              onChange={(e) => setSelectedBloodGroup(e.target.value)}
              className="filter-select"
            >
              <option value="">All Blood Groups</option>
              {bloodGroups.map(group => (
                <option key={group} value={group}>{group}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>Date From</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value }))}
              className="date-input"
            />
          </div>
          
          <div className="filter-group">
            <label>Date To</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value }))}
              className="date-input"
            />
          </div>
        </div>
      </div>

      {/* Department Statistics */}
      <div className="department-stats-card">
        <h3>🏥 Department Usage Overview</h3>
        <div className="department-stats-grid">
          {departmentStats.map(stat => (
            <div key={stat.department} className="department-stat-item">
              <div className="department-header">
                <div 
                  className="department-indicator"
                  style={{ backgroundColor: getDepartmentColor(stat.department) }}
                ></div>
                <div className="department-name">{stat.department.charAt(0).toUpperCase() + stat.department.slice(1)}</div>
              </div>
              <div className="department-metrics">
                <div className="metric">
                  <span className="metric-value">{stat.count}</span>
                  <span className="metric-label">Transfusions</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{stat.volume.toLocaleString()}</span>
                  <span className="metric-label">ml Used</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Records Table */}
      <div className="usage-records-card">
        <div className="records-header">
          <h3>📋 Usage Records ({filteredData.length})</h3>
          <div className="records-actions">
            <button className="view-toggle-btn active">📋 Table View</button>
            <button className="view-toggle-btn">📊 Chart View</button>
          </div>
        </div>

        <div className="usage-records-grid">
          {filteredData.map((record) => (
            <div key={record.usage_id} className="usage-record-card">
              <div className="record-header">
                <div className="record-id">
                  <span className="id-label">ID:</span>
                  <span className="id-value">{record.usage_id.slice(0, 8)}...</span>
                </div>
                <div className="record-date">{formatDate(record.usage_date)}</div>
              </div>

              <div className="record-main">
                <div className="patient-info">
                  <div className="patient-name">
                    <span className="name-icon">👤</span>
                    <span className="name-text">{record.individual_name}</span>
                  </div>
                  <div className="patient-location">
                    <span className="location-icon">📍</span>
                    <span className="location-text">{record.patient_location}</span>
                  </div>
                </div>

                <div className="usage-details">
                  <div className="blood-info">
                    <div className={`blood-type-badge ${record.blood_group.replace('+', 'pos').replace('-', 'neg')}`}>
                      {record.blood_group}
                    </div>
                    <div className="volume-info">
                      <span className="volume-number">{record.volume_given_out}</span>
                      <span className="volume-unit">ml</span>
                    </div>
                  </div>

                  <div className="purpose-department">
                    <div className="purpose-info">
                      <span className="purpose-icon">{getPurposeIcon(record.purpose)}</span>
                      <span className="purpose-text">{record.purpose.charAt(0).toUpperCase() + record.purpose.slice(1)}</span>
                    </div>
                    <div 
                      className="department-badge"
                      style={{ backgroundColor: getDepartmentColor(record.department) }}
                    >
                      {record.department.charAt(0).toUpperCase() + record.department.slice(1)}
                    </div>
                  </div>
                </div>
              </div>

              <div className="record-footer">
                <div className="timestamps">
                  <div className="timestamp">
                    <span className="timestamp-label">Created:</span>
                    <span className="timestamp-value">{formatDateTime(record.created_at)}</span>
                  </div>
                  {record.updated_at !== record.created_at && (
                    <div className="timestamp">
                      <span className="timestamp-label">Updated:</span>
                      <span className="timestamp-value">{formatDateTime(record.updated_at)}</span>
                    </div>
                  )}
                </div>
                <div className="record-actions">
                  <button className="record-action-btn view" title="View Details">
                    <span className="action-icon">👁️</span>
                  </button>
                  <button className="record-action-btn edit" title="Edit Record">
                    <span className="action-icon">✏️</span>
                  </button>
                  <button className="record-action-btn report" title="Generate Report">
                    <span className="action-icon">📊</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredData.length === 0 && (
          <div className="no-records">
            <div className="no-records-icon">📋</div>
            <h4>No Records Found</h4>
            <p>Try adjusting your search criteria or filters</p>
          </div>
        )}
      </div>
    </div>
  )
}

const BloodInventoryView = () => {
  const [inventory, setInventory] = useState<BloodInventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedBloodGroup, setSelectedBloodGroup] = useState<string>('')

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const data = await apiService.getBloodInventory()
        setInventory(data)
      } catch (err: any) {
        setError('Failed to load inventory data')
        console.error('Inventory error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchInventory()
  }, [])

  const getStatusClass = (item: BloodInventoryItem) => {
    if (item.available_units === 0) return 'critical'
    if (item.available_units < 20) return 'warning'
    if (item.total_near_expiry > 0) return 'warning'
    return 'good'
  }

  const getStatusText = (item: BloodInventoryItem) => {
    if (item.available_units === 0) return 'Out of Stock'
    if (item.available_units < 20) return 'Low Stock'
    if (item.total_near_expiry > 0) return 'Near Expiry'
    return 'Good'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalStats = inventory.reduce((acc, item) => ({
    totalAvailable: acc.totalAvailable + item.total_available,
    totalUnits: acc.totalUnits + item.available_units,
    totalNearExpiry: acc.totalNearExpiry + item.total_near_expiry,
    totalExpired: acc.totalExpired + item.total_expired
  }), { totalAvailable: 0, totalUnits: 0, totalNearExpiry: 0, totalExpired: 0 })

  if (loading) {
    return (
      <div className="section-view">
        <div className="loading-spinner">Loading inventory...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="section-view">
        <div className="error-message">{error}</div>
      </div>
    )
  }

  return (
    <div className="section-view">
      <div className="dashboard-header">
        <h2>🏥 Blood Inventory</h2>
        <p>Monitor current blood inventory levels and stock status</p>
      </div>

      {/* Summary Stats */}
      <div className="dashboard-grid">
        <div className="dashboard-card stat-card">
          <div className="stat-icon">🩸</div>
          <div className="stat-content">
            <h3>Total Available</h3>
            <div className="stat-number">{totalStats.totalAvailable.toLocaleString()}</div>
            <div className="stat-label">ml</div>
          </div>
        </div>
        <div className="dashboard-card stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h3>Available Units</h3>
            <div className="stat-number">{totalStats.totalUnits}</div>
            <div className="stat-label">units</div>
          </div>
        </div>
        <div className="dashboard-card stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <h3>Near Expiry</h3>
            <div className="stat-number">{totalStats.totalNearExpiry.toLocaleString()}</div>
            <div className="stat-label">ml</div>
          </div>
        </div>
        <div className="dashboard-card stat-card">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <h3>Expired</h3>
            <div className="stat-number">{totalStats.totalExpired.toLocaleString()}</div>
            <div className="stat-label">ml</div>
          </div>
        </div>
      </div>

      {/* Enhanced Inventory Cards */}
      <div className="dashboard-card">
        <div className="inventory-section-header">
          <div className="section-title">
            <h3>🩸 Blood Inventory Overview</h3>
            <p>Real-time blood stock levels across all blood types</p>
          </div>
          <div className="inventory-actions">
            <button className="action-btn refresh-btn" onClick={() => window.location.reload()}>
              <span className="btn-icon">🔄</span>
              <span className="btn-text">Refresh Data</span>
            </button>
            <button className="action-btn export-btn">
              <span className="btn-icon">📊</span>
              <span className="btn-text">Export Report</span>
            </button>
          </div>
        </div>

        <div className="enhanced-inventory-grid">
          {inventory.map((item) => (
            <div key={item.blood_group} className={`enhanced-inventory-card ${getStatusClass(item)}`}>
              {/* Card Header with Blood Type and Status */}
              <div className="card-header">
                <div className="blood-type-section">
                  <div className={`blood-type-circle ${item.blood_group.replace('+', 'pos').replace('-', 'neg')}`}>
                    <span className="blood-type-text">{item.blood_group}</span>
                  </div>
                  <div className="blood-type-info">
                    <h4>Type {item.blood_group}</h4>
                    <span className="compatibility-info">
                      {item.blood_group.includes('+') ? 'Rh Positive' : 'Rh Negative'}
                    </span>
                  </div>
                </div>
                <div className={`status-indicator ${getStatusClass(item)}`}>
                  <div className="status-dot"></div>
                  <span className="status-text">{getStatusText(item)}</span>
                </div>
              </div>

              {/* Main Stats Display */}
              <div className="card-main-stats">
                <div className="primary-stat">
                  <div className="stat-icon">📦</div>
                  <div className="stat-content">
                    <div className="stat-number">{item.available_units}</div>
                    <div className="stat-label">Available Units</div>
                  </div>
                </div>
                
                <div className="volume-indicator">
                  <div className="volume-bar">
                    <div 
                      className="volume-fill" 
                      style={{ 
                        width: `${Math.min((item.available_units / 100) * 100, 100)}%`,
                        backgroundColor: getStatusClass(item) === 'critical' ? '#ef4444' : 
                                       getStatusClass(item) === 'warning' ? '#f59e0b' : '#10b981'
                      }}
                    ></div>
                  </div>
                  <div className="volume-text">
                    {item.total_available.toLocaleString()} ml total
                  </div>
                </div>
              </div>

              {/* Detailed Stats Grid */}
              <div className="card-detail-stats">
                <div className="detail-stat good">
                  <div className="detail-icon">✅</div>
                  <div className="detail-content">
                    <div className="detail-value">{item.total_available.toLocaleString()}</div>
                    <div className="detail-label">Total Available (ml)</div>
                  </div>
                </div>
                
                <div className="detail-stat warning">
                  <div className="detail-icon">⏰</div>
                  <div className="detail-content">
                    <div className="detail-value">{item.total_near_expiry.toLocaleString()}</div>
                    <div className="detail-label">Near Expiry (ml)</div>
                  </div>
                </div>
                
                <div className="detail-stat critical">
                  <div className="detail-icon">❌</div>
                  <div className="detail-content">
                    <div className="detail-value">{item.total_expired.toLocaleString()}</div>
                    <div className="detail-label">Expired (ml)</div>
                  </div>
                </div>
              </div>

              {/* Alert Messages */}
              {item.available_units === 0 && (
                <div className="alert-message critical">
                  <span className="alert-icon">🚨</span>
                  <span className="alert-text">URGENT: Out of stock - Immediate restocking required</span>
                </div>
              )}
              {item.available_units > 0 && item.available_units < 20 && (
                <div className="alert-message warning">
                  <span className="alert-icon">⚠️</span>
                  <span className="alert-text">LOW STOCK: Only {item.available_units} units remaining</span>
                </div>
              )}
              {item.total_near_expiry > 0 && (
                <div className="alert-message warning">
                  <span className="alert-icon">⏰</span>
                  <span className="alert-text">{item.total_near_expiry.toLocaleString()}ml expiring soon</span>
                </div>
              )}

              {/* Card Footer */}
              <div className="card-footer">
                <div className="last-updated-info">
                  <span className="update-icon">🕒</span>
                  <span className="update-text">Updated {formatDate(item.last_updated)}</span>
                </div>
                <div className="card-actions">
                  <button 
                    className="action-btn-small primary"
                    onClick={() => setSelectedBloodGroup(item.blood_group)}
                    title="View detailed information"
                  >
                    <span className="btn-icon">👁️</span>
                    Details
                  </button>
                  <button 
                    className="action-btn-small secondary"
                    title="Request restock"
                  >
                    <span className="btn-icon">📋</span>
                    Request
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Stats Summary */}
        <div className="inventory-summary">
          <div className="summary-item">
            <span className="summary-label">Blood Types in Stock:</span>
            <span className="summary-value">{inventory.filter(item => item.available_units > 0).length}/8</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Critical Alerts:</span>
            <span className="summary-value critical">{inventory.filter(item => item.available_units === 0).length}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Low Stock Warnings:</span>
            <span className="summary-value warning">{inventory.filter(item => item.available_units > 0 && item.available_units < 20).length}</span>
          </div>
        </div>
      </div>

      {/* Detailed Table View */}
      <div className="dashboard-card table-card">
        <h3>Detailed Inventory Table</h3>
        <div className="table-container">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>Blood Group</th>
                <th>Available Units</th>
                <th>Total Available (ml)</th>
                <th>Near Expiry (ml)</th>
                <th>Expired (ml)</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => (
                <tr key={item.blood_group} className={getStatusClass(item)}>
                  <td>
                    <span className={`blood-type-badge ${item.blood_group.replace('+', 'pos').replace('-', 'neg')}`}>
                      {item.blood_group}
                    </span>
                  </td>
                  <td className="units">{item.available_units}</td>
                  <td className="volume">{item.total_available.toLocaleString()}</td>
                  <td className="near-expiry">{item.total_near_expiry.toLocaleString()}</td>
                  <td className="expired">{item.total_expired.toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${getStatusClass(item)}`}>
                      {getStatusText(item)}
                    </span>
                  </td>
                  <td className="last-updated">{formatDate(item.last_updated)}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="view-btn" title="View Details">👁️</button>
                      <button className="edit-btn" title="Edit">✏️</button>
                      <button className="report-btn" title="Generate Report">📊</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

const LowStockAlertsView = () => {
  return (
    <div className="section-view">
      <div className="dashboard-header">
        <h2>⚠️ Low Stock Alerts</h2>
        <p>Critical inventory alerts and notifications</p>
      </div>
      <div className="dashboard-card">
        <h3>Coming Soon</h3>
        <p>Low stock alerts functionality will be implemented here.</p>
      </div>
    </div>
  )
}

const DonorManagementView = () => {
  return (
    <div className="section-view">
      <div className="dashboard-header">
        <h2>👥 Donor Management</h2>
        <p>Manage donor information and donation history</p>
      </div>
      <div className="dashboard-card">
        <h3>Coming Soon</h3>
        <p>Donor management functionality will be implemented here.</p>
      </div>
    </div>
  )
}

const AnalyticsView = () => {
  // Traffic data
  const trafficData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Page Views',
        data: [1200, 1900, 3000, 5000, 2000, 3000, 4500],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
      {
        label: 'Unique Visitors',
        data: [800, 1200, 2000, 3200, 1500, 2100, 2800],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: '#10b981',
        borderWidth: 1,
      },
    ],
  }

  // Conversion rate data
  const conversionData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Conversion Rate (%)',
        data: [2.4, 3.1, 2.8, 3.5, 4.2, 3.8],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // Device usage data
  const deviceData = {
    labels: ['Desktop', 'Mobile', 'Tablet'],
    datasets: [
      {
        data: [60, 35, 5],
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
        borderWidth: 2,
      },
    ],
  }

  // Bounce rate vs session duration scatter data
  const bounceRateData = {
    datasets: [
      {
        label: 'Pages',
        data: [
          { x: 2.1, y: 45 },
          { x: 3.5, y: 38 },
          { x: 1.8, y: 52 },
          { x: 4.2, y: 28 },
          { x: 2.8, y: 41 },
          { x: 5.1, y: 22 },
          { x: 3.9, y: 35 },
          { x: 2.3, y: 48 },
        ],
        backgroundColor: '#3b82f6',
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  }

  // User engagement bubble chart
  const engagementData = {
    datasets: [
      {
        label: 'User Segments',
        data: [
          { x: 20, y: 30, r: 15 }, // New Users
          { x: 40, y: 10, r: 10 }, // Returning Users
          { x: 60, y: 50, r: 20 }, // Power Users
          { x: 80, y: 70, r: 25 }, // Premium Users
          { x: 30, y: 80, r: 12 }, // Mobile Users
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: '#3b82f6',
        borderWidth: 2,
      },
    ],
  }

  return (
    <div className="section-view">
      <h2>Analytics</h2>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Website Traffic</h3>
          <BarChart data={trafficData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Device Usage</h3>
          <DoughnutChart data={deviceData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Bounce Rate vs Session Duration</h3>
          <ScatterChart data={bounceRateData} height={300} />
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Conversion Rate Trend</h3>
          <LineChart data={conversionData} height={250} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>User Engagement Segments</h3>
          <BubbleChart data={engagementData} height={250} />
        </div>
      </div>
    </div>
  )
}

const UsersView = () => {
  // User growth data
  const userGrowthData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'New Users',
        data: [120, 190, 300, 500, 200, 300],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Active Users',
        data: [800, 950, 1200, 1600, 1400, 1650],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // User demographics
  const demographicsData = {
    labels: ['18-24', '25-34', '35-44', '45-54', '55+'],
    datasets: [
      {
        data: [25, 35, 20, 15, 5],
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#8b5cf6',
        ],
        borderWidth: 2,
      },
    ],
  }

  // User activity by day
  const activityData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Daily Active Users',
        data: [1200, 1900, 3000, 5000, 2000, 1500, 1800],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
    ],
  }

  // User satisfaction radar chart
  const satisfactionData = {
    labels: ['Usability', 'Performance', 'Features', 'Support', 'Design', 'Value'],
    datasets: [{
      label: 'User Satisfaction',
      data: [85, 78, 92, 88, 75, 82],
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      borderColor: '#10b981',
      borderWidth: 2,
      pointBackgroundColor: '#10b981',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#10b981'
    }]
  }

  // User engagement scatter plot
  const userEngagementData = {
    datasets: [
      {
        label: 'User Engagement',
        data: [
          { x: 15, y: 85 }, // High engagement, low churn
          { x: 25, y: 75 },
          { x: 35, y: 65 },
          { x: 45, y: 55 },
          { x: 55, y: 45 },
          { x: 65, y: 35 },
          { x: 75, y: 25 }, // Low engagement, high churn
          { x: 20, y: 90 },
          { x: 30, y: 80 },
          { x: 40, y: 70 },
        ],
        backgroundColor: '#8b5cf6',
        pointRadius: 8,
        pointHoverRadius: 10,
      },
    ],
  }

  return (
    <div className="section-view">
      <h2>Users Management</h2>
      <div className="dashboard-grid charts">
        <div className="dashboard-card chart-card">
          <h3>User Growth</h3>
          <AreaChart data={userGrowthData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Age Demographics</h3>
          <PieChart data={demographicsData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>User Satisfaction</h3>
          <RadarChart data={satisfactionData} height={300} />
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Daily Active Users</h3>
          <BarChart data={activityData} height={250} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Engagement vs Churn Rate</h3>
          <ScatterChart data={userEngagementData} height={250} />
        </div>
      </div>
    </div>
  )
}

const ProductsView = () => {
  // Product sales data
  const productSalesData = {
    labels: ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Beauty'],
    datasets: [
      {
        label: 'Units Sold',
        data: [450, 320, 180, 240, 150, 200],
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#8b5cf6',
          '#06b6d4',
        ],
        borderWidth: 1,
      },
    ],
  }

  // Inventory levels
  const inventoryData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'In Stock',
        data: [1200, 1150, 1300, 1100, 1250, 1180],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Low Stock',
        data: [45, 52, 38, 65, 42, 58],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // Top products
  const topProductsData = {
    labels: ['iPhone 15', 'MacBook Pro', 'AirPods', 'iPad', 'Apple Watch'],
    datasets: [
      {
        label: 'Revenue ($)',
        data: [25000, 45000, 12000, 18000, 15000],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
    ],
  }

  // Product performance radar chart
  const productPerformanceData = {
    labels: ['Quality', 'Price', 'Availability', 'Marketing', 'Reviews', 'Support'],
    datasets: [{
      label: 'Product Performance',
      data: [88, 72, 95, 78, 85, 80],
      backgroundColor: 'rgba(245, 158, 11, 0.2)',
      borderColor: '#f59e0b',
      borderWidth: 2,
      pointBackgroundColor: '#f59e0b',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#f59e0b'
    }]
  }

  // Product price vs sales scatter plot
  const priceSalesData = {
    datasets: [
      {
        label: 'Products',
        data: [
          { x: 299, y: 450 }, // Electronics
          { x: 89, y: 320 },  // Clothing
          { x: 25, y: 180 },  // Books
          { x: 150, y: 240 }, // Home & Garden
          { x: 199, y: 150 }, // Sports
          { x: 45, y: 200 },  // Beauty
          { x: 399, y: 380 },
          { x: 129, y: 290 },
          { x: 79, y: 160 },
          { x: 249, y: 220 },
        ],
        backgroundColor: '#ef4444',
        pointRadius: 8,
        pointHoverRadius: 10,
      },
    ],
  }

  return (
    <div className="section-view">
      <h2>Products</h2>
      <div className="dashboard-grid charts">
        <div className="dashboard-card chart-card">
          <h3>Sales by Category</h3>
          <PolarAreaChart data={productSalesData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Top Products Revenue</h3>
          <BarChart data={topProductsData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Product Performance</h3>
          <RadarChart data={productPerformanceData} height={300} />
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Inventory Levels</h3>
          <AreaChart data={inventoryData} height={250} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Price vs Sales Volume</h3>
          <ScatterChart data={priceSalesData} height={250} />
        </div>
      </div>
    </div>
  )
}

const OrdersView = () => {
  // Orders over time
  const ordersTimeData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Orders',
        data: [65, 89, 120, 151, 142, 189],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }

  // Order status distribution
  const orderStatusData = {
    labels: ['Completed', 'Processing', 'Shipped', 'Cancelled'],
    datasets: [
      {
        data: [65, 20, 12, 3],
        backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#ef4444'],
        borderWidth: 2,
      },
    ],
  }

  // Daily orders
  const dailyOrdersData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Orders',
        data: [12, 19, 30, 50, 20, 30, 45],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
    ],
  }

  // Order fulfillment performance radar
  const fulfillmentData = {
    labels: ['Speed', 'Accuracy', 'Quality', 'Communication', 'Packaging', 'Delivery'],
    datasets: [{
      label: 'Fulfillment Performance',
      data: [92, 88, 95, 85, 90, 87],
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      borderColor: '#10b981',
      borderWidth: 2,
      pointBackgroundColor: '#10b981',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#10b981'
    }]
  }

  // Order value vs processing time bubble chart
  const orderValueData = {
    datasets: [
      {
        label: 'Orders',
        data: [
          { x: 50, y: 2, r: 8 },   // Low value, fast processing
          { x: 150, y: 3, r: 12 }, // Medium value, medium processing
          { x: 300, y: 5, r: 15 }, // High value, slower processing
          { x: 75, y: 1.5, r: 10 },
          { x: 200, y: 4, r: 14 },
          { x: 500, y: 8, r: 20 }, // Premium orders
          { x: 100, y: 2.5, r: 11 },
          { x: 250, y: 6, r: 16 },
        ],
        backgroundColor: 'rgba(139, 92, 246, 0.6)',
        borderColor: '#8b5cf6',
        borderWidth: 2,
      },
    ],
  }

  return (
    <div className="section-view">
      <h2>Orders</h2>
      <div className="dashboard-grid charts">
        <div className="dashboard-card chart-card">
          <h3>Order Status</h3>
          <PieChart data={orderStatusData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Daily Orders</h3>
          <BarChart data={dailyOrdersData} height={300} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Fulfillment Performance</h3>
          <RadarChart data={fulfillmentData} height={300} />
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Orders Over Time</h3>
          <AreaChart data={ordersTimeData} height={250} />
        </div>
        <div className="dashboard-card chart-card">
          <h3>Order Value vs Processing Time</h3>
          <BubbleChart data={orderValueData} height={250} />
        </div>
      </div>
    </div>
  )
}

const SettingsView = () => (
  <div className="section-view">
    <h2>Settings</h2>
    <div className="dashboard-grid">
      <div className="dashboard-card">
        <h3>General Settings</h3>
        <div className="settings-form">
          <div className="form-group">
            <label>Company Name</label>
            <input type="text" defaultValue="My Company" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" defaultValue="admin@company.com" />
          </div>
          <button>Save Changes</button>
        </div>
      </div>
    </div>
  </div>
)

export default Dashboard