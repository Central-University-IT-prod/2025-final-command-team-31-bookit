<script setup lang="ts">
import { computed, ref } from 'vue'
import { useBookingStore } from '@/stores/booking'

import Header from '@/components/Header.vue'
import BookingSteps from '@/components/BookingSteps.vue'
import Footer from '../components/Footer.vue'
import AddressSelection from '@/components/booking/AddressSelection.vue'
import BuildingSelection from '@/components/booking/BuildingSelection.vue'
import FloorSelection from '@/components/booking/FloorSelection.vue'
import SeatSelection from '@/components/booking/SeatSelection.vue'
import TimeSelection from '@/components/booking/TimeSelection.vue'
import OptionsSelection from '@/components/booking/OptionsSelection.vue'
import BookingSummary from '@/components/booking/BookingSummary.vue'

const store = useBookingStore()
const currentStep = computed(() => store.currentStep)
const step = ref(0)

const component = ref('')

const stepForwad = () => {
  step.value += 1
  store.setCurrentStep(step.value)
  console.log(step.value)
}

const stepBack = () => {
  step.value -= 1
  store.setCurrentStep(step.value)
  console.log(step.value)
}

const handleChangeComponent = () => {
  step.value = 7
  store.setCurrentStep(step.value)
  if (component.value === '') {
    return (component.value = 'summary')
  }
}
</script>

<template>
  <Header />
  <div class="navbar_spacer"></div>
  <BookingSteps></BookingSteps>

  <AddressSelection v-show="currentStep === 0"></AddressSelection>
  <BuildingSelection v-show="currentStep === 1"></BuildingSelection>
  <FloorSelection v-show="currentStep === 2"></FloorSelection>
  <TimeSelection v-show="currentStep === 3"></TimeSelection>
  <SeatSelection v-show="currentStep === 4"></SeatSelection>
  <OptionsSelection v-show="currentStep === 5"></OptionsSelection>

  <BookingSummary v-show="currentStep > 5"></BookingSummary>

  <Footer />
</template>

<style scoped lang="scss">
@import '../assets/components/booking/part1.scss';
@import '../assets/components/booking/part2/part2_1.scss';
@import '../assets/components/booking/part2/part2_2.scss';
@import '../assets/components/booking/part2/part2_3.scss';
@import '../assets/components/booking/part2/part2_4.scss';
@import '../assets/components/booking/part2/part2_5.scss';
@import '../assets/components/booking/part2/part2_6.scss';
@import '../assets/components/booking/part3.scss';
@import '../assets/components/container.scss';
@import '../assets/variables.scss';

.booking_part1 {
  display: flex;
  margin-top: 30px;

  button {
    display: flex;
    flex-direction: column;
    width: 100%;
    padding: 0 3px;
    align-items: flex-start;
    background: none;
    border: none;
    cursor: pointer;

    p {
      color: $muted;
      font-size: 18px;
      padding-bottom: 5px;
    }

    .line {
      width: 100%;
      height: 3px;
      //background: $primary;
      background: #ccc;
      margin-top: auto;
    }
  }

  .active {
    p {
      color: $black;
    }

    .line {
      background: $primary;
    }
  }
}

.navbar_spacer {
  height: 50px;
}
</style>
