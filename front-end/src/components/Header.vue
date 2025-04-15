<script setup lang="ts">
import { ref } from 'vue';

const isMenuOpen = ref(false);

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};
</script>

<template>
  <div class="navbar">
    <div class="inner">
      <div class="left">
        <h2><RouterLink to="/">BookIT</RouterLink></h2>
      </div>

      <div class="hamburger" :class="{ active: isMenuOpen }" @click="toggleMenu">
        <span></span>
        <span></span>
        <span></span>
      </div>

      <div class="right" :class="{ active: isMenuOpen }">
        <a href="/index">Главная</a>
        <a href="/booking">Забронировать</a>
        <RouterLink to="/">Личный кабинет</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
</style>
