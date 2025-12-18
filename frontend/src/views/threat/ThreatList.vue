<template>
  <div class="threat-list">
    <div class="page-header">
      <h1 class="page-title">威胁分析</h1>
    </div>

    <div class="page-card">
      <p class="placeholder-text">请先选择一个项目来进行威胁分析</p>
      <el-button type="primary" @click="router.push('/projects')">
        前往项目列表
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.placeholder-text {
  color: #909399;
  margin-bottom: 16px;
}
</style>
