'use client'

import { useEffect, useRef } from 'react'

import { useAuth } from '@/contexts/AuthContext'

// Proactively refresh 5 minutes before the 60-minute access token expires.
// The axios 401 interceptor is the safety net for any edge cases.
const REFRESH_INTERVAL_MS = 55 * 60 * 1000

export function TokenRefreshManager() {
  const { isAuthenticated, refreshToken } = useAuth()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    intervalRef.current = setInterval(refreshToken, REFRESH_INTERVAL_MS)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isAuthenticated, refreshToken])

  return null
}
