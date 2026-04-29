<template>
  <div class="news-layout">
    <SidebarMenu />
    <div class="main-content">
      <HeaderNav :title="pageTitle" />
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import SidebarMenu from '../components/SidebarMenu.vue'
import HeaderNav from '../components/HeaderNav.vue'
import { getMenuCache, findMenuByPath } from '../utils/navigation'

const route = useRoute()
const pageTitle = ref('新闻系统')

const updatePageTitle = () => {
  const menus = getMenuCache()
  if (!menus || menus.length === 0) {
    pageTitle.value = '新闻系统'
    return
  }

  const currentHash = window.location.hash
  const matchedMenu = findMenuByPath(menus, currentHash)
  
  if (matchedMenu) {
    pageTitle.value = matchedMenu.name
  } else {
    pageTitle.value = '新闻系统'
  }
}

onMounted(() => {
  updatePageTitle()
})

watch(() => route.path, () => {
  updatePageTitle()
})
</script>

<style scoped>
.news-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
