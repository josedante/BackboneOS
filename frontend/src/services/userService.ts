import { apiService, type User } from './api'

export const userService = {
  async getUsers(): Promise<User[]> {
    return apiService.getUsers()
  },

  async getUser(id: number): Promise<User> {
    return apiService.getUser(id)
  },

  async createUser(userData: Partial<User>): Promise<User> {
    return apiService.createUser(userData)
  },

  async updateUser(id: number, userData: Partial<User>): Promise<User> {
    return apiService.updateUser(id, userData)
  },

  async deleteUser(id: number): Promise<void> {
    return apiService.deleteUser(id)
  }
}