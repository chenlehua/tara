/**
 * Measure API
 * 
 * API client for control measures management.
 */

import { request, type ApiResponse } from './request'

export interface ControlMeasure {
  id: number
  attack_path_id: number
  threat_risk_id?: number
  name: string
  control_type: string  // prevention, detection, response
  category?: string
  description?: string
  implementation?: string
  effectiveness?: number
  cost?: string
  priority?: number
  status?: string
  iso21434_ref?: string
  created_at: string
  updated_at: string
}

export interface MeasureListParams {
  project_id?: number
  page?: number
  page_size?: number
}

export const measureApi = {
  /**
   * List measures (optionally filtered by project)
   */
  async list(params: MeasureListParams = {}): Promise<ApiResponse<{ items: ControlMeasure[]; total: number }>> {
    return request.get('/measures', params)
  },

  /**
   * Get measure by ID
   */
  async get(measureId: number): Promise<ApiResponse<ControlMeasure>> {
    return request.get(`/measures/${measureId}`)
  },

  /**
   * Create a new measure
   */
  async create(data: Partial<ControlMeasure>): Promise<ApiResponse<ControlMeasure>> {
    return request.post('/measures', data)
  },

  /**
   * Update a measure
   */
  async update(measureId: number, data: Partial<ControlMeasure>): Promise<ApiResponse<ControlMeasure>> {
    return request.put(`/measures/${measureId}`, data)
  },

  /**
   * Delete a measure
   */
  async delete(measureId: number): Promise<ApiResponse<void>> {
    return request.delete(`/measures/${measureId}`)
  },
}
