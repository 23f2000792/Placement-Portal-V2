<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const refreshing = ref(false)
const exporting = ref(false)
const error = ref('')

const student = ref({})
const statistics = ref({})
const upcomingDeadlines = ref([])
const recentApplications = ref([])

const studentName = computed(
  () =>
    student.value.full_name ||
    student.value.name ||
    'Student',
)

const firstName = computed(
  () => studentName.value.trim().split(/\s+/)[0],
)

const summaryCards = computed(() => [
  {
    label: 'Applications',
    value: statistics.value.total_applications || 0,
    icon: 'bi-briefcase-fill',
  },
  {
    label: 'Applied',
    value: statistics.value.pending || 0,
    icon: 'bi-send-fill',
  },
  {
    label: 'Shortlisted',
    value: statistics.value.shortlisted || 0,
    icon: 'bi-person-check-fill',
  },
  {
    label: 'Selected',
    value: statistics.value.selected || 0,
    icon: 'bi-check-circle-fill',
  },
])

const formatDate = (value) => {
  if (!value) return 'Not available'

  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const formatStatus = (status) => {
  if (!status) return 'Unknown'

  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (status) => {
  const classes = {
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
    rejected: 'bg-danger',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const getDaysLeft = (deadline) => {
  if (!deadline) return 0

  const difference =
    new Date(deadline).getTime() - new Date().getTime()

  return Math.max(
    0,
    Math.ceil(difference / (1000 * 60 * 60 * 24)),
  )
}

const getDeadlineLabel = (deadline) => {
  const days = getDaysLeft(deadline)

  if (days === 0) return 'Today'
  if (days === 1) return '1 day left'

  return `${days} days left`
}

const getDeadlineClass = (deadline) => {
  const days = getDaysLeft(deadline)

  if (days <= 1) return 'deadline-urgent'
  if (days <= 3) return 'deadline-soon'

  return ''
}

const fetchDashboard = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await studentAPI.getDashboard()

    student.value = response.data.student || {}
    statistics.value = response.data.statistics || {}
    upcomingDeadlines.value =
      response.data.upcoming_deadlines || []
    recentApplications.value =
      response.data.recent_applications || []
  } catch (requestError) {
    console.error(
      'Unable to load student dashboard:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load student dashboard.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const waitForExport = async (taskId) => {
  while (true) {
    const response = await studentAPI.getExportStatus(taskId)
    const state = response.data.state

    if (state === 'SUCCESS') {
      return response.data.result
    }

    if (state === 'FAILURE') {
      throw new Error(
        response.data.error || 'Application export failed.',
      )
    }

    await new Promise((resolve) => {
      setTimeout(resolve, 1000)
    })
  }
}

const exportApplications = async () => {
  if (exporting.value) return

  exporting.value = true

  try {
    const response = await studentAPI.exportApplications()

    const result = await waitForExport(
      response.data.task_id,
    )

    await studentAPI.downloadExport(result.filename)

    messageStore.updateSuccessMessages(
      `Downloaded ${result.application_count} application(s).`,
    )
  } catch (requestError) {
    console.error('Application export failed:', requestError)

    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        requestError.message ||
        'Unable to export application history.',
    )
  } finally {
    exporting.value = false
  }
}

const viewDrive = (id) => {
  router.push(`/student/drives/${id}`)
}

const viewApplication = (id) => {
  router.push(`/student/applications/${id}`)
}

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="student-dashboard fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">
          Welcome back, {{ firstName }}
        </h1>

        <p class="page-subtitle">
          Track applications and upcoming placement deadlines.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn btn-outline-secondary"
          :disabled="refreshing || loading"
          @click="fetchDashboard(true)"
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
          :disabled="exporting"
          @click="exportApplications"
        >
          <span
            v-if="exporting"
            class="spinner-border spinner-border-sm"
            aria-hidden="true"
          ></span>

          <i
            v-else
            class="bi bi-download"
          ></i>

          {{
            exporting
              ? 'Preparing CSV...'
              : 'Export applications'
          }}
        </button>
      </div>
    </header>

    <div
      v-if="loading"
      class="page-state"
      aria-live="polite"
    >
      <div
        class="spinner-border spinner-border-sm"
        role="status"
      >
        <span class="visually-hidden">
          Loading student dashboard
        </span>
      </div>

      <span>Loading your placement dashboard...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Dashboard could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchDashboard()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        class="summary-grid"
        aria-label="Application statistics"
      >
        <article
          v-for="item in summaryCards"
          :key="item.label"
          class="summary-card"
        >
          <span class="summary-icon">
            <i :class="['bi', item.icon]"></i>
          </span>

          <div>
            <strong>
              {{ Number(item.value).toLocaleString('en-IN') }}
            </strong>

            <span>{{ item.label }}</span>
          </div>
        </article>
      </section>

      <section class="dashboard-grid">
        <div class="main-column">
          <article class="card">
            <div class="card-header section-header">
              <div>
                <h2>Upcoming deadlines</h2>

                <p>
                  Approved placement drives closing within seven days.
                </p>
              </div>

              <button
                type="button"
                class="section-link"
                @click="router.push('/student/drives')"
              >
                View all drives
              </button>
            </div>

            <div
              v-if="upcomingDeadlines.length === 0"
              class="empty-state"
            >
              <i class="bi bi-calendar-check"></i>

              <strong>No upcoming deadlines</strong>

              <span>
                There are no approved drives closing in the next
                seven days.
              </span>
            </div>

            <div
              v-else
              class="deadline-list"
            >
              <button
                v-for="drive in upcomingDeadlines"
                :key="drive.id"
                type="button"
                class="deadline-item"
                @click="viewDrive(drive.id)"
              >
                <span class="company-icon">
                  <i class="bi bi-building"></i>
                </span>

                <span class="deadline-content">
                  <strong>{{ drive.drive_name }}</strong>

                  <span>{{ drive.company_name }}</span>
                </span>

                <span
                  class="deadline-meta"
                  :class="getDeadlineClass(drive.deadline)"
                >
                  <strong>
                    {{ getDeadlineLabel(drive.deadline) }}
                  </strong>

                  <span>
                    {{ formatDate(drive.deadline) }}
                  </span>
                </span>

                <i class="bi bi-chevron-right item-arrow"></i>
              </button>
            </div>
          </article>

          <article class="card recent-card">
            <div class="card-header section-header">
              <div>
                <h2>Recent applications</h2>

                <p>
                  Latest placement applications from your account.
                </p>
              </div>

              <button
                type="button"
                class="section-link"
                @click="
                  router.push('/student/applications')
                "
              >
                View all
              </button>
            </div>

            <div
              v-if="recentApplications.length === 0"
              class="empty-state"
            >
              <i class="bi bi-file-earmark-text"></i>

              <strong>No applications yet</strong>

              <span>
                Browse approved placement drives and submit your first
                application.
              </span>

              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="router.push('/student/drives')"
              >
                Browse drives
              </button>
            </div>

            <div
              v-else
              class="table-responsive"
            >
              <table class="table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Placement drive</th>
                    <th>Applied</th>
                    <th>Status</th>
                    <th class="text-end">Action</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="application in recentApplications"
                    :key="application.id"
                  >
                    <td>
                      <div class="company-cell">
                        <span class="company-avatar">
                          {{
                            application.company_name
                              ?.charAt(0)
                              .toUpperCase() || 'C'
                          }}
                        </span>

                        <strong>
                          {{ application.company_name }}
                        </strong>
                      </div>
                    </td>

                    <td>
                      {{ application.drive_name }}
                    </td>

                    <td>
                      {{ formatDate(application.applied_at) }}
                    </td>

                    <td>
                      <span
                        class="badge"
                        :class="
                          getStatusClass(application.status)
                        "
                      >
                        {{ formatStatus(application.status) }}
                      </span>
                    </td>

                    <td class="text-end">
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        @click="
                          viewApplication(application.id)
                        "
                      >
                        View
                        <i class="bi bi-arrow-up-right ms-1"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </div>

        <aside class="side-column">
          <section class="student-card">
            <span class="student-avatar">
              {{
                studentName
                  .charAt(0)
                  .toUpperCase()
              }}
            </span>

            <h2>{{ studentName }}</h2>

            <p>
              {{
                student.roll_number ||
                'Student profile'
              }}
            </p>

            <div class="student-meta">
              <div>
                <span>Branch</span>

                <strong>
                  {{ student.branch || 'Not provided' }}
                </strong>
              </div>

              <div>
                <span>CGPA</span>

                <strong>
                  {{
                    student.cgpa !== null &&
                    student.cgpa !== undefined
                      ? Number(student.cgpa).toFixed(2)
                      : '—'
                  }}
                </strong>
              </div>
            </div>

            <button
              type="button"
              class="profile-link"
              @click="router.push('/student/profile')"
            >
              Manage profile
              <i class="bi bi-arrow-right"></i>
            </button>
          </section>
        </aside>
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
  gap: 8px;
}

.header-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.page-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 11px;
  min-height: 320px;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.error-state {
  align-items: flex-start;
  justify-content: flex-start;
  min-height: auto;
  padding: 18px;
  background: #fff1f0;
  border: 1px solid #f5cfcc;
  border-radius: var(--border-radius);
}

.error-state > i,
.error-state strong {
  color: var(--color-danger);
}

.error-state p {
  margin: 4px 0 0;
}

.error-state .btn {
  margin-left: auto;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.summary-icon .bi {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 100%;
  height: 100%;

  margin: 0;
  padding: 0;

  color: inherit;
  background: transparent;

  font-size: 1.15rem;
  line-height: 1;
}

.summary-icon .bi::before {
  display: block;
  margin: 0;
  line-height: 1;
  vertical-align: middle;
}

.summary-card strong,
.summary-card span {
  display: block;
}

.summary-card strong {
  color: var(--color-primary);
  font-size: 1.35rem;
  font-weight: 650;
}

.summary-card div > span {
  margin-top: 2px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(270px, 0.55fr);
  gap: 20px;
  align-items: start;
}

.main-column,
.side-column {
  min-width: 0;
}

.card-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.card-header p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.deadline-list {
  display: flex;
  flex-direction: column;
}

.deadline-item {
  display: flex;
  align-items: center;
  gap: 13px;
  width: 100%;
  padding: 15px 18px;
  color: inherit;
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.deadline-item:last-child {
  border-bottom: 0;
}

.deadline-item:hover {
  background: var(--color-surface-muted);
}

.company-icon,
.company-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.deadline-content {
  flex: 1;
  min-width: 0;
}

.deadline-content strong,
.deadline-content span,
.deadline-meta strong,
.deadline-meta span {
  display: block;
}

.deadline-content strong {
  color: var(--color-primary);
  font-size: 0.82rem;
}

.deadline-content span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.deadline-meta {
  min-width: 100px;
  text-align: right;
}

.deadline-meta strong {
  color: var(--color-text);
  font-size: 0.75rem;
}

.deadline-meta span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.deadline-urgent strong {
  color: var(--color-danger);
}

.deadline-soon strong {
  color: #9a6700;
}

.item-arrow {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.recent-card {
  margin-bottom: 0;
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 150px;
}

.company-cell strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.student-card {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 25px 20px 20px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: var(--border-radius);
  text-align: center;
}

.student-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 14px;
  color: var(--color-primary);
  background: #ffffff;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
}

.student-card h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 650;
}

.student-card > p {
  margin: 5px 0 19px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.73rem;
}

.student-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.student-meta > div {
  padding: 13px 8px;
}

.student-meta > div + div {
  border-left: 1px solid rgba(255, 255, 255, 0.12);
}

.student-meta span,
.student-meta strong {
  display: block;
}

.student-meta span {
  color: rgba(255, 255, 255, 0.48);
  font-size: 0.66rem;
}

.student-meta strong {
  margin-top: 4px;
  color: #ffffff;
  font-size: 0.76rem;
}

.profile-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 17px;
  padding: 0;
  color: rgba(255, 255, 255, 0.75);
  background: transparent;
  border: 0;
  font-size: 0.75rem;
  font-weight: 600;
}

.progress-list {
  padding-top: 7px;
  padding-bottom: 7px;
}

.progress-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 0;
  border-bottom: 1px solid var(--color-border);
}

.progress-row:last-child {
  border-bottom: 0;
}

.progress-row span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.progress-row strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.info-card > i {
  color: var(--color-accent);
}

.info-card strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.info-card p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
  line-height: 1.55;
}

.empty-state {
  min-height: 250px;
}

.empty-state strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.empty-state span {
  max-width: 430px;
  font-size: 0.78rem;
}

@media (max-width: 991.98px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .student-card {
    grid-column: 1 / -1;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .summary-grid,
  .side-column {
    grid-template-columns: 1fr;
  }

  .deadline-meta {
    display: none;
  }
}

@media (max-width: 575.98px) {
  .header-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions .btn {
    justify-content: center;
  }
}
</style>