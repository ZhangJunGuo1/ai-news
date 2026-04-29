<template>
  <section class="news-section">
    <div class="section-header">
      <h2 class="section-title">
        <span class="section-icon">{{ getIconEmoji(categoryIcon) }}</span>
        {{ title }}
      </h2>
      <div class="section-actions">
        <button class="action-btn" @click="$emit('refresh')">
          <span class="btn-icon">🔄</span>
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <div class="error-text">{{ error }}</div>
    </div>

    <div v-else-if="newsList.length === 0" class="empty-state">
      <div class="empty-icon">📰</div>
      <div class="empty-text">暂无新闻数据</div>
    </div>

    <div v-else class="news-list">
      <div v-for="(news, index) in newsList" :key="index" class="news-item">
        <div class="news-item-header">
          <h3 class="news-title">{{ news.title }}</h3>
          <span class="news-badge" :class="badgeClass">{{ badgeText }}</span>
        </div>
        <p class="news-summary">{{ news.summary }}</p>
        <div class="news-meta">
          <span class="news-date">{{ news.date || new Date().toLocaleDateString() }}</span>
          <span class="news-source">{{ news.source || '新闻来源' }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { getIconByName } from '../config/icons'

interface Props {
  title: string
  categoryIcon: string
  badgeText: string
  badgeClass?: string
  newsList: any[]
  loading: boolean
  error: string
}

const props = defineProps<Props>()

defineEmits(['refresh'])

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}
</script>

<style scoped>
.news-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color);
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 24px;
}

.section-actions {
  display: flex;
  gap: 12px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 16px;
}

.loading-text {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 500;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 16px;
  color: var(--error-color);
}

.error-icon {
  font-size: 48px;
}

.error-text {
  font-size: 16px;
  font-weight: 500;
  text-align: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 16px;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
  color: var(--text-secondary);
}

.empty-text {
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 500;
}

.news-list {
  display: grid;
  gap: 20px;
}

.news-item {
  padding: 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-large);
  background: var(--bg-container);
  transition: all var(--transition-slow);
}

.news-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
  background: var(--bg-hover);
}

.news-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.news-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  margin-right: 12px;
}

.news-badge {
  background: var(--success-color);
  color: white;
  padding: 4px 12px;
  border-radius: var(--radius-circle);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.news-badge.international {
  background: var(--warning-color);
}

.news-summary {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

.news-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.news-date, .news-source {
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .news-section {
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .section-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
