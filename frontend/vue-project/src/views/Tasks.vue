<template>
  <div class="tasks-container">
    <div class="header">
      <h1>Мои задачи</h1>
      <button @click="handleLogout" class="btn-logout">Выйти</button>
    </div>

    <div class="task-form">
      <input v-model="newTask.title" type="text" placeholder="Название задачи" class="input-field">
      <textarea v-model="newTask.description" placeholder="Описание" class="input-field"></textarea>
      <button @click="saveTask" class="btn-primary">
        {{ isEditing ? 'Обновить' : 'Добавить' }}
      </button>
    </div>

      <div v-if="errors.global" class="error-message global-error">
    {{ errors.global }}
    <button @click="errors.global = null" class="close-error">×</button>
  </div>

  <!-- Ошибки для полей формы -->
  <div v-if="errors.fields" class="field-errors">
    <div v-for="(fieldErrors, field) in errors.fields" :key="field" class="field-error">
      <span v-for="(error, idx) in fieldErrors" :key="idx">{{ error }}</span>
    </div>
  </div>

    <div class="filters">
      <button @click="filter = 'all'" :class="{ active: filter === 'all' }">Все</button>
      <button @click="filter = 'active'" :class="{ active: filter === 'active' }">Активные</button>
      <button @click="filter = 'completed'" :class="{ active: filter === 'completed' }">Выполненные</button>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else class="task-list">
      <div v-for="task in filteredTasks" :key="task.id" class="task-item" :class="{ completed: task.is_completed }">
        <div class="task-content">
          <input type="checkbox" :checked="task.is_completed" @change="toggleTask(task)" class="checkbox">
          <div class="task-info">
            <h3>{{ task.title }}</h3>
            <p>{{ task.description }}</p>
            <small>{{ formatDate(task.created_at) }}</small>
          </div>
        </div>
        <div class="task-actions">
          <button @click="editTask(task)" class="btn-edit">✏️</button>
          <button @click="deleteTask(task.id)" class="btn-delete">🗑️</button>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import api from '@/api'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()

    const tasks = ref([])
    const loading = ref(false)
    const errorMessage = ref('')
    const filter = ref('all')
    const isEditing = ref(false)
    const currentTaskId = ref(null)

    const newTask = ref({
      title: '',
      description: '',
      is_completed: false
    })

    // Фильтр задач
    const filteredTasks = computed(() => {
      switch (filter.value) {
        case 'active': return tasks.value.filter(t => !t.is_completed)
        case 'completed': return tasks.value.filter(t => t.is_completed)
        default: return tasks.value
      }
    })

    // Функция для получения заголовка с токеном
    const authHeader = () => ({
      headers: { Authorization: `Bearer ${store.state.token}` }
    })

    // Получение задач
    const fetchTasks = async () => {
      try {
        loading.value = true
        const response = await api.get('/tasks', authHeader())
        tasks.value = response.data
      } catch (error) {
        handleError(error)
      } finally {
        loading.value = false
      }
    }

    // Создание или обновление задачи
    const saveTask = async () => {
      if (!validateForm()) return

      try {
        if (isEditing.value) {
          await api.put(`/tasks/${currentTaskId.value}`, newTask.value, authHeader())
        } else {
          await api.post('/tasks', newTask.value, authHeader())
        }
        resetForm()
        await fetchTasks()
      } catch (error) {
        handleError(error)
      }
    }

    // Изменение статуса выполнения задачи
    const toggleTask = async (task) => {
      try {
        const updatedTask = {
          title: task.title,
          description: task.description,
          is_completed: !task.is_completed // Переключаем статус
        };

        await api.put(`/tasks/${task.id}`, updatedTask, authHeader());

        // Обновляем локально
        task.is_completed = updatedTask.is_completed;
      } catch (error) {
        handleError(error);
      }
    }

    // Редактирование задачи
    const editTask = (task) => {
      isEditing.value = true
      currentTaskId.value = task.id
      newTask.value = { ...task }
    }

    // Удаление задачи
    const deleteTask = async (id) => {
      try {
        await api.delete(`/tasks/${id}`, authHeader())
        await fetchTasks()
      } catch (error) {
        handleError(error)
      }
    }

    // Выход из системы
    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/login')
    }

    // Очистка формы
    const resetForm = () => {
      isEditing.value = false
      currentTaskId.value = null
      newTask.value = { title: '', description: '', is_completed: false }
    }

    // Форматирование даты
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Обработка ошибок
    const errors = ref({
      global: null,
      fields: null
    })

    // Универсальная обработка ошибок
    const handleError = (error) => {
      // Сбрасываем предыдущие ошибки
      errors.value = { global: null, fields: null }

      if (!error.response) {
        errors.value.global = 'Ошибка соединения с сервером'
        return
      }

      const { status, data } = error.response

      switch(status) {
        case 400:
        case 422:
          if (data.errors) {
            // Обработка ошибок валидации
            errors.value.fields = data.errors
          } else if (data.detail) {
            errors.value.global = data.detail
          }
          break
        case 401:
          errors.value.global = 'Сессия истекла. Пожалуйста, войдите снова'
          store.dispatch('logout')
          router.push('/login')
          break
        case 403:
          errors.value.global = 'Доступ запрещен'
          break
        case 404:
          errors.value.global = 'Ресурс не найден'
          break
        case 500:
          errors.value.global = 'Ошибка сервера. Пожалуйста, попробуйте позже'
          break
        default:
          errors.value.global = 'Произошла непредвиденная ошибка'
      }

      // Автоматическое скрытие ошибок через 10 секунд
      setTimeout(() => {
        errors.value = { global: null, fields: null }
      }, 7000)
    }

    // Валидация формы перед отправкой
    const validateForm = () => {
      const formErrors = {}
      if (!newTask.value.title.trim()) {
        formErrors.title = ['Название задачи обязательно']
      }
      if (Object.keys(formErrors).length > 0) {
        errors.value.fields = formErrors
        return false
      }
      return true
    }

    onMounted(fetchTasks)

    return {
      tasks,
      loading,
      errorMessage,
      filter,
      isEditing,
      newTask,
      errors,
      filteredTasks,
      saveTask,
      toggleTask,
      editTask,
      deleteTask,
      handleLogout,
      formatDate
    }
  }
}
</script>

<style scoped>
.tasks-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.task-form {
  margin-bottom: 2rem;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
}

.input-field {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filters {
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
}

.filters button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  background: white;
}

.filters button.active {
  background: #42b983;
  color: white;
  border-color: #42b983;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  background: white;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-item.completed {
  opacity: 0.7;
  background: #f8f8f8;
}

.task-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-grow: 1;
}

.checkbox {
  width: 20px;
  height: 20px;
}

.task-info {
  flex-grow: 1;
}

.task-info h3 {
  margin: 0;
  color: #333;
}

.task-info p {
  margin: 0.5rem 0;
  color: #666;
}

.task-info small {
  color: #999;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-logout {
  background: #ff4444;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit, .btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.3rem;
}

.btn-delete {
  color: #ff4444;
}

.btn-edit {
  color: #42b983;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

/* Стили для ошибок */
.error-message {
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  background: #ffe3e3;
  color: #ff4444;
  border: 1px solid #ffcccc;
  position: relative;
}

.global-error {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 300px;
  z-index: 1000;
}

.close-error {
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 1.2rem;
  line-height: 1;
}

.field-errors {
  margin: 1rem 0;
  padding: 1rem;
  background: #fff3f3;
  border-radius: 4px;
}

.field-error {
  color: #ff4444;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.input-field.invalid {
  border-color: #ff4444;
  background: #fff3f3;
}
</style>
