import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getMenuCache, findMenuByPath } from '../utils/navigation'
import { getIconByName } from '../config/icons'

export function usePageIcon() {
  const route = useRoute()
  const pageIcon = ref('📄')

  const loadPageIcon = () => {
    const menus = getMenuCache()
    if (menus) {
      const menu = findMenuByPath(menus, route.path)
      if (menu && menu.icon) {
        pageIcon.value = getIconByName(menu.icon)
      }
    }
  }

  onMounted(() => {
    loadPageIcon()
    window.addEventListener('menu-changed', loadPageIcon)
    window.addEventListener('menus-refreshed', loadPageIcon)
  })

  onUnmounted(() => {
    window.removeEventListener('menu-changed', loadPageIcon)
    window.removeEventListener('menus-refreshed', loadPageIcon)
  })

  return { pageIcon }
}
