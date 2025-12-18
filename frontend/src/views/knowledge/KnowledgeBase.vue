<template>
  <div class="page-container animate-fadeIn">
    <div class="page-header">
      <div>
        <h1>知识库</h1>
        <p class="page-subtitle">汽车网络安全威胁情报与最佳实践</p>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          <input 
            type="text" 
            placeholder="搜索知识库..." 
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          >
        </div>
        <button class="btn-primary" @click="showUploadModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          上传文档
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-row" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_documents }}</div>
        <div class="stat-label">文档总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_chunks }}</div>
        <div class="stat-label">知识片段</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" :class="{ 'status-ok': stats.es_available, 'status-error': !stats.es_available }">
          {{ stats.es_available ? '在线' : '离线' }}
        </div>
        <div class="stat-label">全文搜索</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" :class="{ 'status-ok': stats.milvus_available, 'status-error': !stats.milvus_available }">
          {{ stats.milvus_available ? '在线' : '离线' }}
        </div>
        <div class="stat-label">向量搜索</div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="section-header">
        <h2>搜索结果</h2>
        <button class="btn-text" @click="clearSearch">清除</button>
      </div>
      <div class="result-list">
        <div 
          v-for="result in searchResults" 
          :key="result.chunk_id"
          class="result-card tara-card"
        >
          <div class="result-meta">
            <span class="result-type" :class="result.search_type">{{ result.search_type }}</span>
            <span class="result-score">相关度: {{ (result.score * 100).toFixed(1) }}%</span>
          </div>
          <p class="result-content">{{ result.content }}</p>
          <div class="result-source" v-if="result.filename">
            来源: {{ result.filename }}
          </div>
        </div>
      </div>
    </div>

    <div class="category-tabs">
      <button 
        v-for="cat in displayCategories" 
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

    <!-- Document Grid -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="documents.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>知识库为空</h3>
      <p>上传文档开始构建您的知识库</p>
      <button class="btn-primary" @click="showUploadModal = true">上传第一个文档</button>
    </div>

    <div v-else class="knowledge-grid">
      <div 
        v-for="item in documents" 
        :key="item.document_id"
        class="knowledge-card tara-card"
      >
        <div class="card-category" :class="getCategoryClass(item.category)">
          {{ item.category }}
        </div>
        <h3 class="card-title">{{ item.filename }}</h3>
        <p class="card-desc">{{ item.total_chunks }} 个知识片段，{{ formatSize(item.content_length) }}</p>
        <div class="card-meta">
          <span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            {{ formatDate(item.created_at) }}
          </span>
          <span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/>
              <polyline points="13 2 13 9 20 9"/>
            </svg>
            {{ item.indexed_chunks }}/{{ item.total_chunks }}
          </span>
        </div>
        <div class="card-tags">
          <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
        <div class="card-actions">
          <button class="btn-icon" @click="reindexDocument(item.document_id)" title="重新索引">
            🔄
          </button>
          <button class="btn-icon danger" @click="deleteDocument(item.document_id)" title="删除">
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal-content tara-card">
        <h2>上传文档</h2>
        <div class="upload-form">
          <div class="file-input">
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              accept=".pdf,.doc,.docx,.txt,.md,.json,.csv"
            >
            <div class="file-placeholder" @click="triggerFileInput">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <p>{{ selectedFile ? selectedFile.name : '点击选择文件或拖拽至此' }}</p>
            </div>
          </div>
          
          <div class="form-group">
            <label>分类</label>
            <select v-model="uploadCategory">
              <option value="general">通用</option>
              <option value="threat_library">威胁库</option>
              <option value="control_library">控制库</option>
              <option value="standard">标准规范</option>
              <option value="regulation">法规</option>
              <option value="best_practice">最佳实践</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>标签（逗号分隔）</label>
            <input type="text" v-model="uploadTags" placeholder="如: CAN, STRIDE, 威胁分析">
          </div>
          
          <div class="modal-actions">
            <button class="btn-secondary" @click="showUploadModal = false">取消</button>
            <button 
              class="btn-primary" 
              @click="uploadDocument"
              :disabled="!selectedFile || uploading"
            >
              {{ uploading ? '上传中...' : '上传' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { knowledgeApi, type KnowledgeDocument, type SearchResult, type KnowledgeStats } from '@/api'

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
const loading = ref(true)
const documents = ref<KnowledgeDocument[]>([])
const searchResults = ref<SearchResult[]>([])
const stats = ref<KnowledgeStats | null>(null)
const categories = ref<string[]>([])

// Upload modal
const showUploadModal = ref(false)
const selectedFile = ref<File | null>(null)
const uploadCategory = ref('general')
const uploadTags = ref('')
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const displayCategories = computed(() => {
  const baseCats = [
    { id: 'all', name: '全部', count: documents.value.length, icon: IconBook },
  ]
  
  const catCounts: Record<string, number> = {}
  documents.value.forEach(doc => {
    catCounts[doc.category] = (catCounts[doc.category] || 0) + 1
  })
  
  const catIcons: Record<string, any> = {
    'threat_library': IconWarning,
    'control_library': IconShield,
    'standard': IconFile,
    'regulation': IconFile,
    'best_practice': IconBook,
    'general': IconBook,
  }
  
  const catNames: Record<string, string> = {
    'threat_library': '威胁库',
    'control_library': '控制库',
    'standard': '标准规范',
    'regulation': '法规',
    'best_practice': '最佳实践',
    'general': '通用',
  }
  
  categories.value.forEach(cat => {
    if (catCounts[cat] || cat !== 'all') {
      baseCats.push({
        id: cat,
        name: catNames[cat] || cat,
        count: catCounts[cat] || 0,
        icon: catIcons[cat] || IconBook,
      })
    }
  })
  
  return baseCats
})

const getCategoryClass = (category: string) => {
  const classMap: Record<string, string> = {
    'threat_library': 'threat',
    'control_library': 'control',
    'standard': 'standard',
    'regulation': 'standard',
    'best_practice': 'control',
    'general': 'standard',
  }
  return classMap[category] || 'standard'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

const loadData = async () => {
  loading.value = true
  try {
    const [docsRes, statsRes, catsRes] = await Promise.all([
      knowledgeApi.list({ page: 1, page_size: 100 }),
      knowledgeApi.getStats(),
      knowledgeApi.listCategories(),
    ])
    
    if (docsRes.success) {
      documents.value = docsRes.data?.items || []
    }
    if (statsRes.success) {
      stats.value = statsRes.data
    }
    if (catsRes.success) {
      categories.value = catsRes.data?.categories || []
    }
  } catch (error) {
    console.error('Failed to load knowledge base:', error)
    // Set empty defaults on error
    documents.value = []
    stats.value = null
    categories.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  
  try {
    const res = await knowledgeApi.search({
      query: searchQuery.value,
      search_type: 'hybrid',
      top_k: 20,
    })
    
    if (res.success) {
      searchResults.value = res.data?.results || []
    }
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const uploadDocument = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  try {
    const res = await knowledgeApi.upload({
      file: selectedFile.value,
      category: uploadCategory.value,
      tags: uploadTags.value,
    })
    
    if (res.success) {
      showUploadModal.value = false
      selectedFile.value = null
      uploadTags.value = ''
      await loadData()
    }
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    uploading.value = false
  }
}

const deleteDocument = async (documentId: string) => {
  if (!confirm('确定要删除此文档吗？')) return
  
  try {
    await knowledgeApi.delete(documentId)
    await loadData()
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

const reindexDocument = async (documentId: string) => {
  try {
    await knowledgeApi.reindex(documentId)
    await loadData()
  } catch (error) {
    console.error('Reindex failed:', error)
  }
}

onMounted(() => {
  loadData()
})
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

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
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

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--brand-blue);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary svg {
  width: 18px;
  height: 18px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-value.status-ok { color: #10b981; }
.stat-value.status-error { color: #ef4444; }

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

.search-results {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.btn-text {
  background: none;
  border: none;
  color: var(--brand-blue);
  cursor: pointer;
  font-size: 14px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-card {
  padding: 16px;
}

.result-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.result-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.result-type.vector { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.result-type.fulltext { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.result-type.hybrid { background: rgba(16, 185, 129, 0.2); color: #34d399; }

.result-score {
  font-size: 12px;
  color: var(--text-muted);
}

.result-content {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.result-source {
  font-size: 12px;
  color: var(--text-muted);
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

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--brand-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 24px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.knowledge-card {
  position: relative;
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

.card-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.knowledge-card:hover .card-actions {
  opacity: 1;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: var(--bg-hover);
  cursor: pointer;
  font-size: 14px;
}

.btn-icon.danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 480px;
  max-width: 90vw;
  padding: 24px;
}

.modal-content h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.file-input input {
  display: none;
}

.file-placeholder {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.file-placeholder:hover {
  border-color: var(--brand-blue);
  background: rgba(59, 130, 246, 0.05);
}

.file-placeholder svg {
  width: 40px;
  height: 40px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.file-placeholder p {
  color: var(--text-muted);
  font-size: 14px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-secondary {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}
</style>
