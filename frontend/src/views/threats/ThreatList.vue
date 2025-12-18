<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>威胁分析</h1>
        <p class="page-subtitle">基于STRIDE模型的威胁识别与分析</p>
      </div>
      <button class="tara-btn tara-btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
        </svg>
        AI 威胁分析
      </button>
    </div>

    <!-- STRIDE Distribution -->
    <div class="stride-overview">
      <div 
        v-for="category in strideCategories" 
        :key="category.id"
        class="stride-card"
        :class="{ active: selectedCategory === category.id }"
        @click="selectedCategory = selectedCategory === category.id ? null : category.id"
      >
        <div class="stride-icon" :style="{ background: category.bgColor, color: category.color }">
          {{ category.letter }}
        </div>
        <div class="stride-info">
          <div class="stride-name">{{ category.name }}</div>
          <div class="stride-count">{{ category.count }} 威胁</div>
        </div>
      </div>
    </div>

    <!-- Threats Table -->
    <div class="tara-card">
      <div class="tara-card-header">
        <h3 class="tara-card-title">
          <div class="tara-card-title-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
          </div>
          威胁列表
        </h3>
        <div class="table-actions">
          <select v-model="filterRisk">
            <option value="">全部风险等级</option>
            <option value="critical">极高 (CAL-4)</option>
            <option value="high">高 (CAL-3)</option>
            <option value="medium">中 (CAL-2)</option>
            <option value="low">低 (CAL-1)</option>
          </select>
        </div>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载威胁数据中...</p>
      </div>

      <div v-else-if="filteredThreats.length === 0" class="empty-container">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
        </div>
        <h3>暂无威胁数据</h3>
        <p>使用一键生成报告功能自动分析威胁</p>
        <router-link to="/generator" class="tara-btn tara-btn-primary">
          一键生成报告
        </router-link>
      </div>
      
      <div v-else class="threats-table">
        <table>
          <thead>
            <tr>
              <th>威胁ID</th>
              <th>威胁名称</th>
              <th>STRIDE类型</th>
              <th>项目ID</th>
              <th>风险等级</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="threat in filteredThreats" :key="threat.id">
              <td class="threat-id">THR-{{ String(threat.id).padStart(3, '0') }}</td>
              <td class="threat-name">{{ threat.threat_name }}</td>
              <td>
                <span class="stride-tag" :style="{ background: getStrideColor(threat.threat_type) }">
                  {{ threat.threat_type }}
                </span>
              </td>
              <td class="threat-asset">项目 #{{ threat.project_id }}</td>
              <td>
                <span class="risk-badge" :class="getRiskClass(threat.risk_level)">
                  {{ threat.risk_level || 'CAL-2' }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="getStatusClass(threat.treatment)">
                  {{ getStatusText(threat.treatment) }}
                </span>
              </td>
              <td class="actions">
                <button class="action-btn" title="查看详情">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
                <button class="action-btn" title="分析攻击路径">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="18" cy="18" r="3"/>
                    <circle cx="6" cy="6" r="3"/>
                    <path d="M6 21V9a9 9 0 009 9"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { threatApi, type Threat } from '@/api'

const selectedCategory = ref<string | null>(null)
const filterRisk = ref('')
const loading = ref(true)
const threats = ref<Threat[]>([])

const strideCategories = computed(() => {
  const categories = [
    { id: 'S', letter: 'S', name: 'Spoofing', count: 0, bgColor: 'rgba(59,130,246,0.12)', color: '#60A5FA' },
    { id: 'T', letter: 'T', name: 'Tampering', count: 0, bgColor: 'rgba(139,92,246,0.12)', color: '#A78BFA' },
    { id: 'R', letter: 'R', name: 'Repudiation', count: 0, bgColor: 'rgba(236,72,153,0.12)', color: '#F472B6' },
    { id: 'I', letter: 'I', name: 'Info Disclosure', count: 0, bgColor: 'rgba(245,158,11,0.12)', color: '#FBBF24' },
    { id: 'D', letter: 'D', name: 'Denial of Service', count: 0, bgColor: 'rgba(239,68,68,0.12)', color: '#F87171' },
    { id: 'E', letter: 'E', name: 'Elevation', count: 0, bgColor: 'rgba(16,185,129,0.12)', color: '#34D399' }
  ]
  
  // Count threats by STRIDE type
  threats.value.forEach(threat => {
    const cat = categories.find(c => c.id === threat.threat_type)
    if (cat) cat.count++
  })
  
  return categories
})

const loadThreats = async () => {
  loading.value = true
  try {
    const response = await threatApi.list({
      page: 1,
      page_size: 100,
    })
    if (response.success && response.data) {
      threats.value = response.data.items || []
    }
  } catch (error) {
    console.error('Failed to load threats:', error)
  } finally {
    loading.value = false
  }
}

const getRiskClass = (riskLevel: string | undefined): string => {
  if (!riskLevel) return 'medium'
  const map: Record<string, string> = {
    'CAL-4': 'critical',
    'CAL-3': 'high',
    'CAL-2': 'medium',
    'CAL-1': 'low',
  }
  return map[riskLevel] || 'medium'
}

const getStatusText = (treatment: string | undefined): string => {
  const map: Record<string, string> = {
    'mitigate': '已处理',
    'accept': '已接受',
    'transfer': '已转移',
    'avoid': '已规避',
  }
  return map[treatment || ''] || '待处理'
}

const getStatusClass = (treatment: string | undefined): string => {
  const map: Record<string, string> = {
    'mitigate': 'active',
    'accept': 'review',
    'transfer': 'review',
    'avoid': 'active',
  }
  return map[treatment || ''] || 'draft'
}

const filteredThreats = computed(() => {
  return threats.value.filter(threat => {
    const matchesCategory = !selectedCategory.value || threat.threat_type === selectedCategory.value
    const matchesRisk = !filterRisk.value || getRiskClass(threat.risk_level) === filterRisk.value
    return matchesCategory && matchesRisk
  })
})

const getStrideColor = (stride: string) => {
  const colors: Record<string, string> = {
    'S': 'rgba(59,130,246,0.2)',
    'T': 'rgba(139,92,246,0.2)',
    'R': 'rgba(236,72,153,0.2)',
    'I': 'rgba(245,158,11,0.2)',
    'D': 'rgba(239,68,68,0.2)',
    'E': 'rgba(16,185,129,0.2)'
  }
  return colors[stride] || 'rgba(148,163,184,0.2)'
}

onMounted(() => {
  loadThreats()
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

.stride-overview {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stride-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.stride-card:hover {
  background: var(--bg-hover);
}

.stride-card.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--brand-blue);
}

.stride-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
}

.stride-name {
  font-size: 13px;
  font-weight: 600;
}

.stride-count {
  font-size: 12px;
  color: var(--text-muted);
}

.table-actions {
  display: flex;
  gap: 12px;
}

.table-actions select {
  height: 36px;
  padding: 0 32px 0 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.threats-table {
  overflow-x: auto;
}

.threats-table table {
  width: 100%;
  border-collapse: collapse;
}

.threats-table th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
}

.threats-table td {
  padding: 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
}

.threats-table tr:hover {
  background: var(--bg-hover);
}

.threat-id {
  font-family: 'SF Mono', monospace;
  color: var(--text-muted);
}

.threat-name {
  font-weight: 500;
}

.stride-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.risk-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.risk-badge.critical { background: rgba(185, 28, 28, 0.15); color: #F87171; }
.risk-badge.high { background: rgba(245, 158, 11, 0.15); color: #FBBF24; }
.risk-badge.medium { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.risk-badge.low { background: rgba(16, 185, 129, 0.15); color: #34D399; }

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

@media (max-width: 1200px) {
  .stride-overview {
    grid-template-columns: repeat(3, 1fr);
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
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

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: var(--bg-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 28px;
  height: 28px;
  color: var(--text-muted);
}

.empty-container h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

.empty-container p {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 20px;
}
</style>
