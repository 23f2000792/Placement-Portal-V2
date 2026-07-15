<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const error = ref('')
const drives = ref([])
const processingId = ref(null)

const filters = reactive({
  status: '',
  company_id: '',
  search: '',
})

const currentPage = ref(1)
const perPage = 10

const companies = computed(() => {
  const companyMap = new Map()

  drives.value.forEach((drive) => {
    if (drive.company_id && drive.company_name) {
      companyMap.set(drive.company_id, {
        id: drive.company_id,
        company_name: drive.company_name,
      })
    }
  })

  return Array.from(companyMap.values()).sort((a, b) =>
    a.company_name.localeCompare(b.company_name),
  )
})

const filteredDrives = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return drives.value.filter((drive) => {
    const matchesStatus =
      !filters.status || drive.status === filters.status

    const matchesCompany =
      !filters.company_id ||
      String(drive.company_id) === String(filters.company_id)

    const matchesSearch =
      !search ||
      drive.drive_name?.toLowerCase().includes(search) ||
      drive.job_title?.toLowerCase().includes(search) ||
      drive.company_name?.toLowerCase().includes(search)

    return matchesStatus && matchesCompany && matchesSearch
  })
})

const totalCount = computed(() => drives.value.length)

const pendingCount = computed(() =>
  drives.value.filter((drive) => drive.status === 'pending').length,
)

const approvedCount = computed(() =>
  drives.value.filter((drive) => drive.status === 'approved').length,
)

const closedCount = computed(() =>
  drives.value.filter((drive) => drive.status === 'closed').length,
)

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
  Math.min(currentPage.value * perPage, filteredDrives.value.length),
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

const summaryCards = computed(() => [
  {
    label: 'Total drives',
    value: totalCount.value,
    icon: 'bi-briefcase-fill',
  },
  {
    label: 'Pending review',
    value: pendingCount.value,
    icon: 'bi-hourglass-split',
  },
  {
    label: 'Approved',
    value: approvedCount.value,
    icon: 'bi-patch-check-fill',
  },
  {
    label: 'Closed',
    value: closedCount.value,
    icon: 'bi-archive-fill',
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
    const response = await adminAPI.getDrives()
    drives.value = response.data.drives || []
  } catch (requestError) {
    console.error('Unable to load placement drives:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load placement drive records.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.company_id = ''
  filters.search = ''
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

const approveDrive = async (id) => {
  if (!window.confirm('Approve this placement drive?')) return

  processingId.value = id

  try {
    await adminAPI.approveDrive(id)

    messageStore.updateSuccessMessages(
      'Placement drive approved successfully.',
    )

    await fetchDrives()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the placement drive.',
    )
  } finally {
    processingId.value = null
  }
}

const rejectDrive = async (id) => {
  if (!window.confirm('Reject this placement drive?')) return

  processingId.value = id

  try {
    await adminAPI.rejectDrive(id)
    messageStore.updateSuccessMessages('Placement drive rejected.')
    await fetchDrives()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the placement drive.',
    )
  } finally {
    processingId.value = null
  }
}

const closeDrive = async (id) => {
  if (
    !window.confirm(
      'Close this placement drive? Students will no longer be able to apply.',
    )
  ) {
    return
  }

  processingId.value = id

  try {
    await adminAPI.closeDrive(id)
    messageStore.updateSuccessMessages('Placement drive closed.')
    await fetchDrives()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to close the placement drive.',
    )
  } finally {
    processingId.value = null
  }
}

const viewDetails = (id) => {
  router.push(`/admin/drives/${id}`)
}

watch(
  () => [filters.status, filters.company_id, filters.search],
  () => {
    currentPage.value = 1
  },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

const sendingReminders = ref(false)

const sendDeadlineReminders = async () => {
  try {
    const response = await adminAPI.sendDeadlineReminders()

    messageStore.showSuccess(
      response.data.message ||
      "Deadline reminder job has been triggered successfully. Eligible students will receive reminder emails shortly."
    )
  } catch (error) {
    console.error(error)

    messageStore.showError(
      error.response?.data?.message ||
      "Unable to trigger deadline reminder job."
    )
  }
}

onMounted(fetchDrives)
</script>

<template>
  <div class="drives-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Placement drives</h1>

        <p class="page-subtitle">
          Review, approve and manage company recruitment drives.
        </p>
      </div>

      <button
        class="btn btn-primary"
        :disabled="sendingReminders"
        @click="sendDeadlineReminders"
      >
        <i class="bi bi-bell me-2"></i>
        {{ sendingReminders ? 'Sending reminders...' : 'Send deadline reminders' }}
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
        <span class="summary-icon" aria-hidden="true">
          <i :class="['bi', item.icon]"></i>
        </span>

        <div class="summary-content">
          <strong class="summary-value">
            {{ item.value.toLocaleString('en-IN') }}
          </strong>
          <span class="summary-label">{{ item.label }}</span>
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
            aria-label="Filter drives by status"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="closed">Closed</option>
          </select>

          <select
            v-model="filters.company_id"
            class="form-select company-filter"
            aria-label="Filter drives by company"
          >
            <option value="">All companies</option>

            <option
              v-for="company in companies"
              :key="company.id"
              :value="company.id"
            >
              {{ company.company_name }}
            </option>
          </select>

          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search drive, role or company"
              aria-label="Search placement drives"
            />
          </div>

          <button
            v-if="
              filters.status ||
              filters.company_id ||
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
          <span class="visually-hidden">Loading placement drives</span>
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
        <span>Try changing the current search or filters.</span>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Drive</th>
                <th>Company</th>
                <th>Job title</th>
                <th>Eligibility</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Created</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="drive in paginatedDrives"
                :key="drive.id"
              >
                <td>
                  <div class="drive-cell">
                    <strong>{{ drive.drive_name }}</strong>
                    <span>Drive #{{ drive.id }}</span>
                  </div>
                </td>

                <td>
                  <RouterLink
                    :to="`/admin/companies/${drive.company_id}`"
                    class="company-link"
                  >
                    {{ drive.company_name }}
                  </RouterLink>
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

                <td>{{ formatDate(drive.application_deadline) }}</td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(drive.status)"
                  >
                    {{ formatStatus(drive.status) }}
                  </span>
                </td>

                <td>{{ formatDate(drive.created_at) }}</td>

                <td>
                  <div class="action-group">
                    <template v-if="drive.status === 'pending'">
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        :disabled="processingId === drive.id"
                        @click="rejectDrive(drive.id)"
                      >
                        Reject
                      </button>

                      <button
                        type="button"
                        class="btn btn-primary btn-sm"
                        :disabled="processingId === drive.id"
                        @click="approveDrive(drive.id)"
                      >
                        Approve
                      </button>
                    </template>

                    <button
                      v-else-if="drive.status === 'approved'"
                      type="button"
                      class="btn btn-outline-secondary btn-sm"
                      :disabled="processingId === drive.id"
                      @click="closeDrive(drive.id)"
                    >
                      Close
                    </button>

                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm icon-button"
                      title="View drive details"
                      aria-label="View drive details"
                      @click="viewDetails(drive.id)"
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
                :class="{ disabled: currentPage === totalPages }"
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
  gap: 16px;
  min-height: 92px;
  padding: 18px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.summary-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.summary-icon .bi {
  display: inline-block;
  margin: 0;
  padding: 0;
  color: inherit;
  background: transparent;
  font-size: 1rem;
  line-height: 1;
}

.summary-icon .bi::before {
  display: inline-block;
  line-height: 1;
  vertical-align: -0.125em;
}

.summary-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  min-width: 0;
}

.summary-value {
  display: block;
  margin: 0;
  color: var(--color-primary);
  font-size: 1.35rem;
  font-weight: 650;
  line-height: 1;
}

.summary-label {
  display: block;
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  line-height: 1.25;
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
  width: 145px;
}

.filters .company-filter {
  width: 190px;
}

.search-field {
  position: relative;
}

.search-field i {
  position: absolute;
  top: 50%;
  left: 13px;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  transform: translateY(-50%);
}

.search-field .form-control {
  width: 250px;
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

.drive-cell strong,
.drive-cell span {
  display: block;
}

.drive-cell strong {
  min-width: 150px;
  color: var(--color-primary);
  font-size: 0.85rem;
}

.drive-cell span {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.company-link {
  font-size: 0.825rem;
  font-weight: 600;
}

.eligibility-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 130px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  min-width: 190px;
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

@media (max-width: 1199.98px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .records-header {
    align-items: stretch;
    flex-direction: column;
  }

  .filters {
    flex-wrap: wrap;
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
  .filters .company-filter,
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