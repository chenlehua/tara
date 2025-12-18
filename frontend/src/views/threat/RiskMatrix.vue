<template>
  <div class="risk-matrix">
    <div class="page-header">
      <h1 class="page-title">风险矩阵</h1>
    </div>

    <div class="page-card">
      <h3 class="card-title">ISO/SAE 21434 风险矩阵</h3>
      
      <div class="matrix-container">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="corner-cell">影响 / 可能性</th>
              <th>低 (Low)</th>
              <th>中 (Medium)</th>
              <th>高 (High)</th>
              <th>非常高 (Very High)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="row-header">严重 (Severe)</td>
              <td class="risk-high">高</td>
              <td class="risk-critical">严重</td>
              <td class="risk-critical">严重</td>
              <td class="risk-critical">严重</td>
            </tr>
            <tr>
              <td class="row-header">重大 (Major)</td>
              <td class="risk-medium">中</td>
              <td class="risk-high">高</td>
              <td class="risk-critical">严重</td>
              <td class="risk-critical">严重</td>
            </tr>
            <tr>
              <td class="row-header">中等 (Moderate)</td>
              <td class="risk-low">低</td>
              <td class="risk-medium">中</td>
              <td class="risk-high">高</td>
              <td class="risk-critical">严重</td>
            </tr>
            <tr>
              <td class="row-header">轻微 (Minor)</td>
              <td class="risk-negligible">可忽略</td>
              <td class="risk-low">低</td>
              <td class="risk-medium">中</td>
              <td class="risk-high">高</td>
            </tr>
            <tr>
              <td class="row-header">可忽略 (Negligible)</td>
              <td class="risk-negligible">可忽略</td>
              <td class="risk-negligible">可忽略</td>
              <td class="risk-low">低</td>
              <td class="risk-medium">中</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="legend">
        <h4>风险等级说明</h4>
        <div class="legend-items">
          <div class="legend-item">
            <span class="legend-color risk-critical-bg"></span>
            <span>严重 (Critical): 需要立即处理，采取最高优先级的安全措施</span>
          </div>
          <div class="legend-item">
            <span class="legend-color risk-high-bg"></span>
            <span>高 (High): 需要尽快处理，实施必要的安全控制</span>
          </div>
          <div class="legend-item">
            <span class="legend-color risk-medium-bg"></span>
            <span>中 (Medium): 需要计划处理，评估成本效益后决定措施</span>
          </div>
          <div class="legend-item">
            <span class="legend-color risk-low-bg"></span>
            <span>低 (Low): 可接受风险，监控即可</span>
          </div>
          <div class="legend-item">
            <span class="legend-color risk-negligible-bg"></span>
            <span>可忽略 (Negligible): 无需处理</span>
          </div>
        </div>
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

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.matrix-container {
  margin-bottom: 30px;
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.matrix-table th,
.matrix-table td {
  padding: 16px;
  border: 1px solid #ebeef5;
  font-size: 14px;
}

.matrix-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #606266;
}

.corner-cell {
  min-width: 150px;
}

.row-header {
  background: #f5f7fa;
  font-weight: 600;
  color: #606266;
  text-align: left;
}

.risk-critical {
  background: #fef0f0;
  color: #f56c6c;
  font-weight: 600;
}

.risk-high {
  background: #fdf6ec;
  color: #e6a23c;
  font-weight: 600;
}

.risk-medium {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.risk-low {
  background: #f0f9eb;
  color: #67c23a;
  font-weight: 600;
}

.risk-negligible {
  background: #f4f4f5;
  color: #909399;
  font-weight: 600;
}

.legend {
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.legend h4 {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 16px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}

.risk-critical-bg { background: #f56c6c; }
.risk-high-bg { background: #e6a23c; }
.risk-medium-bg { background: #409eff; }
.risk-low-bg { background: #67c23a; }
.risk-negligible-bg { background: #909399; }
</style>
