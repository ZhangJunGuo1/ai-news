<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="logo" :class="{ collapsed: isCollapsed }">
      <span v-if="!isCollapsed" class="logo-icon">{{ getAppIconEmoji() }}</span>
      <span v-if="!isCollapsed" class="logo-text">{{ appName }}</span>
    </div>
    
    <button class="toggle-btn" @click="toggleCollapse">
      <span :class="{ rotated: isCollapsed }">☰</span>
    </button>
    
    <nav v-if="!isCollapsed && menuList.length > 0" class="menu">
      <div v-for="(item, index) in menuList" :key="index" class="menu-item">
        <div
          v-if="item.children && item.children.length > 0"
          class="menu-item-header"
          :class="{ active: activeMenu === item.name }"
          @click="toggleMenu(item)"
        >
          <span class="menu-icon">{{ getIconEmoji(item.icon) }}</span>
          <span class="menu-name">{{ item.name }}</span>
          <span class="arrow" :class="{ expanded: expandedMenus.includes(item.name) }">▶</span>
        </div>
        <div
          v-else
          class="menu-item-header"
          :class="{ active: activeMenu === item.name }"
          @click="handleMenuClick(item)"
        >
          <span class="menu-icon">{{ getIconEmoji(item.icon) }}</span>
          <span class="menu-name">{{ item.name }}</span>
        </div>

        <div v-if="item.children && item.children.length > 0" class="submenu" :class="{ expanded: expandedMenus.includes(item.name) }">
          <div v-for="(child, childIndex) in item.children" :key="childIndex" class="submenu-item">
            <div
              v-if="child.children && child.children.length > 0"
              class="submenu-item-header"
              :class="{ active: activeMenu === child.name }"
              @click="toggleSubMenu(child)"
            >
              <span class="menu-name">{{ child.name }}</span>
              <span class="arrow" :class="{ expanded: expandedSubMenus.includes(child.name) }">▶</span>
            </div>
            <div
              v-else
              class="submenu-item-header"
              :class="{ active: activeMenu === child.name }"
              @click="handleMenuClick(child)"
            >
              <span class="menu-name">{{ child.name }}</span>
            </div>

            <div v-if="child.children && child.children.length > 0" class="sub-submenu" :class="{ expanded: expandedSubMenus.includes(child.name) }">
              <div
                v-for="(grandChild, grandChildIndex) in child.children"
                :key="grandChildIndex"
                class="sub-submenu-item"
                :class="{ active: activeMenu === grandChild.name }"
                @click="handleMenuClick(grandChild)"
              >
                <span class="menu-name">{{ grandChild.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { navigateTo, setMenuCache } from '../utils/navigation'
import { get } from '../utils/request'
import { getIconByName } from '../config/icons'

interface MenuItem {
  id: number
  name: string
  icon: string
  path?: string
  parent_id: number
  order: number
  children?: MenuItem[]
  status: number
}

const appName = ref('AI-新闻系统')
const appIcon = ref('news')

const loadConfig = () => {
  const savedName = localStorage.getItem('app_name')
  const savedIcon = localStorage.getItem('app_icon')
  if (savedName) appName.value = savedName
  if (savedIcon) appIcon.value = savedIcon
}

const getAppIconEmoji = (): string => {
  return getIconByName(appIcon.value)
}

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}

const menuList = ref<MenuItem[]>([])
const activeMenu = ref('新闻汇总')
const expandedMenus = ref<string[]>(['新闻管理'])
const expandedSubMenus = ref<string[]>(['新闻分类'])
const isCollapsed = ref(false)
const loading = ref(true)

const buildMenuTree = (menuList: MenuItem[]): MenuItem[] => {
  const menuMap: Record<number, MenuItem> = {}
  const tree: MenuItem[] = []
  
  menuList.forEach(menu => {
    menuMap[menu.id] = { ...menu, children: [] }
  })
  
  menuList.forEach(menu => {
    if (menu.status === 0) return
    if (menu.parent_id === 0) {
      tree.push(menuMap[menu.id])
    } else if (menuMap[menu.parent_id]) {
      menuMap[menu.parent_id].children?.push(menuMap[menu.id])
    }
  })
  
  return tree
}

const fetchMenus = async () => {
  try {
    loading.value = true
    const data: any = await get('/api/menus')
    
    if (data.success && data.menus) {
      menuList.value = buildMenuTree(data.menus)
      setMenuCache(menuList.value)
      window.dispatchEvent(new Event('menus-refreshed'))
    }
  } catch (error) {
    console.error('获取菜单失败:', error)
  } finally {
    loading.value = false
  }
}

const setActiveMenuFromPath = () => {
  const currentHash = window.location.hash
  
  const findMenuByPath = (menus: MenuItem[], path: string): MenuItem | null => {
    for (const menu of menus) {
      if (menu.path) {
        const cleanPath = path.replace('#', '')
        if (cleanPath === menu.path) {
          return menu
        }
      }
      if (menu.children && menu.children.length > 0) {
        const found = findMenuByPath(menu.children, path)
        if (found) return found
      }
    }
    return null
  }
  
  const matchedMenu = findMenuByPath(menuList.value, currentHash)
  
  if (matchedMenu) {
    saveMenuState()
    activeMenu.value = matchedMenu.name
    
    const findParentMenus = (menus: MenuItem[], targetId: number, parentNames: string[] = []): string[] | null => {
      for (const menu of menus) {
        if (menu.id === targetId) {
          return parentNames
        }
        if (menu.children && menu.children.length > 0) {
          const result = findParentMenus(menu.children, targetId, [...parentNames, menu.name])
          if (result) return result
        }
      }
      return null
    }
    
    const parentNames = findParentMenus(menuList.value, matchedMenu.id)
    if (parentNames && parentNames.length > 0) {
      expandedMenus.value = [parentNames[0]]
      if (parentNames.length > 1) {
        expandedSubMenus.value = [parentNames[1]]
      } else {
        expandedSubMenus.value = []
      }
    } else {
      expandedMenus.value = []
      expandedSubMenus.value = []
    }
  } else {
    if (currentHash.includes('/404')) {
      restoreMenuState()
    } else {
      const defaultMenu = menuList.value.find(m => m.parent_id === 0)
      if (defaultMenu) {
        activeMenu.value = defaultMenu.name
        expandedMenus.value = [defaultMenu.name]
      }
      expandedSubMenus.value = []
    }
  }
}

let previousActiveMenu = ''
let previousExpandedMenus: string[] = []
let previousExpandedSubMenus: string[] = []

const saveMenuState = () => {
  previousActiveMenu = activeMenu.value
  previousExpandedMenus = [...expandedMenus.value]
  previousExpandedSubMenus = [...expandedSubMenus.value]
  localStorage.setItem('sidebarActiveMenu', activeMenu.value)
  localStorage.setItem('sidebarExpandedMenus', JSON.stringify(expandedMenus.value))
  localStorage.setItem('sidebarExpandedSubMenus', JSON.stringify(expandedSubMenus.value))
}

const restoreMenuState = () => {
  const savedActive = localStorage.getItem('sidebarActiveMenu')
  const savedExpanded = localStorage.getItem('sidebarExpandedMenus')
  const savedSubExpanded = localStorage.getItem('sidebarExpandedSubMenus')
  
  if (savedActive) {
    activeMenu.value = savedActive
    expandedMenus.value = savedExpanded ? JSON.parse(savedExpanded) : []
    expandedSubMenus.value = savedSubExpanded ? JSON.parse(savedSubExpanded) : []
  }
}

const route = useRoute()

onMounted(async () => {
  loadConfig()
  window.addEventListener('config-changed', loadConfig)
  window.addEventListener('menu-changed', fetchMenus)
  await fetchMenus()
  const currentHash = window.location.hash
  if (currentHash.includes('/404')) {
    restoreMenuState()
  } else {
    setActiveMenuFromPath()
  }
})

watch(() => route.path, () => {
  setActiveMenuFromPath()
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  if (isCollapsed.value) {
    expandedMenus.value = []
    expandedSubMenus.value = []
  }
}

const toggleMenu = (item: MenuItem) => {
  const index = expandedMenus.value.indexOf(item.name)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(item.name)
  }
}

const toggleSubMenu = (item: MenuItem) => {
  const index = expandedSubMenus.value.indexOf(item.name)
  if (index > -1) {
    expandedSubMenus.value.splice(index, 1)
  } else {
    expandedSubMenus.value.push(item.name)
  }
}

const handleMenuClick = async (item: MenuItem) => {
  saveMenuState()
  activeMenu.value = item.name
  await navigateTo(item.name)
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100vh;
  background: var(--bg-sidebar);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: all var(--transition-slow);
  box-shadow: var(--shadow-box);
  position: relative;
  z-index: 100;
  border-right: 1px solid var(--border-color);
}

.sidebar.collapsed {
  width: 80px;
}

.logo {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border-color);
  transition: all var(--transition-slow);
  background: var(--bg-sidebar);
  box-shadow: var(--shadow-box);
  height: 72px;
  box-sizing: border-box;
}

.logo.collapsed {
  justify-content: center;
  padding: 16px 0;
  height: 72px;
  box-sizing: border-box;
}

.logo-icon {
  font-size: 28px;
  transition: all var(--transition-slow);
}

.logo-text {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.toggle-btn {
  position: absolute;
  top: 24px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-circle);
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-medium);
  transition: all var(--transition-slow);
  z-index: 101;
}

.sidebar.collapsed .toggle-btn {
  right: 24px;
}

.toggle-btn:hover {
  background: var(--primary-color-dark);
  transform: scale(1.1);
}

.toggle-btn span {
  font-size: 16px;
  transition: all var(--transition-slow);
}

.toggle-btn span.rotated {
  transform: rotate(180deg);
}

.menu {
  flex: 1;
  padding: 20px 0;
  background: var(--bg-page);
}

.menu-item {
  margin-bottom: 4px;
}

.menu-item-header {
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all var(--transition-slow);
  border-radius: var(--radius-large);
  margin: 0 12px;
  position: relative;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-box);
}

.menu-item-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  transition: left var(--transition-slow);
}

.menu-item-header:hover::before {
  left: 100%;
}

.menu-item-header:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
}

.menu-item-header.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
}

.menu-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
  transition: all var(--transition-slow);
}

.menu-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-slow);
}

.arrow {
  font-size: 12px;
  transition: all var(--transition-slow);
  opacity: 0.7;
}

.arrow.expanded {
  transform: rotate(90deg);
  opacity: 1;
}

.submenu {
  max-height: 0;
  overflow: hidden;
  transition: max-height var(--transition-slow);
  background: var(--bg-page);
  margin: 0 12px;
  border-radius: var(--radius-large);
}

.submenu.expanded {
  max-height: 800px;
}

.submenu-item {
  margin-bottom: 2px;
}

.submenu-item-header {
  padding: 12px 20px 12px 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all var(--transition-slow);
  border-radius: var(--radius-large);
  position: relative;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-box);
  margin: 4px 0;
}

.submenu-item-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  transition: left var(--transition-slow);
}

.submenu-item-header:hover::before {
  left: 100%;
}

.submenu-item-header:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
}

.submenu-item-header.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
}

.sub-submenu {
  max-height: 0;
  overflow: hidden;
  transition: max-height var(--transition-slow);
  background: var(--bg-page);
  margin: 0 12px;
  border-radius: var(--radius-large);
}

.sub-submenu.expanded {
  max-height: 400px;
}

.sub-submenu-item {
  padding: 10px 20px 10px 72px;
  cursor: pointer;
  transition: all var(--transition-slow);
  border-radius: var(--radius-large);
  font-size: 13px;
  position: relative;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-box);
  margin: 2px 0;
}

.sub-submenu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  transition: left var(--transition-slow);
}

.sub-submenu-item:hover::before {
  left: 100%;
}

.sub-submenu-item:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
}

.sub-submenu-item.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-medium);
  border-color: var(--primary-color);
  border-left: 3px solid #ffffff;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .toggle-btn {
    right: 12px;
  }
}
</style>