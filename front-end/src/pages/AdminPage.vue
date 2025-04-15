<script setup lang="ts">
import { computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import NavbarAdmin from '@/components/NavbarAdmin.vue'
import NewCoworking from '@/components/NewCoworking.vue'
import AdminLayout from '@/components/AdminLayout.vue'
import Dashboard from '@/components/Dashboard.vue'

const adminStore = useAdminStore()
const component = computed(() => adminStore.components)
</script>

<template>
  <div class="container">
    <NavbarAdmin />
    <div class="content">
      <Dashboard v-show="component === 'dashboard'"></Dashboard>
      <NewCoworking v-show="component === 'coworking'"></NewCoworking>
      <AdminLayout v-show="component === 'layout'"></AdminLayout>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  min-height: 100vh;
}

.content {
  flex: 1;
  padding: 2rem;
}
</style>
