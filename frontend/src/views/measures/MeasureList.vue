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

    <div class="measures-grid">
      <div 
        v-for="measure in measures" 
        :key="measure.id"
        class="measure-card tara-card"
      >
        <div class="measure-header">
          <div class="measure-icon" :class="measure.categoryClass">
            <component :is="measure.icon" />
          </div>
          <span class="status-badge" :class="measure.statusClass">{{ measure.status }}</span>
        </div>
        
        <h3 class="measure-name">{{ measure.name }}</h3>
        <p class="measure-desc">{{ measure.description }}</p>
        
        <div class="measure-meta">
          <div class="meta-item">
            <span class="meta-label">类型</span>
            <span class="meta-value">{{ measure.category }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">覆盖威胁</span>
            <span class="meta-value">{{ measure.threatsCount }} 项</span>
          </div>
        </div>
        
        <div class="measure-footer">
          <div class="effectiveness">
            <span>有效性</span>
            <div class="effectiveness-bar">
              <div class="effectiveness-fill" :style="{ width: measure.effectiveness + '%' }"></div>
            </div>
            <span class="effectiveness-value">{{ measure.effectiveness }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Icons
const IconLock = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`
}
const IconKey = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`
}
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}
const IconEye = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
}
const IconRefresh = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>`
}

const measures = ref([
  { id: '1', name: 'SecOC消息认证', description: '使用安全车载通信协议对CAN消息进行认证，防止消息伪造攻击', category: '加密', categoryClass: 'blue', icon: IconLock, status: '已实施', statusClass: 'active', threatsCount: 12, effectiveness: 95 },
  { id: '2', name: '安全启动', description: '验证ECU固件完整性，确保只有经过认证的固件才能运行', category: '完整性', categoryClass: 'purple', icon: IconShield, status: '已实施', statusClass: 'active', threatsCount: 8, effectiveness: 90 },
  { id: '3', name: 'HSM硬件安全模块', description: '使用专用硬件进行密钥存储和加密运算', category: '加密', categoryClass: 'blue', icon: IconKey, status: '已实施', statusClass: 'active', threatsCount: 15, effectiveness: 98 },
  { id: '4', name: '入侵检测系统', description: '实时监控车载网络异常行为，检测潜在攻击', category: '检测', categoryClass: 'orange', icon: IconEye, status: '部署中', statusClass: 'review', threatsCount: 20, effectiveness: 75 },
  { id: '5', name: 'OTA安全更新', description: '支持安全的远程固件更新，修复已知漏洞', category: '更新', categoryClass: 'green', icon: IconRefresh, status: '规划中', statusClass: 'draft', threatsCount: 10, effectiveness: 85 },
  { id: '6', name: '网络分段隔离', description: '将车载网络划分为不同安全域，限制攻击横向移动', category: '隔离', categoryClass: 'cyan', icon: IconShield, status: '已实施', statusClass: 'active', threatsCount: 18, effectiveness: 88 }
])
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
</style>
