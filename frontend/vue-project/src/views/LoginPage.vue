<template>
  <div class="auth-container">
    <h2>Вход в систему</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Email:</label>
        <input v-model="email" type="email" required>
      </div>

      <div class="form-group">
        <label>Пароль:</label>
        <input v-model="password" type="password" required>
      </div>

      <button type="submit" class="btn-primary">Войти</button>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="auth-links">
        Нет аккаунта? <router-link to="/frontend/vue-project/src/views/RegisterPage">Зарегистрируйтесь</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const email = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const store = useStore()
    const router = useRouter()

    const handleLogin = async () => {
      try {
        await store.dispatch('login', {
          email: email.value,
          password: password.value
        })
        await router.push('/tasks')
      } catch (error) {
        errorMessage.value = 'Ошибка авторизации: проверьте данные'
        console.error('Login error:', error)
      }
    }

    return {
      email,
      password,
      errorMessage,
      handleLogin
    }
  }
}
</script>
