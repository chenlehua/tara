<template>
  <div class="document-manager">
    <!-- Upload area -->
    <div class="upload-area">
      <el-upload
        ref="uploadRef"
        drag
        :action="uploadUrl"
        :headers="uploadHeaders"
        :before-upload="beforeUpload"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :show-file-list="false"
        accept=".pdf,.docx,.doc,.xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF, Word, Excel 格式，单个文件不超过 50MB
          </div>
        </template>
      </el-upload>
    </div>

    <!-- Document list -->
    <el-table :data="documents" v-loading="loading" stripe>
      <el-table-column prop="filename" label="文件名" min-width="200">
        <template #default="{ row }">
          <div class="file-name">
            <el-icon class="file-icon"><Document /></el-icon>
            <span>{{ row.filename }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="fileType" label="类型" width="100" />
      <el-table-column prop="fileSize" label="大小" width="100">
        <template #default="{ row }">
          {{ formatFileSize(row.fileSize) }}
        </template>
      </el-table-column>
      <el-table-column prop="parseStatus" label="解析状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getParseStatusType(row.parseStatus)">
            {{ getParseStatusLabel(row.parseStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="上传时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="parseDocument(row.id)">
            解析
          </el-button>
          <el-button type="primary" link @click="viewDocument(row)">
            查看
          </el-button>
          <el-popconfirm title="确定删除该文档?" @confirm="deleteDocument(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRawFile, UploadInstance } from 'element-plus'

const props = defineProps<{
  projectId: number
}>()

const uploadRef = ref<UploadInstance>()
const loading = ref(false)
const documents = ref<any[]>([])

const uploadUrl = computed(() => `/api/v1/documents?project_id=${props.projectId}`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
}))

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

const getParseStatusType = (status: number) => {
  const types: Record<number, string> = {
    0: 'info',
    1: 'warning',
    2: 'success',
    3: 'danger',
  }
  return types[status] || 'info'
}

const getParseStatusLabel = (status: number) => {
  const labels: Record<number, string> = {
    0: '待解析',
    1: '解析中',
    2: '已完成',
    3: '失败',
  }
  return labels[status] || '未知'
}

const beforeUpload = (file: UploadRawFile) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

const onUploadSuccess = () => {
  ElMessage.success('上传成功')
  loadDocuments()
}

const onUploadError = () => {
  ElMessage.error('上传失败')
}

const loadDocuments = async () => {
  loading.value = true
  try {
    // TODO: Call API
    documents.value = []
  } catch (error) {
    console.error('Load documents failed:', error)
  } finally {
    loading.value = false
  }
}

const parseDocument = async (_id: number) => {
  ElMessage.info('开始解析文档...')
}

const viewDocument = (_doc: any) => {
  ElMessage.info('查看文档功能开发中...')
}

const deleteDocument = async (_id: number) => {
  ElMessage.success('删除成功')
  loadDocuments()
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.upload-area {
  margin-bottom: 20px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #409eff;
}
</style>
