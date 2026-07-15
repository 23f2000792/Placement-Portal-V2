<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const applyingId = ref(null)

const drives = ref([])
const studentProfile = ref({})

const filters = reactive({
  search: '',
  eligibility: '',
})

const filteredDrives = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return drives.value.filter((drive) => {
    const matchesSearch =
      !search ||
      drive.drive_name?.toLowerCase().includes(search) ||
      drive.company_name?.toLowerCase().includes(search) ||
      drive.job_title?.toLowerCase().includes(search)

    let matchesEligibility = true

    if (filters.eligibility === 'eligible') {
      matchesEligibility =
        drive.eligibility?.is_eligible &&
        !drive.already_applied
    }

    if (filters.eligibility === 'applied') {
      matchesEligibility = drive.already_applied
    }

    if (filters.eligibility === 'ineligible') {
      matchesEligibility =
        !drive.eligibility?.is_eligible &&
        !drive.already_applied
    }

    return matchesSearch && matchesEligibility
  })
})

const eligibilityCounts = computed(() => ({
  all: drives.value.length,
  eligible: drives.value.filter(
    (drive) =>
      drive.eligibility?.is_eligible &&
      !drive.already_applied,
  ).length,
  applied: drives.value.filter(
    (drive) => drive.already_applied,
  ).length,
}))

const formatDate = (value) => {
  if (!value) return 'No deadline'

  return new Date(value).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const getDaysLeft = (deadline) => {
  if (!deadline) return 'No deadline'

  const difference =
    new Date(deadline).getTime() - new Date().getTime()

  const days = Math.ceil(
    difference / (1000 * 60 * 60 * 24),
  )

  if (days < 0) return 'Closed'
  if (days === 0) return 'Today'
  if (days === 1) return '1 day left'

  return `${days} days left`
}

const getDeadlineClass = (deadline) => {
  if (!deadline) return ''

  const difference =
    new Date(deadline).getTime() - new Date().getTime()

  const days = Math.ceil(
    difference / (1000 * 60 * 60 * 24),
  )

  if (days < 0) return 'deadline-closed'
  if (days <= 1) return 'deadline-urgent'
  if (days <= 3) return 'deadline-soon'

  return ''
}

const getDriveState = (drive) => {
  if (drive.already_applied) {
    return {
      label: 'Applied',
      className: 'state-applied',
      icon: 'bi-check-circle',
    }
  }

  if (!drive.eligibility?.deadline_active) {
    return {
      label: 'Closed',
      className: 'state-closed',
      icon: 'bi-clock-history',
    }
  }

  if (drive.eligibility?.is_eligible) {
    return {
      label: 'Eligible',
      className: 'state-eligible',
      icon: 'bi-check-circle',
    }
  }

  return {
    label: 'Not eligible',
    className: 'state-ineligible',
    icon: 'bi-lock',
  }
}

const fetchData = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const [drivesResponse, profileResponse] =
      await Promise.all([
        studentAPI.getDrives(),
        studentAPI.getProfile(),
      ])

    drives.value = drivesResponse.data.drives || []
    studentProfile.value =
      profileResponse.data.profile || {}
  } catch (requestError) {
    console.error(
      'Unable to load placement drives:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load placement drives.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const applyToDrive = async (drive) => {
  if (
    drive.already_applied ||
    !drive.eligibility?.is_eligible
  ) {
    return
  }

  const confirmed = window.confirm(
    `Apply to ${drive.drive_name} at ${drive.company_name}?`,
  )

  if (!confirmed) return

  applyingId.value = drive.id

  try {
    await studentAPI.applyToDrive(drive.id)

    messageStore.updateSuccessMessages(
      'Application submitted successfully.',
    )

    await fetchData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to submit your application.',
    )
  } finally {
    applyingId.value = null
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.eligibility = ''
}

const viewDrive = (id) => {
  router.push(`/student/drives/${id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="student-drives-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Placement drives</h1>

        <p class="page-subtitle">
          Browse approved recruitment opportunities and check your
          eligibility.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading || refreshing"
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
          Loading placement drives
        </span>
      </div>

      <span>Loading placement drives...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Placement drives could not be loaded</strong>
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
      <section class="overview-grid">
        <article class="overview-card">
          <strong>{{ eligibilityCounts.all }}</strong>
          <span>Available drives</span>
        </article>

        <article class="overview-card">
          <strong>{{ eligibilityCounts.eligible }}</strong>
          <span>Eligible to apply</span>
        </article>

        <article class="overview-card">
          <strong>{{ eligibilityCounts.applied }}</strong>
          <span>Applications submitted</span>
        </article>

        <article class="profile-card">
          <span>
            {{ studentProfile.branch || 'Branch not provided' }}
          </span>

          <strong>
            CGPA
            {{
              studentProfile.cgpa !== null &&
              studentProfile.cgpa !== undefined
                ? Number(studentProfile.cgpa).toFixed(2)
                : '—'
            }}
          </strong>
        </article>
      </section>

      <section class="card filters-card">
        <div class="filters">
          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search drive, company or job title"
              aria-label="Search placement drives"
            />
          </div>

          <select
            v-model="filters.eligibility"
            class="form-select"
            aria-label="Filter placement drives"
          >
            <option value="">All drives</option>
            <option value="eligible">Eligible only</option>
            <option value="applied">Applied only</option>
            <option value="ineligible">Not eligible</option>
          </select>

          <button
            v-if="filters.search || filters.eligibility"
            type="button"
            class="btn btn-outline-secondary"
            @click="resetFilters"
          >
            Clear
          </button>
        </div>

        <span class="result-count">
          {{ filteredDrives.length }}
          {{
            filteredDrives.length === 1
              ? 'drive'
              : 'drives'
          }}
        </span>
      </section>

      <section
        v-if="filteredDrives.length === 0"
        class="empty-state drives-empty"
      >
        <i class="bi bi-briefcase"></i>

        <strong>No placement drives found</strong>

        <span>
          {{
            filters.search || filters.eligibility
              ? 'Try changing your search or eligibility filter.'
              : 'There are no approved placement drives available right now.'
          }}
        </span>

        <button
          v-if="filters.search || filters.eligibility"
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="resetFilters"
        >
          Clear filters
        </button>
      </section>

      <section
        v-else
        class="drives-grid"
      >
        <article
          v-for="drive in filteredDrives"
          :key="drive.id"
          class="drive-card"
        >
          <header class="drive-header">
            <div class="company-heading">
              <span class="company-avatar">
                {{
                  drive.company_name
                    ?.charAt(0)
                    .toUpperCase() || 'C'
                }}
              </span>

              <div>
                <span>{{ drive.company_name }}</span>
                <strong>{{ drive.drive_name }}</strong>
              </div>
            </div>

            <span
              class="drive-state"
              :class="getDriveState(drive).className"
            >
              <i
                :class="[
                  'bi',
                  getDriveState(drive).icon,
                ]"
              ></i>

              {{ getDriveState(drive).label }}
            </span>
          </header>

          <div class="drive-body">
            <div class="role-section">
              <span>Role</span>
              <h2>{{ drive.job_title }}</h2>
            </div>

            <p class="description">
              {{
                drive.job_description ||
                'No job description has been provided.'
              }}
            </p>

            <div class="drive-meta">
              <div>
                <span>Minimum CGPA</span>

                <strong>
                  {{
                    drive.min_cgpa !== null &&
                    drive.min_cgpa !== undefined
                      ? Number(drive.min_cgpa).toFixed(2)
                      : 'No minimum'
                  }}
                </strong>
              </div>

              <div>
                <span>Deadline</span>

                <strong
                  :class="
                    getDeadlineClass(
                      drive.application_deadline,
                    )
                  "
                >
                  {{
                    getDaysLeft(
                      drive.application_deadline,
                    )
                  }}
                </strong>
              </div>
            </div>

            <div class="eligibility-panel">
              <div>
                <span>
                  <i class="bi bi-mortarboard"></i>
                  CGPA eligibility
                </span>

                <strong
                  :class="{
                    eligible:
                      drive.eligibility?.cgpa_eligible,
                    ineligible:
                      !drive.eligibility?.cgpa_eligible,
                  }"
                >
                  {{
                    drive.eligibility?.cgpa_eligible
                      ? 'Eligible'
                      : 'Not eligible'
                  }}
                </strong>
              </div>

              <div>
                <span>
                  <i class="bi bi-diagram-3"></i>
                  Branch eligibility
                </span>

                <strong
                  :class="{
                    eligible:
                      drive.eligibility?.branch_eligible,
                    ineligible:
                      !drive.eligibility?.branch_eligible,
                  }"
                >
                  {{
                    drive.eligibility?.branch_eligible
                      ? 'Eligible'
                      : 'Not eligible'
                  }}
                </strong>
              </div>
            </div>

            <div
              v-if="drive.allowed_branches"
              class="branch-note"
            >
              <span>Allowed branches</span>

              <p>{{ drive.allowed_branches }}</p>
            </div>
          </div>

          <footer class="drive-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="viewDrive(drive.id)"
            >
              View details
            </button>

            <button
              v-if="
                !drive.already_applied &&
                drive.eligibility?.is_eligible
              "
              type="button"
              class="btn btn-primary"
              :disabled="applyingId === drive.id"
              @click="applyToDrive(drive)"
            >
              <span
                v-if="applyingId === drive.id"
                class="spinner-border spinner-border-sm"
                aria-hidden="true"
              ></span>

              <i
                v-else
                class="bi bi-send"
              ></i>

              {{
                applyingId === drive.id
                  ? 'Applying...'
                  : 'Apply'
              }}
            </button>

            <button
              v-else
              type="button"
              class="btn btn-secondary"
              disabled
            >
              {{ getDriveState(drive).label }}
            </button>
          </footer>
        </article>
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

.overview-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr))
    minmax(220px, 1.2fr);
  gap: 16px;
  margin-bottom: 20px;
}

.overview-card,
.profile-card {
  padding: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.overview-card strong,
.overview-card span {
  display: block;
}

.overview-card strong {
  color: var(--color-primary);
  font-size: 1.35rem;
  font-weight: 650;
}

.overview-card span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.profile-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  color: #ffffff;
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.profile-card span {
  color: rgba(255, 255, 255, 0.62);
  font-size: 0.75rem;
}

.profile-card strong {
  color: #ffffff;
  font-size: 0.82rem;
}

.filters-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
  padding: 14px 16px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-field {
  position: relative;
}

.search-field i {
  position: absolute;
  top: 50%;
  left: 13px;
  z-index: 1;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  transform: translateY(-50%);
}

.search-field .form-control {
  width: 320px;
  padding-left: 36px;
}

.filters .form-select {
  width: 170px;
}

.result-count {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.drives-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.drive-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.drive-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid var(--color-border);
}

.company-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.company-avatar {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;

  flex: 0 0 38px;
  width: 38px;
  height: 38px;

  padding: 0 !important;
  margin: 0;

  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;

  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1;

  text-align: center;
}

.company-heading div {
  min-width: 0;
}

.company-heading span,
.company-heading strong {
  display: block;
}

.company-heading div > span {
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.company-heading strong {
  overflow: hidden;
  margin-top: 3px;
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drive-state {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 650;
}

.state-eligible {
  color: #23633c;
  background: #e7f4ec;
}

.state-applied {
  color: #314c77;
  background: #e9eef7;
}

.state-closed,
.state-ineligible {
  color: #696969;
  background: #eeeeec;
}

.drive-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 18px;
}

.role-section > span,
.branch-note > span {
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.role-section h2 {
  margin: 4px 0 0;
  color: var(--color-primary);
  font-size: 1rem;
  font-weight: 650;
}

.description {
  display: -webkit-box;
  overflow: hidden;
  margin: 12px 0 18px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.drive-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.drive-meta > div {
  padding: 11px;
}

.drive-meta > div + div {
  border-left: 1px solid var(--color-border);
}

.drive-meta span,
.drive-meta strong {
  display: block;
}

.drive-meta span {
  color: var(--color-text-muted);
  font-size: 0.65rem;
}

.drive-meta strong {
  margin-top: 4px;
  color: var(--color-text);
  font-size: 0.74rem;
}

.deadline-urgent,
.deadline-closed {
  color: var(--color-danger) !important;
}

.deadline-soon {
  color: #9a6700 !important;
}

.eligibility-panel {
  padding: 12px;
  background: var(--color-surface-muted);
  border-radius: var(--border-radius-sm);
}

.eligibility-panel > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.eligibility-panel > div + div {
  margin-top: 9px;
}

.eligibility-panel span {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.eligibility-panel strong {
  font-size: 0.68rem;
  font-weight: 650;
}

.eligible {
  color: #23633c;
}

.ineligible {
  color: var(--color-danger);
}

.branch-note {
  margin-top: 14px;
}

.branch-note p {
  margin: 4px 0 0;
  color: var(--color-text);
  font-size: 0.7rem;
  line-height: 1.5;
}

.drive-footer {
  display: flex;
  gap: 8px;
  padding: 14px 18px;
  border-top: 1px solid var(--color-border);
}

.drive-footer .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex: 1;
}

.drives-empty {
  min-height: 350px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.drives-empty strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.drives-empty span {
  max-width: 430px;
  font-size: 0.78rem;
}

@media (max-width: 1199.98px) {
  .drives-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .filters-card {
    align-items: stretch;
    flex-direction: column;
  }

  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .search-field .form-control,
  .filters .form-select {
    width: 100%;
  }

  .overview-grid,
  .drives-grid {
    grid-template-columns: 1fr;
  }
}
</style>