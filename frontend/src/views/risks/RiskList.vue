<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>风险评估</h1>
        <p class="page-subtitle">基于ISO 21434的CAL风险等级评估</p>
      </div>
    </div>

    <div class="risk-matrix-container">
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">
            <div class="tara-card-title-icon red">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            风险矩阵
          </h3>
        </div>
        <div class="matrix-wrapper">
          <div class="matrix-y-label">
            <span>影响度</span>
          </div>
          <div class="matrix-content">
            <div class="y-labels">
              <span>极高</span>
              <span>高</span>
              <span>中</span>
              <span>低</span>
              <span>极低</span>
            </div>
            <div class="matrix-grid">
              <div v-for="(row, rowIdx) in matrixData" :key="rowIdx" class="matrix-row">
                <div 
                  v-for="(cell, colIdx) in row" 
                  :key="colIdx"
                  class="matrix-cell"
                  :class="cell.level"
                  @click="showCellDetails(cell)"
                >
                  <span class="cell-count">{{ cell.count }}</span>
                </div>
              </div>
            </div>
            <div class="x-labels">
              <span>极低</span>
              <span>低</span>
              <span>中</span>
              <span>高</span>
              <span>极高</span>
            </div>
          </div>
          <div class="matrix-x-label">
            <span>攻击可行性</span>
          </div>
        </div>
        <div class="matrix-legend">
          <div class="legend-item">
            <div class="legend-color cal-1"></div>
            <span>CAL-1 (低风险)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color cal-2"></div>
            <span>CAL-2 (中风险)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color cal-3"></div>
            <span>CAL-3 (高风险)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color cal-4"></div>
            <span>CAL-4 (极高风险)</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载风险数据中...</p>
    </div>

    <div v-else-if="threats.length === 0" class="empty-container">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
      </div>
      <h3>暂无风险数据</h3>
      <p>使用一键生成报告功能自动进行风险评估</p>
      <router-link to="/generator" class="tara-btn tara-btn-primary">
        一键生成报告
      </router-link>
    </div>

    <div v-else class="risk-summary">
      <div class="summary-card cal-4">
        <div class="summary-value">{{ riskDistribution['CAL-4'] }}</div>
        <div class="summary-label">CAL-4 极高风险</div>
        <div class="summary-desc">需立即处理</div>
      </div>
      <div class="summary-card cal-3">
        <div class="summary-value">{{ riskDistribution['CAL-3'] }}</div>
        <div class="summary-label">CAL-3 高风险</div>
        <div class="summary-desc">优先处理</div>
      </div>
      <div class="summary-card cal-2">
        <div class="summary-value">{{ riskDistribution['CAL-2'] }}</div>
        <div class="summary-label">CAL-2 中风险</div>
        <div class="summary-desc">计划处理</div>
      </div>
      <div class="summary-card cal-1">
        <div class="summary-value">{{ riskDistribution['CAL-1'] }}</div>
        <div class="summary-label">CAL-1 低风险</div>
        <div class="summary-desc">可接受</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { threatApi, type Threat } from '@/api'

const loading = ref(true)
const threats = ref<Threat[]>([])

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

// Calculate risk distribution
const riskDistribution = computed(() => {
  const distribution = {
    'CAL-4': 0,
    'CAL-3': 0,
    'CAL-2': 0,
    'CAL-1': 0,
  }
  
  threats.value.forEach(threat => {
    const level = threat.risk_level as keyof typeof distribution
    if (level && level in distribution) {
      distribution[level]++
    } else {
      // Default to CAL-2 if no risk level
      distribution['CAL-2']++
    }
  })
  
  return distribution
})

// Generate matrix data based on threats
const matrixData = computed(() => {
  // Create a 5x5 matrix based on impact_level and likelihood
  const matrix: Array<Array<{ count: number; level: string }>> = []
  
  for (let i = 0; i < 5; i++) {
    const row: Array<{ count: number; level: string }> = []
    for (let j = 0; j < 5; j++) {
      const impactLevel = 5 - i  // 5=极高, 1=极低
      const likelihood = j + 1   // 1=极低, 5=极高
      
      // Count threats in this cell
      const count = threats.value.filter(t => {
        const tImpact = t.impact_level || 2
        const tLikelihood = t.likelihood || 2
        return Math.ceil(tImpact) === impactLevel && Math.ceil(tLikelihood) === likelihood
      }).length
      
      // Determine risk level based on position
      let level = 'cal-1'
      if (impactLevel >= 4 && likelihood >= 4) level = 'cal-4'
      else if (impactLevel >= 3 && likelihood >= 3) level = 'cal-3'
      else if (impactLevel >= 2 && likelihood >= 2) level = 'cal-2'
      
      row.push({ count, level })
    }
    matrix.push(row)
  }
  
  return matrix
})

const showCellDetails = (cell: any) => {
  console.log('Cell clicked:', cell)
}

onMounted(() => {
  loadThreats()
})
</script>

<style scoped>
.page-container {
  max-width: 1200px;
}

.page-header {
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

.risk-matrix-container {
  margin-bottom: 24px;
}

.matrix-wrapper {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.matrix-y-label {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}

.matrix-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.y-labels {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: absolute;
  left: -70px;
}

.y-labels span {
  height: 56px;
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}

.matrix-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 80px;
  position: relative;
}

.matrix-row {
  display: flex;
  gap: 4px;
}

.matrix-cell {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.matrix-cell:hover {
  transform: scale(1.1);
  z-index: 1;
}

.cell-count {
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.matrix-cell.cal-1 { background: rgba(16, 185, 129, 0.5); }
.matrix-cell.cal-2 { background: rgba(245, 158, 11, 0.6); }
.matrix-cell.cal-3 { background: rgba(239, 68, 68, 0.7); }
.matrix-cell.cal-4 { background: rgba(185, 28, 28, 0.85); }

.x-labels {
  display: flex;
  gap: 4px;
  margin-left: 80px;
  margin-top: 8px;
}

.x-labels span {
  width: 56px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
}

.matrix-x-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  margin-left: 80px;
  margin-top: 16px;
}

.matrix-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-muted);
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
}

.legend-color.cal-1 { background: rgba(16, 185, 129, 0.5); }
.legend-color.cal-2 { background: rgba(245, 158, 11, 0.6); }
.legend-color.cal-3 { background: rgba(239, 68, 68, 0.7); }
.legend-color.cal-4 { background: rgba(185, 28, 28, 0.85); }

.risk-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.summary-card {
  padding: 24px;
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  text-align: center;
  transition: all var(--transition-normal);
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.summary-value {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 8px;
}

.summary-card.cal-4 .summary-value { color: #F87171; }
.summary-card.cal-3 .summary-value { color: #FBBF24; }
.summary-card.cal-2 .summary-value { color: #60A5FA; }
.summary-card.cal-1 .summary-value { color: #34D399; }

.summary-label {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.summary-desc {
  font-size: 13px;
  color: var(--text-muted);
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
