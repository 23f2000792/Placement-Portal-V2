<script setup>
import { ref } from 'vue'
import {
  RouterLink,
  useRoute,
  useRouter,
} from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const redirectAfterLogin = async () => {
  const roleRoutes = {
    admin: '/admin/dashboard',
    company: '/company/dashboard',
    student: '/student/dashboard',
  }

  const requestedRoute =
    typeof route.query.redirect === 'string'
      ? route.query.redirect
      : null

  const role = authStore.getUserRole
  const rolePrefix = `/${role}/`

  const destination =
    requestedRoute?.startsWith(rolePrefix)
      ? requestedRoute
      : roleRoutes[role] || '/login'

  await router.replace(destination)
}

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const result = await authStore.login({
      email: email.value.trim(),
      password: password.value,
    })

    if (!result.success) {
      error.value = result.error || 'Unable to sign in.'
      return
    }

    await redirectAfterLogin()
  } catch (loginError) {
    console.error('Login failed:', loginError)
    error.value = 'Unable to sign in. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <div class="brand">
        <span class="brand-mark">P</span>

        <div>
          <p class="brand-name">Placement Portal</p>
          <p class="brand-description">Institute Placement Cell</p>
        </div>
      </div>

      <div class="auth-heading">
        <h1>Welcome back</h1>
        <p>Sign in to access your placement workspace.</p>
      </div>

      <div
        v-if="error"
        class="alert alert-danger"
        role="alert"
      >
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label
            for="email"
            class="form-label"
          >
            Email address
          </label>

          <input
            id="email"
            v-model="email"
            type="email"
            class="form-control"
            placeholder="name@example.com"
            autocomplete="email"
            required
            :disabled="loading"
          />
        </div>

        <div class="mb-4">
          <label
            for="password"
            class="form-label"
          >
            Password
          </label>

          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            placeholder="Enter your password"
            autocomplete="current-password"
            required
            :disabled="loading"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100 sign-in-button"
          :disabled="loading"
        >
          <span
            v-if="loading"
            class="spinner-border spinner-border-sm"
            role="status"
            aria-hidden="true"
          ></span>

          <span>{{ loading ? 'Signing in...' : 'Sign in' }}</span>
        </button>
      </form>

      <div class="registration-copy">
        <span>New to the placement portal?</span>

        <RouterLink to="/register">
          Create an account
        </RouterLink>
      </div>

      <p class="auth-note">
        Students and approved company representatives can access the portal
        using their registered credentials.
      </p>
    </section>

    <aside class="information-panel">
      <div class="information-content">
        <span class="eyebrow">Placement Portal Application</span>

        <h2>
          Recruitment coordination, without the spreadsheet clutter.
        </h2>

        <p>
          A single workspace for placement drives, student applications,
          interview progress, and institute oversight.
        </p>

        <div class="feature-list">
          <div class="feature">
            <i class="bi bi-briefcase"></i>

            <div>
              <strong>Placement drives</strong>
              <span>Discover and manage approved recruitment opportunities.</span>
            </div>
          </div>

          <div class="feature">
            <i class="bi bi-file-earmark-check"></i>

            <div>
              <strong>Application tracking</strong>
              <span>Follow recruitment progress from application to selection.</span>
            </div>
          </div>

          <div class="feature">
            <i class="bi bi-bar-chart"></i>

            <div>
              <strong>Institute oversight</strong>
              <span>Maintain structured placement records and activity reports.</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.85fr);
  min-height: 100vh;
  background: var(--color-surface);
}

.auth-panel {
  width: 100%;
  max-width: 460px;
  margin: auto;
  padding: 48px 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 64px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: 9px;
  font-weight: 700;
}

.brand-name,
.brand-description {
  margin: 0;
}

.brand-name {
  color: var(--color-primary);
  font-size: 0.925rem;
  font-weight: 650;
}

.brand-description {
  margin-top: 2px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.auth-heading {
  margin-bottom: 28px;
}

.auth-heading h1 {
  margin-bottom: 8px;
  font-size: 2rem;
  font-weight: 650;
  letter-spacing: -0.04em;
}

.auth-heading p {
  color: var(--color-text-muted);
  font-size: 0.925rem;
}

.sign-in-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 44px;
}

.registration-copy {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 24px;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.registration-copy a {
  font-weight: 600;
}

.auth-note {
  margin-top: 32px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  line-height: 1.6;
  text-align: center;
}

.information-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  padding: 72px 64px 36px;
  color: #ffffff;
  background: var(--color-primary);
}

.information-content {
  max-width: 520px;
  margin: auto 0;
}

.eyebrow {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.72rem;
  font-weight: 650;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.information-panel h2 {
  max-width: 500px;
  margin: 20px 0 18px;
  color: #ffffff;
  font-size: clamp(2rem, 3vw, 3.25rem);
  font-weight: 600;
  letter-spacing: -0.05em;
  line-height: 1.08;
}

.information-content > p {
  max-width: 500px;
  color: rgba(255, 255, 255, 0.62);
  font-size: 0.95rem;
  line-height: 1.7;
}

.feature-list {
  display: grid;
  gap: 24px;
  margin-top: 52px;
}

.feature {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.feature > i {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.feature strong,
.feature span {
  display: block;
}

.feature strong {
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
}

.feature span {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  line-height: 1.5;
}

.information-footer {
  margin: 0;
  color: rgba(255, 255, 255, 0.32);
  font-size: 0.72rem;
}

@media (max-width: 991.98px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .information-panel {
    display: none;
  }

  .auth-panel {
    max-width: 480px;
  }
}

@media (max-width: 575.98px) {
  .auth-panel {
    padding: 32px 22px;
  }

  .brand {
    margin-bottom: 48px;
  }

  .auth-heading h1 {
    font-size: 1.75rem;
  }

  .registration-copy {
    flex-wrap: wrap;
  }
}
</style>