<template>
  <main class="settings-content">
    <section class="settings-section">
      <div class="section-header">
        <h2 class="section-title">
          <span class="section-icon">{{ pageIcon }}</span>
          基本设置
        </h2>
        <div class="section-actions">
          <button class="action-btn" @click="fetchConfigs">
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

      <div v-else class="settings-form">
        <div class="form-item">
          <label class="form-label">系统图标</label>
          <div class="form-input-wrapper">
            <IconSelector v-model="form.app_icon" placeholder="请选择系统图标" />
          </div>
          <div class="form-hint">当前选择: {{ getIconLabel(form.app_icon) }}</div>
        </div>

        <div class="form-item">
          <label class="form-label">系统名称</label>
          <div class="form-input-wrapper">
            <input 
              v-model="form.app_name" 
              class="form-input" 
              placeholder="请输入系统名称"
            />
          </div>
          <div class="form-hint">页面左上角显示的系统名称</div>
        </div>

        <div class="form-item">
          <label class="form-label">登录背景图</label>
          <div class="form-input-wrapper">
            <input 
              v-model="form.login_background" 
              class="form-input" 
              placeholder="请输入背景图片文件名，如 login-bg.jpg"
            />
          </div>
          <div class="form-hint">登录页面背景图片，存放在 public 目录下</div>
        </div>

        <div class="divider">
          <span class="divider-text">大语言模型配置</span>
        </div>

        <div class="form-item">
          <label class="form-label">API Key</label>
          <div class="form-input-wrapper">
            <input 
              v-model="form.llm_api_key" 
              class="form-input" 
              type="password"
              placeholder="请输入 LLM API Key"
            />
          </div>
          <div class="form-hint">兼容 OpenAI 格式的 API Key</div>
        </div>

        <div class="form-item">
          <label class="form-label">Base URL</label>
          <div class="form-input-wrapper">
            <input 
              v-model="form.llm_base_url" 
              class="form-input" 
              placeholder="如：https://api.openai.com/v1"
            />
          </div>
          <div class="form-hint">LLM API 的基础 URL，末尾不要加斜杠</div>
        </div>

        <div class="form-item">
          <label class="form-label">模型名称</label>
          <div class="form-input-wrapper">
            <input 
              v-model="form.llm_model" 
              class="form-input" 
              placeholder="如：gpt-3.5-turbo"
            />
          </div>
          <div class="form-hint">使用的 LLM 模型名称</div>
        </div>

        <div class="form-actions">
          <button class="action-btn primary" @click="saveConfigs" :disabled="saving">
            <span v-if="saving" class="loading-spinner"></span>
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { get, put } from '../utils/request'
import { ICON_LIST } from '../config/icons'
import IconSelector from '../components/IconSelector.vue'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const form = ref({
  app_icon: '',
  app_name: '',
  login_background: '',
  llm_api_key: '',
  llm_base_url: '',
  llm_model: ''
})

const getIconLabel = (name: string): string => {
  const icon = ICON_LIST.find(i => i.name === name)
  return icon ? `${icon.emoji} ${icon.label}` : '未选择'
}

const fetchConfigs = async () => {
  try {
    loading.value = true
    error.value = ''

    const data: any = await get('/api/configs')
    if (data.success && data.configs) {
      form.value.app_icon = data.configs.app_icon?.value || ''
      form.value.app_name = data.configs.app_name?.value || ''
      form.value.login_background = data.configs.login_background?.value || ''
      form.value.llm_api_key = data.configs.llm_api_key?.value || ''
      form.value.llm_base_url = data.configs.llm_base_url?.value || ''
      form.value.llm_model = data.configs.llm_model?.value || 'gpt-3.5-turbo'
    }
  } catch (err: any) {
    error.value = '获取配置失败，请重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const saveConfigs = async () => {
  try {
    saving.value = true
    error.value = ''

    const configs = {
      app_icon: form.value.app_icon,
      app_name: form.value.app_name,
      login_background: form.value.login_background,
      llm_api_key: form.value.llm_api_key,
      llm_base_url: form.value.llm_base_url,
      llm_model: form.value.llm_model
    }

    const data: any = await put('/api/configs', { configs })
    $message.success(data.message || '保存成功')
    
    localStorage.setItem('app_name', form.value.app_name)
    localStorage.setItem('app_icon', form.value.app_icon)
    localStorage.setItem('login_background', form.value.login_background)
    
    window.dispatchEvent(new Event('config-changed'))
  } catch (err: any) {
    $message.error(err.message || '保存失败，请重试')
    console.error(err)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped>
.settings-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.settings-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  border: 1px solid var(--border-color);
  max-width: 800px;
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

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input-wrapper {
  width: 100%;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
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

.form-hint {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.form-actions {
  margin-top: 16px;
}

.divider {
  margin: 16px 0;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.divider-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-card);
  padding: 0 16px;
  position: relative;
  top: -12px;
}

@media (max-width: 768px) {
  .settings-content {
    padding: 20px;
  }

  .settings-section {
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
