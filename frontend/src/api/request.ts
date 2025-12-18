import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// API response interface
export interface ApiResponse<T = any> {
  success: boolean
  code: number
  message: string
  data: T
}

// Create axios instance
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
service.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data
    
    // Handle case where response doesn't have expected format
    if (res === null || res === undefined) {
      return {
        success: true,
        code: 200,
        message: 'success',
        data: null
      } as any
    }
    
    // If response already has success field, use it
    if (typeof res.success === 'boolean') {
      if (!res.success) {
        ElMessage.error(res.message || '请求失败')
        return Promise.reject(new Error(res.message || 'Error'))
      }
      return res as any
    }
    
    // If response doesn't have success field but has data, wrap it
    // This handles legacy or non-standard responses
    return {
      success: true,
      code: 200,
      message: 'success',
      data: res
    } as any
  },
  (error) => {
    console.error('Response error:', error)
    
    let message = '请求失败'
    if (error.response) {
      // Try to get message from response body
      const responseData = error.response.data
      if (responseData?.message) {
        message = responseData.message
      } else {
        switch (error.response.status) {
          case 401:
            message = '未授权，请重新登录'
            break
          case 403:
            message = '拒绝访问'
            break
          case 404:
            message = '资源不存在'
            break
          case 500:
            message = responseData?.message || '服务器错误'
            break
          default:
            message = responseData?.message || '请求失败'
        }
      }
    } else if (error.message?.includes('timeout')) {
      message = '请求超时'
    } else if (error.message?.includes('Network Error')) {
      message = '网络连接失败，请检查服务是否启动'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// Request methods
export const request = {
  get<T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.get(url, { params, ...config })
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.put(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.delete(url, config)
  },
  
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.patch(url, data, config)
  },
}

export default service
