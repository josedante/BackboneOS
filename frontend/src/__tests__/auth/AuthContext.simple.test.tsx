import { render, screen, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'

// Mock the API
vi.mock('@/lib/api', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

// Mock next/navigation (AuthProvider uses usePathname + useRouter)
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
  usePathname: () => '/',
}))

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock fetch globally
global.fetch = vi.fn()

// Test component that uses the auth context
function TestComponent() {
  const { user, isAuthenticated, login, logout } = useAuth()
  
  return (
    <div>
      <div data-testid="user">{user?.username || 'No user'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'true' : 'false'}</div>
      <button onClick={() => login('testuser', 'password')}>Login</button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  )
}

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
      <AuthProvider>{ui}</AuthProvider>
    </QueryClientProvider>
  )
}

describe('AuthContext - Simple Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    })
    
    // Mock fetch to prevent token refresh errors
    ;(global.fetch as any).mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: 'Token is invalid or expired' }),
    })
  })

  it('should initialize with no user when no tokens in localStorage', async () => {
    renderWithProviders(<TestComponent />)
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
  })

  it('should initialize with user when tokens exist in localStorage', async () => {
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    const mockTokens = { access: 'access-token', refresh: 'refresh-token' }
    
    // Mock localStorage to return our test data
    const localStorageMock = {
      getItem: vi.fn((key) => {
        if (key === 'user') return JSON.stringify(mockUser)
        if (key === 'auth_tokens') return JSON.stringify(mockTokens)
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    })
    
    renderWithProviders(<TestComponent />)
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })
  })

  it('should handle corrupted localStorage data gracefully', async () => {
    // Mock localStorage to return corrupted data
    const localStorageMock = {
      getItem: vi.fn((key) => {
        if (key === 'user' || key === 'auth_tokens') return 'invalid-json'
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    })
    
    renderWithProviders(<TestComponent />)
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
    
    // Check that corrupted data was cleared
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_tokens')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
  })
})
