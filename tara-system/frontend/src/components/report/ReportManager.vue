<template>
  <div class="report-manager">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-button type="primary" @click="generateReport">
        <el-icon><Document /></el-icon>
        生成报告
      </el-button>
    </div>

    <!-- Report list -->
    <el-table :data="reports" v-loading="loading" stripe>
      <el-table-column prop="name" label="报告名称" min-width="200" />
      <el-table-column prop="template" label="模板" width="150" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="生成时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="previewReport(row)">预览</el-button>
          <el-button type="primary" link @click="downloadReport(row)">下载</el-button>
          <el-popconfirm title="确定删除该报告?" @confirm="deleteReport(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Generate dialog -->
    <el-dialog v-model="showGenerateDialog" title="生成报告" width="500px">
      <el-form :model="reportConfig" label-width="100px">
        <el-form-item label="报告名称">
          <el-input v-model="reportConfig.name" placeholder="请输入报告名称" />
        </el-form-item>
        <el-form-item label="报告模板">
          <el-select v-model="reportConfig.template" placeholder="请选择模板">
            <el-option label="ISO/SAE 21434 标准模板" value="iso21434" />
            <el-option label="UN R155 标准模板" value="unr155" />
            <el-option label="简洁模板" value="simple" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出格式">
          <el-checkbox-group v-model="reportConfig.formats">
            <el-checkbox label="pdf">PDF</el-checkbox>
            <el-checkbox label="docx">Word</el-checkbox>
            <el-checkbox label="xlsx">Excel</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="reportConfig.sections">
            <el-checkbox label="overview">项目概览</el-checkbox>
            <el-checkbox label="assets">资产清单</el-checkbox>
            <el-checkbox label="threats">威胁分析</el-checkbox>
            <el-checkbox label="risks">风险评估</el-checkbox>
            <el-checkbox label="controls">控制措施</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerate" :loading="generating">
          生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  projectId: number
}>()

const loading = ref(false)
const generating = ref(false)
const showGenerateDialog = ref(false)
const reports = ref<any[]>([])

const reportConfig = reactive({
  name: '',
  template: 'iso21434',
  formats: ['pdf'],
  sections: ['overview', 'assets', 'threats', 'risks', 'controls'],
})

const getStatusType = (status: number) => {
  const types: Record<number, string> = {
    0: 'info',
    1: 'warning',
    2: 'success',
    3: 'danger',
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: number) => {
  const labels: Record<number, string> = {
    0: '待生成',
    1: '生成中',
    2: '已完成',
    3: '失败',
  }
  return labels[status] || '未知'
}

const loadReports = async () => {
  loading.value = true
  try {
    // TODO: Call API
    reports.value = []
  } catch (error) {
    console.error('Load reports failed:', error)
  } finally {
    loading.value = false
  }
}

const generateReport = () => {
  reportConfig.name = `TARA报告_${new Date().toISOString().slice(0, 10)}`
  showGenerateDialog.value = true
}

const confirmGenerate = async () => {
  generating.value = true
  try {
    // TODO: Call API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('报告生成任务已提交')
    showGenerateDialog.value = false
    loadReports()
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}

const previewReport = (report: any) => {
  ElMessage.info('预览功能开发中...')
}

const downloadReport = (report: any) => {
  ElMessage.info('下载功能开发中...')
}

const deleteReport = async (id: number) => {
  ElMessage.success('删除成功')
  loadReports()
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
}
</style>
