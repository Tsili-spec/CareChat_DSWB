import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend)

interface DoughnutChartProps {
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

const DoughnutChart = ({ title, data, height = 200 }: DoughnutChartProps) => {
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
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Doughnut data={data} options={options} />
    </div>
  )
}

export default DoughnutChart