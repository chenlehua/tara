<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>安全措施</h1>
        <p class="page-subtitle">威胁缓解措施与安全控制</p>
      </div>
      <button class="tara-btn tara-btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        添加措施
      </button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载安全措施中...</p>
    </div>

    <div v-else-if="measures.length === 0" class="empty-container">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <h3>暂无安全措施</h3>
      <p>使用一键生成报告功能自动生成安全措施建议</p>
      <router-link to="/generator" class="tara-btn tara-btn-primary">
        一键生成报告
      </router-link>
    </div>

    <div v-else class="measures-grid">
      <div 
        v-for="measure in measures" 
        :key="measure.id"
        class="measure-card tara-card"
      >
        <div class="measure-header">
          <div class="measure-icon" :class="getCategoryClass(measure.category)">
            <component :is="getCategoryIcon(measure.category)" />
          </div>
          <span class="status-badge" :class="getStatusClass(measure.status)">{{ getStatusText(measure.status) }}</span>
        </div>
        
        <h3 class="measure-name">{{ measure.name }}</h3>
        <p class="measure-desc">{{ measure.description || measure.implementation }}</p>
        
        <div class="measure-meta">
          <div class="meta-item">
            <span class="meta-label">类型</span>
            <span class="meta-value">{{ measure.control_type || measure.category }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">ISO 21434</span>
            <span class="meta-value">{{ measure.iso21434_ref || '-' }}</span>
          </div>
        </div>
        
        <div class="measure-footer">
          <div class="effectiveness">
            <span>有效性</span>
            <div class="effectiveness-bar">
              <div class="effectiveness-fill" :style="{ width: (measure.effectiveness || 80) + '%' }"></div>
            </div>
            <span class="effectiveness-value">{{ measure.effectiveness || 80 }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { measureApi, type ControlMeasure } from '@/api'

// Icons used for different control categories
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}
const IconEye = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
}
const IconRefresh = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>`
}

const loading = ref(true)
const measures = ref<ControlMeasure[]>([])

const loadMeasures = async () => {
  loading.value = true
  try {
    const response = await measureApi.list({
      page: 1,
      page_size: 100,
    })
    if (response.success && response.data) {
      measures.value = response.data.items || []
    }
  } catch (error) {
    console.error('Failed to load measures:', error)
  } finally {
    loading.value = false
  }
}

const getCategoryClass = (category: string | undefined): string => {
  const map: Record<string, string> = {
    '加密': 'blue',
    '完整性': 'purple',
    '检测': 'orange',
    '更新': 'green',
    '隔离': 'cyan',
    'prevention': 'blue',
    'detection': 'orange',
    'response': 'green',
  }
  return map[category || ''] || 'blue'
}

const getCategoryIcon = (category: string | undefined) => {
  const map: Record<string, any> = {
    '加密': IconShield,
    '完整性': IconShield,
    '检测': IconEye,
    '更新': IconRefresh,
    '隔离': IconShield,
    'prevention': IconShield,
    'detection': IconEye,
    'response': IconRefresh,
  }
  return map[category || ''] || IconShield
}

const getStatusText = (status: string | undefined): string => {
  const map: Record<string, string> = {
    'implemented': '已实施',
    'in_progress': '部署中',
    'planned': '规划中',
  }
  return map[status || ''] || status || '已实施'
}

const getStatusClass = (status: string | undefined): string => {
  const map: Record<string, string> = {
    'implemented': 'active',
    'in_progress': 'review',
    'planned': 'draft',
  }
  return map[status || ''] || 'active'
}

onMounted(() => {
  loadMeasures()
})
</script>

<style scoped>
.page-container {
  max-width: 1400px;
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

.measures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.measure-card {
  transition: all var(--transition-normal);
}

.measure-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.measure-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.measure-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.measure-icon svg {
  width: 24px;
  height: 24px;
}

.measure-icon.blue { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.measure-icon.purple { background: rgba(139, 92, 246, 0.12); color: #A78BFA; }
.measure-icon.orange { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
.measure-icon.green { background: rgba(16, 185, 129, 0.12); color: #34D399; }
.measure-icon.cyan { background: rgba(6, 182, 212, 0.12); color: #22D3EE; }

.measure-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.measure-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
}

.measure-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 12px;
  color: var(--text-disabled);
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
}

.measure-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.effectiveness {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--text-muted);
}

.effectiveness-bar {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.effectiveness-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--success), #059669);
  transition: width 0.6s ease;
}

.effectiveness-value {
  font-weight: 600;
  color: var(--success);
  min-width: 40px;
  text-align: right;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
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

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--bg-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 32px;
  height: 32px;
  color: var(--text-muted);
}

.empty-container h3 {
  font-size: 18px;
  margin-bottom: 8px;
}

.empty-container p {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 24px;
}
</style>
