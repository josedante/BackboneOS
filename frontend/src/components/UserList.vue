<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Users</h1>
      <div class="flex space-x-4">
        <span v-if="user" class="text-sm text-gray-600">
          Welcome, {{ user.username }}!
        </span>
        <button
          @click="logout"
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
        >
          Logout
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="text-center py-4">
      Loading users...
    </div>
    
    <div v-else-if="error" class="text-red-600 text-center py-4">
      {{ error }}
    </div>
    
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="user in users"
        :key="user.id"
        class="bg-white p-4 rounded-lg shadow border"
      >
        <h3 class="font-semibold text-gray-900">{{ user.username }}</h3>
        <p class="text-gray-600">{{ user.email }}</p>
        <p class="text-sm text-gray-500">
          {{ user.first_name }} {{ user.last_name }}
        </p>
      </div>
    </div>
    
    <div v-if="!loading && users.length === 0 && !error" class="text-center py-8 text-gray-500">
      No users found.
    </div>
  </div>
</template>

<script setup lang="ts">
import { userService } from '../services/userService'
import type { User } from '../services/api'

definePageMeta({
  middleware: 'auth'
})

const { user, logout } = useAuth()
const users = ref<User[]>([])
const loading = ref(true)
const error = ref('')

const fetchUsers = async () => {
  try {
    loading.value = true
    error.value = ''
    users.value = await userService.getUsers()
  } catch (err) {
    error.value = 'Failed to load users'
    console.error('Error fetching users:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>