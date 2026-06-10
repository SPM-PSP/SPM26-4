<template>
  <div class="container-fluid py-4">
    <div v-if="post" class="card">
      <div class="card-header pb-0 d-flex justify-content-between align-items-start">
        <div>
          <h3 class="font-weight-bolder">{{ post.title }}</h3>
          <div class="post-meta">
            <span>作者: {{ post.author }}</span>
            <span>发布于: {{ post.createdAt }}</span>
            <span class="badge bg-primary">{{ post.category }}</span>
          </div>
        </div>
        <button @click="handleToggleFavorite" class="btn btn-favorite flex-shrink-0">
          <i :class="isPostFavorite ? 'fa-solid fa-star' : 'fa-regular fa-star'"></i>
          <span>{{ isPostFavorite ? '已收藏' : '收藏' }}</span>
        </button>
      </div>
      <hr class="horizontal dark my-3">
      <div class="card-body">
        <div class="post-content" v-html="formattedContent"></div>
      </div>
      <div class="card-footer pt-0">
        <router-link :to="{ name: 'Forum' }" class="btn btn-outline-primary mb-0">
          ← 返回论坛
        </router-link>
      </div>
    </div>
    <div v-else class="text-center py-5">
      <h4>帖子未找到</h4>
      <p>您要查找的帖子可能已被删除或链接不正确。</p>
    </div>
  </div>
</template>

<script>

import { ref, onMounted } from 'vue';
import { getPostById, toggleFavorite, isFavorite } from '../store/store.js';

export default {
  name: 'PostDetail',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      // 使用 data 属性来帮助强制刷新视图
      forceUpdate: 0
    }
  },
  computed: {
    formattedContent() {
      if (this.post && this.post.content) {
        return this.post.content.replace(/\n/g, '<br />');
      }
      return '';
    },
    isPostFavorite() {
      // 依赖 this.forceUpdate
      this.forceUpdate;
      return isFavorite(Number(this.id));
    }
  },
  methods: {
    handleToggleFavorite() {
      toggleFavorite(Number(this.id));
      // 点击后，更新 data 属性以触发 computed 属性的重新计算
      this.forceUpdate++;
    }
  },
  setup(props) {
    const post = ref(null);
    onMounted(() => {
      post.value = getPostById(props.id);
    });
    return {
      post,
    };
  }
}
</script>

<style scoped>
.post-meta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 0.5rem;
}
.post-content {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #344767;
}
.btn-favorite {
  background: none;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 1rem;
}
.btn-favorite:hover {
  background-color: #f0fdf4;
  border-color: #16a34a;
  color: #16a34a;
}
.btn-favorite i.fa-solid {
  color: #facc15;
}
</style>