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
import LoadingSpinner from './LoadingSpinner'
import { 
  useDashboardStats, 
  useRevenueData, 
  useCategorySales, 
  useRecentActivity,
  useTrafficData,
  useConversionData,
  useDeviceUsage,
  useUserGrowth,
  useUserDemographics,
  useProductSales,
  useInventoryLevels,
  useOrdersTimeline,
  useOrderStatusDistribution,
  useDailyOrders
} from '../hooks/useApi'

interface DashboardProps {
  activeSection: string
}

const DashboardWithApi = ({ activeSection }: DashboardProps) => {
  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardHome />
      case 'analytics':
        return <AnalyticsView />
      case 'users':
        return <UsersView />
      case 'products':
        return <ProductsView />
      case 'orders':
        return <OrdersView />
      case 'settings':
        return <SettingsView />
      default:
        return <DashboardHome />
    }
  }

  return <div className="dashboard-content">{renderContent()}</div>
}

const DashboardHome = () => {
  const { data: stats, isLoading: statsLoading, error: statsError } = useDashboardStats()
  const { data: revenueData, isLoading: revenueLoading } = useRevenueData()
  const { data: categorySales, isLoading: categoryLoading } = useCategorySales()
  const { data: recentActivity, isLoading: activityLoading } = useRecentActivity(5)

  if (statsLoading) {
    return <LoadingSpinner size="large" message="Loading dashboard..." />
  }

  if (statsError) {
    return (
      <div className="error-state">
        <div className="error-icon">⚠️</div>
        <div className="error-message">Failed to load dashboard data</div>
        <button className="retry-button" onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    )
  }

  // Transform API data for charts
  const revenueChartData = revenueData ? {
    labels: revenueData.labels,
    datasets: [
      {
        label: 'Revenue',
        data: revenueData.data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  } : null

  const salesChartData = categorySales ? {
    labels: categorySales.map(item => item.category),
    datasets: [
      {
        data: categorySales.map(item => item.percentage),
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
  } : null

  return (
    <>
      <div className="dashboard-grid">
        {stats && [
          { label: 'Total Revenue', value: `$${stats.totalRevenue.toLocaleString()}`, change: stats.revenueChange, trend: stats.revenueChange.startsWith('+') ? 'up' : 'down' },
          { label: 'Orders', value: stats.orders.toLocaleString(), change: stats.ordersChange, trend: stats.ordersChange.startsWith('+') ? 'up' : 'down' },
          { label: 'Customers', value: stats.customers.toLocaleString(), change: stats.customersChange, trend: stats.customersChange.startsWith('+') ? 'up' : 'down' },
          { label: 'Products', value: stats.products.toLocaleString(), change: stats.productsChange, trend: stats.productsChange.startsWith('+') ? 'up' : 'down' },
        ].map((stat, index) => (
          <div key={index} className="dashboard-card stat-card">
            <h3>{stat.label}</h3>
            <div className="stat-number">{stat.value}</div>
            <div className={`stat-change ${stat.trend}`}>
              {stat.trend === 'up' ? '↗️' : '↘️'} {stat.change}
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Revenue Trend</h3>
          {revenueLoading ? (
            <div className="chart-loading">
              <LoadingSpinner size="small" message="Loading chart..." />
            </div>
          ) : revenueChartData ? (
            <AreaChart data={revenueChartData} height={250} />
          ) : (
            <div className="chart-loading">No data available</div>
          )}
        </div>

        <div className="dashboard-card chart-card">
          <h3>Sales by Category</h3>
          {categoryLoading ? (
            <div className="chart-loading">
              <LoadingSpinner size="small" message="Loading chart..." />
            </div>
          ) : salesChartData ? (
            <PieChart data={salesChartData} height={250} />
          ) : (
            <div className="chart-loading">No data available</div>
          )}
        </div>

        <div className="dashboard-card chart-card">
          <h3>Market Share</h3>
          <PolarAreaChart data={{
            labels: ['Q1', 'Q2', 'Q3', 'Q4'],
            datasets: [{
              data: [30, 45, 35, 50],
              backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
              borderWidth: 2,
            }]
          }} height={250} />
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Performance Metrics</h3>
          <RadarChart data={{
            labels: ['Sales', 'Marketing', 'Support', 'Development', 'Design', 'Operations'],
            datasets: [{
              label: 'Current Quarter',
              data: [85, 75, 90, 80, 70, 85],
              backgroundColor: 'rgba(59, 130, 246, 0.2)',
              borderColor: '#3b82f6',
              borderWidth: 2,
              pointBackgroundColor: '#3b82f6',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: '#3b82f6'
            }]
          }} height={250} />
        </div>

        <div className="dashboard-card">
          <h3>Recent Activity</h3>
          {activityLoading ? (
            <LoadingSpinner size="small" message="Loading activity..." />
          ) : (
            <div className="recent-activity">
              {recentActivity?.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-content">
                    <div className="activity-title">{activity.action}</div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}

const AnalyticsView = () => {
  const { data: trafficData, isLoading: trafficLoading } = useTrafficData()
  const { data: conversionData, isLoading: conversionLoading } = useConversionData()
  const { data: deviceData, isLoading: deviceLoading } = useDeviceUsage()

  // Transform API data for charts
  const trafficChartData = trafficData ? {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Page Views',
        data: trafficData.pageViews,
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
      {
        label: 'Unique Visitors',
        data: trafficData.uniqueVisitors,
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: '#10b981',
        borderWidth: 1,
      },
    ],
  } : null

  const conversionChartData = conversionData ? {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Conversion Rate (%)',
        data: conversionData,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  } : null

  const deviceChartData = deviceData ? {
    labels: deviceData.map(item => item.device),
    datasets: [
      {
        data: deviceData.map(item => item.percentage),
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
        borderWidth: 2,
      },
    ],
  } : null

  return (
    <div className="section-view">
      <h2>Analytics</h2>
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Website Traffic</h3>
          {trafficLoading ? (
            <div className="chart-loading">
              <LoadingSpinner size="small" message="Loading traffic data..." />
            </div>
          ) : trafficChartData ? (
            <BarChart data={trafficChartData} height={300} />
          ) : (
            <div className="chart-loading">No data available</div>
          )}
        </div>
        
        <div className="dashboard-card chart-card">
          <h3>Device Usage</h3>
          {deviceLoading ? (
            <div className="chart-loading">
              <LoadingSpinner size="small" message="Loading device data..." />
            </div>
          ) : deviceChartData ? (
            <DoughnutChart data={deviceChartData} height={300} />
          ) : (
            <div className="chart-loading">No data available</div>
          )}
        </div>
        
        <div className="dashboard-card chart-card">
          <h3>Bounce Rate vs Session Duration</h3>
          <ScatterChart data={{
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
          }} height={300} />
        </div>
      </div>
      
      <div className="dashboard-grid">
        <div className="dashboard-card chart-card">
          <h3>Conversion Rate Trend</h3>
          {conversionLoading ? (
            <div className="chart-loading">
              <LoadingSpinner size="small" message="Loading conversion data..." />
            </div>
          ) : conversionChartData ? (
            <LineChart data={conversionChartData} height={250} />
          ) : (
            <div className="chart-loading">No data available</div>
          )}
        </div>
        
        <div className="dashboard-card chart-card">
          <h3>User Engagement Segments</h3>
          <BubbleChart data={{
            datasets: [
              {
                label: 'User Segments',
                data: [
                  { x: 20, y: 30, r: 15 },
                  { x: 40, y: 10, r: 10 },
                  { x: 60, y: 50, r: 20 },
                  { x: 80, y: 70, r: 25 },
                  { x: 30, y: 80, r: 12 },
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: '#3b82f6',
                borderWidth: 2,
              },
            ],
          }} height={250} />
        </div>
      </div>
    </div>
  )
}

// Keep the other views as they were for now
const UsersView = () => <div>Users View - API integration coming soon</div>
const ProductsView = () => <div>Products View - API integration coming soon</div>
const OrdersView = () => <div>Orders View - API integration coming soon</div>
const SettingsView = () => <div>Settings View - API integration coming soon</div>

export default DashboardWithApi