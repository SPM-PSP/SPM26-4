<template>
  <Radar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
)

export default {
  name: 'RadarChart',
  components: {
    Radar
  },
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  computed: {
    chartData() {
      const labels = Object.keys(this.data).filter(key => key !== 'comment')
      const values = labels.map(label => this.data[label])
      return {
        labels,
        datasets: [
          {
            label: '岗位能力得分',
            data: values,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            fill: true
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 20,
              backdropColor: 'transparent'
            },
            pointLabels: {
              font: {
                size: 14
              }
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: '岗位能力雷达图',
            font: {
              size: 18
            }
          },
          legend: {
            display: false
          }
        }
      }
    }
  }
}
</script>
