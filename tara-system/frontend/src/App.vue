<template>
  <el-config-provider :locale="locale">
    <router-view />
    <!-- 全局 AI 对话助手 -->
    <AiChat :project-id="currentProjectId" />
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { AiChat } from '@/components/ai'

const locale = zhCn
const route = useRoute()

// 获取当前项目ID（如果在项目详情页）
const currentProjectId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : undefined
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
