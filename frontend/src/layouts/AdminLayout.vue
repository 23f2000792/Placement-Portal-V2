<script setup>
import { ref } from 'vue'
import { RouterView } from 'vue-router'

import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'

const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}
</script>

<template>
  <div class="app-layout">
    <Sidebar
      :open="sidebarOpen"
      @close="closeSidebar"
    />

    <Navbar
      @toggle-sidebar="toggleSidebar"
    />

    <main class="layout-content">
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

.sidebar-backdrop {
  display: none;
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
    width: 100%;
    height: 100%;
    padding: 0;
    background: rgba(20, 25, 34, 0.42);
    border: 0;
  }
}

@media (max-width: 575.98px) {
  .layout-content {
    padding: 84px 14px 28px;
  }
}

.backdrop-enter-active,
.backdrop-leave-active {
  transition: opacity 180ms ease;
}

.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
}
</style>