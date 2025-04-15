import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAdminStore = defineStore('admin', () => {
  const components = ref('dashboard') // По умолчанию показываем dashboard

  function setComponent(component: string) {
    components.value = component
  }

  return {
    components,
    setComponent
  }
})
