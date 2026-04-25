import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig
} from 'axios'
import { $message } from '@/utils/message'

// 响应数据格式定义，和后端约定
export interface ResponseData<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 在发送请求之前做些什么
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: any) => {
    // 对请求错误做些什么
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ResponseData>) => {
    const res = response.data
    // 如果返回的状态码不是200，说明出错了
    if (res.code !== 200) {
      $message.error(res.message || '请求失败')

      // 401: 未登录或token过期
      if (res.code === 401) {
        // 清除本地token
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        // 跳转到登录页
        window.location.href = '/login'
      }

      // 403: 权限不足
      if (res.code === 403) {
        $message.error('权限不足，无法访问')
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res.data
    }
  },
  (error: any) => {
    console.error('Response error:', error)
    let errorMessage = '网络错误，请稍后重试'

    if (error.response) {
      switch (error.response.status) {
        case 400:
          errorMessage = '请求参数错误'
          break
        case 401:
          errorMessage = '未登录或登录已过期，请重新登录'
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          window.location.href = '/login'
          break
        case 403:
          errorMessage = '权限不足，无法访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `请求错误 ${error.response.status}`
      }
    } else if (error.request) {
      errorMessage = '网络连接异常，请检查网络设置'
    }

    $message.error(errorMessage)
    return Promise.reject(error)
  }
)

// 封装请求方法
const request = <T = any>(config: AxiosRequestConfig): Promise<T> => {
  return service.request<any, T>(config)
}

// 封装常用方法
export const get = <T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> => {
  return request<T>({
    method: 'get',
    url,
    params,
    ...config
  })
}

export const post = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  return request<T>({
    method: 'post',
    url,
    data,
    ...config
  })
}

export const put = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  return request<T>({
    method: 'put',
    url,
    data,
    ...config
  })
}

export const del = <T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> => {
  return request<T>({
    method: 'delete',
    url,
    params,
    ...config
  })
}

// 上传文件方法
export const upload = <T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<T> => {
  const formData = new FormData()
  formData.append('file', file)

  return request<T>({
    method: 'post',
    url,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...config
  })
}

export default request
