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

    <div class="reports-grid">
      <div 
        v-for="report in reports" 
        :key="report.id"
        class="report-card tara-card"
      >
        <div class="report-header">
          <div class="report-icon" :class="report.iconClass">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
            </svg>
          </div>
          <span class="status-badge" :class="report.statusClass">{{ report.status }}</span>
        </div>
        
        <h3 class="report-name">{{ report.name }}</h3>
        <p class="report-project">{{ report.project }}</p>
        
        <div class="report-meta">
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            <span>{{ report.date }}</span>
          </div>
          <div class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <span>{{ report.pages }} 页</span>
          </div>
        </div>
        
        <div class="report-stats">
          <div class="stat">
            <span class="stat-value">{{ report.assets }}</span>
            <span class="stat-label">资产</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ report.threats }}</span>
            <span class="stat-label">威胁</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ report.measures }}</span>
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
          <button class="tara-btn tara-btn-primary" @click="downloadReport(report)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            下载
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const reports = ref([
  { id: '1', name: 'MY25 EV平台 TARA报告 v1.2', project: 'MY25 EV平台', date: '2024-12-15', pages: 156, assets: 48, threats: 127, measures: 89, status: '已完成', statusClass: 'active', iconClass: 'blue' },
  { id: '2', name: 'ADAS L3系统威胁分析报告', project: 'ADAS L3系统', date: '2024-12-10', pages: 89, assets: 32, threats: 85, measures: 62, status: '审核中', statusClass: 'review', iconClass: 'purple' },
  { id: '3', name: '智能座舱风险评估报告', project: '智能座舱2.0', date: '2024-12-05', pages: 45, assets: 21, threats: 43, measures: 28, status: '草稿', statusClass: 'draft', iconClass: 'cyan' }
])

const previewReport = (report: any) => {
  console.log('Preview:', report)
}

const downloadReport = (report: any) => {
  console.log('Download:', report)
}
</script>

<style scoped>
.page-container {
  max-width: 1200px;
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
