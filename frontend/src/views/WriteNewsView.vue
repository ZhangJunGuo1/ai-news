<template>
  <main class="write-news-content">
    <div class="write-section">
      <div class="section-header">
        <h2 class="section-title">
          <span class="section-icon">{{ pageIcon }}</span>
          撰写新闻
        </h2>
      </div>

      <el-form
        :model="newsForm"
        :rules="rules"
        ref="newsFormRef"
        label-position="top"
        class="news-form"
      >
        <el-form-item label="新闻标题" prop="title">
          <el-input v-model="newsForm.title" placeholder="请输入新闻标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="新闻分类" prop="category">
          <el-select v-model="newsForm.category" placeholder="请选择新闻分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.code"
              :label="cat.name"
              :value="cat.code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="新闻内容" prop="content">
          <el-input
            v-model="newsForm.content"
            type="textarea"
            :rows="15"
            placeholder="请输入新闻内容"
            resize="vertical"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <button class="action-btn" @click="saveAsDraft" :disabled="submitting">
              <span class="btn-icon">📁</span>
              保存草稿
            </button>
            <button class="action-btn primary" @click="publishNews" :disabled="submitting">
              <span class="btn-icon">📤</span>
              直接发布
            </button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption } from 'element-plus'
import { get, post } from '../utils/request'
import { usePageIcon } from '../composables/usePageIcon'
import { useMessage } from '../composables/useMessage'

const { pageIcon } = usePageIcon()
const $message = useMessage()

const categories = ref<any[]>([])
const submitting = ref(false)

const newsForm = ref({
  title: '',
  category: '',
  content: ''
})

const newsFormRef = ref()

const rules = {
  title: [
    { required: true, message: '请输入新闻标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 之间', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择新闻分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入新闻内容', trigger: 'blur' }
  ]
}

const fetchCategories = async () => {
  try {
    const data: any = await get('/api/categories')
    if (data.success) {
      categories.value = data.categories.filter((c: any) => c.status === 'active')
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

const saveAsDraft = async () => {
  if (!newsFormRef.value) return

  try {
    await newsFormRef.value.validate()
    submitting.value = true

    const data: any = await post('/api/save-news', {
      title: newsForm.value.title,
      category: newsForm.value.category,
      content: newsForm.value.content,
      status: 0
    })

    if (data.success) {
      $message.success('草稿保存成功')
      resetForm()
    } else {
      throw new Error(data.message || '保存失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      $message.error(err.message || '保存失败')
    }
  } finally {
    submitting.value = false
  }
}

const publishNews = async () => {
  if (!newsFormRef.value) return

  try {
    await newsFormRef.value.validate()
    submitting.value = true

    const data: any = await post('/api/save-news', {
      title: newsForm.value.title,
      category: newsForm.value.category,
      content: newsForm.value.content,
      status: 1
    })

    if (data.success) {
      $message.success('新闻发布成功')
      resetForm()
    } else {
      throw new Error(data.message || '发布失败')
    }
  } catch (err: any) {
    if (err.message !== 'cancel') {
      $message.error(err.message || '发布失败')
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  newsForm.value = {
    title: '',
    category: '',
    content: ''
  }
  newsFormRef.value?.resetFields()
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.write-news-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.write-section {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  border: 1px solid var(--border-color);
  max-width: 900px;
}

.section-header {
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

.news-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.action-btn {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-base);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn:hover {
  background: var(--bg-hover);
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-medium);
}

.action-btn.primary {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.primary:hover {
  background: var(--primary-color-dark);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .write-news-content {
    padding: 20px;
  }

  .write-section {
    padding: 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
