const THEME_KEY = 'app-theme'

export type ThemeType = 'light' | 'dark'

export const getTheme = (): ThemeType => {
  return (localStorage.getItem(THEME_KEY) as ThemeType) || 'dark'
}

export const setTheme = (theme: ThemeType): void => {
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.classList.toggle('dark', theme === 'dark')
  localStorage.setItem(THEME_KEY, theme)
}

export const initTheme = (): void => {
  const theme = getTheme()
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.classList.toggle('dark', theme === 'dark')
}
