<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const error = ref('')
const applications = ref([])
const drives = ref([])
const companyProfile = ref({})

const processingId = ref(null)
const scheduling = ref(false)
const showScheduleModal = ref(false)
const selectedApplication = ref(null)

const filters = reactive({
  drive_id: route.query.drive
    ? String(route.query.drive)
    : '',
  status: '',
  search: '',
})

const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0,
})

const interviewData = reactive({
  interview_date: '',
  notes: '',
})

const isApproved = computed(
  () => companyProfile.value.approval_status === 'approved',
)

const isBlacklisted = computed(
  () => Boolean(companyProfile.value.is_blacklisted),
)

const canManage = computed(
  () => isApproved.value && !isBlacklisted.value,
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
    label: 'Total Applications',
    value: pagination.total,
    icon: 'bi-file-earmark-text',
  },
  {
    label: 'Applications Pending',
    value: statistics.value.applied,
    icon: 'bi-send',
  },
  {
    label: 'Shortlisted Candidates',
    value: statistics.value.shortlisted,
    icon: 'bi-person-check',
  },
  {
    label: 'Selected Candidates',
    value: statistics.value.selected,
    icon: 'bi-check-circle',
  },
])

const minimumInterviewDate = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())

  return now.toISOString().slice(0, 16)
})

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
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
    rejected: 'bg-danger',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const fetchSupportingData = async () => {
  try {
    const [drivesResponse, profileResponse] = await Promise.all([
      companyAPI.getDrives(),
      companyAPI.getProfile(),
    ])

    drives.value = drivesResponse.data.drives || []
    companyProfile.value = profileResponse.data.profile || {}
  } catch (requestError) {
    console.error(
      'Unable to load application supporting data:',
      requestError,
    )
  }
}

const fetchApplications = async (page = 1) => {
  loading.value = true
  error.value = ''

  try {
    const params = {
      page,
      per_page: pagination.per_page,
    }

    if (filters.drive_id) {
      params.drive_id = filters.drive_id
    }

    if (filters.status) {
      params.status = filters.status
    }

    if (filters.search.trim()) {
      params.search = filters.search.trim()
    }

    const response = await companyAPI.getApplications(params)

    applications.value = response.data.applications || []

    const responsePagination = response.data.pagination || {}

    pagination.current_page =
      responsePagination.current_page || 1
    pagination.last_page =
      responsePagination.last_page || 1
    pagination.total = responsePagination.total || 0
    pagination.from = responsePagination.from || 0
    pagination.to = responsePagination.to || 0
  } catch (requestError) {
    console.error('Unable to load applications:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load application records.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.drive_id = ''
  filters.status = ''
  filters.search = ''

  router.replace('/company/applications')
}

const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return

  fetchApplications(page)
}

const shortlistApplication = async (application) => {
  if (!canManage.value) return

  processingId.value = application.id

  try {
    await companyAPI.shortlistApplication(application.id)

    messageStore.updateSuccessMessages(
      `${application.student_name} shortlisted successfully.`,
    )

    await fetchApplications(pagination.current_page)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to shortlist the application.',
    )
  } finally {
    processingId.value = null
  }
}

const selectApplication = async (application) => {
  if (!canManage.value) return

  const confirmed = window.confirm(
    `Mark ${application.student_name} as selected?`,
  )

  if (!confirmed) return

  processingId.value = application.id

  try {
    await companyAPI.selectApplication(application.id)

    messageStore.updateSuccessMessages(
      `${application.student_name} selected successfully.`,
    )

    await fetchApplications(pagination.current_page)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to select the application.',
    )
  } finally {
    processingId.value = null
  }
}

const rejectApplication = async (application) => {
  if (!canManage.value) return

  const reason = window.prompt('Enter the rejection reason:')

  if (!reason?.trim()) return

  processingId.value = application.id

  try {
    await companyAPI.rejectApplication(application.id, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages(
      `${application.student_name}'s application was rejected.`,
    )

    await fetchApplications(pagination.current_page)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the application.',
    )
  } finally {
    processingId.value = null
  }
}

const openScheduleModal = (application) => {
  if (!canManage.value) return

  selectedApplication.value = application
  interviewData.interview_date = ''
  interviewData.notes = ''
  showScheduleModal.value = true
}

const closeScheduleModal = () => {
  if (scheduling.value) return

  showScheduleModal.value = false
  selectedApplication.value = null
}

const confirmScheduleInterview = async () => {
  if (!selectedApplication.value) return

  if (!interviewData.interview_date) {
    messageStore.updateErrorMessages(
      'Interview date and time are required.',
    )

    return
  }

  if (
    new Date(interviewData.interview_date) <= new Date()
  ) {
    messageStore.updateErrorMessages(
      'Interview date must be in the future.',
    )

    return
  }

  scheduling.value = true

  try {
    await companyAPI.scheduleInterview(
      selectedApplication.value.id,
      {
        interview_date: interviewData.interview_date,
        notes: interviewData.notes.trim(),
      },
    )

    messageStore.updateSuccessMessages(
      'Interview scheduled successfully.',
    )

    showScheduleModal.value = false
    selectedApplication.value = null

    await fetchApplications(pagination.current_page)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to schedule the interview.',
    )
  } finally {
    scheduling.value = false
  }
}

const viewDetails = (id) => {
  router.push(`/company/applications/${id}`)
}

watch(
  () => [filters.drive_id, filters.status],
  () => {
    fetchApplications(1)
  },
)

watch(
  () => route.query.drive,
  (driveId) => {
    filters.drive_id = driveId ? String(driveId) : ''
  },
)

onMounted(async () => {
  await Promise.all([
    fetchSupportingData(),
    fetchApplications(),
  ])
})
</script>

<template>
  <div class="applications-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Applications</h1>

        <p class="page-subtitle">
          Review candidates and manage recruitment decisions.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading"
        @click="fetchApplications(pagination.current_page)"
      >
        <i class="bi bi-arrow-clockwise"></i>
        Refresh
      </button>
    </header>

    <section
      v-if="!canManage"
      class="access-notice"
      :class="{ blacklisted: isBlacklisted }"
    >
      <i
        :class="[
          'bi',
          isBlacklisted ? 'bi-slash-circle' : 'bi-clock',
        ]"
      ></i>

      <div>
        <strong>
          {{
            isBlacklisted
              ? 'Company account blacklisted'
              : 'Company approval pending'
          }}
        </strong>

        <p>
          {{
            isBlacklisted
              ? 'Application records remain visible, but recruitment decisions are disabled.'
              : 'You can review applications, but status updates are available only after institute approval.'
          }}
        </p>
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
            {{ Number(item.value).toLocaleString('en-IN') }}
          </strong>

          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="card records-card">
      <div class="card-header records-header">
        <div>
          <h2>Application records</h2>

          <p>
            {{ pagination.total }}
            {{
              pagination.total === 1
                ? 'application'
                : 'applications'
            }}
            found
          </p>
        </div>

        <div class="filters">
          <select
            v-model="filters.drive_id"
            class="form-select drive-filter"
            aria-label="Filter applications by placement drive"
          >
            <option value="">All drives</option>

            <option
              v-for="drive in drives"
              :key="drive.id"
              :value="String(drive.id)"
            >
              {{ drive.drive_name }}
            </option>
          </select>

          <select
            v-model="filters.status"
            class="form-select"
            aria-label="Filter applications by status"
          >
            <option value="">All statuses</option>
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>

          <form
            class="search-field"
            @submit.prevent="fetchApplications(1)"
          >
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search student"
              aria-label="Search applications by student name"
            />
          </form>

          <button
            v-if="
              filters.drive_id ||
              filters.status ||
              filters.search
            "
            type="button"
            class="btn btn-outline-secondary"
            @click="resetFilters"
          >
            Clear
          </button>
        </div>
      </div>

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
            Loading applications
          </span>
        </div>

        <span>Loading application records...</span>
      </div>

      <div
        v-else-if="error"
        class="page-state error-state"
      >
        <i class="bi bi-exclamation-circle"></i>

        <div>
          <strong>Applications could not be loaded</strong>
          <p>{{ error }}</p>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="fetchApplications()"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="applications.length === 0"
        class="empty-state"
      >
        <i class="bi bi-inbox"></i>
        <strong>No applications found</strong>

        <span>
          Try changing the selected drive, status or student search.
        </span>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Placement drive</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Interview</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="application in applications"
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
                  <strong class="cgpa-value">
                    {{
                      application.student_cgpa !== null &&
                      application.student_cgpa !== undefined
                        ? Number(
                            application.student_cgpa,
                          ).toFixed(2)
                        : '—'
                    }}
                  </strong>
                </td>

                <td>
                  <button
                    type="button"
                    class="drive-link"
                    @click="
                      router.push(
                        `/company/drives/${application.drive_id}`,
                      )
                    "
                  >
                    {{ application.drive_name }}
                  </button>
                </td>

                <td>
                  {{ formatDate(application.applied_at) }}
                </td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(application.status)"
                  >
                    {{ formatStatus(application.status) }}
                  </span>
                </td>

                <td>
                  {{
                    application.interview_date
                      ? formatDateTime(
                          application.interview_date,
                        )
                      : 'Not scheduled'
                  }}
                </td>

                <td>
                  <div class="action-group">
                    <template v-if="canManage">
                      <button
                        v-if="application.status === 'applied'"
                        type="button"
                        class="btn btn-outline-primary btn-sm"
                        :disabled="
                          processingId === application.id
                        "
                        @click="
                          shortlistApplication(application)
                        "
                      >
                        Shortlist
                      </button>

                      <button
                        v-if="
                          application.status === 'shortlisted'
                        "
                        type="button"
                        class="btn btn-outline-success btn-sm"
                        :disabled="
                          processingId === application.id
                        "
                        @click="selectApplication(application)"
                      >
                        Select
                      </button>

                      <button
                        v-if="
                          application.status === 'shortlisted' &&
                          !application.interview_date
                        "
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        @click="openScheduleModal(application)"
                      >
                        Interview
                      </button>

                      <button
                        v-if="
                          application.status === 'applied' ||
                          application.status === 'shortlisted'
                        "
                        type="button"
                        class="btn btn-outline-danger btn-sm"
                        :disabled="
                          processingId === application.id
                        "
                        @click="rejectApplication(application)"
                      >
                        Reject
                      </button>
                    </template>

                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm icon-button"
                      title="View application details"
                      aria-label="View application details"
                      @click="viewDetails(application.id)"
                    >
                      <i class="bi bi-arrow-up-right"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer
          v-if="pagination.total > pagination.per_page"
          class="records-footer"
        >
          <span>
            Showing {{ pagination.from }}–{{ pagination.to }} of
            {{ pagination.total }}
          </span>

          <nav aria-label="Application pagination">
            <ul class="pagination pagination-sm mb-0">
              <li
                class="page-item"
                :class="{
                  disabled: pagination.current_page === 1,
                }"
              >
                <button
                  type="button"
                  class="page-link"
                  @click="
                    changePage(pagination.current_page - 1)
                  "
                >
                  <i class="bi bi-chevron-left"></i>
                </button>
              </li>

              <li
                v-for="page in pagination.last_page"
                :key="page"
                class="page-item"
                :class="{
                  active: page === pagination.current_page,
                }"
              >
                <button
                  type="button"
                  class="page-link"
                  @click="changePage(page)"
                >
                  {{ page }}
                </button>
              </li>

              <li
                class="page-item"
                :class="{
                  disabled:
                    pagination.current_page ===
                    pagination.last_page,
                }"
              >
                <button
                  type="button"
                  class="page-link"
                  @click="
                    changePage(pagination.current_page + 1)
                  "
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
              </li>
            </ul>
          </nav>
        </footer>
      </template>
    </section>

    <div
      v-if="showScheduleModal"
      class="modal-backdrop-custom"
      @click.self="closeScheduleModal"
    >
      <section
        class="schedule-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="scheduleTitle"
      >
        <header class="dialog-header">
          <div>
            <h2 id="scheduleTitle">Schedule interview</h2>

            <p>
              {{ selectedApplication?.student_name }}
            </p>
          </div>

          <button
            type="button"
            class="dialog-close"
            aria-label="Close schedule interview dialog"
            :disabled="scheduling"
            @click="closeScheduleModal"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </header>

        <div class="dialog-body">
          <div class="field-group">
            <label
              for="interviewDate"
              class="form-label"
            >
              Interview date and time
            </label>

            <input
              id="interviewDate"
              v-model="interviewData.interview_date"
              type="datetime-local"
              class="form-control"
              :min="minimumInterviewDate"
              required
            />
          </div>

          <div class="field-group">
            <label
              for="interviewNotes"
              class="form-label"
            >
              Interview instructions
            </label>

            <textarea
              id="interviewNotes"
              v-model="interviewData.notes"
              class="form-control"
              rows="4"
              placeholder="Meeting link, venue or instructions"
            ></textarea>
          </div>
        </div>

        <footer class="dialog-footer">
          <button
            type="button"
            class="btn btn-outline-secondary"
            :disabled="scheduling"
            @click="closeScheduleModal"
          >
            Cancel
          </button>

          <button
            type="button"
            class="btn btn-primary"
            :disabled="
              scheduling || !interviewData.interview_date
            "
            @click="confirmScheduleInterview"
          >
            <span
              v-if="scheduling"
              class="spinner-border spinner-border-sm"
              aria-hidden="true"
            ></span>

            {{
              scheduling
                ? 'Scheduling...'
                : 'Schedule interview'
            }}
          </button>
        </footer>
      </section>
    </div>
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

.access-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  padding: 15px 17px;
  background: #fff9e8;
  border: 1px solid #eadcae;
  border-radius: var(--border-radius);
}

.access-notice.blacklisted {
  background: #fff1f0;
  border-color: #f5cfcc;
}

.access-notice > i {
  color: var(--color-primary);
}

.access-notice strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.access-notice p {
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

.records-card {
  margin-bottom: 0;
}

.records-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.records-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.records-header p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filters .form-select {
  width: 150px;
}

.filters .drive-filter {
  width: 210px;
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
  width: 210px;
  padding-left: 36px;
}

.page-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 11px;
  min-height: 300px;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.error-state {
  align-items: flex-start;
  justify-content: flex-start;
  min-height: auto;
  margin: 20px;
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
.student-cell div > span {
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

.cgpa-value {
  color: var(--color-text);
  font-size: 0.82rem;
}

.drive-link {
  padding: 0;
  color: var(--color-primary);
  background: transparent;
  border: 0;
  font-size: 0.82rem;
  font-weight: 600;
  text-align: left;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  min-width: 250px;
}

.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  padding: 0;
}

.empty-state {
  min-height: 320px;
}

.empty-state strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.empty-state span {
  font-size: 0.8rem;
}

.records-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  color: var(--color-text-muted);
  border-top: 1px solid var(--color-border);
  font-size: 0.75rem;
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  z-index: 1080;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(17, 24, 39, 0.48);
}

.schedule-dialog {
  width: min(100%, 500px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: 0 24px 70px rgba(17, 24, 39, 0.2);
}

.dialog-header,
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
}

.dialog-header {
  border-bottom: 1px solid var(--color-border);
}

.dialog-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 650;
}

.dialog-header p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.dialog-close {
  padding: 5px;
  color: var(--color-text-muted);
  background: transparent;
  border: 0;
}

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
}

.field-group {
  min-width: 0;
}

.form-label {
  margin-bottom: 7px;
  font-size: 0.78rem;
  font-weight: 600;
}

textarea.form-control {
  resize: vertical;
}

.dialog-footer {
  justify-content: flex-end;
  border-top: 1px solid var(--color-border);
}

.dialog-footer .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

@media (max-width: 1199.98px) {
  .records-header {
    align-items: stretch;
    flex-direction: column;
  }

  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 991.98px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .page-header {
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .filters .form-select,
  .filters .drive-filter,
  .search-field .form-control {
    width: 100%;
  }

  .records-footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
  }
}
</style>