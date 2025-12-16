<template>
  <div class="threat-manager">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加威胁
      </el-button>
      <el-button type="success" @click="analyzeThreats">
        <el-icon><MagicStick /></el-icon>
        STRIDE分析
      </el-button>
    </div>

    <!-- Threat list -->
    <el-table :data="threats" v-loading="loading" stripe>
      <el-table-column prop="threatName" label="威胁名称" min-width="200" />
      <el-table-column prop="threatType" label="STRIDE类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getStrideTagType(row.threatType)">
            {{ row.threatType }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="assetName" label="关联资产" width="150" />
      <el-table-column prop="impactLevel" label="影响" width="100">
        <template #default="{ row }">
          <span :class="'risk-' + row.impactLevel?.toLowerCase()">
            {{ getImpactLabel(row.impactLevel) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="likelihood" label="可能性" width="100">
        <template #default="{ row }">
          {{ getLikelihoodLabel(row.likelihood) }}
        </template>
      </el-table-column>
      <el-table-column prop="riskLevel" label="风险等级" width="100">
        <template #default="{ row }">
          <el-tag :type="getRiskTagType(row.riskLevel)">
            {{ getRiskLabel(row.riskLevel) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewThreat(row)">详情</el-button>
          <el-button type="primary" link @click="editThreat(row)">编辑</el-button>
          <el-popconfirm title="确定删除该威胁?" @confirm="deleteThreat(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create dialog -->
    <el-dialog v-model="showCreateDialog" title="添加威胁" width="600px">
      <el-form :model="newThreat" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="威胁名称" prop="threatName">
          <el-input v-model="newThreat.threatName" placeholder="请输入威胁名称" />
        </el-form-item>
        <el-form-item label="STRIDE类型" prop="threatType">
          <el-select v-model="newThreat.threatType" placeholder="请选择">
            <el-option label="欺骗 (Spoofing)" value="Spoofing" />
            <el-option label="篡改 (Tampering)" value="Tampering" />
            <el-option label="否认 (Repudiation)" value="Repudiation" />
            <el-option label="信息泄露 (Information Disclosure)" value="Information Disclosure" />
            <el-option label="拒绝服务 (Denial of Service)" value="Denial of Service" />
            <el-option label="权限提升 (Elevation of Privilege)" value="Elevation of Privilege" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联资产">
          <el-select v-model="newThreat.assetId" placeholder="请选择">
            <!-- TODO: Load assets -->
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newThreat.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createThreat">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

defineProps<{
  projectId: number
}>()

const loading = ref(false)
const showCreateDialog = ref(false)
const formRef = ref<FormInstance>()
const threats = ref<any[]>([])

const newThreat = reactive({
  threatName: '',
  threatType: '',
  assetId: null as number | null,
  description: '',
})

const rules: FormRules = {
  threatName: [{ required: true, message: '请输入威胁名称', trigger: 'blur' }],
  threatType: [{ required: true, message: '请选择STRIDE类型', trigger: 'change' }],
}

const getStrideTagType = (type: string) => {
  const types: Record<string, string> = {
    'Spoofing': 'danger',
    'Tampering': 'warning',
    'Repudiation': 'info',
    'Information Disclosure': 'primary',
    'Denial of Service': 'success',
    'Elevation of Privilege': 'danger',
  }
  return types[type] || ''
}

const getImpactLabel = (level: string) => {
  const labels: Record<string, string> = {
    severe: '严重',
    major: '重大',
    moderate: '中等',
    minor: '轻微',
    negligible: '可忽略',
  }
  return labels[level?.toLowerCase()] || level
}

const getLikelihoodLabel = (level: string) => {
  const labels: Record<string, string> = {
    very_high: '非常高',
    high: '高',
    medium: '中',
    low: '低',
  }
  return labels[level?.toLowerCase()] || level
}

const getRiskTagType = (level: number) => {
  if (level >= 4) return 'danger'
  if (level >= 3) return 'warning'
  if (level >= 2) return 'primary'
  if (level >= 1) return 'success'
  return 'info'
}

const getRiskLabel = (level: number) => {
  const labels: Record<number, string> = {
    5: '严重',
    4: '高',
    3: '中',
    2: '低',
    1: '可忽略',
  }
  return labels[level] || '未评估'
}

const loadThreats = async () => {
  loading.value = true
  try {
    // TODO: Call API
    threats.value = []
  } catch (error) {
    console.error('Load threats failed:', error)
  } finally {
    loading.value = false
  }
}

const analyzeThreats = () => {
  ElMessage.info('STRIDE威胁分析功能开发中...')
}

const viewThreat = (_threat: any) => {
  ElMessage.info('查看威胁详情...')
}

const editThreat = (_threat: any) => {
  ElMessage.info('编辑威胁...')
}

const deleteThreat = async (_id: number) => {
  ElMessage.success('删除成功')
  loadThreats()
}

const createThreat = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: Call API
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadThreats()
      } catch (error) {
        ElMessage.error('创建失败')
      }
    }
  })
}

onMounted(() => {
  loadThreats()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}
</style>
