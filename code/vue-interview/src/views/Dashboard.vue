<template>
  <div class="learning-resources-page">
    <div class="header-section">
      <div class="container-fluid">
        <h1 class="main-title">职业学习资源推荐</h1>
        <p class="subtitle">精选优质学习资源，助力您的职业发展</p>
      </div>
    </div>

    <div class="container-fluid content-body">
      <!-- 热门推荐课程 -->
      <section class="resource-section">
        <div class="section-header">
          <h2 class="section-title">热门推荐课程</h2>
          <p class="section-subtitle">涵盖AI、大数据、物联网等前沿技术</p>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-4 col-sm-6 mb-4" v-for="course in featuredCourses" :key="course.title">
            <div class="resource-card" @click="redirectTo(course.link)">
              <div class="card-image-wrapper">
                <img :src="course.image" class="card-image">
                <div class="image-overlay">
                  <span class="view-details-btn">查看详情</span>
                </div>
              </div>
              <div class="card-content">
                <span class="platform-badge" :class="getPlatformClass(course.platform)">{{ course.platform }}</span>
                <h6 class="card-title">{{ course.title }}</h6>
                <p class="card-provider">{{ course.provider }}</p>
                <p class="card-description">{{ course.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 视频课程专区 -->
      <section class="resource-section">
        <div class="section-header">
          <h2 class="section-title">视频课程专区</h2>
          <p class="section-subtitle">B站、YouTube等平台优质视频资源</p>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-4 col-sm-6 mb-4" v-for="video in videoCourses" :key="video.title">
             <div class="resource-card" @click="redirectTo(video.link)">
              <div class="card-image-wrapper">
                <img :src="video.image" class="card-image">
                <div class="image-overlay">
                  <span class="view-details-btn">前往观看</span>
                </div>
              </div>
              <div class="card-content">
                <span class="platform-badge" :class="getPlatformClass(video.platform)">{{ video.platform }}</span>
                <h6 class="card-title">{{ video.title }}</h6>
                <p class="card-provider">{{ video.instructor }}</p>
                <p class="card-description">{{ video.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 学习社区与论坛 -->
      <section class="resource-section">
         <div class="section-header">
          <h2 class="section-title">学习社区与论坛</h2>
          <p class="section-subtitle">与技术同行交流，共同进步</p>
        </div>
        <div class="community-list">
          <div v-for="community in learningCommunities" :key="community.name" class="community-item" @click="redirectTo(community.link)">
            <div class="community-icon">
              <i :class="getCommunityIcon(community.name)"></i>
            </div>
            <div class="community-info">
              <h6 class="community-name">{{ community.name }}</h6>
              <p class="community-description">{{ community.description }}</p>
            </div>
            <div class="community-action">
              <i class="icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: "LearningResources",
  data() {
    return {
      featuredCourses: [
        { title: "机器学习课程", provider: "Stanford University", image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.coursera.org/learn/machine-learning", description: "吴恩达教授的经典机器学习入门", platform: "Coursera" },
        { title: "大数据专项课程", provider: "University of California", image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.coursera.org/specializations/big-data", description: "从入门到精通的大数据技术栈", platform: "Coursera" },
        { title: "物联网认证课程", provider: "IBM", image: "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.coursera.org/professional-certificates/iot", description: "构建物联网解决方案的完整路径", platform: "Coursera" },
        { title: "Python数据科学", provider: "DataCamp", image: "https://images.unsplash.com/photo-1547658719-da2b51169166?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.datacamp.com/tracks/data-scientist-with-python", description: "使用Python进行数据分析与可视化", platform: "DataCamp" },
        { title: "深度学习专项", provider: "deeplearning.ai", image: "https://images.unsplash.com/photo-1629909613654-28e377c37b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.coursera.org/specializations/deep-learning", description: "深度学习前沿技术全面掌握", platform: "Coursera" },
        { title: "云计算架构师", provider: "AWS", image: "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://aws.amazon.com/cn/training/", description: "AWS云计算架构师认证课程", platform: "AWS" },
        { title: "区块链开发", provider: "Udemy", image: "https://images.unsplash.com/photo-1639762681057-408e52192e55?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.udemy.com/topic/blockchain/", description: "区块链开发从入门到精通", platform: "Udemy" },
        { title: "前端开发全栈", provider: "Meta", image: "https://images.unsplash.com/photo-1509395062183-67c5ad6faff9?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.coursera.org/professional-certificates/meta-front-end-developer", description: "Meta官方出品前端开发课程", platform: "Coursera" }
      ],
      videoCourses: [
        { title: "李宏毅机器学习", instructor: "李宏毅教授", image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.bilibili.com/video/BV1Wv411h7kN", description: "台湾大学李宏毅教授机器学习课程", platform: "B站" },
        { title: "Python数据分析实战", instructor: "莫烦Python", image: "https://images.unsplash.com/photo-1547658719-da2b51169166?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.bilibili.com/video/BV1Ex411L7oT", description: "Python数据分析实战教程", platform: "B站" },
        { title: "CS50 AI入门", instructor: "Harvard University", image: "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.youtube.com/playlist?list=PLhQjrBD2T3828ZVcVzEIhsHVgjANGZveu", description: "哈佛大学人工智能入门课程", platform: "YouTube" },
        { title: "Hadoop大数据开发", instructor: "尚硅谷", image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80", link: "https://www.bilibili.com/video/BV1Qp4y1n7EN", description: "Hadoop大数据开发实战教程", platform: "B站" },
      ],
      learningCommunities: [
        { name: "Stack Overflow", link: "https://stackoverflow.com/", description: "全球最大的技术问答社区" },
        { name: "Towards Data Science", link: "https://towardsdatascience.com/", description: "数据科学与AI技术文章" },
        { name: "GitHub", link: "https://github.com/", description: "开源项目与代码协作平台" },
        { name: "CSDN技术社区", link: "https://www.csdn.net/", description: "中文开发者技术社区" },
        { name: "Kaggle", link: "https://www.kaggle.com/", description: "数据科学与机器学习竞赛平台" }
      ]
    };
  },
  methods: {
    redirectTo(url) {
      window.open(url, '_blank');
    },
    getPlatformClass(platform) {
      const platformClasses = {
        'B站': 'platform-bilibili',
        'YouTube': 'platform-youtube',
        'Coursera': 'platform-coursera',
        'DataCamp': 'platform-datacamp',
        'Udemy': 'platform-udemy',
        'AWS': 'platform-aws',
      };
      return platformClasses[platform] || 'platform-default';
    },
    getCommunityIcon(name) {
      const icons = {
        "Stack Overflow": "icon-stackoverflow",
        "Towards Data Science": "icon-datascience",
        "GitHub": "icon-github",
        "CSDN技术社区": "icon-csdn",
        "Kaggle": "icon-kaggle",
      };
      return icons[name] || "icon-default-community";
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.learning-resources-page {
  --primary-color: #3b82f6;
  --secondary-color: #10b981;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --bg-color: #f9fafb;
  --card-bg-color: #ffffff;
  --border-color: #e5e7eb;
  --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  --card-shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-color);
}

.header-section {
  text-align: center;
  padding: 4rem 1rem;
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  border-bottom: 1px solid var(--border-color);
}
.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}
.subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

.content-body {
  padding-top: 3rem;
  padding-bottom: 4rem;
}

.resource-section {
  margin-bottom: 4rem;
}
.section-header {
  margin-bottom: 2rem;
  padding-left: 1rem;
  border-left: 4px solid var(--primary-color);
}
.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
}
.section-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
}

.resource-card {
  background-color: var(--card-bg-color);
  border-radius: 0.75rem;
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.resource-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--card-shadow-hover);
}

.card-image-wrapper {
  position: relative;
  height: 150px;
  overflow: hidden;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.resource-card:hover .card-image {
  transform: scale(1.05);
}
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(29, 41, 55, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.resource-card:hover .image-overlay {
  opacity: 1;
}
.view-details-btn {
  color: white;
  background-color: var(--primary-color);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-weight: 500;
  font-size: 0.875rem;
}

.card-content {
  padding: 1.25rem;
  flex-grow: 1;
}
.platform-badge {
  display: inline-block;
  padding: 0.25em 0.75em;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 999px;
  color: white;
  margin-bottom: 0.75rem;
}
.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}
.card-provider {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}
.card-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.community-list {
  display: grid;
  gap: 1rem;
}
.community-item {
  background-color: var(--card-bg-color);
  padding: 1.25rem;
  border-radius: 0.75rem;
  box-shadow: var(--card-shadow);
  display: flex;
  align-items: center;
  gap: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.community-item:hover {
  transform: translateX(5px);
  box-shadow: var(--card-shadow-hover);
  border-left: 4px solid var(--primary-color);
  padding-left: calc(1.25rem - 4px);
}

.community-icon {
  background-color: #e0f2fe;
  color: var(--primary-color);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}
.community-info {
  flex-grow: 1;
}
.community-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}
.community-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}
.community-action {
  font-size: 1.25rem;
  color: #9ca3af;
  transition: transform 0.2s;
}
.community-item:hover .community-action {
  transform: translateX(4px);
  color: var(--primary-color);
}


.platform-bilibili { background-color: #fb7299; }
.platform-youtube { background-color: #ff0000; }
.platform-coursera { background-color: #2a73cc; }
.platform-datacamp { background-color: #05cd7d; }
.platform-udemy { background-color: #a435f0; }
.platform-aws { background-color: #ff9900; }
.platform-default { background-color: #6b7280; }

[class^="icon-"]::before { font-style: normal; }
.icon-stackoverflow::before { content: '💬'; }
.icon-datascience::before { content: '📊'; }
.icon-github::before { content: '💻'; }
.icon-csdn::before { content: '📝'; }
.icon-kaggle::before { content: '🏆'; }
.icon-default-community::before { content: '🌐'; }
.icon-arrow-right::before { content: '→'; }
</style>