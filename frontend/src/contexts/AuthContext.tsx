'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import { TokenRefreshManager } from '@/components/auth/TokenRefreshManager'
import { authApi } from '@/lib/api'
import type { User } from '@/lib/api'

interface AuthTokens {
  access: string
  refresh: string
}

interface AuthContextType {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  refreshToken: () => Promise<boolean>
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [tokens, setTokens] = useState<AuthTokens | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedTokens = localStorage.getItem('auth_tokens')
        const storedUser = localStorage.getItem('user')
        
        if (storedTokens && storedUser) {
          const parsedTokens = JSON.parse(storedTokens)
          const parsedUser = JSON.parse(storedUser)
          
          setTokens(parsedTokens)
          setUser(parsedUser)
        }
      } catch (error) {
        console.error('Error initializing auth state:', error)
        // Clear corrupted data
        localStorage.removeItem('auth_tokens')
        localStorage.removeItem('user')
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Store tokens in localStorage
  const storeTokens = (newTokens: AuthTokens) => {
    setTokens(newTokens)
    localStorage.setItem('auth_tokens', JSON.stringify(newTokens))
  }

  // Store user in localStorage
  const storeUser = (newUser: User) => {
    setUser(newUser)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  // Clear all auth data
  const clearAuthData = () => {
    setUser(null)
    setTokens(null)
    localStorage.removeItem('auth_tokens')
    localStorage.removeItem('user')
  }

  // Login function
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response = await authApi.login(username, password)
      
      const newTokens: AuthTokens = {
        access: response.access,
        refresh: response.refresh
      }
      
      storeTokens(newTokens)
      storeUser(response.user)
      
      toast.success('Login successful!')
      return true
    } catch (error: any) {
      console.error('Login error:', error)
      const errorMessage = error.response?.data?.error || 'Login failed'
      toast.error(errorMessage)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      if (tokens?.access) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('Logout error:', error)
      // Continue with logout even if API call fails
    } finally {
      clearAuthData()
      toast.success('Logged out successfully')
      router.push('/login')
    }
  }

  // Refresh token function
  const refreshToken = async (): Promise<boolean> => {
    if (!tokens?.refresh) {
      return false
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'https://backend.proyecto-opensource.orb.local'}/users/jwt/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: tokens.refresh }),
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      
      const newTokens: AuthTokens = {
        access: data.access,
        refresh: data.refresh || tokens.refresh // Use new refresh token if provided, otherwise keep current
      }
      
      storeTokens(newTokens)
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      clearAuthData()
      router.push('/login')
      return false
    }
  }

  // Update user function
  const updateUser = (newUser: User) => {
    storeUser(newUser)
  }

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated: !!user && !!tokens?.access,
    isLoading,
    login,
    logout,
    refreshToken,
    updateUser,
  }

  return (
    <AuthContext.Provider value={value}>
      <TokenRefreshManager />
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
