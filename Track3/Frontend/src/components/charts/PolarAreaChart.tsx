import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { PolarArea } from 'react-chartjs-2'

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend)

interface PolarAreaChartProps {
  title?: string
  data: {
    labels: string[]
    datasets: Array<{
      data: number[]
      backgroundColor: string[]
      borderColor?: string[]
      borderWidth?: number
    }>
  }
  height?: number
}

const PolarAreaChart = ({ title, data, height = 200 }: PolarAreaChartProps) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: !!title,
        text: title,
      },
    },
    scales: {
      r: {
        beginAtZero: true,
      },
    },
  }

  return (
    <div style={{ height: `${height}px` }}>
      <PolarArea data={data} options={options} />
    </div>
  )
}

export default PolarAreaChart