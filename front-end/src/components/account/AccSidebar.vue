<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { computed } from 'vue'

const authStore = useAuthStore()
const profileStore = useProfileStore()
const name = computed(() => authStore.userInfo.user.name)

const steps = [
  { id: 0, name: 'Быстрый доступ' },
  { id: 1, name: 'Основные данные' },
  { id: 2, name: 'Бронирования' },
  { id: 3, name: 'История' },
  { id: 4, name: 'Группы' },
  { id: 5, name: 'Поддержка' },
  { id: 6, name: 'Сбросить QR код' },
]

const setStep = (step: number) => {
  profileStore.setCurrentStep(step)
}

const logOut = async () => {
  await authStore.logOut()
}

</script>

<template>
  <div class="sidebar">
    <div class="maininfo">
      <h3>{{ name }}</h3>
    </div>
    <a v-for="step in steps" class="link" :key="step.id" @click="setStep(step.id)">
      {{ step.name }}
    </a>
    
    <a @click="logOut" class="link logout">Выйти</a>
  </div>
</template>

<style lang="scss">
@import '../../assets/variables.scss';
</style>
