<!-- frontend/src/views/HomeView.vue -->
<template>
  <div class="home">
    <div class="home-content">
      <h1 class="title">Placement Portal</h1>
      <p class="subtitle">Your gateway to campus placements</p>
      
      <div class="buttons" v-if="!authStore.isAuthenticated">
        <router-link to="/login" class="btn btn-primary btn-lg me-3">Login</router-link>
        <router-link to="/register" class="btn btn-outline-light btn-lg">Register</router-link>
      </div>
      
      <div class="buttons" v-else>
        <p class="text-white mb-3">Welcome back, {{ authStore.user?.email }}</p>
        <p class="text-white-50 mb-3">Role: {{ authStore.user?.role }}</p>
        <button @click="goToDashboard" class="btn btn-success btn-lg me-2">Go to Dashboard</button>
        <button @click="logout" class="btn btn-danger btn-lg">Logout</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = async () => {
  console.log('Logout clicked')
  await authStore.logout()
  router.push('/')
}

const goToDashboard = () => {
  console.log('Go to dashboard clicked')
  console.log('Current user:', authStore.user)
  console.log('Token exists:', !!authStore.token)
  
  // Remove the checkAuth call - it doesn't exist!
  
  if (authStore.isAdmin) {
    console.log('Redirecting to admin dashboard')
    router.push('/admin/dashboard')
  } else if (authStore.isCompany) {
    router.push('/company/dashboard')
  } else if (authStore.isStudent) {
    router.push('/student/dashboard')
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.home {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
  padding: 0;
}

.home-content {
  text-align: center;
  color: white;
  width: 100%;
  max-width: 800px;
  padding: 20px;
}

.title {
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn {
  padding: 12px 30px;
  font-size: 1.2rem;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #1266f1;
  border: none;
}

.btn-primary:hover {
  background-color: #0d47a1;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

@media (max-width: 768px) {
  .title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
}
</style>