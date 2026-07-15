import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: {
      guestOnly: true,
    },
  },

  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'admin',
    },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () =>
          import('@/views/admin/DashboardView.vue'),
      },
      {
        path: 'companies',
        name: 'admin-companies',
        component: () =>
          import('@/views/admin/CompaniesView.vue'),
      },
      {
        path: 'companies/:id',
        name: 'admin-company-detail',
        component: () =>
          import('@/views/admin/CompanyDetailView.vue'),
      },
      {
        path: 'students',
        name: 'admin-students',
        component: () =>
          import('@/views/admin/StudentsView.vue'),
      },
      {
        path: 'students/:id',
        name: 'admin-student-detail',
        component: () =>
          import('@/views/admin/StudentDetailView.vue'),
      },
      {
        path: 'drives',
        name: 'admin-drives',
        component: () =>
          import('@/views/admin/DrivesView.vue'),
      },
      {
        path: 'drives/:id',
        name: 'admin-drive-detail',
        component: () =>
          import('@/views/admin/DriveDetailView.vue'),
      },
      {
        path: 'applications',
        name: 'admin-applications',
        component: () =>
          import('@/views/admin/ApplicationsView.vue'),
      },
    ],
  },

  {
    path: '/company',
    component: () => import('@/layouts/CompanyLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'company',
    },
    children: [
      {
        path: '',
        redirect: '/company/dashboard',
      },
      {
        path: 'dashboard',
        name: 'company-dashboard',
        component: () =>
          import('@/views/company/DashboardView.vue'),
      },
      {
        path: 'profile',
        name: 'company-profile',
        component: () =>
          import('@/views/company/ProfileView.vue'),
      },
      {
        path: 'drives',
        name: 'company-drives',
        component: () =>
          import('@/views/company/DrivesView.vue'),
      },
      {
        path: 'drives/create',
        name: 'company-drive-create',
        component: () =>
          import('@/views/company/CreateDriveView.vue'),
      },
      {
        path: 'drives/:id',
        name: 'company-drive-detail',
        component: () =>
          import('@/views/company/DriveDetailView.vue'),
      },
      {
        path: 'applications',
        name: 'company-applications',
        component: () =>
          import('@/views/company/ApplicationsView.vue'),
      },
      {
        path: 'applications/:id',
        name: 'company-application-detail',
        component: () =>
          import('@/views/company/ApplicationDetailView.vue'),
      },
    ],
  },

  {
    path: '/student',
    component: () => import('@/layouts/StudentLayout.vue'),
    meta: {
      requiresAuth: true,
      role: 'student',
    },
    children: [
      {
        path: '',
        redirect: '/student/dashboard',
      },
      {
        path: 'dashboard',
        name: 'student-dashboard',
        component: () =>
          import('@/views/student/DashboardView.vue'),
      },
      {
        path: 'drives',
        name: 'student-drives',
        component: () =>
          import('@/views/student/DrivesView.vue'),
      },
      {
        path: 'drives/:id',
        name: 'student-drive-detail',
        component: () =>
          import('@/views/student/DriveDetailView.vue'),
      },
      {
        path: 'applications',
        name: 'student-applications',
        component: () =>
          import('@/views/student/ApplicationsView.vue'),
      },
      {
        path: 'applications/:id',
        name: 'student-application-detail',
        component: () =>
          import('@/views/student/ApplicationDetailView.vue'),
      },
      {
        path: 'history',
        name: 'student-history',
        component: () =>
          import('@/views/student/HistoryView.vue'),
      },
      {
        path: 'profile',
        name: 'student-profile',
        component: () =>
          import('@/views/student/ProfileView.vue'),
      },
    ],
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,

  scrollBehavior() {
    return {
      top: 0,
    }
  },
})

const dashboardRoutes = {
  admin: '/admin/dashboard',
  company: '/company/dashboard',
  student: '/student/dashboard',
}

const getDashboardRoute = (role) => {
  return dashboardRoutes[role] || '/login'
}

router.beforeEach((to) => {
  const authStore = useAuthStore()

  authStore.initAuth()

  if (
    to.meta.guestOnly &&
    authStore.isAuthenticated
  ) {
    return getDashboardRoute(authStore.getUserRole)
  }

  if (
    to.meta.requiresAuth &&
    !authStore.isAuthenticated
  ) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (
    to.meta.role &&
    authStore.getUserRole !== to.meta.role
  ) {
    return getDashboardRoute(authStore.getUserRole)
  }

  return true
})

export default router