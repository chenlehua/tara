<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>项目管理</h1>
        <p class="page-subtitle">管理和跟踪TARA安全分析项目</p>
      </div>
      <div class="header-actions">
        <router-link to="/generator" class="tara-btn tara-btn-secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
          </svg>
          一键生成
        </router-link>
        <button class="tara-btn tara-btn-primary" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          新建项目
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载项目列表...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="projects.length === 0" class="empty-container">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 16H9m10 0h3v-3.15a1 1 0 00-.84-.99L16 11l-2.7-3.6a1 1 0 00-.8-.4H5.24a2 2 0 00-1.8 1.1l-.8 1.63A6 6 0 002 12.42V16h2"/>
          <circle cx="6.5" cy="16.5" r="2.5"/>
          <circle cx="16.5" cy="16.5" r="2.5"/>
        </svg>
      </div>
      <h3>暂无项目</h3>
      <p>点击"一键生成"上传文件自动创建项目，或点击"新建项目"手动创建</p>
      <div class="empty-actions">
        <router-link to="/generator" class="tara-btn tara-btn-primary">
          一键生成报告
        </router-link>
      </div>
    </div>

    <!-- Projects Grid -->
    <div v-else class="projects-grid">
      <div 
        v-for="project in projects" 
        :key="project.id"
        class="project-card tara-card"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <div class="project-card-header">
          <div class="project-icon" :class="getIconClass(project.status)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 16H9m10 0h3v-3.15a1 1 0 00-.84-.99L16 11l-2.7-3.6a1 1 0 00-.8-.4H5.24a2 2 0 00-1.8 1.1l-.8 1.63A6 6 0 002 12.42V16h2"/>
              <circle cx="6.5" cy="16.5" r="2.5"/>
              <circle cx="16.5" cy="16.5" r="2.5"/>
            </svg>
          </div>
          <span class="status-badge" :class="getStatusClass(project.status)">{{ getStatusText(project.status) }}</span>
        </div>
        
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-desc">{{ project.description || '暂无描述' }}</p>
        
        <div class="project-meta">
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 16H9m10 0h3v-3.15a1 1 0 00-.84-.99L16 11l-2.7-3.6a1 1 0 00-.8-.4H5.24a2 2 0 00-1.8 1.1l-.8 1.63A6 6 0 002 12.42V16h2"/>
            </svg>
            <span>{{ project.vehicle_type || project.vehicleType || '通用' }}</span>
          </div>
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <span>{{ project.standard || 'ISO 21434' }}</span>
          </div>
        </div>
        
        <div class="project-stats">
          <div class="stat">
            <span class="stat-value">{{ project.assets_count || 0 }}</span>
            <span class="stat-label">资产</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ project.threats_count || 0 }}</span>
            <span class="stat-label">威胁</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ project.reports_count || 0 }}</span>
            <span class="stat-label">报告</span>
          </div>
        </div>
        
        <div class="project-footer">
          <span class="create-time">创建: {{ formatDate(project.created_at || project.createdAt) }}</span>
          <div class="project-actions-mini">
            <button class="action-btn" @click.stop="viewProject(project)" title="查看详情">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button 
        class="tara-btn tara-btn-ghost" 
        :disabled="page === 1"
        @click="page--; loadProjects()"
      >上一页</button>
      <span class="page-info">第 {{ page }} / {{ Math.ceil(total / pageSize) }} 页</span>
      <button 
        class="tara-btn tara-btn-ghost"
        :disabled="page >= Math.ceil(total / pageSize)"
        @click="page++; loadProjects()"
      >下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { projectApi, type Project } from '@/api'

const router = useRouter()

const showCreateModal = ref(false)
const loading = ref(true)
const projects = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await projectApi.list({
      page: page.value,
      pageSize: pageSize.value,
    })
    if (response.success && response.data) {
      projects.value = response.data.items || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    console.error('Failed to load projects:', error)
    // Fallback to demo data
    projects.value = [
      {
        id: 1,
        name: 'MY25 EV平台',
        description: '新能源汽车整车网络安全TARA分析',
        vehicle_type: '新能源汽车',
        standard: 'ISO 21434',
        status: 1,
        assets_count: 48,
        threats_count: 127,
        reports_count: 3,
        created_at: '2024-12-15T10:00:00Z',
      },
      {
        id: 2,
        name: 'ADAS L3系统',
        description: '高级驾驶辅助系统安全分析',
        vehicle_type: '智能驾驶',
        standard: 'ISO 21434',
        status: 1,
        assets_count: 32,
        threats_count: 85,
        reports_count: 2,
        created_at: '2024-12-10T10:00:00Z',
      },
      {
        id: 3,
        name: '智能座舱2.0',
        description: '车载信息娱乐系统安全分析',
        vehicle_type: '智能座舱',
        standard: 'ISO 21434',
        status: 0,
        assets_count: 21,
        threats_count: 43,
        reports_count: 1,
        created_at: '2024-12-05T10:00:00Z',
      }
    ]
    total.value = 3
  } finally {
    loading.value = false
  }
}

const getStatusText = (status?: number) => {
  switch (status) {
    case 0: return '草稿'
    case 1: return '进行中'
    case 2: return '已完成'
    case 3: return '已归档'
    default: return '未知'
  }
}

const getStatusClass = (status?: number) => {
  switch (status) {
    case 0: return 'draft'
    case 1: return 'active'
    case 2: return 'completed'
    case 3: return 'archived'
    default: return 'draft'
  }
}

const getIconClass = (status?: number) => {
  switch (status) {
    case 0: return 'cyan'
    case 1: return 'blue'
    case 2: return 'green'
    case 3: return 'purple'
    default: return 'cyan'
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const viewProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.page-container {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-subtitle {
  color: var(--text-muted);
  font-size: 15px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--brand-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-container p {
  color: var(--text-muted);
  font-size: 14px;
}

/* Empty State */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
  color: var(--brand-blue);
}

.empty-container h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-container p {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 20px;
  max-width: 400px;
}

.empty-actions {
  display: flex;
  gap: 12px;
}

/* Project Meta */
.project-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

/* Status Classes */
.status-badge.completed {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}

.status-badge.archived {
  background: rgba(156, 163, 175, 0.15);
  color: #9CA3AF;
}

.project-icon.green {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}

/* Project Footer */
.create-time {
  font-size: 12px;
  color: var(--text-muted);
}

.project-actions-mini {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--brand-blue);
  border-color: var(--brand-blue);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.project-card {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.project-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-icon svg {
  width: 24px;
  height: 24px;
}

.project-icon.blue { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.project-icon.purple { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }
.project-icon.cyan { background: rgba(6, 182, 212, 0.15); color: #22D3EE; }

.project-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.project-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
  line-height: 1.5;
}

.project-stats {
  display: flex;
  gap: 24px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.deadline {
  font-size: 13px;
  color: var(--text-muted);
}

.avatars {
  display: flex;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-blue), var(--brand-purple));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  border: 2px solid var(--bg-secondary);
  margin-left: -8px;
}

.avatar:first-child {
  margin-left: 0;
}
</style>
