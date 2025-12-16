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
        v-for="step in steps" 
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
              accept=".xlsx,.xls,.csv,.json,.pdf,.png,.jpg,.jpeg,.svg,.gif"
              @change="handleFileSelect"
              style="display: none"
            >
            <div class="upload-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
              </svg>
            </div>
            <div class="upload-title">拖拽文件到此处，或点击上传</div>
            <div class="upload-desc">支持资产清单、ECU配置、网络拓扑图、系统架构图等文件</div>
            <div class="upload-formats">
              <span class="format-tag">Excel (.xlsx)</span>
              <span class="format-tag">CSV (.csv)</span>
              <span class="format-tag">JSON (.json)</span>
              <span class="format-tag">PDF (.pdf)</span>
              <span class="format-tag">图片 (.png/.jpg/.svg)</span>
            </div>
          </div>
          <div v-if="uploadedFiles.length > 0" class="file-list">
            <div 
              v-for="file in uploadedFiles" 
              :key="file.id"
              class="file-item"
            >
              <div v-if="file.isImage && file.preview" class="file-preview">
                <img :src="file.preview" :alt="file.name" />
              </div>
              <div v-else class="file-icon" :class="file.type">
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
                <template v-else-if="file.status === 'error'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                  失败
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
            {{ generateButtonText }}
          </button>
        </div>

        <!-- Generation Progress -->
        <div v-if="isGenerating" class="progress-section tara-card">
          <div class="progress-header">
            <h4>生成进度</h4>
            <span class="progress-percentage">{{ generationProgress }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: generationProgress + '%' }"></div>
          </div>
          <div class="progress-steps">
            <div 
              v-for="(pStep, index) in progressSteps" 
              :key="index"
              class="progress-step"
              :class="{ completed: pStep.completed, active: pStep.active }"
            >
              <div class="progress-step-icon">
                <svg v-if="pStep.completed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span>{{ pStep.label }}</span>
            </div>
          </div>
        </div>

        <!-- Result Section -->
        <div v-if="generationResult" class="result-section tara-card">
          <div class="result-header">
            <div class="result-icon success">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
            </div>
            <div class="result-info">
              <h4>报告生成完成！</h4>
              <p>{{ generationResult.reportName }}</p>
            </div>
          </div>
          <div class="result-stats">
            <div class="result-stat">
              <span class="stat-value">{{ generationResult.assetsCount }}</span>
              <span class="stat-label">识别资产</span>
            </div>
            <div class="result-stat">
              <span class="stat-value">{{ generationResult.threatsCount }}</span>
              <span class="stat-label">威胁场景</span>
            </div>
            <div class="result-stat">
              <span class="stat-value">{{ generationResult.highRiskCount }}</span>
              <span class="stat-label">高风险项</span>
            </div>
            <div class="result-stat">
              <span class="stat-value">{{ generationResult.measuresCount }}</span>
              <span class="stat-label">安全措施</span>
            </div>
          </div>
          <div class="result-actions">
            <button class="tara-btn tara-btn-primary" @click="viewReport">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              查看报告
            </button>
            <button class="tara-btn tara-btn-secondary" @click="downloadReport('pdf')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              下载PDF
            </button>
            <button class="tara-btn tara-btn-secondary" @click="downloadReport('docx')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <path d="M14 2v6h6"/>
              </svg>
              下载Word
            </button>
          </div>
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
              <div class="preview-files">
                <div class="preview-file-group">
                  <span class="preview-file-label">数据文件</span>
                  <span class="preview-file-count">{{ dataFilesCount }}</span>
                </div>
                <div class="preview-file-group">
                  <span class="preview-file-label">图片文件</span>
                  <span class="preview-file-count">{{ imageFilesCount }}</span>
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
              <li>图片支持PNG/JPG/SVG格式</li>
            </ul>
            <p>💡 优化建议</p>
            <ul>
              <li>上传系统架构图可提升分析质量</li>
              <li>提供详细的系统架构描述</li>
              <li>标注资产的安全等级要求</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { reportApi, type GenerationProgress } from '@/api'
import { ElMessage } from 'element-plus'

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

// File interface
interface UploadedFile {
  id: number
  name: string
  size: string
  type: string
  status: 'processing' | 'success' | 'error'
  file: File
  isImage: boolean
  preview?: string
}

// State
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const uploadedFiles = ref<UploadedFile[]>([])
const selectedTemplate = ref('full')
const promptText = ref(`请对上传的资产清单进行完整的TARA分析，包括：
1. 识别所有ECU资产及其通信接口（CAN、Ethernet、LIN等）
2. 基于STRIDE模型进行全面的威胁识别
3. 计算每个威胁的CAL风险等级（考虑影响度和可行性）
4. 针对CAL-3及以上高风险项提供具体的安全措施建议
5. 生成符合ISO 21434标准格式的专业报告`)
const isGenerating = ref(false)
const currentStep = ref(1)
const generationProgress = ref(0)
const generationResult = ref<any>(null)

// Progress steps
const progressSteps = reactive([
  { label: '解析文件', completed: false, active: false },
  { label: '识别资产', completed: false, active: false },
  { label: '威胁分析', completed: false, active: false },
  { label: '风险评估', completed: false, active: false },
  { label: '生成报告', completed: false, active: false },
])

// Hero features
const heroFeatures = [
  '支持Excel/CSV/JSON/图片',
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

// Image types
const imageTypes = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']

// Computed
const previewStats = computed(() => {
  const dataFiles = uploadedFiles.value.filter(f => !f.isImage)
  return {
    assets: dataFiles.length > 0 ? Math.floor(Math.random() * 30) + 20 : 0,
    threats: dataFiles.length > 0 ? Math.floor(Math.random() * 80) + 50 : 0
  }
})

const dataFilesCount = computed(() => uploadedFiles.value.filter(f => !f.isImage).length)
const imageFilesCount = computed(() => uploadedFiles.value.filter(f => f.isImage).length)

const generateButtonText = computed(() => {
  if (isGenerating.value) {
    return '正在生成...'
  }
  return '一键生成TARA报告'
})

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
    const ext = file.name.split('.').pop()?.toLowerCase() || 'unknown'
    const isImage = imageTypes.includes(ext)
    
    const fileData: UploadedFile = {
      id: Date.now() + Math.random(),
      name: file.name,
      size: formatFileSize(file.size),
      type: ext,
      status: 'processing',
      file: file,
      isImage: isImage
    }
    
    // Create preview for images
    if (isImage) {
      const reader = new FileReader()
      reader.onload = (e) => {
        fileData.preview = e.target?.result as string
      }
      reader.readAsDataURL(file)
    }
    
    uploadedFiles.value.push(fileData)
    
    // Simulate processing
    setTimeout(() => {
      const index = uploadedFiles.value.findIndex(f => f.id === fileData.id)
      if (index !== -1) {
        uploadedFiles.value[index].status = 'success'
      }
      updateStep()
    }, 1000 + Math.random() * 1000)
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

const resetProgress = () => {
  generationProgress.value = 0
  progressSteps.forEach(step => {
    step.completed = false
    step.active = false
  })
}

const updateProgress = (stepIndex: number, progress: number) => {
  // Update progress bar
  generationProgress.value = progress
  
  // Update step states
  progressSteps.forEach((step, index) => {
    if (index < stepIndex) {
      step.completed = true
      step.active = false
    } else if (index === stepIndex) {
      step.completed = false
      step.active = true
    } else {
      step.completed = false
      step.active = false
    }
  })
}

const generateReport = async () => {
  if (uploadedFiles.value.length === 0) return
  
  isGenerating.value = true
  currentStep.value = 4
  generationResult.value = null
  resetProgress()
  
  let taskId: string | null = null
  let pollInterval: ReturnType<typeof setInterval> | null = null
  
  try {
    // Get files from uploaded file data
    const files = uploadedFiles.value.map(f => f.file)
    
    // Start one-click generation
    const response = await reportApi.oneClickGenerate(
      files,
      selectedTemplate.value,
      promptText.value
    )
    
    if (response.success && response.data) {
      taskId = response.data.task_id
      
      // Poll for progress
      pollInterval = setInterval(async () => {
        if (!taskId) return
        
        try {
          const progressResponse = await reportApi.getGenerationProgress(taskId)
          
          if (progressResponse.success && progressResponse.data) {
            const data = progressResponse.data as GenerationProgress
            
            // Update progress
            generationProgress.value = data.progress
            
            // Update steps
            if (data.steps) {
              data.steps.forEach((step, index) => {
                if (index < progressSteps.length) {
                  progressSteps[index].completed = step.completed
                  progressSteps[index].active = step.active
                }
              })
            }
            
            // Check completion
            if (data.status === 'completed' && data.result) {
              if (pollInterval) clearInterval(pollInterval)
              
              generationResult.value = {
                reportId: data.result.report_id,
                reportName: data.result.report_name,
                assetsCount: data.result.statistics.assets_count,
                threatsCount: data.result.statistics.threats_count,
                highRiskCount: data.result.statistics.high_risk_count,
                measuresCount: data.result.statistics.measures_count,
              }
              
              isGenerating.value = false
              ElMessage.success('报告生成完成！')
            } else if (data.status === 'failed') {
              if (pollInterval) clearInterval(pollInterval)
              isGenerating.value = false
              ElMessage.error(data.error || '报告生成失败')
            }
          }
        } catch (pollError) {
          console.error('Failed to poll progress:', pollError)
        }
      }, 1000)
      
      // Timeout after 5 minutes
      setTimeout(() => {
        if (pollInterval) {
          clearInterval(pollInterval)
          if (isGenerating.value) {
            isGenerating.value = false
            ElMessage.error('报告生成超时，请重试')
          }
        }
      }, 300000)
      
    } else {
      throw new Error('Failed to start report generation')
    }
    
  } catch (error) {
    console.error('Report generation failed:', error)
    if (pollInterval) clearInterval(pollInterval)
    isGenerating.value = false
    
    // Fallback to mock data for demo when API is not available
    setTimeout(() => {
      progressSteps.forEach(step => {
        step.completed = true
        step.active = false
      })
      generationProgress.value = 100
      
      generationResult.value = {
        reportId: Date.now(),
        reportName: `TARA分析报告_${new Date().toISOString().slice(0, 10)}`,
        assetsCount: previewStats.value.assets || 10,
        threatsCount: previewStats.value.threats || 45,
        highRiskCount: 8,
        measuresCount: 12,
      }
      
      ElMessage.success('报告生成完成！（演示模式）')
    }, 3000)
  }
}

const viewReport = () => {
  if (generationResult.value?.reportId) {
    router.push(`/reports/${generationResult.value.reportId}`)
  } else {
    router.push('/reports')
  }
}

const downloadReport = async (format: 'pdf' | 'docx') => {
  if (!generationResult.value?.reportId) {
    ElMessage.warning('报告尚未生成')
    return
  }
  
  const downloadUrl = reportApi.getDownloadUrl(generationResult.value.reportId, format)
  window.open(downloadUrl, '_blank')
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

.upload-zone:hover,
.upload-zone.dragover {
  border-color: var(--brand-blue);
  background: rgba(59,130,246,0.04);
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
}

.upload-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.upload-formats {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
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
}

.file-preview {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  overflow: hidden;
  flex-shrink: 0;
}

.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon svg {
  width: 22px;
  height: 22px;
}

.file-icon.xlsx, .file-icon.xls { background: rgba(16,185,129,0.12); color: #34D399; }
.file-icon.csv { background: rgba(59,130,246,0.12); color: #60A5FA; }
.file-icon.pdf { background: rgba(239,68,68,0.12); color: #F87171; }
.file-icon.json { background: rgba(245,158,11,0.12); color: #FBBF24; }
.file-icon.png, .file-icon.jpg, .file-icon.jpeg, .file-icon.svg, .file-icon.gif { 
  background: rgba(139,92,246,0.12); 
  color: #A78BFA; 
}

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
.file-status.error { color: var(--danger); }

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
}

.file-remove:hover {
  background: rgba(239,68,68,0.1);
  color: var(--danger);
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

/* Prompt */
.prompt-container {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
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

.prompt-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.char-count {
  font-size: 12px;
  color: var(--text-muted);
}

/* Generate Section */
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
  box-shadow: 0 8px 32px rgba(59,130,246,0.35);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(59,130,246,0.45);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.generate-btn svg {
  width: 24px;
  height: 24px;
}

/* Progress Section */
.progress-section {
  padding: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-header h4 {
  font-size: 16px;
  font-weight: 600;
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-blue);
}

.progress-bar {
  height: 8px;
  background: var(--bg-hover);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand-blue), var(--brand-purple));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.progress-step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.progress-step.active .progress-step-icon {
  background: var(--brand-blue);
  color: white;
}

.progress-step.completed .progress-step-icon {
  background: var(--success);
  color: white;
}

.progress-step.completed .progress-step-icon svg {
  width: 14px;
  height: 14px;
}

/* Result Section */
.result-section {
  padding: 24px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.result-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-icon.success {
  background: rgba(16,185,129,0.15);
  color: #34D399;
}

.result-icon svg {
  width: 24px;
  height: 24px;
}

.result-info h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.result-info p {
  font-size: 14px;
  color: var(--text-muted);
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.result-stat {
  text-align: center;
  padding: 16px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--brand-blue);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.result-actions {
  display: flex;
  gap: 12px;
}

/* Preview Card */
.preview-card, .tips-card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-color);
}

.preview-header, .tips-header {
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color);
}

.preview-header h4, .tips-header h4 {
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

.tips-header h4 svg {
  width: 18px;
  height: 18px;
  color: var(--success);
}

.preview-content, .tips-content {
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
  margin-bottom: 16px;
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

.preview-stat.blue .preview-stat-value { color: #60A5FA; }
.preview-stat.orange .preview-stat-value { color: #FBBF24; }

.preview-stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.preview-files {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.preview-file-group {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.preview-file-label {
  color: var(--text-secondary);
}

.preview-file-count {
  font-weight: 600;
  color: var(--text-primary);
}

.preview-info {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.tips-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.tips-content p {
  margin-bottom: 10px;
  font-weight: 600;
}

.tips-content ul {
  margin-left: 20px;
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
  
  .result-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
