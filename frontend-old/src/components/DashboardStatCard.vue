<template>
  <UCard class="p-6 hover:shadow-md transition-shadow duration-200">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-3xl font-bold text-gray-900 mt-2">{{ value }}</p>
        <p
          v-if="change"
          class="text-sm mt-1 flex items-center"
          :class="
            changeType === 'increase'
              ? 'text-green-600'
              : changeType === 'decrease'
              ? 'text-red-600'
              : 'text-gray-600'
          "
        >
          <UIcon
            v-if="changeType === 'increase'"
            name="i-heroicons-arrow-trending-up"
            class="h-4 w-4 mr-1"
          />
          <UIcon
            v-else-if="changeType === 'decrease'"
            name="i-heroicons-arrow-trending-down"
            class="h-4 w-4 mr-1"
          />
          {{ change }}
        </p>
      </div>
      <div
        class="p-3 rounded-full flex-shrink-0 ml-4"
        :class="iconBg || 'bg-primary-100'"
      >
        <UIcon
          :name="icon"
          class="h-6 w-6"
          :class="iconColor || 'text-primary-600'"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "increase" | "decrease" | "neutral";
  icon: string;
  iconBg?: string;
  iconColor?: string;
}

defineProps<Props>();
</script>
