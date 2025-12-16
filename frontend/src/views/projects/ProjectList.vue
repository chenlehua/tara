<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>项目管理</h1>
        <p class="page-subtitle">管理和跟踪TARA安全分析项目</p>
      </div>
      <button class="tara-btn tara-btn-primary" @click="showCreateModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        新建项目
      </button>
    </div>

    <div class="projects-grid">
      <div 
        v-for="project in projects" 
        :key="project.id"
        class="project-card tara-card"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <div class="project-card-header">
          <div class="project-icon" :class="project.iconClass">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 16H9m10 0h3v-3.15a1 1 0 00-.84-.99L16 11l-2.7-3.6a1 1 0 00-.8-.4H5.24a2 2 0 00-1.8 1.1l-.8 1.63A6 6 0 002 12.42V16h2"/>
              <circle cx="6.5" cy="16.5" r="2.5"/>
              <circle cx="16.5" cy="16.5" r="2.5"/>
            </svg>
          </div>
          <span class="status-badge" :class="project.statusClass">{{ project.status }}</span>
        </div>
        
        <h3 class="project-name">{{ project.name }}</h3>
        <p class="project-desc">{{ project.description }}</p>
        
        <div class="project-stats">
          <div class="stat">
            <span class="stat-value">{{ project.assets }}</span>
            <span class="stat-label">资产</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ project.threats }}</span>
            <span class="stat-label">威胁</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ project.risks }}</span>
            <span class="stat-label">高风险</span>
          </div>
        </div>
        
        <div class="progress-bar" style="margin-top: 16px;">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
          </div>
          <span class="progress-text">{{ project.progress }}%</span>
        </div>
        
        <div class="project-footer">
          <span class="deadline">截止: {{ project.deadline }}</span>
          <div class="avatars">
            <div v-for="(member, i) in project.members.slice(0, 3)" :key="i" class="avatar">
              {{ member.charAt(0) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showCreateModal = ref(false)

const projects = ref([
  {
    id: '1',
    name: 'MY25 EV平台',
    description: '新能源汽车整车网络安全TARA分析',
    assets: 48,
    threats: 127,
    risks: 23,
    status: '进行中',
    statusClass: 'active',
    progress: 68,
    deadline: '2025-03-15',
    iconClass: 'blue',
    members: ['张', '李', '王', '赵']
  },
  {
    id: '2',
    name: 'ADAS L3系统',
    description: '高级驾驶辅助系统安全分析',
    assets: 32,
    threats: 85,
    risks: 12,
    status: '审核中',
    statusClass: 'review',
    progress: 92,
    deadline: '2025-02-28',
    iconClass: 'purple',
    members: ['李', '王']
  },
  {
    id: '3',
    name: '智能座舱2.0',
    description: '车载信息娱乐系统安全分析',
    assets: 21,
    threats: 43,
    risks: 8,
    status: '草稿',
    statusClass: 'draft',
    progress: 25,
    deadline: '2025-04-30',
    iconClass: 'cyan',
    members: ['张', '赵', '钱']
  }
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

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-subtitle {
  color: var(--text-muted);
  font-size: 15px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.project-card {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.project-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-icon svg {
  width: 24px;
  height: 24px;
}

.project-icon.blue { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.project-icon.purple { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }
.project-icon.cyan { background: rgba(6, 182, 212, 0.15); color: #22D3EE; }

.project-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.project-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
  line-height: 1.5;
}

.project-stats {
  display: flex;
  gap: 24px;
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

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.deadline {
  font-size: 13px;
  color: var(--text-muted);
}

.avatars {
  display: flex;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-blue), var(--brand-purple));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  border: 2px solid var(--bg-secondary);
  margin-left: -8px;
}

.avatar:first-child {
  margin-left: 0;
}
</style>
