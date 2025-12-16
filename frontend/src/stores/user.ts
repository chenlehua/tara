import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string
  role: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const userInitial = computed(() => user.value?.username?.charAt(0) || 'U')
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)
  }

  const login = async (email: string, _password: string) => {
    isLoading.value = true
    try {
      // TODO: Call actual API
      // const response = await authApi.login(email, _password)
      
      // Mock response for development
      const mockUser: User = {
        id: '1',
        username: '张工程师',
        email: email,
        role: '高级安全分析师'
      }
      const mockToken = 'mock-jwt-token-' + Date.now()
      
      setUser(mockUser)
      setToken(mockToken)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  const checkAuth = async () => {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      token.value = savedToken
      // TODO: Validate token and fetch user info
      // For now, set a mock user
      user.value = {
        id: '1',
        username: '张工程师',
        email: 'zhang@example.com',
        role: '高级安全分析师'
      }
    }
  }

  const updateProfile = async (updates: Partial<User>) => {
    if (!user.value) return
    
    isLoading.value = true
    try {
      // TODO: Call actual API
      user.value = { ...user.value, ...updates }
      return { success: true }
    } catch (error) {
      console.error('Update profile error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // Initialize
  checkAuth()

  return {
    // State
    user,
    token,
    isLoading,
    // Getters
    isLoggedIn,
    userInitial,
    isAdmin,
    // Actions
    setUser,
    setToken,
    login,
    logout,
    checkAuth,
    updateProfile
  }
})
