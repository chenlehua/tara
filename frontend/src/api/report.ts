/**
 * Report API
 * 
 * API client for TARA report generation.
 */

import { request, type ApiResponse } from './request'

// Types
export interface GenerationProgress {
  task_id: string
  status: 'processing' | 'completed' | 'failed' | 'not_found'
  progress: number
  current_step: string
  steps: Array<{
    label: string
    completed: boolean
    active: boolean
  }>
  result?: GenerationResult
  error?: string
}

export interface GenerationResult {
  report_id: number
  project_id: number
  report_name: string
  template: string
  generated_at: string
  statistics: {
    assets_count: number
    threats_count: number
    high_risk_count: number
    measures_count: number
  }
  download_urls: {
    pdf: string
    docx: string
  }
}

export interface OneClickResponse {
  task_id: string
  report_id: number
  project_id: number
  status: string
  message: string
}

export interface Report {
  id: number
  project_id: number
  name: string
  report_type: string
  description?: string
  template?: string
  status: number
  progress: number
  file_path?: string
  file_format?: string
  file_size?: number
  version: string
  version_count?: number
  current_version_id?: number
  baseline_version_id?: number
  author?: string
  reviewer?: string
  created_at: string
  updated_at: string
  statistics?: {
    assets_count?: number
    threats_count?: number
    high_risk_count?: number
    measures_count?: number
  }
}

// Version types
export interface ReportVersion {
  id: number
  report_id: number
  version_number: string
  major_version: number
  minor_version: number
  status: string
  is_baseline: boolean
  is_current: boolean
  change_summary?: string
  change_reason?: string
  created_by?: string
  approved_by?: string
  approved_at?: string
  created_at: string
  statistics?: Record<string, any>
}

export interface ReportVersionDetail extends ReportVersion {
  content?: Record<string, any>
  sections?: Array<Record<string, any>>
  snapshot_data?: Record<string, any>
  file_paths?: Record<string, string>
  changes?: Array<{
    id: number
    change_type: string
    entity_type: string
    entity_name?: string
    field_name?: string
    old_value?: string
    new_value?: string
  }>
}

export interface VersionCompareResult {
  version_a: string
  version_b: string
  summary: {
    added: number
    modified: number
    deleted: number
  }
  changes: Array<{
    change_type: string
    entity_type: string
    entity_name?: string
    field_name?: string
    old_value?: any
    new_value?: any
    description?: string
  }>
}

// API functions
export const reportApi = {
  /**
   * One-click generate TARA report from uploaded files
   */
  async oneClickGenerate(
    files: File[],
    template: string = 'full',
    prompt: string = '',
    projectName?: string
  ): Promise<ApiResponse<OneClickResponse>> {
    const formData = new FormData()
    
    files.forEach(file => {
      formData.append('files', file)
    })
    
    formData.append('template', template)
    formData.append('prompt', prompt)
    
    if (projectName) {
      formData.append('project_name', projectName)
    }
    
    return request.post<OneClickResponse>('/reports/oneclick', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for upload
    })
  },

  /**
   * Get report generation progress
   */
  async getGenerationProgress(taskId: string): Promise<ApiResponse<GenerationProgress>> {
    return request.get<GenerationProgress>(`/reports/oneclick/${taskId}/progress`)
  },

  /**
   * List reports for a project
   */
  async listReports(
    projectId?: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<{ items: Report[]; total: number }>> {
    const params: Record<string, number> = {
      page,
      page_size: pageSize,
    }
    if (projectId !== undefined) {
      params.project_id = projectId
    }
    return request.get('/reports', params)
  },

  /**
   * List all reports without project filter
   */
  async listAllReports(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<{ items: Report[]; total: number }>> {
    return request.get('/reports/all', {
      page,
      page_size: pageSize,
    })
  },

  /**
   * Get report by ID
   */
  async getReport(reportId: number): Promise<ApiResponse<Report>> {
    return request.get<Report>(`/reports/${reportId}`)
  },

  /**
   * Delete a report
   */
  async deleteReport(reportId: number): Promise<ApiResponse<void>> {
    return request.delete(`/reports/${reportId}`)
  },

  /**
   * Download report file
   */
  getDownloadUrl(reportId: number, format: 'pdf' | 'docx' | 'xlsx' = 'pdf'): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    return `${baseUrl}/reports/${reportId}/download?format=${format}`
  },

  /**
   * Get report preview data
   */
  async getReportPreview(reportId: number): Promise<ApiResponse<any>> {
    return request.get(`/reports/${reportId}/preview`)
  },

  // ================== Version Management APIs ==================

  /**
   * List versions for a report
   */
  async listVersions(
    reportId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<{
    versions: ReportVersion[]
    total: number
    current_version?: string
    baseline_version?: string
  }>> {
    return request.get(`/reports/${reportId}/versions`, {
      page,
      page_size: pageSize,
    })
  },

  /**
   * Create a new version
   */
  async createVersion(
    reportId: number,
    options: {
      is_major?: boolean
      change_summary?: string
      change_reason?: string
      created_by?: string
    } = {}
  ): Promise<ApiResponse<ReportVersion>> {
    return request.post(`/reports/${reportId}/versions`, options)
  },

  /**
   * Get version detail
   */
  async getVersionDetail(
    reportId: number,
    versionNumber: string
  ): Promise<ApiResponse<ReportVersionDetail>> {
    return request.get(`/reports/${reportId}/versions/${versionNumber}`)
  },

  /**
   * Compare two versions
   */
  async compareVersions(
    reportId: number,
    versionA: string,
    versionB: string
  ): Promise<ApiResponse<VersionCompareResult>> {
    return request.post(`/reports/${reportId}/versions/compare`, {
      version_a: versionA,
      version_b: versionB,
    })
  },

  /**
   * Rollback to a version
   */
  async rollbackToVersion(
    reportId: number,
    versionNumber: string,
    options: {
      created_by?: string
      reason?: string
    } = {}
  ): Promise<ApiResponse<ReportVersion>> {
    return request.post(`/reports/${reportId}/versions/${versionNumber}/rollback`, options)
  },

  /**
   * Set a version as baseline
   */
  async setBaseline(
    reportId: number,
    versionNumber: string,
    comment?: string
  ): Promise<ApiResponse<ReportVersion>> {
    return request.post(`/reports/${reportId}/versions/${versionNumber}/baseline`, {
      comment,
    })
  },

  /**
   * Approve a version
   */
  async approveVersion(
    reportId: number,
    versionNumber: string,
    approvedBy: string,
    comment?: string
  ): Promise<ApiResponse<ReportVersion>> {
    return request.post(`/reports/${reportId}/versions/${versionNumber}/approve`, {
      approved_by: approvedBy,
      comment,
    })
  },

  /**
   * Get current version
   */
  async getCurrentVersion(reportId: number): Promise<ApiResponse<ReportVersion>> {
    return request.get(`/reports/${reportId}/versions/current`)
  },
}
