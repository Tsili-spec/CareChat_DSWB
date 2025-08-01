import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Scatter } from 'react-chartjs-2'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)

interface ScatterChartProps {
  title?: string
  data: {
    datasets: Array<{
      label: string
      data: Array<{ x: number; y: number }>
      backgroundColor: string
      borderColor?: string
      pointRadius?: number
      pointHoverRadius?: number
    }>
  }
  height?: number
}

const ScatterChart = ({ title, data, height = 200 }: ScatterChartProps) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: !!title,
        text: title,
      },
    },
    scales: {
      x: {
        type: 'linear' as const,
        position: 'bottom' as const,
        grid: {
          color: '#e2e8f0',
        },
      },
      y: {
        grid: {
          color: '#e2e8f0',
        },
      },
    },
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Scatter data={data} options={options} />
    </div>
  )
}

export default ScatterChart