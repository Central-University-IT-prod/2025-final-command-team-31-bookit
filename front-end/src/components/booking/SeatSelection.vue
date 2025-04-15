<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBookingStore } from '../../stores/booking'

const store = useBookingStore()
const mapElement = ref<HTMLElement | null>(null)
const floorplanElement = ref<HTMLElement>()
const mousedown = ref(false)
const mapOffX = ref(0)
const mapOffY = ref(0)
const zoom = ref(1)
const toggledSeat = ref(-1)

const seats = [
  {
    id: '395693ce-759e-477b-8975-b675781abc58',
    posx: 0.5,
    posy: 0.5,
    name: 'Место 1',
    price: 300,
    status: 'empty',
  },
  {
    id: 'b014cea6-ce67-4c99-b36d-f3909ea4ca28',
    posx: 0.6,
    posy: 0.5,
    name: 'Место 2',
    price: 200,
    status: 'partial',
  },
  {
    id: '29508764-8350-4e94-9238-d652e2cda723',
    posx: 0.6,
    posy: 0.6,
    name: 'Место 3',
    price: 0,
    status: 'full',
  },
]

const marketDim = 20
const markerPad = 5

function handleMouseMove(event: MouseEvent) {
  if (mousedown.value) {
    mapOffX.value += event.movementX / zoom.value
    mapOffY.value += event.movementY / zoom.value

    if (floorplanElement.value) {
      floorplanElement.value.style.transform = `translate(${mapOffX.value}px, ${mapOffY.value}px)`
    }

    fixpos()
  }
}

function handleMouseDown() {
  mousedown.value = true
}

function handleMouseUp() {
  mousedown.value = false
}

function handleMouseLeave() {
  mousedown.value = false
}

function handleWheel(event: WheelEvent) {
  const zoomdelta = event.deltaY * 0.1 * -1
  let newzoom = zoom.value + zoomdelta
  newzoom = Math.min(Math.max(newzoom, 0.5), 3)

  zoom.value = newzoom

  if (floorplanElement.value) {
    floorplanElement.value.style.scale = `${newzoom}`
    floorplanElement.value.style.transform = `translate(${mapOffX.value}px, ${mapOffY.value}px)`
  }

  fixpos()

  event.preventDefault()
}

function fixpos() {
  if (!floorplanElement.value) return

  const imgw = floorplanElement.value.clientWidth * zoom.value
  const imgh = floorplanElement.value.clientHeight * zoom.value

  for (let i = 0; i < seats.length; i++) {
    const seatBtn = document.getElementById(`seat_btn_${i}`)
    const seatDesc = document.getElementById(`seat_desc_${i}`)

    if (seatBtn && seatDesc) {
      seatBtn.style.transform = `translate(${mapOffX.value * zoom.value - imgw / 2 + imgw * seats[i].posx}px, ${mapOffY.value * zoom.value - imgh / 2 + imgh * seats[i].posy}px)`

      const mw = seatDesc.clientWidth
      const mh = seatDesc.clientHeight
      const xpos =
        mapOffX.value * zoom.value -
        imgw / 2 +
        imgw * seats[i].posx -
        markerPad +
        mw / 2 -
        marketDim / 2
      const ypos =
        mapOffY.value * zoom.value -
        imgh / 2 +
        imgh * seats[i].posy -
        markerPad +
        mh / 2 -
        marketDim / 2

      seatDesc.style.transform = `translate(${xpos}px, ${ypos}px)`
    }
  }
}

function toggleSeat(i: number) {
  untoggleSeats()

  if (toggledSeat.value === -1 || toggledSeat.value !== i) {
    toggledSeat.value = i
    const seatBtn = document.getElementById(`seat_btn_${i}`)
    const seatDesc = document.getElementById(`seat_desc_${i}`)

    if (seatBtn && seatDesc) {
      seatBtn.style.zIndex = '5'
      seatDesc.style.zIndex = '4'
      seatDesc.style.display = 'flex'
    }
  } else {
    toggledSeat.value = -1
  }

  fixpos()
}

function untoggleSeats() {
  for (let i = 0; i < seats.length; i++) {
    const seatBtn = document.getElementById(`seat_btn_${i}`)
    const seatDesc = document.getElementById(`seat_desc_${i}`)

    if (seatBtn && seatDesc) {
      seatBtn.style.zIndex = '3'
      seatDesc.style.zIndex = '0'
      seatDesc.style.display = 'none'
    }
  }
}

function selectSeat(seatId: string) {
  store.setSelectedSeat(seatId)
  store.setCurrentStep(5)
}
fixpos()

onMounted(() => {
  fixpos()
  if (mapElement.value) {
    mapElement.value.addEventListener('mousemove', handleMouseMove)
    mapElement.value.addEventListener('mousedown', handleMouseDown)
    mapElement.value.addEventListener('mouseup', handleMouseUp)
    mapElement.value.addEventListener('mouseleave', handleMouseLeave)
    mapElement.value.addEventListener('wheel', handleWheel)
  }

  if (floorplanElement.value) {
    floorplanElement.value.setAttribute('draggable', 'false')
    fixpos()
  }

  setTimeout(fixpos, 100)
})

</script>

<template>
  <div class="booking_part2_4 container">
    <div id="map" ref="mapElement">
      <img src="../../../public/img/floorplan.jpg" id="floorplan" ref="floorplanElement" />

      <button
        type="button"
        v-for="(seat, i) in seats"
        :key="seat.id"
        :id="`seat_btn_${i}`"
        :class="seat.status"
        @click="toggleSeat(i)"
      >
        {{ seat.price > 0 ? '$' : '' }}
      </button>

      <div v-for="(seat, i) in seats" :key="`desc_${seat.id}`" :id="`seat_desc_${i}`" class="desc">
        <h3>{{ seat.name }}</h3>
        <p>Цена: {{ seat.price }} руб/час</p>
        <button type="button" @click="selectSeat(seat.id)">Выбрать</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '../../assets/components/booking/part2/part2_4.scss';
@import '../../assets/components/container.scss';
</style>
