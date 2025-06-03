<template>
  <NuxtLayout name="dashboard">
    <template #title>Users</template>

    <div class="mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
          <p class="text-gray-600 mt-1">Manage and view all system users</p>
        </div>
        <UButton
          icon="i-heroicons-plus"
          size="sm"
          color="primary"
          variant="solid"
          to="/users/new"
        >
          Add User
        </UButton>
      </div>
    </div>

    <UCard>
      <div v-if="loading" class="flex justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="h-6 w-6 animate-spin" />
        <span class="ml-2">Loading users...</span>
      </div>

      <UAlert
        v-else-if="error"
        icon="i-heroicons-exclamation-triangle"
        color="error"
        variant="subtle"
        :title="error"
        class="mb-4"
      />

      <div v-else-if="users.length > 0">
        <!-- Users table -->
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  User
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Email
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Role
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Last Login
                </th>
                <th class="relative px-6 py-3">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <UAvatar
                      :src="user.avatar"
                      :alt="user.username"
                      size="sm"
                      class="mr-3"
                    />
                    <div>
                      <div class="text-sm font-medium text-gray-900">
                        {{ user.first_name }} {{ user.last_name }}
                      </div>
                      <div class="text-sm text-gray-500">
                        @{{ user.username }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ user.email }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <UBadge
                    :color="user.is_active ? 'success' : 'error'"
                    variant="subtle"
                  >
                    {{ user.is_active ? "Active" : "Inactive" }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <UBadge
                    :color="user.is_staff ? 'primary' : 'secondary'"
                    variant="subtle"
                  >
                    {{ user.is_staff ? "Staff" : "User" }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ user.last_login ? formatDate(user.last_login) : "Never" }}
                </td>
                <td
                  class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                >
                  <UDropdown :items="getUserActions(user)">
                    <UButton
                      variant="ghost"
                      size="sm"
                      icon="i-heroicons-ellipsis-vertical"
                    />
                  </UDropdown>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <UIcon
          name="i-heroicons-user-group"
          class="h-12 w-12 text-gray-400 mx-auto mb-4"
        />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No users found</h3>
        <p class="text-gray-500 mb-4">Get started by adding your first user.</p>
        <UButton icon="i-heroicons-plus" color="primary" to="/users/new">
          Add User
        </UButton>
      </div>
    </UCard>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { userService } from "~/src/services/userService";
import type { User } from "~/src/services/api";

definePageMeta({
  middleware: "auth",
});

const users = ref<User[]>([]);
const loading = ref(true);
const error = ref("");

const fetchUsers = async () => {
  try {
    loading.value = true;
    error.value = "";
    users.value = await userService.getUsers();
  } catch (err) {
    error.value = "Failed to load users. Please try again.";
    console.error("Error fetching users:", err);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const getUserActions = (user: User) => [
  [
    {
      label: "View Profile",
      icon: "i-heroicons-eye",
      click: () => navigateTo(`/users/${user.id}`),
    },
    {
      label: "Edit User",
      icon: "i-heroicons-pencil",
      click: () => navigateTo(`/users/${user.id}/edit`),
    },
  ],
  [
    {
      label: user.is_active ? "Deactivate" : "Activate",
      icon: user.is_active ? "i-heroicons-user-minus" : "i-heroicons-user-plus",
      click: () => toggleUserStatus(user),
    },
  ],
  [
    {
      label: "Delete User",
      icon: "i-heroicons-trash",
      click: () => deleteUser(user),
    },
  ],
];

const toggleUserStatus = async (user: User) => {
  // TODO: Implement user status toggle
  console.log("Toggle user status:", user);
};

const deleteUser = async (user: User) => {
  // TODO: Implement user deletion with confirmation
  console.log("Delete user:", user);
};

onMounted(() => {
  fetchUsers();
});
</script>
