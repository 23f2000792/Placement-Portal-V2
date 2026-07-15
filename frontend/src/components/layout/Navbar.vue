<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const authStore = useAuthStore()

const roleDetails = computed(() => {
  const details = {
    admin: {
      label: 'Institute Portal',
      dashboard: '/admin/dashboard',
    },
    company: {
      label: 'Company Portal',
      dashboard: '/company/dashboard',
    },
    student: {
      label: 'Student Portal',
      dashboard: '/student/dashboard',
    },
  }

  return (
    details[authStore.getUserRole] || {
      label: 'Placement Portal',
      dashboard: '/login',
    }
  )
})

const userEmail = computed(
  () => authStore.user?.email || 'Account',
)

const logout = () => {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <nav class="app-navbar">
    <div class="navbar-left">
      <button
        type="button"
        class="menu-button"
        aria-label="Open navigation"
        @click="$emit('toggle-sidebar')"
      >
        <i class="bi bi-list"></i>
      </button>

      <router-link
        :to="roleDetails.dashboard"
        class="portal-title"
      >
        {{ roleDetails.label }}
      </router-link>
    </div>

    <div class="navbar-right">
      <div class="user-details">
        <span class="user-icon">
          <i class="bi bi-person"></i>
        </span>

        <div>
          <span>Signed in as</span>
          <strong>{{ userEmail }}</strong>
        </div>
      </div>

      <button
        type="button"
        class="logout-button"
        @click="logout"
      >
        <i class="bi bi-box-arrow-right"></i>
        <span>Sign out</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.app-navbar {
  position: fixed;
  top: 0;
  right: 0;
  left: 248px;
  z-index: 1030;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 28px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.navbar-left,
.navbar-right,
.user-details,
.logout-button {
  display: flex;
  align-items: center;
}

.navbar-left {
  gap: 12px;
}

.navbar-right {
  gap: 18px;
}

.menu-button {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  color: var(--color-primary);
  background: transparent;
  border: 0;
  border-radius: 8px;
  font-size: 1.2rem;
}

.menu-button:hover {
  background: var(--color-surface-muted);
}

.portal-title {
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 650;
  text-decoration: none;
}

.user-details {
  gap: 9px;
}

.user-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  color: var(--color-primary);
  background: var(--color-surface-muted);
  border-radius: 8px;
}

.user-details div > span,
.user-details strong {
  display: block;
}

.user-details div > span {
  color: var(--color-text-muted);
  font-size: 0.6rem;
}

.user-details strong {
  max-width: 220px;
  margin-top: 2px;
  overflow: hidden;
  color: var(--color-text);
  font-size: 0.7rem;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-button {
  gap: 7px;
  padding: 8px 11px;
  color: var(--color-text-muted);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
}

.logout-button:hover {
  color: var(--color-danger);
  border-color: #e4c5c2;
  background: #fff7f6;
}

@media (max-width: 991.98px) {
  .app-navbar {
    left: 0;
    padding: 0 18px;
  }

  .menu-button {
    display: inline-flex;
  }
}

@media (max-width: 575.98px) {
  .app-navbar {
    padding: 0 14px;
  }

  .user-details {
    display: none;
  }

  .logout-button span {
    display: none;
  }

  .logout-button {
    width: 36px;
    height: 36px;
    justify-content: center;
    padding: 0;
  }
}
</style>