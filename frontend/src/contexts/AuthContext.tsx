'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import { TokenRefreshManager } from '@/components/auth/TokenRefreshManager'
import { authApi } from '@/lib/api'
import type { User } from '@/lib/api'

interface AuthContextType {
  user: User | null
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
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // On mount, restore session from the httpOnly access_token cookie.
  // A 401 here means either no cookie or an expired one; the axios interceptor
  // will try the refresh cookie automatically before rejecting.
  useEffect(() => {
    authApi.getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      const { user: loggedInUser } = await authApi.login(username, password)
      setUser(loggedInUser)
      toast.success('Login successful!')
      return true
    } catch (error) {
      const errorMessage = (error as any).response?.data?.error || 'Login failed'
      toast.error(errorMessage)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await authApi.logout()
    } catch {
      // Continue with local logout even if the server call fails
    } finally {
      setUser(null)
      toast.success('Logged out successfully')
      router.push('/login')
    }
  }

  // Called by TokenRefreshManager on a proactive timer.
  // Token rotation happens server-side via the httpOnly cookie; we call /me to
  // confirm the session is alive and pick up any user-data changes.
  const refreshToken = async (): Promise<boolean> => {
    try {
      const freshUser = await authApi.getCurrentUser()
      setUser(freshUser)
      return true
    } catch {
      setUser(null)
      router.push('/login')
      return false
    }
  }

  const updateUser = (newUser: User) => {
    setUser(newUser)
  }

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      refreshToken,
      updateUser,
    }}>
      <TokenRefreshManager />
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
