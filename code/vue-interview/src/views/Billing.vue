<!-- 模拟面试界面-->
<template>
  <div class="interview-page-wrapper">
    <div class="container-fluid mt-4">
      <div class="row align-items-center">
        <div class="col-lg-12 text-center">
          <h2 class="mb-4">模拟面试系统</h2>
        </div>
      </div>

      <!-- 职业选择界面 -->
      <div v-if="!interviewStarted" class="selection-container">
        <div class="search-box mb-4">
          <input type="text" v-model="searchQuery" placeholder="搜索领域或职位，例如：前端、产品经理..." class="form-control">
        </div>
        <h3 class="selection-title">选择面试领域</h3>
        <div v-if="groupedFilteredFields.length > 0">
          <div v-for="(row, rowIndex) in groupedFilteredFields" :key="`field-row-${rowIndex}`" class="options-group">
            <button 
              v-for="item in row"
              :key="item.value"
              @click="selectField(item.value)" 
              class="option-btn" 
              :class="{ active: selectedField === item.value }"
              :style="selectedField !== item.value ? getTagStyle(item.runningIndex) : null"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
        <h3 class="selection-title" v-if="selectedField">选择职业</h3>
        <div v-if="selectedField && groupedFilteredJobs.length > 0">
          <div v-for="(row, rowIndex) in groupedFilteredJobs" :key="`job-row-${rowIndex}`" class="options-group">
              <button 
                  v-for="item in row"
                  :key="item.value"
                  @click="selectJob(item.value)" 
                  class="option-btn" 
                  :class="{ active: selectedJob === item.value }"
                  :style="selectedJob !== item.value ? getTagStyle(fields.length + item.runningIndex) : null"
              >
                  {{ item.label }}
              </button>
          </div>
        </div>
        <button @click="showInterviewPage" class="start-interview-btn" :disabled="!selectedJob || isLoadingResumeCheck">
          <span v-if="isLoadingResumeCheck" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ isLoadingResumeCheck ? '正在检查...' : '进入面试' }}
        </button>
      </div>

      <!-- 面试交互界面 -->
      <div class="row" v-if="interviewStarted">
        <div class="col-lg-8">
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">面试视频</h5>
              <div>
                <button @click="goBackToSelection" class="btn btn-sm btn-secondary me-2" :disabled="interviewActive">
                  返回选择
                </button>
                <button @click="toggleInterviewActive" class="btn btn-sm" :class="{'btn-danger': interviewActive, 'btn-success': !interviewActive}">
                  {{ interviewActive ? '结束面试' : '开始面试' }}
                </button>
              </div>
            </div>
            <div class="card-body text-center">
              <video ref="userVideo" autoplay playsinline muted class="w-100 border rounded"></video>
              <p class="text-muted mt-2">{{ statusMessage }}</p>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header"><h5 class="mb-0">面试问题</h5></div>
            <div class="card-body">
              <div v-if="isLoadingQuestion" class="alert alert-light"><div class="spinner-border spinner-border-sm me-2"></div>正在分析您的回答，请稍候...</div>
              <p v-else-if="currentQuestionText" class="lead">{{ currentQuestionText }}</p>
              <p v-else class="text-muted">面试已结束，请返回个人中心，稍等几分钟查看面试报告</p>
              <div v-if="isSilenceWarningVisible" class="alert alert-warning mt-3 silence-warning">
                检测声音过小或回答结束，将在 {{ countdown }} 秒后分析回答...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 职业百科侧边栏 -->
    <div class="panel-overlay" :class="{ 'is-visible': isPanelOpen }" @click="togglePanel"></div>
    <div class="side-panel" :class="{ 'is-open': isPanelOpen }">
      <div class="panel-header">
        <h3>职业百科</h3>
        <p>探索不同岗位的世界</p>
      </div>
      <div class="panel-content">
        <a 
          v-for="resource in careerResources" 
          :key="resource.title"
          :href="resource.url"
          target="_blank"
          class="resource-item-link"
        >
          <div class="resource-item">
            <img :src="resource.imageUrl" class="resource-image" alt="">
            <div class="resource-info">
              <span class="resource-category">{{ resource.category }}</span>
              <h4 class="resource-title">{{ resource.title }}</h4>
            </div>
          </div>
        </a>
      </div>
    </div>
    <button class="open-panel-btn" @click="togglePanel">
      <i class="icon-help"></i>
      <span>不知道选什么职业？</span>
    </button>
  </div>
</template>

<script>
export default {
  name: "Interview",
  data() {
    return {
      isPanelOpen: false, // 控制侧边栏的显示
      // 职业百科资源
      careerResources: [
        { category: '人工智能', title: 'AI算法工程师是做什么的？', url: 'https://zhuanlan.zhihu.com/p/35532598', imageUrl: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
        { category: '大数据', title: '大数据开发工程师的职业路径', url: 'https://zhuanlan.zhihu.com/p/34292534', imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
        { category: '物联网', title: '物联网工程师需要哪些技能？', url: 'https://www.zhihu.com/question/268322046', imageUrl: 'https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
        { category: '前端开发', title: '前端开发的学习路线与前景', url: 'https://www.zhihu.com/question/399322478', imageUrl: 'https://images.unsplash.com/photo-1509395062183-67c5ad6faff9?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
        { category: '产品管理', title: '一文读懂什么是产品经理', url: 'https://zhuanlan.zhihu.com/p/19434827', imageUrl: 'https://images.unsplash.com/photo-1556740758-90de374c12ad?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
        { category: 'UI/UX设计', title: 'UI设计师和UX设计师有什么区别？', url: 'https://www.zhihu.com/question/21255495', imageUrl: 'https://images.unsplash.com/photo-1547658719-da2b51169166?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=400' },
      ],
      searchQuery: '',
      tagColors: [
        '#e0f2f1', '#e3f2fd', '#fffde7', '#fbe9e7', '#e8eaf6',
        '#fce4ec', '#f1f8e9', '#fff3e0', '#efebe9', '#eceff1',
        '#e0f7fa', '#f9fbe7', '#ffebee', '#f3e5f5', '#e1f5fe'
      ],
      fields: [
        { value: 'ai', label: '人工智能' }, { value: 'bigdata', label: '大数据' }, { value: 'iot', label: '物联网' },
        { value: 'cloud', label: '云计算' }, { value: 'frontend', label: '前端开发' }, { value: 'backend', label: '后端开发' },
        { value: 'mobile', label: '移动开发' }, { value: 'security', label: '网络安全' }, { value: 'devops', label: '开发运维(DevOps)' },
        { value: 'qa', label: '软件测试' }, { value: 'blockchain', label: '区块链' }, { value: 'arvr', label: '增强/虚拟现实(AR/VR)' },
        { value: 'gamedev', label: '游戏开发' }, { value: 'edge', label: '边缘计算' }, { value: 'pm', label: '产品管理' },
        { value: 'uidesign', label: 'UI设计' }, { value: 'uxdesign', label: 'UX设计' }, { value: 'datascience', label: '数据科学' },
        { value: 'dataanalysis', label: '数据分析' }, { value: 'project', label: '项目管理' }, { value: 'embedded', label: '嵌入式系统' },
      ],
      jobs: [
        { value: 'ml_engineer', label: '机器学习测试工程师', field: 'ai' }, { value: 'ai_pm', label: 'AI产品经理', field: 'ai' }, { value: 'cv_engineer', label: '计算机视觉工程师', field: 'ai' }, { value: 'nlp_engineer', label: '自然语言处理工程师', field: 'ai' }, { value: 'recsys_engineer', label: '推荐系统工程师', field: 'ai' }, { value: 'ai_researcher', label: 'AI研究员', field: 'ai' },
        { value: 'bigdata_engineer', label: '大数据开发工程师', field: 'bigdata' }, { value: 'data_architect', label: '数据架构师', field: 'bigdata' }, { value: 'data_warehouse_engineer', label: '数据仓库工程师', field: 'bigdata' }, { value: 'etl_developer', label: 'ETL开发工程师', field: 'bigdata' }, { value: 'spark_developer', label: 'Spark开发工程师', field: 'bigdata' },
        { value: 'iot_architect', label: '物联网产品经理', field: 'iot' }, { value: 'iot_solutions_architect', label: '物联网解决方案架构师', field: 'iot' }, { value: 'iot_backend_developer', label: '物联网后端开发', field: 'iot' }, { value: 'iot_security_specialist', label: '物联网安全专家', field: 'iot' }, { value: 'iot_embedded_engineer', label: '物联网嵌入式工程师', field: 'iot' },
        { value: 'cloud_architect', label: '云架构师', field: 'cloud' }, { value: 'cloud_engineer', label: '云工程师', field: 'cloud' }, { value: 'sre', label: '网站可靠性工程师(SRE)', field: 'cloud' }, { value: 'cloud_security_engineer', label: '云安全工程师', field: 'cloud' }, { value: 'cloud_native_developer', label: '云原生开发工程师', field: 'cloud' },
        { value: 'frontend_developer', label: '前端开发工程师', field: 'frontend' }, { value: 'ui_engineer', label: 'UI工程师', field: 'frontend' }, { value: 'react_developer', label: 'React开发工程师', field: 'frontend' }, { value: 'vue_developer', label: 'Vue开发工程师', field: 'frontend' }, { value: 'web_accessibility_specialist', label: 'Web无障碍专家', field: 'frontend' },
        { value: 'backend_developer', label: '后端开发工程师', field: 'backend' }, { value: 'java_developer', label: 'Java开发工程师', field: 'backend' }, { value: 'python_developer', label: 'Python后端开发', field: 'backend' }, { value: 'go_developer', label: 'Go开发工程师', field: 'backend' },
        { value: 'android_developer', label: 'Android开发工程师', field: 'mobile' }, { value: 'ios_developer', label: 'iOS开发工程师', field: 'mobile' }, { value: 'flutter_developer', label: 'Flutter开发工程师', field: 'mobile' },
        { value: 'security_analyst', label: '安全分析师', field: 'security' }, { value: 'penetration_tester', label: '渗透测试工程师', field: 'security' },
        { value: 'devops_engineer', label: 'DevOps工程师', field: 'devops' },
        { value: 'qa_engineer', label: '测试工程师', field: 'qa' }, { value: 'automation_qa', label: '自动化测试工程师', field: 'qa' },
        { value: 'blockchain_developer', label: '区块链开发工程师', field: 'blockchain' },
        { value: 'ar_engineer', label: 'AR工程师', field: 'arvr' }, { value: 'vr_developer', label: 'VR开发工程师', field: 'arvr' },
        { value: 'unity_developer', label: 'Unity开发工程师', field: 'gamedev' }, { value: 'unreal_engine_developer', label: 'UE开发工程师', field: 'gamedev' },
        { value: 'edge_computing_engineer', label: '边缘计算工程师', field: 'edge' },
        { value: 'product_manager', label: '产品经理', field: 'pm' }, { value: 'product_owner', label: '产品负责人(PO)', field: 'pm' },
        { value: 'ui_designer', label: 'UI设计师', field: 'uidesign' }, { value: 'visual_designer', label: '视觉设计师', field: 'uidesign' },
        { value: 'ux_designer', label: 'UX设计师', field: 'uxdesign' }, { value: 'interaction_designer', label: '交互设计师', field: 'uxdesign' },
        { value: 'data_scientist', label: '数据科学家', field: 'datascience' },
        { value: 'data_analyst', label: '数据分析师', field: 'dataanalysis' }, { value: 'business_analyst', label: '商业分析师', field: 'dataanalysis' },
        { value: 'project_manager', label: '项目经理', field: 'project' }, { value: 'agile_coach', label: '敏捷教练', field: 'project' },
        { value: 'embedded_engineer', label: '嵌入式工程师', field: 'embedded' }, { value: 'firmware_engineer', label: '固件工程师', field: 'embedded' },
      ],
      selectedField: null,
      selectedJob: null,
      interviewStarted: false,
      interviewActive: false,
      isLoadingResumeCheck: false,
      mockId: '',
      mockResume: null,
      mockJob:null,
      statusMessage: '请选择您的面试岗位',
      currentQuestionText: '',
      isLoadingQuestion: false,
      localStream: null, mediaRecorder: null, webSocket: null, audioContext: null,
      silenceTimer: null, silenceDuration: 0, isSilenceWarningVisible: false, countdown: 3, 
      SILENCE_THRESHOLD: 1.5, SILENCE_WARNING_MS: 5000, SILENCE_STOP_MS: 8000, 
    };
  },
  created() {
    // 从localstorage中取账号数据
    this.mockId = localStorage.getItem('account') || '';
  },
  computed: {
    filteredFields() {
      if (!this.searchQuery.trim()) {
        return this.fields;
      }
      const query = this.searchQuery.toLowerCase();
      return this.fields.filter(field => {
        const fieldMatches = field.label.toLowerCase().includes(query) || field.value.toLowerCase().includes(query);
        if (fieldMatches) return true;
        const hasMatchingJob = this.jobs.some(job => 
          job.field === field.value && (job.label.toLowerCase().includes(query) || job.value.toLowerCase().includes(query))
        );
        return hasMatchingJob;
      });
    },
    filteredJobs() {
      if (!this.selectedField) return [];
      let jobsForField = this.jobs.filter(job => job.field === this.selectedField);
      if (!this.searchQuery.trim()) {
        return jobsForField;
      }
      const query = this.searchQuery.toLowerCase();
      return jobsForField.filter(job =>
        job.label.toLowerCase().includes(query) || job.value.toLowerCase().includes(query)
      );
    },
    groupedFilteredFields() {
        return this.groupItems(this.filteredFields, [6, 5, 6, 4]);
    },
    groupedFilteredJobs() {
        return this.groupItems(this.filteredJobs, [5, 4, 5]);
    },
    dynamicWebSocketUrl() {
      const encodedId = encodeURIComponent(this.mockId);
      const formattedDate = this.getFormattedDateTime(); 
      const encodedDate = encodeURIComponent(formattedDate);
      const encodedResume = this.mockResume ? encodeURIComponent(this.mockResume) : '';
      const encodedJob = this.mockJob ? encodeURIComponent(this.mockJob) : '';
      return `ws://localhost:8000/interview/ws?id=${encodedId}&date=${encodedDate}&resume=${encodedResume}&selected_job=${encodedJob}`;
    }
  },
  methods: {
    // 侧边栏切换
    togglePanel() {
      this.isPanelOpen = !this.isPanelOpen;
    },
    groupItems(items, groupSizes) {
      if (!items || !items.length) return [];
      const grouped = [];
      let sourceIndex = 0;
      const itemsWithIndex = items.map((item, index) => ({ ...item, runningIndex: index }));
      for (const size of groupSizes) {
        if (sourceIndex >= itemsWithIndex.length) break;
        const group = itemsWithIndex.slice(sourceIndex, sourceIndex + size);
        grouped.push(group);
        sourceIndex += size;
      }
      if (sourceIndex < itemsWithIndex.length) {
        grouped.push(itemsWithIndex.slice(sourceIndex));
      }
      return grouped;
    },
    getTagStyle(index) {
      const color = this.tagColors[index % this.tagColors.length];
      return { backgroundColor: color, borderColor: color };
    },
    padZero(num) { return num < 10 ? '0' + num : num; },
    getFormattedDateTime() {
        const now = new Date();
        return `${now.getFullYear()}-${this.padZero(now.getMonth() + 1)}-${this.padZero(now.getDate())} ${this.padZero(now.getHours())}:${this.padZero(now.getMinutes())}:${this.padZero(now.getSeconds())}`;
    },
    selectField(field) {
      this.selectedField = this.selectedField === field ? null : field;
      this.selectedJob = null;
    },
    selectJob(job) {
      this.selectedJob = this.selectedJob === job ? null : job;
    },
    async showInterviewPage() {
      this.isLoadingResumeCheck = true;
      this.mockId = localStorage.getItem('account');
      if (!this.mockId) { // 判断是否登录
        alert('请先登录后再进入面试。');
        this.$router.push('/sign-in');
        this.isLoadingResumeCheck = false;
        return;
      }
      const LIVE_JOBS = new Set(['ml_engineer', 'bigdata_engineer', 'iot_architect']);
      if (!LIVE_JOBS.has(this.selectedJob)) {
          alert('此面试岗位暂未开发，敬请期待');
          this.isLoadingResumeCheck = false;
          return;
      }
      try { // 判断简历是否上传
        const res = await fetch(`http://localhost:8000/api/users/${encodeURIComponent(this.mockId)}/resume/check`);
        if (!res.ok) throw new Error('服务器响应失败: ' + res.status);
        const result = await res.json();
        if (result.code === 200) {
          if (!result.data.hasResume) {
            alert('您尚未上传简历，请先前往个人中心上传后再进入面试。');
            this.$router.push('/profile');
            return;
          }
          this.mockResume = result.data.resumeUrl || '';
          this.mockJob = `${this.selectedField}:${this.selectedJob}`;
          this.interviewStarted = true;
          this.statusMessage = '准备就绪，请点击开始面试';
        } else {
          alert('简历状态检查失败，请稍后重试。');
        }
      } catch (error) {
        console.error('检查简历状态失败:', error);
        alert('网络错误或后端服务异常，请稍后再试。');
      } finally {
        this.isLoadingResumeCheck = false;
      }
    },
    async toggleInterviewActive() {
      if (this.interviewActive) this.stopInterviewSession();
      else await this.startInterviewSession();
    },
    async startInterviewSession() {
      this.statusMessage = '正在启动摄像头...';
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        this.localStream = stream;
        this.$refs.userVideo.srcObject = stream;
      } catch (err) {
        this.statusMessage = '摄像头/麦克风启动失败，请检查设备权限。';
        return;
      }
      this.statusMessage = '正在连接服务器...';
      this.webSocket = new WebSocket(this.dynamicWebSocketUrl);
      this.webSocket.onopen = () => { this.interviewActive = true; this.statusMessage = '连接成功，等待第一个问题...'; };
      this.webSocket.onmessage = (event) => this.handleNewQuestion(event.data);
      this.webSocket.onclose = () => { this.statusMessage = '面试已结束。'; this.cleanupAfterInterview(); };
      this.webSocket.onerror = (error) => { this.statusMessage = '连接发生错误。'; console.error('WS Error:', error); this.cleanupAfterInterview(); };
    },
    handleNewQuestion(questionText) {
      this.currentQuestionText = questionText;
      this.isLoadingQuestion = false;
      this.statusMessage = '面试进行中，请回答问题...';
      this.startNewRecorder();
    },
    startNewRecorder() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') this.mediaRecorder.stop();
      this.mediaRecorder = new MediaRecorder(this.localStream, { mimeType: 'video/webm; codecs=vp8,opus' });
      this.mediaRecorder.ondataavailable = e => { if (e.data.size > 0 && this.webSocket?.readyState === 1) this.webSocket.send(e.data); };
      this.mediaRecorder.onstop = () => { this.isLoadingQuestion = true; this.statusMessage = '回答结束，正在分析...'; this.isSilenceWarningVisible = false; };
      this.mediaRecorder.start(1000);
      this.setupSilenceDetection();
    },
    setupSilenceDetection() {
        if (this.silenceTimer) clearInterval(this.silenceTimer);
        if (!this.audioContext || this.audioContext.state === 'closed') this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = this.audioContext.createMediaStreamSource(this.localStream);
        const analyser = this.audioContext.createAnalyser();
        source.connect(analyser);
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        this.resetSilenceDetection();
        this.silenceTimer = setInterval(() => {
            if (this.mediaRecorder?.state !== 'recording') return;
            analyser.getByteTimeDomainData(dataArray);
            const volume = dataArray.reduce((acc, val) => acc + Math.abs(val - 128), 0) / dataArray.length;
            if (volume < this.SILENCE_THRESHOLD) { this.silenceDuration += 200; }
            else { this.resetSilenceDetection(); }
            if (this.silenceDuration >= this.SILENCE_STOP_MS) { if (this.mediaRecorder.state === 'recording') { this.mediaRecorder.stop(); }
            } else if (this.silenceDuration >= this.SILENCE_WARNING_MS) {
                if (!this.isSilenceWarningVisible) { this.isSilenceWarningVisible = true; }
                this.countdown = Math.max(0, Math.ceil((this.SILENCE_STOP_MS - this.silenceDuration) / 1000));
            }
        }, 200);
    },
    resetSilenceDetection() {
      this.silenceDuration = 0;
      this.isSilenceWarningVisible = false;
      this.countdown = Math.ceil((this.SILENCE_STOP_MS - this.SILENCE_WARNING_MS) / 1000);
    },
    stopInterviewSession() {
      if (this.webSocket) this.webSocket.close();
      this.isLoadingQuestion = false; this.currentQuestionText = ''; 
      this.statusMessage = '面试已结束，请等待一段时间后前往个人中心查看面试评测结果。'; 
    },
    goBackToSelection() { this.stopInterviewSession(); this.interviewStarted = false; this.resetAllStates(); },
    cleanupAfterInterview() {
      this.interviewActive = false;
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') this.mediaRecorder.stop();
      if (this.localStream) this.localStream.getTracks().forEach(track => track.stop());
      if (this.silenceTimer) clearInterval(this.silenceTimer);
      if (this.audioContext && this.audioContext.state !== 'closed') this.audioContext.close();
      const videoEl = this.$refs.userVideo;
      if (videoEl) videoEl.srcObject = null;
      this.localStream = null; this.mediaRecorder = null; this.webSocket = null;
      this.silenceTimer = null; this.audioContext = null;
    },
    resetAllStates() {
        this.selectedField = null; this.selectedJob = null; this.mockResume = null;
        this.mockJob = null; this.currentQuestionText = ''; this.isLoadingQuestion = false;
        this.statusMessage = '请选择您的面试岗位'; this.isSilenceWarningVisible = false; this.searchQuery = '';
    }
  },
  unmounted() {
    this.stopInterviewSession();
  }
};
</script>

<style scoped>
.interview-page-wrapper { position: relative; }
.selection-container { background-color: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05); text-align: center; }
.search-box { max-width: 600px; margin: 0 auto 30px; }
.search-box .form-control { border-radius: 25px; padding: 10px 20px; border: 1px solid #dee2e6; transition: all 0.3s ease; }
.search-box .form-control:focus { border-color: #86b7fe; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); }
.selection-title { color: #212529; font-weight: 600; margin-top: 30px; margin-bottom: 20px; }
.selection-title:first-of-type { margin-top: 0; }
.options-group { display: flex; justify-content: center; gap: 12px 15px; flex-wrap: wrap; margin-bottom: 10px; }
.option-btn { padding: 8px 20px; border: 1px solid transparent; border-radius: 20px; color: #333; font-weight: 500; cursor: pointer; font-size: 0.95em; transition: all 0.25s ease-in-out; transform: scale(1.0); }
.option-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.option-btn.active { background-color: #0d6efd !important; color: white !important; border-color: #0d6efd !important; transform: scale(1.1); box-shadow: 0 4px 12px rgba(13, 110, 253, 0.4); }
.start-interview-btn { margin-top: 40px; padding: 12px 40px; font-size: 1.2em; background-color: #198754; color: white; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
.start-interview-btn:disabled { background-color: #6c757d; cursor: not-allowed; box-shadow: none; opacity: 0.65; }
.start-interview-btn:hover:not(:disabled) { background-color: #157347; box-shadow: 0 4px 12px rgba(25, 135, 84, 0.4); transform: translateY(-2px); }
.card { height: 100%; }
video { height: 650px; background: #000; }
.silence-warning { font-size: 1.3em; font-weight: bold; text-align: center; }

/* --- 侧边栏样式 --- */
.open-panel-btn {
  position: fixed; top: 50%; right: 0; transform: translateY(-50%);
  background-color: #6366f1; color: white; border: none; padding: 1rem 0.5rem;
  border-top-left-radius: 0.75rem; border-bottom-left-radius: 0.75rem;
  cursor: pointer; box-shadow: -2px 2px 10px rgba(0,0,0,0.1);
  transition: all 0.3s ease; z-index: 1050; display: flex; align-items: center; gap: 0.5rem;
}
.open-panel-btn span { writing-mode: vertical-rl; text-orientation: mixed; font-weight: 500; white-space: nowrap; }
.open-panel-btn:hover { background-color: #4f46e5; padding-right: 0.75rem; }
.icon-help::before { content: '💡'; font-size: 1.2rem; }
.panel-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); opacity: 0; visibility: hidden; transition: all 0.4s ease; z-index: 1040; }
.panel-overlay.is-visible { opacity: 1; visibility: visible; }
.side-panel { position: fixed; top: 0; right: 0; width: 450px; max-width: 90vw; height: 100%; background-color: #f8f8fa; box-shadow: -5px 0 25px rgba(0,0,0,0.1); transform: translateX(100%); transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); z-index: 1045; display: flex; flex-direction: column; }
.side-panel.is-open { transform: translateX(0); }
.panel-header { padding: 1.5rem; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; }
.panel-header h3 { color: #1f2937; font-weight: 600; margin-bottom: 0.25rem; }
.panel-header p { color: #6b7280; margin: 0; }
.panel-content { padding: 1.5rem; overflow-y: auto; flex-grow: 1; }
.panel-content::-webkit-scrollbar { width: 5px; }
.panel-content::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 10px; }
.resource-item-link { text-decoration: none; }
.resource-item { display: flex; align-items: center; gap: 1rem; background-color: #ffffff; padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: all 0.2s ease; }
.resource-item:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08); }
.resource-image { width: 80px; height: 80px; object-fit: cover; border-radius: 0.5rem; flex-shrink: 0; }
.resource-info { display: flex; flex-direction: column; }
.resource-category { font-size: 0.75rem; font-weight: 500; color: #6366f1; background-color: #eef2ff; padding: 0.2rem 0.6rem; border-radius: 999px; align-self: flex-start; margin-bottom: 0.5rem; }
.resource-title { font-size: 1rem; font-weight: 600; color: #1f2937; line-height: 1.3; }
</style>