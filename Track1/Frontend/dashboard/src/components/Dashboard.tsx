import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { Download, TrendingUp, MessageSquare, Calendar, AlertTriangle } from 'lucide-react'
import StatsCard from './StatsCard'
import ChartCard from './ChartCard'

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

const Dashboard = () => {
  const [data, setData] = useState<ApiData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
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
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">CareChat Analytics</h1>
          <p className="text-gray-600 mt-1">Hospital feedback and reminder insights</p>
        </div>
        <button
          onClick={handleExport}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Download className="h-4 w-4" />
          Export Data
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Sentiment Analysis */}
        <ChartCard title="Sentiment Analysis" description="Overall feedback sentiment distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
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
          <ResponsiveContainer width="100%" height={300}>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Negative Topics */}
        <ChartCard title="Common Issues" description="Most frequently reported negative topics">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topicData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="topic" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="count" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Reminders Timeline */}
        <ChartCard title="Daily Reminders" description="Reminder activity over time">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={reminderData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}

export default Dashboard