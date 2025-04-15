<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()
const login = ref<string>('')
const password = ref<string>('')

const signIn = async () => {
  await store.login(login.value, password.value)
}

</script>

<template>
  <div class="signin">
    <form action="">
      <h2>Вход</h2>
      <p>Логин</p>
      <input v-model="login" type="text" placeholder="логин" />
      <p>Пароль</p>
      <input v-model="password" type="password" placeholder="пароль" />
      <div class="checkbox">
        <input   type="checkbox" id="chk1" />
        <label for="chk1">Запомнить меня</label>
      </div>
      <div class="inline">
        <button type="button" @click="signIn">Войти</button>
        <RouterLink to="/register">Регистрация</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped lang="scss">


</style>
