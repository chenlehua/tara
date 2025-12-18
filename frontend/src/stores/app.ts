import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const locale = ref('zh-CN')

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const setLocale = (newLocale: string) => {
    locale.value = newLocale
  }

  return {
    sidebarCollapsed,
    theme,
    locale,
    toggleSidebar,
    setTheme,
    setLocale,
  }
})
