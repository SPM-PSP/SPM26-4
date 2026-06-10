<template>
  <div class="chart-container">
    <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
    <div v-else class="no-data">加载数据中...</div>
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
)

export default {
  name: 'HorizontalBarChart',
  components: { Bar },
  props: {
    stutterData: {
      type: Object,
      required: true,
      validator: value => {
        return 'nonstutter' in value &&
               'repetition' in value &&
               'prolongation' in value &&
               'blocks' in value
      }
    }
  },
  computed: {
    chartData() {
      if (!this.stutterData) return null

      return {
        labels: ['流畅', '重复', '延长', '阻塞'],
        datasets: [{
          label: '出现概率 (%)',
          data: [
            this.stutterData.nonstutter * 100,
            this.stutterData.repetition * 100,
            this.stutterData.prolongation * 100,
            this.stutterData.blocks * 100
          ],
          backgroundColor: [
            '#FFDAB9', // 浅橙
            '#E6E6FA',  // 淡紫
            '#FFB6C1', // 粉红
            '#B0E0E6', // 粉蓝
          ],
          borderRadius: 8,
          barThickness: 24
        }]
      }
    },
    chartOptions() {
      return {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#333',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              label: (context) => `${context.label}: ${context.parsed.x.toFixed(2)}%`
            }
          }
        },
        layout: {
          padding: {
            top: 10,
            bottom: 10,
            left: 20,
            right: 20
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: (value) => `${value}%`,
              color: '#444',
              font: {
                size: 13
              }
            },
            grid: {
              drawTicks: false,
              color: '#f0f0f0'
            }
          },
          y: {
            ticks: {
              color: '#444',
              font: {
                size: 13
              }
            },
            grid: {
              display: false
            }
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
  padding: 12px 0;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  color: #999;
  font-size: 14px;
}
</style>
