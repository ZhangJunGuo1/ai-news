<template>
  <main class="menu-content">
    <div class="menu-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="section-icon">{{ pageIcon }}</span>
              菜单管理
            </h2>
            <div class="section-actions">
              <button class="action-btn" @click="fetchMenus">
                <span class="btn-icon">🔄</span>
                刷新
              </button>
              <button class="action-btn primary" @click="addMenu">
                <span class="btn-icon">➕</span>
                新增菜单
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

          <div v-else-if="menuTree.length === 0" class="empty-state">
            <div class="empty-icon">🗂️</div>
            <div class="empty-text">暂无菜单数据</div>
          </div>

          <div v-else class="menu-tree-wrapper">
            <el-tree
              :key="treeKey"
              :data="menuTree"
              node-key="id"
              :props="defaultProps"
              default-expand-all
            >
              <template #default="{ data }">
                <div class="tree-node-content">
                  <span class="menu-icon">{{ getIconEmoji(data.icon) }}</span>
                  <span class="menu-name">{{ data.name }}</span>
                  <span class="menu-status" :class="data.status === 1 ? 'visible' : 'hidden'">
                    {{ data.status === 1 ? '展示' : '隐藏' }}
                  </span>
                  <div class="menu-actions">
                    <button class="btn-toggle" @click.stop="toggleStatus(data)">
                      {{ data.status === 1 ? '隐藏' : '展示' }}
                    </button>
                    <button class="btn-edit" @click.stop="editMenu(data)">编辑</button>
                    <button class="btn-delete" @click.stop="deleteMenu(data.id)">删除</button>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </div>

    <!-- 新增/编辑菜单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      custom-class="custom-dialog"
    >
      <el-form
        :model="menuForm"
        :rules="rules"
        ref="menuFormRef"
        label-position="top"
      >
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单图标" prop="icon">
          <IconSelector v-model="menuForm.icon" placeholder="请选择菜单图标" />
        </el-form-item>
        <el-form-item label="菜单路径" prop="path">
          <el-input v-model="menuForm.path" placeholder="请输入菜单路径" />
        </el-form-item>
        <el-form-item label="父菜单" prop="parent_id">
          <el-select v-model="menuForm.parent_id" placeholder="请选择父菜单">
            <el-option label="根菜单" :value="0" />
            <el-option
              v-for="menu in menuOptions"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="menuForm.order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="menuForm.status" placeholder="请选择状态">
            <el-option label="展示" :value="1" />
            <el-option label="隐藏" :value="0" />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox, ElTree, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElInputNumber } from 'element-plus'
import { get, post, put } from '../utils/request'
import IconSelector from '../components/IconSelector.vue'
import { getIconByName } from '../config/icons'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const menus = ref<any[]>([])
const menuTree = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const treeKey = ref(0)

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const currentMenuId = ref<number | null>(null)

// 表单相关
const menuForm = ref({
  name: '',
  icon: '',
  path: '',
  parent_id: 0,
  order: 0,
  status: 1
})

const menuFormRef = ref()

const rules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 1, max: 50, message: '菜单名称长度在 1 到 50 之间', trigger: 'blur' }
  ],
  icon: [
    { required: true, message: '请输入菜单图标', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入菜单路径', trigger: 'blur' }
  ],
  parent_id: [
    { required: true, message: '请选择父菜单', trigger: 'change' }
  ],
  order: [
    { required: true, message: '请输入排序', trigger: 'blur' },
    { type: 'number', min: 0, max: 999, message: '排序范围在 0 到 999 之间', trigger: 'blur' }
  ]
}

// 菜单选项（用于父菜单选择）
const menuOptions = computed(() => {
  return menus.value.filter(menu => menu.parent_id === 0)
})

const defaultProps = {
  children: 'children',
  label: 'name'
}

const fetchMenus = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const data: any = await get('/api/menus')
    
    if (data.success) {
      menus.value = data.menus
      menuTree.value = buildMenuTree(data.menus)
    } else {
      throw new Error(data.message || '获取菜单列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取菜单列表失败'
  } finally {
    loading.value = false
  }
}

const buildMenuTree = (menuList: any[]): any[] => {
  const menuMap: Record<number, any> = {}
  const tree: any[] = []
  
  // 构建菜单映射
  menuList.forEach(menu => {
    menuMap[menu.id] = {
      ...menu,
      children: []
    }
  })
  
  // 构建树结构
  menuList.forEach(menu => {
    if (menu.parent_id === 0) {
      // 根节点
      tree.push(menuMap[menu.id])
    } else if (menuMap[menu.parent_id]) {
      // 子节点
      menuMap[menu.parent_id].children.push(menuMap[menu.id])
    }
  })
  
  return tree
}

const addMenu = () => {
  dialogTitle.value = '新增菜单'
  currentMenuId.value = null
  menuForm.value = {
    name: '',
    icon: '',
    path: '',
    parent_id: 0,
    order: 0,
    status: 1
  }
  dialogVisible.value = true
}

const editMenu = (menu: any) => {
  dialogTitle.value = '编辑菜单'
  currentMenuId.value = menu.id
  menuForm.value = {
    name: menu.name,
    icon: menu.icon,
    path: menu.path,
    parent_id: menu.parent_id,
    order: menu.order,
    status: menu.status ?? 1
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!menuFormRef.value) return
  
  try {
    await menuFormRef.value.validate()
    
    let data: any
    if (currentMenuId.value) {
      data = await put(`/api/menus/${currentMenuId.value}`, menuForm.value)
    } else {
      data = await post('/api/menus', menuForm.value)
    }
    
    if (data.success) {
      $message.success(data.message || '操作成功')
      dialogVisible.value = false
      treeKey.value++
      fetchMenus()
      window.dispatchEvent(new Event('menu-changed'))
    } else {
      throw new Error(data.message || '操作失败')
    }
  } catch (err: any) {
    $message.error(err.message || '操作失败')
  }
}

const deleteMenu = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此菜单吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'custom-message-box'
    })

    const data: any = await post('/api/delete-menu', { menu_id: id })
    
    if (data.success) {
      $message.success('删除成功')
      treeKey.value++
      fetchMenus()
    } else {
      throw new Error(data.message || '删除失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      $message.error(err.message || '删除失败')
    }
  }
}

const toggleStatus = async (menu: any) => {
  const newStatus = menu.status === 1 ? 0 : 1
  try {
    const data: any = await put(`/api/menus/${menu.id}`, {
      name: menu.name,
      icon: menu.icon,
      path: menu.path,
      parent_id: menu.parent_id,
      order: menu.order,
      status: newStatus
    })
    
    if (data.success) {
      $message.success(newStatus === 1 ? '已设置为展示' : '已设置为隐藏')
      fetchMenus()
    } else {
      throw new Error(data.message || '操作失败')
    }
  } catch (err: any) {
    $message.error(err.message || '操作失败')
  }
}

onMounted(() => {
  fetchMenus()
})
</script>

<style scoped>
.menu-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.menu-section {
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

.menu-tree-wrapper {
  background: var(--bg-container);
  border-radius: var(--radius-large);
  padding: 16px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

:deep(.el-tree) {
  background: transparent !important;
  color: var(--tree-node-text-color);
}

:deep(.el-tree-node__content) {
  background: transparent !important;
  color: var(--tree-node-text-color);
  border-radius: var(--radius-base);
  height: 40px;
}

:deep(.el-tree-node__content:hover) {
  background: var(--tree-node-hover-bg) !important;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: var(--tree-node-active-bg) !important;
  color: var(--primary-color);
}

:deep(.el-tree__empty-block) {
  background: transparent;
}

:deep(.el-tree__empty-text) {
  color: var(--text-secondary);
}

:deep(.el-tree-node__expand-icon) {
  color: var(--text-secondary);
}

:deep(.el-tree-node__expand-icon:hover) {
  color: var(--primary-color);
}

:deep(.el-tree-node__label) {
  color: var(--tree-node-text-color);
}

.tree-node-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px;
}

.tree-node-content .menu-icon {
  margin-right: 12px;
  font-size: 16px;
  width: 24px;
  text-align: center;
  color: var(--text-primary);
}

.tree-node-content .menu-name {
  flex: 1;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.tree-node-content .menu-status {
  padding: 2px 10px;
  border-radius: var(--radius-circle);
  font-size: 12px;
  font-weight: 600;
  margin-left: 12px;
}

.tree-node-content .menu-status.visible {
  background: var(--success-color);
  color: white;
}

.tree-node-content .menu-status.hidden {
  background: var(--text-secondary);
  color: white;
}

.tree-node-content .menu-actions {
  display: flex;
  gap: 8px;
  margin-left: 16px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.tree-node-content:hover .menu-actions {
  opacity: 1;
}

.btn-edit,
.btn-delete,
.btn-toggle {
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-base);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-toggle {
  background: var(--warning-color);
  color: white;
}

.btn-toggle:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-medium);
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
  .menu-content {
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

  .menu-tree-wrapper {
    padding: 12px;
  }

  .tree-node-content {
    padding: 8px 4px;
  }

  .tree-node-content .menu-actions {
    opacity: 1;
    margin-left: 8px;
  }

  .btn-edit,
  .btn-delete {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>