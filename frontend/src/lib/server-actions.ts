'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

import { api } from './api'

// Type definitions for error handling
interface ApiError {
  response?: {
    data?: {
      error?: string
      [key: string]: unknown
    }
  }
  message?: string
}

// Server Actions for mutations - acts as BFF/proxy to Django
export async function loginAction(formData: FormData) {
  const username = formData.get('username') as string
  const password = formData.get('password') as string

  try {
    const response = await api.post('/users/jwt/login/', { username, password })
    
    // In a real app, you'd set the token in a secure httpOnly cookie
    // For now, we'll return the token to be stored client-side
    return {
      success: true,
      token: response.data.access,
      user: response.data.user,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    console.error('Login error:', error)
    console.error('API Error response:', apiError.response)
    console.error('API Error data:', apiError.response?.data)
    return {
      success: false,
      error: apiError.response?.data?.error || apiError.message || 'Login failed',
    }
  }
}

export async function logoutAction() {
  try {
    await api.post('/users/jwt/logout/')
    revalidatePath('/')
    redirect('/login')
  } catch (error) {
    console.error('Logout error:', error)
    // Still redirect even if logout fails
    redirect('/login')
  }
}

export async function createUserAction(formData: FormData) {
  const userData = {
    username: formData.get('username') as string,
    email: formData.get('email') as string,
    first_name: formData.get('first_name') as string,
    last_name: formData.get('last_name') as string,
    password: formData.get('password') as string,
  }

  try {
    const response = await api.post('/api/users/', userData)
    revalidatePath('/users')
    return {
      success: true,
      user: response.data,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to create user',
    }
  }
}

export async function updateUserAction(id: number, formData: FormData) {
  const userData = {
    username: formData.get('username') as string,
    email: formData.get('email') as string,
    first_name: formData.get('first_name') as string,
    last_name: formData.get('last_name') as string,
  }

  try {
    const response = await api.patch(`/api/users/${id}/`, userData)
    revalidatePath('/users')
    revalidatePath(`/users/${id}`)
    return {
      success: true,
      user: response.data,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to update user',
    }
  }
}

export async function deleteUserAction(id: number) {
  try {
    await api.delete(`/api/users/${id}/`)
    revalidatePath('/users')
    return {
      success: true,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to delete user',
    }
  }
}

export async function createProductAction(formData: FormData) {
  const productData = {
    name: formData.get('name') as string,
    description: formData.get('description') as string,
    price: parseFloat(formData.get('price') as string),
    category: formData.get('category') as string,
  }

  try {
    const response = await api.post('/api/products/', productData)
    revalidatePath('/products')
    return {
      success: true,
      product: response.data,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to create product',
    }
  }
}

export async function updateProductAction(id: number, formData: FormData) {
  const productData = {
    name: formData.get('name') as string,
    description: formData.get('description') as string,
    price: parseFloat(formData.get('price') as string),
    category: formData.get('category') as string,
  }

  try {
    const response = await api.patch(`/api/products/${id}/`, productData)
    revalidatePath('/products')
    revalidatePath(`/products/${id}`)
    return {
      success: true,
      product: response.data,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to update product',
    }
  }
}

export async function deleteProductAction(id: number) {
  try {
    await api.delete(`/api/products/${id}/`)
    revalidatePath('/products')
    return {
      success: true,
    }
  } catch (error: unknown) {
    const apiError = error as ApiError
    return {
      success: false,
      error: apiError.response?.data || 'Failed to delete product',
    }
  }
}
