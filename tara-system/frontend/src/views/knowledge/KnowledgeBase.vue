<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>知识库</h1>
        <p class="page-subtitle">汽车网络安全威胁情报与最佳实践</p>
      </div>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input type="text" placeholder="搜索知识库..." v-model="searchQuery">
      </div>
    </div>

    <div class="category-tabs">
      <button 
        v-for="cat in categories" 
        :key="cat.id"
        class="category-tab"
        :class="{ active: selectedCategory === cat.id }"
        @click="selectedCategory = cat.id"
      >
        <component :is="cat.icon" />
        <span>{{ cat.name }}</span>
        <span class="count">{{ cat.count }}</span>
      </button>
    </div>

    <div class="knowledge-grid">
      <div 
        v-for="item in filteredItems" 
        :key="item.id"
        class="knowledge-card tara-card"
        @click="openItem(item)"
      >
        <div class="card-category" :class="item.categoryClass">
          {{ item.category }}
        </div>
        <h3 class="card-title">{{ item.title }}</h3>
        <p class="card-desc">{{ item.description }}</p>
        <div class="card-meta">
          <span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            {{ item.date }}
          </span>
          <span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            {{ item.views }}
          </span>
        </div>
        <div class="card-tags">
          <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Icons
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}
const IconWarning = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`
}
const IconBook = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>`
}
const IconFile = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>`
}

const searchQuery = ref('')
const selectedCategory = ref('all')

const categories = [
  { id: 'all', name: '全部', count: 156, icon: IconBook },
  { id: 'threats', name: '威胁情报', count: 48, icon: IconWarning },
  { id: 'controls', name: '安全控制', count: 62, icon: IconShield },
  { id: 'standards', name: '标准规范', count: 28, icon: IconFile },
  { id: 'patterns', name: '攻击模式', count: 18, icon: IconWarning }
]

const knowledgeItems = ref([
  { id: '1', title: 'CAN总线安全威胁分析', description: '详细分析CAN总线面临的各类安全威胁，包括消息注入、DoS攻击等', category: '威胁情报', categoryClass: 'threat', date: '2024-12-10', views: 1256, tags: ['CAN', 'STRIDE', '消息注入'] },
  { id: '2', title: 'SecOC安全通信协议实施指南', description: 'AUTOSAR SecOC协议的详细实施步骤和最佳实践', category: '安全控制', categoryClass: 'control', date: '2024-12-08', views: 892, tags: ['SecOC', 'AUTOSAR', '消息认证'] },
  { id: '3', title: 'ISO/SAE 21434合规指南', description: '汽车网络安全工程标准的解读和合规建议', category: '标准规范', categoryClass: 'standard', date: '2024-12-05', views: 2341, tags: ['ISO 21434', '合规', 'CSMS'] },
  { id: '4', title: 'T-Box远程攻击案例分析', description: '真实案例分析：T-Box远程攻击手法与防护措施', category: '攻击模式', categoryClass: 'pattern', date: '2024-12-01', views: 1567, tags: ['T-Box', '远程攻击', '案例'] },
  { id: '5', title: 'HSM硬件安全模块部署指南', description: '车载HSM的选型、部署和密钥管理最佳实践', category: '安全控制', categoryClass: 'control', date: '2024-11-28', views: 756, tags: ['HSM', '密钥管理', '硬件安全'] },
  { id: '6', title: 'UN R155法规解读', description: '联合国R155法规的详细解读和OEM合规路径', category: '标准规范', categoryClass: 'standard', date: '2024-11-25', views: 1890, tags: ['UN R155', '法规', 'OEM'] }
])

const filteredItems = computed(() => {
  return knowledgeItems.value.filter(item => {
    const matchesSearch = !searchQuery.value || 
      item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'all' || 
      item.categoryClass === selectedCategory.value.replace('s', '')
    return matchesSearch && matchesCategory
  })
})

const openItem = (item: any) => {
  console.log('Open:', item)
}
</script>

<style scoped>
.page-container {
  max-width: 1200px;
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

.search-box {
  position: relative;
}

.search-box svg {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.search-box input {
  width: 300px;
  height: 42px;
  padding: 0 16px 0 42px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
}

.search-box input:focus {
  border-color: var(--border-focus);
}

.category-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  white-space: nowrap;
}

.category-tab:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.category-tab.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--brand-blue);
  color: var(--text-primary);
}

.category-tab svg {
  width: 18px;
  height: 18px;
}

.category-tab .count {
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--bg-hover);
  font-size: 12px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.knowledge-card {
  cursor: pointer;
  transition: all var(--transition-normal);
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.card-category {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 12px;
}

.card-category.threat { background: rgba(245, 158, 11, 0.15); color: #FBBF24; }
.card-category.control { background: rgba(16, 185, 129, 0.15); color: #34D399; }
.card-category.standard { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
.card-category.pattern { background: rgba(239, 68, 68, 0.15); color: #F87171; }

.card-title {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
}

.card-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 16px;
}

.card-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.card-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
}

.card-meta svg {
  width: 14px;
  height: 14px;
}

.card-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: var(--bg-hover);
  color: var(--text-secondary);
}
</style>
