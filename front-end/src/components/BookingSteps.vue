<script setup lang="ts">
import { computed } from 'vue'
import { useBookingStore } from '../stores/booking'

const store = useBookingStore()
const currentStep = computed(() => store.currentStep)

const steps = [
  { id: 0, name: 'Выбор адреса' },
  { id: 1, name: 'Выбор здания' },
  { id: 2, name: 'Выбор этажа' },
  { id: 3, name: 'Выбор времени' },
  { id: 4, name: 'Выбор мест' },
  { id: 5, name: 'Доп. опции' }
]

const setStep = (step: number) => {
  store.setCurrentStep(step)
  console.log(step)
}
</script>

<template>
  <div class="booking_part1 container">
    <button 
      v-for="step in steps" 
      :key="step.id"
      :class="{ active: currentStep === step.id }"
      @click="setStep(step.id)"
    >
      <p>{{ step.name }}</p>
      <div class="line"></div>
    </button>
  </div>
</template>