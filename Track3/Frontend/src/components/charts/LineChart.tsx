import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface LineChartProps {
  title?: string
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      borderColor: string
      backgroundColor: string
      tension?: number
    }>
  }
  height?: number
}

const LineChart = ({ title, data, height = 200 }: LineChartProps) => {
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
      y: {
        beginAtZero: true,
        grid: {
          color: '#e2e8f0',
        },
      },
      x: {
        grid: {
          color: '#e2e8f0',
        },
      },
    },
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Line data={data} options={options} />
    </div>
  )
}

export default LineChart