<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBookingStore } from '../../stores/booking'

const store = useBookingStore()
const buildings = computed(() => store.buildingInfo)
const floor = computed(() => store.floorId)

const days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

interface Booking {
  day: string
  month: string
  year: string
  dayOfWeek: string
  timeFrom: { hour: string; minute: string }
  timeTo: { hour: string; minute: string }
}

const bookings = ref<Booking[]>([
  {
    day: '03',
    month: '03',
    year: '2025',
    dayOfWeek: 'ПН',
    timeFrom: { hour: '07', minute: '00' },
    timeTo: { hour: '23', minute: '00' },
  },
])

const updateDayOfWeek = (index: number) => {
  const booking = bookings.value[index]
  const date = new Date(`${booking.year}-${booking.month}-${booking.day}`)
  const dayIndex = date.getDay()

  const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1

  booking.dayOfWeek = days[adjustedDayIndex]

  validateTimeRange(index)
}

const getAvailableHours = (bookingIndex: number, type: 'from' | 'to') => {
  const booking = bookings.value[bookingIndex]
  const date = new Date(`${booking.year}-${booking.month}-${booking.day}`)
  const dayIndex = date.getDay()
  const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1

  const building = buildings.value[0]

  if (!building) return []

  const openingMinutes = building.t_from[adjustedDayIndex]
  const closingMinutes = building.t_to[adjustedDayIndex]

  if (openingMinutes === 0 || closingMinutes === 0) {
    return []
  }

  const openingHour = Math.floor(openingMinutes / 60)
  const closingHour = Math.floor(closingMinutes / 60)

  const hours = []

  if (type === 'from') {
    for (let h = openingHour; h < closingHour; h++) {
      hours.push(h < 10 ? `0${h}` : `${h}`)
    }
  } else {
    const fromHour = parseInt(booking.timeFrom.hour)
    const startHour = Math.max(openingHour + 1, fromHour + 1)

    for (let h = startHour; h <= closingHour; h++) {
      hours.push(h < 10 ? `0${h}` : `${h}`)
    }
  }

  return hours
}

const validateTimeRange = (index: number) => {
  const booking = bookings.value[index]
  const date = new Date(`${booking.year}-${booking.month}-${booking.day}`)
  const dayIndex = date.getDay()
  const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1
  
  const building = buildings.value[0]
  
  if (!building) return
  
  const openingMinutes = building.t_from[adjustedDayIndex]
  const closingMinutes = building.t_to[adjustedDayIndex]
  
  if (openingMinutes === 0 || closingMinutes === 0) {
    booking.timeFrom = { hour: '00', minute: '00' }
    booking.timeTo = { hour: '00', minute: '00' }
    return
  }
  
  const openingHour = Math.floor(openingMinutes / 60)
  const closingHour = Math.floor(closingMinutes / 60)
  
  const fromHour = parseInt(booking.timeFrom.hour)
  if (isNaN(fromHour) || fromHour < openingHour || fromHour >= closingHour) {
    booking.timeFrom.hour = openingHour < 10 ? `0${openingHour}` : `${openingHour}`
  }
  
  const toHour = parseInt(booking.timeTo.hour)
  const minToHour = parseInt(booking.timeFrom.hour) + 1
  
  if (isNaN(toHour) || toHour <= fromHour || toHour > closingHour) {
    booking.timeTo.hour = Math.min(minToHour, closingHour) < 10 
      ? `0${Math.min(minToHour, closingHour)}` 
      : `${Math.min(minToHour, closingHour)}`
  }
}

const addDay = () => {
  const lastBooking = bookings.value[bookings.value.length - 1]

  const lastDate = new Date(`${lastBooking.year}-${lastBooking.month}-${lastBooking.day}`)
  lastDate.setDate(lastDate.getDate() + 1)

  const newDay = lastDate.getDate().toString().padStart(2, '0')
  const newMonth = (lastDate.getMonth() + 1).toString().padStart(2, '0')
  const newYear = lastDate.getFullYear().toString()

  const dayIndex = lastDate.getDay()
  const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1

  const newBooking = {
    day: newDay,
    month: newMonth,
    year: newYear,
    dayOfWeek: days[adjustedDayIndex],
    timeFrom: { hour: '07', minute: '00' },
    timeTo: { hour: '23', minute: '00' },
  }

  bookings.value.push(newBooking)

  validateTimeRange(bookings.value.length - 1)
}

const comment = ref('')
const suggestions = ['Приносите кофе 1 раз каждый день', 'Помогите подняться на этаж']

const deleteBooking = (index: number) => {
  bookings.value.splice(index, 1)
}

const addSuggestion = (suggestion: string) => {
  if (comment.value) {
    comment.value += '\n' + suggestion
  } else {
    comment.value = suggestion
  }
}

const continueToOptions = () => {
  const formattedBookings = bookings.value.map((booking) => {
    const dateStr = `${booking.day}.${booking.month}.${booking.year}`

    const date = new Date(`${booking.year}-${booking.month}-${booking.day}`)
    const dayIndex = date.getDay()
    const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1

    const building = buildings.value[0]
    const isDayOff =
      building && (building.t_from[adjustedDayIndex] === 0 || building.t_to[adjustedDayIndex] === 0)

    let startTimestamp = ref(0)
    let endTimestamp = ref(0)

    if (!isDayOff) {
      const startDate = new Date(
        `${booking.year}-${booking.month}-${booking.day}T${booking.timeFrom.hour}:${booking.timeFrom.minute}:00+03:00`,
      )
      const endDate = new Date(
        `${booking.year}-${booking.month}-${booking.day}T${booking.timeTo.hour}:${booking.timeTo.minute}:00+03:00`,
      )

      startTimestamp.value = startDate.getTime()
      endTimestamp.value = endDate.getTime()
    }

    return {
      date: dateStr,
      dayOfWeek: booking.dayOfWeek,
      timeFrom: isDayOff ? { hour: 'Выходной', minute: '' } : booking.timeFrom,
      timeTo: isDayOff ? { hour: 'Выходной', minute: '' } : booking.timeTo,
      startTimestamp,
      endTimestamp,
      isDayOff,
    }
  })
  let earliestStartTimestamp = Number.MAX_SAFE_INTEGER
  let latestEndTimestamp = 0
  
  formattedBookings.forEach(booking => {
    if (!booking.isDayOff) {
      if (booking.startTimestamp.value < earliestStartTimestamp) {
        earliestStartTimestamp = booking.startTimestamp.value
      }
      if (booking.endTimestamp.value > latestEndTimestamp) {
        latestEndTimestamp = booking.endTimestamp.value
      }
    }
  })
  
  if (earliestStartTimestamp === Number.MAX_SAFE_INTEGER) {
    earliestStartTimestamp = 0
  }
  console.log(earliestStartTimestamp, latestEndTimestamp);
  store.setTime(earliestStartTimestamp, latestEndTimestamp)
  store.getSeats(floor.value, earliestStartTimestamp, latestEndTimestamp)
  console.log(formattedBookings)
  store.setBookingTimes(formattedBookings)
  store.setComment(comment.value)
  store.setCurrentStep(4)
}

const isDayOff = (index: number) => {
  const booking = bookings.value[index]
  const date = new Date(`${booking.year}-${booking.month}-${booking.day}`)
  const dayIndex = date.getDay()
  const adjustedDayIndex = dayIndex === 0 ? 6 : dayIndex - 1

  const building = buildings.value[0]
  if (!building) return false

  return building.t_from[adjustedDayIndex] === 0 || building.t_to[adjustedDayIndex] === 0
}

const formatTime = (minutes: number): string => {
  if (minutes === 0) return 'Выходной'
  const hours = Math.floor(minutes / 60)
  return `${hours < 10 ? '0' : ''}${hours}:00`
}
</script>

<template>
  <div class="booking_part2_6 container">
    <h3>Расписание работы коворкинга:</h3>

    <table class="schedule-table" v-for="time in buildings" :key="time.id">
      <thead>
        <tr>
          <th></th>
          <th v-for="day in days" :key="day">{{ day }}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Открытие</td>
          <td
            v-for="(from, index) in time.t_from"
            :key="`from-${index}`"
            :class="{ 'day-off': from === 0 }"
          >
            <p class="time">
              {{ formatTime(from) }}
              <span v-if="from !== 0" class="tz">+3 UTC</span>
            </p>
          </td>
        </tr>
        <tr>
          <td>Закрытие</td>
          <td
            v-for="(to, index) in time.t_to"
            :key="`to-${index}`"
            :class="{ 'day-off': to === 0 }"
          >
            <p class="time">
              {{ formatTime(to) }}
              <span v-if="to !== 0" class="tz">+3 UTC</span>
            </p>
          </td>
        </tr>
      </tbody>
    </table>

    <h3>Бронирование:</h3>
    <table>
      <tr>
        <th>Дата</th>
        <th>Время с</th>
        <th>Время до</th>
        <th>Действия</th>
      </tr>
      <tr v-for="(booking, index) in bookings" :key="index">
        <td>
          <div class="dateselect">
            <select v-model="booking.day" @change="updateDayOfWeek(index)">
              <option value="03">03</option>
              <option value="04">04</option>
              <option value="05">05</option>
              <option value="06">06</option>
              <option value="07">07</option>
              <option value="08">08</option>
              <option value="09">09</option>
            </select>
            <p>.</p>
            <select v-model="booking.month" @change="updateDayOfWeek(index)">
              <option value="03">03</option>
            </select>
            <p>.</p>
            <select v-model="booking.year" @change="updateDayOfWeek(index)">
              <option value="2025">2025</option>
            </select>
            <span class="dayofweek">({{ booking.dayOfWeek }})</span>
          </div>
        </td>
        <td>
          <div class="dateselect">
            <div v-if="isDayOff(index)" class="day-off-text">Выходной</div>
            <div v-else class="timeselect">
              <select v-model="booking.timeFrom.hour" @change="validateTimeRange(index)">
                <option v-for="h in getAvailableHours(index, 'from')" :key="h" :value="h">
                  {{ h }}
                </option>
              </select>
              <p>:</p>
              <select v-model="booking.timeFrom.minute">
                <option value="00">00</option>
                <option value="30">30</option>
              </select>
              <span class="tz">+3 UTC</span>
            </div>
          </div>
        </td>
        <td>
          <div class="dateselect">
            <div v-if="isDayOff(index)" class="day-off-text">Выходной</div>
            <div v-else class="timeselect">
              <select v-model="booking.timeTo.hour" @change="validateTimeRange(index)">
                <option v-for="h in getAvailableHours(index, 'to')" :key="h" :value="h">
                  {{ h }}
                </option>
              </select>
              <p>:</p>
              <select v-model="booking.timeTo.minute">
                <option value="00">00</option>
                <option value="30">30</option>
              </select>
              <span class="tz">+3 UTC</span>
            </div>
          </div>
        </td>
        <td>
          <button class="delete" @click="deleteBooking(index)">Удалить</button>
        </td>
      </tr>
    </table>
    <button class="addday" @click="addDay">+ Добавить день</button>

    <h3>Комментарий:</h3>
    <textarea
      rows="3"
      v-model="comment"
      placeholder="Ваши желания, предложения, требования"
    ></textarea>

    <h4>Предложеня:</h4>
    <div class="comment_suggestions">
      <button
        v-for="(suggestion, index) in suggestions"
        :key="index"
        @click="addSuggestion(suggestion)"
      >
        <div class="circle"></div>
        <p>{{ suggestion }}</p>
      </button>
    </div>
    <button class="button" type="button" @click="continueToOptions">Продолжить</button>
  </div>
</template>


<style scoped lang="scss">
@import '../../assets/components/booking/part2/part2_6.scss';
@import '../../assets/components/container.scss';
$color: #ffc107;

.button {
  margin-top: 10px;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5rem;
  color: #fff;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.1rem;
  transition: all 0.3s;
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
    transition: all 0.3s;
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

@media (max-width: 768px) {
    .button {
        padding: 0.4rem 0.8rem;
        font-size: 0.75rem;
    }}

</style>
