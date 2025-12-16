import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatResponse {
  content: string
  sources?: string[]
  suggestions?: string[]
  metadata?: Record<string, any>
}

export interface ChatHistory {
  id: string
  projectId?: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for AI responses
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const chatApi = {
  /**
   * Send a message to the AI assistant
   */
  async sendMessage(
    message: string,
    projectId?: string,
    context?: Record<string, any>
  ): Promise<ChatResponse> {
    try {
      const response = await api.post('/agent/chat', {
        message,
        project_id: projectId,
        context
      })
      return response.data
    } catch (error) {
      console.error('Chat API error:', error)
      throw error
    }
  },

  /**
   * Send a message with streaming response
   */
  async sendMessageStream(
    message: string,
    projectId?: string,
    onChunk?: (chunk: string) => void
  ): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/agent/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
        },
        body: JSON.stringify({
          message,
          project_id: projectId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        fullContent += chunk
        
        if (onChunk) {
          onChunk(chunk)
        }
      }

      return {
        content: fullContent,
        sources: []
      }
    } catch (error) {
      console.error('Stream chat error:', error)
      throw error
    }
  },

  /**
   * Get chat history
   */
  async getChatHistory(projectId?: string): Promise<ChatHistory[]> {
    try {
      const params = projectId ? { project_id: projectId } : {}
      const response = await api.get('/agent/chat/history', { params })
      return response.data
    } catch (error) {
      console.error('Get chat history error:', error)
      throw error
    }
  },

  /**
   * Clear chat history
   */
  async clearChatHistory(projectId?: string): Promise<void> {
    try {
      const params = projectId ? { project_id: projectId } : {}
      await api.delete('/agent/chat/history', { params })
    } catch (error) {
      console.error('Clear chat history error:', error)
      throw error
    }
  },

  /**
   * Quick action - Threat Analysis
   */
  async analyzeThreat(assetId: string): Promise<ChatResponse> {
    return this.sendMessage(
      `请对资产 ${assetId} 进行STRIDE威胁分析`,
      undefined,
      { action: 'threat_analysis', asset_id: assetId }
    )
  },

  /**
   * Quick action - Risk Calculation
   */
  async calculateRisk(threatId: string): Promise<ChatResponse> {
    return this.sendMessage(
      `请计算威胁 ${threatId} 的CAL风险等级`,
      undefined,
      { action: 'risk_calculation', threat_id: threatId }
    )
  },

  /**
   * Quick action - Measure Recommendation
   */
  async recommendMeasures(threatId: string): Promise<ChatResponse> {
    return this.sendMessage(
      `请为威胁 ${threatId} 推荐安全措施`,
      undefined,
      { action: 'measure_recommendation', threat_id: threatId }
    )
  },

  /**
   * Quick action - Attack Path Analysis
   */
  async analyzeAttackPath(assetId: string): Promise<ChatResponse> {
    return this.sendMessage(
      `请分析资产 ${assetId} 的攻击路径`,
      undefined,
      { action: 'attack_path', asset_id: assetId }
    )
  }
}

export default chatApi
