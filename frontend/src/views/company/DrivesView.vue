<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const drives = ref([])

const filters = reactive({
  status: '',
  search: '',
})

const currentPage = ref(1)
const perPage = 10

const filteredDrives = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return drives.value.filter((drive) => {
    const matchesStatus =
      !filters.status || drive.status === filters.status

    const matchesSearch =
      !search ||
      drive.drive_name?.toLowerCase().includes(search) ||
      drive.job_title?.toLowerCase().includes(search)

    return matchesStatus && matchesSearch
  })
})

const statusCounts = computed(() => {
  const counts = {
    total: drives.value.length,
    pending: 0,
    approved: 0,
    closed: 0,
  }

  drives.value.forEach((drive) => {
    if (Object.hasOwn(counts, drive.status)) {
      counts[drive.status] += 1
    }
  })

  return counts
})

const summaryCards = computed(() => [
  {
    label: 'Total drives',
    value: statusCounts.value.total,
    icon: 'bi-briefcase',
  },
  {
    label: 'Pending review',
    value: statusCounts.value.pending,
    icon: 'bi-clock',
  },
  {
    label: 'Approved',
    value: statusCounts.value.approved,
    icon: 'bi-check-circle',
  },
  {
    label: 'Closed',
    value: statusCounts.value.closed,
    icon: 'bi-archive',
  },
])

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredDrives.value.length / perPage)),
)

const paginatedDrives = computed(() => {
  const start = (currentPage.value - 1) * perPage

  return filteredDrives.value.slice(start, start + perPage)
})

const rangeStart = computed(() => {
  if (!filteredDrives.value.length) return 0

  return (currentPage.value - 1) * perPage + 1
})

const rangeEnd = computed(() =>
  Math.min(
    currentPage.value * perPage,
    filteredDrives.value.length,
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

const fetchDrives = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await companyAPI.getDrives()

    drives.value = response.data.drives || []
  } catch (requestError) {
    console.error('Unable to load placement drives:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load placement drives.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.search = ''
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return

  currentPage.value = page
}

const createDrive = () => {
  router.push('/company/drives/create')
}

const viewDrive = (id) => {
  router.push(`/company/drives/${id}`)
}

watch(
  () => [filters.status, filters.search],
  () => {
    currentPage.value = 1
  },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(fetchDrives)
</script>

<template>
  <div class="drives-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Placement drives</h1>

        <p class="page-subtitle">
          Create and manage your company's recruitment drives.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="createDrive"
      >
        <i class="bi bi-plus-lg"></i>
        Create drive
      </button>
    </header>

    <section
      class="summary-grid"
      aria-label="Placement drive statistics"
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

    <section class="card records-card">
      <div class="card-header records-header">
        <div>
          <h2>Drive records</h2>

          <p>
            {{ filteredDrives.length }}
            {{ filteredDrives.length === 1 ? 'drive' : 'drives' }}
            found
          </p>
        </div>

        <div class="filters">
          <select
            v-model="filters.status"
            class="form-select"
            aria-label="Filter placement drives by status"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="closed">Closed</option>
          </select>

          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search drive or job title"
              aria-label="Search placement drives"
            />
          </div>

          <button
            v-if="filters.status || filters.search"
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
          @click="fetchDrives"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="paginatedDrives.length === 0"
        class="empty-state"
      >
        <i class="bi bi-briefcase"></i>
        <strong>No placement drives found</strong>

        <span v-if="filters.status || filters.search">
          Try changing the current search or status filter.
        </span>

        <span v-else>
          Create your first placement drive to begin recruitment.
        </span>

        <button
          v-if="!filters.status && !filters.search"
          type="button"
          class="btn btn-primary btn-sm"
          @click="createDrive"
        >
          Create drive
        </button>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Placement drive</th>
                <th>Job title</th>
                <th>Eligibility</th>
                <th>Deadline</th>
                <th>Applicants</th>
                <th>Status</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="drive in paginatedDrives"
                :key="drive.id"
              >
                <td>
                  <div class="drive-cell">
                    <span class="drive-icon">
                      <i class="bi bi-briefcase"></i>
                    </span>

                    <div>
                      <strong>{{ drive.drive_name }}</strong>
                      <span>Drive #{{ drive.id }}</span>
                    </div>
                  </div>
                </td>

                <td>{{ drive.job_title }}</td>

                <td>
                  <div class="eligibility-cell">
                    <span v-if="drive.min_cgpa">
                      CGPA {{ drive.min_cgpa }}+
                    </span>

                    <span v-if="drive.allowed_branches">
                      {{ drive.allowed_branches }}
                    </span>

                    <span
                      v-if="
                        !drive.min_cgpa &&
                        !drive.allowed_branches
                      "
                    >
                      No restrictions
                    </span>
                  </div>
                </td>

                <td>
                  {{ formatDate(drive.application_deadline) }}
                </td>

                <td>
                  <strong class="applicant-count">
                    {{
                      Number(
                        drive.application_count || 0,
                      ).toLocaleString('en-IN')
                    }}
                  </strong>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(drive.status)"
                  >
                    {{ formatStatus(drive.status) }}
                  </span>
                </td>

                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    @click="viewDrive(drive.id)"
                  >
                    Manage
                    <i class="bi bi-arrow-up-right ms-1"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer
          v-if="filteredDrives.length > perPage"
          class="records-footer"
        >
          <span>
            Showing {{ rangeStart }}–{{ rangeEnd }} of
            {{ filteredDrives.length }}
          </span>

          <nav aria-label="Placement drive pagination">
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
                :class="{ active: currentPage === page }"
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
  width: 260px;
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

.drive-cell {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 190px;
}

.drive-icon {
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
}

.drive-cell strong,
.drive-cell div > span {
  display: block;
}

.drive-cell strong {
  color: var(--color-primary);
  font-size: 0.85rem;
}

.drive-cell div > span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.eligibility-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 130px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.applicant-count {
  color: var(--color-primary);
  font-size: 0.85rem;
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