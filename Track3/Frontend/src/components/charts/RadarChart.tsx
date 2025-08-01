import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar } from 'react-chartjs-2'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

interface RadarChartProps {
  title?: string
  data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor: string
      borderColor: string
      borderWidth?: number
      pointBackgroundColor?: string
      pointBorderColor?: string
      pointHoverBackgroundColor?: string
      pointHoverBorderColor?: string
    }>
  }
  height?: number
}

const RadarChart = ({ title, data, height = 200 }: RadarChartProps) => {
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
      r: {
        angleLines: {
          display: true,
        },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
  }

  return (
    <div style={{ height: `${height}px` }}>
      <Radar data={data} options={options} />
    </div>
  )
}

export default RadarChart