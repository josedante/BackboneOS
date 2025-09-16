/**
 * Token Refresh Testing Utilities
 * 
 * This file provides utilities to test token refresh functionality in development.
 * Use these tools to verify that token refresh works correctly.
 */

interface TokenPayload {
  exp: number
  iat: number
  user_id: number
  username: string
}

// Helper function to decode JWT token (same as in TokenRefreshManager)
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

// Helper function to get time until token expires
function getTimeUntilExpiry(token: string): number {
  const payload = decodeJWT(token)
  if (!payload) return 0

  const now = Math.floor(Date.now() / 1000)
  return payload.exp - now
}

// Helper function to format time in a readable way
function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} seconds`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

export class TokenRefreshTester {
  private static instance: TokenRefreshTester
  private refreshLog: Array<{ timestamp: Date; success: boolean; error?: string }> = []

  static getInstance(): TokenRefreshTester {
    if (!TokenRefreshTester.instance) {
      TokenRefreshTester.instance = new TokenRefreshTester()
    }
    return TokenRefreshTester.instance
  }

  /**
   * Get current token information from localStorage
   */
  getTokenInfo(): {
    hasTokens: boolean
    accessToken?: string
    refreshToken?: string
    accessPayload?: TokenPayload
    refreshPayload?: TokenPayload
    timeUntilExpiry?: number
    isExpiringSoon?: boolean
  } {
    try {
      const tokensStr = localStorage.getItem('auth_tokens')
      if (!tokensStr) {
        return { hasTokens: false }
      }

      const tokens = JSON.parse(tokensStr)
      const accessPayload = decodeJWT(tokens.access) || undefined
      const refreshPayload = decodeJWT(tokens.refresh) || undefined
      const timeUntilExpiry = accessPayload ? getTimeUntilExpiry(tokens.access) : 0
      const isExpiringSoon = accessPayload ? isTokenExpiringSoon(tokens.access) : false

      return {
        hasTokens: true,
        accessToken: tokens.access,
        refreshToken: tokens.refresh,
        ...(accessPayload && { accessPayload }),
        ...(refreshPayload && { refreshPayload }),
        timeUntilExpiry,
        isExpiringSoon
      }
    } catch (error) {
      console.error('Error getting token info:', error)
      return { hasTokens: false }
    }
  }

  /**
   * Manually trigger token refresh
   */
  async manualRefresh(): Promise<{ success: boolean; error?: string; newTokens?: any }> {
    try {
      const tokensStr = localStorage.getItem('auth_tokens')
      if (!tokensStr) {
        return { success: false, error: 'No tokens found' }
      }

      const tokens = JSON.parse(tokensStr)
      const apiBase = process.env['NEXT_PUBLIC_API_BASE'] || 'https://backend.proyecto-opensource.orb.local'
      
      const response = await fetch(`${apiBase}/users/jwt/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: tokens.refresh }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        this.refreshLog.push({ timestamp: new Date(), success: false, error: `HTTP ${response.status}: ${errorText}` })
        return { success: false, error: `HTTP ${response.status}: ${errorText}` }
      }

      const data = await response.json()
      this.refreshLog.push({ timestamp: new Date(), success: true })
      
      return { success: true, newTokens: data }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      this.refreshLog.push({ timestamp: new Date(), success: false, error: errorMessage })
      return { success: false, error: errorMessage }
    }
  }

  /**
   * Create a token that expires soon for testing
   */
  createExpiringToken(expiresInSeconds: number = 30): string {
    const now = Math.floor(Date.now() / 1000)
    const exp = now + expiresInSeconds
    
    const payload = {
      exp,
      iat: now,
      user_id: 1,
      username: 'testuser'
    }

    // Create a mock JWT (this won't be valid for API calls, but useful for testing UI)
    const header = { alg: 'HS256', typ: 'JWT' }
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))
    const signature = 'test-signature'
    
    return `${encodedHeader}.${encodedPayload}.${signature}`
  }

  /**
   * Simulate token expiration by setting a token that expires soon
   */
  simulateTokenExpiration(expiresInSeconds: number = 30): void {
    try {
      const tokensStr = localStorage.getItem('auth_tokens')
      if (!tokensStr) {
        console.warn('No tokens found to simulate expiration')
        return
      }

      const tokens = JSON.parse(tokensStr)
      const expiringToken = this.createExpiringToken(expiresInSeconds)
      
      // Keep the same refresh token, just update the access token
      const newTokens = {
        access: expiringToken,
        refresh: tokens.refresh
      }

      localStorage.setItem('auth_tokens', JSON.stringify(newTokens))
      console.log(`Token set to expire in ${expiresInSeconds} seconds`)
    } catch (error) {
      console.error('Error simulating token expiration:', error)
    }
  }

  /**
   * Get refresh log
   */
  getRefreshLog(): Array<{ timestamp: Date; success: boolean; error?: string }> {
    return [...this.refreshLog]
  }

  /**
   * Clear refresh log
   */
  clearRefreshLog(): void {
    this.refreshLog = []
  }

  /**
   * Print token information to console
   */
  printTokenInfo(): void {
    const info = this.getTokenInfo()
    
    console.group('🔐 Token Information')
    console.log('Has Tokens:', info.hasTokens)
    
    if (info.hasTokens && info.accessPayload) {
      console.log('User ID:', info.accessPayload.user_id)
      console.log('Username:', info.accessPayload.username)
      console.log('Issued At:', new Date(info.accessPayload.iat * 1000).toLocaleString())
      console.log('Expires At:', new Date(info.accessPayload.exp * 1000).toLocaleString())
      console.log('Time Until Expiry:', formatTime(info.timeUntilExpiry || 0))
      console.log('Is Expiring Soon:', info.isExpiringSoon)
    }
    
    console.groupEnd()
  }

  /**
   * Start monitoring token refresh (for debugging)
   */
  startMonitoring(): void {
    console.log('🔍 Starting token refresh monitoring...')
    
    const monitor = () => {
      const info = this.getTokenInfo()
      if (info.hasTokens && info.isExpiringSoon) {
        console.warn('⚠️ Token is expiring soon!', {
          timeUntilExpiry: formatTime(info.timeUntilExpiry || 0),
          isExpiringSoon: info.isExpiringSoon
        })
      }
    }

    // Check every 10 seconds
    setInterval(monitor, 10000)
    monitor() // Initial check
  }
}

// Export a singleton instance
export const tokenRefreshTester = TokenRefreshTester.getInstance()

// Make it available globally in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  (window as any).tokenRefreshTester = tokenRefreshTester
  console.log('🔧 Token Refresh Tester available as window.tokenRefreshTester')
}
