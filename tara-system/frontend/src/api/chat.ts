/**
 * Chat API for AI assistant
 */
import request from './request'

export interface ChatMessage {
  message: string
  project_id?: number
  stream?: boolean
}

export interface ChatResponse {
  success: boolean
  data: {
    message: string
    content?: string
  }
}

export const chatApi = {
  /**
   * Send a chat message to AI assistant
   */
  sendMessage(data: ChatMessage): Promise<ChatResponse> {
    return request({
      url: '/agent/chat',
      method: 'post',
      data,
    })
  },

  /**
   * Send a chat message with streaming response
   */
  sendMessageStream(data: ChatMessage): EventSource {
    const params = new URLSearchParams({
      message: data.message,
      project_id: String(data.project_id || ''),
    })
    
    return new EventSource(`/api/v1/agent/chat/stream?${params}`)
  },

  /**
   * Get chat history for a project
   */
  getChatHistory(projectId: number) {
    return request({
      url: `/agent/chat/history/${projectId}`,
      method: 'get',
    })
  },

  /**
   * Clear chat history for a project
   */
  clearChatHistory(projectId: number) {
    return request({
      url: `/agent/chat/history/${projectId}`,
      method: 'delete',
    })
  },
}
