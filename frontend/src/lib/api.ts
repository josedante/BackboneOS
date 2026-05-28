/**
 * Phase 5 API client scope: auth + users only.
 *
 * CRM modules (products, entities, interactions, campaigns, offers) were removed —
 * Django template views call selectors/services directly (no in-app REST loopback).
 * The entire frontend package may be deleted in Phase 6 when Next is decommissioned.
 */
import https from 'https'

import axios from 'axios'

const API_BASE = process.env['NEXT_PUBLIC_API_BASE'] || 'https://backend.proyecto-opensource.orb.local'

// Only create HTTPS agent that ignores self-signed certificates in development
const isDevelopment = process.env.NODE_ENV === 'development' ||
                     process.env['NEXT_PUBLIC_NODE_ENV'] === 'development' ||
                     API_BASE.includes('localhost') ||
                     API_BASE.includes('orb.local')

const httpsAgent = isDevelopment ? new https.Agent({
  rejectUnauthorized: false
}) : undefined

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export const getResults = <T>(response: PaginatedResponse<T> | undefined): T[] => {
  return response?.results || []
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  date_joined: string
}

export interface UserCreateData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
}

export interface UserUpdateData {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
}

export interface ApiParams {
  offset?: number
  limit?: number
  search?: string
  ordering?: string
  [key: string]: unknown
}

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  ...(httpsAgent && { httpsAgent }),
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: () => void
  reject: (error: Error) => void
}> = []

const processQueue = (error: Error | null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve()
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/jwt/refresh/')) {
        return Promise.reject(error)
      }

      if (typeof window !== 'undefined' && window.location.pathname === '/login') {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise<void>((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => api(originalRequest))
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await api.post('/users/jwt/refresh/')
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error)
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (username: string, password: string): Promise<{ user: User }> => {
    const response = await api.post('/users/jwt/login/', { username, password })
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/user/')
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/users/jwt/logout/')
  },
}

export const usersApi = {
  getUsers: async (params?: ApiParams) => {
    const response = await api.get('/api/users/', { params })
    return response.data
  },

  getUser: async (id: number) => {
    const response = await api.get(`/api/users/${id}/`)
    return response.data
  },

  createUser: async (userData: UserCreateData) => {
    const response = await api.post('/api/users/', userData)
    return response.data
  },

  updateUser: async (id: number, userData: UserUpdateData) => {
    const response = await api.patch(`/api/users/${id}/`, userData)
    return response.data
  },

  deleteUser: async (id: number) => {
    const response = await api.delete(`/api/users/${id}/`)
    return response.data
  },
}

export default api
