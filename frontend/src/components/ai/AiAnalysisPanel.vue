<template>
  <div class="ai-analysis-panel">
    <el-card class="analysis-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><MagicStick /></el-icon>
            AI 智能分析
          </span>
          <el-button
            type="primary"
            size="small"
            :loading="isAnalyzing"
            @click="startAnalysis"
          >
            {{ isAnalyzing ? '分析中...' : '开始分析' }}
          </el-button>
        </div>
      </template>

      <!-- 分析进度 -->
      <div v-if="isAnalyzing || analysisResult" class="analysis-content">
        <!-- 进度条 -->
        <div v-if="isAnalyzing" class="progress-section">
          <el-progress
            :percentage="progress"
            :stroke-width="10"
            :status="progressStatus"
          />
          <p class="progress-text">{{ progressText }}</p>
        </div>

        <!-- 分析结果 -->
        <div v-if="analysisResult" class="result-section">
          <el-collapse v-model="activeCollapse">
            <!-- 资产发现 -->
            <el-collapse-item name="assets" title="资产发现">
              <template #title>
                <el-icon><Box /></el-icon>
                <span>发现 {{ analysisResult.assets?.length || 0 }} 个资产</span>
              </template>
              <ul class="result-list">
                <li v-for="asset in analysisResult.assets" :key="asset.name">
                  <el-tag size="small" :type="getAssetTagType(asset.type)">
                    {{ asset.type }}
                  </el-tag>
                  {{ asset.name }}
                </li>
              </ul>
            </el-collapse-item>

            <!-- 威胁识别 -->
            <el-collapse-item name="threats" title="威胁识别">
              <template #title>
                <el-icon><Warning /></el-icon>
                <span>识别 {{ analysisResult.threats?.length || 0 }} 个威胁</span>
              </template>
              <ul class="result-list">
                <li v-for="threat in analysisResult.threats" :key="threat.name">
                  <el-tag size="small" type="danger">
                    {{ threat.stride_type }}
                  </el-tag>
                  {{ threat.name }}
                </li>
              </ul>
            </el-collapse-item>

            <!-- 风险评估 -->
            <el-collapse-item name="risks" title="风险评估">
              <template #title>
                <el-icon><DataAnalysis /></el-icon>
                <span>风险分布概览</span>
              </template>
              <div class="risk-summary">
                <div
                  v-for="(count, level) in analysisResult.riskSummary"
                  :key="level"
                  class="risk-item"
                >
                  <span class="risk-level" :style="{ color: getRiskColor(String(level)) }">
                    {{ level }}
                  </span>
                  <span class="risk-count">{{ count }}</span>
                </div>
              </div>
            </el-collapse-item>

            <!-- 建议措施 -->
            <el-collapse-item name="recommendations" title="安全建议">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>{{ analysisResult.recommendations?.length || 0 }} 条建议</span>
              </template>
              <ul class="recommendation-list">
                <li
                  v-for="(rec, index) in analysisResult.recommendations"
                  :key="index"
                >
                  <el-tag size="small" :type="getPriorityType(rec.priority)">
                    {{ rec.priority }}
                  </el-tag>
                  {{ rec.description }}
                </li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="点击上方按钮开始 AI 智能分析">
          <template #image>
            <el-icon :size="64" color="#c0c4cc"><MagicStick /></el-icon>
          </template>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  MagicStick,
  Box,
  Warning,
  DataAnalysis,
  Document,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const props = defineProps<{
  projectId: number
}>()

const emit = defineEmits<{
  (e: 'analysis-complete', result: any): void
}>()

const isAnalyzing = ref(false)
const progress = ref(0)
const progressText = ref('')
const analysisResult = ref<any>(null)
const activeCollapse = ref(['assets', 'threats', 'risks', 'recommendations'])

const progressStatus = computed(() => {
  if (progress.value === 100) return 'success'
  return undefined
})

// 开始分析
const startAnalysis = async () => {
  isAnalyzing.value = true
  progress.value = 0
  analysisResult.value = null

  try {
    // 阶段1: 文档分析
    progressText.value = '正在分析文档...'
    await simulateProgress(0, 25)

    // 阶段2: 资产发现
    progressText.value = '正在识别资产...'
    await simulateProgress(25, 50)

    // 阶段3: 威胁分析
    progressText.value = '正在分析威胁...'
    await simulateProgress(50, 75)

    // 阶段4: 风险评估
    progressText.value = '正在评估风险...'
    await simulateProgress(75, 90)

    // 调用实际API
    const response = await request({
      url: '/agent/analyze',
      method: 'post',
      data: { project_id: props.projectId },
    })

    progress.value = 100
    progressText.value = '分析完成!'

    // 模拟结果（实际应使用API返回的数据）
    analysisResult.value = response.data || {
      assets: [
        { name: 'Gateway ECU', type: 'gateway' },
        { name: 'Engine ECU', type: 'ecu' },
        { name: 'CAN Bus', type: 'bus' },
      ],
      threats: [
        { name: 'CAN消息注入', stride_type: 'Tampering' },
        { name: 'ECU固件篡改', stride_type: 'Tampering' },
        { name: '诊断接口滥用', stride_type: 'Elevation of Privilege' },
      ],
      riskSummary: {
        Critical: 1,
        High: 3,
        Medium: 5,
        Low: 4,
      },
      recommendations: [
        { priority: '高', description: '实施CAN消息认证机制' },
        { priority: '高', description: '启用安全启动和固件签名验证' },
        { priority: '中', description: '加强OBD端口访问控制' },
      ],
    }

    emit('analysis-complete', analysisResult.value)
    ElMessage.success('AI分析完成')
  } catch (error) {
    console.error('Analysis failed:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    isAnalyzing.value = false
  }
}

// 模拟进度
const simulateProgress = (start: number, end: number): Promise<void> => {
  return new Promise((resolve) => {
    const step = (end - start) / 10
    let current = start

    const interval = setInterval(() => {
      current += step
      progress.value = Math.min(current, end)

      if (current >= end) {
        clearInterval(interval)
        resolve()
      }
    }, 100)
  })
}

// 获取资产标签类型
const getAssetTagType = (type: string): string => {
  const types: Record<string, string> = {
    ecu: 'primary',
    gateway: 'success',
    bus: 'info',
    sensor: 'warning',
    actuator: 'danger',
  }
  return types[type] || 'info'
}

// 获取风险颜色
const getRiskColor = (level: string): string => {
  const colors: Record<string, string> = {
    Critical: '#ff0000',
    High: '#ff6600',
    Medium: '#ffcc00',
    Low: '#00cc00',
    Negligible: '#999999',
  }
  return colors[level] || '#999999'
}

// 获取优先级类型
const getPriorityType = (priority: string): string => {
  const types: Record<string, string> = {
    高: 'danger',
    中: 'warning',
    低: 'info',
  }
  return types[priority] || 'info'
}
</script>

<style scoped lang="scss">
.ai-analysis-panel {
  .analysis-card {
    :deep(.el-card__header) {
      padding: 16px 20px;
      background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    span {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      color: #303133;
    }
  }

  .progress-section {
    text-align: center;
    padding: 24px;

    .progress-text {
      margin-top: 16px;
      color: #606266;
    }
  }

  .result-section {
    :deep(.el-collapse-item__header) {
      font-weight: 500;

      .el-icon {
        margin-right: 8px;
      }
    }
  }

  .result-list {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      display: flex;
      align-items: center;
      gap: 8px;

      &:last-child {
        border-bottom: none;
      }
    }
  }

  .risk-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    .risk-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .risk-level {
        font-weight: 600;
      }

      .risk-count {
        background: #f0f0f0;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
      }
    }
  }

  .recommendation-list {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      padding: 8px 0;
      display: flex;
      align-items: flex-start;
      gap: 8px;

      .el-tag {
        flex-shrink: 0;
      }
    }
  }

  .empty-state {
    padding: 40px;
  }
}
</style>
