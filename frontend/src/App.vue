<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  // Check authentication on app mount
  userStore.checkAuth()
})
</script>

<style>
/* Global styles are imported in main.ts */
</style>
