<template>
  <div class="report-generator animate-fadeIn">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="glow-1"></div>
      <div class="glow-2"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          AI驱动
        </div>
        <h1 class="hero-title">🚀 <span>一键生成</span> TARA安全分析报告</h1>
        <p class="hero-subtitle">
          上传资产清单和配置文件，AI自动完成威胁识别、风险评估，生成符合ISO 21434标准的专业报告。支持多轮对话优化。
        </p>
        <div class="hero-features">
          <div v-for="feature in heroFeatures" :key="feature" class="hero-feature">
            <div class="hero-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
            </div>
            {{ feature }}
          </div>
        </div>
      </div>
    </div>

    <!-- Steps Indicator -->
    <div class="steps-indicator">
      <div 
        v-for="(step, index) in steps" 
        :key="step.number"
        class="step-item"
        :class="{ active: currentStep === step.number, completed: currentStep > step.number }"
      >
        <div class="step-number">
          <svg v-if="currentStep > step.number" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          <span v-else>{{ step.number }}</span>
        </div>
        <div class="step-info">
          <div class="step-label">{{ step.label }}</div>
          <div class="step-desc">{{ step.desc }}</div>
        </div>
      </div>
      <div 
        v-for="(step, index) in steps.slice(0, -1)" 
        :key="'connector-' + index"
        class="step-connector"
        :class="{ active: currentStep > step.number, completed: currentStep > step.number + 1 }"
      ></div>
    </div>

    <!-- Generator Grid -->
    <div class="generator-grid">
      <div class="generator-main">
        <!-- Upload Section -->
        <div class="tara-card">
          <div class="tara-card-header">
            <h3 class="tara-card-title">
              <div class="tara-card-title-icon blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
              </div>
              上传分析文件
            </h3>
          </div>
          <div 
            class="upload-zone"
            :class="{ dragover: isDragging, 'has-files': uploadedFiles.length > 0 }"
            @click="triggerFileInput"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="handleDrop"
          >
            <input 
              ref="fileInputRef"
              type="file" 
              multiple 
              accept=".xlsx,.xls,.csv,.json,.pdf"
              @change="handleFileSelect"
              style="display: none"
            >
            <div class="upload-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
              </svg>
            </div>
            <div class="upload-title">拖拽文件到此处，或点击上传</div>
            <div class="upload-desc">支持资产清单、ECU配置、网络拓扑等文件</div>
            <div class="upload-formats">
              <span class="format-tag">Excel (.xlsx)</span>
              <span class="format-tag">CSV (.csv)</span>
              <span class="format-tag">JSON (.json)</span>
              <span class="format-tag">PDF (.pdf)</span>
            </div>
          </div>
          <div v-if="uploadedFiles.length > 0" class="file-list">
            <div 
              v-for="file in uploadedFiles" 
              :key="file.id"
              class="file-item"
            >
              <div class="file-icon" :class="file.type">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                  <path d="M14 2v6h6"/>
                </svg>
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span>{{ file.size }}</span>
                  <span>{{ file.type.toUpperCase() }}</span>
                </div>
              </div>
              <div class="file-status" :class="file.status">
                <template v-if="file.status === 'success'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                  已解析
                </template>
                <template v-else>
                  <svg class="animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
                  </svg>
                  解析中
                </template>
              </div>
              <button class="file-remove" @click.stop="removeFile(file.id)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Template Selection -->
        <div class="tara-card">
          <div class="tara-card-header">
            <h3 class="tara-card-title">
              <div class="tara-card-title-icon purple">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <path d="M3 9h18M9 21V9"/>
                </svg>
              </div>
              选择报告模板
            </h3>
          </div>
          <div class="template-grid">
            <button 
              v-for="template in templates" 
              :key="template.type"
              class="template-btn"
              :class="{ selected: selectedTemplate === template.type }"
              @click="selectedTemplate = template.type"
            >
              <div class="template-icon" :style="{ background: template.bgColor, color: template.color }">
                <component :is="template.icon" />
              </div>
              <div class="template-title">{{ template.title }}</div>
              <div class="template-desc">{{ template.desc }}</div>
            </button>
          </div>
        </div>

        <!-- Prompt Input -->
        <div class="tara-card">
          <div class="tara-card-header">
            <h3 class="tara-card-title">
              <div class="tara-card-title-icon cyan">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
              </div>
              分析提示词
            </h3>
          </div>
          <div class="prompt-container">
            <textarea 
              v-model="promptText"
              placeholder="请描述您的具体分析需求..."
            ></textarea>
          </div>
          <div class="prompt-toolbar">
            <span class="char-count">{{ promptText.length }} / 2000</span>
            <button class="tara-btn tara-btn-ghost" @click="promptText = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
              清空
            </button>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="generate-section">
          <button 
            class="generate-btn"
            :class="{ generating: isGenerating }"
            :disabled="uploadedFiles.length === 0 || isGenerating"
            @click="generateReport"
          >
            <svg v-if="isGenerating" class="animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
            </svg>
            {{ isGenerating ? '正在生成...' : '一键生成TARA报告' }}
          </button>
        </div>
      </div>

      <div class="generator-sidebar">
        <!-- Preview Card -->
        <div class="preview-card">
          <div class="preview-header">
            <h4>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              分析预览
            </h4>
          </div>
          <div class="preview-content">
            <div v-if="uploadedFiles.length === 0" class="preview-empty">
              📁 上传文件后显示分析预览
            </div>
            <template v-else>
              <div class="preview-stats">
                <div class="preview-stat blue">
                  <div class="preview-stat-value">{{ previewStats.assets }}</div>
                  <div class="preview-stat-label">识别资产</div>
                </div>
                <div class="preview-stat orange">
                  <div class="preview-stat-value">{{ previewStats.threats }}</div>
                  <div class="preview-stat-label">预估威胁</div>
                </div>
              </div>
              <div class="preview-info">
                预计生成时间: <strong>2-3分钟</strong>
              </div>
            </template>
          </div>
        </div>

        <!-- Tips Card -->
        <div class="tips-card">
          <div class="tips-header">
            <h4>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01"/>
              </svg>
              使用提示
            </h4>
          </div>
          <div class="tips-content">
            <p>📁 文件要求</p>
            <ul>
              <li>Excel需包含资产名称、类型、接口列</li>
              <li>CSV使用UTF-8编码</li>
              <li>JSON符合TARA资产模型格式</li>
            </ul>
            <p>💡 优化建议</p>
            <ul>
              <li>提供详细的系统架构描述</li>
              <li>标注资产的安全等级要求</li>
              <li>说明已有的安全控制措施</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Icons
const IconFile = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>`
}
const IconWarning = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`
}
const IconActivity = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
}
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}

// State
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const uploadedFiles = ref<any[]>([])
const selectedTemplate = ref('full')
const promptText = ref(`请对上传的资产清单进行完整的TARA分析，包括：
1. 识别所有ECU资产及其通信接口（CAN、Ethernet、LIN等）
2. 基于STRIDE模型进行全面的威胁识别
3. 计算每个威胁的CAL风险等级（考虑影响度和可行性）
4. 针对CAL-3及以上高风险项提供具体的安全措施建议
5. 生成符合ISO 21434标准格式的专业报告`)
const isGenerating = ref(false)
const currentStep = ref(1)

// Hero features
const heroFeatures = [
  '支持Excel/CSV/JSON',
  'STRIDE威胁建模',
  'CAL风险评估',
  '多轮对话优化'
]

// Steps
const steps = [
  { number: 1, label: '上传文件', desc: '资产清单/配置' },
  { number: 2, label: '选择模板', desc: '报告类型' },
  { number: 3, label: '填写提示', desc: '分析要求' },
  { number: 4, label: '生成优化', desc: 'AI分析' }
]

// Templates
const templates = [
  {
    type: 'full',
    title: '完整TARA报告',
    desc: '资产识别 + 威胁分析 + 风险评估 + 措施建议，符合ISO 21434标准',
    icon: IconFile,
    bgColor: 'rgba(59,130,246,0.12)',
    color: '#60A5FA'
  },
  {
    type: 'threat',
    title: '威胁分析报告',
    desc: '专注STRIDE威胁识别、攻击树分析和攻击路径推理',
    icon: IconWarning,
    bgColor: 'rgba(245,158,11,0.12)',
    color: '#FBBF24'
  },
  {
    type: 'risk',
    title: '风险评估报告',
    desc: '影响分析、CAL等级评估、风险矩阵和优先级排序',
    icon: IconActivity,
    bgColor: 'rgba(239,68,68,0.12)',
    color: '#F87171'
  },
  {
    type: 'measure',
    title: '安全措施报告',
    desc: '防护策略、控制措施、验证方案和实施路线图',
    icon: IconShield,
    bgColor: 'rgba(16,185,129,0.12)',
    color: '#34D399'
  }
]

// Preview stats
const previewStats = computed(() => ({
  assets: uploadedFiles.value.length > 0 ? Math.floor(Math.random() * 30) + 20 : 0,
  threats: uploadedFiles.value.length > 0 ? Math.floor(Math.random() * 80) + 50 : 0
}))

// Methods
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files) {
    handleFiles(Array.from(e.dataTransfer.files))
  }
}

const handleFiles = (files: File[]) => {
  files.forEach(file => {
    const fileData = {
      id: Date.now() + Math.random(),
      name: file.name,
      size: formatFileSize(file.size),
      type: file.name.split('.').pop()?.toLowerCase() || 'unknown',
      status: 'processing'
    }
    uploadedFiles.value.push(fileData)
    
    // Simulate processing
    setTimeout(() => {
      const index = uploadedFiles.value.findIndex(f => f.id === fileData.id)
      if (index !== -1) {
        uploadedFiles.value[index].status = 'success'
      }
      updateStep()
    }, 1500)
  })
  updateStep()
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const removeFile = (id: number) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== id)
  updateStep()
}

const updateStep = () => {
  if (uploadedFiles.value.length === 0) {
    currentStep.value = 1
  } else if (selectedTemplate.value) {
    currentStep.value = promptText.value.length > 0 ? 3 : 2
  }
}

const generateReport = async () => {
  if (uploadedFiles.value.length === 0) return
  
  isGenerating.value = true
  currentStep.value = 4
  
  // Simulate report generation
  setTimeout(() => {
    isGenerating.value = false
    // Navigate to report or show success
    router.push('/reports')
  }, 3000)
}
</script>

<style scoped>
.report-generator {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 36px 40px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.1) 50%, rgba(236,72,153,0.08) 100%);
  border: 1px solid rgba(255,255,255,0.08);
}

.hero-section .glow-1 {
  position: absolute;
  top: -80%;
  right: 0%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 60%);
  filter: blur(80px);
}

.hero-section .glow-2 {
  position: absolute;
  bottom: -60%;
  left: 10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 60%);
  filter: blur(60px);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--brand-purple), var(--brand-pink));
  font-size: 12px;
  font-weight: 600;
  color: white;
  margin-bottom: 16px;
}

.hero-badge svg {
  width: 14px;
  height: 14px;
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.3;
}

.hero-title span {
  background: linear-gradient(135deg, #60A5FA, #A78BFA, #F472B6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 28px;
  max-width: 600px;
  line-height: 1.6;
}

.hero-features {
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}

.hero-feature {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}

.hero-feature-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(16,185,129,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-feature-icon svg {
  width: 14px;
  height: 14px;
  color: #34D399;
}

/* Steps Indicator */
.steps-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0;
  padding: 24px 32px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  position: relative;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 24px;
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
  z-index: 1;
}

.step-item.active {
  background: rgba(59,130,246,0.1);
}

.step-item.completed {
  background: rgba(16,185,129,0.08);
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: var(--bg-hover);
  color: var(--text-muted);
  transition: all var(--transition-normal);
}

.step-item.active .step-number {
  background: var(--brand-blue);
  color: white;
  box-shadow: 0 4px 12px rgba(59,130,246,0.4);
}

.step-item.completed .step-number {
  background: var(--success);
  color: white;
}

.step-item.completed .step-number svg {
  width: 18px;
  height: 18px;
}

.step-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.step-connector {
  width: 60px;
  height: 2px;
  background: var(--border-color);
  position: absolute;
}

.step-connector:nth-of-type(5) { left: calc(25% - 30px); }
.step-connector:nth-of-type(6) { left: calc(50% - 30px); }
.step-connector:nth-of-type(7) { left: calc(75% - 30px); }

.step-connector.active {
  background: linear-gradient(90deg, var(--brand-blue), var(--brand-purple));
}

.step-connector.completed {
  background: var(--success);
}

/* Generator Grid */
.generator-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}

.generator-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.generator-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Upload Zone */
.upload-zone {
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-xl);
  padding: 48px 32px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  background: rgba(255,255,255,0.01);
  position: relative;
  overflow: hidden;
}

.upload-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(59,130,246,0.03), rgba(139,92,246,0.03));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.upload-zone:hover,
.upload-zone.dragover {
  border-color: var(--brand-blue);
  background: rgba(59,130,246,0.04);
}

.upload-zone:hover::before,
.upload-zone.dragover::before {
  opacity: 1;
}

.upload-zone.has-files {
  border-style: solid;
  border-color: var(--success);
}

.upload-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.12));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.upload-icon svg {
  width: 36px;
  height: 36px;
  color: var(--brand-blue);
}

.upload-title {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.upload-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.upload-formats {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.format-tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: var(--bg-hover);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

/* File List */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  transition: all var(--transition-normal);
}

.file-item:hover {
  background: var(--bg-hover);
}

.file-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-icon svg {
  width: 22px;
  height: 22px;
}

.file-icon.xlsx,
.file-icon.xls { background: rgba(16,185,129,0.12); color: #34D399; }
.file-icon.csv { background: rgba(59,130,246,0.12); color: #60A5FA; }
.file-icon.pdf { background: rgba(239,68,68,0.12); color: #F87171; }
.file-icon.json { background: rgba(245,158,11,0.12); color: #FBBF24; }

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.file-status svg {
  width: 16px;
  height: 16px;
}

.file-status.success { color: var(--success); }
.file-status.processing { color: var(--warning); }

.file-remove {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.file-remove:hover {
  background: rgba(239,68,68,0.1);
  color: var(--danger);
}

.file-remove svg {
  width: 16px;
  height: 16px;
}

/* Template Grid */
.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.template-btn {
  padding: 18px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-normal);
}

.template-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-light);
}

.template-btn.selected {
  background: rgba(59,130,246,0.08);
  border-color: var(--brand-blue);
}

.template-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.template-icon svg {
  width: 20px;
  height: 20px;
}

.template-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.template-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Prompt Input */
.prompt-container {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.prompt-container textarea {
  width: 100%;
  padding: 18px 20px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  min-height: 140px;
  line-height: 1.6;
}

.prompt-container textarea::placeholder {
  color: var(--text-muted);
}

.prompt-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: rgba(255,255,255,0.01);
}

.char-count {
  font-size: 12px;
  color: var(--text-muted);
}

/* Generate Button */
.generate-section {
  display: flex;
  justify-content: center;
  padding: 32px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
}

.generate-btn {
  padding: 18px 56px;
  border-radius: var(--radius-xl);
  border: none;
  background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-purple) 100%);
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all var(--transition-normal);
  box-shadow: 0 8px 32px rgba(59,130,246,0.35);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(59,130,246,0.45);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.generate-btn svg {
  width: 24px;
  height: 24px;
}

.generate-btn.generating {
  animation: pulse 1.5s infinite;
}

/* Preview Card */
.preview-card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.preview-header {
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color);
}

.preview-header h4 {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-header h4 svg {
  width: 18px;
  height: 18px;
  color: var(--brand-purple);
}

.preview-content {
  padding: 20px;
}

.preview-empty {
  text-align: center;
  padding: 32px 20px;
  color: var(--text-muted);
  font-size: 14px;
}

.preview-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.preview-stat {
  padding: 16px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  text-align: center;
}

.preview-stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.preview-stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.preview-stat.blue .preview-stat-value { color: #60A5FA; }
.preview-stat.orange .preview-stat-value { color: #FBBF24; }

.preview-info {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

/* Tips Card */
.tips-card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.tips-header {
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color);
}

.tips-header h4 {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tips-header h4 svg {
  width: 18px;
  height: 18px;
  color: var(--success);
}

.tips-content {
  padding: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.tips-content p {
  margin-bottom: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tips-content ul {
  margin-left: 24px;
  margin-bottom: 16px;
}

.tips-content li {
  margin-bottom: 6px;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 1400px) {
  .generator-grid {
    grid-template-columns: 1fr;
  }
  
  .generator-sidebar {
    display: none;
  }
  
  .steps-indicator {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .step-connector {
    display: none;
  }
}
</style>
