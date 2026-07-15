<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

const loading = ref(true)
const refreshing = ref(false)
const deleting = ref(false)
const error = ref('')

const drive = ref({})
const applications = ref([])
const companyProfile = ref({})

const canEdit = computed(
  () =>
    drive.value.status === 'pending' &&
    companyProfile.value.approval_status === 'approved' &&
    !companyProfile.value.is_blacklisted,
)

const statistics = computed(() => {
  const result = {
    total: applications.value.length,
    applied: 0,
    shortlisted: 0,
    selected: 0,
    rejected: 0,
  }

  applications.value.forEach((application) => {
    const status = application.status?.toLowerCase()

    if (Object.hasOwn(result, status)) {
      result[status] += 1
    }
  })

  return result
})

const summaryCards = computed(() => [
  {
    label: 'Applications',
    value: statistics.value.total,
    icon: 'bi-file-earmark-text',
  },
  {
    label: 'Shortlisted',
    value: statistics.value.shortlisted,
    icon: 'bi-person-check',
  },
  {
    label: 'Selected',
    value: statistics.value.selected,
    icon: 'bi-check-circle',
  },
  {
    label: 'Rejected',
    value: statistics.value.rejected,
    icon: 'bi-x-circle',
  },
])

const recentApplications = computed(() =>
  applications.value.slice(0, 5),
)

const formatDate = (value) => {
  if (!value) return 'Not available'

  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const formatDateTime = (value) => {
  if (!value) return 'Not scheduled'

  return new Date(value).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatStatus = (status) => {
  if (!status) return 'Unknown'

  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (status) => {
  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
    closed: 'bg-secondary',
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const statusNotice = computed(() => {
  const notices = {
    pending: {
      icon: 'bi-clock',
      title: 'Pending institute approval',
      message:
        'Students cannot view or apply to this placement drive until it is approved.',
    },
    approved: {
      icon: 'bi-check-circle',
      title: 'Drive approved',
      message:
        'This placement drive is visible to eligible students.',
    },
    rejected: {
      icon: 'bi-x-circle',
      title: 'Drive rejected',
      message:
        'The institute placement cell has not approved this placement drive.',
    },
    closed: {
      icon: 'bi-archive',
      title: 'Drive closed',
      message:
        'This placement drive is closed and no longer accepts applications.',
    },
  }

  return notices[drive.value.status] || {
    icon: 'bi-info-circle',
    title: 'Drive status unavailable',
    message: 'The current placement drive status is unavailable.',
  }
})

const fetchData = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const [driveResponse, applicationsResponse, profileResponse] =
      await Promise.all([
        companyAPI.getDrive(driveId),
        companyAPI.getDriveApplications(driveId),
        companyAPI.getProfile(),
      ])

    drive.value = driveResponse.data.drive || {}
    applications.value =
      applicationsResponse.data.applications || []
    companyProfile.value = profileResponse.data.profile || {}
  } catch (requestError) {
    console.error('Unable to load drive details:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load placement drive details.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const viewApplications = () => {
  router.push({
    path: '/company/applications',
    query: {
      drive: driveId,
    },
  })
}

const viewApplication = (applicationId) => {
  router.push(`/company/applications/${applicationId}`)
}

const deleteDrive = async () => {
  if (!canEdit.value) return

  const confirmed = window.confirm(
    'Delete this pending placement drive? This action cannot be undone.',
  )

  if (!confirmed) return

  deleting.value = true

  try {
    await companyAPI.deleteDrive(driveId)

    messageStore.updateSuccessMessages(
      'Placement drive deleted successfully.',
    )

    router.push('/company/drives')
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to delete the placement drive.',
    )
  } finally {
    deleting.value = false
  }
}

const goBack = () => {
  router.push('/company/drives')
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="drive-detail-page fade-in">
    <header class="page-header">
      <div>
        <button
          type="button"
          class="back-link"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Placement drives
        </button>

        <div class="title-row">
          <h1 class="dashboard-title">
            {{ drive.drive_name || 'Placement drive' }}
          </h1>

          <span
            v-if="!loading"
            class="badge"
            :class="getStatusClass(drive.status)"
          >
            {{ formatStatus(drive.status) }}
          </span>
        </div>

        <p class="page-subtitle">
          {{ drive.job_title || 'Review placement drive details.' }}
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn btn-outline-secondary"
          :disabled="refreshing || loading"
          @click="fetchData(true)"
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
          Loading placement drive
        </span>
      </div>

      <span>Loading placement drive...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Placement drive could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchData()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        class="status-notice"
        :class="`status-${drive.status}`"
      >
        <span class="notice-icon">
          <i :class="['bi', statusNotice.icon]"></i>
        </span>

        <div>
          <strong>{{ statusNotice.title }}</strong>
          <p>{{ statusNotice.message }}</p>
        </div>
      </section>

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
              {{ item.value.toLocaleString('en-IN') }}
            </strong>

            <span>{{ item.label }}</span>
          </div>
        </article>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <article class="card">
            <div class="card-header">
              <div>
                <h2>Job description</h2>
                <p>Role and recruitment information.</p>
              </div>
            </div>

            <div class="card-body">
              <p class="description-text">
                {{
                  drive.job_description ||
                  'No job description has been provided.'
                }}
              </p>
            </div>
          </article>

          <article class="card applications-card">
            <div class="card-header section-header">
              <div>
                <h2>Recent applications</h2>

                <p>
                  Latest students who applied to this placement drive.
                </p>
              </div>

              <button
                type="button"
                class="section-link"
                @click="viewApplications"
              >
                View all
              </button>
            </div>

            <div
              v-if="recentApplications.length === 0"
              class="empty-state"
            >
              <i class="bi bi-inbox"></i>
              <strong>No applications yet</strong>

              <span>
                Student applications will appear here once submitted.
              </span>
            </div>

            <div
              v-else
              class="table-responsive"
            >
              <table class="table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Branch</th>
                    <th>CGPA</th>
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
                      <div class="student-cell">
                        <span class="student-avatar">
                          {{
                            application.student_name
                              ?.charAt(0)
                              .toUpperCase() || 'S'
                          }}
                        </span>

                        <div>
                          <strong>
                            {{ application.student_name }}
                          </strong>

                          <span>
                            {{
                              application.student_roll ||
                              'Roll number unavailable'
                            }}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>
                      {{
                        application.student_branch ||
                        'Not provided'
                      }}
                    </td>

                    <td>
                      {{
                        application.student_cgpa !== null &&
                        application.student_cgpa !== undefined
                          ? Number(
                              application.student_cgpa,
                            ).toFixed(2)
                          : '—'
                      }}
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
                        Review
                        <i
                          class="bi bi-arrow-up-right ms-1"
                        ></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </div>

        <aside class="side-column">
          <article class="card">
            <div class="card-header">
              <h2>Drive information</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row">
                <span>Drive ID</span>
                <strong>#{{ drive.id }}</strong>
              </div>

              <div class="detail-row">
                <span>Drive name</span>
                <strong>{{ drive.drive_name }}</strong>
              </div>

              <div class="detail-row">
                <span>Job title</span>
                <strong>{{ drive.job_title }}</strong>
              </div>

              <div class="detail-row">
                <span>Created</span>
                <strong>
                  {{ formatDate(drive.created_at) }}
                </strong>
              </div>

              <div
                v-if="drive.approved_at"
                class="detail-row"
              >
                <span>Approved</span>
                <strong>
                  {{ formatDate(drive.approved_at) }}
                </strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Eligibility</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row">
                <span>Minimum CGPA</span>

                <strong>
                  {{
                    drive.min_cgpa !== null &&
                    drive.min_cgpa !== undefined
                      ? Number(drive.min_cgpa).toFixed(2)
                      : 'No restriction'
                  }}
                </strong>
              </div>

              <div class="detail-row">
                <span>Allowed branches</span>

                <strong>
                  {{ drive.allowed_branches || 'All branches' }}
                </strong>
              </div>

              <div class="detail-row stacked-row">
                <span>Additional criteria</span>

                <strong>
                  {{
                    drive.eligibility_criteria ||
                    'No additional criteria'
                  }}
                </strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Schedule</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row stacked-row">
                <span>Application deadline</span>

                <strong>
                  {{
                    formatDateTime(
                      drive.application_deadline,
                    )
                  }}
                </strong>
              </div>

              <div class="detail-row stacked-row">
                <span>Drive date</span>

                <strong>
                  {{ formatDateTime(drive.drive_date) }}
                </strong>
              </div>
            </div>
          </article>

          <article
            v-if="canEdit"
            class="danger-card"
          >
            <div>
              <strong>Delete placement drive</strong>

              <p>
                Pending drives can be permanently deleted before
                institute approval.
              </p>
            </div>

            <button
              type="button"
              class="btn btn-outline-danger btn-sm"
              :disabled="deleting"
              @click="deleteDrive"
            >
              {{
                deleting
                  ? 'Deleting...'
                  : 'Delete drive'
              }}
            </button>
          </article>
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

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 18px;
  padding: 0;
  color: var(--color-text-muted);
  background: transparent;
  border: 0;
  font-size: 0.8rem;
  font-weight: 600;
}

.back-link:hover {
  color: var(--color-primary);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
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

.status-notice {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  margin-bottom: 20px;
  padding: 15px 17px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.notice-icon {
  color: var(--color-primary);
}

.status-pending {
  background: #fff9e8;
  border-color: #eadcae;
}

.status-rejected {
  background: #fff1f0;
  border-color: #f5cfcc;
}

.status-approved {
  background: #edf8f1;
  border-color: #cbe7d5;
}

.status-notice strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.status-notice p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.76rem;
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

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.6fr);
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

.description-text {
  margin: 0;
  color: var(--color-text);
  font-size: 0.84rem;
  line-height: 1.75;
  white-space: pre-line;
}

.applications-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.student-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 170px;
}

.student-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
}

.student-cell strong,
.student-cell span {
  display: block;
}

.student-cell strong {
  color: var(--color-primary);
  font-size: 0.82rem;
}

.student-cell div > span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.detail-list {
  padding-top: 7px;
  padding-bottom: 7px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-row > span {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.detail-row strong {
  overflow-wrap: anywhere;
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
  text-align: right;
}

.stacked-row {
  flex-direction: column;
  gap: 5px;
}

.stacked-row strong {
  text-align: left;
}

.danger-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 17px;
  background: #fff8f7;
  border: 1px solid #f1d5d2;
  border-radius: var(--border-radius);
}

.danger-card strong {
  color: var(--color-danger);
  font-size: 0.8rem;
}

.danger-card p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.7rem;
  line-height: 1.5;
}

.empty-state {
  min-height: 250px;
}

.empty-state strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.empty-state span {
  font-size: 0.8rem;
}

@media (max-width: 1199.98px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
}

@media (max-width: 991.98px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .summary-grid,
  .side-column {
    grid-template-columns: 1fr;
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

  .danger-card {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>