<template>
  <div class="bar-chart-container">
    <Bar 
      :data="chartData" 
      :options="chartOptions" 
      class="bar-chart"
    />
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

// 马卡龙色系配色
const MACARON_COLORS = [
  '#FF9AA2', // 粉红
  '#FFB7B2', // 浅粉
  '#FFDAC1', // 浅橙
  '#E2F0CB', // 薄荷绿
  '#B5EAD7', // 浅绿
  '#C7CEEA', // 浅紫
  '#F8B195', // 珊瑚
]

export default {
  name: 'BarChart',
  components: { Bar },
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
    values() {
      return this.labels.map(label => this.data[label])
    },
    chartData() {
      return {
        labels: this.labels.map(label => this.translateEmotion(label)),
        datasets: [
          {
            label: '百分比',
            data: this.values,
            backgroundColor: this.labels.map((_, index) => 
              MACARON_COLORS[index % MACARON_COLORS.length]
            ),
            borderRadius: 8,
            borderWidth: 1,
            borderColor: '#fff'
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: this.data.comment || '',
            font: {
              size: 16,
              weight: 'bold',
              family: "'Helvetica Neue', 'Arial', sans-serif"
            },
            padding: {
              top: 10,
              bottom: 20
            },
            color: '#555'
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            titleColor: '#333',
            bodyColor: '#555',
            borderColor: '#ddd',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              label: context => `${context.parsed.y.toFixed(2)}%`,
              title: (items) => {
                return this.translateEmotion(items[0].label)
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: val => val + '%',
              color: '#777',
              font: {
                family: "'Helvetica Neue', 'Arial', sans-serif"
              }
            },
            grid: {
              drawBorder: false,
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#555',
              font: {
                family: "'Helvetica Neue', 'Arial', sans-serif",
                weight: 'bold'
              }
            }
          }
        }
      }
    }
  },
  methods: {
    translateEmotion(emotion) {
      const translations = {
        fear: '恐惧',
        angry: '愤怒',
        neutral: '中性',
        happy: '快乐',
        sad: '悲伤',
        disgust: '厌恶',
        surprise: '惊讶'
      }
      return translations[emotion] || emotion
    }
  }
}
</script>

<style scoped>
.bar-chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.bar-chart {
  width: 100%;
  height: 100%;
}
</style>