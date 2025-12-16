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

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载资产中...</p>
    </div>

    <div v-else-if="filteredAssets.length === 0" class="empty-container">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="4" y="4" width="16" height="16" rx="2"/>
          <rect x="9" y="9" width="6" height="6"/>
          <path d="M9 1v3M15 1v3M9 20v3M15 20v3"/>
        </svg>
      </div>
      <h3>暂无资产</h3>
      <p>使用一键生成报告功能自动识别资产</p>
      <router-link to="/generator" class="tara-btn tara-btn-primary">
        一键生成报告
      </router-link>
    </div>

    <div v-else class="assets-grid">
      <div 
        v-for="asset in filteredAssets" 
        :key="asset.id"
        class="asset-card tara-card"
        @click="selectedAsset = asset"
      >
        <div class="asset-header">
          <div class="asset-icon" :class="getIconClass(asset)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <rect x="9" y="9" width="6" height="6"/>
              <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
            </svg>
          </div>
          <span class="security-badge" :class="getSecurityClass(asset)">{{ getSecurityLevel(asset) }}</span>
        </div>
        <h3 class="asset-name">{{ asset.name }}</h3>
        <p class="asset-type">{{ asset.asset_type }}</p>
        <div class="asset-interfaces">
          <span v-for="iface in getInterfaces(asset)" :key="iface" class="interface-tag">
            {{ iface }}
          </span>
        </div>
        <div class="asset-meta">
          <span class="meta-item">项目 #{{ asset.project_id }}</span>
          <span class="meta-item">{{ asset.source || '系统生成' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { assetApi, type Asset } from '@/api'

const showCreateModal = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const filterSecurityLevel = ref('')
const selectedAsset = ref<Asset | null>(null)
const loading = ref(true)
const assets = ref<Asset[]>([])

const loadAssets = async () => {
  loading.value = true
  try {
    const response = await assetApi.list({
      page: 1,
      page_size: 100,
    })
    if (response.success && response.data) {
      assets.value = response.data.items || []
    }
  } catch (error) {
    console.error('Failed to load assets:', error)
    // Fallback to demo data
    assets.value = [
      { id: 1, project_id: 1, name: 'VCU (整车控制器)', asset_type: 'ECU', criticality: 'critical', interfaces: [{ type: 'CAN' }, { type: 'Ethernet' }], created_at: '', updated_at: '' },
      { id: 2, project_id: 1, name: 'BMS (电池管理系统)', asset_type: 'ECU', criticality: 'critical', interfaces: [{ type: 'CAN' }], created_at: '', updated_at: '' },
      { id: 3, project_id: 1, name: 'MCU (电机控制器)', asset_type: 'ECU', criticality: 'high', interfaces: [{ type: 'CAN' }], created_at: '', updated_at: '' },
      { id: 4, project_id: 1, name: 'T-Box', asset_type: 'Gateway', criticality: 'critical', interfaces: [{ type: '4G/5G' }, { type: 'CAN' }, { type: 'Ethernet' }], created_at: '', updated_at: '' },
      { id: 5, project_id: 1, name: 'Central Gateway', asset_type: 'Gateway', criticality: 'critical', interfaces: [{ type: 'CAN' }, { type: 'LIN' }, { type: 'Ethernet' }], created_at: '', updated_at: '' },
    ]
  } finally {
    loading.value = false
  }
}

const getSecurityLevel = (asset: Asset): string => {
  const criticality = asset.criticality?.toLowerCase() || 'medium'
  const map: Record<string, string> = {
    'critical': 'CAL-4',
    'high': 'CAL-3',
    'medium': 'CAL-2',
    'low': 'CAL-1',
  }
  return map[criticality] || 'CAL-2'
}

const getSecurityClass = (asset: Asset): string => {
  const criticality = asset.criticality?.toLowerCase() || 'medium'
  return criticality
}

const getIconClass = (asset: Asset): string => {
  const criticality = asset.criticality?.toLowerCase() || 'medium'
  const map: Record<string, string> = {
    'critical': 'red',
    'high': 'orange',
    'medium': 'blue',
    'low': 'green',
  }
  return map[criticality] || 'blue'
}

const getInterfaces = (asset: Asset): string[] => {
  if (!asset.interfaces) return []
  return asset.interfaces.map(i => typeof i === 'string' ? i : (i.type || ''))
}

const filteredAssets = computed(() => {
  return assets.value.filter(asset => {
    const matchesSearch = !searchQuery.value || 
      asset.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesType = !filterType.value || asset.asset_type === filterType.value
    const matchesSecurity = !filterSecurityLevel.value || getSecurityLevel(asset) === filterSecurityLevel.value
    return matchesSearch && matchesType && matchesSecurity
  })
})

onMounted(() => {
  loadAssets()
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

.asset-meta {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.meta-item {
  font-size: 12px;
  color: var(--text-muted);
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
