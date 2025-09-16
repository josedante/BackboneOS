<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Iniciar Sesión
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input
              id="username"
              v-model="form.username"
              name="username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Username"
            >
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            >
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            <span v-if="loading">Iniciando sesión...</span>
            <span v-else>Iniciar Sesión</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  auth: false
})

const { login, isAuthenticated } = useAuth()
const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!form.username || !form.password) {
    error.value = 'Username y password son requeridos'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('Attempting login...')
    const success = await login(form.username, form.password)
    console.log('Login success:', success)
    console.log('Is authenticated after login:', isAuthenticated.value)
    
    if (success) {
      console.log('Navigating to home...')
      await navigateTo('/')
    } else {
      error.value = 'Credenciales inválidas'
    }
  } catch (err) {
    error.value = 'Error al iniciar sesión'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

// Redirect if already authenticated
watchEffect(() => {
  if (isAuthenticated.value) {
    navigateTo('/')
  }
})
</script>