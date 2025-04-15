<script setup lang="ts">
import { computed } from 'vue'
import { useBookingStore } from '../../stores/booking'

const store = useBookingStore()
const buildings = computed(() => store.buildingInfo)

const selectBuilding = (buildingId: string, addressID: string) => {
  store.getFloor(buildingId, addressID)
  store.setCurrentStep(2)
}


</script>

<template>
  <div class="booking_part2_2 container" style="display: flex">
    <div class="card" v-for="building in buildings" :key="building.id">
      <div class="img" :style="{'background-image': `${building.img}`}"></div>
      <h3>{{ building.name }}</h3>
      <button @click="selectBuilding(building.id, building.address_id)">Выбрать</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '../../assets/components/booking/part2/part2_2.scss';
@import '../../assets/components/container.scss';

</style>
