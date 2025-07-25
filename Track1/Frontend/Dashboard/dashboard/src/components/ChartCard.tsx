import type { ReactNode } from 'react'

interface ChartCardProps {
  title: string
  description?: string
  children: ReactNode
}

const ChartCard = ({ title, description, children }: ChartCardProps) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && (
          <p className="text-gray-600 text-sm mt-1">{description}</p>
        )}
      </div>
      {children}
    </div>
  )
}

export default ChartCard