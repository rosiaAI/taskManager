<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">Вход в систему</h2>

      <form @submit.prevent="handleLogin" class="auth-form">
        <!-- Поле Email -->
        <div class="form-group">
          <label class="input-label">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="input-field"
            :class="{ 'invalid': errors.fields?.email }"
            placeholder="example@mail.com"
            @input="clearError('email')"
          >
          <transition name="fade">
            <div v-if="errors.fields?.email" class="error-message">
              {{ errors.fields.email[0] }}
            </div>
          </transition>
        </div>

        <!-- Поле Пароль -->
        <div class="form-group">
          <label class="input-label">Пароль</label>
          <input
            v-model="form.password"
            type="password"
            class="input-field"
            :class="{ 'invalid': errors.fields?.password }"
            placeholder="••••••••"
            @input="clearError('password')"
          >
          <transition name="fade">
            <div v-if="errors.fields?.password" class="error-message">
              {{ errors.fields.password[0] }}
            </div>
          </transition>
        </div>

        <!-- Кнопка входа -->
        <button
          type="submit"
          class="btn-primary"
          :disabled="loading"
        >
          <span v-if="loading" class="loader"></span>
          {{ loading ? 'Выполняется вход...' : 'Войти' }}
        </button>

        <!-- Ссылки -->
        <div class="auth-links">
          Нет аккаунта?
          <router-link :to="{ name: 'Register' }" class="link">Зарегистрироваться</router-link>
        </div>
      </form>
    </div>

    <!-- Глобальные уведомления -->
    <transition name="slide-fade">
      <div v-if="errors.global" class="global-notification error">
        {{ errors.global }}
        <button @click="clearGlobalError" class="close-btn">×</button>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()

    const form = ref({
      email: '',
      password: ''
    })

    const errors = ref({
      global: null,
      fields: null
    })

    const loading = ref(false)

    const validateForm = () => {
      const newErrors = {}
      let isValid = true

      // Валидация email
      if (!form.value.email) {
        newErrors.email = ['Email обязателен для заполнения']
        isValid = false
      } else if (!/\S+@\S+\.\S+/.test(form.value.email)) {
        newErrors.email = ['Введите корректный email']
        isValid = false
      }

      // Валидация пароля
      if (!form.value.password) {
        newErrors.password = ['Пароль обязателен для заполнения']
        isValid = false
      } else if (form.value.password.length < 6) {
        newErrors.password = ['Пароль должен содержать минимум 6 символов']
        isValid = false
      }

      if (Object.keys(newErrors).length > 0) {
        errors.value.fields = newErrors
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) return

      try {
        loading.value = true
        clearErrors()

        await store.dispatch('login', {
          email: form.value.email,
          password: form.value.password
        })
        await router.push('/tasks')
      } catch (error) {
        handleError(error)
      } finally {
        loading.value = false
      }
    }

    const handleError = (error) => {
      // Сброс предыдущих ошибок
      clearErrors()

      if (!error.response) {
        errors.value.global = 'Ошибка соединения с сервером'
        return
      }

      const { status, data } = error.response

      switch (status) {
        case 400:
        case 422:
          if (data.detail) {
            if (data.detail[0].type === 'missing'){
              errors.value.global = 'Пользователь с таким email не зарегистрирован'
            } else {
              errors.value.global = data.detail
            }
          } else if (data.errors) {
            errors.value.fields = data.errors
          }
          break
        case 401:
          errors.value.global = 'Неверные учетные данные'
          break
        case 403:
          errors.value.global = 'Доступ запрещен'
          break
        case 500:
          errors.value.global = 'Ошибка сервера. Попробуйте позже'
          break
        default:
          errors.value.global = 'Произошла непредвиденная ошибка'
      }

      // Автоматическое скрытие через 5 секунд
      setTimeout(clearErrors, 7000)
    }

    const clearError = (field) => {
      if (errors.value.fields?.[field]) {
        delete errors.value.fields[field]
      }
    }

    const clearGlobalError = () => {
      errors.value.global = null
    }

    const clearErrors = () => {
      errors.value.global = null
      errors.value.fields = null
    }

    return {
      form,
      errors,
      loading,
      handleLogin,
      clearError,
      clearGlobalError
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 2rem;
}

.auth-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  transition: transform 0.3s ease;
}

.auth-card:hover {
  transform: translateY(-2px);
}

.auth-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
}

.input-field {
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.1);
}

.input-field.invalid {
  border-color: #fc8181;
  background-color: #fff5f5;
}

.btn-primary {
  width: 100%;
  padding: 0.8rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.auth-links {
  text-align: center;
  margin-top: 1rem;
  color: #718096;
  font-size: 0.9rem;
}

.link {
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.5rem;
}

.link:hover {
  text-decoration: underline;
}

.error-message {
  color: #e53e3e;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  padding: 0.25rem 0;
}

.global-notification {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.global-notification.error {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  margin-left: 1rem;
  font-size: 1.2rem;
  line-height: 1;
}

.loader {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
