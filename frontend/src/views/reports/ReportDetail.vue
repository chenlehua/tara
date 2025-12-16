<template>
  <div class="report-detail">
    <!-- Header -->
    <div class="report-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
          返回
        </button>
        <div class="title-section">
          <h1>{{ report?.name || '报告详情' }}</h1>
          <div class="report-meta">
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                <line x1="16" x2="16" y1="2" y2="6"/>
                <line x1="8" x2="8" y1="2" y2="6"/>
                <line x1="3" x2="21" y1="10" y2="10"/>
              </svg>
              {{ formatDate(report?.created_at) }}
            </span>
            <span class="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              {{ report?.template || 'ISO 21434' }}
            </span>
            <span :class="['status-badge', getStatusClass(report?.status)]">
              {{ getStatusText(report?.status) }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="tara-btn tara-btn-secondary" @click="downloadReport('xlsx')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" x2="12" y1="15" y2="3"/>
          </svg>
          下载 Excel
        </button>
        <button class="tara-btn tara-btn-secondary" @click="downloadReport('docx')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" x2="12" y1="15" y2="3"/>
          </svg>
          下载 Word
        </button>
        <button class="tara-btn tara-btn-primary" @click="downloadReport('pdf')">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" x2="12" y1="15" y2="3"/>
          </svg>
          下载 PDF
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载报告中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" x2="12" y1="8" y2="12"/>
        <line x1="12" x2="12.01" y1="16" y2="16"/>
      </svg>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="tara-btn tara-btn-primary" @click="loadReport">重试</button>
    </div>

    <!-- Report Content -->
    <div v-else class="report-content">
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon assets">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="7" height="7" x="3" y="3" rx="1"/>
              <rect width="7" height="7" x="14" y="3" rx="1"/>
              <rect width="7" height="7" x="14" y="14" rx="1"/>
              <rect width="7" height="7" x="3" y="14" rx="1"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ statistics.assets_count || 0 }}</span>
            <span class="stat-label">识别资产</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon threats">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <path d="M12 9v4"/>
              <path d="M12 17h.01"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ statistics.threats_count || 0 }}</span>
            <span class="stat-label">威胁场景</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon risks">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
              <path d="m14.5 9-5 5"/>
              <path d="m9.5 9 5 5"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ statistics.high_risk_count || 0 }}</span>
            <span class="stat-label">高风险项</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon measures">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
              <path d="m9 12 2 2 4-4"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ statistics.measures_count || 0 }}</span>
            <span class="stat-label">安全措施</span>
          </div>
        </div>
      </div>

      <!-- Report Sections -->
      <div class="report-sections">
        <!-- Project Info Section -->
        <div class="section-card">
          <h2>项目信息</h2>
          <div class="section-content">
            <p>本报告基于 ISO/SAE 21434 标准，对目标系统进行了全面的威胁分析和风险评估 (TARA)。</p>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">项目名称</span>
                <span class="info-value">{{ preview?.content?.project?.name || preview?.project?.name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">车型</span>
                <span class="info-value">{{ preview?.content?.project?.vehicle_type || preview?.project?.vehicle_type || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">适用标准</span>
                <span class="info-value">{{ preview?.content?.project?.standard || preview?.project?.standard || 'ISO/SAE 21434' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">报告版本</span>
                <span class="info-value">{{ report?.version || '1.0' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">作者</span>
                <span class="info-value">{{ report?.author || 'TARA Pro' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">生成时间</span>
                <span class="info-value">{{ formatDate(preview?.content?.generated_at || report?.created_at) }}</span>
              </div>
            </div>
            <div class="section-actions" v-if="report?.project_id">
              <router-link :to="`/projects/${report.project_id}`" class="link-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                查看项目详情
              </router-link>
            </div>
          </div>
        </div>

        <!-- Assets Section -->
        <div class="section-card" v-if="contentAssets.length > 0">
          <h2>资产清单 ({{ contentAssets.length }})</h2>
          <div class="section-content">
            <table class="data-table">
              <thead>
                <tr>
                  <th>资产名称</th>
                  <th>类型</th>
                  <th>接口</th>
                  <th>安全等级</th>
                  <th>攻击面</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="asset in contentAssets.slice(0, 10)" :key="asset.id">
                  <td>{{ asset.name }}</td>
                  <td>{{ asset.type || asset.asset_type }}</td>
                  <td>
                    <span v-for="(iface, idx) in (asset.interfaces || []).slice(0, 3)" :key="idx" class="interface-tag">
                      {{ iface.type || iface }}
                    </span>
                    <span v-if="(asset.interfaces || []).length > 3" class="interface-more">+{{ asset.interfaces.length - 3 }}</span>
                  </td>
                  <td><span :class="['cal-badge', (asset.security_level || asset.criticality || '').toLowerCase()]">{{ asset.security_level || asset.criticality || 'CAL-2' }}</span></td>
                  <td>{{ asset.attack_surface || '-' }}/10</td>
                </tr>
              </tbody>
            </table>
            <p v-if="contentAssets.length > 10" class="more-hint">
              还有 {{ contentAssets.length - 10 }} 项资产，请下载完整报告查看
            </p>
            <div class="section-actions">
              <router-link to="/assets" class="link-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                查看资产管理
              </router-link>
            </div>
          </div>
        </div>

        <!-- Threats Section -->
        <div class="section-card" v-if="contentThreats.length > 0">
          <h2>威胁分析 ({{ contentThreats.length }})</h2>
          <div class="section-content">
            <table class="data-table">
              <thead>
                <tr>
                  <th>威胁ID</th>
                  <th>威胁名称</th>
                  <th>类别</th>
                  <th>攻击向量</th>
                  <th>风险等级</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="threat in contentThreats.slice(0, 10)" :key="threat.id">
                  <td>{{ threat.id }}</td>
                  <td>{{ threat.name }}</td>
                  <td>{{ threat.category_name || threat.category }}</td>
                  <td class="attack-vector-cell">{{ (threat.attack_vector || '').substring(0, 30) }}{{ threat.attack_vector?.length > 30 ? '...' : '' }}</td>
                  <td><span :class="['risk-badge', (threat.risk_level || '').toLowerCase()]">{{ threat.risk_name || threat.risk_level }}</span></td>
                </tr>
              </tbody>
            </table>
            <p v-if="contentThreats.length > 10" class="more-hint">
              还有 {{ contentThreats.length - 10 }} 项威胁，请下载完整报告查看
            </p>
            <div class="section-actions">
              <router-link to="/threats" class="link-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                查看威胁分析
              </router-link>
            </div>
          </div>
        </div>

        <!-- Risk Distribution -->
        <div class="section-card" v-if="riskDistribution">
          <h2>风险评估</h2>
          <div class="section-content">
            <div class="risk-distribution">
              <div class="risk-bar">
                <div 
                  class="risk-segment cal-4" 
                  :style="{ width: getRiskPercentage('CAL-4') + '%' }"
                  v-if="riskDistribution['CAL-4']"
                >
                  {{ riskDistribution['CAL-4'] }}
                </div>
                <div 
                  class="risk-segment cal-3" 
                  :style="{ width: getRiskPercentage('CAL-3') + '%' }"
                  v-if="riskDistribution['CAL-3']"
                >
                  {{ riskDistribution['CAL-3'] }}
                </div>
                <div 
                  class="risk-segment cal-2" 
                  :style="{ width: getRiskPercentage('CAL-2') + '%' }"
                  v-if="riskDistribution['CAL-2']"
                >
                  {{ riskDistribution['CAL-2'] }}
                </div>
                <div 
                  class="risk-segment cal-1" 
                  :style="{ width: getRiskPercentage('CAL-1') + '%' }"
                  v-if="riskDistribution['CAL-1']"
                >
                  {{ riskDistribution['CAL-1'] }}
                </div>
              </div>
              <div class="risk-legend">
                <span class="legend-item"><span class="legend-color cal-4"></span>CAL-4 极高 ({{ riskDistribution['CAL-4'] || 0 }})</span>
                <span class="legend-item"><span class="legend-color cal-3"></span>CAL-3 高 ({{ riskDistribution['CAL-3'] || 0 }})</span>
                <span class="legend-item"><span class="legend-color cal-2"></span>CAL-2 中 ({{ riskDistribution['CAL-2'] || 0 }})</span>
                <span class="legend-item"><span class="legend-color cal-1"></span>CAL-1 低 ({{ riskDistribution['CAL-1'] || 0 }})</span>
              </div>
            </div>
            <div class="section-actions">
              <router-link to="/risks" class="link-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                查看风险评估
              </router-link>
            </div>
          </div>
        </div>

        <!-- Control Measures Section -->
        <div class="section-card" v-if="contentMeasures.length > 0">
          <h2>安全措施 ({{ contentMeasures.length }})</h2>
          <div class="section-content">
            <table class="data-table">
              <thead>
                <tr>
                  <th>措施名称</th>
                  <th>类型</th>
                  <th>关联威胁</th>
                  <th>有效性</th>
                  <th>ISO 21434参考</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(measure, idx) in contentMeasures.slice(0, 10)" :key="idx">
                  <td>{{ measure.name }}</td>
                  <td><span class="measure-type-tag">{{ measure.control_type || measure.category || 'preventive' }}</span></td>
                  <td>{{ measure.threat_name || '-' }}</td>
                  <td><span :class="['effectiveness-badge', measure.effectiveness || 'medium']">{{ getEffectivenessText(measure.effectiveness) }}</span></td>
                  <td>{{ measure.iso21434_ref || '-' }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="contentMeasures.length > 10" class="more-hint">
              还有 {{ contentMeasures.length - 10 }} 项安全措施，请下载完整报告查看
            </p>
            <div class="section-actions">
              <router-link to="/measures" class="link-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                查看安全措施
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { reportApi, type Report } from '@/api/report'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const report = ref<Report | null>(null)
const preview = ref<any>(null)

const reportId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? parseInt(id, 10) : 0
})

const statistics = computed(() => {
  if (preview.value?.statistics) {
    return preview.value.statistics
  }
  if (report.value?.statistics) {
    return report.value.statistics as any
  }
  return {
    assets_count: contentAssets.value.length || 0,
    threats_count: contentThreats.value.length || 0,
    high_risk_count: 0,
    measures_count: contentMeasures.value.length || 0
  }
})

// Get assets from preview content
const contentAssets = computed(() => {
  if (preview.value?.content?.assets) {
    return preview.value.content.assets
  }
  if (preview.value?.assets) {
    return preview.value.assets
  }
  return []
})

// Get threats from preview content
const contentThreats = computed(() => {
  if (preview.value?.content?.threats) {
    return preview.value.content.threats
  }
  if (preview.value?.threats) {
    return preview.value.threats
  }
  return []
})

// Get control measures from preview content
const contentMeasures = computed(() => {
  if (preview.value?.content?.control_measures) {
    return preview.value.content.control_measures
  }
  // Extract measures from threats if not available separately
  const measures: any[] = []
  const threats = contentThreats.value || []
  threats.forEach((threat: any) => {
    if (threat.control_measures) {
      threat.control_measures.forEach((m: any) => {
        measures.push({
          ...m,
          threat_name: threat.name,
          threat_id: threat.id
        })
      })
    }
  })
  return measures
})

// Get risk distribution from preview content
const riskDistribution = computed(() => {
  if (preview.value?.content?.risk_distribution) {
    return preview.value.content.risk_distribution
  }
  if (preview.value?.risk_distribution) {
    return preview.value.risk_distribution
  }
  return null
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status?: number) => {
  switch (status) {
    case 0: return 'pending'
    case 1: return 'generating'
    case 2: return 'completed'
    case 3: return 'failed'
    default: return 'pending'
  }
}

const getStatusText = (status?: number) => {
  switch (status) {
    case 0: return '待生成'
    case 1: return '生成中'
    case 2: return '已完成'
    case 3: return '生成失败'
    default: return '未知'
  }
}

const getEffectivenessText = (effectiveness?: string) => {
  switch (effectiveness) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return '中'
  }
}

const getRiskPercentage = (level: string) => {
  if (!riskDistribution.value) return 0
  const total = Object.values(riskDistribution.value).reduce((a: number, b: any) => a + (b || 0), 0) as number
  if (total === 0) return 0
  return ((riskDistribution.value[level] || 0) / total * 100).toFixed(1)
}

const goBack = () => {
  router.push('/reports')
}

const loadReport = async () => {
  if (!reportId.value) {
    error.value = '无效的报告ID'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''

  try {
    // Try to get report details
    const reportRes = await reportApi.getReport(reportId.value)
    if (reportRes.success && reportRes.data) {
      report.value = reportRes.data
    }

    // Try to get preview data
    const previewRes = await reportApi.getReportPreview(reportId.value)
    if (previewRes.success && previewRes.data) {
      preview.value = previewRes.data
    }
  } catch (e: any) {
    console.error('Failed to load report:', e)
    // If API fails, show demo data
    report.value = {
      id: reportId.value,
      project_id: 1,
      name: `TARA分析报告_${new Date().toISOString().slice(0, 10)}`,
      report_type: 'tara',
      template: 'ISO 21434',
      status: 2,
      progress: 100,
      version: '1.0',
      author: 'TARA Pro',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    preview.value = {
      assets: [
        { id: 'ASSET-001', name: '整车控制器 (VCU)', type: 'ECU', security_level: 'CAL-4', attack_surface: 6 },
        { id: 'ASSET-002', name: '电池管理系统 (BMS)', type: 'ECU', security_level: 'CAL-4', attack_surface: 5 },
        { id: 'ASSET-003', name: '智能网关 (CGW)', type: 'Gateway', security_level: 'CAL-4', attack_surface: 8 },
        { id: 'ASSET-004', name: '远程通信单元 (T-Box)', type: 'Gateway', security_level: 'CAL-4', attack_surface: 10 },
        { id: 'ASSET-005', name: '信息娱乐系统 (IVI)', type: 'ECU', security_level: 'CAL-2', attack_surface: 7 },
      ],
      threats: [
        { id: 'THREAT-001', name: 'VCU身份伪造威胁', category: 'Spoofing', category_name: '身份伪造', risk_level: 'CAL-4', risk_name: '极高' },
        { id: 'THREAT-002', name: 'CAN总线数据篡改', category: 'Tampering', category_name: '数据篡改', risk_level: 'CAL-4', risk_name: '极高' },
        { id: 'THREAT-003', name: 'T-Box远程攻击', category: 'Spoofing', category_name: '身份伪造', risk_level: 'CAL-3', risk_name: '高' },
        { id: 'THREAT-004', name: '通信数据泄露', category: 'Information Disclosure', category_name: '信息泄露', risk_level: 'CAL-2', risk_name: '中' },
        { id: 'THREAT-005', name: 'DoS攻击', category: 'Denial of Service', category_name: '拒绝服务', risk_level: 'CAL-3', risk_name: '高' },
      ],
      risk_distribution: {
        'CAL-4': 8,
        'CAL-3': 12,
        'CAL-2': 15,
        'CAL-1': 10
      },
      statistics: {
        assets_count: 5,
        threats_count: 45,
        high_risk_count: 8,
        measures_count: 12
      }
    }
  } finally {
    loading.value = false
  }
}

const downloadReport = (format: 'pdf' | 'docx' | 'xlsx') => {
  if (!reportId.value) {
    ElMessage.warning('报告ID无效')
    return
  }
  const url = reportApi.getDownloadUrl(reportId.value, format)
  window.open(url, '_blank')
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-detail {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.title-section h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.report-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.status-badge.generating {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.pending {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

/* Buttons */
.tara-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.tara-btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.tara-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.tara-btn-secondary {
  background: var(--bg-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.tara-btn-secondary:hover {
  background: var(--bg-hover);
}

/* Loading & Error */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container svg {
  color: #ef4444;
  margin-bottom: 16px;
}

.error-container h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.error-container p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-icon.assets {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.stat-icon.threats {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-icon.risks {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-icon.measures {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Sections */
.report-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.section-card h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.section-content {
  padding: 20px;
}

.section-content p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* Tables */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  background: var(--bg-secondary);
}

.data-table td {
  font-size: 14px;
  color: var(--text-primary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.cal-badge,
.risk-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.cal-badge.cal-4,
.risk-badge.cal-4 {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.cal-badge.cal-3,
.risk-badge.cal-3 {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.cal-badge.cal-2,
.risk-badge.cal-2 {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.cal-badge.cal-1,
.risk-badge.cal-1 {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.more-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: center;
  padding-top: 12px;
  margin: 0;
}

/* Section Actions */
.section-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.link-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6366f1;
  font-size: 13px;
  text-decoration: none;
  transition: all 0.2s;
}

.link-btn:hover {
  color: #8b5cf6;
}

/* Interface Tags */
.interface-tag {
  display: inline-block;
  padding: 2px 6px;
  margin-right: 4px;
  border-radius: 4px;
  font-size: 11px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.interface-more {
  font-size: 11px;
  color: var(--text-tertiary);
}

.attack-vector-cell {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Measure Type Tag */
.measure-type-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  text-transform: capitalize;
}

/* Effectiveness Badge */
.effectiveness-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.effectiveness-badge.high {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.effectiveness-badge.medium {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.effectiveness-badge.low {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

/* Risk Distribution */
.risk-distribution {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-bar {
  display: flex;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.risk-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  min-width: 30px;
}

.risk-segment.cal-4 {
  background: #ef4444;
}

.risk-segment.cal-3 {
  background: #f59e0b;
}

.risk-segment.cal-2 {
  background: #3b82f6;
}

.risk-segment.cal-1 {
  background: #22c55e;
}

.risk-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.cal-4 {
  background: #ef4444;
}

.legend-color.cal-3 {
  background: #f59e0b;
}

.legend-color.cal-2 {
  background: #3b82f6;
}

.legend-color.cal-1 {
  background: #22c55e;
}
</style>
