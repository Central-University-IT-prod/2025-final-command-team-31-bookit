<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import axios from 'axios'

const buildingImageFile = ref<File | null>(null)
const isUploading = ref(false)
const weekDays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
const currentStep = ref(1)
const totalSteps = 3
const isSubmitting = ref(false)
const addressId = ref<string | null>(null)
const newBuildingName = ref('')

interface Floor {
  number: number | null
  floorPlan: File | null
}

interface Building {
  name: string
  floors: Floor[]
  workingHours: WorkingHoursDay[]
  buildingId?: string // Добавляем поле для хранения ID здания
}

const createDefaultWorkingHours = () => {
  return weekDays.map((_, index) => ({
    openTime: '09:00',
    closeTime: '18:00',
    isDayOff: index >= 5, // По умолчанию выходные - суббота и воскресенье
  }))
}

interface WorkingHoursDay {
  openTime: string
  closeTime: string
  isDayOff: boolean
}

const formData = reactive({
  address: '',
  latitude: null as number | null,
  longitude: null as number | null,
  buildings: [] as {
    name: string
    floors: { number: number | null; floorPlan: File | null }[]
    workingHours: { openTime: string; closeTime: string; isDayOff: boolean }[]
    buildingImage: File | null
    buildingId?: string // Добавляем поле для хранения ID здания
  }[],
})

// Функция для обработки выбора файла изображения здания
const handleBuildingImageUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const buildingIndex = getCurrentBuildingIndex.value

  if (input.files && input.files.length > 0 && buildingIndex !== -1) {
    formData.buildings[buildingIndex].buildingImage = input.files[0]
    buildingImageFile.value = input.files[0]
  }
}

const uploadBuildingData = async () => {
  if (!currentBuilding.value || !addressId.value || !buildingImageFile.value) {
    console.error('Не хватает данных для загрузки здания')
    return
  }

  try {
    // Находим текущее здание в массиве
    const buildingData = formData.buildings.find((b) => b.name === currentBuilding.value)
    if (!buildingData) {
      console.error('Здание не найдено')
      return
    }

    // Преобразуем время работы в нужный формат
    const t_from = buildingData.workingHours.map((day) => {
      if (day.isDayOff) return 0
      const [hours, minutes] = day.openTime.split(':').map(Number)
      return (hours * 60 + minutes) * 60 // Преобразуем время в минуты от начала дня
    })

    const t_to = buildingData.workingHours.map((day) => {
      if (day.isDayOff) return 0
      const [hours, minutes] = day.closeTime.split(':').map(Number)
      return (hours * 60 + minutes) * 60 // Преобразуем время в минуты от начала дня
    })

    // Создаем объект с данными здания
    const buildingDataToSend = {
      name: buildingData.name,
      address_id: addressId.value,
      t_from: t_from,
      t_to: t_to,
    }

    // Создаем FormData для отправки файлов
    const formDataToSend = new FormData()

    // Добавляем JSON данные о здании
    formDataToSend.append('building_data', JSON.stringify(buildingDataToSend))

    // Добавляем изображение здания
    if (buildingImageFile.value) {
      formDataToSend.append('img', buildingImageFile.value)
    }

    // Отправляем данные о здании
    const token: any = localStorage.getItem('token')
    const buildingResponse = await axios.post('/api/buildings/add', formDataToSend, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `${token}`,
      },
    })

    console.log('Building created:', buildingResponse.data)
    const buildingId = buildingResponse.data.uuid

    // Загружаем этажи для этого здания
    for (const floor of buildingData.floors) {
      if (floor.number !== null && floor.floorPlan !== null) {
        const floorFormData = new FormData()

        // Создаем объект с данными этажа
        const floorCreateData = {
          number: floor.number,
          building_id: buildingId,
        }

        // Добавляем JSON-объект floor_create
        floorFormData.append('floor_create', JSON.stringify(floorCreateData))

        // Добавляем изображение этажа
        floorFormData.append('img', floor.floorPlan)
        const token: any = localStorage.getItem('token')
        const floorResponse = await axios.post('/api/floors/add', floorFormData, {
          headers: {
            'Content-Type': 'multipart/form-data',
             Authorization: `${token}`
          },
        })
        console.log('Floor created:', floorResponse.data)
      }
    }

    return buildingId
  } catch (error) {
    console.error('Error uploading building data:', error)
    throw error
  }
}

const selectedBuildings = ref<string[]>([])
const currentBuilding = ref<string | null>(null)

const validateLatitude = (event: Event) => {
  const input = event.target as HTMLInputElement
  const value = parseFloat(input.value)

  if (value < 0) {
    formData.latitude = 0
  } else if (value > 90) {
    formData.latitude = 90
  }
}

const getCurrentBuildingData = () => {
  const index = getCurrentBuildingIndex.value
  if (index !== -1) {
    return formData.buildings[index]
  }
  // Возвращаем пустой объект с нужной структурой, если здание не найдено
  return {
    name: '',
    floors: [],
    workingHours: [],
    buildingImage: null,
  }
}

const validateLongitude = (event: Event) => {
  const input = event.target as HTMLInputElement
  const value = parseFloat(input.value)

  if (value < 0) {
    formData.longitude = 0
  } else if (value > 180) {
    formData.longitude = 180
  }
}

const nextStep = () => {
  // Сохраняем текущие данные перед переходом на следующий шаг
  if (currentStep.value === 2) {
    // Сохраняем данные о зданиях, если мы находимся на шаге 2
    // Это уже происходит в вашем коде, но можно добавить дополнительную логику
    // для сохранения изображений и времени работы
  }

  if (currentStep.value === 2 && selectedBuildings.value.length > 0) {
    // Инициализируем здания с выбранными корпусами
    formData.buildings = selectedBuildings.value.map((name) => {
      // Проверяем, существует ли уже здание с таким именем
      const existingBuilding = formData.buildings.find((b) => b.name === name)
      if (existingBuilding) {
        // Если здание уже существует, возвращаем его
        return existingBuilding
      }
      // Иначе создаем новое здание
      return {
        name,
        floors: [{ number: null, floorPlan: null }],
        workingHours: createDefaultWorkingHours(),
        buildingImage: null,
      }
    })

    // Устанавливаем первый корпус как текущий
    currentBuilding.value = selectedBuildings.value[0]
  }

  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const addBuilding = () => {
  if (
    newBuildingName.value.trim() &&
    !selectedBuildings.value.includes(newBuildingName.value.trim())
  ) {
    formData.buildings.push({
      name: newBuildingName.value.trim(),
      floors: [{ number: null, floorPlan: null }],
      buildingImage: null, // Инициализируем как null
      workingHours: [
        { openTime: '09:00', closeTime: '18:00', isDayOff: false }, // Понедельник
        { openTime: '09:00', closeTime: '18:00', isDayOff: false }, // Вторник
        { openTime: '09:00', closeTime: '18:00', isDayOff: false }, // Среда
        { openTime: '09:00', closeTime: '18:00', isDayOff: false }, // Четверг
        { openTime: '09:00', closeTime: '18:00', isDayOff: false }, // Пятница
        { openTime: '09:00', closeTime: '18:00', isDayOff: true }, // Суббота
        { openTime: '09:00', closeTime: '18:00', isDayOff: true }, // Воскресенье
      ],
    })
    selectedBuildings.value.push(newBuildingName.value.trim())
    currentBuilding.value = newBuildingName.value.trim()
    newBuildingName.value = ''
  }
}

const removeBuilding = (building: string) => {
  const index = selectedBuildings.value.indexOf(building)
  if (index !== -1) {
    selectedBuildings.value.splice(index, 1)
  }
}

const switchBuilding = (buildingName: string) => {
  currentBuilding.value = buildingName
}

const getCurrentBuildingIndex = computed(() => {
  if (!currentBuilding.value) return -1
  return formData.buildings.findIndex((b) => b.name === currentBuilding.value)
})

const getCurrentBuilding = computed(() => {
  const index = getCurrentBuildingIndex.value
  return index !== -1 ? formData.buildings[index] : null
})

const addFloor = () => {
  const index = getCurrentBuildingIndex.value
  if (index !== -1) {
    formData.buildings[index].floors.push({ number: null, floorPlan: null })
  }
}

const removeFloor = (floorIndex: number) => {
  const buildingIndex = getCurrentBuildingIndex.value
  if (buildingIndex !== -1 && floorIndex > 0) {
    formData.buildings[buildingIndex].floors.splice(floorIndex, 1)
  }
}

const handleFloorPlanUpload = (event: Event, floorIndex: number) => {
  const input = event.target as HTMLInputElement
  const buildingIndex = getCurrentBuildingIndex.value

  if (input.files && input.files.length > 0 && buildingIndex !== -1) {
    formData.buildings[buildingIndex].floors[floorIndex].floorPlan = input.files[0]
  }
}

const getFileName = (file: File | null): string => {
  if (!file) return 'Нет файла'
  return file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name
}

const isFormValid = computed(() => {
  return (
    formData.buildings.every(
      (building) =>
        building.buildingImage !== null && // Проверяем наличие изображения здания
        building.floors.every((floor) => floor.number !== null && floor.floorPlan !== null),
    ) &&
    formData.latitude !== null &&
    formData.longitude !== null
  )
})

// Функция для отправки данных об адресе
const sendAddressData = async () => {
  try {
    const token: any = localStorage.getItem('token')
    const response = await axios.post(
      '/api/addresses/add',
      {
        name: formData.address,
        lon: formData.longitude,
        lat: formData.latitude,
      },
      {
        headers: {
          Authorization: `${token}`,
        },
      },
      
    )

    console.log('Address created:', response.data)
    addressId.value = response.data.uuid
    return response.data.uuid
  } catch (error) {
    console.error('Error creating address:', error)
    throw error
  }
}

const submitForm = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    // Шаг 1: Отправляем данные об адресе, если они еще не отправлены
    if (!addressId.value) {
      const addrId = await sendAddressData()
      addressId.value = addrId
    }

    // Шаг 3: Отправляем данные об этажах для текущего здания
    const currentBuildingData = formData.buildings.find((b) => b.name === currentBuilding.value)

    if (currentBuildingData) {
      // Получаем ID здания, если он еще не был получен
      let buildingId

      // Если мы уже загрузили здание на шаге 2, то используем его ID
      // Иначе загружаем здание сейчас
      if (!currentBuildingData.buildingId) {
        buildingId = await uploadBuildingData()
        // Сохраняем ID здания для возможного использования в будущем
        currentBuildingData.buildingId = buildingId
      } else {
        buildingId = currentBuildingData.buildingId
      }

      // Загружаем этажи для этого здания
    }

    // Можно добавить редирект или другие действия после успешного добавления
  } catch (error) {
    console.error('Error submitting form:', error)
    alert('Произошла ошибка при добавлении коворкинга. Пожалуйста, попробуйте снова.')
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  currentStep.value = 1
  formData.address = ''
  formData.latitude = null
  formData.longitude = null
  formData.buildings = []
  selectedBuildings.value = []
  currentBuilding.value = null
  addressId.value = null
  newBuildingName.value = ''
}
</script>

<template>
  <div class="new-coworking-container">
    <h1>Добавление нового коворкинга</h1>

    <div class="step-indicator">
      <div
        v-for="step in totalSteps"
        :key="step"
        class="step"
        :class="{ active: step === currentStep, completed: step < currentStep }"
      >
        {{ step }}
      </div>
    </div>

    <form @submit.prevent="submitForm" class="coworking-form">
      <!-- Step 1: Address -->
      <div v-if="currentStep === 1" class="form-step">
        <h2>Шаг 1: Укажите адрес</h2>
        <div class="form-group">
          <label for="address">Адрес</label>
          <input
            id="address"
            v-model="formData.address"
            type="text"
            placeholder="Введите адрес (например: Москва, Красная площадь)"
            class="form-control"
            required
          />
        </div>
        <div class="coordinates-container">
          <div class="form-group">
            <label for="latitude">Широта</label>
            <input
              id="latitude"
              v-model.number="formData.latitude"
              type="number"
              step="0.000001"
              min="0"
              max="90"
              placeholder="Введите широту (например: 55.7558)"
              class="form-control"
              required
              @input="validateLatitude"
            />
          </div>
          <div class="form-group">
            <label for="longitude">Долгота</label>
            <input
              id="longitude"
              v-model.number="formData.longitude"
              type="number"
              step="0.000001"
              min="0"
              max="180"
              placeholder="Введите долготу (например: 37.6173)"
              class="form-control"
              required
              @input="validateLongitude"
            />
          </div>
        </div>
        <div class="form-actions">
          <button
            type="button"
            @click="nextStep"
            class="next-btn"
            :disabled="
              !formData.address || formData.latitude === null || formData.longitude === null
            "
          >
            Далее
          </button>
        </div>
      </div>

      <!-- Step 2: Buildings -->
      <div v-if="currentStep === 2" class="form-step">
        <div class="selected-info">
          <p><strong>Выбранный адрес:</strong> {{ formData.address }}</p>
          <p><strong>Координаты:</strong> {{ formData.latitude }}, {{ formData.longitude }}</p>
        </div>

        <div class="form-group">
          <label for="building-name">Название здания/корпуса:</label>
          <div class="building-input-container">
            <input
              type="text"
              id="building-name"
              v-model="newBuildingName"
              class="form-control"
              placeholder="Введите название здания или корпуса"
            />
            <button type="button" @click="addBuilding" class="add-building-btn">Добавить</button>
          </div>
        </div>

        <div v-if="selectedBuildings.length > 0" class="selected-buildings">
          <div class="building-tabs">
            <button
              v-for="building in selectedBuildings"
              :key="building"
              @click="currentBuilding = building"
              class="building-tab"
              :class="{ active: currentBuilding === building }"
            >
              {{ building }}
            </button>
          </div>

          <div class="form-group">
            <label for="buildingImage">Изображение здания</label>
            <input
              type="file"
              id="buildingImage"
              accept="image/*"
              @change="handleBuildingImageUpload"
              class="form-control"
            />
            <div v-if="getCurrentBuilding && getCurrentBuilding.buildingImage" class="file-name">
              {{ getFileName(getCurrentBuilding.buildingImage) }}
            </div>
          </div>

          <div v-if="currentBuilding" class="building-details">
            <div class="form-group">
              <label>Время работы здания:</label>
              <div class="working-hours-container">
                <table class="working-hours-table">
                  <thead>
                    <tr>
                      <th>День недели</th>
                      <th>Открытие</th>
                      <th>Закрытие</th>
                      <th>Выходной</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(day, index) in weekDays" :key="day">
                      <td>{{ day }}</td>
                      <td>
                        <input
                          type="time"
                          v-model="getCurrentBuildingData().workingHours[index].openTime"
                          class="form-control time-input"
                          :disabled="getCurrentBuildingData().workingHours[index].isDayOff"
                        />
                      </td>
                      <td>
                        <input
                          type="time"
                          v-model="getCurrentBuildingData().workingHours[index].closeTime"
                          class="form-control time-input"
                          :disabled="getCurrentBuildingData().workingHours[index].isDayOff"
                        />
                      </td>
                      <td>
                        <input
                          type="checkbox"
                          v-model="getCurrentBuildingData().workingHours[index].isDayOff"
                          class="day-off-checkbox"
                        />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="selectedBuildings.length > 0" class="selected-buildings">
              <h4>Добавленные корпуса:</h4>
              <div
                v-for="building in selectedBuildings"
                :key="building"
                class="selected-building-item"
              >
                <span>{{ building }}</span>
                <button type="button" @click="removeBuilding(building)" class="remove-building-btn">
                  ✕
                </button>
              </div>
            </div>
            <div v-else class="no-buildings-message">
              <p>Добавьте хотя бы один корпус</p>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="prevStep" class="prev-btn">Назад</button>
            <button
              type="button"
              @click="nextStep"
              class="next-btn"
              :disabled="selectedBuildings.length === 0"
            >
              Далее
            </button>
          </div>
        </div>
      </div>

      <!-- Step 3: Floors -->
      <div v-if="currentStep === 3" class="form-step">
        <h2>Шаг 3: Укажите этажи для каждого корпуса</h2>
        <div class="selected-info">
          <div><strong>Адрес:</strong> {{ formData.address }}</div>
          <div><strong>Добавленные корпуса:</strong> {{ selectedBuildings.join(', ') }}</div>
        </div>

        <!-- Tabs for buildings -->
        <div class="building-tabs">
          <button
            v-for="building in formData.buildings"
            :key="building.name"
            type="button"
            class="building-tab"
            :class="{ active: currentBuilding === building.name }"
            @click="switchBuilding(building.name)"
          >
            {{ building.name }}
          </button>
        </div>

        <!-- Current building floors -->
        <div v-if="getCurrentBuilding" class="floors-container">
          <h3>Этажи для {{ currentBuilding }}</h3>
          <div v-for="(floor, index) in getCurrentBuilding.floors" :key="index" class="floor-item">
            <div class="form-group">
              <label :for="`floor-${index}`">Этаж</label>
              <div class="floor-input-group">
                <input
                  :id="`floor-${index}`"
                  v-model.number="floor.number"
                  type="number"
                  min="1"
                  placeholder="Номер этажа *"
                  class="form-control"
                  required
                />
                <div class="floor-plan-upload" :class="{ 'file-missing': !floor.floorPlan }">
                  <input
                    type="file"
                    :id="`floor-plan-${currentBuilding}-${index}`"
                    @change="(e) => handleFloorPlanUpload(e, index)"
                    accept="image/*,.pdf"
                    class="floor-plan-input"
                    hidden
                    required
                  />
                  <label :for="`floor-plan-${currentBuilding}-${index}`" class="floor-plan-btn">
                    <span class="upload-icon">📄</span>
                    <span class="upload-text">{{
                      floor.floorPlan ? getFileName(floor.floorPlan) : 'План этажа *'
                    }}</span>
                  </label>
                </div>
                <button
                  type="button"
                  @click="removeFloor(index)"
                  class="remove-floor-btn"
                  v-if="index > 0"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
          <button type="button" @click="addFloor" class="add-floor-btn">+ Добавить этаж</button>
        </div>

        <div class="form-actions">
          <button type="button" @click="prevStep" class="prev-btn">Назад</button>
          <button
            @click="submitForm"
            :disabled="!isFormValid || isSubmitting"
            class="btn btn-primary"
          >
            {{ isSubmitting ? 'Добавление...' : 'Добавить коворкинг' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<style lang="scss" scoped>
.working-hours-container {
  margin-top: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
}

.working-hours-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f2f2f2;
  }

  .time-input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 100%;
  }

  .day-off-checkbox {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
}

.new-coworking-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;

  h1 {
    margin-bottom: 20px;
    text-align: center;
  }

  h2 {
    margin-bottom: 15px;
    font-size: 1.2rem;
  }
}

.step-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;

  .step {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #f0f0f0;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 10px;
    font-weight: bold;
    position: relative;

    &:not(:last-child)::after {
      content: '';
      position: absolute;
      width: 30px;
      height: 2px;
      background-color: #f0f0f0;
      right: -30px;
      top: 50%;
      transform: translateY(-50%);
    }

    &.active {
      background-color: #4a90e2;
      color: white;
    }

    &.completed {
      background-color: #4caf50;
      color: white;

      &::after {
        background-color: #4caf50;
      }
    }
  }
}

.coworking-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-step {
  animation: fadeIn 0.3s ease-in-out;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;

  label {
    font-weight: bold;
  }

  .form-control {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
  }
}

.coordinates-container {
  display: flex;
  gap: 15px;

  .form-group {
    flex: 1;
  }
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;

  button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.2s;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .prev-btn {
    background-color: #f0f0f0;
    color: #333;

    &:hover:not(:disabled) {
      background-color: #e0e0e0;
    }
  }

  .next-btn,
  .submit-btn {
    background-color: #4a90e2;
    color: white;

    &:hover:not(:disabled) {
      background-color: #3a80d2;
    }
  }
}

.selected-address,
.selected-info {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  border-left: 3px solid #4a90e2;
}

.building-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 5px;

  .building-option {
    padding: 10px 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #4a90e2;
    }

    &.selected {
      background-color: #4a90e2;
      color: white;
      border-color: #4a90e2;
    }
  }
}

.building-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 5px;

  .building-tab {
    padding: 8px 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    background-color: #f0f0f0;
    white-space: nowrap;

    &.active {
      background-color: #4a90e2;
      color: white;
      border-color: #4a90e2;
    }
  }
}

.floors-container {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;

  h3 {
    margin-bottom: 15px;
    font-size: 1.1rem;
  }
}

.floor-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;

  &:last-child {
    border-bottom: none;
  }
}

.floor-input-group {
  display: flex;
  gap: 10px;
  align-items: center;

  .form-control {
    flex: 1;
  }

  .floor-plan-upload {
    flex: 2;

    .floor-plan-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
      cursor: pointer;
      background-color: #fff;
      width: 100%;

      .upload-icon {
        font-size: 1.2rem;
      }

      .upload-text {
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    &.file-missing .floor-plan-btn {
      border-color: #ff6b6b;
      color: #ff6b6b;
    }
  }

  .remove-floor-btn {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: none;
    background-color: #ff6b6b;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;

    &:hover {
      background-color: #ff5252;
    }
  }
}

.add-floor-btn {
  width: 100%;
  padding: 10px;
  border: 1px dashed #4a90e2;
  border-radius: 4px;
  background-color: transparent;
  color: #4a90e2;
  cursor: pointer;
  margin-top: 10px;
  font-weight: bold;

  &:hover {
    background-color: rgba(74, 144, 226, 0.1);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.new-coworking-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.step-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.step {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 10px;
  font-weight: bold;
}

.step.active {
  background-color: #4caf50;
  color: white;
}

.step.completed {
  background-color: #8bc34a;
  color: white;
}

.form-step {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.coordinates-container {
  display: flex;
  gap: 20px;
}

.coordinates-container .form-group {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.next-btn,
.prev-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.next-btn,
.submit-btn {
  background-color: #4caf50;
  color: white;
}

.next-btn:disabled,
.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.prev-btn {
  background-color: #f0f0f0;
}

.selected-address,
.selected-info {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.building-input-container {
  display: flex;
  margin-bottom: 10px;
}

.building-input-container input {
  flex: 1;
  margin-right: 10px;
}

.add-building-btn {
  padding: 10px 15px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.selected-buildings {
  margin-top: 15px;
}

.selected-building-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #e3f2fd;
  border-radius: 4px;
  margin-bottom: 5px;
}

.remove-building-btn {
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  font-size: 18px;
}

.building-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.building-tab {
  padding: 8px 15px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.building-tab.active {
  background-color: #2196f3;
  color: white;
}

.floors-container {
  margin-top: 20px;
}

.floor-item {
  margin-bottom: 15px;
}

.floor-input-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.floor-input-group input {
  flex: 0 0 100px;
}

.floor-plan-upload {
  flex: 1;
}

.floor-plan-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border: 1px dashed #aaa;
  border-radius: 4px;
  cursor: pointer;
}

.file-missing .floor-plan-btn {
  border-color: #f44336;
}

.upload-icon {
  font-size: 20px;
}

.remove-floor-btn {
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  font-size: 18px;
}

.add-floor-btn {
  padding: 8px 15px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.final-actions {
  margin-top: 30px;
}
</style>
