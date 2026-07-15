<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const processingAction = ref(false)

const drive = ref({})
const applications = ref([])

const applicationStats = computed(() => {
  const stats = {
    applied: 0,
    shortlisted: 0,
    selected: 0,
    rejected: 0,
  }

  applications.value.forEach((application) => {
    if (Object.hasOwn(stats, application.status)) {
      stats[application.status] += 1
    }
  })

  return stats
})

const daysRemaining = computed(() => {
  if (!drive.value.application_deadline) return 'No deadline'

  const deadline = new Date(drive.value.application_deadline)
  const today = new Date()

  deadline.setHours(23, 59, 59, 999)

  const difference = deadline.getTime() - today.getTime()
  const days = Math.ceil(difference / (1000 * 60 * 60 * 24))

  if (days < 0) return 'Expired'
  if (days === 0) return 'Today'

  return `${days} ${days === 1 ? 'day' : 'days'} left`
})

const applicationSummary = computed(() => [
  {
    label: 'Applied',
    value: applicationStats.value.applied,
    icon: 'bi-file-earmark-arrow-up-fill',
  },
  {
    label: 'Shortlisted',
    value: applicationStats.value.shortlisted,
    icon: 'bi-person-check-fill',
  },
  {
    label: 'Selected',
    value: applicationStats.value.selected,
    icon: 'bi-award-fill',
  },
  {
    label: 'Rejected',
    value: applicationStats.value.rejected,
    icon: 'bi-person-x-fill',
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

const getDriveStatusClass = (status) => {
  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
    closed: 'bg-secondary',
  }

  return classes[status] || 'bg-secondary'
}

const getApplicationStatusClass = (status) => {
  const classes = {
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
    rejected: 'bg-danger',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const fetchDriveDetails = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await adminAPI.getDriveDetails(driveId)

    drive.value = response.data.drive || {}
    applications.value = response.data.applications || []
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

const approveDrive = async () => {
  if (!window.confirm('Approve this placement drive?')) return

  processingAction.value = true

  try {
    await adminAPI.approveDrive(driveId)

    messageStore.updateSuccessMessages(
      'Placement drive approved successfully.',
    )

    await fetchDriveDetails(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the placement drive.',
    )
  } finally {
    processingAction.value = false
  }
}

const rejectDrive = async () => {
  if (!window.confirm('Reject this placement drive?')) return

  processingAction.value = true

  try {
    await adminAPI.rejectDrive(driveId)
    messageStore.updateSuccessMessages('Placement drive rejected.')
    await fetchDriveDetails(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the placement drive.',
    )
  } finally {
    processingAction.value = false
  }
}

const closeDrive = async () => {
  if (
    !window.confirm(
      'Close this placement drive? Students will no longer be able to apply.',
    )
  ) {
    return
  }

  processingAction.value = true

  try {
    await adminAPI.closeDrive(driveId)
    messageStore.updateSuccessMessages('Placement drive closed.')
    await fetchDriveDetails(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to close the placement drive.',
    )
  } finally {
    processingAction.value = false
  }
}

const goBack = () => {
  router.push('/admin/drives')
}

const viewAllApplications = () => {
  router.push({
    path: '/admin/applications',
    query: {
      drive: driveId,
    },
  })
}

onMounted(() => {
  fetchDriveDetails()
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

        <h1 class="dashboard-title">Drive details</h1>

        <p class="page-subtitle">
          Review recruitment requirements, eligibility and application activity.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary refresh-button"
        :disabled="refreshing || loading"
        @click="fetchDriveDetails(true)"
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
        <span class="visually-hidden">Loading drive details</span>
      </div>

      <span>Loading placement drive details...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Drive details could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchDriveDetails()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section class="drive-overview">
        <div class="drive-identity">
          <span class="drive-icon">
            <i class="bi bi-briefcase"></i>
          </span>

          <div class="identity-copy">
            <div class="drive-title-row">
              <h2>{{ drive.drive_name }}</h2>

              <span
                class="badge"
                :class="getDriveStatusClass(drive.status)"
              >
                {{ formatStatus(drive.status) }}
              </span>
            </div>

            <p>{{ drive.job_title }}</p>

            <RouterLink
              :to="`/admin/companies/${drive.company_id}`"
              class="company-link"
            >
              {{ drive.company_name }}
              <i class="bi bi-arrow-up-right"></i>
            </RouterLink>

            <span class="drive-id">Drive ID #{{ drive.id }}</span>
          </div>

          <div class="drive-actions">
            <template v-if="drive.status === 'pending'">
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="processingAction"
                @click="rejectDrive"
              >
                Reject
              </button>

              <button
                type="button"
                class="btn btn-primary"
                :disabled="processingAction"
                @click="approveDrive"
              >
                <span
                  v-if="processingAction"
                  class="spinner-border spinner-border-sm"
                  aria-hidden="true"
                ></span>

                Approve drive
              </button>
            </template>

            <button
              v-else-if="drive.status === 'approved'"
              type="button"
              class="btn btn-outline-secondary"
              :disabled="processingAction"
              @click="closeDrive"
            >
              <i class="bi bi-stop-circle"></i>
              Close drive
            </button>
          </div>
        </div>
      </section>

      <section class="content-grid">
        <div class="primary-column">
          <article class="card">
            <div class="card-header">
              <h2>Job description</h2>
            </div>

            <div class="card-body description-content">
              <p>
                {{ drive.job_description || 'No job description provided.' }}
              </p>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Eligibility criteria</h2>
            </div>

            <div class="card-body">
              <div class="criteria-grid">
                <div class="criteria-item">
                  <span>Minimum CGPA</span>
                  <strong>
                    {{ drive.min_cgpa || 'No minimum specified' }}
                  </strong>
                </div>

                <div class="criteria-item">
                  <span>Application deadline</span>
                  <strong>{{ formatDate(drive.application_deadline) }}</strong>
                </div>

                <div class="criteria-item">
                  <span>Deadline status</span>
                  <strong>{{ daysRemaining }}</strong>
                </div>

                <div class="criteria-item">
                  <span>Drive date</span>
                  <strong>{{ formatDate(drive.drive_date) }}</strong>
                </div>
              </div>

              <div class="branches-section">
                <span class="detail-label">Allowed branches</span>

                <div
                  v-if="drive.allowed_branches"
                  class="branch-list"
                >
                  <span
                    v-for="branch in drive.allowed_branches
                      .split(',')
                      .map((item) => item.trim())
                      .filter(Boolean)"
                    :key="branch"
                    class="branch-chip"
                  >
                    {{ branch }}
                  </span>
                </div>

                <p v-else>All branches are eligible.</p>
              </div>

              <div
                v-if="drive.eligibility_criteria"
                class="additional-criteria"
              >
                <span class="detail-label">Additional criteria</span>
                <p>{{ drive.eligibility_criteria }}</p>
              </div>
            </div>
          </article>

          <article class="card applications-card">
            <div class="card-header section-header">
              <div>
                <div class="section-title-row">
                  <h2>Applications</h2>

                  <span class="badge bg-primary">
                    {{ applications.length }}
                  </span>
                </div>

                <p>Student applications submitted for this drive.</p>
              </div>

              <button
                v-if="applications.length > 5"
                type="button"
                class="section-link"
                @click="viewAllApplications"
              >
                View all
              </button>
            </div>

            <div
              v-if="applications.length === 0"
              class="empty-state"
            >
              <i class="bi bi-inbox"></i>
              <strong>No applications received</strong>
              <span>Student applications will appear here.</span>
            </div>

            <template v-else>
              <div class="application-summary">
                <div
                  v-for="item in applicationSummary"
                  :key="item.label"
                  class="summary-item"
                >
                  <strong>{{ item.value }}</strong>
                  <span>{{ item.label }}</span>
                </div>
              </div>

              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Roll number</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Status</th>
                      <th>Applied</th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr
                      v-for="application in applications.slice(0, 5)"
                      :key="application.id"
                    >
                      <td class="primary-cell">
                        {{ application.student_name }}
                      </td>

                      <td>{{ application.student_roll }}</td>
                      <td>{{ application.student_branch }}</td>
                      <td>{{ application.student_cgpa }}</td>

                      <td>
                        <span
                          class="badge text-capitalize"
                          :class="
                            getApplicationStatusClass(application.status)
                          "
                        >
                          {{ application.status }}
                        </span>
                      </td>

                      <td>{{ formatDate(application.applied_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
          </article>
        </div>

        <aside class="secondary-column">
          <article class="card">
            <div class="card-header">
              <h2>Drive information</h2>
            </div>

            <div class="card-body details-list">
              <div class="detail-row">
                <span>Company</span>

                <RouterLink
                  :to="`/admin/companies/${drive.company_id}`"
                >
                  {{ drive.company_name }}
                </RouterLink>
              </div>

              <div class="detail-row">
                <span>Job title</span>
                <strong>{{ drive.job_title }}</strong>
              </div>

              <div class="detail-row">
                <span>Created</span>
                <strong>{{ formatDate(drive.created_at) }}</strong>
              </div>

              <div
                v-if="drive.approved_at"
                class="detail-row"
              >
                <span>Approved</span>
                <strong>{{ formatDate(drive.approved_at) }}</strong>
              </div>

              <div
                v-if="drive.approved_by"
                class="detail-row"
              >
                <span>Approved by</span>
                <strong>{{ drive.approved_by_name || 'Admin' }}</strong>
              </div>
            </div>
          </article>

          <article class="status-card">
            <span class="detail-label">Current drive status</span>

            <strong>{{ formatStatus(drive.status) }}</strong>

            <p v-if="drive.status === 'pending'">
              This drive is awaiting institute review.
            </p>

            <p v-else-if="drive.status === 'approved'">
              Students can view and apply to this drive while eligible.
            </p>

            <p v-else-if="drive.status === 'closed'">
              Applications are no longer accepted for this drive.
            </p>

            <p v-else-if="drive.status === 'rejected'">
              This drive was not approved by the placement cell.
            </p>
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

.dashboard-title {
  margin-bottom: 0;
}

.refresh-button {
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

.drive-overview {
  margin-bottom: 20px;
}

.drive-identity {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.drive-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 64px;
  width: 64px;
  height: 64px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 12px;
  font-size: 1.35rem;
}

.identity-copy {
  min-width: 0;
}

.drive-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.drive-title-row h2 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 650;
  letter-spacing: -0.03em;
}

.identity-copy p {
  margin: 6px 0 4px;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.company-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 600;
}

.drive-id {
  display: block;
  margin-top: 5px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.drive-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.drive-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.7fr);
  gap: 20px;
}

.primary-column,
.secondary-column {
  min-width: 0;
}

.card-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.description-content p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  line-height: 1.7;
  white-space: pre-line;
}

.criteria-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.criteria-item {
  padding: 14px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.criteria-item span,
.criteria-item strong {
  display: block;
}

.criteria-item span,
.detail-label {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.criteria-item strong {
  margin-top: 5px;
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 600;
}

.branches-section,
.additional-criteria {
  margin-top: 20px;
}

.branch-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 9px;
}

.branch-chip {
  padding: 5px 9px;
  color: #525d6d;
  background: #eef0f3;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.branches-section p,
.additional-criteria p {
  margin: 8px 0 0;
  color: var(--color-text-muted);
  font-size: 0.825rem;
  line-height: 1.6;
  white-space: pre-line;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.section-header p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.application-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  padding: 16px;
  background: var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.summary-item {
  padding: 13px;
  background: var(--color-surface);
  text-align: center;
}

.summary-item strong,
.summary-item span {
  display: block;
}

.summary-item strong {
  color: var(--color-primary);
  font-size: 1.25rem;
  font-weight: 650;
}

.summary-item span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.primary-cell {
  color: var(--color-primary);
  font-weight: 600;
}

.empty-state {
  min-height: 240px;
}

.empty-state strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.empty-state span {
  font-size: 0.8rem;
}

.details-list {
  padding-top: 8px;
  padding-bottom: 8px;
}

.detail-row {
  padding: 13px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-row span,
.detail-row strong,
.detail-row a {
  display: block;
}

.detail-row span {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.detail-row strong,
.detail-row a {
  margin-top: 4px;
  overflow-wrap: anywhere;
  font-size: 0.825rem;
  font-weight: 600;
}

.status-card {
  padding: 20px;
  background: var(--color-primary);
  border-radius: var(--border-radius);
}

.status-card .detail-label {
  color: rgba(255, 255, 255, 0.5);
}

.status-card strong {
  display: block;
  margin-top: 7px;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 650;
}

.status-card p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.8rem;
  line-height: 1.6;
}

@media (max-width: 1199.98px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .secondary-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
}

@media (max-width: 767.98px) {
  .page-header {
    flex-direction: column;
  }

  .drive-identity {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .drive-actions {
    width: 100%;
    margin-left: 82px;
  }

  .criteria-grid,
  .application-summary,
  .secondary-column {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 575.98px) {
  .drive-identity {
    padding: 20px;
  }

  .drive-icon {
    width: 52px;
    height: 52px;
    flex-basis: 52px;
  }

  .drive-title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .drive-actions {
    align-items: stretch;
    flex-direction: column;
    margin-left: 0;
  }

  .drive-actions .btn {
    justify-content: center;
  }
}
</style>