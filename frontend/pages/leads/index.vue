<template>
  <NuxtLayout name="dashboard">
    <template #title>Leads</template>

    <!-- Header section -->
    <div class="mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Lead Management</h1>
          <p class="text-gray-600 mt-1">Track and manage your sales leads</p>
        </div>
        <div class="mt-4 sm:mt-0 flex space-x-3">
          <UButton variant="outline" icon="i-heroicons-funnel" size="sm">
            Filters
          </UButton>
          <UButton
            variant="outline"
            icon="i-heroicons-arrow-down-tray"
            size="sm"
          >
            Export
          </UButton>
          <UButton
            icon="i-heroicons-plus"
            size="sm"
            color="primary"
            to="/leads/new"
          >
            Add Lead
          </UButton>
        </div>
      </div>
    </div>

    <!-- Stats overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <DashboardStatCard
        title="Total Leads"
        value="2,847"
        change="+12.5% from last month"
        change-type="increase"
        icon="i-heroicons-user-plus"
        icon-bg="bg-blue-100"
        icon-color="text-blue-600"
      />
      <DashboardStatCard
        title="Qualified"
        value="1,248"
        change="+8.3% from last month"
        change-type="increase"
        icon="i-heroicons-check-badge"
        icon-bg="bg-green-100"
        icon-color="text-green-600"
      />
      <DashboardStatCard
        title="Conversion Rate"
        value="43.8%"
        change="+2.1% from last month"
        change-type="increase"
        icon="i-heroicons-arrow-trending-up"
        icon-bg="bg-purple-100"
        icon-color="text-purple-600"
      />
      <DashboardStatCard
        title="Avg. Response Time"
        value="2.4h"
        change="-15min from last month"
        change-type="increase"
        icon="i-heroicons-clock"
        icon-bg="bg-yellow-100"
        icon-color="text-yellow-600"
      />
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <!-- Leads table -->
      <div class="lg:col-span-3">
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">Recent Leads</h3>
              <div class="flex items-center space-x-3">
                <UInput
                  placeholder="Search leads..."
                  icon="i-heroicons-magnifying-glass"
                  size="sm"
                  v-model="searchQuery"
                />
                <USelectMenu
                  v-model="selectedStatus"
                  :options="statusOptions"
                  placeholder="All Status"
                  size="sm"
                />
              </div>
            </div>
          </template>

          <div v-if="loading" class="flex justify-center py-8">
            <UIcon
              name="i-heroicons-arrow-path"
              class="h-6 w-6 animate-spin mr-2"
            />
            <span>Loading leads...</span>
          </div>

          <div v-else-if="leads.length > 0" class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Lead
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Company
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Source
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Value
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Created
                  </th>
                  <th class="relative px-6 py-3">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="lead in filteredLeads"
                  :key="lead.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <UAvatar
                        :src="lead.avatar"
                        :alt="lead.name"
                        size="sm"
                        class="mr-3"
                      />
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{
                          lead.name
                        }}</div>
                        <div class="text-sm text-gray-500">{{
                          lead.email
                        }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ lead.company }}</div>
                    <div class="text-sm text-gray-500">{{ lead.title }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <UBadge
                      :color="getStatusColor(lead.status)"
                      variant="subtle"
                    >
                      {{ lead.status }}
                    </UBadge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ lead.source }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${{ lead.estimatedValue.toLocaleString() }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(lead.createdAt) }}
                  </td>
                  <td
                    class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                  >
                    <UDropdown :items="getLeadActions(lead)">
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

          <div v-else class="text-center py-12">
            <UIcon
              name="i-heroicons-user-plus"
              class="h-12 w-12 text-gray-400 mx-auto mb-4"
            />
            <h3 class="text-lg font-medium text-gray-900 mb-2"
              >No leads found</h3
            >
            <p class="text-gray-500 mb-4"
              >Start by adding your first lead or adjust your filters.</p
            >
            <UButton icon="i-heroicons-plus" color="primary" to="/leads/new">
              Add Lead
            </UButton>
          </div>
        </UCard>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Lead Sources -->
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold text-gray-900">Lead Sources</h3>
          </template>

          <div class="space-y-4">
            <div
              v-for="source in leadSources"
              :key="source.name"
              class="flex items-center justify-between"
            >
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 rounded-full" :class="source.color" />
                <span class="text-sm font-medium text-gray-900">{{
                  source.name
                }}</span>
              </div>
              <div class="text-right">
                <span class="text-sm font-semibold text-gray-900">{{
                  source.count
                }}</span>
                <span class="text-xs text-gray-500 block"
                  >{{ source.percentage }}%</span
                >
              </div>
            </div>
          </div>
        </UCard>

        <!-- Recent Activity -->
        <ActivityFeed
          title="Lead Activity"
          :activities="leadActivity"
          :loading="false"
        />
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import DashboardStatCard from "~/src/components/DashboardStatCard.vue";
import ActivityFeed from "~/src/components/ActivityFeed.vue";

definePageMeta({
  middleware: "auth",
});

// Reactive data
const loading = ref(false);
const searchQuery = ref("");
const selectedStatus = ref("");

// Status options for filter
const statusOptions = [
  { label: "All Status", value: "" },
  { label: "New", value: "new" },
  { label: "Contacted", value: "contacted" },
  { label: "Qualified", value: "qualified" },
  { label: "Proposal", value: "proposal" },
  { label: "Closed Won", value: "closed-won" },
  { label: "Closed Lost", value: "closed-lost" },
];

// Mock leads data
const leads = ref([
  {
    id: 1,
    name: "John Doe",
    email: "john.doe@techcorp.com",
    company: "Tech Corp",
    title: "CTO",
    status: "qualified",
    source: "Website",
    estimatedValue: 45000,
    createdAt: "2024-05-28T10:00:00Z",
    avatar: "",
  },
  {
    id: 2,
    name: "Jane Smith",
    email: "jane.smith@startup.io",
    company: "Startup Inc",
    title: "CEO",
    status: "new",
    source: "Referral",
    estimatedValue: 75000,
    createdAt: "2024-05-29T14:30:00Z",
    avatar: "",
  },
  {
    id: 3,
    name: "Mike Johnson",
    email: "mike@acme.com",
    company: "Acme Industries",
    title: "Director",
    status: "proposal",
    source: "LinkedIn",
    estimatedValue: 120000,
    createdAt: "2024-05-25T09:15:00Z",
    avatar: "",
  },
]);

// Lead sources
const leadSources = ref([
  { name: "Website", count: 1247, percentage: 42, color: "bg-blue-400" },
  { name: "LinkedIn", count: 856, percentage: 29, color: "bg-blue-600" },
  { name: "Referral", count: 534, percentage: 18, color: "bg-green-400" },
  { name: "Cold Email", count: 210, percentage: 11, color: "bg-yellow-400" },
]);

// Lead activity
const leadActivity = ref([
  {
    id: 1,
    title: "New lead from Tech Corp",
    description: "John Doe submitted contact form on pricing page",
    time: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    icon: "i-heroicons-user-plus",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
  },
  {
    id: 2,
    title: "Lead qualified",
    description: "Jane Smith moved to qualified stage",
    time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    icon: "i-heroicons-check-badge",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
  },
]);

// Computed
const filteredLeads = computed(() => {
  let filtered = leads.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (lead) =>
        lead.name.toLowerCase().includes(query) ||
        lead.email.toLowerCase().includes(query) ||
        lead.company.toLowerCase().includes(query)
    );
  }

  if (selectedStatus.value) {
    filtered = filtered.filter((lead) => lead.status === selectedStatus.value);
  }

  return filtered;
});

// Methods
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    new: "blue",
    contacted: "yellow",
    qualified: "green",
    proposal: "purple",
    "closed-won": "green",
    "closed-lost": "red",
  };
  return colors[status] || "gray";
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const getLeadActions = (lead: any) => [
  [
    {
      label: "View Details",
      icon: "i-heroicons-eye",
      click: () => navigateTo(`/leads/${lead.id}`),
    },
    {
      label: "Edit Lead",
      icon: "i-heroicons-pencil",
      click: () => navigateTo(`/leads/${lead.id}/edit`),
    },
  ],
  [
    {
      label: "Convert to Deal",
      icon: "i-heroicons-arrow-right",
      click: () => convertToDeal(lead),
    },
  ],
  [
    {
      label: "Delete Lead",
      icon: "i-heroicons-trash",
      click: () => deleteLead(lead),
    },
  ],
];

const convertToDeal = (lead: any) => {
  console.log("Convert to deal:", lead);
};

const deleteLead = (lead: any) => {
  console.log("Delete lead:", lead);
};
</script>
