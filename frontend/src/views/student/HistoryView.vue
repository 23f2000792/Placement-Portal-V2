<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'

const router = useRouter()

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const history = ref([])

const currentPage = ref(1)
const perPage = 10

const filters = reactive({
  search: '',
  year: '',
  status: '',
})

const availableYears = computed(() => {
  const years = history.value
    .filter((item) => item.applied_at)
    .map((item) => new Date(item.applied_at).getFullYear())

  return [...new Set(years)].sort((a, b) => b - a)
})

const filteredHistory = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return history.value.filter((item) => {
    const matchesSearch =
      !search ||
      item.company_name?.toLowerCase().includes(search) ||
      item.drive_name?.toLowerCase().includes(search) ||
      item.job_title?.toLowerCase().includes(search)

    const matchesYear =
      !filters.year ||
      new Date(item.applied_at).getFullYear() ===
        Number(filters.year)

    const matchesStatus =
      !filters.status ||
      item.final_status === filters.status

    return matchesSearch && matchesYear && matchesStatus
  })
})

const summary = computed(() => {
  const items = filteredHistory.value

  return {
    total: items.length,
    selected: items.filter(
      (item) => item.final_status === 'selected',
    ).length,
    shortlisted: items.filter(
      (item) => item.final_status === 'shortlisted',
    ).length,
    rejected: items.filter(
      (item) => item.final_status === 'rejected',
    ).length,
  }
})

const successRate = computed(() => {
  if (!summary.value.total) return 0

  return Math.round(
    (summary.value.selected / summary.value.total) * 100,
  )
})

const totalPages = computed(() =>
  Math.max(
    1,
    Math.ceil(filteredHistory.value.length / perPage),
  ),
)

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * perPage

  return filteredHistory.value.slice(
    start,
    start + perPage,
  )
})

const pageStart = computed(() => {
  if (!filteredHistory.value.length) return 0

  return (currentPage.value - 1) * perPage + 1
})

const pageEnd = computed(() =>
  Math.min(
    currentPage.value * perPage,
    filteredHistory.value.length,
  ),
)

const summaryCards = computed(() => [
  {
    label: 'Applications',
    value: summary.value.total,
    icon: 'bi-file-earmark-text',
  },
  {
    label: 'Selected',
    value: summary.value.selected,
    icon: 'bi-check-circle',
  },
  {
    label: 'Shortlisted',
    value: summary.value.shortlisted,
    icon: 'bi-person-check',
  },
  {
    label: 'Success rate',
    value: `${successRate.value}%`,
    icon: 'bi-graph-up-arrow',
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

const fetchHistory = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await studentAPI.getHistory()

    history.value = response.data.history || []
  } catch (requestError) {
    console.error(
      'Unable to load placement history:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load your placement history.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.year = ''
  filters.status = ''
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return

  currentPage.value = page
}

const viewApplication = (id) => {
  router.push(`/student/applications/${id}`)
}

watch(
  filters,
  () => {
    currentPage.value = 1
  },
  { deep: true },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="history-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Placement history</h1>

        <p class="page-subtitle">
          Review your complete placement journey and recruitment
          outcomes.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading || refreshing"
        @click="fetchHistory(true)"
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
          Loading placement history
        </span>
      </div>

      <span>Loading placement history...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Placement history could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchHistory()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section class="summary-grid">
        <article
          v-for="item in summaryCards"
          :key="item.label"
          class="summary-card"
        >
          <span class="summary-icon">
            <i :class="['bi', item.icon]"></i>
          </span>

          <div>
            <strong>{{ item.value }}</strong>
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
              placeholder="Search company, drive or role"
              aria-label="Search placement history"
            />
          </div>

          <select
            v-model="filters.year"
            class="form-select"
            aria-label="Filter by year"
          >
            <option value="">All years</option>

            <option
              v-for="year in availableYears"
              :key="year"
              :value="year"
            >
              {{ year }}
            </option>
          </select>

          <select
            v-model="filters.status"
            class="form-select"
            aria-label="Filter by status"
          >
            <option value="">All statuses</option>
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="selected">Selected</option>
            <option value="rejected">Rejected</option>
          </select>

          <button
            v-if="
              filters.search ||
              filters.year ||
              filters.status
            "
            type="button"
            class="btn btn-outline-secondary"
            @click="resetFilters"
          >
            Clear
          </button>
        </div>

        <span class="result-count">
          {{ filteredHistory.length }}
          {{
            filteredHistory.length === 1
              ? 'record'
              : 'records'
          }}
        </span>
      </section>

      <section
        v-if="filteredHistory.length === 0"
        class="empty-state history-empty"
      >
        <i class="bi bi-clock-history"></i>

        <strong>
          {{
            history.length === 0
              ? 'No placement history yet'
              : 'No matching records'
          }}
        </strong>

        <span>
          {{
            history.length === 0
              ? 'Your placement applications and recruitment outcomes will appear here.'
              : 'Try changing your search or filters.'
          }}
        </span>

        <button
          v-if="history.length === 0"
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
        class="card history-card"
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
                <th>Selected on</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in paginatedHistory"
                :key="item.id"
              >
                <td>
                  <div class="company-cell">
                    <span class="company-avatar">
                      {{
                        item.company_name
                          ?.charAt(0)
                          .toUpperCase() || 'C'
                      }}
                    </span>

                    <strong>{{ item.company_name }}</strong>
                  </div>
                </td>

                <td>
                  <div class="drive-cell">
                    <strong>{{ item.drive_name }}</strong>
                    <span>{{ item.job_title }}</span>
                  </div>
                </td>

                <td>{{ formatDate(item.applied_at) }}</td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(item.final_status)"
                  >
                    {{ formatStatus(item.final_status) }}
                  </span>
                </td>

                <td>
                  <span
                    v-if="item.interview_date"
                    class="date-detail"
                  >
                    <i class="bi bi-calendar-event"></i>
                    {{ formatDate(item.interview_date) }}
                  </span>

                  <span
                    v-else
                    class="not-available"
                  >
                    —
                  </span>
                </td>

                <td>
                  <span
                    v-if="item.selected_at"
                    class="date-detail"
                  >
                    <i class="bi bi-check-circle"></i>
                    {{ formatDate(item.selected_at) }}
                  </span>

                  <span
                    v-else
                    class="not-available"
                  >
                    —
                  </span>
                </td>

                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    @click="viewApplication(item.id)"
                  >
                    View
                    <i class="bi bi-arrow-up-right ms-1"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer
          v-if="totalPages > 1"
          class="table-footer"
        >
          <span>
            Showing {{ pageStart }}–{{ pageEnd }} of
            {{ filteredHistory.length }}
          </span>

          <nav aria-label="Placement history pages">
            <ul class="pagination mb-0">
              <li
                class="page-item"
                :class="{ disabled: currentPage === 1 }"
              >
                <button
                  type="button"
                  class="page-link"
                  :disabled="currentPage === 1"
                  @click="changePage(currentPage - 1)"
                >
                  <i class="bi bi-chevron-left"></i>
                </button>
              </li>

              <li
                v-for="page in totalPages"
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
                  :disabled="currentPage === totalPages"
                  @click="changePage(currentPage + 1)"
                >
                  <i class="bi bi-chevron-right"></i>
                </button>
              </li>
            </ul>
          </nav>
        </footer>
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
.summary-card div > span {
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
  width: 300px;
  padding-left: 36px;
}

.filters .form-select {
  width: 145px;
}

.result-count {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.history-card {
  margin-bottom: 0;
  overflow: hidden;
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 150px;
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
  font-size: 0.68rem;
}

.date-detail {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 110px;
  color: var(--color-text);
  font-size: 0.72rem;
}

.date-detail i {
  color: var(--color-accent);
}

.not-available {
  color: var(--color-text-muted);
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 18px;
  border-top: 1px solid var(--color-border);
}

.table-footer > span {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.history-empty {
  min-height: 350px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.history-empty strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.history-empty span {
  max-width: 430px;
  font-size: 0.78rem;
}

@media (max-width: 991.98px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filters-card {
    align-items: stretch;
    flex-direction: column;
  }

  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .search-field .form-control,
  .filters .form-select {
    width: 100%;
  }

  .table-footer {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 575.98px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>