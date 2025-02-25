<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import store from './store'

onMounted(() => {
  store.dispatch('initialize')
})
</script>
<style>
#app {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
