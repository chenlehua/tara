<template>
  <div class="project-detail" v-loading="loading">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()" icon="ArrowLeft" circle />
        <h1 class="page-title">{{ project?.name }}</h1>
        <el-tag :type="getStatusType(project?.status)" size="large">
          {{ getStatusLabel(project?.status) }}
        </el-tag>
      </div>
      <div class="header-right">
        <el-button @click="startAnalysis" type="success">
          <el-icon><VideoPlay /></el-icon>
          开始AI分析
        </el-button>
        <el-button type="primary">
          <el-icon><Download /></el-icon>
          生成报告
        </el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="project-tabs">
      <!-- Overview -->
      <el-tab-pane label="概览" name="overview">
        <el-row :gutter="20">
          <el-col :span="16">
            <!-- Project info -->
            <div class="page-card">
              <h3 class="card-title">项目信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="项目名称">{{ project?.name }}</el-descriptions-item>
                <el-descriptions-item label="车辆类型">{{ project?.vehicleType }}</el-descriptions-item>
                <el-descriptions-item label="车型">{{ project?.vehicleModel || '-' }}</el-descriptions-item>
                <el-descriptions-item label="年份">{{ project?.vehicleYear || '-' }}</el-descriptions-item>
                <el-descriptions-item label="参考标准">{{ project?.standard }}</el-descriptions-item>
                <el-descriptions-item label="负责人">{{ project?.owner || '-' }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ project?.createdAt }}</el-descriptions-item>
                <el-descriptions-item label="更新时间">{{ project?.updatedAt }}</el-descriptions-item>
                <el-descriptions-item label="项目描述" :span="2">
                  {{ project?.description || '无' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- Analysis progress -->
            <div class="page-card">
              <h3 class="card-title">分析进度</h3>
              <el-steps :active="analysisStep" finish-status="success">
                <el-step title="文档解析" description="上传并解析技术文档" />
                <el-step title="资产识别" description="识别系统资产和组件" />
                <el-step title="威胁分析" description="STRIDE威胁建模" />
                <el-step title="风险评估" description="评估风险等级" />
                <el-step title="报告生成" description="生成TARA报告" />
              </el-steps>
            </div>
          </el-col>

          <el-col :span="8">
            <!-- Stats -->
            <div class="page-card">
              <h3 class="card-title">统计概览</h3>
              <div class="stats-list">
                <div class="stat-item">
                  <span class="stat-label">文档数量</span>
                  <span class="stat-value">{{ stats.documentCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">资产数量</span>
                  <span class="stat-value">{{ stats.assetCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">威胁数量</span>
                  <span class="stat-value">{{ stats.threatCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">攻击路径</span>
                  <span class="stat-value">{{ stats.attackPathCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">控制措施</span>
                  <span class="stat-value">{{ stats.controlCount }}</span>
                </div>
              </div>
            </div>

            <!-- Risk summary -->
            <div class="page-card">
              <h3 class="card-title">风险分布</h3>
              <div class="risk-bars">
                <div class="risk-bar-item">
                  <div class="risk-bar-label">
                    <span class="risk-dot risk-critical"></span>
                    <span>严重</span>
                  </div>
                  <el-progress :percentage="riskPercentages.critical" color="#f56c6c" />
                </div>
                <div class="risk-bar-item">
                  <div class="risk-bar-label">
                    <span class="risk-dot risk-high"></span>
                    <span>高</span>
                  </div>
                  <el-progress :percentage="riskPercentages.high" color="#e6a23c" />
                </div>
                <div class="risk-bar-item">
                  <div class="risk-bar-label">
                    <span class="risk-dot risk-medium"></span>
                    <span>中</span>
                  </div>
                  <el-progress :percentage="riskPercentages.medium" color="#409eff" />
                </div>
                <div class="risk-bar-item">
                  <div class="risk-bar-label">
                    <span class="risk-dot risk-low"></span>
                    <span>低</span>
                  </div>
                  <el-progress :percentage="riskPercentages.low" color="#67c23a" />
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Documents -->
      <el-tab-pane label="文档" name="documents">
        <DocumentManager :projectId="projectId" />
      </el-tab-pane>

      <!-- Assets -->
      <el-tab-pane label="资产" name="assets">
        <AssetManager :projectId="projectId" />
      </el-tab-pane>

      <!-- Threats -->
      <el-tab-pane label="威胁" name="threats">
        <ThreatManager :projectId="projectId" />
      </el-tab-pane>

      <!-- Reports -->
      <el-tab-pane label="报告" name="reports">
        <ReportManager :projectId="projectId" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectApi, type Project } from '@/api/project'
import DocumentManager from '@/components/document/DocumentManager.vue'
import AssetManager from '@/components/asset/AssetManager.vue'
import ThreatManager from '@/components/threat/ThreatManager.vue'
import ReportManager from '@/components/report/ReportManager.vue'

const router = useRouter()
const route = useRoute()

const projectId = computed(() => Number(route.params.id))
const loading = ref(false)
const activeTab = ref('overview')
const analysisStep = ref(0)

const project = ref<Project | null>(null)

const stats = reactive({
  documentCount: 0,
  assetCount: 0,
  threatCount: 0,
  attackPathCount: 0,
  controlCount: 0,
})

const riskPercentages = reactive({
  critical: 10,
  high: 25,
  medium: 40,
  low: 25,
})

const getStatusType = (status?: number) => {
  if (status === undefined) return 'info'
  const types: Record<number, string> = { 0: 'info', 1: 'primary', 2: 'success', 3: 'warning' }
  return types[status] || 'info'
}

const getStatusLabel = (status?: number) => {
  if (status === undefined) return '加载中'
  const labels: Record<number, string> = { 0: '草稿', 1: '进行中', 2: '已完成', 3: '已归档' }
  return labels[status] || '未知'
}

const loadProject = async () => {
  loading.value = true
  try {
    const res = await projectApi.get(projectId.value, true)
    if (res.success) {
      project.value = res.data
    }
  } catch (error) {
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

const startAnalysis = () => {
  ElMessage.info('AI分析功能开发中...')
}

onMounted(() => {
  loadProject()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.project-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.risk-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.risk-bar-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.risk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.risk-dot.risk-critical { background: #f56c6c; }
.risk-dot.risk-high { background: #e6a23c; }
.risk-dot.risk-medium { background: #409eff; }
.risk-dot.risk-low { background: #67c23a; }
</style>
