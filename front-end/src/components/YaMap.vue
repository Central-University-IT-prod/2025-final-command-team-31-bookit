<script setup lang="ts">
import { shallowRef, ref, computed, onMounted, onErrorCaptured } from 'vue'
import type { YMap } from '@yandex/ymaps3-types'
import { useBookingStore } from '@/stores/booking'
import {
  YandexMap,
  YandexMapDefaultSchemeLayer,
  YandexMapDefaultFeaturesLayer,
  YandexMapMarker,
} from 'vue-yandex-maps'


const store = useBookingStore()
const addresses = computed(() => store.addressInfo)
const mapError = ref<string | null>(null)
const isLoading = ref(true)

const map = shallowRef<YMap | null>(null)

const markerSelect = async(id: string) => {
  console.log('Selected marker:', id)
  store.setCurrentStep(1)
  await store.getBuildings(id)
}

const toggleMarkerInfo = (index: number) => {
  const markerElement = document.getElementById(`marker_${index}`)
  if (markerElement) {
    markerElement.classList.toggle('marker_show')
  }
}

const handleMapError = (error: any) => {
  console.error('Map error:', error)
  mapError.value = 'Не удалось загрузить карту. Пожалуйста, попробуйте позже.'
  return false // Контр ошибка
}

const handleMapLoad = () => {
  console.log('Map loaded successfully')
  isLoading.value = false
}

onErrorCaptured(handleMapError)

onMounted(() => {
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  if (isMobile) {
    console.log('Mobile device detected')
  }

  setTimeout(() => {
    if (isLoading.value) {
      console.log('Forcing map to show after timeout')
      isLoading.value = false
    }
  }, 3000)
})
</script>

<template>
  <div id="yamap" class="yamap-container">
    <div v-if="mapError" class="map-error">
      {{ mapError }}
    </div>
    <div v-else-if="isLoading" class="map-loading">
      Загрузка карты...
    </div>
    <yandex-map
      v-else
      v-model="map"
      :settings="{
        location: {
          center: [37.588144, 55.733842],
          zoom: 5,
        },
      }"
      width="100%"
      height="500px"
      @created="handleMapLoad"
    >
      <yandex-map-default-scheme-layer />
      <yandex-map-default-features-layer />

      <template v-for="(element, index) in addresses" :key="element.id">
        <yandex-map-marker v-if="element.lat" :settings="{ coordinates: [element.lat, element.lon] }">
          <div class="marker-class">
            <div>
              <button @click="toggleMarkerInfo(index)">
                <img src="/img/yamaps_icon.png" alt="Marker Icon" />
              </button>
              <div :id="`marker_${index}`" class="marker-info">
                <p>{{ element.name }}</p>
                <button type="button" @click="markerSelect(element.id)">Выбрать</button>
              </div>
            </div>
          </div>
        </yandex-map-marker>
      </template>
    </yandex-map>
  </div>
</template>

<style lang="scss" scoped>
@import '../assets/components/booking/part2/part2_1.scss';
@import '../assets/variables.scss';

.yamap-container {
  position: relative;
  width: 100%;
  height: 500px;
}

.map-error, .map-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: #f5f5f5;
  color: #333;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
}

.map-error {
  background-color: #fff0f0;
  color: #d32f2f;
}

.marker-info {
  display: none;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: absolute;
  z-index: 100;
  min-width: 150px;

  &.marker_show {
    display: block;
  }

  button {
    margin-top: 8px;
    padding: 5px 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;

    &:hover {
      background-color: #45a049;
    }
  }
}

// Адаптивность для мобильных устройств
@media (max-width: 768px) {
  .yamap-container {
    height: 300px;
  }

  .marker-info {
    min-width: 120px;
    font-size: 14px;

    button {
      padding: 4px 8px;
      font-size: 12px;
    }
  }
}
</style>
