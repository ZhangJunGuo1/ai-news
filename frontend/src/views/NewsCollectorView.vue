<template>
  <main class="collector-content">
    <div class="collector-section">
      <h2 class="section-title">
        <span class="section-icon">{{ pageIcon }}</span>
        选择新闻来源
      </h2>
      <div class="source-options">
        <div 
          v-for="source in sources" 
          :key="source.value"
          class="source-option"
          :class="{ active: selectedSource === source.value }"
          @click="selectSource(source.value)"
        >
          <div class="source-icon">{{ source.icon }}</div>
          <div class="source-info">
            <div class="source-name">{{ source.name }}</div>
            <div class="source-desc">{{ source.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="collector-section" v-if="selectedSource">
      <div class="section-header">
        <h2 class="section-title">
          <span class="section-icon">{{ getSourceIcon(selectedSource) }}</span>
          {{ getSourceName(selectedSource) }} - 采集设置
        </h2>
        <div class="section-actions" v-if="selectedSource === 'web'">
          <el-button type="primary" @click="goToNews" :disabled="!hasCollected">查看新闻</el-button>
        </div>
        <div class="section-actions" v-if="selectedSource === 'llm'">
          <el-button type="primary" @click="resetLLMChat">开启新对话</el-button>
        </div>
      </div>
      
      <div v-if="selectedSource === 'api'" class="api-form">
        <div class="form-container">
          <div class="form-item">
            <label class="form-label">选择新闻API</label>
            <el-select v-model="selectedApi" placeholder="请选择新闻API" style="width: 100%">
              <el-option
                v-for="api in newsApis"
                :key="api.value"
                :label="api.name"
                :value="api.value"
              >
                <span style="margin-right: 8px">{{ api.icon }}</span>
                <span>{{ api.name }}</span>
              </el-option>
            </el-select>
          </div>
          <div class="form-item">
            <el-alert
              :title="currentApiDescription"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
          <div class="form-item">
            <el-button 
              type="primary" 
              @click="collectNews" 
              :loading="loading"
              :disabled="!selectedApi"
              style="width: 100%"
            >
              开始采集
            </el-button>
          </div>
        </div>
      </div>

      <div v-else-if="selectedSource === 'llm'" class="llm-chat-section">
        <LLMChat ref="llmChatRef" />
      </div>

      <div v-else-if="selectedSource === 'web'" class="web-scraping-form">
        <div class="form-container">
          <div class="form-item">
            <label class="form-label">网页URL</label>
            <div class="input-wrapper">
              <span class="input-icon">🌐</span>
              <el-input 
                v-model="form.url" 
                placeholder="请输入要采集的网页URL" 
                style="width: 100%"
              />
            </div>
          </div>
          <div class="form-item">
            <el-button 
              type="primary" 
              @click="collectNews" 
              :loading="loading"
              style="width: 100%"
            >
              开始采集
            </el-button>
          </div>
        </div>

        <div class="supported-sites">
          <h3 class="sites-title">支持采集的新闻网站</h3>
          <table class="sites-table">
            <thead>
              <tr>
                <th>网站名称</th>
                <th>示例URL</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="site in supportedSites" :key="site.name">
                <td>{{ site.name }}</td>
                <td class="url-cell">{{ site.example }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { post } from '../utils/request'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'
import LLMChat from '../components/LLMChat.vue'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const router = useRouter()
const llmChatRef = ref<InstanceType<typeof LLMChat> | null>(null)

const sources = [
  {
    value: 'api',
    name: '新闻API',
    icon: '📡',
    description: '从新闻API获取最新资讯'
  },
  {
    value: 'llm',
    name: '大语言模型',
    icon: '🤖',
    description: '使用AI生成新闻内容'
  },
  {
    value: 'web',
    name: '网页爬取',
    icon: '🕷️',
    description: '从指定网页采集新闻内容'
  }
]

const newsApis = [
    {
    value: '60s',
    name: '60秒新闻',
    icon: '⏱️',
    description: '每日60秒新闻速览，快速了解今日热点（免费，无需注册）'
  },
  {
    value: 'cctv',
    name: 'CCTV新闻',
    icon: '📺',
    description: 'CCTV官方RSS最新国内新闻，权威资讯（免费，无需注册）'
  },
  {
    value: 'sina',
    name: '新浪新闻',
    icon: '📰',
    description: '新浪滚动新闻，涵盖国内、国际、社会等（免费，无需注册）'
  },
  {
    value: 'baidu',
    name: '百度热搜',
    icon: '🔥',
    description: '百度实时热搜榜单，反映当前网络热点（免费，无需注册）'
  }
]

const selectedSource = ref('')
const selectedApi = ref('')
const loading = ref(false)
const hasCollected = ref(false)

const form = ref({
  url: ''
})

const supportedSites = [
  { name: '新华网', example: 'http://www.xinhuanet.com/world/20260424/7ca09b489b814bd2826f58b93c1dd9f5/c.html' },
  { name: '中国新闻网', example: 'https://www.chinanews.com.cn/gn/2026/04-25/10610640.shtml' },
  { name: '人民网', example: 'https://world.people.com.cn/n1/2026/0426/c1002-40708728.html' },
  { name: '网易新闻', example: 'https://www.163.com/news/article/KREAT35D000189FH.html' },
  { name: '腾讯网', example: 'https://news.qq.com/rain/a/20260425A05HU400' },
  { name: '央视新闻', example: 'https://ysxw.cctv.cn/article.html?toc_style_id=feeds_default&item_id=14652252681970605513&channelId=1215' },
]

const currentApiDescription = computed(() => {
  const api = newsApis.find(a => a.value === selectedApi.value)
  return api?.description || '请选择一个新闻API'
})

const selectSource = (value: string) => {
  selectedSource.value = value
  selectedApi.value = ''
  hasCollected.value = false
  form.value.url = ''
}

const getSourceName = (value: string) => {
  const source = sources.find(s => s.value === value)
  return source?.name || ''
}

const getSourceIcon = (value: string) => {
  const source = sources.find(s => s.value === value)
  return source?.icon || '📋'
}

const collectNews = async () => {
  if (selectedSource.value === 'api' && !selectedApi.value) {
    ElMessageBox.alert('请选择新闻API', '提示', {
      confirmButtonText: '确定',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })
    return
  }

  if (selectedSource.value === 'web' && !form.value.url) {
    ElMessageBox.alert('请输入网页URL', '提示', {
      confirmButtonText: '确定',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })
    return
  }

  loading.value = true
  try {
    const data: any = await post('/api/collect-news', {
      source: selectedSource.value,
      api_type: selectedSource.value === 'api' ? selectedApi.value : undefined,
      url: form.value.url
    })

    if (data.success) {
      hasCollected.value = true
      $message({
        message: data.message || '采集成功',
        type: 'success',
      })
    } else {
      $message({
        message: data.message || '采集失败',
        type: 'error',
      })
    }
  } catch (error: any) {
    $message({
      message: error.message || '采集失败，请检查网络连接',
      type: 'error',
    })
    console.error('采集错误:', error)
  } finally {
    loading.value = false
  }
}

const goToNews = () => {
  router.push('/draft-box')
}

const resetLLMChat = () => {
  llmChatRef.value?.resetChat()
}
</script>

<style scoped>
.collector-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: var(--bg-page);
}

.collector-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  margin-bottom: 12px;
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

.source-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.source-option {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-large);
  cursor: pointer;
  transition: all var(--transition-slow);
  background: var(--bg-container);
}

.source-option:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-medium);
  transform: translateY(-2px);
}

.source-option.active {
  border-color: var(--primary-color);
  background: var(--primary-color-light);
}

.source-icon {
  font-size: 32px;
  margin-right: 16px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), #60a5fa);
  border-radius: var(--radius-circle);
  color: white;
  box-shadow: var(--shadow-medium);
}

.source-info {
  flex: 1;
}

.source-name {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
  font-size: 16px;
}

.source-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.web-scraping-form,
.api-form {
  margin-top: 16px;
}

.supported-sites {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.sites-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.sites-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.sites-table th,
.sites-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.sites-table th {
  background: var(--bg-container);
  font-weight: 600;
  color: var(--text-primary);
}

.sites-table td {
  color: var(--text-secondary);
}

.url-cell {
  font-family: monospace;
  font-size: 12px;
  word-break: break-all;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.form-item {
  width: 100%;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.coming-soon {
  padding: 40px 0;
  text-align: center;
}

.llm-chat-section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .collector-content {
    padding: 20px;
  }

  .source-options {
    grid-template-columns: 1fr;
  }

  .source-option {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .source-icon {
    margin-right: 0;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    width: 100%;
  }
}
</style>
