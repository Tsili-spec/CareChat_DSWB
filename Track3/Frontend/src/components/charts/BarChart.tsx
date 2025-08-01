import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface BarChartProps {
  title?: string
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor: string | string[]
      borderColor?: string | string[]
      borderWidth?: number
    }>
  }
  height?: number
}

const BarChart = ({ title, data, height = 200 }: BarChartProps) => {
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
      <Bar data={data} options={options} />
    </div>
  )
}

export default BarChart