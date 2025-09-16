<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <div
      class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform -translate-x-full lg:translate-x-0 transition-transform duration-200 ease-in-out"
      :class="{ 'translate-x-0': sidebarOpen }"
    >
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between h-16 px-6 bg-primary-600">
        <h1 class="text-xl font-bold text-white">BackboneOS</h1>
        <UButton
          variant="ghost"
          size="sm"
          icon="i-heroicons-x-mark"
          class="lg:hidden text-white"
          @click="sidebarOpen = false"
        />
      </div>

      <!-- Navigation -->
      <nav class="mt-8 px-4">
        <div class="space-y-2">
          <UButton
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            variant="ghost"
            :class="[
              'w-full justify-start font-medium',
              $route.path === item.href
                ? 'bg-primary-50 text-primary-600 border-r-2 border-primary-600'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
            ]"
          >
            <UIcon :name="item.icon" class="mr-3 h-5 w-5" />
            {{ item.name }}
          </UButton>
        </div>
      </nav>
    </div>

    <!-- Main content -->
    <div class="lg:pl-64">
      <!-- Top header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div
          class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8"
        >
          <div class="flex items-center">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-heroicons-bars-3"
              class="lg:hidden"
              @click="sidebarOpen = true"
            />
            <h2 class="text-xl font-semibold text-gray-900 ml-4 lg:ml-0">
              <slot name="title">Dashboard</slot>
            </h2>
          </div>

          <!-- User menu -->
          <div class="flex items-center space-x-4">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-heroicons-bell"
              class="relative"
            >
              <span
                class="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-xs text-white flex items-center justify-center"
                >3</span
              >
            </UButton>

            <UDropdown
              :items="userMenuItems"
              :popper="{ placement: 'bottom-end' }"
            >
              <UAvatar
                :src="user?.avatar"
                :alt="user?.username || 'User'"
                size="sm"
                class="cursor-pointer"
              />
            </UDropdown>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>

    <!-- Mobile sidebar overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
      @click="sidebarOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
const { user, logout } = useAuth();

// Sidebar state
const sidebarOpen = ref(false);

// Navigation items
const navigation = [
  { name: "Dashboard", href: "/", icon: "i-heroicons-home" },
  { name: "Leads", href: "/leads", icon: "i-heroicons-user-plus" },
  // {
  //   name: "Opportunities",
  //   href: "/opportunities",
  //   icon: "i-heroicons-light-bulb",
  // },
  // { name: "Customers", href: "/customers", icon: "i-heroicons-users" },
  // { name: "Pipeline", href: "/pipeline", icon: "i-heroicons-chart-bar" },
  // { name: "Deals", href: "/deals", icon: "i-heroicons-banknotes" },
  // { name: "Quotes", href: "/quotes", icon: "i-heroicons-document-text" },
  // { name: "Reports", href: "/reports", icon: "i-heroicons-chart-pie" },
  // {
  //   name: "Analytics",
  //   href: "/analytics",
  //   icon: "i-heroicons-presentation-chart-line",
  // },
  { name: "Users", href: "/users", icon: "i-heroicons-user-group" },
  { name: "Settings", href: "/settings", icon: "i-heroicons-cog-6-tooth" },
];

// User menu items
const userMenuItems = [
  [
    {
      label: user.value?.email || "Profile",
      avatar: { src: user.value?.avatar },
      disabled: true,
    },
  ],
  [
    {
      label: "Profile Settings",
      icon: "i-heroicons-user-circle",
      click: () => navigateTo("/settings/profile"),
    },
    {
      label: "Account Settings",
      icon: "i-heroicons-cog-6-tooth",
      click: () => navigateTo("/settings/account"),
    },
  ],
  [
    {
      label: "Sign out",
      icon: "i-heroicons-arrow-right-on-rectangle",
      click: logout,
    },
  ],
];
</script>
