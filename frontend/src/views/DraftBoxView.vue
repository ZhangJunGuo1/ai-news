<template>
  <main class="draft-content">
    <div class="draft-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="section-icon">{{ pageIcon }}</span>
              待发布新闻
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

          <div v-else-if="drafts.length === 0" class="empty-state">
            <div class="empty-icon">📭</div>
            <div class="empty-text">暂无草稿</div>
          </div>

          <div v-else class="table-wrapper">
            <div class="batch-actions" v-if="selectedIds.length > 0">
              <span class="selected-count">已选择 {{ selectedIds.length }} 项</span>
              <button class="action-btn primary" @click="batchPublish">
                <span class="btn-icon">📤</span>
                批量发布
              </button>
              <button class="action-btn danger" @click="batchDelete">
                <span class="btn-icon">🗑️</span>
                批量删除
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
                  <th class="col">采集时间</th>
                  <th class="col">状态</th>
                  <th class="col">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(draft, index) in drafts" :key="draft.id">
                  <td class="col">
                    <input type="checkbox" :checked="selectedIds.includes(draft.id)" @change="toggleSelect(draft.id)" />
                  </td>
                  <td class="col">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td class="col" :title="draft.title">{{ draft.title }}</td>
                  <td class="col">{{ draft.category }}</td>
                  <td class="col source-cell" :title="draft.source">{{ draft.source }}</td>
                  <td class="col">{{ formatDate(draft.create_time) }}</td>
                  <td class="col">
                    <span class="status-badge draft">{{ draft.status }}</span>
                  </td>
                  <td class="col">
                    <button class="btn-action primary" @click="editDraft(draft)">编辑</button>
                    <button class="btn-action success" @click="publishDraft(draft.id)">发布</button>
                    <button class="btn-action danger" @click="deleteDraft(draft.id)">删除</button>
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

  <el-dialog
    v-model="editDialogVisible"
    title="编辑草稿"
    width="700px"
    :close-on-click-modal="false"
  >
    <div class="edit-form">
      <div class="form-item">
        <label class="form-label">分类</label>
        <el-input v-model="editForm.category" disabled />
      </div>
      <div class="form-item">
        <label class="form-label">来源</label>
        <el-input v-model="editForm.source" disabled />
      </div>
      <div class="form-item">
        <label class="form-label">状态</label>
        <el-input v-model="editForm.status" disabled />
      </div>
      <div class="form-item">
        <label class="form-label">标题</label>
        <el-input v-model="editForm.title" placeholder="请输入标题" />
      </div>
      <div class="form-item">
        <label class="form-label">内容</label>
        <el-input
          v-model="editForm.content"
          type="textarea"
          :rows="10"
          placeholder="请输入内容"
        />
      </div>
    </div>
    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { get, post } from '../utils/request'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const drafts = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const editDialogVisible = ref(false)
const saving = ref(false)
const selectedIds = ref<number[]>([])
const categories = ref<any[]>([])
const keyword = ref('')
const category = ref('')
const source = ref('')
const editForm = ref({
  id: 0,
  title: '',
  content: '',
  category: '',
  source: '',
  status: ''
})

const isAllSelected = computed(() => {
  return drafts.value.length > 0 && selectedIds.value.length === drafts.value.length
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

const fetchDrafts = async () => {
  loading.value = true
  error.value = ''
  
  try {
    let url = `/api/drafts?page=${currentPage.value}&page_size=${pageSize.value}`
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
      drafts.value = data.drafts
      total.value = data.total
    } else {
      throw new Error(data.message || '获取草稿列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取草稿列表失败'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchDrafts()
}

const handleReset = () => {
  keyword.value = ''
  category.value = ''
  source.value = ''
  currentPage.value = 1
  fetchDrafts()
}

const publishDraft = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要发布这条新闻吗？', '发布确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/publish-news', { news_id: id })
    
    if (data.success) {
      ElMessageBox.alert('发布成功', '提示', {
        confirmButtonText: '确定',
        type: 'success',
        center: true,
        customClass: 'custom-message-box',
        callback: () => {
          fetchDrafts()
        }
      })
    } else {
      throw new Error(data.message || '发布失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '发布失败', '提示', {
        confirmButtonText: '确定',
        type: 'error',
        center: true,
        customClass: 'custom-message-box'
      })
    }
  }
}

const deleteDraft = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条草稿吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/delete-draft', { news_id: id })
    
    if (data.success) {
      $message({
        message: '删除成功',
        type: 'success',
      })
      fetchDrafts()
    } else {
      throw new Error(data.message || '删除失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '删除失败', '提示', {
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

const editDraft = (draft: any) => {
  editForm.value = {
    id: draft.id,
    title: draft.title,
    content: draft.content,
    category: draft.category,
    source: draft.source,
    status: draft.status
  }
  editDialogVisible.value = true
}

const saveEdit = async () => {
  if (!editForm.value.title) {
    $message.warning('请输入标题')
    return
  }
  
  saving.value = true
  try {
    const data: any = await post('/api/update-draft', {
      news_id: editForm.value.id,
      title: editForm.value.title,
      content: editForm.value.content
    })
    
    if (data.success) {
      $message.success('保存成功')
      editDialogVisible.value = false
      fetchDrafts()
    } else {
      throw new Error(data.message || '保存失败')
    }
  } catch (err: any) {
    $message.error(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    selectedIds.value = []
    fetchDrafts()
  }
}

const changePageSize = () => {
  currentPage.value = 1
  selectedIds.value = []
  fetchDrafts()
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
    selectedIds.value = drafts.value.map(d => d.id)
  }
}

const batchPublish = async () => {
  try {
    await ElMessageBox.confirm(`确定要发布选中的 ${selectedIds.value.length} 条新闻吗？`, '批量发布确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/batch-publish-drafts', { news_ids: selectedIds.value })
    
    if (data.success) {
      ElMessageBox.alert(data.message || '批量发布成功', '提示', {
        confirmButtonText: '确定',
        type: 'success',
        center: true,
        customClass: 'custom-message-box',
        callback: () => {
          selectedIds.value = []
          fetchDrafts()
        }
      })
    } else {
      throw new Error(data.message || '批量发布失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '批量发布失败', '提示', {
        confirmButtonText: '确定',
        type: 'error',
        center: true,
        customClass: 'custom-message-box'
      })
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条草稿吗？此操作不可恢复。`, '批量删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/batch-delete-drafts', { news_ids: selectedIds.value })
    
    if (data.success) {
      $message({
        message: data.message || '批量删除成功',
        type: 'success',
      })
      selectedIds.value = []
      fetchDrafts()
    } else {
      throw new Error(data.message || '批量删除失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      ElMessageBox.alert(err.message || '批量删除失败', '提示', {
        confirmButtonText: '确定',
        type: 'error',
        center: true,
        customClass: 'custom-message-box'
      })
    }
  }
}

onMounted(() => {
  fetchCategories()
  fetchDrafts()
})
</script>

<style scoped>
.draft-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: var(--bg-page);
}

.draft-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-form .form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-form .form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
