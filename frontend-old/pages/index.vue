<template>
  <NuxtLayout name="dashboard">
    <template #title>Dashboard</template>

    <!-- Welcome section -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        Welcome back, {{ user?.first_name || user?.username }}! 👋
      </h1>
      <p class="text-gray-600 mt-1"
        >Here's what's happening with your business today.</p
      >
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <DashboardStatCard
        v-for="stat in stats"
        :key="stat.title"
        :title="stat.title"
        :value="stat.value"
        :change="stat.change"
        :change-type="stat.changeType"
        :icon="stat.icon"
        :icon-bg="stat.iconBg"
        :icon-color="stat.iconColor"
      />
    </div>

    <!-- Main dashboard content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Recent activity -->
      <div class="lg:col-span-2">
        <ActivityFeed
          title="Recent Activity"
          :activities="recentActivity"
          :loading="loadingActivity"
          view-all-link="/activity"
          @activity-click="handleActivityClick"
        />
      </div>

      <!-- Quick actions & overview -->
      <div class="space-y-6">
        <!-- Quick actions -->
        <QuickActions title="Quick Actions" :actions="quickActions" />

        <!-- Pipeline overview -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900"
                >Sales Pipeline</h3
              >
              <UButton variant="ghost" size="sm" to="/pipeline"
                >View Pipeline</UButton
              >
            </div>
          </template>

          <div class="space-y-4">
            <div
              v-for="stage in pipelineStages"
              :key="stage.name"
              class="flex items-center justify-between"
            >
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 rounded-full" :class="stage.color" />
                <span class="text-sm font-medium text-gray-900">{{
                  stage.name
                }}</span>
              </div>
              <div class="text-right">
                <span class="text-sm font-semibold text-gray-900">{{
                  stage.count
                }}</span>
                <span class="text-xs text-gray-500 ml-1"
                  >${{ stage.value }}</span
                >
              </div>
            </div>

            <!-- Pipeline progress bar -->
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div
                class="flex items-center justify-between text-sm text-gray-600 mb-2"
              >
                <span>Overall Progress</span>
                <span>{{ calculatePipelineProgress() }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${calculatePipelineProgress()}%` }"
                />
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import DashboardStatCard from "~/src/components/DashboardStatCard.vue";
import ActivityFeed from "~/src/components/ActivityFeed.vue";
import QuickActions from "~/src/components/QuickActions.vue";

const { user } = useAuth();

definePageMeta({
  middleware: "auth",
});

// Loading states
const loadingActivity = ref(false);

// Dashboard stats
const stats = ref([
  {
    title: "Total Leads",
    value: "2,847",
    change: "+12.5% from last month",
    changeType: "increase" as const,
    icon: "i-heroicons-user-plus",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
  },
  {
    title: "Active Deals",
    value: "184",
    change: "+8.2% from last month",
    changeType: "increase" as const,
    icon: "i-heroicons-banknotes",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
  },
  {
    title: "Revenue",
    value: "$847,290",
    change: "+4.3% from last month",
    changeType: "increase" as const,
    icon: "i-heroicons-chart-bar",
    iconBg: "bg-yellow-100",
    iconColor: "text-yellow-600",
  },
  {
    title: "Conversion Rate",
    value: "24.8%",
    change: "-2.1% from last month",
    changeType: "decrease" as const,
    icon: "i-heroicons-arrow-trending-up",
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
  },
]);

// Recent activity with proper timestamps
const recentActivity = ref([
  {
    id: 1,
    title: "New lead added",
    description:
      "John Doe from Tech Corp expressed interest in our Enterprise plan",
    time: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
    icon: "i-heroicons-user-plus",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
    priority: "high" as const,
  },
  {
    id: 2,
    title: "Deal closed",
    description: "Successfully closed $45,000 deal with Acme Industries",
    time: new Date(Date.now() - 60 * 60 * 1000).toISOString(), // 1 hour ago
    icon: "i-heroicons-check-circle",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
    priority: "high" as const,
  },
  {
    id: 3,
    title: "Quote sent",
    description: "Sent proposal to StartupXYZ for their Q2 requirements",
    time: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
    icon: "i-heroicons-document-text",
    iconBg: "bg-yellow-100",
    iconColor: "text-yellow-600",
    priority: "medium" as const,
  },
  {
    id: 4,
    title: "Meeting scheduled",
    description: "Demo call scheduled with GlobalTech for next Tuesday",
    time: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
    icon: "i-heroicons-calendar",
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
    priority: "low" as const,
  },
]);

// Quick actions with badges
const quickActions = ref([
  {
    name: "Add New Lead",
    icon: "i-heroicons-plus",
    href: "/leads/new",
    badge: "5",
    badgeColor: "blue",
  },
  {
    name: "Create Quote",
    icon: "i-heroicons-document-plus",
    href: "/quotes/new",
  },
  {
    name: "Schedule Meeting",
    icon: "i-heroicons-calendar-plus",
    href: "/calendar/new",
    badge: "New",
    badgeColor: "green",
  },
  {
    name: "View Reports",
    icon: "i-heroicons-chart-bar-square",
    href: "/reports",
    badge: "3",
    badgeColor: "yellow",
  },
]);

// Pipeline stages with values
const pipelineStages = ref([
  { name: "Prospecting", count: "127", value: "890K", color: "bg-gray-400" },
  { name: "Qualification", count: "89", value: "1.2M", color: "bg-blue-400" },
  { name: "Proposal", count: "43", value: "780K", color: "bg-yellow-400" },
  { name: "Negotiation", count: "21", value: "560K", color: "bg-orange-400" },
  { name: "Closed Won", count: "156", value: "2.1M", color: "bg-green-400" },
]);

// Methods
const handleActivityClick = (activity: {
  id: string | number;
  title: string;
  description: string;
}) => {
  console.log("Activity clicked:", activity);
  // Navigate to activity detail or perform action
};

const calculatePipelineProgress = () => {
  const totalDeals = pipelineStages.value.reduce(
    (sum, stage) => sum + parseInt(stage.count),
    0
  );
  const closedWon = parseInt(pipelineStages.value[4].count);
  return Math.round((closedWon / totalDeals) * 100);
};
</script>
