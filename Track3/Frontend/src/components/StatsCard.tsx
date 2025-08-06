import type { ReactNode } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string
  icon: ReactNode
  trend?: string
  trendUp?: boolean
}

const StatsCard = ({ title, value, icon, trend, trendUp }: StatsCardProps) => {
  return (
    <div className="stats-card">
      <div className="stats-card-header">
        <div className="stats-card-icon-container">
          <div className="stats-card-icon-wrapper">
            <div className="stats-card-icon">{icon}</div>
          </div>
        </div>
        {trend && (
          <div className={`stats-card-trend ${trendUp ? 'trend-up' : 'trend-down'}`}>
            {trendUp ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            {trend}
          </div>
        )}
      </div>
      <div className="stats-card-content">
        <h3 className="stats-card-value">{value}</h3>
        <p className="stats-card-title">{title}</p>
      </div>
    </div>
  )
}

export default StatsCard
