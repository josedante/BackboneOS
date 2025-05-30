<template>
  <div>
    <UserList />
  </div>
</template>

<script setup lang="ts">
import UserList from '~/src/components/UserList.vue'

definePageMeta({
  middleware: 'auth'
})
</script>