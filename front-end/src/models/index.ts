export interface User {
  role: string
  login: string
  name: string
  surname: string
  secondname: string
  email: string
  contacts: string
}

export interface AddressInfo {
  id: string
  lat: number
  lon: number
  name: string
}

export interface BuildingInfo {
  address_id: string
  id: string
  img: string
  name: string
  t_from: any
  t_to: any
}

export interface FloorInfo {
  building_id: string
  id: string
  img: string
  number: number
}

export interface SeatsInfo {
  id: string
  posx: number
  posy: number
  name: string
  price: number
  status: string
  collisions: any
}

export interface TimeInfo {
  hour: string
  minute: string
  tz?: string
}

export interface BookingTime {
  date: string
  dayOfWeek: string
  timeFrom: TimeInfo
  timeTo: TimeInfo
}

export interface FoodItem {
  id: string
  name: string
  price: number
  image: string
  quantity: number
  active: boolean
}

export interface EquipmentItem {
  id: string
  name: string
  price: number
  image: string
  quantity: number
  active: boolean
}
