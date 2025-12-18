<template>
  <div class="login-container">
    <div class="ambient-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
    </div>
    
    <div class="login-card animate-fadeIn">
      <div class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <div class="logo-text">
          <div class="logo-title">TARA Pro</div>
          <div class="logo-subtitle">智能安全分析平台</div>
        </div>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>邮箱地址</label>
          <div class="input-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <path d="M22 6l-10 7L2 6"/>
            </svg>
            <input 
              type="email" 
              v-model="email" 
              placeholder="请输入邮箱"
              required
            >
          </div>
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <div class="input-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="11" width="18" height="11" rx="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
              placeholder="请输入密码"
              required
            >
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                <path d="M1 1l22 22"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe">
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>
        
        <button type="submit" class="login-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>
      
      <div class="login-footer">
        <p>还没有账号？ <a href="#">联系管理员</a></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  try {
    await userStore.login(email.value, password.value)
    router.push('/')
  } catch (error) {
    console.error('Login failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(24px);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  position: relative;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.logo-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.logo-title {
  font-size: 24px;
  font-weight: 700;
}

.logo-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper svg {
  position: absolute;
  left: 16px;
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.input-wrapper input {
  width: 100%;
  height: 48px;
  padding: 0 48px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 15px;
  outline: none;
  transition: all var(--transition-normal);
}

.input-wrapper input:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.toggle-password {
  position: absolute;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.toggle-password:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toggle-password svg {
  position: static;
  width: 18px;
  height: 18px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
}

.remember-me input {
  width: 16px;
  height: 16px;
}

.forgot-password {
  font-size: 14px;
  color: var(--brand-blue);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-btn {
  height: 48px;
  border-radius: var(--radius-md);
  border: none;
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-purple) 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: 32px;
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
}

.login-footer a {
  color: var(--brand-blue);
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>
