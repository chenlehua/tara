/**
 * Knowledge Base API
 */
import request, { type ApiResponse } from './request'

export interface KnowledgeDocument {
  document_id: string
  filename: string
  project_id?: number
  category: string
  tags: string[]
  total_chunks: number
  indexed_chunks: number
  content_length: number
  created_at: string
}

export interface SearchResult {
  chunk_id: string
  document_id: string
  filename?: string
  content: string
  score: number
  search_type: string
}

export interface KnowledgeStats {
  total_documents: number
  total_chunks: number
  categories: string[]
  es_available: boolean
  milvus_available: boolean
  es_doc_count?: number
  milvus_row_count?: number
}

export interface UploadParams {
  file: File
  project_id?: number
  category?: string
  tags?: string
}

export interface SearchParams {
  query: string
  search_type?: 'vector' | 'fulltext' | 'hybrid'
  project_id?: number
  category?: string
  top_k?: number
}

export interface ListParams {
  project_id?: number
  category?: string
  page?: number
  page_size?: number
}

export const knowledgeApi = {
  /**
   * Upload a document to the knowledge base
   */
  async upload(params: UploadParams): Promise<ApiResponse<KnowledgeDocument>> {
    const formData = new FormData()
    formData.append('file', params.file)
    if (params.project_id) {
      formData.append('project_id', params.project_id.toString())
    }
    formData.append('category', params.category || 'general')
    if (params.tags) {
      formData.append('tags', params.tags)
    }
    return request.post('/knowledge/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /**
   * List documents in the knowledge base
   */
  async list(params: ListParams = {}): Promise<ApiResponse<{ items: KnowledgeDocument[]; total: number }>> {
    const queryParams: Record<string, unknown> = {}
    if (params.project_id !== undefined) queryParams.project_id = params.project_id
    if (params.category !== undefined) queryParams.category = params.category
    if (params.page !== undefined) queryParams.page = params.page
    if (params.page_size !== undefined) queryParams.page_size = params.page_size
    return request.get('/knowledge/documents', queryParams)
  },

  /**
   * Get document details
   */
  async get(documentId: string): Promise<ApiResponse<KnowledgeDocument>> {
    return request.get(`/knowledge/documents/${documentId}`)
  },

  /**
   * Delete a document
   */
  async delete(documentId: string): Promise<ApiResponse<void>> {
    return request.delete(`/knowledge/documents/${documentId}`)
  },

  /**
   * Search the knowledge base
   */
  async search(params: SearchParams): Promise<ApiResponse<{ query: string; results: SearchResult[]; total: number }>> {
    const queryParams: Record<string, unknown> = { query: params.query }
    if (params.search_type !== undefined) queryParams.search_type = params.search_type
    if (params.project_id !== undefined) queryParams.project_id = params.project_id
    if (params.category !== undefined) queryParams.category = params.category
    if (params.top_k !== undefined) queryParams.top_k = params.top_k
    return request.post('/knowledge/search', null, { params: queryParams })
  },

  /**
   * Get knowledge base statistics
   */
  async getStats(): Promise<ApiResponse<KnowledgeStats>> {
    return request.get('/knowledge/stats')
  },

  /**
   * List categories
   */
  async listCategories(): Promise<ApiResponse<{ categories: string[] }>> {
    return request.get('/knowledge/categories')
  },

  /**
   * Reindex a document
   */
  async reindex(documentId: string): Promise<ApiResponse<void>> {
    return request.post(`/knowledge/documents/${documentId}/reindex`)
  },
}
