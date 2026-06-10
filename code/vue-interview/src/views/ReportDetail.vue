<template>
  <div v-if="reportData" class="report-wrapper" ref="reportRef">
    <!-- 顶部按钮（支持报告下载） -->
    <div class="report-header">
      <button class="btn btn-success" @click="downloadPDF">
        <i class="icon-download"></i> 下载报告 (PDF)
      </button>
      <button class="btn btn-default" @click="goBack">
        <i class="icon-back"></i> 返回个人中心
      </button>
    </div>

    <!-- 报告正文 -->
    <div class="report-container">
      <!-- 视频信息 -->
      <div class="video-info-section">
        <div class="video-info-item">
          <span class="info-label">视频编号：</span>
          <span class="info-value">{{ reportData.videoID }}</span>
        </div>
        <div class="video-info-item">
          <span class="info-label">面试时间：</span>
          <span class="info-value">{{ formatDate(reportData.datetime) }}</span>
        </div>
        <div class="video-info-item">
          <span class="info-label">应聘职位：</span>
          <span class="info-value">{{ reportData.job }}</span>
        </div>
      </div>

      <div class="report-header-section">
        <h1 class="report-title">面试分析综合报告</h1>
        <div class="divider"></div>
        <p class="report-summary" v-html="formatSummary(reportData.summary)"></p>
      </div>

      <!-- 雷达图部分 -->
      <section class="report-section card">
        <h2 class="section-title">
          <i class="icon-chart"></i> 岗位能力雷达图
        </h2>
        <div class="chart-container">
          <RadarChart :data="reportData.radarCharData" />
        </div>
      </section>

      <div class="grid-container">
        <!-- 身体姿态分析 -->
        <section class="report-section card">
          <h2 class="section-title">
            <i class="icon-pose"></i> 身体姿态分析
          </h2>
          <div class="chart-container pie-chart-container">
            <PieChart :data="reportData.pose" />
          </div>
        </section>

        <!-- 面部情绪分析 -->
        <section class="report-section card">
          <h2 class="section-title">
            <i class="icon-emotion"></i> 面部情绪分析
          </h2>
          <div class="chart-container">
            <BarChart :data="reportData.emotion" />
          </div>
        </section>
      </div>

      <div class="grid-container">
         <!-- 眼神接触分析 -->
         <section class="report-section card">
          <h2 class="section-title">
            <i class="icon-eye"></i> 眼神接触分析
          </h2>
          <div class="chart-container pie-chart-container">
            <PieChart :data="reportData.eye_contact" />
          </div>
        </section>
      </div>

      <!-- 言语分析部分（流畅度、语调、语速） -->
      <section class="report-section card">
        <h2 class="section-title">
          <i class="icon-speech"></i> 言语分析
        </h2>
        
        <div class="sub-section">
          <h3>流畅度分析</h3>
          <div class="chart-container">
            <HorizontalBarChart :stutterData="reportData.stutter_speed_rhythm.stutter_analysis" />
          </div>
        </div>

      <div class="sub-section">
        <h3>语调分析</h3>
        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-value">{{ reportData.stutter_speed_rhythm.rhythm_analysis.score }}</div>
            <div class="metric-label">综合评分</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ reportData.stutter_speed_rhythm.rhythm_analysis.description }}</div>
            <div class="metric-label">评估结果</div>
          </div>
        </div>
      </div>

      <div class="sub-section">
        <h3>语速分析</h3>
        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-value">{{ reportData.stutter_speed_rhythm.speed_analysis.score }}</div>
            <div class="metric-label">综合评分</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ reportData.stutter_speed_rhythm.speed_analysis.words_per_minute }}</div>
            <div class="metric-label">字/分钟</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ reportData.stutter_speed_rhythm.speed_analysis.description }}</div>
            <div class="metric-label">评估结果</div>
          </div>
        </div>
      </div>
      </section>

      <!-- 手部与身体移动 -->
      <section class="report-section card">
        <h2 class="section-title">
            <i class="icon-movement"></i> 手部与身体移动
        </h2>
        <div class="movement-analysis">
            <div class="movement-section">
            <h3>手部移动分析</h3>
            <div class="metrics-grid">
                <div class="metric-item">
                  <div class="metric-value">{{ reportData.hand_movement.total_movement.toFixed(2) }}</div>
                  <div class="metric-label">手部总移动量</div>
                </div>
                <div class="metric-item">
                  <div class="metric-value">{{ reportData.hand_movement.average_movement_per_frame.toFixed(2) }}</div>
                  <div class="metric-label">平均每帧移动量</div>
                </div>
            </div>
            </div>
            
            <div class="movement-section">
            <h3>身体移动分析</h3>
            <div class="metrics-grid">
                <div class="metric-item">
                  <div class="metric-value">{{ reportData.object_tracker.total_distance.toFixed(2) }}</div>
                  <div class="metric-label">身体总移动距离</div>
                </div>
                <div class="metric-item">
                  <div class="metric-value">{{ reportData.object_tracker.average_distance_per_frame.toFixed(2) }}</div>
                  <div class="metric-label">平均每帧移动距离</div>
                </div>
            </div>
            </div>
        </div>
        
        <div class="assessment-box">
            <p>{{ reportData.object_tracker.assessment }}</p>
        </div>
      </section>
      <!-- 个性化学习推荐 -->
      <section class="report-section card" v-if="reportData.study_route && reportData.study_route.recommendations.length > 0">
        <h2 class="section-title">
          <i class="icon-recommend"></i> 个性化学习推荐
        </h2>
        <div class="recommendations-list">
          <div v-for="(item, index) in reportData.study_route.recommendations" :key="index" class="recommendation-item">
            <!-- 图片部分 -->
            <a :href="item.url" target="_blank" class="recommendation-image-link">
              <div class="recommendation-image">
                <img :src="getImageUrl(index)" :alt="item.reason + ' 推荐内容图片'">
              </div>
            </a>
            <!-- 文字部分 -->
            <div class="recommendation-content">
              <span class="recommendation-type">{{ item.type }}</span>
              <a :href="item.url" target="_blank" class="recommendation-link">{{ item.reason }}</a>
              <div class="recommendation-reason">
                <span class="reason-label">内容：</span>
                <span class="recommendation-title-text">{{ item.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 综合评分部分 -->
      <section class="report-section score-section card">
        <h2 class="section-title">
          <i class="icon-score"></i> 综合评分
        </h2>
        <div class="score-container">
          <div class="score-circle" :style="scoreCircleStyle">
            <span class="score-value">{{ reportData.overall_score }}</span>
            <span class="score-total">/100</span>
          </div>
          <div class="score-feedback">
            根据您的面试表现，我们为您提供了详细的改进建议。继续努力，您会做得更好！
          </div>
        </div>
      </section>
    </div>
  </div>
  <!-- 加载状态提示-->
  <div v-else class="loading-container">
    <p class="loading-text">正在加载报告数据...</p>
    <p class="loading-subtext">如果长时间无法加载，请确保您是从个人中心点击“查看报告”进入的。</p>
    <button class="btn btn-default" @click="goBack">返回个人中心</button>
  </div>
</template>

<script>
import RadarChart from '@/components/charts/RadarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import html2pdf from 'html2pdf.js';

export default {
  name: 'ReportDetail',
  components: {
    RadarChart,
    PieChart,
    BarChart,
    HorizontalBarChart
  },
  data() {
    return {
      reportData: null
    }
  },
  created() {
    const dataStr = localStorage.getItem('reportData')
    if (dataStr) {
      try {
        this.reportData = JSON.parse(dataStr)
        console.log("成功加载并解析报告数据: ", this.reportData);
      } catch (e) {
        console.error("解析报告数据失败: ", e);
        this.$router.push({ name: 'Profile' });
      }
    } else {
      console.error("在 localStorage 中未找到报告数据。");
    }
  },
  computed: {
    scoreCircleStyle() {
      if (!this.reportData) return {};
      const score = this.reportData.overall_score;
      let color = '#A5D6A7'; 
      if (score < 80 && score >= 60) {
        color = '#FFE082'; 
      } else if (score < 60) {
        color = '#EF9A9A'; 
      }
      return {
        '--progress': `${score}%`,
        background: `conic-gradient(${color} 0% ${score}%, #eee ${score}% 100%)`
      };
    }
  },

  methods: {
    formatSummary(summaryText) {
      if (!summaryText) return '';
      return summaryText.replace(/\n/g, '<br />');
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
      }).replace(/\//g, '-');
    },
    goBack() {
      const accountID = this.reportData?.accountID || localStorage.getItem("account");
      this.$router.push({ name: 'Profile', query: { accountID } });
    },
    async downloadPDF() {
      const el = this.$refs.reportRef;
      if (!el) return;
      const headerEl = el.querySelector('.report-header');
      if (headerEl) headerEl.style.display = 'none';
      try {
        const opt = {
          margin: 0.2, filename: '面试分析报告.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
          jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        };
        await html2pdf().set(opt).from(el).save();
      } catch (err) {
        console.error('PDF 导出失败:', err);
      } finally {
        if (headerEl) headerEl.style.display = '';
      }
    },
    getImageUrl(index) {
      const imageNumber = (index % 10) + 1;
      try {
        return require(`../assets/img/${imageNumber}.png`);
      } catch (e) {
        console.error(`无法加载图片: ../assets/img/${imageNumber}.png`, e);
        return '';
      }
    }
  }
}
</script>

<style scoped>
:root {
  --primary-color: #36a2eb;
  --secondary-color: #4bc0c0;
  --text-color: #333;
  --light-text: #666;
  --border-color: #eaeaea;
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  --transition: all 0.3s ease;
}
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
  text-align: center;
}
.loading-text {
  font-size: 24px;
  font-weight: 500;
  color: var(--primary-color);
}
.loading-subtext {
  font-size: 16px;
  color: var(--light-text);
  margin-top: 10px;
  margin-bottom: 30px;
}
.report-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f9fafc;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: var(--text-color);
}
.report-header {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-bottom: 30px;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  border: none;
  font-size: 14px;
  margin: 0 5px;
}
.btn i {
  margin-right: 8px;
  font-size: 16px;
}
.btn-success {
  background-color: #4CAF50;
  color: white;
}
.btn-success:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
}
.btn-default {
  background-color: white;
  color: #555;
  border: 1px solid #ddd;
}
.btn-default:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
}
.video-info-section {
  background: #f0f7ff;
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
.video-info-item {
  display: flex;
  align-items: center;
}
.info-label {
  font-weight: 600;
  color: var(--primary-color);
}
.info-value {
  color: var(--text-color);
}
.report-container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: var(--card-shadow);
}
.report-header-section {
  text-align: center;
  margin-bottom: 40px;
}
.report-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 20px;
}
.divider {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  margin: 0 auto 20px;
  border-radius: 2px;
}
.report-summary {
  font-size: 16px;
  line-height: 1.8;
  color: var(--light-text);
  max-width: 800px;
  margin: 0 auto;
  text-align: left;
  text-indent: 2em;
}
.card {
  background: white;
  border-radius: 10px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: var(--card-shadow);
  transition: var(--transition);
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--primary-color);
  display: flex;
  align-items: center;
}
.section-title i {
  margin-right: 10px;
  font-size: 24px;
}
.chart-container {
  height: 400px;
  margin-top: 20px;
}
.report-section {
  margin-bottom: 30px;
}
.chart-container {
  height: 400px;
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.section-title + .chart-container {
  height: 500px;
}
.pie-chart-container {
  width: 100%;
  max-width: 400px;
  height: 400px;
  margin: 0 auto;
}
.sub-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 0;
  margin-bottom: 15px;
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}
.metric-item {
  text-align: center;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
}
.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 5px;
  white-space: normal;
  word-break: break-word;
}
.metric-label {
  font-size: 12px;
  color: var(--light-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.metric-item:nth-child(2) .metric-value,
.metric-item:nth-child(3) .metric-value {
  font-size: 20px;
  line-height: 1.3;
}
.assessment-box {
  background: #f0f7ff;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
  font-size: 15px;
  line-height: 1.6;
}
.movement-analysis {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.movement-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 15px;
}
.movement-section h3 {
  margin-top: 0;
  color: var(--primary-color);
  font-size: 16px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.recommendation-item {
  display: flex;
  align-items: flex-start; 
  gap: 20px;
  padding: 20px;
  background: #fdfdfd;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
}
.recommendation-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(54, 162, 235, 0.15);
}
.recommendation-image-link {
  flex-shrink: 0;
  display: block;
  text-decoration: none;
}
.recommendation-image {
  width: 150px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #e9ecef;
  cursor: pointer;
  transition: transform 0.3s ease;
}
.recommendation-image-link:hover .recommendation-image {
  transform: scale(1.05);
}
.recommendation-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommendation-content {
  flex: 1;
  display: grid;
  grid-template-columns: auto 1fr; 
  gap: 8px 10px; 
  align-items: baseline; 
}

.recommendation-type {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
  background: var(--primary-color);
  color: white;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  align-self: center; 
}

.recommendation-link {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600; 
  transition: var(--transition);
}
.recommendation-link:hover {
  text-decoration: underline;
  color: #2a85c6;
}

.recommendation-reason {
  grid-column: 2 / 3;
  grid-row: 2 / 3;
  display: flex;
  font-size: 14px;
  color: var(--light-text);
  line-height: 1.7;
}

.reason-label {
  flex-shrink: 0;
  color: var(--text-color);
  font-weight: 500;
  margin-right: 4px; 
}


.recommendation-title-text {
  flex: 1; 
}

.score-section {
  text-align: center;
  padding: 40px 20px;
  background: #fefefe;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  margin-bottom: 40px;
}
.score-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.score-circle {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: conic-gradient(
    var(--primary-color) 0% var(--progress, 0%),
    #e0e0e0 var(--progress, 0%) 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05),
              0 4px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  transition: var(--transition);
}
.score-circle::after {
  content: '';
  position: absolute;
  width: 130px;
  height: 130px;
  background: white;
  border-radius: 50%;
  box-shadow: inset 0 0 4px rgba(0, 0, 0, 0.06);
}
.score-value {
  position: relative;
  font-size: 48px;
  font-weight: 700;
  color: var(--primary-color);
  z-index: 1;
}
.score-total {
  position: relative;
  font-size: 20px;
  color: #aaa;
  z-index: 1;
  margin-left: 5px;
}
.score-feedback {
  max-width: 600px;
  font-size: 16px;
  color: #444;
  line-height: 1.7;
  margin-top: 10px;
  background: #f0f7ff;
  padding: 15px 20px;
  border-left: 5px solid var(--primary-color);
  border-radius: 8px;
}
.icon-download::before { content: "↓"; }
.icon-back::before { content: "←"; }
.icon-chart::before { content: "📊"; }
.icon-pose::before { content: "🧘"; }
.icon-emotion::before { content: "😊"; }
.icon-eye::before { content: "👀"; }
.icon-speech::before { content: "🗣️"; }
.icon-movement::before { content: "🏃"; }
.icon-recommend::before { content: "📚"; }
.icon-score::before { content: "⭐"; }
@media (max-width: 768px) {
  .report-container {
    padding: 20px;
  }
  .video-info-section {
    flex-direction: column;
    gap: 10px;
  }
  .report-title {
    font-size: 24px;
  }
  .section-title {
    font-size: 18px;
  }
  .chart-container {
    height: 300px;
  }
  .metrics-grid {
    grid-template-columns: 1fr 1fr;
  }
  .section-title + .chart-container {
    height: 400px;
  }
  .pie-chart-container {
    max-width: 300px;
    height: 300px;
  }
  .recommendation-item {
    flex-direction: column;
    align-items: stretch;
  }
  .recommendation-image-link {
    width: 100%;
  }
  .recommendation-image {
    width: 100%;
    height: 180px;
  }
}
@media (max-width: 480px) {
  .report-header {
    flex-direction: column;
    gap: 10px;
  }
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  .score-circle {
    width: 120px;
    height: 120px;
  }
  .score-circle::after {
    width: 90px;
    height: 90px;
  }
  .score-value {
    font-size: 36px;
  }
}
</style>