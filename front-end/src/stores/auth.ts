import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import router from '@/router'
import type { User } from '@/models/index'
import axios from 'axios'

export const useAuthStore = defineStore('counter', () => {
  const userInfo = ref({
    user: {} as User,
  })

  const login = async (login: string, password: string) => {
    try {
      const response = await axios.post(`/api/sign_in`, {
        login: login,
        password: password,
      })
      localStorage.setItem('token', response.data.user_token)
      router.replace('/')
      setTimeout(() => {
        location.reload()
      }, 400)
    } catch (e: any) {
      alert(e.response?.data?.message)
    }
  }

  const registration = async (
    role: string,
    login: string,
    name: string,
    surname: string,
    secondname: string,
    password: string,
    email: string,
    contacts: string,
  ) => {
    try {
      const response = await axios.post(`/api/sign_up`, {
        role: role,
        name: name,
        surname: surname,
        secondname: secondname,
        email: email,
        contacts: contacts,
        login: login,
        password: password,
      })
      // const file = await axios.post(`/api/avatar`, {
      //   file: file
      // })
      localStorage.setItem('token', response.data.user_token)
      router.replace('/')
    } catch (e: any) {
      alert(e.response.data.message)
    }
  }

  const patchData = async (
    role: string,
    login: string,
    name: string,
    surname: string,
    second_name: string,
    email: string,
    contacts: string,
  ) => {
    try {
      const token: any = localStorage.getItem('token')
      const response = await axios.patch(
        `/api/edit_user_data`,
        {
          role: role,
          name: name,
          surname: surname,
          second_name: second_name,
          email: email,
          contacts: contacts,
          login: login,
        },
        {
          headers: {
            Authorization: `${token}`,
          },
        },
      )
      userInfo.value = { user: response.data }
    } catch (e: any) {
      alert(e.response.data.message)
    }
  }

  const chekAuth = async () => {
    try {
      const token: any = localStorage.getItem('token')
      if (token == 'undefined' || token == undefined || token == null) {
        console.log(token)
        router.replace('/login')
      } else {
        console.log(token)
        const response = await axios.get(`/api/user_info`, {
          headers: {
            Authorization: `${token}`,
          },
        })
        userInfo.value = { user: response.data }
        console.log(userInfo.value.user)
      }
    } catch (e) {
      throw e
    }
  }

  const logOut = async () => {
    const token: any = localStorage.getItem('token')
    try {
      const response = await axios.post(
        `/api/sign_out`,
        {},
        {
          headers: {
            Authorization: `${token}`,
          },
        },
      )
      localStorage.removeItem('token')
      userInfo.value = {
        user: {} as User,
      }
      router.replace('/')
      location.reload()
    } catch (e) {
      throw e
    }
  }

  

  return { userInfo, login, registration, patchData, chekAuth, logOut }
})
