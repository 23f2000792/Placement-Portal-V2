<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const dashboard = ref({})
const drives = ref([])

const company = computed(() => dashboard.value.company || {})

const stats = computed(() => {
  const source = dashboard.value.statistics || {}

  return {
    totalDrives:
      source.total_drives ??
      drives.value.length,

    activeDrives:
      source.active_drives ??
      drives.value.filter(
        (drive) => drive.status === 'approved',
      ).length,

    totalApplications:
      source.total_applications ??
      drives.value.reduce(
        (total, drive) =>
          total + Number(drive.application_count || 0),
        0,
      ),

    selectedStudents:
      source.selected ?? 0,
  }
})

const summaryCards = computed(() => [
  {
    label: 'Placement drives',
    value: stats.value.totalDrives,
    icon: 'bi-briefcase-fill',
  },
  {
    label: 'Active drives',
    value: stats.value.activeDrives,
    icon: 'bi-play-circle-fill',
  },
  {
    label: 'Applications',
    value: stats.value.totalApplications,
    icon: 'bi-file-earmark-text-fill',
  },
  {
    label: 'Selected students',
    value: stats.value.selectedStudents,
    icon: 'bi-person-check-fill',
  },
])

const recentDrives = computed(() => drives.value.slice(0, 5))

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
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
    closed: 'bg-secondary',
  }

  return classes[status] || 'bg-secondary'
}

const fetchDashboard = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await companyAPI.getDashboard()

    dashboard.value = response.data || {}

    drives.value =
      response.data.drives ||
      response.data.recent_drives ||
      []
  } catch (requestError) {
    console.error('Unable to load company dashboard:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load company dashboard.'
  } finally {
    loading.value = false
  }
}

const createDrive = () => {
  router.push('/company/drives/create')
}

const viewDrives = () => {
  router.push('/company/drives')
}

const viewDrive = (id) => {
  router.push(`/company/drives/${id}`)
}

const viewApplications = () => {
  router.push('/company/applications')
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="company-dashboard fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Company dashboard</h1>

        <p class="page-subtitle">
          Manage recruitment drives and review placement activity.
        </p>
      </div>

      <button
        v-if="company.approval_status === 'approved'"
        type="button"
        class="btn btn-primary"
        @click="createDrive"
      >
        <i class="bi bi-plus-lg"></i>
        Create drive
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
        <span class="visually-hidden">
          Loading company dashboard
        </span>
      </div>

      <span>Loading dashboard...</span>
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
        @click="fetchDashboard"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        v-if="company.approval_status !== 'approved'"
        class="approval-notice"
        :class="{
          'rejected-notice':
            company.approval_status === 'rejected',
        }"
      >
        <span class="notice-icon">
          <i
            :class="[
              'bi',
              company.approval_status === 'rejected'
                ? 'bi-x-circle'
                : 'bi-clock',
            ]"
          ></i>
        </span>

        <div>
          <strong>
            {{
              company.approval_status === 'rejected'
                ? 'Company registration rejected'
                : 'Company approval pending'
            }}
          </strong>

          <p>
            {{
              company.approval_status === 'rejected'
                ? 'Your company cannot create placement drives at this time.'
                : 'The institute placement cell must approve your company before you can create placement drives.'
            }}
          </p>
        </div>
      </section>

      <section class="company-summary">
        <div>
          <span class="company-avatar">
            {{
              company.company_name?.charAt(0).toUpperCase() ||
              'C'
            }}
          </span>

          <div>
            <div class="company-title-row">
              <h2>
                {{ company.company_name || 'Company profile' }}
              </h2>

              <span
                class="badge"
                :class="
                  company.approval_status === 'approved'
                    ? 'bg-success'
                    : company.approval_status === 'rejected'
                      ? 'bg-danger'
                      : 'bg-warning'
                "
              >
                {{ formatStatus(company.approval_status) }}
              </span>
            </div>

            <p>
              {{ company.industry || 'Industry not provided' }}
              <span>·</span>
              {{ company.location || 'Location not provided' }}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="router.push('/company/profile')"
        >
          View profile
        </button>
      </section>

      <section
        class="summary-grid"
        aria-label="Company placement statistics"
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
              {{ Number(item.value || 0).toLocaleString('en-IN') }}
            </strong>

            <span>{{ item.label }}</span>
          </div>
        </article>
      </section>

      <section class="dashboard-grid">
        <article class="card drives-card">
          <div class="card-header section-header">
            <div>
              <h2>Recent placement drives</h2>

              <p>
                Latest recruitment drives created by your company.
              </p>
            </div>

            <button
              type="button"
              class="section-link"
              @click="viewDrives"
            >
              View all
            </button>
          </div>

          <div
            v-if="recentDrives.length === 0"
            class="empty-state"
          >
            <i class="bi bi-briefcase"></i>
            <strong>No placement drives</strong>

            <span v-if="company.approval_status === 'approved'">
              Create your first placement drive to begin recruitment.
            </span>

            <span v-else>
              Placement drives can be created after company approval.
            </span>

            <button
              v-if="company.approval_status === 'approved'"
              type="button"
              class="btn btn-primary btn-sm"
              @click="createDrive"
            >
              Create drive
            </button>
          </div>

          <div
            v-else
            class="drive-list"
          >
            <button
              v-for="drive in recentDrives"
              :key="drive.id"
              type="button"
              class="drive-item"
              @click="viewDrive(drive.id)"
            >
              <span class="drive-icon">
                <i class="bi bi-briefcase"></i>
              </span>

              <span class="drive-copy">
                <strong>
                  {{ drive.drive_name }}
                </strong>

                <small>
                  {{ drive.job_title }}
                  <span>·</span>
                  Deadline
                  {{ formatDate(drive.application_deadline) }}
                </small>
              </span>

              <span
                class="badge"
                :class="getStatusClass(drive.status)"
              >
                {{ formatStatus(drive.status) }}
              </span>

              <span class="applicant-count">
                <strong>
                  {{ Number(drive.application_count || 0) }}
                </strong>

                <small>Applicants</small>
              </span>

              <i class="bi bi-chevron-right drive-arrow"></i>
            </button>
          </div>
        </article>

        <aside class="dashboard-sidebar">
          <article class="card quick-actions-card">
            <div class="card-header">
              <h2>Quick actions</h2>
            </div>

            <div class="card-body quick-actions">
              <button
                type="button"
                :disabled="
                  company.approval_status !== 'approved'
                "
                @click="createDrive"
              >
                <span>
                  <i class="bi bi-plus-lg"></i>
                </span>

                <div>
                  <strong>Create placement drive</strong>
                  <small>
                    Add a new recruitment opportunity.
                  </small>
                </div>

                <i class="bi bi-chevron-right"></i>
              </button>

              <button
                type="button"
                @click="viewApplications"
              >
                <span>
                  <i class="bi bi-file-earmark-text"></i>
                </span>

                <div>
                  <strong>Review applications</strong>
                  <small>
                    View and manage student applications.
                  </small>
                </div>

                <i class="bi bi-chevron-right"></i>
              </button>

              <button
                type="button"
                @click="viewDrives"
              >
                <span>
                  <i class="bi bi-briefcase"></i>
                </span>

                <div>
                  <strong>Manage drives</strong>
                  <small>
                    Review your recruitment drive records.
                  </small>
                </div>

                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
          </article>

          <article class="status-card">
            <span>Account status</span>

            <strong>
              {{ formatStatus(company.approval_status) }}
            </strong>

            <p v-if="company.approval_status === 'approved'">
              Your company can create and manage placement drives.
            </p>

            <p v-else-if="company.approval_status === 'rejected'">
              Your company registration has not been approved.
            </p>

            <p v-else>
              Your registration is awaiting institute approval.
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

.dashboard-title {
  margin-bottom: 0;
}

.page-header .btn {
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

.approval-notice {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  margin-bottom: 20px;
  padding: 16px 18px;
  background: #fff9e8;
  border: 1px solid #eadcae;
  border-radius: var(--border-radius);
}

.approval-notice.rejected-notice {
  background: #fff1f0;
  border-color: #f5cfcc;
}

.notice-icon {
  color: #8a6b17;
}

.rejected-notice .notice-icon {
  color: var(--color-danger);
}

.approval-notice strong {
  color: var(--color-primary);
  font-size: 0.85rem;
}

.approval-notice p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.78rem;
  line-height: 1.55;
}

.company-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.company-summary > div {
  display: flex;
  align-items: center;
  gap: 14px;
}

.company-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 10px;
  font-weight: 700;
}

.company-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.company-title-row h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 650;
}

.company-summary p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.78rem;
}

.company-summary p span {
  margin: 0 5px;
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
  grid-template-columns: minmax(0, 1.65fr) minmax(280px, 0.7fr);
  gap: 20px;
}

.drives-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.section-header h2,
.quick-actions-card h2 {
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

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.drive-list {
  display: flex;
  flex-direction: column;
}

.drive-item {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto 75px 16px;
  align-items: center;
  gap: 13px;
  width: 100%;
  padding: 15px 16px;
  color: inherit;
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.drive-item:last-child {
  border-bottom: 0;
}

.drive-item:hover {
  background: var(--color-surface-muted);
}

.drive-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.drive-copy strong,
.drive-copy small,
.applicant-count strong,
.applicant-count small {
  display: block;
}

.drive-copy strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.drive-copy small {
  margin-top: 4px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.drive-copy small span {
  margin: 0 4px;
}

.applicant-count {
  text-align: right;
}

.applicant-count strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.applicant-count small {
  color: var(--color-text-muted);
  font-size: 0.65rem;
}

.drive-arrow {
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.dashboard-sidebar {
  min-width: 0;
}

.quick-actions {
  padding: 8px;
}

.quick-actions > button {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) 14px;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 12px;
  color: inherit;
  background: transparent;
  border: 0;
  border-radius: var(--border-radius-sm);
  text-align: left;
}

.quick-actions > button:hover:not(:disabled) {
  background: var(--color-surface-muted);
}

.quick-actions > button:disabled {
  opacity: 0.45;
}

.quick-actions > button > span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.quick-actions strong,
.quick-actions small {
  display: block;
}

.quick-actions strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.quick-actions small {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.quick-actions > button > i {
  color: var(--color-text-muted);
  font-size: 0.65rem;
}

.status-card {
  padding: 20px;
  background: var(--color-primary);
  border-radius: var(--border-radius);
}

.status-card > span {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.72rem;
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
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .company-summary {
    align-items: stretch;
    flex-direction: column;
  }

  .summary-grid,
  .dashboard-sidebar {
    grid-template-columns: 1fr;
  }

  .drive-item {
    grid-template-columns: 40px minmax(0, 1fr) auto;
  }

  .drive-item > .badge {
    grid-column: 2;
  }

  .applicant-count {
    grid-column: 3;
    grid-row: 1;
  }

  .drive-arrow {
    display: none;
  }
}

@media (max-width: 575.98px) {
  .company-summary > div {
    align-items: flex-start;
  }

  .company-title-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>