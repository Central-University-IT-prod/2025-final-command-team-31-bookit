<script setup lang="ts">
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
</script>

<template>
  <Header></Header>
  <div class="navbar_spacer"></div>
  <div class="index_part1 container" style="background-image: url(img/bg.png)">
    <div class="box">
      <h2>BookIT - бронирование коворкинга</h2>
      <p>Быстрое и простое бронирование коворкингов</p>
      <RouterLink to="/booking">Забронировать</RouterLink>
    </div>
  </div>
  <div class="index_part2 container">
    <h2>Почему мы?</h2>
    <div class="cards">
      <div class="card">
        <div class="img" style="background-image: url(img/event.png)"></div>
        <h3>Простой интерфейс</h3>
      </div>
      <div class="card">
        <div class="img" style="background-image: url(img/qr-code.png)"></div>
        <h3>Проход по QR коду</h3>
      </div>
      <div class="card">
        <div class="img" style="background-image: url(img/tap.png)"></div>
        <h3>Перебронирование в 1 клик</h3>
      </div>
      <div class="card">
        <div class="img" style="background-image: url(img/people.png)"></div>
        <h3>Возможность бронирования на группу</h3>
      </div>
      <div class="card">
        <div class="img" style="background-image: url(img/equipment.png)"></div>
        <h3>Аренда оборудования</h3>
      </div>
      <div class="card">
        <div class="img" style="background-image: url(img/coffee.png)"></div>
        <h3>Предзаказ еды</h3>
      </div>
    </div>
    <RouterLink to="/booking">Забронировать</RouterLink>
  </div>
  <div class="index_part3 container" id="support">
    <h2>Поддержка</h2>
    <input type="text" placeholder="Ваши контакты" />
    <textarea placeholder="Текст обращения" rows="5"></textarea>
    <button>Отправить</button>
  </div>
  <Footer></Footer>
</template>

<style scoped lang="scss">

</style>
