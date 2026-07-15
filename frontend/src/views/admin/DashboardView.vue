<script setup>
import { onMounted, ref } from 'vue'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()

const loading = ref(true)
const refreshing = ref(false)
const generatingReport = ref(false)
const processingAction = ref(null)
const error = ref('')

const stats = ref({
  total_students: 0,
  total_companies: 0,
  total_drives: 0,
  total_applications: 0,
})

const pendingCompanies = ref([])
const pendingDrives = ref([])
const recentApplications = ref([])
const lastUpdated = ref(null)

const statisticCards = [
  {
    key: 'total_students',
    label: 'Students',
    description: 'Registered student profiles',
    icon: 'bi-mortarboard-fill',
    route: '/admin/students',
  },
  {
    key: 'total_companies',
    label: 'Companies',
    description: 'Registered company profiles',
    icon: 'bi-building-fill',
    route: '/admin/companies',
  },
  {
    key: 'total_drives',
    label: 'Placement drives',
    description: 'Total recruitment drives',
    icon: 'bi-briefcase-fill',
    route: '/admin/drives',
  },
  {
    key: 'total_applications',
    label: 'Applications',
    description: 'Student drive applications',
    icon: 'bi-file-earmark-person-fill',
    route: '/admin/applications',
  },
]

const formatNumber = (value) => {
  return Number(value || 0).toLocaleString('en-IN')
}

const formatDate = (value) => {
  if (!value) return 'Not available'

  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const formatDateTime = (value) => {
  if (!value) return 'Not available'

  return new Date(value).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formattedLastUpdated = () => {
  if (!lastUpdated.value) return 'Not updated'

  return lastUpdated.value.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusBadgeClass = (status) => {
  const classes = {
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
    rejected: 'bg-danger',
    pending: 'bg-warning',
    approved: 'bg-success',
    closed: 'bg-secondary',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const fetchDashboardData = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await adminAPI.getDashboardStats()
    const data = response.data || {}

    stats.value = {
      total_students: data.stats?.total_students || 0,
      total_companies: data.stats?.total_companies || 0,
      total_drives:
        data.stats?.total_drives ?? data.stats?.active_drives ?? 0,
      total_applications: data.stats?.total_applications || 0,
    }

    pendingCompanies.value = data.pending_companies || []
    pendingDrives.value = data.pending_drives || []
    recentApplications.value = data.recent_applications || []
    lastUpdated.value = new Date()
  } catch (requestError) {
    console.error('Unable to load admin dashboard:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load dashboard information.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const generateMonthlyReport = async () => {
  if (generatingReport.value) return

  generatingReport.value = true

  try {
    await adminAPI.generateMonthlyReport()

    messageStore.updateSuccessMessages(
      'Monthly report generation has started. The report will be emailed when ready.',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to generate the monthly report.',
    )
  } finally {
    generatingReport.value = false
  }
}

const approveCompany = async (companyId) => {
  processingAction.value = `company-${companyId}`

  try {
    await adminAPI.approveCompany(companyId)
    messageStore.updateSuccessMessages('Company approved successfully.')
    await fetchDashboardData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the company.',
    )
  } finally {
    processingAction.value = null
  }
}

const rejectCompany = async (companyId) => {
  const reason = window.prompt('Enter the reason for rejecting this company:')

  if (!reason?.trim()) return

  processingAction.value = `company-${companyId}`

  try {
    await adminAPI.rejectCompany(companyId, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages('Company registration rejected.')
    await fetchDashboardData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the company.',
    )
  } finally {
    processingAction.value = null
  }
}

const approveDrive = async (driveId) => {
  processingAction.value = `drive-${driveId}`

  try {
    await adminAPI.approveDrive(driveId)
    messageStore.updateSuccessMessages('Placement drive approved.')
    await fetchDashboardData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the placement drive.',
    )
  } finally {
    processingAction.value = null
  }
}

const rejectDrive = async (driveId) => {
  processingAction.value = `drive-${driveId}`

  try {
    await adminAPI.rejectDrive(driveId)
    messageStore.updateSuccessMessages('Placement drive rejected.')
    await fetchDashboardData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the placement drive.',
    )
  } finally {
    processingAction.value = null
  }
}

const sendingReminders = ref(false)

const sendDeadlineReminders = async () => {
  sendingReminders.value = true

  try {
    const response = await api.post('/admin/reminders/send')

    alert(
      response.data.message ||
      'Deadline reminder job started successfully.'
    )
  } catch (error) {
    console.error('Reminder error:', error)

    alert(
      error.response?.data?.message ||
      'Unable to start deadline reminder job.'
    )
  } finally {
    sendingReminders.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="dashboard-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Dashboard</h1>
        <p class="page-subtitle">
          Placement activity and pending administrative actions.
        </p>
      </div>

      <div class="header-actions">
        <span class="last-updated">
          Updated {{ formattedLastUpdated() }}
        </span>

        <button
          type="button"
          class="btn btn-outline-secondary"
          :disabled="refreshing"
          @click="fetchDashboardData(true)"
        >
          <span
            v-if="refreshing"
            class="spinner-border spinner-border-sm"
            aria-hidden="true"
          ></span>

          <i
            v-else
            class="bi bi-arrow-clockwise"
          ></i>

          Refresh
        </button>

        <button
          type="button"
          class="btn btn-primary"
          :disabled="generatingReport"
          @click="generateMonthlyReport"
        >
          <span
            v-if="generatingReport"
            class="spinner-border spinner-border-sm"
            aria-hidden="true"
          ></span>

          <i
            v-else
            class="bi bi-file-earmark-text"
          ></i>

          {{ generatingReport ? 'Generating...' : 'Monthly report' }}
        </button>
      </div>
    </header>

    <div
      v-if="loading"
      class="dashboard-state"
      aria-live="polite"
    >
      <div
        class="spinner-border spinner-border-sm"
        role="status"
      >
        <span class="visually-hidden">Loading dashboard</span>
      </div>

      <span>Loading placement data...</span>
    </div>

    <div
      v-else-if="error"
      class="dashboard-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Dashboard could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchDashboardData()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        class="statistics-grid"
        aria-label="Placement statistics"
      >
        <RouterLink
          v-for="item in statisticCards"
          :key="item.key"
          :to="item.route"
          class="statistic-card"
        >
          <div class="statistic-header">
            <span class="statistic-icon">
              <i :class="['bi', item.icon]"></i>
            </span>

            <i class="bi bi-arrow-up-right card-arrow"></i>
          </div>

          <strong class="statistic-value">
            {{ formatNumber(stats[item.key]) }}
          </strong>

          <span class="statistic-label">{{ item.label }}</span>
          <span class="statistic-description">{{ item.description }}</span>
        </RouterLink>
      </section>

      <section class="approval-grid">
        <article class="card approval-card">
          <div class="card-header section-header">
            <div>
              <div class="section-title-row">
                <h2>Company approvals</h2>

                <span class="badge bg-warning">
                  {{ pendingCompanies.length }}
                </span>
              </div>

              <p>Company registrations awaiting review.</p>
            </div>

            <RouterLink
              to="/admin/companies?status=pending"
              class="section-link"
            >
              View all
            </RouterLink>
          </div>

          <div
            v-if="pendingCompanies.length === 0"
            class="empty-state compact-empty-state"
          >
            <i class="bi bi-check-circle"></i>
            <span>No pending company registrations.</span>
          </div>

          <div
            v-else
            class="table-responsive"
          >
            <table class="table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>HR contact</th>
                  <th>Registered</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="company in pendingCompanies.slice(0, 5)"
                  :key="company.id"
                >
                  <td class="primary-cell">
                    {{ company.company_name }}
                  </td>

                  <td>{{ company.hr_name || 'Not provided' }}</td>
                  <td>{{ formatDate(company.created_at) }}</td>

                  <td>
                    <div class="table-actions">
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        :disabled="
                          processingAction === `company-${company.id}`
                        "
                        @click="rejectCompany(company.id)"
                      >
                        Reject
                      </button>

                      <button
                        type="button"
                        class="btn btn-primary btn-sm"
                        :disabled="
                          processingAction === `company-${company.id}`
                        "
                        @click="approveCompany(company.id)"
                      >
                        Approve
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="card approval-card">
          <div class="card-header section-header">
            <div>
              <div class="section-title-row">
                <h2>Drive approvals</h2>

                <span class="badge bg-warning">
                  {{ pendingDrives.length }}
                </span>
              </div>

              <p>Placement drives awaiting institute approval.</p>
            </div>

            <RouterLink
              to="/admin/drives?status=pending"
              class="section-link"
            >
              View all
            </RouterLink>
          </div>

          <div
            v-if="pendingDrives.length === 0"
            class="empty-state compact-empty-state"
          >
            <i class="bi bi-check-circle"></i>
            <span>No pending placement drives.</span>
          </div>

          <div
            v-else
            class="table-responsive"
          >
            <table class="table">
              <thead>
                <tr>
                  <th>Drive</th>
                  <th>Company</th>
                  <th>Created</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="drive in pendingDrives.slice(0, 5)"
                  :key="drive.id"
                >
                  <td class="primary-cell">
                    {{ drive.drive_name }}
                  </td>

                  <td>{{ drive.company_name }}</td>
                  <td>{{ formatDate(drive.created_at) }}</td>

                  <td>
                    <div class="table-actions">
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        :disabled="
                          processingAction === `drive-${drive.id}`
                        "
                        @click="rejectDrive(drive.id)"
                      >
                        Reject
                      </button>

                      <button
                        type="button"
                        class="btn btn-primary btn-sm"
                        :disabled="
                          processingAction === `drive-${drive.id}`
                        "
                        @click="approveDrive(drive.id)"
                      >
                        Approve
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section class="card applications-card">
        <div class="card-header section-header">
          <div>
            <h2>Recent applications</h2>
            <p>Latest student activity across placement drives.</p>
          </div>

          <RouterLink
            to="/admin/applications"
            class="section-link"
          >
            View all
          </RouterLink>
        </div>

        <div
          v-if="recentApplications.length === 0"
          class="empty-state"
        >
          <i class="bi bi-inbox"></i>
          <span>No applications have been recorded yet.</span>
        </div>

        <div
          v-else
          class="table-responsive"
        >
          <table class="table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Company</th>
                <th>Drive</th>
                <th>Status</th>
                <th>Applied</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="application in recentApplications"
                :key="application.id"
              >
                <td class="primary-cell">
                  {{ application.student_name }}
                </td>

                <td>{{ application.company_name }}</td>
                <td>{{ application.drive_name }}</td>

                <td>
                  <span
                    class="badge text-capitalize"
                    :class="getStatusBadgeClass(application.status)"
                  >
                    {{ application.status }}
                  </span>
                </td>

                <td>{{ formatDateTime(application.applied_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
}

.dashboard-title {
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.last-updated {
  margin-right: 4px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.dashboard-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 320px;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.error-state {
  align-items: flex-start;
  min-height: auto;
  padding: 20px;
  background: #fff1f0;
  border: 1px solid #f5cfcc;
  border-radius: var(--border-radius);
}

.error-state > i {
  color: var(--color-danger);
  font-size: 1.1rem;
}

.error-state strong {
  color: var(--color-danger);
}

.error-state p {
  margin: 4px 0 0;
}

.error-state .btn {
  margin-left: auto;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.statistic-card {
  display: flex;
  flex-direction: column;
  min-height: 190px;
  padding: 20px;
  color: inherit;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition:
    border-color var(--transition),
    box-shadow var(--transition);
}

.statistic-card:hover {
  color: inherit;
  border-color: #cbd2dc;
  box-shadow: var(--shadow);
}

.statistic-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: auto;
}

.statistic-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.card-arrow {
  color: #a0a8b5;
  font-size: 0.85rem;
}

.statistic-value {
  margin-top: 26px;
  color: var(--color-primary);
  font-size: 2rem;
  font-weight: 650;
  letter-spacing: -0.04em;
  line-height: 1;
}

.statistic-label {
  margin-top: 9px;
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 600;
}

.statistic-description {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.approval-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.approval-card,
.applications-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.section-header p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.section-link {
  flex-shrink: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.primary-cell {
  color: var(--color-primary);
  font-weight: 600;
}

.table-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.compact-empty-state {
  min-height: 220px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
}

.empty-state i {
  color: #a7afbb;
  font-size: 1.5rem;
}

@media (max-width: 1199.98px) {
  .statistics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .approval-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767.98px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .last-updated {
    width: 100%;
  }

  .statistics-grid {
    grid-template-columns: 1fr;
  }

  .statistic-card {
    min-height: 170px;
  }
}

@media (max-width: 575.98px) {
  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .section-header {
    gap: 12px;
  }
}
</style>