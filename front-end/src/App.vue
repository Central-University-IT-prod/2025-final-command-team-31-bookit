<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from './stores/booking'

const authStore = useAuthStore()
const bookingStore = useBookingStore()

onMounted(() => {
  authStore.chekAuth()
  bookingStore.getAllAdresses()
})

</script>

<template>
  <RouterView />
</template>

<style scoped>
</style>
