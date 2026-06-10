<template>
  <div class="profile-page">
    <div class="profile-banner" :style="{ backgroundImage: 'url(' + require('@/assets/img/curved-images/curved14.jpg') + ')' }">
      <span class="banner-mask"></span>
    </div>

    <div class="container-fluid main-content">
      <!-- 用户信息部分 -->
      <div class="user-card card">
        <div class="user-info-wrapper">
          <div class="avatar-wrapper" @click="handleAvatarClick">
            <img :src="avatarUrl" alt="profile_image" class="user-avatar" />
            <div class="avatar-overlay">
              <span>更换头像</span>
            </div>
            <input type="file" ref="avatarInput" accept="image/*" style="display: none" @change="handleAvatarChange" />
          </div>
          <div class="user-details">
            <h5 class="user-name">{{ info.nickname || '未设置昵称' }}</h5>
            <p class="user-id">@{{ info.account || '未登录' }}</p>
          </div>
          <div class="user-actions">
            <template v-if="isLoggedIn">
              <button class="btn-custom btn-logout" @click="logout">退出登录</button>
            </template>
            <template v-else>
              <button class="btn-custom btn-secondary" @click="goToRegister">注册</button>
              <button class="btn-custom btn-primary" @click="goToLogin">登录</button>
            </template>
          </div>
        </div>
      </div>

      <!-- 个人资料部分 -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="info-card card">
            <div class="card-header">
              <h6 class="card-title">个人资料</h6>
              <div v-if="!isEditing" class="header-actions">
                <button class="btn-custom btn-secondary btn-sm" @click="showPasswordModal = true">修改密码</button>
                <button class="btn-custom btn-primary btn-sm" @click="startEditing">编辑资料</button>
              </div>
            </div>
            <div class="card-body">
              <template v-if="!isEditing">
                <div class="profile-details-grid">
                  <div class="detail-item"><span>昵称</span><strong>{{ info.nickname }}</strong></div>
                  <div class="detail-item"><span>账号</span><strong>{{ info.account }}</strong></div>
                  <div class="detail-item"><span>学校</span><strong>{{ info.school }}</strong></div>
                  <div class="detail-item"><span>专业</span><strong>{{ info.major }}</strong></div>
                  <div class="detail-item"><span>学历</span><strong>{{ info.education }}</strong></div>
                  <div class="detail-item"><span>生日</span><strong>{{ info.birthday }}</strong></div>
                </div>
              </template>
              <template v-else>
                <div class="row g-3">
                  <div class="col-md-6"><label class="form-label">昵称</label><input v-model="info.nickname" type="text" class="form-control" /></div>
                  <div class="col-md-6"><label class="form-label">账号</label><input v-model="info.account" type="text" class="form-control" disabled /></div>
                  <div class="col-md-6"><label class="form-label">学校</label><input v-model="info.school" type="text" class="form-control" /></div>
                  <div class="col-md-6"><label class="form-label">专业</label><input v-model="info.major" type="text" class="form-control" /></div>
                  <div class="col-md-6"><label class="form-label">学历</label><select v-model="info.education" class="form-select"><option>高职</option><option>本科</option><option>研究生</option><option>博士</option></select></div>
                  <div class="col-md-6"><label class="form-label">生日</label><input v-model="info.birthday" type="date" class="form-control" /></div>
                </div>
                <div class="d-flex justify-content-end mt-4">
                  <button class="btn-custom btn-secondary me-2" @click="cancelEditing">取消</button>
                  <button class="btn-custom btn-primary" @click="submitProfileUpdate">保存更改</button>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的发布 -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="info-card card">
            <div class="card-header">
              <h6 class="card-title">我的发布</h6>
            </div>
            <div class="card-body">
              <div v-if="myPosts.length > 0" class="my-posts-list">
                <div v-for="post in myPosts" :key="post.id" class="post-item">
                  <div class="post-info">
                    <router-link :to="{ name: 'PostDetail', params: { id: post.id } }" class="post-title-link">
                      {{ post.title }}
                    </router-link>
                    <div class="post-meta">
                      <span class="badge post-category-badge">{{ post.category }}</span>
                      <span class="post-time">{{ formatDate(post.createdAt) }}</span>
                    </div>
                  </div>
                  <div class="post-actions">
                     <router-link :to="{ name: 'PostDetail', params: { id: post.id } }" class="btn-custom btn-secondary btn-sm">
                      查看
                    </router-link>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>您还没有发布任何内容</p>
                <router-link :to="{name: 'Forum'}" class="btn-custom btn-primary btn-sm">去论坛逛逛</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 我的收藏 -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="info-card card">
            <div class="card-header">
              <h6 class="card-title">我的收藏</h6>
            </div>
            <div class="card-body">
              <div v-if="myFavorites.length > 0" class="my-posts-list">
                <div v-for="post in myFavorites" :key="post.id" class="post-item">
                  <div class="post-info">
                    <router-link :to="{ name: 'PostDetail', params: { id: post.id } }" class="post-title-link">
                      {{ post.title }}
                    </router-link>
                    <div class="post-meta">
                      <span class="badge post-category-badge">{{ post.category }}</span>
                      <span class="post-time">作者: {{ post.author }}</span>
                    </div>
                  </div>
                  <div class="post-actions">
                     <router-link :to="{ name: 'PostDetail', params: { id: post.id } }" class="btn-custom btn-secondary btn-sm">
                      查看
                    </router-link>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>您还没有收藏任何帖子</p>
                <router-link :to="{name: 'Forum'}" class="btn-custom btn-primary btn-sm">去发现宝藏</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 简历和历史报告 -->
      <div class="row mt-4">
        <div class="col-lg-5 mb-4 mb-lg-0">
          <div class="info-card card h-100">
            <div class="card-header"><h6 class="card-title">简历上传</h6></div>
            <div class="card-body resume-section">
              <p class="status-text">当前状态：
                <span v-if="info.hasResume" class="status-badge status-success">已上传</span>
                <span v-else class="status-badge status-muted">未上传</span>
              </p>
              <div class="resume-actions">
                <label for="resumeUpload" class="btn-custom btn-primary">{{ info.hasResume ? '更新简历' : '上传简历' }}</label>
                <input id="resumeUpload" type="file" accept=".pdf" @change="handleResumeUpload" style="display: none;" />
                <a v-if="info.hasResume" :href="getResumeDownloadUrl()" target="_blank" class="btn-custom btn-secondary">下载简历</a>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-7">
          <div class="info-card card h-100">
            <div class="card-header">
              <h6 class="card-title">历史报告及视频</h6>
              <button class="btn-custom btn-primary btn-sm" @click="fetchHistoryReports" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ loading ? '加载中...' : '刷新列表' }}
              </button>
            </div>
            <div class="card-body">
              <div v-if="historyReports.length > 0" class="history-list">
                <div v-for="report in historyReports" :key="report.reportID" class="history-item">
                  <div class="report-info"><p class="report-job">{{ report.job }}</p><p class="report-time">{{ formatDate(report.datetime) }}</p></div>
                  <div class="report-actions">
                    <button class="btn-custom btn-secondary btn-sm" @click="previewVideo(report.videoID)">预览视频</button>
                    <button class="btn-custom btn-primary btn-sm" @click="viewReport(report)">查看报告</button>
                  </div>
                </div>
              </div>
              <div v-else-if="historyLoaded && !loading" class="empty-state"><p>暂无历史报告数据</p></div>
              <div v-if="loading && !historyLoaded" class="loading-state"><div class="spinner-border spinner-border-sm" role="status"></div></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 修改密码部分 -->
      <div v-if="showPasswordModal" class="modal-backdrop">
        <div class="modal-content card">
          <div class="modal-header"><h5 class="modal-title">修改密码</h5><button type="button" class="btn-close" @click="cancelPasswordModal"></button></div>
          <div class="modal-body">
            <input type="password" v-model="newPassword" class="form-control mb-3" placeholder="新密码" />
            <input type="password" v-model="confirmPassword" class="form-control" placeholder="确认新密码" />
          </div>
          <div class="modal-footer"><button class="btn-custom btn-secondary" @click="cancelPasswordModal">取消</button><button class="btn-custom btn-primary" @click="submitPasswordChange">保存</button></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { posts, favorites } from "../store/store.js";

export default {
  name: "Profile",
  data() {
    return {
      isLoggedIn: false,
      avatarUrl: require("@/assets/img/default.png"),
      isEditing: false,
      info: { nickname: "", account: "", school: "", major: "", education: "", birthday: "", hasResume: false },
      showPasswordModal: false,
      newPassword: "",
      confirmPassword: "",
      backupInfo: {},
      historyReports: [],
      historyLoaded: false,
      loading: false,
    }
  },
  computed: {
    myPosts() {
      if (!this.isLoggedIn || !this.info.nickname) {
        return [];
      }
      return posts.value.filter(post => post.author === this.info.nickname);
    },
    myFavorites() {
      return favorites.value
        .map(favId => posts.value.find(post => post.id === favId))
        .filter(post => post); 
    }
  },
  created() {
    const accountID = this.$route.query.accountID || localStorage.getItem("account");
    if (accountID) {
      this.fetchUserInfo(accountID);
      this.fetchHistoryReports();
    } else {
      this.isLoggedIn = false;
    }
  },
  methods: {
    async fetchUserInfo(accountID) {
      this.loading = true;
      try {
        const res = await axios.get(`http://localhost:8000/api/users/${accountID}`);
        if (res.data.code === 200 && res.data.data) {
          this.isLoggedIn = true;
          const data = res.data.data;
          this.info = {
            nickname: data.nickName,
            account: data.accountID, school: data.schoolName,
            major: data.major, education: data.qualification, birthday: data.birthday,
            hasResume: data.hasResume
          };
          localStorage.setItem("account", data.accountID);
          try {
            const avatarRes = await axios.get(`http://localhost:8000/api/users/${accountID}/avatar`, { responseType: 'blob' });
            this.avatarUrl = URL.createObjectURL(avatarRes.data);
          } catch (err) { this.avatarUrl = require("@/assets/img/default.png"); }
        } else {
          this.isLoggedIn = false;
        }
      } catch (err) {
        this.isLoggedIn = false;
      } finally {
        this.loading = false;
      }
    },
    startEditing() {
      this.backupInfo = JSON.parse(JSON.stringify(this.info));
      this.isEditing = true;
    },
    cancelEditing() {
      this.info = JSON.parse(JSON.stringify(this.backupInfo));
      this.isEditing = false;
    },
    handleAvatarClick() { this.$refs.avatarInput.click(); },
    async handleAvatarChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
        alert("只允许上传 JPG, PNG, GIF, WebP 格式的图片。"); return;
      }
      const formData = new FormData();
      formData.append('avatar_file', file);
      try {
        const res = await axios.post(`http://localhost:8000/api/users/${this.info.account}/avatar/upload`, formData);
        if (res.data.code === 200) {
          alert("头像更换成功！");
          this.avatarUrl = URL.createObjectURL(file);
        } else { throw new Error(res.data.message || "头像上传失败"); }
      } catch (err) { alert(err.response?.data?.detail || err.message || "上传头像时发生未知错误"); }
    },
    async submitProfileUpdate() {
      try {
        const userInfoPayload = {};
        const fieldsMap = { nickName: 'nickname', schoolName: 'school', major: 'major', qualification: 'education', birthday: 'birthday' };
        Object.keys(fieldsMap).forEach(key => {
            const frontendKey = fieldsMap[key];
            if (this.info[frontendKey] !== this.backupInfo[frontendKey] && this.info[frontendKey] != null && this.info[frontendKey] !== '') {
                userInfoPayload[key] = this.info[frontendKey];
            }
        });
        if (Object.keys(userInfoPayload).length > 0) {
            const res = await axios.put(`http://localhost:8000/api/users/${this.info.account}`, userInfoPayload);
            if (res.data.code !== 200) throw new Error(res.data.message || "用户信息更新失败");
        }
        alert("资料保存成功！");
        this.isEditing = false;
      } catch (err) { alert(err.message || "请求失败"); }
    },
    cancelPasswordModal() { this.showPasswordModal = false; this.newPassword = ""; this.confirmPassword = ""; },
    async submitPasswordChange() {
      if (!this.newPassword || this.newPassword !== this.confirmPassword) {
        alert("密码为空或两次输入不一致！"); return;
      }
      try {
        const res = await axios.put(`http://localhost:8000/api/users/${this.info.account}`, { password: this.newPassword });
        if (res.data.code === 200) {
          alert("密码修改成功"); this.cancelPasswordModal();
        } else { alert(res.data.message || "修改失败"); }
      } catch (err) { alert("请求失败"); }
    },
    async handleResumeUpload(event) {
      const file = event.target.files[0];
      if (!file || file.type !== "application/pdf") { alert("请选择一个 PDF 格式的简历文件"); return; }
      const formData = new FormData();
      formData.append("resume_file", file);
      const uploadUrl = `http://localhost:8000/api/users/${this.info.account}/resume/upload`;
      try {
        const res = await axios.post(uploadUrl, formData);
        if (res.data.code === 200) { alert("简历上传成功"); this.info.hasResume = true; }
        else { throw new Error(res.data.message || "上传失败"); }
      } catch (err) {
        if (err.response?.status === 409 && confirm("简历已存在，是否覆盖？")) {
          try {
            const res2 = await axios.post(`${uploadUrl}?overwrite=true`, formData);
            if (res2.data.code === 200) { alert("简历覆盖上传成功"); this.info.hasResume = true; }
            else { throw new Error(res2.data.message || "覆盖上传失败"); }
          } catch (err2) { alert(err2.response?.data?.detail || "覆盖上传失败"); }
        } else { alert(err.response?.data?.detail || "上传失败"); }
      }
    },
    getResumeDownloadUrl() { return `http://localhost:8000/api/download/resume/${this.info.account}/download`; },
    formatDate(datetimeString) {
      if (!datetimeString) return 'N/A';
      const date = new Date(datetimeString);
      // 检查日期是否有效
      if (isNaN(date)) return 'Invalid Date';
      // 仅格式化日期部分
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    },
    async fetchHistoryReports() {
      const accountID = this.info.account || localStorage.getItem("account");
      if (!accountID) { return; }
      this.loading = true; this.historyLoaded = false; this.historyReports = [];
      try {
        const res = await axios.get(`http://localhost:8000/api/interview/reports/history/${accountID}`);
        if (res.data?.code === 200 && Array.isArray(res.data.data)) {
          this.historyReports = res.data.data;
        } else { this.historyReports = []; }
      } catch (error) { this.historyReports = []; }
      finally { this.loading = false; this.historyLoaded = true; }
    },
    viewReport(report) { localStorage.setItem('reportData', JSON.stringify(report)); this.$router.push({ name: 'ReportDetail' }); },
    previewVideo(videoID) { window.open(`http://localhost:8000/api/download/video/${this.info.account}/${videoID}/download?preview=true`, '_blank'); },
    goToLogin() { this.$router.push("/sign-in"); },
    goToRegister() { this.$router.push("/sign-up"); },
    logout() {
      this.isLoggedIn = false;
      this.avatarUrl = require("@/assets/img/default.png");
      this.info = { nickname: "", account: "", school: "", major: "", education: "", birthday: "", hasResume: false };
      this.historyReports = []; this.historyLoaded = false;
      localStorage.removeItem('account');
      this.$router.replace({ name: "Profile", query: {} });
    },
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.profile-page {
  --primary-color: #16a34a; --primary-hover-color: #15803d;
  --secondary-color: #f0fdf4; --accent-color: #a3e635;
  --danger-color: #ef4444; --text-primary: #1f2937;
  --text-secondary: #6b7280; --bg-color: #f8fafc;
  --card-bg-color: #ffffff; --border-color: #e5e7eb;
  --font-family: 'Inter', sans-serif;
  --card-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
  background-color: var(--bg-color); font-family: var(--font-family);
}
.profile-banner { height: 300px; border-radius: 1.5rem; margin: 1rem; background-size: cover; background-position: center; position: relative; }
.banner-mask { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(310deg, var(--primary-color), var(--accent-color)); opacity: 0.6; border-radius: 1.5rem; }
.main-content { margin-top: -80px; }
.user-card { padding: 1.5rem; position: relative; z-index: 2; }
.user-info-wrapper { display: flex; align-items: center; gap: 1.5rem; }
.avatar-wrapper { position: relative; width: 90px; height: 90px; cursor: pointer; }
.user-avatar { width: 100%; height: 100%; object-fit: cover; border-radius: 0.75rem; border: 4px solid var(--card-bg-color); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.avatar-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); color: white; display: flex; align-items: center; justify-content: center; border-radius: 0.75rem; opacity: 0; transition: opacity 0.3s ease; font-size: 0.875rem; }
.avatar-wrapper:hover .avatar-overlay { opacity: 1; }
.user-details { flex-grow: 1; }
.user-name { font-size: 1.5rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; }
.user-id { font-size: 0.9rem; color: var(--text-secondary); margin: 0; }
.user-actions { margin-left: auto; }
.info-card { padding: 0; }
.card-header { padding: 1.25rem 1.5rem; background-color: transparent; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.card-body { padding: 1.5rem; }
.profile-details-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem 2.5rem; }
.detail-item { display: flex; flex-direction: column; }
.detail-item span { font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem; }
.detail-item strong { font-size: 1rem; font-weight: 500; color: var(--text-primary); }
.resume-section { display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
.status-text { color: var(--text-secondary); }
.status-badge { padding: 0.25em 0.6em; font-size: 0.8rem; border-radius: 999px; font-weight: 600; }
.status-success { background-color: var(--secondary-color); color: var(--primary-hover-color); }
.status-muted { background-color: #f3f4f6; color: #6b7280; }
.resume-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.history-list { max-height: 250px; overflow-y: auto; padding-right: 0.5rem; }
.history-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-radius: 0.5rem; transition: background-color 0.2s ease; }
.history-item:not(:last-child) { border-bottom: 1px solid var(--border-color); }
.history-item:hover { background-color: var(--secondary-color); }
.report-job { font-weight: 600; color: var(--text-primary); margin: 0; }
.report-time { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }
.report-actions { display: flex; gap: 0.5rem; }
.btn-custom { border: 1px solid transparent; padding: 0.5rem 1rem; font-size: 0.875rem; font-weight: 600; border-radius: 0.5rem; cursor: pointer; transition: all 0.2s ease; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.8rem; }
.btn-primary { background-color: var(--primary-color); color: white; border-color: var(--primary-color); }
.btn-primary:hover { background-color: var(--primary-hover-color); border-color: var(--primary-hover-color); transform: translateY(-2px); }
.btn-secondary { background-color: transparent; color: var(--text-secondary); border-color: var(--border-color); }
.btn-secondary:hover { background-color: #f3f4f6; color: var(--text-primary); }
.btn-logout { background-color: transparent; color: var(--danger-color); border-color: var(--danger-color); }
.btn-logout:hover { background-color: var(--danger-color); color: white; }
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1050; }
.modal-content { width: 500px; max-width: 90%; animation: modal-fade-in 0.3s ease-out; }
@keyframes modal-fade-in { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header, .modal-body, .modal-footer { padding: 1.5rem; }
.modal-header { border-bottom: 1px solid var(--border-color); }
.modal-footer { border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; }
.modal-title { font-size: 1.25rem; font-weight: 600; }
.btn-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; }
.card { border: 1px solid var(--border-color); border-radius: 1rem; box-shadow: var(--card-shadow); background-color: var(--card-bg-color); }
.empty-state, .loading-state { text-align: center; padding: 2rem; color: var(--text-secondary); }
.my-posts-list { max-height: 300px; overflow-y: auto; padding-right: 0.5rem; }
.post-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; transition: background-color 0.2s ease; }
.post-item:not(:last-child) { border-bottom: 1px solid var(--border-color); }
.post-info { display: flex; flex-direction: column; }
.post-title-link { font-weight: 600; color: var(--text-primary); text-decoration: none; margin-bottom: 0.25rem; transition: color 0.2s ease; }
.post-title-link:hover { color: var(--primary-color); }
.post-meta { display: flex; align-items: center; gap: 0.75rem; }
.post-category-badge { background-color: #eef2ff; color: #4f46e5; font-size: 0.75rem; font-weight: 500; padding: 0.2em 0.5em; }
.post-time { font-size: 0.875rem; color: var(--text-secondary); }
.post-actions .btn-custom { transform: scale(0.9); opacity: 0.8; }
.post-item:hover .post-actions .btn-custom { opacity: 1; }
.empty-state p { margin-bottom: 1rem; }
@media (max-width: 768px) { .profile-details-grid { grid-template-columns: 1fr; gap: 1rem; } }
</style>