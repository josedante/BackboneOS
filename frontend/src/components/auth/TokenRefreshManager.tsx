'use client'

import { useEffect, useRef } from 'react'

import { useAuth } from '@/contexts/AuthContext'

interface TokenPayload {
  exp: number
  iat: number
  user_id: number
  username: string
}

// Helper function to decode JWT token
function decodeJWT(token: string): TokenPayload | null {
  try {
    if (!token || typeof token !== 'string') {
      return null
    }
    
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }
    
    const base64Url = parts[1]
    if (!base64Url) {
      return null
    }
    
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error decoding JWT:', error)
    return null
  }
}

// Helper function to check if token is expired or will expire soon
function isTokenExpiringSoon(token: string, bufferMinutes: number = 5): boolean {
  const payload = decodeJWT(token)
  if (!payload) return true

  const now = Math.floor(Date.now() / 1000)
  const expirationTime = payload.exp
  const bufferTime = bufferMinutes * 60 // Convert minutes to seconds

  return (expirationTime - now) <= bufferTime
}

export function TokenRefreshManager() {
  const { tokens, refreshToken } = useAuth()
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!tokens?.access) {
      // Clear any existing interval if no tokens
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
        refreshIntervalRef.current = null
      }
      return
    }

    // Check if token is expiring soon
    if (isTokenExpiringSoon(tokens.access)) {
      refreshToken()
    }

    // Set up interval to check token expiration every minute
    refreshIntervalRef.current = setInterval(() => {
      if (tokens?.access && isTokenExpiringSoon(tokens.access)) {
        refreshToken()
      }
    }, 60000) // Check every minute

    // Cleanup function
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
        refreshIntervalRef.current = null
      }
    }
  }, [tokens, refreshToken])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [])

  // This component doesn't render anything
  return null
}
