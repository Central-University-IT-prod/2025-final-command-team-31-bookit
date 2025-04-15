<script setup lang="ts">
import { computed } from 'vue'
import { useBookingStore } from '../../stores/booking'

const store = useBookingStore()
const selectedAddress = computed(() => store.selectedAddress)
const floorId = computed(() => store.floorId)
const selectedSeat = computed(() => store.selectedSeat)
const selectedFood = computed(() => store.selectedFood)
const timeFrom = computed(() => store.tFrom)
const timeTo = computed(() => store.tTo)

const submitBooking = async() => {
  console.log(timeFrom.value,timeTo.value );
  
  // Create times array from bookingTimes
  const times = ([{
    t_from: timeFrom.value, // Assuming timestamp is available or needs to be added
    t_to: timeTo.value      // Assuming timestamp is available or needs to be added
  }])
  
  // Create items array from selectedFood and selectedEquipment
  const items = [
    ...selectedFood.value.map(food => ({
      item_id: food.id,
      qty: food.quantity
    })),
    ...store.selectedEquipment.map(equipment => ({
      item_id: equipment.id,
      qty: equipment.quantity
    }))
  ]
  // Call the store method with the new format
  store.bookOne(floorId.value, selectedSeat.value, times, items, store.comment || '')
}

const totalPrice = computed(() => {
  return store.calculateTotalPrice()
})
</script>

<template>
  <div class="booking_summary">
    <h2>Итог заказа</h2>
    
    <div class="summary_section">
      <h3>Выбранное место</h3>
      <p>{{ selectedSeat }}</p>
    </div>
    
    <div class="summary_section">
      <h3>Выбранное время</h3>
      <div v-for="(booking, index) in store.bookingTimes" :key="index">
        <p>{{ booking.date }} ({{ booking.dayOfWeek }}) с {{ booking.timeFrom.hour }}:{{ booking.timeFrom.minute }} до {{ booking.timeTo.hour }}:{{ booking.timeTo.minute }}</p>
      </div>
    </div>
    
    <div class="summary_section" v-if="selectedFood.length > 0">
      <h3>Еда</h3>
      <div v-for="food in selectedFood" :key="food.id">
        <p>{{ food.name }} x {{ food.quantity }} = {{ food.price * food.quantity }} руб</p>
      </div>
    </div>
    
    <div class="summary_section" v-if="store.selectedEquipment.length > 0">
      <h3>Оборудование</h3>
      <div v-for="equipment in store.selectedEquipment" :key="equipment.id">
        <p>{{ equipment.name }} x {{ equipment.quantity }} = {{ equipment.price * equipment.quantity }} руб/час</p>
      </div>
    </div>
    
    <div class="summary_section" v-if="store.comment">
      <h3>Комментарий</h3>
      <p>{{ store.comment }}</p>
    </div>
    
    <div class="summary_total">
      <h2>Итого: {{ totalPrice }} руб</h2>
    </div>

    <div>
      <button @click="submitBooking" type="button">Оформить бронь</button>
    </div>
  </div>
</template>

<style scoped>
.booking_summary {
  margin-top: 2rem;
}

.summary_section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.summary_section h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.summary_total {
  margin-top: 2rem;
  text-align: right;
  font-weight: bold;
}
</style>