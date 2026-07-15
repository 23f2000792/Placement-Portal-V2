import { defineStore } from 'pinia'

let errorTimer = null
let successTimer = null

export const useMessageStore = defineStore('message', {
  state: () => ({
    errorMessages: null,
    successMessages: null,
  }),

  actions: {
    updateErrorMessages(message) {
      if (errorTimer) {
        clearTimeout(errorTimer)
      }

      this.errorMessages = message
      this.successMessages = null

      errorTimer = setTimeout(() => {
        this.errorMessages = null
        errorTimer = null
      }, 5000)
    },

    updateSuccessMessages(message) {
      if (successTimer) {
        clearTimeout(successTimer)
      }

      this.successMessages = message
      this.errorMessages = null

      successTimer = setTimeout(() => {
        this.successMessages = null
        successTimer = null
      }, 5000)
    },

    clearMessages() {
      if (errorTimer) {
        clearTimeout(errorTimer)
        errorTimer = null
      }

      if (successTimer) {
        clearTimeout(successTimer)
        successTimer = null
      }

      this.errorMessages = null
      this.successMessages = null
    },
  },
})