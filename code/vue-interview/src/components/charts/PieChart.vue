<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script>
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  ArcElement
)

export default {
  name: 'PieChart',
  components: {
    Doughnut
  },
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  computed: {
    labels() {
      return Object.keys(this.data).filter(key => key !== 'comment')
    },
    chartData() {
      const values = this.labels.map(label => this.data[label])

      const backgroundColors = [
        '#FADADD',  // 珊瑚粉
        '#E6E6FA', // 紫
        '#D6F5D6', // 浅绿
        '#AEDFF7', // 淡蓝
        '#FFF4B2', // 浅黄
        '#FFC1CC', // 淡粉
      ]

      return {
        labels: this.labels,
        datasets: [
          {
            data: values,
            backgroundColor: backgroundColors.slice(0, this.labels.length),
            hoverOffset: 10
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: this.data.comment || '分析图',
            font: {
              size: 16
            }
          },
          legend: {
            position: 'bottom'
          }
        },
        // 自动判断是否为甜甜圈
        cutout: this.labels.length > 2 ? '50%' : 0
      }
    }
  }
}
</script>
