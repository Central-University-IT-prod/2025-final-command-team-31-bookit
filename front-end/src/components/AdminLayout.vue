<script setup lang="ts">
import NavbarAdmin from '@/components/NavbarAdmin.vue'
import { defineProps, ref } from 'vue'

defineProps({
  title: {
    type: String,
    default: 'Панель администратора'
  }
})

const isSidebarOpen = ref(true)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}
</script>

<template>
  <div class="admin-layout" :class="{ 'sidebar-closed': !isSidebarOpen }">
    <div class="admin-layout-content">
      <div class="admin-layout-header">
        <h1 v-if="title">{{ title }}</h1>
        <slot name="header"></slot>
      </div>
      <div class="admin-layout-body">
        <slot></slot>
      </div>
      <div class="admin-layout-footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  position: relative;
}

.sidebar-toggle {
  position: absolute;
  top: 20px;
  left: 240px;
  z-index: 1000;
  background-color: #343a40;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: left 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.sidebar-closed .sidebar-toggle {
  left: 20px;
}

.toggle-icon {
  font-size: 14px;
  font-weight: bold;
}

.admin-layout-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.sidebar-closed .admin-layout-content {
  margin-left: -250px;
}

.admin-layout-header {
  margin-bottom: 1.5rem;
}

.admin-layout-body {
  flex: 1;
}

.admin-layout-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eaeaea;
}

h1 {
  margin-bottom: 1rem;
  font-size: 1.75rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }

  .admin-layout-content {
    margin-top: 60px;
    padding: 1.5rem;
  }

  .sidebar-toggle {
    top: 10px;
    left: auto;
    right: 10px;
  }

  .sidebar-closed .sidebar-toggle {
    left: auto;
    right: 10px;
  }
}
</style>
