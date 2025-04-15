<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

// Определение интерфейсов для типизации данных
interface Address {
  id: string | number;
  name: string;
  lat: number;
  lon: number;
}

interface Building {
  id: string | number;
  name: string;
  img?: string;
  t_from: number; // Время начала работы в часах
  t_to: number;   // Время окончания работы в часах
  d_from: number; // День недели начала работы (0-6)
  d_to: number;   // День недели окончания работы (0-6)
  address_id: string | number;
}

interface Floor {
  id: string | number;
  number: number;
  img?: string;
  building_id: string | number;
}

// Массив дней недели для отображения
const daysOfWeek = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

// Типизированные ref
const addresses = ref<Address[]>([]);
const buildingsByAddress = ref<Record<string | number, Building[]>>({});
const loading = ref<boolean>(true);
const error = ref<string | null>(null);

// Для модального окна
const showModal = ref<boolean>(false);
const selectedBuilding = ref<Building | null>(null);
const buildingFloors = ref<Floor[]>([]);
const loadingFloors = ref<boolean>(false);

// Функция для форматирования времени работы
const formatWorkingHours = (building: Building): string => {
  // Проверяем наличие всех необходимых данных
  if (building.d_from === undefined || building.d_to === undefined ||
    building.t_from === undefined || building.t_to === undefined) {
    return 'Часы работы неизвестны';
  }

  // Получаем названия дней недели
  const dayFrom = daysOfWeek[building.d_from];
  const dayTo = daysOfWeek[building.d_to];

  // Проверяем, что индексы дней недели корректны
  if (!dayFrom || !dayTo) {
    return 'Часы работы неизвестны';
  }

  // Форматируем время в часах
  return `${dayFrom}-${dayTo} с ${building.t_from}:00 до ${building.t_to}:00`;
};

// Получение URL изображения здания
const getBuildingImageUrl = (imageName: string | undefined): string => {
  if (!imageName) return '';
  return `/api/buildings/image/${imageName}`;
};

// Получение URL изображения этажа
const getFloorImageUrl = (imageName: string | undefined): string => {
  if (!imageName) return '';
  return `/api/floors/image/${imageName}`;
};

// Fetch all addresses
const fetchAddresses = async (): Promise<Address[]> => {
  try {
    const response = await axios.get<Address[]>('/api/addresses/all');
    addresses.value = response.data;
    return response.data;
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
    error.value = 'Ошибка при загрузке адресов: ' + errorMessage;
    console.error('Error fetching addresses:', err);
    return [];
  }
};


const deleteAddress = async (addressId: string | number, event: Event): Promise<void> => {
  event.stopPropagation(); // Предотвращаем всплытие события

  if (confirm('Вы уверены, что хотите удалить этот адрес? Все связанные здания также будут удалены.')) {
    try {
      const token: any = localStorage.getItem('token')
      await axios.delete(`/api/addresses/${addressId}`, {
          headers: {
             Authorization: `${token}`
          },
        });

      // Удаляем адрес из локального состояния
      addresses.value = addresses.value.filter(address => address.id !== addressId);

      // Удаляем связанные здания из локального состояния
      delete buildingsByAddress.value[addressId];

    } catch (err: unknown) {
      console.error(`Error deleting address ${addressId}:`, err);
      alert('Произошла ошибка при удалении адреса');
    }
  }
};

// Fetch buildings for a specific address
const fetchBuildingsByAddress = async (addressId: string | number): Promise<void> => {
  try {
    const response = await axios.get<Building[]>(`/api/buildings/by-address/${addressId}`);
    buildingsByAddress.value[addressId] = response.data;

    // Сохраняем address_id для каждого здания
    buildingsByAddress.value[addressId].forEach(building => {
      building.address_id = addressId;
    });
  } catch (err: unknown) {
    console.error(`Error fetching buildings for address ${addressId}:`, err);
    buildingsByAddress.value[addressId] = [];
  }
};



// Fetch floors for a specific building
const fetchFloorsByBuilding = async (buildingId: string | number): Promise<void> => {
  loadingFloors.value = true;
  try {
    const response = await axios.get<Floor[]>(`/api/floors/by-building/${buildingId}`);
    buildingFloors.value = response.data;
  } catch (err: unknown) {
    console.error(`Error fetching floors for building ${buildingId}:`, err);
    buildingFloors.value = [];
  } finally {
    loadingFloors.value = false;
  }
};

// Load all data
const loadData = async (): Promise<void> => {
  loading.value = true;
  error.value = null;

  try {
    const addressesData = await fetchAddresses();

    // Fetch buildings for each address
    const promises = addressesData.map((address: Address) => fetchBuildingsByAddress(address.id));
    await Promise.all(promises);

  } catch (err: unknown) {
    error.value = 'Произошла ошибка при загрузке данных';
    console.error('Error loading data:', err);
  } finally {
    loading.value = false;
  }
};

// Открыть модальное окно с подробной информацией о здании
const openBuildingDetails = async (building: Building): Promise<void> => {
  selectedBuilding.value = building;
  showModal.value = true;
  await fetchFloorsByBuilding(building.id);
};

// Закрыть модальное окно
const closeModal = (): void => {
  showModal.value = false;
  selectedBuilding.value = null;
  buildingFloors.value = [];
};

onMounted(() => {
  loadData();
});

const deleteBuilding = async (buildingId: string | number, event: Event): Promise<void> => {
  event.stopPropagation(); // Предотвращаем всплытие события

  if (confirm('Вы уверены, что хотите удалить это здание?')) {
    try {
      // Находим здание, чтобы получить его address_id перед удалением
      let addressId = null;
      for (const [addrId, buildings] of Object.entries(buildingsByAddress.value)) {
        const building = buildings.find(b => b.id === buildingId);
        if (building) {
          addressId = building.address_id;
          break;
        }
      }
    const token: any = localStorage.getItem('token')
      await axios.delete(`/api/buildings/${buildingId}`, {
          headers: {
             Authorization: `${token}`
          },
        });

      // Если нашли addressId, обновляем только здания для этого адреса
      if (addressId) {
        await fetchBuildingsByAddress(addressId);
      } else {
        // Если не нашли addressId, обновляем все данные
        await loadData();
      }
    } catch (err) {
      console.error('Ошибка при удалении здания:', err);
      alert('Не удалось удалить здание. Пожалуйста, попробуйте снова.');
    }
  }
};

const deleteFloor = async (floorId: string | number, event: Event): Promise<void> => {
  event.stopPropagation(); // Предотвращаем всплытие события

  if (confirm('Вы уверены, что хотите удалить этот этаж?')) {
    try {
      const token: any = localStorage.getItem('token')
      await axios.delete(`/api/floors/delete/${floorId}`,{
          headers: {
             Authorization: `${token}`
          },
        });

      // Обновляем список этажей для текущего здания
      if (selectedBuilding.value) {
        await fetchFloorsByBuilding(selectedBuilding.value.id);
      }

    } catch (err: unknown) {
      console.error(`Error deleting floor ${floorId}:`, err);
      alert('Произошла ошибка при удалении этажа');
    }
  }
};


</script>

<template>
  <div class="dashboard">
    <h1 class="dashboard-title">Доступные здания</h1>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-button">Попробовать снова</button>
    </div>

    <div v-else class="addresses-container">
      <div v-for="address in addresses" :key="address.id" class="address-section">
        <div class="address-header">
          <h2 class="address-name">{{ address.name }}</h2>
          <button @click="deleteAddress(address.id, $event)" class="delete-button">
            <span class="delete-icon">×</span>
          </button>
        </div>

        <div class="buildings-grid">
          <div
            v-for="building in buildingsByAddress[address.id] || []"
            :key="building.id"
            class="building-card"
          >
            <div class="building-image-container">
              <img
                v-if="building.img"
                :src="getBuildingImageUrl(building.img)"
                :alt="building.name"
                class="building-image"
              >
              <div v-else class="building-image-placeholder">
                Нет изображения
              </div>
            </div>

            <div class="building-info">
              <h3 class="building-name">{{ building.name }}</h3>
              <div class="building-actions">
                <button @click="openBuildingDetails(building)" class="view-details-button">Подробнее</button>
                <button @click="deleteBuilding(building.id, $event)" class="delete-button">
                  <span class="delete-icon">×</span>
                </button>
              </div>
            </div>
          </div>

          <div v-if="(buildingsByAddress[address.id]?.length || 0) === 0" class="no-buildings">
            Нет доступных зданий по этому адресу
          </div>
        </div>
      </div>

      <div v-if="addresses.length === 0" class="no-addresses">
        Нет доступных адресов
      </div>
    </div>

    <!-- Модальное окно с подробной информацией о здании -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeModal">&times;</button>

        <div v-if="selectedBuilding" class="building-details">
          <h2 class="modal-title">{{ selectedBuilding.name }}</h2>

          <div class="building-image-container modal-image">
            <img
              v-if="selectedBuilding.img"
              :src="getBuildingImageUrl(selectedBuilding.img)"
              :alt="selectedBuilding.name"
              class="building-image"
            >
            <div v-else class="building-image-placeholder">
              Нет изображения
            </div>
          </div>

          <div class="building-details-info">
            <h3>Время работы:</h3>
            <p>{{ formatWorkingHours(selectedBuilding) }}</p>

            <h3>Этажи:</h3>
            <div v-if="loadingFloors" class="loading-container">
              <div class="loading-spinner"></div>
              <p>Загрузка этажей...</p>
            </div>

            <div v-else-if="buildingFloors.length === 0" class="no-floors">
              Нет доступных этажей для этого здания
            </div>

            <div v-else class="floors-grid">
              <div v-for="floor in buildingFloors" :key="floor.id" class="floor-card">
                <div class="floor-header">
                  <h4>Этаж {{ floor.number }}</h4>
                  <button @click="deleteFloor(floor.id, $event)" class="delete-button">
                    <span class="delete-icon">×</span>
                  </button>
                </div>
                <div class="floor-image-container">
                  <img
                    v-if="floor.img"
                    :src="getFloorImageUrl(floor.img)"
                    :alt="`Этаж ${floor.number}`"
                    class="floor-image"
                  >
                  <div v-else class="floor-image-placeholder">
                    Нет изображения этажа
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-title {
  font-size: 28px;
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 30px;
  background-color: #fff3f3;
  border-radius: 8px;
  color: #e74c3c;
}

.retry-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #2980b9;
}

.addresses-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.address-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.address-name {
  font-size: 22px;
  margin-bottom: 5px;
  color: #2c3e50;
}

.address-coordinates {
  color: #7f8c8d;
  margin-bottom: 20px;
  font-size: 14px;
}

.buildings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.building-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.building-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.building-image-container {
  height: 180px;
  overflow: hidden;
  background-color: #eee;
}

.building-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.building-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #95a5a6;
  font-style: italic;
}

.building-info {
  padding: 15px;
}

.building-name {
  font-size: 18px;
  margin-bottom: 8px;
  color: #34495e;
}

.building-hours {
  color: #7f8c8d;
  font-size: 14px;
  margin-bottom: 15px;
}

.view-details-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.3s;
}

.view-details-button:hover {
  background-color: #2980b9;
}

.no-buildings, .no-addresses {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
  background-color: #f5f5f5;
  border-radius: 8px;
  font-style: italic;
}

/* Стили для модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 25px;
  position: relative;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
  transition: color 0.3s;
}

.modal-close:hover {
  color: #e74c3c;
}

.modal-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #2c3e50;
  padding-right: 30px;
}

.modal-image {
  height: 250px;
  margin-bottom: 20px;
  border-radius: 6px;
}

.building-details-info {
  margin-top: 20px;
}

.building-details-info h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #34495e;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.building-details-info p {
  margin-bottom: 20px;
  color: #555;
}

.floors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.floor-card {
  background-color: #f9f9f9;
  border-radius: 6px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.floor-card h4 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #2c3e50;
  text-align: center;
}

.floor-image-container {
  height: 150px;
  overflow: hidden;
  background-color: #eee;
  border-radius: 4px;
}

.floor-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.floor-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 10px;
}

.no-floors {
  text-align: center;
  padding: 20px;
  color: #7f8c8d;
  background-color: #f5f5f5;
  border-radius: 6px;
  font-style: italic;
  margin-top: 10px;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    padding: 15px;
  }

  .floors-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .floor-image-container {
    height: 120px;
  }

  .modal-image {
    height: 200px;
  }
}


.floor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.floor-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.floor-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.floor-card .delete-button {
  width: 24px;
  height: 24px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.floor-card .delete-button:hover {
  background-color: #ff7875;
}
</style>
