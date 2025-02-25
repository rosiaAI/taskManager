import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    redirect: '/tasks'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to) => {
  // Получаем состояние напрямую из хранилища
  const isAuthenticated = store.getters.isAuthenticated
  const isTokenExpired = () => {
    const token = store.state.token
    if (!token) return true
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  }

  // Для защищенных маршрутов
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return { name: 'Login' }
    }

    if (isTokenExpired()) {
      await store.dispatch('logout')
      return {
        name: 'Login',
        query: { sessionExpired: 'true' }
      }
    }
  }

  // Редирект авторизованных пользователей
  if (['Login', 'Register'].includes(to.name) && isAuthenticated && !isTokenExpired()) {
    return { name: 'Tasks' }
  }
})

export default router
