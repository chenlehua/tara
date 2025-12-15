<template>
  <div class="app-container">
    <!-- Ambient Background -->
    <div class="ambient-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div class="logo-text">
            <div class="logo-title">TARA Pro</div>
            <div class="logo-subtitle">智能安全分析</div>
          </div>
        </div>
      </div>

      <nav class="nav-menu">
        <div class="nav-section-title">主要功能</div>
        <router-link 
          v-for="item in mainNavItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item"
          :class="{ active: isActiveRoute(item.path) }"
        >
          <component :is="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge" :class="item.badgeType">
            {{ item.badge }}
          </span>
        </router-link>

        <div class="nav-section-title" style="margin-top: 16px;">分析模块</div>
        <router-link 
          v-for="item in analysisNavItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item"
          :class="{ active: isActiveRoute(item.path) }"
        >
          <component :is="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge" :class="item.badgeType">
            {{ item.badge }}
          </span>
        </router-link>

        <div class="nav-section-title" style="margin-top: 16px;">输出</div>
        <router-link 
          v-for="item in outputNavItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item"
          :class="{ active: isActiveRoute(item.path) }"
        >
          <component :is="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge" :class="item.badgeType">
            {{ item.badge }}
          </span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="toggleSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          <span>收起菜单</span>
        </button>
        <div class="user-card" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <div class="user-name">{{ userName }}</div>
            <div class="user-role">{{ userRole }}</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <div class="page-title">
            <div class="page-title-icon" :style="{ background: currentPageColor }">
              <component :is="currentPageIcon" />
            </div>
            <span>{{ currentPageTitle }}</span>
          </div>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            <input 
              type="text" 
              placeholder="搜索资产、威胁、报告..." 
              v-model="searchQuery"
              @keyup.enter="handleSearch"
            >
            <span class="search-shortcut">⌘K</span>
          </div>
          <button class="icon-btn" @click="showNotifications = !showNotifications">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>
            </svg>
            <span v-if="hasNotifications" class="badge"></span>
          </button>
          <button class="icon-btn" @click="showSettings = !showSettings">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
            </svg>
          </button>
        </div>
      </header>

      <!-- Content Wrapper -->
      <div class="content-wrapper">
        <!-- Content Area -->
        <div class="content-area">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>

        <!-- AI Panel -->
        <AiChatPanel v-if="showAiPanel" @close="showAiPanel = false" />
      </div>
    </main>

    <!-- AI Toggle Button (when panel is hidden) -->
    <button v-if="!showAiPanel" class="ai-toggle-btn" @click="showAiPanel = true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96.44 2.5 2.5 0 01-2.96-3.08 3 3 0 01-.34-5.58 2.5 2.5 0 011.32-4.24 2.5 2.5 0 011.98-3A2.5 2.5 0 019.5 2z"/>
        <path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.96.44 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-1.98-3A2.5 2.5 0 0014.5 2z"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AiChatPanel from '@/components/ai/AiChatPanel.vue'

// Icons as inline components
const IconHome = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><path d="M9 22V12h6v10"/></svg>`
}
const IconSparkles = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/></svg>`
}
const IconFolder = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>`
}
const IconCpu = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>`
}
const IconWarning = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>`
}
const IconActivity = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
}
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}
const IconFile = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>`
}
const IconDatabase = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`
}

const route = useRoute()
const userStore = useUserStore()

// State
const sidebarCollapsed = ref(false)
const showAiPanel = ref(true)
const showUserMenu = ref(false)
const showNotifications = ref(false)
const showSettings = ref(false)
const searchQuery = ref('')
const hasNotifications = ref(true)

// User info
const userName = computed(() => userStore.user?.username || '张工程师')
const userRole = computed(() => userStore.user?.role || '高级安全分析师')
const userInitial = computed(() => userName.value.charAt(0))

// Navigation items
const mainNavItems = [
  { path: '/', label: '工作台', icon: IconHome },
  { path: '/generator', label: '一键生成报告', icon: IconSparkles, badge: 'AI', badgeType: 'new' }
]

const analysisNavItems = [
  { path: '/projects', label: '项目管理', icon: IconFolder, badge: '3' },
  { path: '/assets', label: '资产识别', icon: IconCpu, badge: '48' },
  { path: '/threats', label: '威胁分析', icon: IconWarning, badge: '127', badgeType: 'danger' },
  { path: '/risks', label: '风险评估', icon: IconActivity, badge: '23', badgeType: 'danger' },
  { path: '/measures', label: '安全措施', icon: IconShield, badge: '89', badgeType: 'success' }
]

const outputNavItems = [
  { path: '/reports', label: '报告中心', icon: IconFile, badge: '2' },
  { path: '/knowledge', label: '知识库', icon: IconDatabase }
]

// Page info based on current route
const pageConfig: Record<string, { title: string; icon: any; color: string }> = {
  '/': { title: '工作台', icon: IconHome, color: 'rgba(59,130,246,0.15)' },
  '/generator': { title: '一键生成报告', icon: IconSparkles, color: 'rgba(139,92,246,0.15)' },
  '/projects': { title: '项目管理', icon: IconFolder, color: 'rgba(59,130,246,0.15)' },
  '/assets': { title: '资产识别', icon: IconCpu, color: 'rgba(6,182,212,0.15)' },
  '/threats': { title: '威胁分析', icon: IconWarning, color: 'rgba(245,158,11,0.15)' },
  '/risks': { title: '风险评估', icon: IconActivity, color: 'rgba(239,68,68,0.15)' },
  '/measures': { title: '安全措施', icon: IconShield, color: 'rgba(16,185,129,0.15)' },
  '/reports': { title: '报告中心', icon: IconFile, color: 'rgba(139,92,246,0.15)' },
  '/knowledge': { title: '知识库', icon: IconDatabase, color: 'rgba(6,182,212,0.15)' }
}

const currentPageTitle = computed(() => {
  const basePath = '/' + (route.path.split('/')[1] || '')
  return pageConfig[basePath]?.title || '工作台'
})

const currentPageIcon = computed(() => {
  const basePath = '/' + (route.path.split('/')[1] || '')
  return pageConfig[basePath]?.icon || IconHome
})

const currentPageColor = computed(() => {
  const basePath = '/' + (route.path.split('/')[1] || '')
  return pageConfig[basePath]?.color || 'rgba(59,130,246,0.15)'
})

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const isActiveRoute = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const handleSearch = () => {
  console.log('Search:', searchQuery.value)
}
</script>

<style scoped>
/* ==================== SIDEBAR ==================== */
.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(24px);
  border-right: 1px solid var(--border-color);
  position: relative;
  z-index: 20;
  transition: width var(--transition-slow);
}

.sidebar.collapsed {
  width: 76px;
}

.sidebar-header {
  height: 68px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.logo-icon svg {
  width: 22px;
  height: 22px;
  color: white;
}

.logo-text {
  overflow: hidden;
  transition: opacity var(--transition-slow), width var(--transition-slow);
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  width: 0;
}

.logo-title {
  font-weight: 700;
  font-size: 18px;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Navigation */
.nav-section-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-disabled);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 0 12px;
  margin-bottom: 8px;
}

.sidebar.collapsed .nav-section-title {
  display: none;
}

.nav-menu {
  flex: 1;
  padding: 8px 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
  color: var(--text-primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 22px;
  background: linear-gradient(180deg, var(--brand-blue), var(--brand-purple));
  border-radius: 0 3px 3px 0;
}

.nav-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  transition: color var(--transition-normal);
}

.nav-item.active svg {
  color: var(--brand-blue);
}

.nav-label {
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
}

.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-badge {
  display: none;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-color);
}

.collapse-btn {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-normal);
  font-size: 13px;
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.collapse-btn svg {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-slow);
}

.sidebar.collapsed .collapse-btn svg {
  transform: rotate(180deg);
}

.sidebar.collapsed .collapse-btn span {
  display: none;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-normal);
  margin-top: 8px;
}

.user-card:hover {
  background: var(--bg-hover);
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34D399, #06B6D4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.user-info {
  overflow: hidden;
}

.sidebar.collapsed .user-info {
  display: none;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-muted);
}

/* ==================== MAIN CONTENT ==================== */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 10;
}

/* Header */
.header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title-icon svg {
  width: 18px;
  height: 18px;
  color: #60A5FA;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
}

.search-box input {
  width: 260px;
  height: 40px;
  padding: 0 16px 0 42px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: all var(--transition-normal);
}

.search-box input::placeholder {
  color: var(--text-muted);
}

.search-box input:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.search-box svg {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.search-shortcut {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  padding: 3px 6px;
  border-radius: 4px;
  background: var(--bg-hover);
  color: var(--text-disabled);
  font-size: 11px;
  font-weight: 500;
}

/* Content Area */
.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.content-area {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
}

/* AI Toggle Button */
.ai-toggle-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-pink) 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
  z-index: 100;
  transition: all var(--transition-normal);
}

.ai-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.5);
}

.ai-toggle-btn svg {
  width: 24px;
  height: 24px;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1400px) {
  .sidebar {
    width: 76px;
  }
  
  .sidebar .logo-text,
  .sidebar .nav-label,
  .sidebar .nav-badge,
  .sidebar .user-info,
  .sidebar .collapse-btn span,
  .sidebar .nav-section-title {
    display: none;
  }
  
  .sidebar .collapse-btn svg {
    transform: rotate(180deg);
  }
}
</style>
