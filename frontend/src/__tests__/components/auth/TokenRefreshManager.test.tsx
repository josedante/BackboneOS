import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { TokenRefreshManager } from '@/components/auth/TokenRefreshManager'
import { useAuth } from '@/contexts/AuthContext'

// Mock the auth context
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

// Helper function to render with providers
function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

describe('TokenRefreshManager', () => {
  const mockRefreshToken = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should not refresh when no tokens exist', () => {
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: null,
      refreshToken: mockRefreshToken,
    })
    
    renderWithProviders(<TokenRefreshManager />)
    
    // Fast-forward time
    vi.advanceTimersByTime(60000) // 1 minute
    
    expect(mockRefreshToken).not.toHaveBeenCalled()
  })

  it('should refresh token when it is expiring soon', () => {
    // Create a token that expires in 3 minutes (180 seconds from now)
    const exp = Math.floor(Date.now() / 1000) + 180
    const payload = { exp, iat: Math.floor(Date.now() / 1000), user_id: 1, username: 'test' }
    const header = { alg: 'HS256', typ: 'JWT' }
    
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))
    const token = `${encodedHeader}.${encodedPayload}.signature`
    
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: { access: token, refresh: 'refresh-token' },
      refreshToken: mockRefreshToken,
    })
    
    renderWithProviders(<TokenRefreshManager />)
    
    // Should immediately try to refresh since token expires in 3 minutes (< 5 minute buffer)
    expect(mockRefreshToken).toHaveBeenCalled()
  })

  it('should not refresh token when it is not expiring soon', () => {
    // Create a token that expires in 10 minutes (600 seconds from now)
    const exp = Math.floor(Date.now() / 1000) + 600
    const payload = { exp, iat: Math.floor(Date.now() / 1000), user_id: 1, username: 'test' }
    const header = { alg: 'HS256', typ: 'JWT' }
    
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))
    const token = `${encodedHeader}.${encodedPayload}.signature`
    
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: { access: token, refresh: 'refresh-token' },
      refreshToken: mockRefreshToken,
    })
    
    renderWithProviders(<TokenRefreshManager />)
    
    // Should not immediately refresh since token expires in 10 minutes (> 5 minute buffer)
    expect(mockRefreshToken).not.toHaveBeenCalled()
  })

  it('should set up interval to check token expiration', () => {
    const exp = Math.floor(Date.now() / 1000) + 600 // 10 minutes from now
    const payload = { exp, iat: Math.floor(Date.now() / 1000), user_id: 1, username: 'test' }
    const header = { alg: 'HS256', typ: 'JWT' }
    
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))
    const token = `${encodedHeader}.${encodedPayload}.signature`
    
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: { access: token, refresh: 'refresh-token' },
      refreshToken: mockRefreshToken,
    })
    
    renderWithProviders(<TokenRefreshManager />)
    
    // Fast-forward 1 minute
    vi.advanceTimersByTime(60000)
    
    // Should not refresh yet
    expect(mockRefreshToken).not.toHaveBeenCalled()
    
    // Fast-forward another 4 minutes (total 5 minutes)
    vi.advanceTimersByTime(240000)
    
    // Should refresh now since token expires in 5 minutes
    expect(mockRefreshToken).toHaveBeenCalled()
  })

  it('should handle invalid token gracefully', () => {
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: { access: 'invalid-token', refresh: 'refresh-token' },
      refreshToken: mockRefreshToken,
    })
    
    renderWithProviders(<TokenRefreshManager />)
    
    // Should try to refresh since invalid token is treated as expiring
    expect(mockRefreshToken).toHaveBeenCalled()
  })

  it('should clean up interval on unmount', () => {
    const exp = Math.floor(Date.now() / 1000) + 600
    const payload = { exp, iat: Math.floor(Date.now() / 1000), user_id: 1, username: 'test' }
    const header = { alg: 'HS256', typ: 'JWT' }
    
    const encodedHeader = btoa(JSON.stringify(header))
    const encodedPayload = btoa(JSON.stringify(payload))
    const token = `${encodedHeader}.${encodedPayload}.signature`
    
    ;(useAuth as jest.Mock).mockReturnValue({
      tokens: { access: token, refresh: 'refresh-token' },
      refreshToken: mockRefreshToken,
    })
    
    const { unmount } = renderWithProviders(<TokenRefreshManager />)
    
    // Unmount the component
    unmount()
    
    // Fast-forward time
    vi.advanceTimersByTime(60000)
    
    // Should not refresh since interval was cleaned up
    expect(mockRefreshToken).not.toHaveBeenCalled()
  })
})
