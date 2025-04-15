<script setup lang="ts">
import { ref } from 'vue'
import { useBookingStore } from '../../stores/booking'

const store = useBookingStore()

const foodItems = ref([
  {
    id: 'bca0953a-be69-4e65-900d-8120927d9474',
    name: 'Кофе 1',
    price: 300,
    image: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y29mZmVlfGVufDB8fDB8fHww&w=1000&q=80 ',
    quantity: 2,
    active: true
  },
  {
    id: '28c319bd-9603-47c5-974b-238289f554c1',
    name: 'Кофе 2',
    price: 200,
    image: 'img/item2.jpg',
    quantity: 0,
    active: false
  },
  {
    id: 'c46762ca-fc6d-4b31-945e-513fe0bb9ca1',
    name: 'Кофе 3',
    price: 350,
    image: 'img/item3.jpg',
    quantity: 0,
    active: false
  }
])

const equipmentItems = ref([
  {
    id: '4e75cd6d-5a52-4d8e-8d77-2d3180d2c83e',
    name: 'Монитор',
    price: 300,
    image: 'img/item4.jpg',
    quantity: 0,
    active: false
  },
  {
    id: '8ce13580-a030-4ccc-83d8-764318d30e4d',
    name: 'Веб-камера',
    price: 200,
    image: 'img/item5.jpg',
    quantity: 0,
    active: false
  },
  {
    id: '395b70cb-3502-42f5-836a-d7191cd85e52',
    name: 'Софтбокс',
    price: 350,
    image: 'img/item6.jpg',
    quantity: 0,
    active: false
  }
])

const toggleItem = (item: any) => {
  item.active = !item.active
  if (item.active && item.quantity === 0) {
    item.quantity = 1
  }
}

const increaseQuantity = (item: any) => {
  item.quantity++
  item.active = true
}

const decreaseQuantity = (item: any) => {
  if (item.quantity > 0) {
    item.quantity--
    if (item.quantity === 0) {
      item.active = false
    }
  }
}

const saveOptions = () => {
  const selectedFood = foodItems.value.filter((item) => item.active)
  const selectedEquipment = equipmentItems.value.filter((item) => item.active)

  store.setSelectedFood(selectedFood)
  store.setSelectedEquipment(selectedEquipment)

  store.setCurrentStep(6)
}
</script>

<template>
  <div class="booking_part2_5 container">
    <h2>Еда</h2>
    <div class="cards">
      <button 
        v-for="item in foodItems" 
        :key="item.id"
        class="card"
        :class="{ active: item.active }"
        @click="toggleItem(item)"
      >
        <div class="img" :style="{ backgroundImage: `url(${item.image})` }"></div>
        <h3>{{ item.name }}</h3>
        <div class="price">{{ item.price }} руб</div>
        <div class="qty" v-if="item.active">
          <a @click.stop="decreaseQuantity(item)">-</a>
          <p>{{ item.quantity }}</p>
          <a @click.stop="increaseQuantity(item)">+</a>
        </div>
      </button>
    </div>
    
    <h2>Оборудование</h2>
    <div class="cards">
      <button 
        v-for="item in equipmentItems" 
        :key="item.id"
        class="card"
        :class="{ active: item.active }"
        @click="toggleItem(item)"
      >
        <div class="img" :style="{ backgroundImage: `url(${item.image})` }"></div>
        <h3>{{ item.name }}</h3>
        <div class="price">{{ item.price }} руб/час</div>
        <div class="qty" v-if="item.active">
          <a @click.stop="decreaseQuantity(item)">-</a>
          <p>{{ item.quantity }}</p>
          <a @click.stop="increaseQuantity(item)">+</a>
        </div>
      </button>
    </div>
  <button class="button" @click="saveOptions">Сохранить</button>

  </div>


  
</template>

<style scoped lang="scss">
@import '../../assets/components/booking/part2/part2_5.scss';
@import '../../assets/components/container.scss';
$color: #ffc107;

.button {
  display: inline-block;
  padding: .75rem 1.25rem;
  border: none;
  border-radius: 5rem;
  color: #fff;
  text-transform: uppercase;
  font-size: 1rem;
  letter-spacing: .15rem;
  transition: all .3s;
  position: relative;
  overflow: hidden;
  z-index: 1;
  &:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: $color;
    border-radius: 10rem;
    z-index: -2;
  }
  &:before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0%;
    height: 100%;
    background-color: darken($color, 15%);
    transition: all .3s;
    border-radius: 10rem;
    z-index: -1;
  }
  &:hover {
    color: #fff;
    &:before {
      width: 100%;
    }
  }
}


</style>
