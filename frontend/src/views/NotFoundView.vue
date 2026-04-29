<template>
  <main class="not-found-content">
    <div class="not-found-container">
      <div class="error-code">404</div>
      <div class="error-title">页面未找到</div>
      <div class="error-description">抱歉，您访问的页面不存在或正在开发中</div>
      <button class="action-btn primary" @click="goHome">返回首页</button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/news-summary')
}
</script>

<style scoped>
.not-found-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
}

.not-found-container {
  text-align: center;
  background: var(--bg-card);
  padding: 60px 40px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  border: 1px solid var(--border-color);
  max-width: 500px;
  width: 100%;
}

.error-code {
  font-size: 120px;
  font-weight: 800;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.error-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 32px;
}
</style>
