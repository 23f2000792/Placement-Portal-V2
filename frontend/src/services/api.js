import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const setAuthToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common[
      'Authentication-Token'
    ] = token
    return
  }

  delete apiClient.defaults.headers.common[
    'Authentication-Token'
  ]
}

const downloadAuthenticatedFile = async (url, filename) => {
  const response = await apiClient.get(url, {
    responseType: 'blob',
  })

  const blob = new Blob([response.data], {
    type: response.headers['content-type'] || 'text/csv',
  })

  const blobUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = blobUrl
  link.setAttribute('download', filename)

  document.body.appendChild(link)
  link.click()
  link.remove()

  window.URL.revokeObjectURL(blobUrl)
}

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')

    if (token) {
      config.headers['Authentication-Token'] = token
    }

    return config
  },
  (error) => Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      setAuthToken(null)

      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export const authAPI = {
  login: (credentials) =>
    apiClient.post('/login', credentials),

  registerStudent: (data) =>
    apiClient.post('/register', {
      ...data,
      role: 'student',
    }),

  registerCompany: (data) =>
    apiClient.post('/register', {
      ...data,
      role: 'company',
    }),
}

export const adminAPI = {
  getDashboardStats: () =>
    apiClient.get('/admin/dashboard'),

  getApplications: (params = {}) =>
    apiClient.get('/admin/applications', { params }),

  getCompanies: (params = {}) =>
    apiClient.get('/admin/companies', { params }),

  getCompanyDetails: (id) =>
    apiClient.get(`/admin/companies/${id}`),

  approveCompany: (id) =>
    apiClient.post(`/admin/companies/${id}/approve`),

  rejectCompany: (id) =>
    apiClient.post(`/admin/companies/${id}/reject`),

  blacklistCompany: (id) =>
    apiClient.post(`/admin/companies/${id}/blacklist`),

  activateCompany: (id) =>
    apiClient.post(`/admin/companies/${id}/activate`),

  getDrives: (params = {}) =>
    apiClient.get('/admin/drives', { params }),

  getDriveDetails: (id) =>
    apiClient.get(`/admin/drives/${id}`),

  approveDrive: (id) =>
    apiClient.post(`/admin/drives/${id}/approve`),

  rejectDrive: (id) =>
    apiClient.post(`/admin/drives/${id}/reject`),

  closeDrive: (id) =>
    apiClient.post(`/admin/drives/${id}/close`),

  sendDeadlineReminders() {
    return apiClient.post("/admin/reminders/send")
  },

  getStudents: (params = {}) =>
    apiClient.get('/admin/students', { params }),

  getStudentDetails: (id) =>
    apiClient.get(`/admin/students/${id}`),

  blacklistStudent: (id) =>
    apiClient.post(`/admin/students/${id}/blacklist`),

  activateStudent: (id) =>
    apiClient.post(`/admin/students/${id}/activate`),

  generateMonthlyReport: () =>
    apiClient.post('/admin/reports/monthly'),

  getTaskStatus: (taskId) =>
    apiClient.get(`/admin/tasks/${taskId}`),

  downloadStudentResume: (studentId, filename = 'resume.pdf') =>
    downloadAuthenticatedFile(
      `/admin/students/${studentId}/resume`,
      filename,
    ),
}

export const companyAPI = {
  getDashboard: () =>
    apiClient.get('/company/dashboard'),

  getProfile: () =>
    apiClient.get('/company/profile'),

  updateProfile: (data) =>
    apiClient.put('/company/profile', data),

  getDrives: () =>
    apiClient.get('/company/drives'),

  createDrive: (data) =>
    apiClient.post('/company/drives', data),

  getDrive: (id) =>
    apiClient.get(`/company/drives/${id}`),

  updateDrive: (id, data) =>
    apiClient.put(`/company/drives/${id}`, data),

  deleteDrive: (id) =>
    apiClient.delete(`/company/drives/${id}`),

  getDriveApplications: (driveId) =>
    apiClient.get(
      `/company/drives/${driveId}/applications`,
    ),

  getApplications: (params = {}) =>
    apiClient.get('/company/applications', { params }),

  getApplication: (id) =>
    apiClient.get(`/company/applications/${id}`),

  shortlistApplication: (id) =>
    apiClient.post(
      `/company/applications/${id}/shortlist`,
    ),

  selectApplication: (id) =>
    apiClient.post(
      `/company/applications/${id}/select`,
    ),

  rejectApplication: (id) =>
    apiClient.post(
      `/company/applications/${id}/reject`,
    ),

  scheduleInterview: (id, data) =>
    apiClient.post(
      `/company/applications/${id}/schedule-interview`,
      data,
    ),

  downloadStudentResume: (studentId, filename = 'resume.pdf') =>
    downloadAuthenticatedFile(
      `/company/students/${studentId}/resume`,
      filename,
    ),
}

export const studentAPI = {
  getDashboard: () =>
    apiClient.get('/student/dashboard'),

  getDrives: () =>
    apiClient.get('/student/drives'),

  getDrive: (id) =>
    apiClient.get(`/student/drives/${id}`),

  applyToDrive: (driveId) =>
    apiClient.post(`/student/drives/${driveId}/apply`),

  getApplications: () =>
    apiClient.get('/student/applications'),

  getApplication: (id) =>
    apiClient.get(`/student/applications/${id}`),

  deleteApplication: (id) =>
    apiClient.delete(`/student/applications/${id}`),

  getProfile: () =>
    apiClient.get('/student/profile'),

  updateProfile: (data) =>
    apiClient.put('/student/profile', data),

  getHistory: () =>
    apiClient.get('/student/history'),

  exportApplications: () =>
    apiClient.post('/student/export/applications'),

  getExportStatus: (taskId) =>
    apiClient.get(`/student/export/applications/${taskId}`),

  downloadExport: (filename) =>
    downloadAuthenticatedFile(
      `/student/export/download/${filename}`,
      filename,
    ),

  uploadResume: (file) => {
    const formData = new FormData()

    formData.append('resume', file)

    return apiClient.post('/student/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  downloadResume: (filename = 'resume.pdf') =>
    downloadAuthenticatedFile(
      '/student/resume',
      filename,
    ),
}

export default apiClient