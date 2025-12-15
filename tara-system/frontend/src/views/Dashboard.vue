<template>
  <div class="dashboard">
    <h1 class="page-title">工作台</h1>

    <!-- Stats cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="24"><Folder /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.projectCount }}</div>
            <div class="stat-label">项目总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="24"><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.assetCount }}</div>
            <div class="stat-label">资产数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="24"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.threatCount }}</div>
            <div class="stat-label">威胁数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon :size="24"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.highRiskCount }}</div>
            <div class="stat-label">高风险项</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">风险分布</h3>
          <div class="chart-container">
            <v-chart :option="riskChartOption" autoresize />
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="page-card">
          <h3 class="card-title">威胁类型分布 (STRIDE)</h3>
          <div class="chart-container">
            <v-chart :option="strideChartOption" autoresize />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Recent projects -->
    <div class="page-card">
      <h3 class="card-title">最近项目</h3>
      <el-table :data="recentProjects" stripe>
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="vehicleType" label="车辆类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToProject(row.id)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()

const stats = ref({
  projectCount: 12,
  assetCount: 156,
  threatCount: 89,
  highRiskCount: 15,
})

const recentProjects = ref([
  { id: 1, name: '新能源汽车TARA分析', vehicleType: 'BEV', status: 1, updatedAt: '2024-01-15 14:30' },
  { id: 2, name: '智能座舱安全评估', vehicleType: 'ICE', status: 2, updatedAt: '2024-01-14 10:20' },
  { id: 3, name: 'ADAS系统威胁分析', vehicleType: 'HEV', status: 0, updatedAt: '2024-01-13 16:45' },
])

const riskChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 3, name: '严重', itemStyle: { color: '#f56c6c' } },
      { value: 12, name: '高', itemStyle: { color: '#e6a23c' } },
      { value: 28, name: '中', itemStyle: { color: '#409eff' } },
      { value: 35, name: '低', itemStyle: { color: '#67c23a' } },
      { value: 11, name: '可忽略', itemStyle: { color: '#909399' } },
    ],
  }],
}))

const strideChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['欺骗(S)', '篡改(T)', '否认(R)', '信息泄露(I)', '拒绝服务(D)', '权限提升(E)'],
  },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [15, 22, 8, 18, 12, 14],
    itemStyle: { color: '#409eff' },
  }],
}))

const getStatusType = (status: number) => {
  const types: Record<number, string> = { 0: 'info', 1: 'primary', 2: 'success', 3: 'warning' }
  return types[status] || 'info'
}

const getStatusLabel = (status: number) => {
  const labels: Record<number, string> = { 0: '草稿', 1: '进行中', 2: '已完成', 3: '已归档' }
  return labels[status] || '未知'
}

const goToProject = (id: number) => {
  router.push(`/projects/${id}`)
}
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.chart-container {
  height: 300px;
}
</style>
