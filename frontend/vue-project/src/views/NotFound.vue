<template>
  <div class="not-found">
    <h1>404 - Страница не найдена</h1>
    <router-link to="/">Вернуться на главную</router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 2rem;
}
</style>
