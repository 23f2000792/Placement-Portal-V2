<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterView, useRouter } from 'vue-router'

import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import { companyAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

const sidebarOpen = ref(false)
const companyProfile = ref({})
const loading = ref(true)

const isBlacklisted = computed(
  () => Boolean(companyProfile.value.is_blacklisted),
)

const isApproved = computed(
  () => companyProfile.value.approval_status === 'approved',
)

const fetchCompanyProfile = async () => {
  loading.value = true

  try {
    const response = await companyAPI.getProfile()

    companyProfile.value = response.data.profile || {}
  } catch (error) {
    console.error(
      'Unable to load company profile:',
      error,
    )

    messageStore.updateErrorMessages(
      error.response?.data?.message ||
        'Unable to load your company profile.',
    )
  } finally {
    loading.value = false
  }
}

const toggleSidebar = () => {
  if (isBlacklisted.value) return

  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

const logout = () => {
  authStore.logout()
  router.replace('/login')
}

onMounted(() => {
  fetchCompanyProfile()
})
</script>

<template>
  <div class="app-layout">
    <Navbar @toggle-sidebar="toggleSidebar" />

    <main
      v-if="loading"
      class="layout-loading"
      aria-live="polite"
    >
      <div
        class="spinner-border spinner-border-sm"
        role="status"
      >
        <span class="visually-hidden">
          Loading company workspace
        </span>
      </div>

      <span>Loading company workspace...</span>
    </main>

    <template v-else-if="isBlacklisted">
      <main class="account-state-page">
        <section class="account-state-card">
          <span class="state-icon">
            <i class="bi bi-lock"></i>
          </span>

          <h1>Company access suspended</h1>

          <p>
            This company account has been blacklisted by the
            institute placement cell. Placement drives and
            applications are currently unavailable.
          </p>

          <span class="state-note">
            Contact the institute placement cell for clarification
            about your account status.
          </span>

          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="logout"
          >
            <i class="bi bi-box-arrow-right"></i>
            Sign out
          </button>
        </section>
      </main>
    </template>

    <template v-else>
      <Sidebar
        :open="sidebarOpen"
        @close="closeSidebar"
      />

      <main class="layout-content">
        <section
          v-if="!isApproved"
          class="approval-notice"
          role="status"
        >
          <span class="notice-icon">
            <i class="bi bi-clock"></i>
          </span>

          <div>
            <strong>Company approval pending</strong>

            <p>
              Your company profile is awaiting institute approval.
              Placement drives cannot be created until the account
              is approved.
            </p>
          </div>
        </section>

        <RouterView />
      </main>

      <Transition name="backdrop">
        <button
          v-if="sidebarOpen"
          type="button"
          class="sidebar-backdrop"
          aria-label="Close navigation"
          @click="closeSidebar"
        ></button>
      </Transition>
    </template>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--color-background);
}

.layout-content {
  min-height: 100vh;
  margin-left: 248px;
  padding: 92px 28px 36px;
}

.layout-loading,
.account-state-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.layout-loading {
  gap: 10px;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.approval-notice {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  margin-bottom: 24px;
  padding: 15px 17px;
  background: #fff8e8;
  border: 1px solid #f0d99e;
  border-radius: var(--border-radius);
}

.notice-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  color: #704500;
  background: #ffefc5;
  border-radius: 8px;
}

.approval-notice strong {
  color: #704500;
  font-size: 0.82rem;
}

.approval-notice p {
  margin: 4px 0 0;
  color: #875b17;
  font-size: 0.75rem;
  line-height: 1.55;
}

.account-state-page {
  padding: 88px 24px 40px;
}

.account-state-card {
  width: min(100%, 520px);
  padding: 40px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.state-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  color: var(--color-danger);
  background: #feeceb;
  border-radius: 12px;
  font-size: 1.2rem;
}

.account-state-card h1 {
  margin: 20px 0 0;
  color: var(--color-primary);
  font-size: 1.55rem;
  font-weight: 650;
}

.account-state-card p {
  margin: 13px 0 0;
  color: var(--color-text-muted);
  font-size: 0.84rem;
  line-height: 1.7;
}

.state-note {
  display: block;
  margin-top: 12px;
  color: var(--color-text-muted);
  font-size: 0.74rem;
}

.account-state-card .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 26px;
}

.sidebar-backdrop {
  display: none;
}

.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity 180ms ease;
}

.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
}

@media (max-width: 991.98px) {
  .layout-content {
    margin-left: 0;
    padding: 88px 20px 32px;
  }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1035;
    display: block;
    padding: 0;
    background: rgba(20, 25, 34, 0.42);
    border: 0;
  }
}

@media (max-width: 575.98px) {
  .layout-content {
    padding: 84px 14px 28px;
  }

  .account-state-page {
    padding-right: 14px;
    padding-left: 14px;
  }

  .account-state-card {
    padding: 32px 22px;
  }
}
</style>