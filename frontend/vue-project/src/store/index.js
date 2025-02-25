import { createStore } from 'vuex'
import api from '@/api'
import router from '@/router'

const store = createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || null
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
      localStorage.removeItem('token')
    }
  },
  actions: {
    initialize({ commit, dispatch }) {
      const token = localStorage.getItem('token')
      if (token) {
        commit('SET_TOKEN', token)
        const payload = JSON.parse(atob(token.split('.')[1]))
        const expiresIn = payload.exp * 1000 - Date.now()
        if (expiresIn > 0) {
          setTimeout(() => dispatch('logout'), expiresIn)
        }
      }
    },
    async login({ commit }, { email, password }) {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      commit('SET_TOKEN', response.data.access_token);
      const userResponse = await api.get('/auth/me');
      commit('SET_USER', userResponse.data);
    },
    logout({ commit }) {
      commit('LOGOUT')
      router.push('/login')
    },
    async register({ commit }, { email, password }) {
      try {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await api.post('/auth/register', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        commit('SET_TOKEN', response.data.access_token);

        const userResponse = await api.get('/auth/me');
        commit('SET_USER', userResponse.data);
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Registration failed');
      }
    },
  },
  getters: {
    isAuthenticated: state => !!state.token,
    isTokenExpired: state => {
      if (!state.token) return true
      const payload = JSON.parse(atob(state.token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    }
  }
})

export default store
