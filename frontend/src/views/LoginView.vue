<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <h1 class="login-title">{{ appName }}</h1>
        <p class="login-subtitle">登录后查看新闻内容</p>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input
              type="text"
              id="username"
              v-model="form.username"
              class="form-input"
              placeholder="请输入用户名"
              required
            >
          </div>
        </div>
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input
              type="password"
              id="password"
              v-model="form.password"
              class="form-input"
              placeholder="请输入密码"
              required
            >
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>{{ loading ? '登录中...' : '登录' }}</span>
          </button>
        </div>
        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { md5 } from '../utils/md5'

const router = useRouter()
const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')
const loginBackground = ref('/login-bg.jpg')
const appName = ref('AI-新闻系统')

const loadConfig = () => {
  const savedBg = localStorage.getItem('login_background')
  const savedName = localStorage.getItem('app_name')
  
  if (savedBg) {
    loginBackground.value = `/${savedBg}`
  }
  if (savedName) {
    appName.value = savedName
  }
  
  const container = document.querySelector('.login-container') as HTMLElement
  if (container) {
    container.style.backgroundImage = `url('${loginBackground.value}')`
  }
}

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''

    const encryptedPassword = md5(form.value.password)

    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: form.value.username,
        password: encryptedPassword
      })
    })

    if (!response.ok) {
      throw new Error('登录失败，请检查用户名和密码')
    }

    const data = await response.json()

    if (data.success) {
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', form.value.username)
      router.push('/news-summary')
    } else {
      throw new Error('登录失败，请检查用户名和密码')
    }
  } catch (err: any) {
    error.value = err.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadConfig()
  window.addEventListener('config-changed', loadConfig)
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-size: cover;
  background-position: center;
  position: relative;
  padding: 20px;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.login-form-wrapper {
  background: var(--bg-card);
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-large);
  padding: 40px;
  width: 100%;
  max-width: 450px;
  position: relative;
  z-index: 2;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
}

.login-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--text-secondary);
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-base);
  background: var(--bg-input);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-color-light);
  background: var(--bg-hover);
}

.form-input::placeholder {
  color: var(--text-secondary);
  opacity: 0.7;
}

.form-actions {
  margin-top: 8px;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left var(--transition-fast);
}

.login-btn:hover::before {
  left: 100%;
}

.login-btn:hover {
  background: var(--primary-color-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: var(--radius-circle);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: var(--error-color-light);
  border: 1px solid var(--error-color);
  border-radius: var(--radius-base);
  padding: 12px 16px;
  color: var(--error-color);
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .login-form-wrapper {
    padding: 32px 24px;
    margin: 0 20px;
  }

  .login-title {
    font-size: 24px;
  }

  .form-input {
    padding: 12px 14px 12px 44px;
  }

  .login-btn {
    padding: 12px;
  }
}
</style>