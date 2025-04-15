import { createRouter, createWebHistory } from 'vue-router'
import AdminPage from '../pages/AdminPage.vue'
import Main from '../pages/Main.vue'
import BookingPage from '../pages/BookingPage.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Profile from '../pages/Profile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/index',
      name: 'main',
      component: Main
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
    },
    {
      path:'/booking',
      name: 'booking',
      component: BookingPage,
    },
    {
      path:'/login',
      name: 'login',
      component: Login,
    },
    {
      path:'/register',
      name: 'register',
      component: Register,
    },
    {
      path:'/',
      name: 'profile',
      component: Profile,
    },
  ],
})

export default router
