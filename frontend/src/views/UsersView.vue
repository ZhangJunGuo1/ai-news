<template>
  <main class="news-content">
    <section class="news-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="section-icon">{{ pageIcon }}</span>
              用户信息
            </h2>
            <div class="section-actions">
              <button class="action-btn" @click="fetchUsers">
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
          <div v-else class="table-wrapper">
            <table class="user-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>角色</th>
                  <th>状态</th>
                  <th>创建时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span class="role-badge" :class="getRoleClass(user.role)">{{ user.role }}</span>
                  </td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(user.status)">{{ user.status }}</span>
                  </td>
                  <td>{{ user.createTime }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
    </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePageIcon } from '../composables/usePageIcon'

const { pageIcon } = usePageIcon()

const loading = ref(true)
const error = ref('')
const users = ref<any[]>([])



const fetchUsers = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await fetch('/api/users')
    if (!response.ok) {
      throw new Error('获取用户列表失败')
    }
    const data = await response.json()
    users.value = data.users || []
  } catch (err) {
    error.value = '获取用户列表失败，请重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getRoleClass = (role: string) => {
  switch (role) {
    case '管理员':
      return 'role-admin'
    case '编辑':
      return 'role-editor'
    case '测试':
      return 'role-test'
    default:
      return 'role-viewer'
  }
}

const getStatusClass = (status: string) => {
  return status === '正常' ? 'status-active' : 'status-disabled'
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.news-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.news-section {
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

.table-wrapper {
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-container);
  border-radius: var(--radius-large);
  overflow: hidden;
}

.user-table thead {
  background: var(--table-header-bg);
}

.user-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

.user-table td {
  padding: 14px 20px;
  font-size: 14px;
  color: var(--text-regular);
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

.user-table tbody tr {
  transition: all var(--transition-fast);
}

.user-table tbody tr:hover {
  background: var(--table-row-hover-bg);
}

.user-table tbody tr:last-child td {
  border-bottom: none;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-circle);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.role-badge.role-admin {
  background: linear-gradient(135deg, var(--primary-color), #60a5fa);
  color: white;
}

.role-badge.role-editor {
  background: linear-gradient(135deg, var(--success-color), #34d399);
  color: white;
}

.role-badge.role-test {
  background: linear-gradient(135deg, var(--warning-color), #fbbf24);
  color: white;
}

.role-badge.role-viewer {
  background: linear-gradient(135deg, var(--text-secondary), #94a3b8);
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-circle);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.status-active {
  background: var(--success-color-light);
  color: var(--success-color);
  border: 1px solid var(--success-color);
}

.status-badge.status-disabled {
  background: var(--error-color-light);
  color: var(--error-color);
  border: 1px solid var(--error-color);
}

@media (max-width: 768px) {
  .news-content {
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

  .user-table {
    font-size: 12px;
  }

  .user-table th,
  .user-table td {
    padding: 10px 12px;
  }
}
</style>