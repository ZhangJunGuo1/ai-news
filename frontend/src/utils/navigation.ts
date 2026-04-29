import { get } from './request'
import router from '../router'

const findMenuItem = (name: string, menus: any[]): any => {
  for (const menu of menus) {
    if (menu.name === name) {
      return menu
    }
    if (menu.children && menu.children.length > 0) {
      const found = findMenuItem(name, menu.children)
      if (found) {
        return found
      }
    }
  }
  return null
}

let cachedMenuTree: any[] | null = null

export const setMenuCache = (menus: any[]) => {
  cachedMenuTree = menus
}

export const getMenuCache = (): any[] | null => {
  return cachedMenuTree
}

export const findMenuByPath = (menus: any[], path: string): any => {
  for (const menu of menus) {
    if (menu.path) {
      const cleanPath = path.replace('#', '')
      const menuPath = menu.path.split('?')[0]
      if (cleanPath === menuPath || cleanPath.startsWith(menuPath + '?')) {
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

export const navigateTo = async (pageName: string) => {
  const menuTree = cachedMenuTree
  
  if (!menuTree) {
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
        
        cachedMenuTree = buildMenuTree(data.menus)
      }
    } catch (error) {
      console.error('获取菜单数据失败:', error)
      router.push('/404')
      return
    }
  }
  
  const menuItem = findMenuItem(pageName, cachedMenuTree!)
  
  if (menuItem && menuItem.path) {
    router.push(menuItem.path)
  } else {
    localStorage.setItem('sidebarActiveMenu', pageName)
    router.push('/404')
  }
}