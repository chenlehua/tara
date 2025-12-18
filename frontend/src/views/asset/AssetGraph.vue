<template>
  <div class="asset-graph">
    <div class="page-header">
      <h1 class="page-title">资产图谱</h1>
    </div>

    <div class="page-card graph-container">
      <div class="graph-placeholder">
        <el-icon :size="64" color="#dcdfe6"><Share /></el-icon>
        <p>资产关系图谱将在此处展示</p>
        <p class="hint">请先选择项目并完成资产识别</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

.graph-container {
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.graph-placeholder {
  text-align: center;
  color: #909399;
}

.graph-placeholder p {
  margin-top: 16px;
}

.graph-placeholder .hint {
  font-size: 14px;
  color: #c0c4cc;
}
</style>
