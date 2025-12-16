<template>
  <div class="project-list">
    <div class="page-header">
      <h1 class="page-title">项目列表</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <!-- Filters -->
    <div class="page-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索项目名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="草稿" :value="0" />
            <el-option label="进行中" :value="1" />
            <el-option label="已完成" :value="2" />
            <el-option label="已归档" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProjects">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Project list -->
    <div class="page-card">
      <el-table :data="projects" v-loading="loading" stripe>
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/projects/${row.id}`" class="project-link">
              {{ row.name }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="vehicleType" label="车辆类型" width="120" />
        <el-table-column prop="standard" label="参考标准" width="150" />
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToProject(row.id)">查看</el-button>
            <el-button type="primary" link @click="editProject(row)">编辑</el-button>
            <el-popconfirm title="确定删除该项目?" @confirm="deleteProject(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadProjects"
          @current-change="loadProjects"
        />
      </div>
    </div>

    <!-- Create dialog -->
    <el-dialog v-model="showCreateDialog" title="新建项目" width="600px">
      <el-form :model="newProject" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="newProject.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="车辆类型" prop="vehicleType">
          <el-select v-model="newProject.vehicleType" placeholder="请选择">
            <el-option label="BEV (纯电动)" value="BEV" />
            <el-option label="HEV (混动)" value="HEV" />
            <el-option label="ICE (燃油)" value="ICE" />
            <el-option label="FCEV (氢燃料)" value="FCEV" />
          </el-select>
        </el-form-item>
        <el-form-item label="车型">
          <el-input v-model="newProject.vehicleModel" placeholder="请输入车型" />
        </el-form-item>
        <el-form-item label="参考标准">
          <el-select v-model="newProject.standard">
            <el-option label="ISO/SAE 21434" value="ISO/SAE 21434" />
            <el-option label="UN R155" value="UN R155" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="newProject.owner" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="newProject.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createProject">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { projectApi } from '@/api/project'

const router = useRouter()

const loading = ref(false)
const showCreateDialog = ref(false)
const formRef = ref<FormInstance>()

const filters = reactive({
  keyword: '',
  status: undefined as number | undefined,
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const projects = ref<any[]>([])

const newProject = reactive({
  name: '',
  vehicleType: '',
  vehicleModel: '',
  standard: 'ISO/SAE 21434',
  owner: '',
  description: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  vehicleType: [{ required: true, message: '请选择车辆类型', trigger: 'change' }],
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = { 0: 'info', 1: 'primary', 2: 'success', 3: 'warning' }
  return types[status] || 'info'
}

const getStatusLabel = (status: number) => {
  const labels: Record<number, string> = { 0: '草稿', 1: '进行中', 2: '已完成', 3: '已归档' }
  return labels[status] || '未知'
}

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await projectApi.list({
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: filters.keyword,
      status: filters.status,
    })
    if (res.success) {
      projects.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('Load projects failed:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = undefined
  pagination.page = 1
  loadProjects()
}

const goToProject = (id: number) => {
  router.push(`/projects/${id}`)
}

const editProject = (project: any) => {
  // TODO: Implement edit
}

const deleteProject = async (id: number) => {
  try {
    await projectApi.delete(id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const createProject = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await projectApi.create(newProject)
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadProjects()
      } catch (error) {
        ElMessage.error('创建失败')
      }
    }
  })
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.project-link {
  color: #409eff;
  text-decoration: none;
}

.project-link:hover {
  text-decoration: underline;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
