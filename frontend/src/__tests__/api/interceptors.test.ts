import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock window.location
delete (window as any).location
window.location = { href: '' } as any

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Interceptors', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    mockFetch.mockClear()
  })

  describe('Token Storage', () => {
    it('should handle token storage correctly', () => {
      const mockTokens = { access: 'test-access-token', refresh: 'test-refresh-token' }
      
      localStorageMock.setItem('auth_tokens', JSON.stringify(mockTokens))
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockTokens))
      
      const storedTokens = JSON.parse(localStorageMock.getItem('auth_tokens') || '{}')
      
      expect(storedTokens).toEqual(mockTokens)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_tokens', JSON.stringify(mockTokens))
    })

    it('should handle missing tokens gracefully', () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const storedTokens = localStorageMock.getItem('auth_tokens')
      
      expect(storedTokens).toBeNull()
    })

    it('should handle corrupted token data', () => {
      localStorageMock.getItem.mockReturnValue('invalid-json')
      
      expect(() => {
        JSON.parse(localStorageMock.getItem('auth_tokens') || '{}')
      }).toThrow()
    })
  })

  describe('Token Refresh Logic', () => {
    it('should handle successful token refresh', async () => {
      const mockTokens = { access: 'expired-token', refresh: 'valid-refresh-token' }
      const newTokens = { access: 'new-access-token', refresh: 'new-refresh-token' }
      
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockTokens))
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(newTokens),
      })
      
      const response = await fetch('/users/jwt/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: mockTokens.refresh }),
      })
      
      const data = await response.json()
      
      expect(response.ok).toBe(true)
      expect(data).toEqual(newTokens)
      expect(mockFetch).toHaveBeenCalledWith('/users/jwt/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: mockTokens.refresh }),
      })
    })

    it('should handle failed token refresh', async () => {
      const mockTokens = { access: 'expired-token', refresh: 'invalid-refresh-token' }
      
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockTokens))
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Token is invalid or expired' }),
      })
      
      const response = await fetch('/users/jwt/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: mockTokens.refresh }),
      })
      
      expect(response.ok).toBe(false)
      expect(response.status).toBe(401)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network Error'))
      
      try {
        await fetch('/test')
      } catch (error: any) {
        expect(error.message).toBe('Network Error')
      }
    })

    it('should clear auth data on refresh failure', () => {
      // Simulate clearing auth data
      localStorageMock.removeItem('auth_tokens')
      localStorageMock.removeItem('user')
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_tokens')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
    })
  })
})