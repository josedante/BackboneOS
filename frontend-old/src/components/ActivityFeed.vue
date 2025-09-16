<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        <UButton v-if="viewAllLink" variant="ghost" size="sm" :to="viewAllLink">
          View all
        </UButton>
      </div>
    </template>

    <div v-if="loading" class="flex justify-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="h-5 w-5 animate-spin mr-2" />
      <span class="text-gray-600">Loading activities...</span>
    </div>

    <div v-else-if="activities.length === 0" class="text-center py-8">
      <UIcon
        name="i-heroicons-clock"
        class="h-12 w-12 text-gray-400 mx-auto mb-4"
      />
      <p class="text-gray-500">No recent activity</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
        @click="$emit('activityClick', activity)"
      >
        <div class="flex-shrink-0">
          <div
            class="p-2 rounded-full"
            :class="activity.iconBg || 'bg-gray-100'"
          >
            <UIcon
              :name="activity.icon"
              class="h-4 w-4"
              :class="activity.iconColor || 'text-gray-600'"
            />
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900">{{ activity.title }}</p>
          <p class="text-sm text-gray-600 mt-1">{{ activity.description }}</p>
          <div class="flex items-center justify-between mt-2">
            <p class="text-xs text-gray-500">{{ formatTime(activity.time) }}</p>
            <UBadge
              v-if="activity.priority"
              :color="getPriorityColor(activity.priority)"
              variant="subtle"
              size="xs"
            >
              {{ activity.priority }}
            </UBadge>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
interface Activity {
  id: string | number;
  title: string;
  description: string;
  time: string;
  icon: string;
  iconBg?: string;
  iconColor?: string;
  priority?: "high" | "medium" | "low";
  type?: string;
}

interface Props {
  title?: string;
  activities: Activity[];
  loading?: boolean;
  viewAllLink?: string;
}

withDefaults(defineProps<Props>(), {
  title: "Recent Activity",
  loading: false,
});

defineEmits<{
  activityClick: [activity: Activity];
}>();

const formatTime = (timeString: string) => {
  const now = new Date();
  const activityTime = new Date(timeString);
  const diffInHours =
    (now.getTime() - activityTime.getTime()) / (1000 * 60 * 60);

  if (diffInHours < 1) {
    const minutes = Math.floor(diffInHours * 60);
    return `${minutes} minutes ago`;
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)} hours ago`;
  } else {
    const days = Math.floor(diffInHours / 24);
    return `${days} days ago`;
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "high":
      return "red";
    case "medium":
      return "yellow";
    case "low":
      return "green";
    default:
      return "gray";
  }
};
</script>
