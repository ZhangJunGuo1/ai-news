<template>
  <main class="published-content">
    <div class="published-section">
      <div class="section-header">
        <h2 class="section-title">
          <span class="section-icon">{{ pageIcon }}</span>
          已发布新闻
        </h2>
      </div>

      <div class="filter-bar">
        <div class="filter-item">
          <input 
            v-model="keyword" 
            type="text" 
            placeholder="搜索标题..." 
            class="filter-input"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="filter-item">
          <select v-model="category" class="filter-select" @change="handleSearch">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat.code" :value="cat.code">{{ cat.name }}</option>
          </select>
        </div>
        <div class="filter-item">
          <select v-model="source" class="filter-select" style="width: 180px;" @change="handleSearch">
            <option value="">全部来源</option>
            <option value="60秒新闻">60秒新闻</option>
            <option value="CCTV新闻">CCTV新闻</option>
            <option value="新浪新闻">新浪新闻</option>
            <option value="百度热搜">百度热搜</option>
            <option value="系统">系统</option>
          </select>
        </div>
        <div class="filter-item">
          <button class="action-btn primary" @click="handleSearch">
            <span class="btn-icon">🔍</span>
            查询
          </button>
          <button class="action-btn" @click="handleReset">
            <span class="btn-icon">↩️</span>
            重置
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
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无已发布新闻</div>
      </div>

      <div v-else class="table-wrapper">
        <div class="batch-actions" v-if="selectedIds.length > 0">
          <span class="selected-count">已选择 {{ selectedIds.length }} 项</span>
          <button class="action-btn warning" @click="batchUnpublish">
            <span class="btn-icon">↩️</span>
            批量撤销发布
          </button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th class="col">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
              </th>
              <th class="col">序号</th>
              <th class="col">标题</th>
              <th class="col">分类</th>
              <th class="col">来源</th>
              <th class="col">发布时间</th>
              <th class="col">状态</th>
              <th class="col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(news, index) in newsList" :key="news.id">
              <td class="col">
                <input type="checkbox" :checked="selectedIds.includes(news.id)" @change="toggleSelect(news.id)" />
              </td>
              <td class="col">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="col" :title="news.title">{{ news.title }}</td>
              <td class="col">{{ news.category }}</td>
              <td class="col source-cell" :title="news.source">{{ news.source }}</td>
              <td class="col">{{ formatDate(news.create_time) }}</td>
              <td class="col">
                <span class="status-badge published">{{ news.status }}</span>
              </td>
              <td class="col">
                <button class="btn-action warning" @click="unpublishNews(news.id)">撤销发布</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="total > 0" class="pagination-wrapper">
        <div class="pagination-info">
          共 {{ total }} 条记录，第 {{ currentPage }}/{{ totalPages }} 页
        </div>
        <div class="pagination-controls">
          <div class="page-size-selector">
            <span class="page-size-label">每页显示：</span>
            <select v-model="pageSize" @change="changePageSize" class="page-size-select">
              <option :value="10">10 条</option>
              <option :value="20">20 条</option>
              <option :value="50">50 条</option>
              <option :value="100">100 条</option>
            </select>
          </div>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="changePage(1)"
          >
            首页
          </button>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="pagination-btn"
            :class="{ active: page === currentPage }"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="changePage(totalPages)"
          >
            末页
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { get, post } from '../utils/request'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const newsList = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedIds = ref<number[]>([])
const categories = ref<any[]>([])
const keyword = ref('')
const category = ref('')
const source = ref('')

const isAllSelected = computed(() => {
  return newsList.value.length > 0 && selectedIds.value.length === newsList.value.length
})

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const fetchCategories = async () => {
  try {
    const data: any = await get('/api/categories')
    if (data.success) {
      categories.value = data.categories
    }
  } catch (err: any) {
    console.error('获取分类列表失败:', err)
  }
}

const fetchPublished = async () => {
  loading.value = true
  error.value = ''
  
  try {
    let url = `/api/published-news?page=${currentPage.value}&page_size=${pageSize.value}`
    if (keyword.value) {
      url += `&keyword=${encodeURIComponent(keyword.value)}`
    }
    if (category.value) {
      url += `&category=${encodeURIComponent(category.value)}`
    }
    if (source.value) {
      url += `&source=${encodeURIComponent(source.value)}`
    }
    
    const data: any = await get(url)
    
    if (data.success) {
      newsList.value = data.news
      total.value = data.total
    } else {
      throw new Error(data.message || '获取已发布新闻失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取已发布新闻失败'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPublished()
}

const handleReset = () => {
  keyword.value = ''
  category.value = ''
  source.value = ''
  currentPage.value = 1
  fetchPublished()
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    selectedIds.value = []
    fetchPublished()
  }
}

const changePageSize = () => {
  currentPage.value = 1
  selectedIds.value = []
  fetchPublished()
}

const toggleSelect = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = newsList.value.map(n => n.id)
  }
}

const unpublishNews = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要撤销发布这条新闻吗？撤销后将回到草稿状态。', '撤销发布确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/unpublish-news', { news_id: id })
    
    if (data.success) {
      $message({
        message: '撤销发布成功',
        type: 'success',
      })
      fetchPublished()
    } else {
      throw new Error(data.message || '撤销发布失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '撤销发布失败', '提示', {
        confirmButtonText: '确定',
        type: 'error',
        center: true,
        customClass: 'custom-message-box'
      })
    }
  }
}

const batchUnpublish = async () => {
  try {
    await ElMessageBox.confirm(`确定要撤销发布选中的 ${selectedIds.value.length} 条新闻吗？撤销后将回到草稿状态。`, '批量撤销发布确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/batch-unpublish-news', { news_ids: selectedIds.value })
    
    if (data.success) {
      $message({
        message: data.message || '批量撤销发布成功',
        type: 'success',
      })
      selectedIds.value = []
      fetchPublished()
    } else {
      throw new Error(data.message || '批量撤销发布失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '批量撤销发布失败', '提示', {
        confirmButtonText: '确定',
        type: 'error',
        center: true,
        customClass: 'custom-message-box'
      })
    }
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchCategories()
  fetchPublished()
})
</script>

<style scoped>
.published-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: var(--bg-page);
}

.published-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}
</style>
