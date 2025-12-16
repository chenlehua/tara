/**
 * Threat API
 * 
 * API client for threat and risk management.
 */

import { request, type ApiResponse } from './request'

export interface Threat {
  id: number
  project_id: number
  asset_id?: number
  threat_name: string
  threat_type: string  // S, T, R, I, D, E
  threat_desc?: string
  attack_vector?: string
  attack_surface?: string
  likelihood?: number
  safety_impact?: number
  financial_impact?: number
  operational_impact?: number
  privacy_impact?: number
  impact_level?: number
  risk_value?: number
  risk_level?: string  // CAL-1, CAL-2, CAL-3, CAL-4
  treatment?: string
  source?: string
  created_at: string
  updated_at: string
}

export interface ThreatListParams {
  project_id?: number
  page?: number
  page_size?: number
  asset_id?: number
  threat_type?: string
  risk_level?: string
}

export interface RiskDistribution {
  'CAL-4': number
  'CAL-3': number
  'CAL-2': number
  'CAL-1': number
}

export const threatApi = {
  /**
   * List threats (optionally filtered by project)
   */
  async list(params: ThreatListParams = {}): Promise<ApiResponse<{ items: Threat[]; total: number }>> {
    return request.get('/threats', params)
  },

  /**
   * Get threat by ID
   */
  async get(threatId: number): Promise<ApiResponse<Threat>> {
    return request.get(`/threats/${threatId}`)
  },

  /**
   * Create a new threat
   */
  async create(data: Partial<Threat>): Promise<ApiResponse<Threat>> {
    return request.post('/threats', data)
  },

  /**
   * Update a threat
   */
  async update(threatId: number, data: Partial<Threat>): Promise<ApiResponse<Threat>> {
    return request.put(`/threats/${threatId}`, data)
  },

  /**
   * Delete a threat
   */
  async delete(threatId: number): Promise<ApiResponse<void>> {
    return request.delete(`/threats/${threatId}`)
  },

  /**
   * Calculate risk distribution from threats
   */
  calculateDistribution(threats: Threat[]): RiskDistribution {
    const distribution: RiskDistribution = {
      'CAL-4': 0,
      'CAL-3': 0,
      'CAL-2': 0,
      'CAL-1': 0,
    }
    
    threats.forEach(threat => {
      const level = threat.risk_level as keyof RiskDistribution
      if (level && level in distribution) {
        distribution[level]++
      }
    })
    
    return distribution
  },

  /**
   * Get STRIDE category info
   */
  getStrideInfo(type: string): { name: string; nameCn: string; color: string; bgColor: string } {
    const strideMap: Record<string, { name: string; nameCn: string; color: string; bgColor: string }> = {
      'S': { name: 'Spoofing', nameCn: '身份伪造', color: '#60A5FA', bgColor: 'rgba(59,130,246,0.12)' },
      'T': { name: 'Tampering', nameCn: '数据篡改', color: '#A78BFA', bgColor: 'rgba(139,92,246,0.12)' },
      'R': { name: 'Repudiation', nameCn: '抵赖', color: '#F472B6', bgColor: 'rgba(236,72,153,0.12)' },
      'I': { name: 'Info Disclosure', nameCn: '信息泄露', color: '#FBBF24', bgColor: 'rgba(245,158,11,0.12)' },
      'D': { name: 'Denial of Service', nameCn: '拒绝服务', color: '#F87171', bgColor: 'rgba(239,68,68,0.12)' },
      'E': { name: 'Elevation', nameCn: '权限提升', color: '#34D399', bgColor: 'rgba(16,185,129,0.12)' },
    }
    return strideMap[type] || { name: 'Unknown', nameCn: '未知', color: '#94A3B8', bgColor: 'rgba(148,163,184,0.12)' }
  },
}
