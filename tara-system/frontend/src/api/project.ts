import { request, type ApiResponse } from './request'

export interface Project {
  id: number
  name: string
  description?: string
  vehicleType?: string
  vehicleModel?: string
  vehicleYear?: string
  standard: string
  scope?: string
  status: number
  owner?: string
  team: string[]
  tags: string[]
  createdAt: string
  updatedAt: string
}

export interface ProjectListParams {
  page?: number
  pageSize?: number
  keyword?: string
  status?: number
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  pageSize: number
  pages: number
}

export interface CreateProjectData {
  name: string
  description?: string
  vehicleType?: string
  vehicleModel?: string
  vehicleYear?: string
  standard?: string
  scope?: string
  owner?: string
  team?: string[]
  tags?: string[]
}

export const projectApi = {
  /**
   * Get project list
   */
  list(params: ProjectListParams): Promise<ApiResponse<ProjectListResponse>> {
    return request.get('/projects', params)
  },

  /**
   * Get project by ID
   */
  get(id: number, includeStats = false): Promise<ApiResponse<Project>> {
    return request.get(`/projects/${id}`, { includeStats })
  },

  /**
   * Create project
   */
  create(data: CreateProjectData): Promise<ApiResponse<Project>> {
    return request.post('/projects', data)
  },

  /**
   * Update project
   */
  update(id: number, data: Partial<CreateProjectData>): Promise<ApiResponse<Project>> {
    return request.put(`/projects/${id}`, data)
  },

  /**
   * Delete project
   */
  delete(id: number): Promise<ApiResponse<void>> {
    return request.delete(`/projects/${id}`)
  },

  /**
   * Clone project
   */
  clone(id: number, name: string, options?: {
    includeDocuments?: boolean
    includeAssets?: boolean
    includeThreats?: boolean
  }): Promise<ApiResponse<Project>> {
    return request.post(`/projects/${id}/clone`, {
      name,
      ...options,
    })
  },

  /**
   * Get project stats
   */
  getStats(id: number): Promise<ApiResponse<any>> {
    return request.get(`/projects/${id}/stats`)
  },

  /**
   * Update project status
   */
  updateStatus(id: number, status: number): Promise<ApiResponse<Project>> {
    return request.patch(`/projects/${id}/status`, null, {
      params: { status },
    })
  },
}
