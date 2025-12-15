<template>
  <div class="dashboard animate-fadeIn">
    <!-- Welcome Banner -->
    <div class="welcome-banner">
      <div class="glow"></div>
      <div class="pattern"></div>
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，<span>{{ userName }}</span> 👋</h2>
          <p>您有 {{ activeProjects }} 个项目正在进行中，{{ highRiskCount }} 个高风险威胁待处理</p>
          <div class="welcome-meta">
            <div class="welcome-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
              </svg>
              当前项目：{{ currentProject }}
            </div>
            <div class="welcome-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              上次保存：{{ lastSaved }}
            </div>
          </div>
        </div>
        <div class="welcome-actions">
          <button class="tara-btn tara-btn-primary" @click="continueAnalysis">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M5 3l14 9-14 9V3z"/>
            </svg>
            继续分析
          </button>
          <button class="tara-btn tara-btn-secondary" @click="viewReport">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            查看报告
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div 
        v-for="stat in stats" 
        :key="stat.label" 
        class="stat-card"
        :style="{ '--stat-color': stat.statColor }"
        @click="navigateToStat(stat.path)"
      >
        <div class="stat-header">
          <div class="stat-icon" :class="stat.iconClass">
            <component :is="stat.icon" />
          </div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            <svg v-if="stat.trend > 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 6l-9.5 9.5-5-5L1 18"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 18l-9.5-9.5-5 5L1 6"/>
            </svg>
            {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}{{ stat.trendUnit || '' }}
          </div>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="main-grid">
      <!-- Projects Card -->
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">
            <div class="tara-card-title-icon blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
              </svg>
            </div>
            项目进度
          </h3>
          <span class="card-action" @click="$router.push('/projects')">
            查看全部
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </span>
        </div>
        <div class="project-list">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="project-item"
            :class="{ selected: project.id === selectedProject }"
            @click="selectProject(project.id)"
          >
            <div class="project-header">
              <div class="project-info">
                <div class="project-icon" :class="project.iconClass">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 16H9m10 0h3v-3.15a1 1 0 00-.84-.99L16 11l-2.7-3.6a1 1 0 00-.8-.4H5.24a2 2 0 00-1.8 1.1l-.8 1.63A6 6 0 002 12.42V16h2"/>
                    <circle cx="6.5" cy="16.5" r="2.5"/>
                    <circle cx="16.5" cy="16.5" r="2.5"/>
                  </svg>
                </div>
                <div>
                  <div class="project-name">{{ project.name }}</div>
                  <div class="project-meta">
                    <span>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="4" y="4" width="16" height="16" rx="2"/>
                      </svg>
                      {{ project.assets }} 资产
                    </span>
                    <span>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                      </svg>
                      {{ project.threats }} 威胁
                    </span>
                  </div>
                </div>
              </div>
              <span class="status-badge" :class="project.statusClass">{{ project.status }}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ project.progress }}%</span>
            </div>
            <div class="project-footer">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <path d="M16 2v4M8 2v4M3 10h18"/>
              </svg>
              截止：{{ project.deadline }}
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Card -->
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">
            <div class="tara-card-title-icon purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            最近活动
          </h3>
        </div>
        <div class="activity-list">
          <div 
            v-for="activity in activities" 
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon" :class="activity.iconClass">
              <component :is="activity.icon" />
            </div>
            <div class="activity-content">
              <div class="activity-action">{{ activity.action }}</div>
              <div class="activity-target">{{ activity.target }}</div>
              <div class="activity-time">{{ activity.user }} · {{ activity.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <!-- Heatmap -->
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">
            <div class="tara-card-title-icon red">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            风险热力图
          </h3>
          <span style="font-size: 12px; color: var(--text-muted);">影响度 × 可行性</span>
        </div>
        <div class="heatmap-container">
          <div class="heatmap-labels">
            <span>极高</span>
            <span>高</span>
            <span>中</span>
            <span>低</span>
            <span>极低</span>
          </div>
          <div class="heatmap-grid">
            <div class="heatmap-cells">
              <div 
                v-for="(cell, index) in heatmapData" 
                :key="index"
                class="heatmap-cell"
                :class="'level-' + cell.level"
                @click="showCellDetails(cell)"
              >
                {{ cell.value || '' }}
              </div>
            </div>
            <div class="heatmap-x-labels">
              <span>极低</span>
              <span>低</span>
              <span>中</span>
              <span>高</span>
              <span>极高</span>
            </div>
          </div>
        </div>
        <div class="heatmap-legend">
          <div class="legend-item">
            <div class="legend-dot" style="background: rgba(16,185,129,0.5)"></div>
            <span>低风险</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: rgba(245,158,11,0.6)"></div>
            <span>中风险</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: rgba(239,68,68,0.7)"></div>
            <span>高风险</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background: rgba(185,28,28,0.85)"></div>
            <span>极高风险</span>
          </div>
        </div>
      </div>

      <!-- STRIDE -->
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">
            <div class="tara-card-title-icon orange">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="6"/>
                <circle cx="12" cy="12" r="2"/>
              </svg>
            </div>
            威胁分布 (STRIDE)
          </h3>
        </div>
        <div class="stride-list">
          <div 
            v-for="item in strideData" 
            :key="item.label"
            class="stride-item"
          >
            <span class="stride-label">{{ item.label }}</span>
            <div class="stride-bar-container">
              <div 
                class="stride-bar" 
                :style="{ width: item.percent + '%', background: item.color }"
              >
                {{ item.count }}
              </div>
            </div>
            <span class="stride-percent">{{ item.percent }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// Icons
const IconThreat = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`
}
const IconMeasure = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}
const IconRisk = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
}
const IconAsset = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>`
}
const IconReport = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>`
}
const IconCpu = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg>`
}

// Data
const userName = computed(() => userStore.user?.username || '张工程师')
const activeProjects = ref(3)
const highRiskCount = ref(23)
const currentProject = ref('MY25 EV平台')
const lastSaved = ref('10分钟前')
const selectedProject = ref('1')

const stats = ref([
  {
    label: '已识别资产',
    value: 48,
    trend: 5,
    icon: IconCpu,
    iconClass: 'blue',
    statColor: '#3B82F6',
    path: '/assets'
  },
  {
    label: '威胁场景',
    value: 127,
    trend: 12,
    icon: IconThreat,
    iconClass: 'orange',
    statColor: '#F59E0B',
    path: '/threats'
  },
  {
    label: '高风险项',
    value: 23,
    trend: -3,
    icon: IconRisk,
    iconClass: 'red',
    statColor: '#EF4444',
    path: '/risks'
  },
  {
    label: '缓解率',
    value: '89%',
    trend: 8,
    trendUnit: '%',
    icon: IconMeasure,
    iconClass: 'green',
    statColor: '#10B981',
    path: '/measures'
  }
])

const projects = ref([
  {
    id: '1',
    name: 'MY25 EV平台',
    assets: 48,
    threats: 127,
    status: '进行中',
    statusClass: 'active',
    progress: 68,
    deadline: '2025-03-15',
    iconClass: 'blue'
  },
  {
    id: '2',
    name: 'ADAS L3系统',
    assets: 32,
    threats: 85,
    status: '审核中',
    statusClass: 'review',
    progress: 92,
    deadline: '2025-02-28',
    iconClass: 'purple'
  },
  {
    id: '3',
    name: '智能座舱2.0',
    assets: 21,
    threats: 43,
    status: '草稿',
    statusClass: 'draft',
    progress: 25,
    deadline: '2025-04-30',
    iconClass: 'cyan'
  }
])

const activities = ref([
  { id: 1, action: '完成威胁分析', target: 'CAN总线消息伪造攻击', user: '张工程师', time: '10分钟前', icon: IconThreat, iconClass: 'threat' },
  { id: 2, action: '添加安全措施', target: '消息认证机制(SecOC)', user: '李分析师', time: '25分钟前', icon: IconMeasure, iconClass: 'measure' },
  { id: 3, action: '更新风险评级', target: 'T-Box通信模块 → CAL-4', user: '张工程师', time: '1小时前', icon: IconRisk, iconClass: 'risk' },
  { id: 4, action: '导入资产清单', target: 'ADAS子系统 (14个ECU)', user: '王经理', time: '2小时前', icon: IconAsset, iconClass: 'asset' },
  { id: 5, action: '生成TARA报告', target: 'MY25 EV平台 v1.2', user: '系统', time: '3小时前', icon: IconReport, iconClass: 'report' }
])

const heatmapData = ref([
  { level: 0, value: null }, { level: 1, value: 1 }, { level: 1, value: 2 }, { level: 1, value: 1 }, { level: 0, value: null },
  { level: 1, value: 1 }, { level: 2, value: 3 }, { level: 3, value: 4 }, { level: 2, value: 2 }, { level: 1, value: 1 },
  { level: 2, value: 2 }, { level: 3, value: 5 }, { level: 4, value: 8 }, { level: 3, value: 3 }, { level: 1, value: 1 },
  { level: 1, value: 1 }, { level: 2, value: 3 }, { level: 3, value: 4 }, { level: 2, value: 2 }, { level: 0, value: null },
  { level: 0, value: null }, { level: 1, value: 1 }, { level: 1, value: 1 }, { level: 0, value: null }, { level: 0, value: null }
])

const strideData = ref([
  { label: 'Spoofing', count: 28, percent: 22, color: '#3B82F6' },
  { label: 'Tampering', count: 24, percent: 19, color: '#8B5CF6' },
  { label: 'Repudiation', count: 12, percent: 9, color: '#EC4899' },
  { label: 'Disclosure', count: 31, percent: 24, color: '#F59E0B' },
  { label: 'DoS', count: 18, percent: 14, color: '#EF4444' },
  { label: 'Elevation', count: 14, percent: 11, color: '#10B981' }
])

// Methods
const continueAnalysis = () => {
  router.push(`/projects/${selectedProject.value}`)
}

const viewReport = () => {
  router.push('/reports')
}

const navigateToStat = (path: string) => {
  router.push(path)
}

const selectProject = (id: string) => {
  selectedProject.value = id
}

const showCellDetails = (cell: any) => {
  if (cell.value) {
    console.log('Cell clicked:', cell)
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Welcome Banner */
.welcome-banner {
  position: relative;
  padding: 32px 36px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.welcome-banner .glow {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
  filter: blur(60px);
}

.welcome-banner .pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.welcome-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-text h2 span {
  background: linear-gradient(135deg, #60A5FA, #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-text p {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.welcome-meta {
  display: flex;
  gap: 24px;
}

.welcome-meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.welcome-meta-item svg {
  width: 16px;
  height: 16px;
  color: var(--text-disabled);
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  padding: 24px;
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--stat-color), transparent);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-normal);
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}

.stat-icon svg {
  width: 26px;
  height: 26px;
}

.stat-icon.blue { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.stat-icon.orange { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
.stat-icon.red { background: rgba(239, 68, 68, 0.12); color: #F87171; }
.stat-icon.green { background: rgba(16, 185, 129, 0.12); color: #34D399; }

.stat-trend {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up { background: rgba(16, 185, 129, 0.12); color: #34D399; }
.stat-trend.down { background: rgba(239, 68, 68, 0.12); color: #F87171; }

.stat-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 4px;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

/* Card Action */
.card-action {
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color var(--transition-fast);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
}

.card-action:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.card-action svg {
  width: 14px;
  height: 14px;
}

/* Project List */
.project-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-item {
  padding: 18px 20px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.project-item:hover {
  background: var(--bg-hover);
}

.project-item.selected {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.project-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-icon svg {
  width: 22px;
  height: 22px;
}

.project-icon.blue { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.project-icon.purple { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }
.project-icon.cyan { background: rgba(6, 182, 212, 0.15); color: #22D3EE; }

.project-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.project-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.project-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.project-meta svg {
  width: 13px;
  height: 13px;
}

.project-footer {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}

.project-footer svg {
  width: 13px;
  height: 13px;
  margin-right: 5px;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-item {
  display: flex;
  gap: 14px;
  padding: 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.activity-item:hover {
  background: var(--bg-hover);
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon svg {
  width: 16px;
  height: 16px;
}

.activity-icon.threat { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
.activity-icon.measure { background: rgba(16, 185, 129, 0.12); color: #34D399; }
.activity-icon.risk { background: rgba(239, 68, 68, 0.12); color: #F87171; }
.activity-icon.asset { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.activity-icon.report { background: rgba(139, 92, 246, 0.12); color: #A78BFA; }

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-action {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.activity-target {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-time {
  font-size: 11px;
  color: var(--text-disabled);
  margin-top: 4px;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* Risk Heatmap */
.heatmap-container {
  display: flex;
  gap: 16px;
}

.heatmap-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4px 0;
}

.heatmap-labels span {
  height: 40px;
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}

.heatmap-grid {
  flex: 1;
}

.heatmap-cells {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.heatmap-cell {
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.heatmap-cell:hover {
  transform: scale(1.08);
  z-index: 1;
}

.heatmap-cell.level-0 { background: rgba(30, 41, 59, 0.6); color: transparent; }
.heatmap-cell.level-1 { background: rgba(16, 185, 129, 0.5); }
.heatmap-cell.level-2 { background: rgba(245, 158, 11, 0.6); }
.heatmap-cell.level-3 { background: rgba(239, 68, 68, 0.7); }
.heatmap-cell.level-4 { background: rgba(185, 28, 28, 0.85); }

.heatmap-x-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.heatmap-x-labels span {
  font-size: 12px;
  color: var(--text-muted);
}

.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.legend-dot {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-sm);
}

/* STRIDE Chart */
.stride-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.stride-item {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.stride-item:hover .stride-label {
  color: var(--text-primary);
}

.stride-label {
  width: 90px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color var(--transition-fast);
}

.stride-bar-container {
  flex: 1;
  height: 28px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  overflow: hidden;
}

.stride-bar {
  height: 100%;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  padding-left: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  transition: all 0.6s ease;
}

.stride-item:hover .stride-bar {
  filter: brightness(1.1);
}

.stride-percent {
  width: 50px;
  text-align: right;
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

/* Responsive */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
}
</style>
