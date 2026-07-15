<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const applications = ref([])

const filters = reactive({
  status: '',
  search: '',
  driveId: route.query.drive ? String(route.query.drive) : '',
  applicationId: route.query.application
    ? String(route.query.application)
    : '',
})

const currentPage = ref(1)
const perPage = 12

const filteredApplications = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return applications.value.filter((application) => {
    const matchesStatus =
      !filters.status ||
      application.status?.toLowerCase() === filters.status

    const matchesDrive =
      !filters.driveId ||
      String(application.drive_id) === filters.driveId

    const matchesApplication =
      !filters.applicationId ||
      String(application.id) === filters.applicationId

    const matchesSearch =
      !search ||
      application.student_name?.toLowerCase().includes(search) ||
      application.student_roll?.toLowerCase().includes(search) ||
      application.company_name?.toLowerCase().includes(search) ||
      application.drive_name?.toLowerCase().includes(search) ||
      application.job_title?.toLowerCase().includes(search)

    return (
      matchesStatus &&
      matchesDrive &&
      matchesApplication &&
      matchesSearch
    )
  })
})

const totalPages = computed(() =>
  Math.max(
    1,
    Math.ceil(filteredApplications.value.length / perPage),
  ),
)

const paginatedApplications = computed(() => {
  const start = (currentPage.value - 1) * perPage

  return filteredApplications.value.slice(start, start + perPage)
})

const rangeStart = computed(() => {
  if (!filteredApplications.value.length) return 0

  return (currentPage.value - 1) * perPage + 1
})

const rangeEnd = computed(() =>
  Math.min(
    currentPage.value * perPage,
    filteredApplications.value.length,
  ),
)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let page = start; page <= end; page += 1) {
    pages.push(page)
  }

  return pages
})

const statusCounts = computed(() => {
  const counts = {
    total: applications.value.length,
    applied: 0,
    shortlisted: 0,
    selected: 0,
    rejected: 0,
  }

  applications.value.forEach((application) => {
    const status = application.status?.toLowerCase()

    if (Object.hasOwn(counts, status)) {
      counts[status] += 1
    }
  })

  return counts
})

const summaryCards = computed(() => [
  {
    label: 'Applications',
    value: statusCounts.value.total,
    icon: 'bi-file-earmark-text',
  },
  {
    label: 'Applied',
    value: statusCounts.value.applied,
    icon: 'bi-send',
  },
  {
    label: 'Shortlisted',
    value: statusCounts.value.shortlisted,
    icon: 'bi-person-check',
  },
  {
    label: 'Selected',
    value: statusCounts.value.selected,
    icon: 'bi-check-circle',
  },
])

const hasQueryFilter = computed(
  () => filters.driveId || filters.applicationId,
)

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

const fetchApplications = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminAPI.getApplications()

    applications.value = response.data.applications || []
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
  filters.status = ''
  filters.search = ''
  filters.driveId = ''
  filters.applicationId = ''

  router.replace({
    path: '/admin/applications',
  })
}

const clearQueryFilter = () => {
  filters.driveId = ''
  filters.applicationId = ''

  router.replace({
    path: '/admin/applications',
  })
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return

  currentPage.value = page
}

const viewStudent = (studentId) => {
  if (!studentId) return

  router.push(`/admin/students/${studentId}`)
}

const viewDrive = (driveId) => {
  if (!driveId) return

  router.push(`/admin/drives/${driveId}`)
}

watch(
  () => [
    filters.status,
    filters.search,
    filters.driveId,
    filters.applicationId,
  ],
  () => {
    currentPage.value = 1
  },
)

watch(
  () => route.query,
  (query) => {
    filters.driveId = query.drive ? String(query.drive) : ''
    filters.applicationId = query.application
      ? String(query.application)
      : ''
  },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(fetchApplications)
</script>

<template>
  <div class="applications-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Applications</h1>

        <p class="page-subtitle">
          Review student application activity across placement drives.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading"
        @click="fetchApplications"
      >
        <i class="bi bi-arrow-clockwise"></i>
        Refresh
      </button>
    </header>

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

    <div
      v-if="hasQueryFilter"
      class="active-filter"
    >
      <div>
        <i class="bi bi-funnel"></i>

        <span v-if="filters.applicationId">
          Showing application #{{ filters.applicationId }}
        </span>

        <span v-else>
          Showing applications for drive #{{ filters.driveId }}
        </span>
      </div>

      <button
        type="button"
        class="filter-clear"
        @click="clearQueryFilter"
      >
        Clear filter
      </button>
    </div>

    <section class="card records-card">
      <div class="card-header records-header">
        <div>
          <h2>Application records</h2>

          <p>
            {{ filteredApplications.length }}
            {{
              filteredApplications.length === 1
                ? 'application'
                : 'applications'
            }}
            found
          </p>
        </div>

        <div class="filters">
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

          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search student, company or drive"
              aria-label="Search applications"
            />
          </div>

          <button
            v-if="
              filters.status ||
              filters.search ||
              hasQueryFilter
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
          @click="fetchApplications"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="paginatedApplications.length === 0"
        class="empty-state"
      >
        <i class="bi bi-inbox"></i>
        <strong>No applications found</strong>

        <span>
          Try changing the current search or status filter.
        </span>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Company</th>
                <th>Placement drive</th>
                <th>Job title</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Interview</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="application in paginatedApplications"
                :key="application.id"
              >
                <td>
                  <button
                    type="button"
                    class="record-link student-record"
                    :disabled="!application.student_id"
                    @click="viewStudent(application.student_id)"
                  >
                    <span class="student-avatar">
                      {{
                        application.student_name
                          ?.charAt(0)
                          .toUpperCase() || 'S'
                      }}
                    </span>

                    <span>
                      <strong>
                        {{ application.student_name }}
                      </strong>

                      <small>
                        {{
                          application.student_roll ||
                          'Roll number unavailable'
                        }}
                      </small>
                    </span>
                  </button>
                </td>

                <td>
                  {{ application.company_name || 'Not available' }}
                </td>

                <td>
                  <button
                    type="button"
                    class="drive-link"
                    :disabled="!application.drive_id"
                    @click="viewDrive(application.drive_id)"
                  >
                    {{
                      application.drive_name ||
                      `Drive #${application.drive_id}`
                    }}
                  </button>
                </td>

                <td>
                  {{ application.job_title || 'Not provided' }}
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
                      ? formatDate(application.interview_date)
                      : 'Not scheduled'
                  }}
                </td>

                <td>
                  <div class="action-group">
                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm"
                      :disabled="!application.student_id"
                      @click="viewStudent(application.student_id)"
                    >
                      Student
                    </button>

                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm icon-button"
                      :disabled="!application.drive_id"
                      title="View placement drive"
                      aria-label="View placement drive"
                      @click="viewDrive(application.drive_id)"
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
          v-if="filteredApplications.length > perPage"
          class="records-footer"
        >
          <span>
            Showing {{ rangeStart }}–{{ rangeEnd }} of
            {{ filteredApplications.length }}
          </span>

          <nav aria-label="Application pagination">
            <ul class="pagination pagination-sm mb-0">
              <li
                class="page-item"
                :class="{ disabled: currentPage === 1 }"
              >
                <button
                  type="button"
                  class="page-link"
                  aria-label="Previous page"
                  @click="changePage(currentPage - 1)"
                >
                  <i class="bi bi-chevron-left"></i>
                </button>
              </li>

              <li
                v-for="page in visiblePages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
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
                  disabled: currentPage === totalPages,
                }"
              >
                <button
                  type="button"
                  class="page-link"
                  aria-label="Next page"
                  @click="changePage(currentPage + 1)"
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
              </li>
            </ul>
          </nav>
        </footer>
      </template>
    </section>
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

.active-filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 11px 14px;
  color: var(--color-text-muted);
  background: #f1f4ff;
  border: 1px solid #dce3ff;
  border-radius: var(--border-radius-sm);
  font-size: 0.78rem;
}

.active-filter div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-clear {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.75rem;
  font-weight: 600;
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
  width: 160px;
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
  width: 280px;
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

.record-link,
.drive-link {
  padding: 0;
  color: inherit;
  background: transparent;
  border: 0;
  text-align: left;
}

.record-link:disabled,
.drive-link:disabled {
  opacity: 1;
}

.student-record {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
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

.student-record strong,
.student-record small {
  display: block;
}

.student-record strong {
  color: var(--color-primary);
  font-size: 0.825rem;
}

.student-record small {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.drive-link {
  color: var(--color-primary);
  font-size: 0.825rem;
  font-weight: 600;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  min-width: 115px;
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

@media (max-width: 991.98px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .records-header {
    align-items: stretch;
    flex-direction: column;
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