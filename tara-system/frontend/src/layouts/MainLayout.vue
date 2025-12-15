<template>
  <div class="main-layout">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <img src="/logo.svg" alt="TARA" class="logo-img" />
          <span class="logo-text">TARA System</span>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <el-avatar :size="32" icon="User" />
            <span class="username">管理员</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人设置</el-dropdown-item>
              <el-dropdown-item divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- Main content -->
    <div class="main-content">
      <!-- Sidebar -->
      <aside class="sidebar">
        <el-menu
          :default-active="activeMenu"
          :router="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>工作台</span>
          </el-menu-item>

          <el-sub-menu index="project">
            <template #title>
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </template>
            <el-menu-item index="/projects">项目列表</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="document">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>文档解析</span>
            </template>
            <el-menu-item index="/documents">文档管理</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="asset">
            <template #title>
              <el-icon><Grid /></el-icon>
              <span>资产管理</span>
            </template>
            <el-menu-item index="/assets">资产列表</el-menu-item>
            <el-menu-item index="/assets/graph">资产图谱</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="threat">
            <template #title>
              <el-icon><Warning /></el-icon>
              <span>威胁风险</span>
            </template>
            <el-menu-item index="/threats">威胁分析</el-menu-item>
            <el-menu-item index="/risks">风险矩阵</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="report">
            <template #title>
              <el-icon><Files /></el-icon>
              <span>报告中心</span>
            </template>
            <el-menu-item index="/reports">报告列表</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>

      <!-- Content -->
      <main class="content-wrapper">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.header {
  height: var(--header-height);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.sidebar {
  height: calc(100vh - var(--header-height));
  overflow-y: auto;
}

.sidebar .el-menu {
  border-right: none;
}
</style>
