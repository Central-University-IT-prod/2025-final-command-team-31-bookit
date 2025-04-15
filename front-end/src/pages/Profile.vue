<script setup lang="ts">
import { computed } from 'vue';
import { useProfileStore } from '@/stores/profile';
import Header from '../components/Header.vue'
import AccSidebar from '@/components/account/AccSidebar.vue';
import AccMain from '@/components/account/AccFast.vue';
import AccData from '@/components/account/AccData.vue';
import AccBooking from '@/components/account/AccBooking.vue';

const profileStore = useProfileStore()
const currentStep = computed(() => profileStore.currentStep)




</script>

<template>
  <Header></Header>
  <div class="navbar_spacer"></div>
  <div class="account">
    <AccSidebar></AccSidebar>
    <AccMain v-show="currentStep === 0"></AccMain>
    <AccData v-show="currentStep === 1"></AccData>
    <AccBooking v-show="currentStep === 2"></AccBooking>
  </div>
</template>

<style scoped>
@import '../assets/components/account.scss';

</style>
