export default defineNuxtRouteMiddleware(async (to) => {
  const { checkAuth, isAuthenticated } = useAuth()
  
  console.log('Auth middleware: Checking route:', to.path)
  console.log('Auth middleware: Route meta:', to.meta)
  
  // Check if the route requires authentication
  const requiresAuth = to.meta.auth !== false
  
  console.log('Auth middleware: Requires auth:', requiresAuth)
  
  if (requiresAuth) {
    console.log('Auth middleware: Checking authentication...')
    const authValid = await checkAuth()
    
    console.log('Auth middleware: Auth valid:', authValid)
    console.log('Auth middleware: Is authenticated:', isAuthenticated.value)
    
    if (!authValid || !isAuthenticated.value) {
      console.log('Auth middleware: Redirecting to login')
      return navigateTo('/login')
    }
    
    console.log('Auth middleware: Authentication passed')
  }
})