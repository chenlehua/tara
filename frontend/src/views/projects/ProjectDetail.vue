<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <router-link to="/projects">项目管理</router-link>
          <span>/</span>
          <span>{{ project.name }}</span>
        </div>
        <h1>{{ project.name }}</h1>
        <p class="page-subtitle">{{ project.description }}</p>
      </div>
      <div class="header-actions">
        <button class="tara-btn tara-btn-secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          编辑
        </button>
        <button class="tara-btn tara-btn-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
            <path d="M14 2v6h6"/>
          </svg>
          生成报告
        </button>
      </div>
    </div>

    <div class="detail-grid">
      <!-- Overview Stats -->
      <div class="stats-row">
        <div class="mini-stat">
          <div class="mini-stat-icon blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <rect x="9" y="9" width="6" height="6"/>
            </svg>
          </div>
          <div>
            <div class="mini-stat-value">{{ project.assets }}</div>
            <div class="mini-stat-label">已识别资产</div>
          </div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            </svg>
          </div>
          <div>
            <div class="mini-stat-value">{{ project.threats }}</div>
            <div class="mini-stat-label">威胁场景</div>
          </div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-icon red">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div>
            <div class="mini-stat-value">{{ project.highRisks }}</div>
            <div class="mini-stat-label">高风险项</div>
          </div>
        </div>
        <div class="mini-stat">
          <div class="mini-stat-icon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <div class="mini-stat-value">{{ project.measures }}</div>
            <div class="mini-stat-label">安全措施</div>
          </div>
        </div>
      </div>

      <!-- Progress -->
      <div class="tara-card">
        <div class="tara-card-header">
          <h3 class="tara-card-title">分析进度</h3>
          <span class="status-badge" :class="project.statusClass">{{ project.status }}</span>
        </div>
        <div class="progress-steps">
          <div v-for="step in analysisSteps" :key="step.id" class="progress-step" :class="step.status">
            <div class="step-icon">
              <svg v-if="step.status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              <span v-else>{{ step.id }}</span>
            </div>
            <div class="step-info">
              <div class="step-name">{{ step.name }}</div>
              <div class="step-desc">{{ step.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const project = ref({
  id: route.params.id,
  name: 'MY25 EV平台',
  description: '新能源汽车整车网络安全TARA分析',
  assets: 48,
  threats: 127,
  highRisks: 23,
  measures: 89,
  status: '进行中',
  statusClass: 'active',
  progress: 68
})

const analysisSteps = ref([
  { id: 1, name: '资产识别', desc: '识别所有ECU和通信接口', status: 'completed' },
  { id: 2, name: '威胁分析', desc: 'STRIDE威胁建模', status: 'completed' },
  { id: 3, name: '风险评估', desc: 'CAL等级计算', status: 'active' },
  { id: 4, name: '措施建议', desc: '安全控制措施', status: 'pending' },
  { id: 5, name: '报告生成', desc: '生成TARA报告', status: 'pending' }
])
</script>

<style scoped>
.page-container {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.breadcrumb a {
  color: var(--text-muted);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--text-primary);
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

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
}

.mini-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-stat-icon svg {
  width: 24px;
  height: 24px;
}

.mini-stat-icon.blue { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
.mini-stat-icon.orange { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
.mini-stat-icon.red { background: rgba(239, 68, 68, 0.12); color: #F87171; }
.mini-stat-icon.green { background: rgba(16, 185, 129, 0.12); color: #34D399; }

.mini-stat-value {
  font-size: 24px;
  font-weight: 700;
}

.mini-stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

.progress-steps {
  display: flex;
  gap: 16px;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.02);
  transition: all var(--transition-normal);
}

.progress-step.active {
  background: rgba(59, 130, 246, 0.1);
}

.progress-step.completed {
  background: rgba(16, 185, 129, 0.08);
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-bottom: 12px;
  background: var(--bg-hover);
  color: var(--text-muted);
}

.progress-step.active .step-icon {
  background: var(--brand-blue);
  color: white;
}

.progress-step.completed .step-icon {
  background: var(--success);
  color: white;
}

.progress-step.completed .step-icon svg {
  width: 20px;
  height: 20px;
}

.step-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
