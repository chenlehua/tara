/**
 * Tests for project store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { projectApi } from '@/api/project'

// Mock the API
vi.mock('@/api/project', () => ({
  projectApi: {
    getProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
  },
}))

describe('Project Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should initialize with empty state', () => {
    const store = useProjectStore()
    
    expect(store.projects).toEqual([])
    expect(store.currentProject).toBeNull()
    expect(store.loading).toBe(false)
  })

  it('should fetch projects', async () => {
    const mockProjects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' },
    ]
    
    ;(projectApi.getProjects as any).mockResolvedValue({
      data: { items: mockProjects, total: 2 },
    })
    
    const store = useProjectStore()
    await store.fetchProjects()
    
    expect(store.projects).toEqual(mockProjects)
    expect(store.total).toBe(2)
    expect(projectApi.getProjects).toHaveBeenCalled()
  })

  it('should set loading state while fetching', async () => {
    ;(projectApi.getProjects as any).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: { items: [], total: 0 } }), 100))
    )
    
    const store = useProjectStore()
    const fetchPromise = store.fetchProjects()
    
    expect(store.loading).toBe(true)
    
    await fetchPromise
    
    expect(store.loading).toBe(false)
  })

  it('should fetch a single project', async () => {
    const mockProject = { id: 1, name: 'Test Project' }
    
    ;(projectApi.getProject as any).mockResolvedValue({
      data: mockProject,
    })
    
    const store = useProjectStore()
    await store.fetchProject(1)
    
    expect(store.currentProject).toEqual(mockProject)
  })

  it('should create a project', async () => {
    const newProject = { name: 'New Project', vehicle_type: 'BEV' }
    const createdProject = { id: 1, ...newProject }
    
    ;(projectApi.createProject as any).mockResolvedValue({
      data: createdProject,
    })
    
    const store = useProjectStore()
    const result = await store.createProject(newProject)
    
    expect(result).toEqual(createdProject)
    expect(projectApi.createProject).toHaveBeenCalledWith(newProject)
  })

  it('should update a project', async () => {
    const updatedProject = { id: 1, name: 'Updated Project' }
    
    ;(projectApi.updateProject as any).mockResolvedValue({
      data: updatedProject,
    })
    
    const store = useProjectStore()
    store.projects = [{ id: 1, name: 'Old Project' }]
    
    await store.updateProject(1, { name: 'Updated Project' })
    
    expect(store.projects[0].name).toBe('Updated Project')
  })

  it('should delete a project', async () => {
    ;(projectApi.deleteProject as any).mockResolvedValue({})
    
    const store = useProjectStore()
    store.projects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' },
    ]
    
    await store.deleteProject(1)
    
    expect(store.projects).toHaveLength(1)
    expect(store.projects[0].id).toBe(2)
  })

  it('should handle errors', async () => {
    const error = new Error('API Error')
    ;(projectApi.getProjects as any).mockRejectedValue(error)
    
    const store = useProjectStore()
    
    await expect(store.fetchProjects()).rejects.toThrow('API Error')
    expect(store.loading).toBe(false)
  })
})
