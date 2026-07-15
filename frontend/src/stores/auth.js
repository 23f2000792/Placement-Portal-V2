import { defineStore } from 'pinia'

import {
  authAPI,
  setAuthToken,
} from '@/services/api'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

const readStoredUser = () => {
  try {
    const storedUser = localStorage.getItem(USER_KEY)

    return storedUser
      ? JSON.parse(storedUser)
      : null
  } catch {
    localStorage.removeItem(USER_KEY)

    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY),
    user: readStoredUser(),
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) =>
      Boolean(state.token && state.user),

    getUserRole: (state) =>
      state.user?.role || null,

    isAdmin: (state) =>
      state.user?.role === 'admin',

    isCompany: (state) =>
      state.user?.role === 'company',

    isStudent: (state) =>
      state.user?.role === 'student',

    getUserEmail: (state) =>
      state.user?.email || '',
  },

  actions: {
    initAuth() {
      if (!this.token || !this.user) {
        this.clearAuth()
        return
      }

      setAuthToken(this.token)
    },

    setAuth(token, user) {
      this.token = token
      this.user = user

      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(
        USER_KEY,
        JSON.stringify(user),
      )

      setAuthToken(token)
    },

    clearAuth() {
      this.token = null
      this.user = null

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)

      setAuthToken(null)
    },

    async login(credentials) {
      this.loading = true

      try {
        const response = await authAPI.login(credentials)

        const token = response.data.auth_token
        const user = response.data.user

        if (!token || !user) {
          return {
            success: false,
            error:
              'The server returned an invalid login response.',
          }
        }

        this.setAuth(token, user)

        return {
          success: true,
          user,
        }
      } catch (error) {
        return {
          success: false,
          error:
            error.response?.data?.message ||
            'Unable to sign in.',
        }
      } finally {
        this.loading = false
      }
    },

    async registerStudent(data) {
      this.loading = true

      try {
        const response =
          await authAPI.registerStudent(data)

        return {
          success: true,
          message:
            response.data.message ||
            'Student registration completed.',
        }
      } catch (error) {
        return {
          success: false,
          error:
            error.response?.data?.message ||
            'Unable to register student account.',
        }
      } finally {
        this.loading = false
      }
    },

    async registerCompany(data) {
      this.loading = true

      try {
        const response =
          await authAPI.registerCompany(data)

        return {
          success: true,
          message:
            response.data.message ||
            'Company registration completed.',
        }
      } catch (error) {
        return {
          success: false,
          error:
            error.response?.data?.message ||
            'Unable to register company account.',
        }
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.clearAuth()
    },
  },
})