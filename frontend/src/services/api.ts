interface AuthResponse {
  access: string
  refresh: string
  user: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
  }
}

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

class ApiService {
  private get baseURL() {
    const config = useRuntimeConfig()
    return config.public.apiBase || 'http://localhost:8000'
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const accessToken = useCookie('access-token')
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (accessToken.value) {
      headers.Authorization = `Bearer ${accessToken.value}`
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      })

      if (response.status === 401 && accessToken.value) {
        // Try to refresh token
        const refreshed = await this.refreshToken()
        if (refreshed) {
          // Retry the original request
          headers.Authorization = `Bearer ${accessToken.value}`
          const retryResponse = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers,
          })
          if (!retryResponse.ok) {
            throw new Error(`HTTP error! status: ${retryResponse.status}`)
          }
          return retryResponse.json()
        } else {
          // Refresh failed, redirect to login
          await navigateTo('/login')
          throw new Error('Authentication failed')
        }
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/auth/jwt/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = useCookie('refresh-token')
      const accessToken = useCookie('access-token')
      
      if (!refreshToken.value) {
        return false
      }

      const response = await fetch(`${this.baseURL}/api/auth/jwt/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken.value }),
      })

      if (response.ok) {
        const data = await response.json()
        accessToken.value = data.access
        return true
      } else {
        // Refresh token is invalid, clear tokens
        accessToken.value = null
        refreshToken.value = null
        return false
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
  }

  async getUsers(): Promise<User[]> {
    const response = await this.request<{ results: User[] }>('/api/users/')
    return response.results
  }

  async getUser(id: number): Promise<User> {
    return this.request<User>(`/api/users/${id}/`)
  }

  async createUser(userData: Partial<User>): Promise<User> {
    return this.request<User>('/api/users/', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async updateUser(id: number, userData: Partial<User>): Promise<User> {
    return this.request<User>(`/api/users/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    })
  }

  async deleteUser(id: number): Promise<void> {
    await this.request<void>(`/api/users/${id}/`, {
      method: 'DELETE',
    })
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/auth/user/')
  }
}

export const apiService = new ApiService()
export type { AuthResponse, User }