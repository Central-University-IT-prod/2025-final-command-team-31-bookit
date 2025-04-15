<script setup lang="ts">
import { computed } from 'vue'
import { useBookingStore } from '../../stores/booking'


const store = useBookingStore()
const floors = computed(() => store.floorInfo)
const address = computed(() => store.address)

const selectFloor = (address: string, floorId: string) => {
  store.getBuildings(address, floorId)
  store.setCurrentStep(3)
}

</script>

<template>
  <div class="booking_part2_3 container" style="display: block">
    <div class="list" v-for="floor in floors" :key="floor.id">
      <div class="row">
        <img :src="`${floor.img}`" alt="Этаж">
        <button @click="selectFloor(address, floor.id)" type="button">Этаж {{ floor.number }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '../../assets/components/booking/part2/part2_3.scss';
@import '../../assets/components/container.scss';
</style>
