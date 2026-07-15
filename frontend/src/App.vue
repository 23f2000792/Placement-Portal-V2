<script setup>
import { computed } from 'vue'
import { RouterView } from 'vue-router'

import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()

const successMessage = computed(
  () => messageStore.successMessages,
)

const errorMessage = computed(
  () => messageStore.errorMessages,
)
</script>

<template>
  <div class="app-root">
    <Transition name="notification">
      <div
        v-if="successMessage"
        class="app-notification notification-success"
        role="status"
      >
        <i class="bi bi-check-circle"></i>

        <span>{{ successMessage }}</span>

        <button
          type="button"
          aria-label="Dismiss success message"
          @click="messageStore.clearMessages"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    </Transition>

    <Transition name="notification">
      <div
        v-if="errorMessage"
        class="app-notification notification-error"
        role="alert"
      >
        <i class="bi bi-exclamation-circle"></i>

        <span>{{ errorMessage }}</span>

        <button
          type="button"
          aria-label="Dismiss error message"
          @click="messageStore.clearMessages"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    </Transition>

    <RouterView />
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
}

.app-notification {
  position: fixed;
  top: 18px;
  right: 18px;
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 10px;
  width: min(390px, calc(100vw - 36px));
  padding: 13px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  font-size: 0.78rem;
}

.app-notification > i {
  flex: 0 0 auto;
  font-size: 0.9rem;
}

.app-notification > span {
  flex: 1;
  color: var(--color-text);
  line-height: 1.5;
}

.app-notification > button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  padding: 0;
  color: var(--color-text-muted);
  background: transparent;
  border: 0;
  border-radius: 6px;
}

.app-notification > button:hover {
  color: var(--color-primary);
  background: var(--color-surface-muted);
}

.notification-success {
  border-left: 3px solid #2f6f49;
}

.notification-success > i {
  color: #2f6f49;
}

.notification-error {
  border-left: 3px solid var(--color-danger);
}

.notification-error > i {
  color: var(--color-danger);
}

.notification-enter-active,
.notification-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 575.98px) {
  .app-notification {
    top: 12px;
    right: 12px;
    width: calc(100vw - 24px);
  }
}
</style>