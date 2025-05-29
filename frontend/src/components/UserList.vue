<template>
  <div class="user-list">
    <div class="header">
      <h2>Lista de Usuarios</h2>
      <button @click="fetchUsers" :disabled="loading" class="refresh-btn">
        <span v-if="loading">🔄</span>
        <span v-else>🔄</span>
        {{ loading ? 'Cargando...' : 'Actualizar' }}
      </button>
    </div>

    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchUsers" class="retry-btn">Reintentar</button>
    </div>

    <div v-else-if="users.length > 0" class="users-grid">
      <div v-for="user in users" :key="user.id" class="user-card">
        <div class="user-info">
          <h3>{{ user.first_name }} {{ user.last_name }}</h3>
          <p class="username">@{{ user.username }}</p>
          <p class="email">{{ user.email }}</p>
          <p class="date">Registrado: {{ formatDate(user.date_joined) }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="no-users">
      <p>No hay usuarios registrados.</p>
      <p class="hint">Crea un superusuario desde Django Admin para ver datos aquí.</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando usuarios...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userService, type User } from '../services/userService'

const users = ref<User[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const fetchUsers = async () => {
  loading.value = true
  error.value = null

  try {
    users.value = await userService.getUsers()
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = 'Endpoint de API no encontrado. Verifica que Django esté ejecutándose.'
    } else if (err.code === 'ECONNREFUSED') {
      error.value =
        'No se puede conectar al backend. Verifica que Django esté ejecutándose en el puerto 8000.'
    } else {
      error.value = `Error: ${err.message || 'Error desconocido al cargar usuarios'}`
    }
    console.error('Error fetching users:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h2 {
  color: var(--color-heading);
  margin: 0;
}

.refresh-btn {
  background: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--color-border-hover);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #ffeaea;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  margin-bottom: 2rem;
}

.error-message p {
  color: #e74c3c;
  margin: 0 0 1rem 0;
}

.retry-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background: #c0392b;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.user-card {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-info h3 {
  color: var(--color-heading);
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.username {
  color: var(--color-text-mute);
  font-family: monospace;
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
}

.email {
  color: var(--color-text);
  margin: 0 0 1rem 0;
}

.date {
  color: var(--color-text-mute);
  font-size: 0.85rem;
  margin: 0;
}

.no-users {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-mute);
}

.hint {
  font-size: 0.9rem;
  color: var(--color-text-mute);
  margin-top: 0.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: var(--color-text-mute);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-text);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
