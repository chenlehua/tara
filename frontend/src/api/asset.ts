/**
 * Asset API
 * 
 * API client for asset management.
 */

import { request, type ApiResponse } from './request'

export interface Asset {
  id: number
  project_id: number
  name: string
  asset_type: string
  category?: string
  description?: string
  interfaces?: Array<{ type: string; [key: string]: any }>
  security_attrs?: {
    confidentiality?: string
    integrity?: string
    availability?: string
  }
  criticality?: string
  source?: string
  created_at: string
  updated_at: string
}

export interface AssetListParams {
  project_id?: number
  page?: number
  page_size?: number
  asset_type?: string
  category?: string
  keyword?: string
}

export const assetApi = {
  /**
   * List assets (optionally filtered by project)
   */
  async list(params: AssetListParams = {}): Promise<ApiResponse<{ items: Asset[]; total: number }>> {
    return request.get('/assets', params)
  },

  /**
   * Get asset by ID
   */
  async get(assetId: number): Promise<ApiResponse<Asset>> {
    return request.get(`/assets/${assetId}`)
  },

  /**
   * Create a new asset
   */
  async create(data: Partial<Asset>): Promise<ApiResponse<Asset>> {
    return request.post('/assets', data)
  },

  /**
   * Update an asset
   */
  async update(assetId: number, data: Partial<Asset>): Promise<ApiResponse<Asset>> {
    return request.put(`/assets/${assetId}`, data)
  },

  /**
   * Delete an asset
   */
  async delete(assetId: number): Promise<ApiResponse<void>> {
    return request.delete(`/assets/${assetId}`)
  },
}
