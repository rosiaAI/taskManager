<template>
  <div class="auth-container">
    <h2>Регистрация</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label>Email:</label>
        <input v-model="email" type="email" required>
      </div>

      <div class="form-group">
        <label>Пароль:</label>
        <input v-model="password" type="password" required>
      </div>

      <button type="submit" class="btn-primary">Зарегистрироваться</button>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="auth-links">
        Уже есть аккаунт? <router-link to="/frontend/vue-project/src/views/LoginPage">Войдите</router-link>
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

    const handleRegister = async () => {
      errorMessage.value = ''
      try {
        await store.dispatch('register', {
          email: email.value,
          password: password.value
        })
        router.push('/tasks')
      } catch (error) {
        // Подробная обработка ошибок
        if (error.response) {
          const errors = error.response.data.errors
          if (errors.email) {
            errorMessage.value = errors.email[0]
          } else if (errors.password) {
            errorMessage.value = errors.password[0]
          } else {
            errorMessage.value = 'Ошибка регистрации'
          }
        } else {
          errorMessage.value = 'Сервер недоступен'
        }
      }
    }

    return {
      email,
      password,
      errorMessage,
      handleRegister
    }
  }
}
</script>
