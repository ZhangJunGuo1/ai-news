export interface IconItem {
  name: string
  emoji: string
  label: string
}

export const ICON_LIST: IconItem[] = [
  { name: 'news', emoji: '📰', label: '新闻' },
  { name: 'users', emoji: '👥', label: '用户' },
  { name: 'settings', emoji: '🔧', label: '设置' },
  { name: 'summary', emoji: '📋', label: '汇总' },
  { name: 'category', emoji: '📑', label: '分类' },
  { name: 'edit', emoji: '✏️', label: '编辑' },
  { name: 'user', emoji: '👤', label: '用户' },
  { name: 'pin', emoji: '📌', label: '标记' },
  { name: 'lock', emoji: '🔒', label: '安全' },
  { name: 'menu', emoji: '🗂️', label: '菜单' },
  { name: 'archive', emoji: '🗃️', label: '归档' },
  { name: 'china', emoji: '🇨🇳', label: '中国' },
  { name: 'world', emoji: '🌍', label: '世界' },
  { name: 'spider', emoji: '🕷️', label: '采集' },
  { name: 'api', emoji: '📡', label: 'API' },
  { name: 'llm', emoji: '🤖', label: '大语言模型' },
  { name: 'web', emoji: '🌐', label: '网页' },
  { name: 'write', emoji: '📝', label: '撰写' },
  { name: 'folder', emoji: '📁', label: '文件夹' },
  { name: 'published', emoji: '📮', label: '已发布' },
  { name: 'refresh', emoji: '🔄', label: '刷新' },
  { name: 'add', emoji: '➕', label: '添加' },
  { name: 'warning', emoji: '⚠️', label: '警告' },
  { name: 'home', emoji: '🏠', label: '首页' },
  { name: 'dashboard', emoji: '📊', label: '仪表盘' },
  { name: 'chart', emoji: '📈', label: '图表' },
  { name: 'calendar', emoji: '📅', label: '日历' },
  { name: 'bell', emoji: '🔔', label: '通知' },
  { name: 'star', emoji: '⭐', label: '收藏' },
  { name: 'heart', emoji: '❤️', label: '喜欢' },
  { name: 'search', emoji: '🔍', label: '搜索' },
  { name: 'eye', emoji: '👁️', label: '查看' },
  { name: 'camera', emoji: '📷', label: '相机' },
  { name: 'video', emoji: '🎥', label: '视频' },
  { name: 'music', emoji: '🎵', label: '音乐' },
  { name: 'cloud', emoji: '☁️', label: '云' },
  { name: 'download', emoji: '⬇️', label: '下载' },
  { name: 'upload', emoji: '⬆️', label: '上传' },
  { name: 'link', emoji: '🔗', label: '链接' },
  { name: 'trash', emoji: '🗑️', label: '删除' },
  { name: 'flag', emoji: '🚩', label: '标记' },
  { name: 'gift', emoji: '🎁', label: '礼物' },
  { name: 'rocket', emoji: '🚀', label: '火箭' },
  { name: 'fire', emoji: '🔥', label: '热门' },
]

export const getIconByName = (name: string): string => {
  const icon = ICON_LIST.find(i => i.name === name)
  return icon?.emoji || '📄'
}

export const getIconNameByEmoji = (emoji: string): string => {
  const icon = ICON_LIST.find(i => i.emoji === emoji)
  return icon?.name || ''
}
