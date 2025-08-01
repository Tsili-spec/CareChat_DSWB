import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Pie } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend)

interface PieChartProps {
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

const PieChart = ({ title, data, height = 200 }: PieChartProps) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: !!title,
        text: title,
      },
    },
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Pie data={data} options={options} />
    </div>
  )
}

export default PieChart