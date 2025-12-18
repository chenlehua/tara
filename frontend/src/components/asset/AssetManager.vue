<template>
  <div class="asset-manager">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加资产
      </el-button>
      <el-button type="success" @click="discoverAssets">
        <el-icon><MagicStick /></el-icon>
        AI识别资产
      </el-button>
    </div>

    <!-- Asset list -->
    <el-table :data="assets" v-loading="loading" stripe row-key="id" default-expand-all>
      <el-table-column prop="name" label="资产名称" min-width="200" />
      <el-table-column prop="assetType" label="资产类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ getAssetTypeLabel(row.assetType) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="安全属性" width="200">
        <template #default="{ row }">
          <div class="security-attrs">
            <el-tag v-if="row.securityAttrs?.confidentiality" size="small" type="info">
              C:{{ row.securityAttrs.confidentiality }}
            </el-tag>
            <el-tag v-if="row.securityAttrs?.integrity" size="small" type="warning">
              I:{{ row.securityAttrs.integrity }}
            </el-tag>
            <el-tag v-if="row.securityAttrs?.availability" size="small" type="success">
              A:{{ row.securityAttrs.availability }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewAsset(row)">详情</el-button>
          <el-button type="primary" link @click="editAsset(row)">编辑</el-button>
          <el-popconfirm title="确定删除该资产?" @confirm="deleteAsset(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create dialog -->
    <el-dialog v-model="showCreateDialog" title="添加资产" width="600px">
      <el-form :model="newAsset" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="newAsset.name" placeholder="请输入资产名称" />
        </el-form-item>
        <el-form-item label="资产类型" prop="assetType">
          <el-select v-model="newAsset.assetType" placeholder="请选择">
            <el-option label="ECU" value="ecu" />
            <el-option label="通信总线" value="bus" />
            <el-option label="传感器" value="sensor" />
            <el-option label="执行器" value="actuator" />
            <el-option label="网关" value="gateway" />
            <el-option label="外部接口" value="external_interface" />
            <el-option label="数据" value="data" />
            <el-option label="功能" value="function" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newAsset.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-divider>安全属性</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="机密性">
              <el-select v-model="newAsset.confidentiality">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="完整性">
              <el-select v-model="newAsset.integrity">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可用性">
              <el-select v-model="newAsset.availability">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createAsset">创建</el-button>
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
const assets = ref<any[]>([])

const newAsset = reactive({
  name: '',
  assetType: '',
  description: '',
  confidentiality: 'medium',
  integrity: 'medium',
  availability: 'medium',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  assetType: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
}

const getAssetTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    ecu: 'ECU',
    bus: '通信总线',
    sensor: '传感器',
    actuator: '执行器',
    gateway: '网关',
    external_interface: '外部接口',
    data: '数据',
    function: '功能',
  }
  return labels[type] || type
}

const loadAssets = async () => {
  loading.value = true
  try {
    // TODO: Call API
    assets.value = []
  } catch (error) {
    console.error('Load assets failed:', error)
  } finally {
    loading.value = false
  }
}

const discoverAssets = () => {
  ElMessage.info('AI资产识别功能开发中...')
}

const viewAsset = (_asset: any) => {
  ElMessage.info('查看资产详情...')
}

const editAsset = (_asset: any) => {
  ElMessage.info('编辑资产...')
}

const deleteAsset = async (_id: number) => {
  ElMessage.success('删除成功')
  loadAssets()
}

const createAsset = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: Call API
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadAssets()
      } catch (error) {
        ElMessage.error('创建失败')
      }
    }
  })
}

onMounted(() => {
  loadAssets()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.security-attrs {
  display: flex;
  gap: 4px;
}
</style>
