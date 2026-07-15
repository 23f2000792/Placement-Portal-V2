<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'

const router = useRouter()

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')

const applications = ref([])
const statistics = ref({})

const filters = reactive({
  search: '',
  status: '',
})

const summaryCards = computed(() => [
  {
    label: 'Total',
    value: statistics.value.total || 0,
    icon: 'bi-file-earmark-text',
  },
  {
    label: 'Applied',
    value: statistics.value.applied || 0,
    icon: 'bi-send',
  },
  {
    label: 'Shortlisted',
    value: statistics.value.shortlisted || 0,
    icon: 'bi-person-check',
  },
  {
    label: 'Selected',
    value: statistics.value.selected || 0,
    icon: 'bi-check-circle',
  },
  {
    label: 'Rejected',
    value: statistics.value.rejected || 0,
    icon: 'bi-x-circle',
  },
])

const filteredApplications = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return applications.value.filter((application) => {
    const matchesSearch =
      !search ||
      application.company_name?.toLowerCase().includes(search) ||
      application.drive_name?.toLowerCase().includes(search)

    const matchesStatus =
      !filters.status ||
      application.status === filters.status

    return matchesSearch && matchesStatus
  })
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

const fetchApplications = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await studentAPI.getApplications()

    applications.value = response.data.applications || []
    statistics.value = response.data.statistics || {}
  } catch (requestError) {
    console.error(
      'Unable to load student applications:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load your applications.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
}

const viewApplication = (id) => {
  router.push(`/student/applications/${id}`)
}

onMounted(() => {
  fetchApplications()
})
</script>

<template>
  <div class="applications-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">My applications</h1>

        <p class="page-subtitle">
          Track every placement application and recruitment decision.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn btn-outline-secondary"
          :disabled="loading || refreshing"
          @click="fetchApplications(true)"
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
          @click="router.push('/student/drives')"
        >
          <i class="bi bi-briefcase"></i>
          Browse drives
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
          Loading applications
        </span>
      </div>

      <span>Loading your applications...</span>
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

      <section class="card filters-card">
        <div class="filters">
          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search company or placement drive"
              aria-label="Search applications"
            />
          </div>

          <select
            v-model="filters.status"
            class="form-select"
            aria-label="Filter by application status"
          >
            <option value="">All statuses</option>
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>

          <button
            v-if="filters.search || filters.status"
            type="button"
            class="btn btn-outline-secondary"
            @click="resetFilters"
          >
            Clear
          </button>
        </div>

        <span class="result-count">
          {{ filteredApplications.length }}
          {{
            filteredApplications.length === 1
              ? 'application'
              : 'applications'
          }}
        </span>
      </section>

      <section
        v-if="filteredApplications.length === 0"
        class="empty-state applications-empty"
      >
        <i class="bi bi-file-earmark-text"></i>

        <strong>
          {{
            applications.length === 0
              ? 'No applications yet'
              : 'No matching applications'
          }}
        </strong>

        <span>
          {{
            applications.length === 0
              ? 'Browse approved placement drives and submit your first application.'
              : 'Try changing your search or status filter.'
          }}
        </span>

        <button
          v-if="applications.length === 0"
          type="button"
          class="btn btn-primary btn-sm"
          @click="router.push('/student/drives')"
        >
          Browse placement drives
        </button>

        <button
          v-else
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="resetFilters"
        >
          Clear filters
        </button>
      </section>

      <section
        v-else
        class="card applications-card"
      >
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Placement drive</th>
                <th>Applied on</th>
                <th>Status</th>
                <th>Interview</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="application in filteredApplications"
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
                  <div class="drive-cell">
                    <strong>
                      {{ application.drive_name }}
                    </strong>

                    <span>
                      Drive #{{ application.drive_id }}
                    </span>
                  </div>
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
                  <div
                    v-if="application.interview_date"
                    class="interview-cell"
                  >
                    <i class="bi bi-calendar-event"></i>

                    <span>
                      {{
                        formatDateTime(
                          application.interview_date,
                        )
                      }}
                    </span>
                  </div>

                  <span
                    v-else
                    class="not-scheduled"
                  >
                    Not scheduled
                  </span>
                </td>

                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    @click="viewApplication(application.id)"
                  >
                    View
                    <i class="bi bi-arrow-up-right ms-1"></i>
                  </button>
                </td>
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
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 17px;
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
.summary-card div > span {
  display: block;
}

.summary-card strong {
  color: var(--color-primary);
  font-size: 1.25rem;
  font-weight: 650;
}

.summary-card div > span {
  margin-top: 2px;
  color: var(--color-text-muted);
  font-size: 0.72rem;
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

.search-field > i {
  position: absolute;
  top: 50%;
  left: 13px;
  z-index: 1;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  transform: translateY(-50%);
}

.search-field .form-control {
  width: 330px;
  padding-left: 36px;
}

.filters .form-select {
  width: 175px;
}

.result-count {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.applications-card {
  margin-bottom: 0;
  overflow: hidden;
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 160px;
}

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
  font-size: 0.75rem;
  font-weight: 700;
}

.company-cell strong,
.drive-cell strong {
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 600;
}

.drive-cell {
  min-width: 170px;
}

.drive-cell strong,
.drive-cell span {
  display: block;
}

.drive-cell span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.67rem;
}

.interview-cell {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 180px;
  color: var(--color-text);
  font-size: 0.73rem;
}

.interview-cell i {
  color: var(--color-accent);
}

.not-scheduled {
  color: var(--color-text-muted);
  font-size: 0.73rem;
}

.applications-empty {
  min-height: 350px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.applications-empty strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.applications-empty span {
  max-width: 430px;
  font-size: 0.78rem;
}

@media (max-width: 1199.98px) {
  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .filters-card {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions,
  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions .btn {
    justify-content: center;
  }

  .search-field .form-control,
  .filters .form-select {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>