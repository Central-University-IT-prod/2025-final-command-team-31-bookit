import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import type {
  SeatsInfo,
  BookingTime,
  FoodItem,
  EquipmentItem,
  AddressInfo,
  BuildingInfo,
  FloorInfo,
} from '@/models'

export const useBookingStore = defineStore('booking', () => {
  const currentStep = ref(0)
  const selectedAddress = ref('')
  const selectedBuilding = ref('')
  const selectedFloor = ref('')
  const selectedSeat = ref('')
  const bookingTimes = ref<BookingTime[]>([])
  const comment = ref('')
  const selectedFood = ref<FoodItem[]>([])
  const selectedEquipment = ref<EquipmentItem[]>([])

  const tFrom = ref()
  const tTo = ref()
  const address = ref('')
  const floorId = ref('')

  const addressInfo = ref<AddressInfo[]>([])
  const buildingInfo = ref<BuildingInfo[]>([])
  const floorInfo = ref<FloorInfo[]>([])
  const seatsInfo = ref({
    seats: {} as SeatsInfo,
  })

  function setCurrentStep(step: number) {
    currentStep.value = step
  }

  function setSelectedAddress(address: string) {
    selectedAddress.value = address
  }

  function setSelectedBuilding(building: string, addressId: string) {
    selectedBuilding.value = building
    address.value = addressId
  }

  function setSelectedFloor(floor: string) {
    selectedFloor.value = floor
  }

  function setSelectedSeat(seat: string) {
    selectedSeat.value = seat
  }

  function setBookingTimes(times: BookingTime[]) {
    bookingTimes.value = times
  }

  function setComment(text: string) {
    comment.value = text
  }

  function setSelectedFood(food: FoodItem[]) {
    selectedFood.value = food
  }

  function setSelectedEquipment(equipment: EquipmentItem[]) {
    selectedEquipment.value = equipment
  }

  function setTime(t_from: number, t_to: number) {
    tFrom.value = t_from
    tTo.value = t_to
  }

  function calculateTotalPrice() {
    let total = 0

    // Calculate food price
    selectedFood.value.forEach((item) => {
      total += item.price * item.quantity
    })

    // Calculate equipment price (per hour)
    let totalHours = 0
    bookingTimes.value.forEach((booking) => {
      const fromHour = parseInt(booking.timeFrom.hour)
      const fromMinute = parseInt(booking.timeFrom.minute)
      const toHour = parseInt(booking.timeTo.hour)
      const toMinute = parseInt(booking.timeTo.minute)

      const hours = toHour - fromHour + (toMinute - fromMinute) / 60
      totalHours += hours
    })

    selectedEquipment.value.forEach((item) => {
      total += item.price * item.quantity * totalHours
    })

    return total
  }

  const testStuff = async () => {
    const token: any = localStorage.getItem('token')
    let id = 'ddcc2745-89fc-47cc-ba0c-b308185d023a'
    try {
      const response = await axios.post(
        `/api/testing_stuff`,
        {
          floor_id: id,
          times: [
            { t_from: 0, t_to: 0 },
            { t_from: 0, t_to: 0 },
          ],
        },
        {
          headers: {
            Authorization: `${token}`,
          },
        },
      )
      console.log(response.data)
    } catch (e) {
      throw e
    }
  }

  const getAllAdresses = async () => {
    try {
      const response = await axios.get(`/api/addresses/all`)
      const data = response.data
      addressInfo.value = data
    } catch (e) {
      throw e
    }
  }

  const getBuildings = async (address_id: string, floor_id?: string) => {
    try {
      floorId.value = floor_id
      const response = await axios.get(`/api/buildings/by-address/${address_id}`)
      const data = response.data
      console.log(response.data)
      buildingInfo.value = data
    } catch (e) {
      throw e
    }
  }

  const getFloor = async (building_id: string, address_id: string) => {
    try {
      address.value = address_id
      const response = await axios.get(`/api/floors/by-building/${building_id}`)
      const data = response.data
      floorInfo.value = data
      console.log(floorInfo.value)
    } catch (e) {
      throw e
    }
  }

  const getSeats = async (floor_id: string, t_from: number, t_to: number) => {
    const token: any = localStorage.getItem('token')
    try {
      const response = await axios.post(
        `/api/booking/get_seats`,
        {
          floor_id: floor_id,
          times: [{ t_from: t_from, t_to: t_to }],
        },
        {
          headers: {
            Authorization: `${token}`,
          },
        },
      )
      console.log(response.data)
      seatsInfo.value = {
        seats: response.data,
      }
    } catch (e) {
      throw e
    }
  }

  const bookOne = async (
    floor_id: string,
    seat_id: string,
    times: any,
    items?: any,
    comment?: string,
  ) => {
    try {
      const token: any = localStorage.getItem('token')
      const getCircularReplacer = () => {
        const seen = new WeakSet()
        return (key: string, value: any) => {
          if (typeof value === 'object' && value !== null) {
            if (seen.has(value)) {
              return
            }
            seen.add(value)
          }
          return value
        }
      }
      const response = await axios.post(
        `/api/booking/book_one`,
        {
          floor_id: floor_id,
          seat_id: seat_id,
          times: JSON.parse(JSON.stringify(times, getCircularReplacer())),
          items: JSON.parse(JSON.stringify(items, getCircularReplacer())),
          comment: comment,
        },
        {
          headers: {
            Authorization: `${token}`,
          },
        },
      )
      const data = response.data
      console.log('Data:', data)
    } catch (e) {
      console.log(e)
      throw e
    }
  }

  return {
    currentStep,
    selectedAddress,
    selectedBuilding,
    selectedFloor,
    selectedSeat,
    bookingTimes,
    comment,
    tFrom,
    tTo,
    floorId,
    address,
    addressInfo,
    buildingInfo,
    floorInfo,
    selectedFood,
    selectedEquipment,
    setCurrentStep,
    setSelectedAddress,
    setSelectedBuilding,
    setSelectedFloor,
    setSelectedSeat,
    setBookingTimes,
    setComment,
    setSelectedFood,
    setSelectedEquipment,
    setTime,
    calculateTotalPrice,
    getSeats,
    testStuff,
    getAllAdresses,
    getBuildings,
    getFloor,
    bookOne,
  }
})
