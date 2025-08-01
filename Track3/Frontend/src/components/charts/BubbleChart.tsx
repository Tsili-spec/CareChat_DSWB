import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bubble } from 'react-chartjs-2'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

interface BubbleChartProps {
  title?: string
  data: {
    datasets: Array<{
      label: string
      data: Array<{ x: number; y: number; r: number }>
      backgroundColor: string
      borderColor?: string
      borderWidth?: number
    }>
  }
  height?: number
}

const BubbleChart = ({ title, data, height = 200 }: BubbleChartProps) => {
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
      <Bubble data={data} options={options} />
    </div>
  )
}

export default BubbleChart