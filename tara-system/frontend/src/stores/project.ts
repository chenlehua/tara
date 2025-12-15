import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi, type Project } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref<Project | null>(null)
  const projects = ref<Project[]>([])
  const loading = ref(false)

  const hasProject = computed(() => currentProject.value !== null)

  const setCurrentProject = (project: Project | null) => {
    currentProject.value = project
    if (project) {
      localStorage.setItem('currentProjectId', String(project.id))
    } else {
      localStorage.removeItem('currentProjectId')
    }
  }

  const loadProject = async (id: number) => {
    loading.value = true
    try {
      const res = await projectApi.get(id)
      if (res.success) {
        setCurrentProject(res.data)
      }
    } catch (error) {
      console.error('Load project failed:', error)
    } finally {
      loading.value = false
    }
  }

  const loadProjects = async (params?: any) => {
    loading.value = true
    try {
      const res = await projectApi.list(params)
      if (res.success) {
        projects.value = res.data.items
      }
    } catch (error) {
      console.error('Load projects failed:', error)
    } finally {
      loading.value = false
    }
  }

  const restoreCurrentProject = async () => {
    const savedId = localStorage.getItem('currentProjectId')
    if (savedId) {
      await loadProject(Number(savedId))
    }
  }

  return {
    currentProject,
    projects,
    loading,
    hasProject,
    setCurrentProject,
    loadProject,
    loadProjects,
    restoreCurrentProject,
  }
})
