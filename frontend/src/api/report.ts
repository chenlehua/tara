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
  author?: string
  reviewer?: string
  created_at: string
  updated_at: string
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
    projectId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<{ items: Report[]; total: number }>> {
    return request.get('/reports', {
      project_id: projectId,
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
  getDownloadUrl(reportId: number, format: 'pdf' | 'docx' = 'pdf'): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    return `${baseUrl}/reports/${reportId}/download?format=${format}`
  },

  /**
   * Get report preview data
   */
  async getReportPreview(reportId: number): Promise<ApiResponse<any>> {
    return request.get(`/reports/${reportId}/preview`)
  },
}
