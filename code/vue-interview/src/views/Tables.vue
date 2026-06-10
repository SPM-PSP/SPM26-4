<template>
  <div class="practice-system-wrapper py-4">
    <div class="container">
      <div class="header-section">
        <h1 class="main-title">在线题库</h1>
        <p class="subtitle">选择领域、岗位和难度，探索知识的海洋</p>
      </div>

      <!-- 题目领域、岗位、难度选择 -->
      <div class="row justify-content-center mb-5">
        <div class="col-lg-12">
          <div class="filter-card card">
            <div class="row align-items-end">
              <div class="col-md-6 col-lg-3 mb-3 mb-lg-0">
                <label for="field-select" class="form-label">技术领域</label>
                <select id="field-select" v-model="selectedField" class="form-select">
                  <option disabled value="">请选择领域</option>
                  <option v-for="field in fields" :key="field.value" :value="field.value">
                    {{ field.label }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 col-lg-4 mb-3 mb-lg-0">
                <label for="job-select" class="form-label">岗位</label>
                <select id="job-select" v-model="selectedJob" class="form-select" :disabled="!selectedField">
                  <option disabled value="">请先选择领域</option>
                  <option v-for="job in filteredJobs" :key="job.value" :value="job.value">
                    {{ job.label }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 col-lg-2 mb-3 mb-lg-0">
                <label for="difficulty-select" class="form-label">难度</label>
                <select id="difficulty-select" v-model="selectedDifficulty" class="form-select">
                  <option disabled value="">请选择</option>
                  <option v-for="difficulty in difficulties" :key="difficulty" :value="difficulty">
                    {{ difficulty }}
                  </option>
                </select>
              </div>
              <div class="col-md-6 col-lg-3">
                <button 
                  @click="fetchQuestions" 
                  class="btn-update-questions w-100"
                  :disabled="!canStart || isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  {{ isLoading ? '加载中...' : '更新题目' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 题目展示区域 -->
      <div class="row justify-content-center">
        <div class="col-lg-12">
          <!-- 加载状态 -->
          <div class="loading-state" v-if="isLoading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">正在努力加载题库...</p>
          </div>
          
          <!-- 题目内容 -->
          <div class="questions-container" v-else>
            <div v-if="questions.length > 0">
              <div v-for="(question, index) in questions" :key="question.id || index" class="question-card card">
                <div class="card-header">
                  <h5 class="question-title">题目 #{{ index + 1 }}</h5>
                  <span class="difficulty-badge" :class="getDifficultyClass(question.degree)">
                    {{ question.degree }}
                  </span>
                </div>
                <div class="card-body">
                  <div class="question-content">
                    <div class="question-header">
                        <p class="question-prefix">面试题：</p>
                        <button @click="copyText(question.question, question, 'question')" class="btn-copy">
                            <i class="icon-copy"></i> {{ question.questionCopied ? '已复制!' : '复制题目问问AI' }}
                        </button>
                    </div>
                    <p class="question-text">{{ question.question }}</p>
                  </div>
                  
                  <!-- 用户回答部分 -->
                  <div class="user-answer-section">
                    <label :for="'user-answer-' + index" class="form-label">你的回答：</label>
                    <textarea :id="'user-answer-' + index" v-model="question.userAnswer" class="form-control user-answer-textarea" rows="4" placeholder="在此输入你的答案，方便整理和复制..."></textarea>
                    <button @click="copyText(question.userAnswer, question, 'answer')" class="btn-copy-answer" :disabled="!question.userAnswer">
                      <i class="icon-copy"></i> {{ question.answerCopied ? '已复制!' : '复制回答' }}
                    </button>
                  </div>
                  
                  <button @click="toggleAnswer(index)" class="btn-toggle-answer">
                    <i :class="question.showAnswer ? 'icon-eye-off' : 'icon-eye-on'"></i>
                    {{ question.showAnswer ? '隐藏答案' : '显示答案' }}
                  </button>

                  <div class="answer-area-wrapper" v-if="question.showAnswer">
                    <div class="answer-area">
                      <p class="answer-prefix">参考答案</p>
                      <p class="answer-text">{{ question.answer }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="empty-state card" v-else>
              <i class="icon-empty-box"></i>
              <p class="h5">暂无题目</p>
              <p>请尝试选择其他领域或难度。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "PracticeSystem",
  data() {
    return {
      fields: [
        { value: 'ai', label: '人工智能', apiValue: 'ai' },
        { value: 'bigdata', label: '大数据', apiValue: 'bigdata' },
        { value: 'iot', label: '物联网', apiValue: 'internetofthings' },
        { value: 'cloud', label: '云计算', apiValue: 'cloud' },
        { value: 'frontend', label: '前端开发', apiValue: 'frontend' },
        { value: 'backend', label: '后端开发', apiValue: 'backend' },
      ],
      jobs: [
        { value: 'ml_engineer', label: '机器学习测试工程师', field: 'ai' },
        { value: 'bigdata_engineer', label: '大数据开发工程师', field: 'bigdata' },
        { value: 'iot_architect', label: '物联网产品经理', field: 'iot' },
        { value: 'cloud_architect', label: '云架构师', field: 'cloud' },
        { value: 'frontend_developer', label: '前端开发工程师', field: 'frontend' },
        { value: 'backend_developer', label: '后端开发工程师', field: 'backend' },
      ],
      difficulties: ['简单', '中等', '困难'],
      
      selectedField: 'bigdata',
      selectedJob: 'bigdata_engineer',
      selectedDifficulty: '简单',

      questions: [],
      isLoading: true,
    };
  },
  computed: {
    filteredJobs() {
      if (!this.selectedField) return [];
      return this.jobs.filter(job => job.field === this.selectedField);
    },
    canStart() {
      return this.selectedField && this.selectedJob && this.selectedDifficulty;
    },
  },
  created() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      this.isLoading = true;
      this.questions = [];

      const liveJobs = new Set(['ml_engineer', 'bigdata_engineer', 'iot_architect']);
      if (!this.selectedJob || !liveJobs.has(this.selectedJob)) {
        if(this.selectedJob) alert('该岗位下的题库正在建设中，敬请期待！');
        this.isLoading = false;
        return;
      }

      try {
        const selectedJobObject = this.jobs.find(j => j.value === this.selectedJob);
        const correspondingField = this.fields.find(f => f.value === selectedJobObject.field);
        const apiParam = correspondingField.apiValue;

        const response = await axios.get(`http://localhost:8000/api/questions/${apiParam}`, {
          params: {
            degree: this.selectedDifficulty,
            limit: 50 
          }
        });

        if (response.status === 200 && response.data.code === 200) {
          if (response.data.data && response.data.data.length > 0) {
            this.questions = response.data.data.map(q => ({ 
              ...q, 
              showAnswer: false, 
              userAnswer: '', 
              questionCopied: false, 
              answerCopied: false 
            }));
          }
        } else {
          alert(response.data.message || '题目加载失败');
        }
      } catch (error) {
        console.error('获取题目失败:', error);
        alert('获取题目失败，请检查网络或稍后再试');
      } finally {
        this.isLoading = false;
      }
    },
    toggleAnswer(index) {
      this.questions[index].showAnswer = !this.questions[index].showAnswer;
    },
    getDifficultyClass(level) {
      return {
        'difficulty-easy': level === '简单',
        'difficulty-medium': level === '中等',
        'difficulty-hard': level === '困难'
      };
    },
    // 文本复制功能
    copyText(textToCopy, question, type) {
      if (!textToCopy) return;    
      navigator.clipboard.writeText(textToCopy).then(() => {
        if (type === 'question') {
          question.questionCopied = true;
        } else if (type === 'answer') {
          question.answerCopied = true;
        }
        setTimeout(() => {
          if (type === 'question') {
            question.questionCopied = false;
          } else if (type === 'answer') {
            question.answerCopied = false;
          }
        }, 1500); // 1.5秒后恢复按钮状态
      }).catch(err => {
        console.error('复制失败: ', err);
        alert('复制失败，您的浏览器可能不支持或未授权。');
      });
    }
  },
  watch: {
    selectedField(newValue, oldValue) {
        if (newValue !== oldValue) {
            this.selectedJob = '';
        }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.practice-system-wrapper {
  --primary-color: #4f46e5;
  --primary-hover-color: #4338ca;
  --secondary-color: #e0e7ff;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --bg-color: #f9fafb;
  --card-bg-color: #f7f8ff; 
  --border-color: #e5e7eb;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --answer-bg: #eff6ff; 
  --answer-border: #3b82f6;
  --font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.07), 0 1px 2px -1px rgba(0, 0, 0, 0.07);
  --card-shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.08);

  background-color: var(--bg-color);
  font-family: var(--font-family);
  min-height: 100vh;
}

.header-section {
  text-align: center;
  margin-bottom: 2.5rem;
  padding-top: 1rem;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
}

.filter-card {
  padding: 1.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  display: block;
}

.form-select {
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  padding: 0.625rem 1rem;
  font-size: 0.95rem;
  transition: all 0.2s ease-in-out;
  background-color: #ffffff; 
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
}
.form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
  outline: none;
}
.form-select:disabled {
  background-color: #f3f4f6;
  opacity: 0.7;
}

.btn-update-questions {
  background-color: var(--primary-color);
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 0.5rem;
  padding: 0.625rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: calc(1.5em + 1.25rem + 2px);
}
.btn-update-questions:hover:not(:disabled) {
  background-color: var(--primary-hover-color);
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}
.btn-update-questions:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.question-card {
  margin-bottom: 1.5rem;
  transition: all 0.2s ease-in-out;
}
.question-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: transparent;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}
.question-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0;
}
.difficulty-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3em 0.8em;
  border-radius: 9999px;
  color: white;
}
.difficulty-easy { background-color: var(--success-color); }
.difficulty-medium { background-color: var(--warning-color); }
.difficulty-hard { background-color: var(--danger-color); }

.card-body {
  padding: 1.5rem;
}
.question-content {
  margin-bottom: 1.5rem;
}

.question-prefix {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}
.question-text {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-primary);
}

.btn-toggle-answer {
  background-color: #ffffff; 
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.btn-toggle-answer:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
  color: var(--primary-color);
}

.icon-eye-on::before { content: "👁️"; }
.icon-eye-off::before { content: "🙈"; }

.answer-area-wrapper {
  margin-top: 1.5rem;
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.answer-area {
  background-color: var(--answer-bg);
  border-radius: 0.5rem;
  padding: 1.25rem;
  border-left: 4px solid var(--answer-border);
}
.answer-prefix {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--answer-border);
  margin-bottom: 0.5rem;
}
.answer-text {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}
.loading-state .spinner-border {
  width: 3rem;
  height: 3rem;
  color: var(--primary-color);
}
.empty-state {
  background-color: var(--card-bg-color);
  border-radius: 0.75rem;
}
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
.icon-empty-box::before { content: "📦"; }

.card {
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  box-shadow: var(--card-shadow);
  background-color: var(--card-bg-color); 
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.question-prefix {
  margin-bottom: 0; 
}

.btn-copy {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.btn-copy:hover {
  background-color: #f3f4f6;
  color: var(--primary-color);
}
.icon-copy::before {
  content: "📋";
  font-size: 0.9em;
}

.user-answer-section {
  margin-bottom: 1.5rem;
}

.user-answer-textarea {
  font-family: var(--font-family);
  font-size: 0.95rem;
  line-height: 1.6;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #ffffff;
}
.user-answer-textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
  outline: none;
}

.btn-copy-answer {
  background-color: #f3f4f6;
  color: var(--text-secondary);
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.btn-copy-answer:hover:not(:disabled) {
  background-color: var(--secondary-color);
  color: var(--primary-color);
}
.btn-copy-answer:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

</style>