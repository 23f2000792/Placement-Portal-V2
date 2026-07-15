<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const destination = computed(() => {
  const routes = {
    admin: '/admin/dashboard',
    company: '/company/dashboard',
    student: '/student/dashboard',
  }

  return routes[authStore.getUserRole] || '/login'
})

const destinationLabel = computed(() =>
  authStore.isAuthenticated
    ? 'Return to dashboard'
    : 'Return to sign in',
)

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
    return
  }

  router.push(destination.value)
}
</script>

<template>
  <main class="not-found-page">
    <section class="not-found-card fade-in">
      <span class="error-code">404</span>

      <h1>Page not found</h1>

      <p>
        The page you requested does not exist or is no longer
        available.
      </p>

      <div class="actions">
        <button
          type="button"
          class="btn btn-outline-secondary"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Go back
        </button>

        <button
          type="button"
          class="btn btn-primary"
          @click="router.push(destination)"
        >
          {{ destinationLabel }}
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background: var(--color-background);
}

.not-found-card {
  width: min(100%, 520px);
  padding: 48px 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.error-code {
  display: block;
  color: var(--color-accent);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.not-found-card h1 {
  margin: 10px 0 0;
  color: var(--color-primary);
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 650;
  letter-spacing: -0.04em;
}

.not-found-card p {
  max-width: 390px;
  margin: 14px auto 0;
  color: var(--color-text-muted);
  font-size: 0.82rem;
  line-height: 1.7;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 28px;
}

.actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
}

@media (max-width: 575.98px) {
  .not-found-card {
    padding: 38px 22px;
  }

  .actions {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>