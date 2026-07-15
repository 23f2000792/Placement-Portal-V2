<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close'])

const route = useRoute()
const authStore = useAuthStore()

const navigation = {
  admin: [
    {
      label: 'Dashboard',
      icon: 'bi-grid',
      path: '/admin/dashboard',
    },
    {
      label: 'Companies',
      icon: 'bi-buildings',
      path: '/admin/companies',
    },
    {
      label: 'Students',
      icon: 'bi-people',
      path: '/admin/students',
    },
    {
      label: 'Placement drives',
      icon: 'bi-briefcase',
      path: '/admin/drives',
    },
    {
      label: 'Applications',
      icon: 'bi-file-earmark-text',
      path: '/admin/applications',
    },
  ],

  company: [
    {
      label: 'Dashboard',
      icon: 'bi-grid',
      path: '/company/dashboard',
    },
    {
      label: 'Company profile',
      icon: 'bi-building',
      path: '/company/profile',
    },
    {
      label: 'Placement drives',
      icon: 'bi-briefcase',
      path: '/company/drives',
    },
    {
      label: 'Applications',
      icon: 'bi-file-earmark-text',
      path: '/company/applications',
    },
  ],

  student: [
    {
      label: 'Dashboard',
      icon: 'bi-grid',
      path: '/student/dashboard',
    },
    {
      label: 'Placement drives',
      icon: 'bi-briefcase',
      path: '/student/drives',
    },
    {
      label: 'My applications',
      icon: 'bi-file-earmark-text',
      path: '/student/applications',
    },
    {
      label: 'Placement history',
      icon: 'bi-clock-history',
      path: '/student/history',
    },
    {
      label: 'My profile',
      icon: 'bi-person',
      path: '/student/profile',
    },
  ],
}

const role = computed(
  () => authStore.getUserRole,
)

const navigationItems = computed(
  () => navigation[role.value] || [],
)

const roleLabel = computed(() => {
  const labels = {
    admin: 'Institute',
    company: 'Company',
    student: 'Student',
  }

  return labels[role.value] || 'Portal'
})

const isActive = (path) => {
  if (route.path === path) {
    return true
  }

  return route.path.startsWith(`${path}/`)
}

const closeSidebar = () => {
  emit('close')
}
</script>

<template>
  <aside
    class="app-sidebar"
    :class="{ 'sidebar-open': open }"
  >
    <div class="sidebar-brand">
      <router-link
        :to="`/${role}/dashboard`"
        class="brand-link"
        @click="closeSidebar"
      >
        <span class="brand-mark">P</span>

        <div>
          <strong>Placement Portal</strong>
          <span>{{ roleLabel }}</span>
        </div>
      </router-link>

      <button
        type="button"
        class="sidebar-close"
        aria-label="Close navigation"
        @click="closeSidebar"
      >
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <nav
      class="sidebar-navigation"
      aria-label="Primary navigation"
    >
      <router-link
        v-for="item in navigationItems"
        :key="item.path"
        :to="item.path"
        class="navigation-link"
        :class="{ active: isActive(item.path) }"
        @click="closeSidebar"
      >
        <i :class="['bi', item.icon]"></i>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <span class="footer-mark">PPA</span>

      <div>
        <strong>Placement Portal</strong>
        <span>Application V2</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1040;
  display: flex;
  flex-direction: column;
  width: 248px;
  background: var(--color-primary);
  transition: transform 200ms ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
  color: #ffffff;
  text-decoration: none;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  color: var(--color-primary);
  background: #ffffff;
  border-radius: 9px;
  font-size: 0.9rem;
  font-weight: 700;
}

.brand-link div {
  min-width: 0;
}

.brand-link strong,
.brand-link div > span {
  display: block;
}

.brand-link strong {
  overflow: hidden;
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-link div > span {
  margin-top: 2px;
  color: rgba(255, 255, 255, 0.48);
  font-size: 0.64rem;
}

.sidebar-close {
  display: none;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  color: rgba(255, 255, 255, 0.65);
  background: transparent;
  border: 0;
  border-radius: 7px;
}

.sidebar-close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-navigation {
  flex: 1;
  padding: 18px 12px;
  overflow-y: auto;
}

.navigation-link {
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 42px;
  margin-bottom: 3px;
  padding: 0 12px;
  color: rgba(255, 255, 255, 0.58);
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 500;
  text-decoration: none;
  transition:
    color 150ms ease,
    background 150ms ease;
}

.navigation-link i {
  width: 18px;
  font-size: 0.9rem;
  text-align: center;
}

.navigation-link:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.06);
}

.navigation-link.active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.11);
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.sidebar-footer strong,
.sidebar-footer div > span {
  display: block;
}

.sidebar-footer strong {
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.68rem;
  font-weight: 600;
}

.sidebar-footer div > span {
  margin-top: 2px;
  color: rgba(255, 255, 255, 0.38);
  font-size: 0.6rem;
}

@media (max-width: 991.98px) {
  .app-sidebar {
    transform: translateX(-100%);
  }

  .app-sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-close {
    display: inline-flex;
  }
}
</style>