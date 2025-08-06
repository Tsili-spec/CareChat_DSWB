import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { Download, TrendingUp, MessageSquare, Calendar, AlertTriangle } from 'lucide-react'
import StatsCard from './StatsCard'
import ChartCard from './ChartCard'
import './FeedbackAnalytics.css'

interface ApiData {
  rating_trends: {
    [key: string]: {
      [rating: string]: number
    }
  }
  sentiment_summary: {
    negative: number
    neutral: number
    positive: number
  }
  negative_topic_counts: {
    [topic: string]: number
  }
  reminders_by_day: {
    [date: string]: number
  }
}

const FeedbackAnalytics = () => {
  const [data, setData] = useState<ApiData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Note: You'll need to replace this with the actual Track3 feedback API endpoint
      const response = await fetch('https://carechat-dswb-v8ex.onrender.com/api/summary')
      if (!response.ok) {
        throw new Error('Failed to fetch data')
      }
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      // Note: You'll need to replace this with the actual Track3 export API endpoint
      const response = await fetch('https://carechat-dswb-v8ex.onrender.com/api/export')
      if (!response.ok) {
        throw new Error('Failed to export data')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'feedback_export.csv'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

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

  if (loading) {
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
            <div className="menu-item" onClick={navigateToDashboard} title="Dashboard">
              <span className="menu-icon">🏠</span>
            </div>
            <div className="menu-item" onClick={navigateToForecasting} title="Forecasting">
              <span className="menu-icon">📊</span>
            </div>
            <div className="menu-item active" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
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
          <div className="loading-container">
            <div className="loading-spinner"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
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
            <div className="menu-item" onClick={navigateToDashboard} title="Dashboard">
              <span className="menu-icon">🏠</span>
            </div>
            <div className="menu-item" onClick={navigateToForecasting} title="Forecasting">
              <span className="menu-icon">📊</span>
            </div>
            <div className="menu-item active" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
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
          <div className="error-container">
            <div className="error-content">
              <AlertTriangle className="error-icon" />
              <h2 className="error-title">Error Loading Dashboard</h2>
              <p className="error-message">{error}</p>
              <button
                onClick={fetchData}
                className="retry-button"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!data) return null

  // Process data for charts
  const sentimentData = [
    { name: 'Positive', value: data.sentiment_summary.positive, color: '#10b981' },
    { name: 'Neutral', value: data.sentiment_summary.neutral, color: '#f59e0b' },
    { name: 'Negative', value: data.sentiment_summary.negative, color: '#ef4444' }
  ]

  const ratingData = Object.entries(data.rating_trends.Unknown || {}).map(([rating, count]) => ({
    rating: `${rating} Star${rating !== '1' ? 's' : ''}`,
    count
  }))

  const topicData = Object.entries(data.negative_topic_counts).map(([topic, count]) => ({
    topic: topic.replace(/[{}]/g, '').replace(/_/g, ' '),
    count
  }))

  const reminderData = Object.entries(data.reminders_by_day).map(([date, count]) => ({
    date: new Date(date).toLocaleDateString(),
    count
  }))

  const totalFeedback = data.sentiment_summary.positive + data.sentiment_summary.neutral + data.sentiment_summary.negative
  const totalReminders = Object.values(data.reminders_by_day).reduce((sum, count) => sum + count, 0)
  const totalTopics = Object.values(data.negative_topic_counts).reduce((sum, count) => sum + count, 0)

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
          <div className="menu-item" onClick={navigateToDashboard} title="Dashboard">
            <span className="menu-icon">🏠</span>
          </div>
          <div className="menu-item" onClick={navigateToForecasting} title="Forecasting">
            <span className="menu-icon">📊</span>
          </div>
          <div className="menu-item active" onClick={navigateToFeedbackAnalytics} title="Feedback Analytics">
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

        {/* Analytics Content */}
        <div className="analytics-content">
          {/* Header */}
          <div className="analytics-header">
            <div className="analytics-title-section">
              <h1>CareChat Analytics</h1>
              <p>Hospital feedback and reminder insights</p>
            </div>
            <button
              onClick={handleExport}
              className="export-button"
            >
              <Download className="h-4 w-4" />
              Export Data
            </button>
          </div>

          {/* Stats Cards */}
          <div className="stats-grid">
            <StatsCard
              title="Total Feedback"
              value={totalFeedback.toString()}
              icon={<MessageSquare className="h-6 w-6" />}
              trend="+12%"
              trendUp={true}
            />
            <StatsCard
              title="Active Reminders"
              value={totalReminders.toString()}
              icon={<Calendar className="h-6 w-6" />}
              trend="+8%"
              trendUp={true}
            />
            <StatsCard
              title="Negative Issues"
              value={totalTopics.toString()}
              icon={<AlertTriangle className="h-6 w-6" />}
              trend="-5%"
              trendUp={false}
            />
            <StatsCard
              title="Satisfaction Rate"
              value={`${Math.round((data.sentiment_summary.positive / totalFeedback) * 100)}%`}
              icon={<TrendingUp className="h-6 w-6" />}
              trend="+3%"
              trendUp={true}
            />
          </div>

          {/* Charts Grid */}
          <div className="charts-grid">
            {/* Sentiment Analysis */}
            <ChartCard title="Sentiment Analysis" description="Overall feedback sentiment distribution">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Rating Distribution */}
            <ChartCard title="Rating Distribution" description="Breakdown of user ratings">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={ratingData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="rating" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <div className="charts-grid-bottom">
            {/* Negative Topics */}
            <ChartCard title="Common Issues" description="Most frequently reported negative topics">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={topicData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="topic" type="category" width={120} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Reminders Timeline */}
            <ChartCard title="Daily Reminders" description="Reminder activity over time">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={reminderData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FeedbackAnalytics
