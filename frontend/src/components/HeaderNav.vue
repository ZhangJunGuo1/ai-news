<template>
  <header class="news-header">
    <div class="header-left">
      <h1 class="page-title">{{ title }}</h1>
    </div>
    <div class="header-right">
      <button @click="toggleTheme" class="theme-btn" :title="currentTheme === 'dark' ? '切换亮色主题' : '切换夜间主题'">
        <span class="theme-icon">{{ currentTheme === 'dark' ? '☀️' : '🌙' }}</span>
      </button>
      <div class="user-profile">
        <div class="user-info">
          <span class="user-name">欢迎, {{ username }}</span>
          <button @click="handleLogout" class="logout-btn">
            <span class="logout-icon">🚪</span>
            <span class="logout-text">退出</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTheme, setTheme, type ThemeType } from '../utils/theme'

const props = defineProps<{
  title: string
}>()

const router = useRouter()
const username = ref('')
const currentTheme = ref<ThemeType>('dark')

const checkLogin = () => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  if (!isLoggedIn) {
    router.push('/')
    return false
  }
  username.value = localStorage.getItem('username') || ''
  return true
}

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  setTheme(currentTheme.value)
}

const handleLogout = () => {
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('username')
  router.push('/')
}

onMounted(() => {
  checkLogin()
  currentTheme.value = getTheme()
})
</script>

<style scoped>
.news-header {
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-box);
  position: sticky;
  top: 0;
  z-index: 50;
  height: 72px;
  box-sizing: border-box;
}

.header-left .page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-base);
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
}

.theme-btn:hover {
  background: var(--bg-hover);
  border-color: var(--primary-color);
  transform: scale(1.05);
}

.theme-icon {
  font-size: 20px;
}

.user-profile {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--error-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 14px;
  font-weight: 500;
}

.logout-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

@media (max-width: 768px) {
  .news-header {
    padding: 16px 20px;
    flex-direction: column;
    gap: 12px;
    text-align: center;
    height: auto;
  }

  .header-left, .header-right {
    width: 100%;
  }

  .header-right {
    justify-content: center;
  }

  .user-info {
    justify-content: center;
  }
}
</style>