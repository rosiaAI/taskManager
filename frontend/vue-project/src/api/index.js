import axios from 'axios'
import store from '../store' // Импортируем хранилище напрямую

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// Интерсептор для добавления токена
api.interceptors.request.use(config => {
  const token = store.state.token // Получаем токен напрямую из хранилища
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Интерсептор для обработки просроченного токена
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response.status === 401) {
      await store.dispatch('logout') // Вызываем action напрямую
      window.location = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
