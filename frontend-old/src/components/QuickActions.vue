<template>
  <UCard>
    <template #header>
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
    </template>

    <div class="space-y-3">
      <UButton
        v-for="action in actions"
        :key="action.name"
        :to="action.href"
        variant="outline"
        block
        class="justify-start hover:bg-gray-50"
        @click="action.onClick && action.onClick()"
      >
        <UIcon :name="action.icon" class="mr-2 h-4 w-4" />
        {{ action.name }}
        <UBadge
          v-if="action.badge"
          :color="action.badgeColor || 'primary'"
          variant="subtle"
          size="xs"
          class="ml-auto"
        >
          {{ action.badge }}
        </UBadge>
      </UButton>
    </div>
  </UCard>
</template>

<script setup lang="ts">
interface QuickAction {
  name: string;
  icon: string;
  href?: string;
  onClick?: () => void;
  badge?: string | number;
  badgeColor?: string;
}

interface Props {
  title?: string;
  actions: QuickAction[];
}

withDefaults(defineProps<Props>(), {
  title: "Quick Actions",
});
</script>
