<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>报告中心</h1>
        <p class="page-subtitle">管理和导出TARA安全分析报告</p>
      </div>
      <router-link to="/generator" class="tara-btn tara-btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
        </svg>
        生成新报告
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载报告列表...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="reports.length === 0" class="empty-container">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <path d="M14 2v6h6M12 18v-6M9 15h6"/>
        </svg>
      </div>
      <h3>暂无报告</h3>
      <p>点击"生成新报告"按钮开始创建您的第一份TARA分析报告</p>
      <router-link to="/generator" class="tara-btn tara-btn-primary">
        生成新报告
      </router-link>
    </div>

    <!-- Reports Grid -->
    <div v-else class="reports-grid">
      <div 
        v-for="report in reports" 
        :key="report.id"
        class="report-card tara-card"
      >
        <div class="report-header">
          <div class="report-icon" :class="getIconClass(report.status)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
            </svg>
          </div>
          <span class="status-badge" :class="getStatusClass(report.status)">{{ getStatusText(report.status) }}</span>
        </div>
        
        <h3 class="report-name">{{ report.name }}</h3>
        <p class="report-project">项目ID: {{ report.project_id }}</p>
        
        <div class="report-meta">
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            <span>{{ formatDate(report.created_at) }}</span>
          </div>
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <span>{{ report.template || 'ISO 21434' }}</span>
          </div>
        </div>
        
        <div class="report-stats">
          <div class="stat">
            <span class="stat-value">{{ report.statistics?.assets_count || 0 }}</span>
            <span class="stat-label">资产</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ report.statistics?.threats_count || 0 }}</span>
            <span class="stat-label">威胁</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ report.statistics?.measures_count || 0 }}</span>
            <span class="stat-label">措施</span>
          </div>
        </div>
        
        <div class="report-actions">
          <button class="tara-btn tara-btn-secondary" @click="previewReport(report)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            预览
          </button>
          <button class="tara-btn tara-btn-primary" @click="downloadReport(report)" :disabled="report.status !== 2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            下载
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button 
        class="tara-btn tara-btn-ghost" 
        :disabled="page === 1"
        @click="page--; loadReports()"
      >上一页</button>
      <span class="page-info">第 {{ page }} / {{ Math.ceil(total / pageSize) }} 页</span>
      <button 
        class="tara-btn tara-btn-ghost"
        :disabled="page >= Math.ceil(total / pageSize)"
        @click="page++; loadReports()"
      >下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reportApi, type Report } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const loading = ref(true)
const reports = ref<Report[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadReports = async () => {
  loading.value = true
  try {
    const response = await reportApi.listReports(undefined, page.value, pageSize.value)
    if (response.success && response.data) {
      reports.value = response.data.items || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    console.error('Failed to load reports:', error)
    // Fallback to demo data
    reports.value = [
      { 
        id: 1, 
        project_id: 1, 
        name: 'MY25 EV平台 TARA报告 v1.2', 
        report_type: 'tara',
        template: 'ISO 21434',
        status: 2, 
        progress: 100,
        version: '1.2',
        created_at: '2024-12-15T10:00:00Z',
        updated_at: '2024-12-15T10:00:00Z',
        statistics: { assets_count: 48, threats_count: 127, high_risk_count: 12, measures_count: 89 }
      },
      { 
        id: 2, 
        project_id: 2, 
        name: 'ADAS L3系统威胁分析报告', 
        report_type: 'threat',
        template: 'ISO 21434',
        status: 1, 
        progress: 75,
        version: '1.0',
        created_at: '2024-12-10T10:00:00Z',
        updated_at: '2024-12-10T10:00:00Z',
        statistics: { assets_count: 32, threats_count: 85, high_risk_count: 8, measures_count: 62 }
      },
      { 
        id: 3, 
        project_id: 3, 
        name: '智能座舱风险评估报告', 
        report_type: 'risk',
        template: 'ISO 21434',
        status: 0, 
        progress: 0,
        version: '1.0',
        created_at: '2024-12-05T10:00:00Z',
        updated_at: '2024-12-05T10:00:00Z',
        statistics: { assets_count: 21, threats_count: 43, high_risk_count: 5, measures_count: 28 }
      }
    ]
    total.value = 3
  } finally {
    loading.value = false
  }
}

const getStatusText = (status?: number) => {
  switch (status) {
    case 0: return '待生成'
    case 1: return '生成中'
    case 2: return '已完成'
    case 3: return '失败'
    default: return '未知'
  }
}

const getStatusClass = (status?: number) => {
  switch (status) {
    case 0: return 'draft'
    case 1: return 'review'
    case 2: return 'active'
    case 3: return 'failed'
    default: return 'draft'
  }
}

const getIconClass = (status?: number) => {
  switch (status) {
    case 0: return 'cyan'
    case 1: return 'purple'
    case 2: return 'blue'
    case 3: return 'red'
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

const previewReport = (report: Report) => {
  router.push(`/reports/${report.id}`)
}

const downloadReport = (report: Report) => {
  if (report.status !== 2) {
    ElMessage.warning('报告尚未完成生成')
    return
  }
  const url = reportApi.getDownloadUrl(report.id, 'pdf')
  window.open(url, '_blank')
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.page-container {
  max-width: 1200px;
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

/* Status Badge - Failed */
.status-badge.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #F87171;
}

.report-icon.red {
  background: rgba(239, 68, 68, 0.12);
  color: #F87171;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
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

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.report-card {
  transition: all var(--transition-normal);
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.report-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-icon svg {
  width: 24px;
  height: 24px;
}

.report-icon.blue { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.report-icon.purple { background: rgba(139, 92, 246, 0.12); color: #A78BFA; }
.report-icon.cyan { background: rgba(6, 182, 212, 0.12); color: #22D3EE; }

.report-name {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 4px;
}

.report-project {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.report-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.meta-item svg {
  width: 16px;
  height: 16px;
}

.report-stats {
  display: flex;
  gap: 24px;
  padding: 16px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
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

.report-actions {
  display: flex;
  gap: 12px;
}

.report-actions .tara-btn {
  flex: 1;
}
</style>
