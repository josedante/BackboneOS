export default defineNuxtPlugin(async () => {
  const { checkAuth } = useAuth()
  
  // Initialize authentication state on client-side
  if (process.client) {
    console.log('Auth plugin: Initializing authentication...')
    await checkAuth()
  }
})