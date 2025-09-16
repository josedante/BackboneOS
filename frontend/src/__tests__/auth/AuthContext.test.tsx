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

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
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
    
    localStorage.setItem('user', JSON.stringify(mockUser))
    localStorage.setItem('auth_tokens', JSON.stringify(mockTokens))
    
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
    
    renderWithProviders(<TestComponent />)
    
    const loginButton = screen.getByText('Login')
    await act(async () => {
      loginButton.click()
    })
    
    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith('testuser', 'password')
      expect(screen.getByTestId('user')).toHaveTextContent('testuser')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })
    
    // Check that tokens are stored in localStorage
    const storedTokens = JSON.parse(localStorage.getItem('auth_tokens') || '{}')
    expect(storedTokens).toEqual({
      access: 'new-access-token',
      refresh: 'new-refresh-token'
    })
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
    
    localStorage.setItem('user', JSON.stringify(mockUser))
    localStorage.setItem('auth_tokens', JSON.stringify(mockTokens))
    
    ;(authApi.logout as any).mockResolvedValue({})
    
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
      expect(localStorage.getItem('auth_tokens')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })
  })

  it('should handle corrupted localStorage data gracefully', async () => {
    localStorage.setItem('user', 'invalid-json')
    localStorage.setItem('auth_tokens', 'invalid-json')
    
    renderWithProviders(<TestComponent />)
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
    
    // Check that corrupted data was cleared
    expect(localStorage.getItem('auth_tokens')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })
})
