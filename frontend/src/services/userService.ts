import apiClient from './api'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
}

// Servicios para interactuar con el backend Django
export const userService = {
  // Obtener todos los usuarios
  async getUsers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/api/users/')
    return response.data
  },

  // Obtener un usuario por ID
  async getUser(id: number): Promise<User> {
    const response = await apiClient.get<User>(`/api/users/${id}/`)
    return response.data
  },

  // Crear un nuevo usuario
  async createUser(userData: Omit<User, 'id'>): Promise<User> {
    const response = await apiClient.post<User>('/api/users/', userData)
    return response.data
  },

  // Actualizar un usuario
  async updateUser(id: number, userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(`/api/users/${id}/`, userData)
    return response.data
  },

  // Eliminar un usuario
  async deleteUser(id: number): Promise<void> {
    await apiClient.delete(`/api/users/${id}/`)
  },
}

// Servicio de autenticación
export const authService = {
  // Login
  async login(username: string, password: string): Promise<{ token: string; user: User }> {
    const response = await apiClient.post('/api/auth/login/', { username, password })
    const { token, user } = response.data
    localStorage.setItem('token', token)
    return { token, user }
  },

  // Logout
  logout(): void {
    localStorage.removeItem('token')
  },

  // Verificar si el usuario está autenticado
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
  },
}
