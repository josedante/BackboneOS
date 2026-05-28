import { render, screen, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { authApi } from '@/lib/api'

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

// Mock fetch globally to prevent TokenRefreshManager from making real API calls
global.fetch = vi.fn()

// Mock TokenRefreshManager to prevent it from interfering with tests
vi.mock('@/components/auth/TokenRefreshManager', () => ({
  TokenRefreshManager: () => null,
}))

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

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
    
    // Reset localStorage mock
    const localStorageMock = {
      getItem: vi.fn(),
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
    
    // Mock fetch to prevent TokenRefreshManager from making real API calls
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

  it('should handle successful login', async () => {
    const mockResponse = {
      access: 'new-access-token',
      refresh: 'new-refresh-token',
      user: { id: 1, username: 'testuser', email: 'test@example.com' }
    }
    
    ;(authApi.login as any).mockResolvedValue(mockResponse)
    
    // Mock localStorage to track setItem calls and return null initially
    const localStorageMock = {
      getItem: vi.fn(() => null), // Start with no tokens
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
    
    // Wait for initial state to be ready
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
    
    const loginButton = screen.getByText('Login')
    await act(async () => {
      loginButton.click()
    })
    
    // Wait for login to complete and state to update
    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith('testuser', 'password')
      expect(screen.getByTestId('user')).toHaveTextContent('testuser')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    }, { timeout: 3000 })
    
    // Check that tokens are stored in localStorage
    expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_tokens', JSON.stringify({
      access: 'new-access-token',
      refresh: 'new-refresh-token'
    }))
    expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify({
      id: 1, username: 'testuser', email: 'test@example.com'
    }))
  })

  it('should handle login failure', async () => {
    const mockError = new Error('Invalid credentials')
    ;(authApi.login as any).mockRejectedValue(mockError)
    
    renderWithProviders(<TestComponent />)
    
    const loginButton = screen.getByText('Login')
    await act(async () => {
      loginButton.click()
    })
    
    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith('testuser', 'password')
      expect(screen.getByTestId('user')).toHaveTextContent('No user')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
  })

  it('should handle logout', async () => {
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    const mockTokens = { access: 'access-token', refresh: 'refresh-token' }
    
    ;(authApi.logout as any).mockResolvedValue({})
    
    // Mock localStorage to return initial data and track removeItem calls
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
    
    // Wait for initial state
    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })
    
    const logoutButton = screen.getByText('Logout')
    await act(async () => {
      logoutButton.click()
    })
    
    await waitFor(() => {
      expect(authApi.logout).toHaveBeenCalled()
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_tokens')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
    })
  })

  it('should handle corrupted localStorage data gracefully', async () => {
    // Mock localStorage to return corrupted data initially, then null after clearing
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
