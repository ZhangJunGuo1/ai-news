<template>
  <main class="news-content">
    <div v-if="currentNewsType === 'all'" class="dashboard-overview">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">{{ getIconEmoji('news') }}</div>
          <div class="stat-info">
            <div class="stat-number">{{ totalNews }}</div>
            <div class="stat-label">新闻总数</div>
          </div>
        </div>
        <div v-for="category in categoryNewsList" :key="category.code" class="stat-card" @click="scrollToCategory(category.code)">
          <div class="stat-icon">{{ getIconEmoji(category.icon || 'news') }}</div>
          <div class="stat-info">
            <div class="stat-number">{{ category.news.length }}</div>
            <div class="stat-label">{{ category.name }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="currentNewsType === 'all'">
      <NewsList
        v-for="category in categoryNewsList"
        :key="category.code"
        :id="`category-${category.code}`"
        :title="category.description || category.name"
        :category-icon="category.icon || 'news'"
        :badge-text="category.name"
        :news-list="category.news"
        :loading="loading"
        :error="error"
        @refresh="fetchNews()"
      />
    </div>

    <div v-else>
      <NewsList
        :title="currentCategoryTitle"
        :category-icon="currentCategoryIcon"
        :badge-text="currentCategoryBadge"
        :news-list="filteredNews"
        :loading="loading"
        :error="error"
        @refresh="fetchNews(currentNewsType)"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import NewsList from '../components/NewsList.vue'
import { getIconByName } from '../config/icons'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const categoryNewsList = ref<any[]>([])
const currentNewsType = ref<string>('all')

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}

const totalNews = computed(() => {
  return categoryNewsList.value.reduce((sum, cat) => sum + cat.news.length, 0)
})

const filteredNews = computed(() => {
  return categoryNewsList.value.length > 0 ? categoryNewsList.value[0].news : []
})

const currentCategoryTitle = computed(() => {
  const cat = categoryNewsList.value[0]
  console.log('currentCategoryTitle - category:', cat)
  if (!cat) return ''
  return cat.description || cat.name || ''
})

const currentCategoryIcon = computed(() => {
  const cat = categoryNewsList.value[0]
  console.log('currentCategoryIcon - icon:', cat?.icon)
  return cat?.icon || 'news'
})

const currentCategoryBadge = computed(() => {
  const cat = categoryNewsList.value[0]
  return cat?.name || ''
})

const fetchNews = async (type?: string) => {
  try {
    loading.value = true
    error.value = ''

    let url = '/api/news'
    if (type) {
      url += `?type=${type}`
    }

    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('获取新闻失败')
    }
    const data = await response.json()
    console.log('API response data:', data)

    if (type) {
      if (data.category) {
        console.log('Setting category data:', data.category)
        categoryNewsList.value = [{
          code: data.category.code,
          name: data.category.name,
          icon: data.category.icon,
          description: data.category.description,
          news: data.news || []
        }]
      } else {
        console.log('No category data, using default')
        categoryNewsList.value = [{ code: type, name: type, icon: 'news', description: '', news: data.news || [] }]
      }
    } else {
      categoryNewsList.value = data.categories || []
    }
  } catch (err) {
    error.value = '获取新闻失败，请重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const scrollToCategory = (code: string) => {
  const element = document.getElementById(`category-${code}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const updateNewsType = () => {
  const type = route.query.type as string
  if (type) {
    currentNewsType.value = type
    fetchNews(type)
  } else {
    currentNewsType.value = 'all'
    fetchNews()
  }
}

onMounted(() => {
  updateNewsType()
})

watch(() => route.query.type, () => {
  updateNewsType()
})
</script>

<style scoped>
.news-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: var(--bg-page);
}

.dashboard-overview {
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.stat-card {
  background: var(--bg-card);
  padding: 24px;
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-medium);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all var(--transition-slow);
  border: 1px solid var(--border-color);
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-large);
  border-color: var(--primary-color);
}

.stat-icon {
  font-size: 32px;
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

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

@media (max-width: 768px) {
  .news-content {
    padding: 20px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
