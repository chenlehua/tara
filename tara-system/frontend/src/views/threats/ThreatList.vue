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
      
      <div class="threats-table">
        <table>
          <thead>
            <tr>
              <th>威胁ID</th>
              <th>威胁名称</th>
              <th>STRIDE类型</th>
              <th>目标资产</th>
              <th>风险等级</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="threat in filteredThreats" :key="threat.id">
              <td class="threat-id">{{ threat.id }}</td>
              <td class="threat-name">{{ threat.name }}</td>
              <td>
                <span class="stride-tag" :style="{ background: getStrideColor(threat.stride) }">
                  {{ threat.stride }}
                </span>
              </td>
              <td class="threat-asset">{{ threat.asset }}</td>
              <td>
                <span class="risk-badge" :class="threat.riskClass">
                  {{ threat.riskLevel }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="threat.statusClass">
                  {{ threat.status }}
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
import { ref, computed } from 'vue'

const selectedCategory = ref<string | null>(null)
const filterRisk = ref('')

const strideCategories = [
  { id: 'S', letter: 'S', name: 'Spoofing', count: 28, bgColor: 'rgba(59,130,246,0.12)', color: '#60A5FA' },
  { id: 'T', letter: 'T', name: 'Tampering', count: 24, bgColor: 'rgba(139,92,246,0.12)', color: '#A78BFA' },
  { id: 'R', letter: 'R', name: 'Repudiation', count: 12, bgColor: 'rgba(236,72,153,0.12)', color: '#F472B6' },
  { id: 'I', letter: 'I', name: 'Info Disclosure', count: 31, bgColor: 'rgba(245,158,11,0.12)', color: '#FBBF24' },
  { id: 'D', letter: 'D', name: 'Denial of Service', count: 18, bgColor: 'rgba(239,68,68,0.12)', color: '#F87171' },
  { id: 'E', letter: 'E', name: 'Elevation', count: 14, bgColor: 'rgba(16,185,129,0.12)', color: '#34D399' }
]

const threats = ref([
  { id: 'THR-001', name: 'CAN总线消息伪造攻击', stride: 'S', asset: 'CAN Bus', riskLevel: 'CAL-4', riskClass: 'critical', status: '已分析', statusClass: 'active' },
  { id: 'THR-002', name: 'ECU固件篡改', stride: 'T', asset: 'VCU', riskLevel: 'CAL-4', riskClass: 'critical', status: '分析中', statusClass: 'review' },
  { id: 'THR-003', name: '诊断数据窃取', stride: 'I', asset: 'OBD-II', riskLevel: 'CAL-3', riskClass: 'high', status: '已分析', statusClass: 'active' },
  { id: 'THR-004', name: 'DoS攻击导致CAN总线瘫痪', stride: 'D', asset: 'CAN Bus', riskLevel: 'CAL-4', riskClass: 'critical', status: '待处理', statusClass: 'draft' },
  { id: 'THR-005', name: 'T-Box远程控制劫持', stride: 'E', asset: 'T-Box', riskLevel: 'CAL-4', riskClass: 'critical', status: '已分析', statusClass: 'active' },
  { id: 'THR-006', name: '车载网络身份伪造', stride: 'S', asset: 'Gateway', riskLevel: 'CAL-3', riskClass: 'high', status: '分析中', statusClass: 'review' },
  { id: 'THR-007', name: '传感器数据注入', stride: 'T', asset: 'ADAS Sensor', riskLevel: 'CAL-4', riskClass: 'critical', status: '待处理', statusClass: 'draft' },
  { id: 'THR-008', name: '用户隐私数据泄露', stride: 'I', asset: 'IVI System', riskLevel: 'CAL-2', riskClass: 'medium', status: '已分析', statusClass: 'active' }
])

const filteredThreats = computed(() => {
  return threats.value.filter(threat => {
    const matchesCategory = !selectedCategory.value || threat.stride === selectedCategory.value
    const matchesRisk = !filterRisk.value || threat.riskClass === filterRisk.value
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
</style>
