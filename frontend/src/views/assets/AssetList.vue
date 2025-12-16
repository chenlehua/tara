<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>资产识别</h1>
        <p class="page-subtitle">管理和分析汽车网络安全资产</p>
      </div>
      <div class="header-actions">
        <button class="tara-btn tara-btn-secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
          </svg>
          导入资产
        </button>
        <button class="tara-btn tara-btn-primary" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          添加资产
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="search-input">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input type="text" placeholder="搜索资产..." v-model="searchQuery">
      </div>
      <div class="filter-group">
        <select v-model="filterType">
          <option value="">全部类型</option>
          <option value="ECU">ECU</option>
          <option value="Sensor">传感器</option>
          <option value="Gateway">网关</option>
          <option value="Interface">接口</option>
        </select>
        <select v-model="filterSecurityLevel">
          <option value="">全部安全等级</option>
          <option value="CAL-4">CAL-4 (极高)</option>
          <option value="CAL-3">CAL-3 (高)</option>
          <option value="CAL-2">CAL-2 (中)</option>
          <option value="CAL-1">CAL-1 (低)</option>
        </select>
      </div>
    </div>

    <div class="assets-grid">
      <div 
        v-for="asset in filteredAssets" 
        :key="asset.id"
        class="asset-card tara-card"
        @click="selectedAsset = asset"
      >
        <div class="asset-header">
          <div class="asset-icon" :class="asset.iconClass">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <rect x="9" y="9" width="6" height="6"/>
              <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
            </svg>
          </div>
          <span class="security-badge" :class="asset.securityClass">{{ asset.securityLevel }}</span>
        </div>
        <h3 class="asset-name">{{ asset.name }}</h3>
        <p class="asset-type">{{ asset.type }}</p>
        <div class="asset-interfaces">
          <span v-for="iface in asset.interfaces" :key="iface" class="interface-tag">
            {{ iface }}
          </span>
        </div>
        <div class="asset-stats">
          <div class="stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
            <span>{{ asset.threats }} 威胁</span>
          </div>
          <div class="stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="18" cy="18" r="3"/>
              <circle cx="6" cy="6" r="3"/>
              <path d="M6 21V9a9 9 0 009 9"/>
            </svg>
            <span>{{ asset.connections }} 连接</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Asset interface
interface Asset {
  id: string
  name: string
  type: string
  securityLevel: string
  securityClass: string
  iconClass: string
  interfaces: string[]
  threats: number
  connections: number
}

const showCreateModal = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const filterSecurityLevel = ref('')
const selectedAsset = ref<Asset | null>(null)

const assets = ref<Asset[]>([
  { id: '1', name: 'VCU (整车控制器)', type: 'ECU', securityLevel: 'CAL-4', securityClass: 'critical', iconClass: 'red', interfaces: ['CAN', 'Ethernet'], threats: 12, connections: 8 },
  { id: '2', name: 'BMS (电池管理系统)', type: 'ECU', securityLevel: 'CAL-4', securityClass: 'critical', iconClass: 'red', interfaces: ['CAN'], threats: 8, connections: 5 },
  { id: '3', name: 'MCU (电机控制器)', type: 'ECU', securityLevel: 'CAL-3', securityClass: 'high', iconClass: 'orange', interfaces: ['CAN'], threats: 6, connections: 4 },
  { id: '4', name: 'T-Box', type: 'Gateway', securityLevel: 'CAL-4', securityClass: 'critical', iconClass: 'red', interfaces: ['4G/5G', 'CAN', 'Ethernet'], threats: 15, connections: 12 },
  { id: '5', name: 'Central Gateway', type: 'Gateway', securityLevel: 'CAL-4', securityClass: 'critical', iconClass: 'red', interfaces: ['CAN', 'LIN', 'Ethernet'], threats: 10, connections: 15 },
  { id: '6', name: 'ADAS Controller', type: 'ECU', securityLevel: 'CAL-4', securityClass: 'critical', iconClass: 'red', interfaces: ['CAN', 'Ethernet'], threats: 18, connections: 9 },
  { id: '7', name: 'Camera Module', type: 'Sensor', securityLevel: 'CAL-3', securityClass: 'high', iconClass: 'orange', interfaces: ['Ethernet'], threats: 4, connections: 2 },
  { id: '8', name: 'Radar Sensor', type: 'Sensor', securityLevel: 'CAL-3', securityClass: 'high', iconClass: 'orange', interfaces: ['CAN'], threats: 3, connections: 1 },
  { id: '9', name: 'OBD-II Port', type: 'Interface', securityLevel: 'CAL-3', securityClass: 'high', iconClass: 'orange', interfaces: ['CAN'], threats: 7, connections: 1 },
  { id: '10', name: 'IVI System', type: 'ECU', securityLevel: 'CAL-2', securityClass: 'medium', iconClass: 'blue', interfaces: ['CAN', 'Ethernet', 'USB'], threats: 9, connections: 6 },
])

const filteredAssets = computed(() => {
  return assets.value.filter(asset => {
    const matchesSearch = !searchQuery.value || 
      asset.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesType = !filterType.value || asset.type === filterType.value
    const matchesSecurity = !filterSecurityLevel.value || asset.securityLevel === filterSecurityLevel.value
    return matchesSearch && matchesType && matchesSecurity
  })
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

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-input {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input svg {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.search-input input {
  width: 100%;
  height: 42px;
  padding: 0 16px 0 42px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
}

.search-input input:focus {
  border-color: var(--border-focus);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-group select {
  height: 42px;
  padding: 0 32px 0 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.asset-card {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.asset-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.asset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.asset-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-icon svg {
  width: 22px;
  height: 22px;
}

.asset-icon.red { background: rgba(239, 68, 68, 0.12); color: #F87171; }
.asset-icon.orange { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
.asset-icon.blue { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.asset-icon.green { background: rgba(16, 185, 129, 0.12); color: #34D399; }

.security-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.security-badge.critical { background: rgba(185, 28, 28, 0.15); color: #F87171; }
.security-badge.high { background: rgba(245, 158, 11, 0.15); color: #FBBF24; }
.security-badge.medium { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.security-badge.low { background: rgba(16, 185, 129, 0.15); color: #34D399; }

.asset-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.asset-type {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.asset-interfaces {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.interface-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.asset-stats {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.asset-stats .stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.asset-stats .stat svg {
  width: 14px;
  height: 14px;
}
</style>
