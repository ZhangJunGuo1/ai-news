<template>
  <main class="category-content">
    <div class="category-section">
      <div class="section-header">
        <h2 class="section-title">
          <span class="section-icon">{{ pageIcon }}</span>
          分类管理
        </h2>
        <div class="section-actions">
          <button class="action-btn" @click="fetchCategories">
            <span class="btn-icon">🔄</span>
            刷新
          </button>
          <button class="action-btn primary" @click="addCategory">
            <span class="btn-icon">➕</span>
            新增分类
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

      <div v-else-if="categories.length === 0" class="empty-state">
        <div class="empty-icon">📑</div>
        <div class="empty-text">暂无分类数据</div>
      </div>

      <div v-else class="category-table">
        <table>
          <thead>
            <tr>
              <th>分类名称</th>
              <th class="icon-header">图标</th>
              <th>主题</th>
              <th>分类代码</th>
              <th>排序</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td>{{ category.name }}</td>
              <td class="icon-cell">{{ getIconEmoji(category.icon) }}</td>
              <td class="desc-cell">{{ category.description || '-' }}</td>
              <td><code>{{ category.code }}</code></td>
              <td>{{ category.sort_order }}</td>
              <td>
                <span class="status-badge" :class="category.status === 'active' ? 'active' : 'inactive'">
                  {{ category.status === 'active' ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(category.create_time) }}</td>
              <td class="actions-cell">
                <button class="btn-edit" @click="editCategory(category)">编辑</button>
                <button class="btn-delete" @click="deleteCategory(category.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      custom-class="custom-dialog"
    >
      <el-form
        :model="categoryForm"
        :rules="rules"
        ref="categoryFormRef"
        label-position="top"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类图标" prop="icon">
          <IconSelector v-model="categoryForm.icon" placeholder="请选择分类图标" />
        </el-form-item>
        <el-form-item label="主题" prop="description">
          <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类主题" />
        </el-form-item>
        <el-form-item label="分类代码" prop="code">
          <el-input v-model="categoryForm.code" placeholder="请输入分类代码（英文，如 domestic）" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="categoryForm.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="categoryForm.status" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="action-btn" @click="dialogVisible = false">取消</button>
          <button class="action-btn primary" @click="submitForm">确定</button>
        </div>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElInputNumber } from 'element-plus'
import { get, post, put } from '../utils/request'
import IconSelector from '../components/IconSelector.vue'
import { getIconByName } from '../config/icons'
import { setMenuCache } from '../utils/navigation'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const categories = ref<any[]>([])
const loading = ref(false)
const error = ref('')

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}

const dialogVisible = ref(false)
const dialogTitle = ref('新增分类')
const currentCategoryId = ref<number | null>(null)

const categoryForm = ref({
  name: '',
  icon: '',
  code: '',
  description: '',
  sort_order: 0,
  status: 'active'
})

const categoryFormRef = ref()

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 之间', trigger: 'blur' }
  ],
  icon: [
    { required: true, message: '请输入分类图标', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入分类代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_]+$/, message: '分类代码只能包含英文字母和下划线', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序', trigger: 'blur' },
    { type: 'number', min: 0, max: 999, message: '排序范围在 0 到 999 之间', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

const fetchCategories = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const data: any = await get('/api/categories')
    
    if (data.success) {
      categories.value = data.categories
    } else {
      throw new Error(data.message || '获取分类列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取分类列表失败'
  } finally {
    loading.value = false
  }
}

const addCategory = () => {
  dialogTitle.value = '新增分类'
  currentCategoryId.value = null
  categoryForm.value = {
    name: '',
    icon: '',
    code: '',
    description: '',
    sort_order: 0,
    status: 'active'
  }
  dialogVisible.value = true
}

const editCategory = (category: any) => {
  dialogTitle.value = '编辑分类'
  currentCategoryId.value = category.id
  categoryForm.value = {
    name: category.name,
    icon: category.icon,
    code: category.code,
    description: category.description,
    sort_order: category.sort_order,
    status: category.status
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!categoryFormRef.value) return
  
  try {
    await categoryFormRef.value.validate()
    
    let data: any
    if (currentCategoryId.value) {
      data = await put(`/api/categories/${currentCategoryId.value}`, categoryForm.value)
    } else {
      data = await post('/api/categories', categoryForm.value)
    }
    
    if (data.success) {
      $message.success(data.message || '操作成功')
      dialogVisible.value = false
      fetchCategories()
      refreshMenuCache()
    } else {
      throw new Error(data.message || '操作失败')
    }
  } catch (err: any) {
    $message.error(err.message || '操作失败')
  }
}

const deleteCategory = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此分类吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/delete-category', { category_id: id })
    
    if (data.success) {
      $message.success('删除成功')
      fetchCategories()
      refreshMenuCache()
    } else {
      throw new Error(data.message || '删除失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      $message.error(err.message || '删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const refreshMenuCache = async () => {
  try {
    const data: any = await get('/api/menus')
    if (data.success && data.menus) {
      const buildMenuTree = (menuList: any[]): any[] => {
        const menuMap: Record<number, any> = {}
        const tree: any[] = []
        menuList.forEach(menu => {
          menuMap[menu.id] = { ...menu, children: [] }
        })
        menuList.forEach(menu => {
          if (menu.parent_id === 0) {
            tree.push(menuMap[menu.id])
          } else if (menuMap[menu.parent_id]) {
            menuMap[menu.parent_id].children?.push(menuMap[menu.id])
          }
        })
        return tree
      }
      setMenuCache(buildMenuTree(data.menus))
    }
  } catch (error) {
    console.error('刷新菜单缓存失败:', error)
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.category-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
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

.category-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-container);
  border-radius: var(--radius-large);
  overflow: hidden;
}

thead {
  background: var(--bg-header);
}

th {
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  border-bottom: 2px solid var(--border-color);
}

td {
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
}

tbody tr:hover {
  background: var(--bg-hover);
}

.icon-header {
  text-align: center;
}

.icon-cell {
  font-size: 20px;
  text-align: center;
}

.desc-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

code {
  background: var(--bg-card);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--primary-color);
}

.status-badge {
  padding: 4px 12px;
  border-radius: var(--radius-circle);
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: var(--success-color);
  color: white;
}

.status-badge.inactive {
  background: var(--text-secondary);
  color: white;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-base);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-edit {
  background: var(--primary-color);
  color: white;
}

.btn-edit:hover {
  background: var(--primary-color-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-medium);
}

.btn-delete {
  background: var(--error-color);
  color: white;
}

.btn-delete:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-medium);
}

@media (max-width: 768px) {
  .category-content {
    padding: 20px;
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

  th, td {
    padding: 12px 8px;
    font-size: 12px;
  }

  .actions-cell {
    flex-direction: column;
    gap: 4px;
  }

  .btn-edit,
  .btn-delete {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>
