import { apiService, type AuthResponse, type User } from '~/src/services/api'

export const useAuth = () => {
  const config = useRuntimeConfig()
  const isProduction = !config.public.isDevelopment && process.env.NODE_ENV === 'production'
  
  const cookieOptions = {
    secure: isProduction, // Only secure in production (HTTPS)
    sameSite: isProduction ? 'strict' : 'lax', // Stricter in production
    httpOnly: false, // Keep false for client-side access
    domain: isProduction ? undefined : undefined // Can be configured per environment
  }
  
  const accessToken = useCookie('access-token', {
    default: () => null,
    maxAge: 60 * 60, // 1 hour
    ...cookieOptions
  })
  
  const refreshToken = useCookie('refresh-token', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7, // 7 days
    ...cookieOptions
  })
  
  const user = useState<User | null>('auth.user', () => null)

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      console.log('Auth service: Making login request...')
      const response: AuthResponse = await apiService.login(username, password)
      console.log('Auth service: Login response received:', response)
      
      accessToken.value = response.access
      refreshToken.value = response.refresh
      user.value = response.user
      
      console.log('Auth service: Tokens and user set')
      console.log('Access token:', accessToken.value ? 'SET' : 'NOT SET')
      console.log('User:', user.value)
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const logout = async () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    
    await navigateTo('/login')
  }

  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value
  })

  const checkAuth = async (): Promise<boolean> => {
    console.log('CheckAuth called')
    console.log('Access token exists:', !!accessToken.value)
    console.log('Refresh token exists:', !!refreshToken.value)
    console.log('User exists:', !!user.value)
    
    if (!accessToken.value || !refreshToken.value) {
      console.log('No tokens found')
      return false
    }

    // If we have tokens but no user data, try to get current user info
    if (!user.value) {
      console.log('Tokens exist but no user data, attempting to get current user...')
      try {
        // Try to get current user info with current token
        const currentUser = await apiService.getCurrentUser()
        user.value = currentUser
        console.log('User data restored:', user.value)
        return true
      } catch (error) {
        console.log('Failed to get current user, trying token refresh...')
        const refreshed = await apiService.refreshToken()
        if (refreshed) {
          // Try getting user info again after refresh
          try {
            const currentUser = await apiService.getCurrentUser()
            user.value = currentUser
            console.log('User data restored after refresh:', user.value)
            return true
          } catch (userError) {
            console.log('Failed to get user after refresh:', userError)
            return false
          }
        }
        return refreshed
      }
    }

    return true
  }

  return {
    user: readonly(user),
    login,
    logout,
    isAuthenticated,
    checkAuth
  }
}