<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const error = ref('')
const companies = ref([])
const processingId = ref(null)

const filters = reactive({
  status: '',
  search: '',
})

const currentPage = ref(1)
const perPage = 10

const totalCount = computed(() => companies.value.length)

const pendingCount = computed(() =>
  companies.value.filter(
    (company) => company.approval_status === 'pending',
  ).length,
)

const approvedCount = computed(() =>
  companies.value.filter(
    (company) =>
      company.approval_status === 'approved' &&
      !company.is_blacklisted,
  ).length,
)

const blacklistedCount = computed(() =>
  companies.value.filter((company) => company.is_blacklisted).length,
)

const filteredCompanies = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return companies.value.filter((company) => {
    let matchesStatus = true

    if (filters.status === 'blacklisted') {
      matchesStatus = Boolean(company.is_blacklisted)
    } else if (filters.status === 'approved') {
      matchesStatus =
        company.approval_status === 'approved' &&
        !company.is_blacklisted
    } else if (filters.status) {
      matchesStatus = company.approval_status === filters.status
    }

    const matchesSearch =
      !search ||
      company.company_name?.toLowerCase().includes(search) ||
      company.hr_name?.toLowerCase().includes(search) ||
      company.hr_email?.toLowerCase().includes(search)

    return matchesStatus && matchesSearch
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredCompanies.value.length / perPage)),
)

const paginatedCompanies = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredCompanies.value.slice(start, start + perPage)
})

const rangeStart = computed(() => {
  if (!filteredCompanies.value.length) return 0
  return (currentPage.value - 1) * perPage + 1
})

const rangeEnd = computed(() =>
  Math.min(
    currentPage.value * perPage,
    filteredCompanies.value.length,
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

const summaryCards = computed(() => [
  {
    label: 'Total companies',
    value: totalCount.value,
    icon: 'bi-buildings',
  },
  {
    label: 'Pending review',
    value: pendingCount.value,
    icon: 'bi-clock',
  },
  {
    label: 'Approved',
    value: approvedCount.value,
    icon: 'bi-check-circle',
  },
  {
    label: 'Blacklisted',
    value: blacklistedCount.value,
    icon: 'bi-slash-circle',
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

const getDisplayStatus = (company) => {
  if (company.is_blacklisted) return 'Blacklisted'

  const status = company.approval_status || 'unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (company) => {
  if (company.is_blacklisted) return 'bg-secondary'

  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
  }

  return classes[company.approval_status] || 'bg-secondary'
}

const fetchCompanies = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminAPI.getCompanies()
    companies.value = response.data.companies || []
  } catch (requestError) {
    console.error('Unable to load companies:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load company records.'
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

const approveCompany = async (id) => {
  if (!window.confirm('Approve this company registration?')) return

  processingId.value = id

  try {
    await adminAPI.approveCompany(id)
    messageStore.updateSuccessMessages('Company approved successfully.')
    await fetchCompanies()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the company.',
    )
  } finally {
    processingId.value = null
  }
}

const rejectCompany = async (id) => {
  const reason = window.prompt('Enter the rejection reason:')

  if (!reason?.trim()) return

  processingId.value = id

  try {
    await adminAPI.rejectCompany(id, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages('Company registration rejected.')
    await fetchCompanies()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the company.',
    )
  } finally {
    processingId.value = null
  }
}

const blacklistCompany = async (id) => {
  const reason = window.prompt('Enter the blacklist reason:')

  if (!reason?.trim()) return

  processingId.value = id

  try {
    await adminAPI.blacklistCompany(id, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages('Company blacklisted successfully.')
    await fetchCompanies()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to blacklist the company.',
    )
  } finally {
    processingId.value = null
  }
}

const activateCompany = async (id) => {
  if (!window.confirm('Reactivate this company account?')) return

  processingId.value = id

  try {
    await adminAPI.activateCompany(id)
    messageStore.updateSuccessMessages('Company account reactivated.')
    await fetchCompanies()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reactivate the company.',
    )
  } finally {
    processingId.value = null
  }
}

const viewDetails = (id) => {
  router.push(`/admin/companies/${id}`)
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

onMounted(fetchCompanies)
</script>

<template>
  <div class="companies-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Companies</h1>

        <p class="page-subtitle">
          Review registrations and manage company access.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading"
        @click="fetchCompanies"
      >
        <i class="bi bi-arrow-clockwise"></i>
        Refresh
      </button>
    </header>

    <section
      class="summary-grid"
      aria-label="Company statistics"
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
          <strong>{{ item.value.toLocaleString('en-IN') }}</strong>
          <span>{{ item.label }}</span>
        </div>
      </article>
    </section>

    <section class="card records-card">
      <div class="card-header records-header">
        <div>
          <h2>Company records</h2>

          <p>
            {{ filteredCompanies.length }}
            {{ filteredCompanies.length === 1 ? 'company' : 'companies' }}
            found
          </p>
        </div>

        <div class="filters">
          <select
            v-model="filters.status"
            class="form-select"
            aria-label="Filter companies by status"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="blacklisted">Blacklisted</option>
          </select>

          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search company or HR contact"
              aria-label="Search companies"
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
          <span class="visually-hidden">Loading companies</span>
        </div>

        <span>Loading company records...</span>
      </div>

      <div
        v-else-if="error"
        class="page-state error-state"
      >
        <i class="bi bi-exclamation-circle"></i>

        <div>
          <strong>Company records could not be loaded</strong>
          <p>{{ error }}</p>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="fetchCompanies"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="paginatedCompanies.length === 0"
        class="empty-state"
      >
        <i class="bi bi-buildings"></i>
        <strong>No companies found</strong>

        <span>
          Try changing the current status or search filter.
        </span>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Company</th>
                <th>HR contact</th>
                <th>Contact details</th>
                <th>Status</th>
                <th>Registered</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="company in paginatedCompanies"
                :key="company.id"
              >
                <td>
                  <div class="company-cell">
                    <span class="company-avatar">
                      {{ company.company_name?.charAt(0).toUpperCase() || 'C' }}
                    </span>

                    <div>
                      <strong>{{ company.company_name }}</strong>
                      <span>Company #{{ company.id }}</span>
                    </div>
                  </div>
                </td>

                <td>
                  {{ company.hr_name || 'Not provided' }}
                </td>

                <td>
                  <div class="contact-cell">
                    <a
                      v-if="company.hr_email"
                      :href="`mailto:${company.hr_email}`"
                    >
                      {{ company.hr_email }}
                    </a>

                    <span v-else>Not provided</span>

                    <small>
                      {{ company.hr_phone || 'No phone number' }}
                    </small>
                  </div>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(company)"
                  >
                    {{ getDisplayStatus(company) }}
                  </span>
                </td>

                <td>
                  {{ formatDate(company.created_at) }}
                </td>

                <td>
                  <div class="action-group">
                    <template
                      v-if="company.approval_status === 'pending'"
                    >
                      <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        :disabled="processingId === company.id"
                        @click="rejectCompany(company.id)"
                      >
                        Reject
                      </button>

                      <button
                        type="button"
                        class="btn btn-primary btn-sm"
                        :disabled="processingId === company.id"
                        @click="approveCompany(company.id)"
                      >
                        Approve
                      </button>
                    </template>

                    <template
                      v-else-if="company.approval_status === 'approved'"
                    >
                      <button
                        v-if="!company.is_blacklisted"
                        type="button"
                        class="btn btn-outline-secondary btn-sm"
                        :disabled="processingId === company.id"
                        @click="blacklistCompany(company.id)"
                      >
                        Blacklist
                      </button>

                      <button
                        v-else
                        type="button"
                        class="btn btn-outline-primary btn-sm"
                        :disabled="processingId === company.id"
                        @click="activateCompany(company.id)"
                      >
                        Reactivate
                      </button>
                    </template>

                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm icon-button"
                      title="View company details"
                      aria-label="View company details"
                      @click="viewDetails(company.id)"
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
          v-if="filteredCompanies.length > perPage"
          class="records-footer"
        >
          <span>
            Showing {{ rangeStart }}–{{ rangeEnd }} of
            {{ filteredCompanies.length }}
          </span>

          <nav aria-label="Company pagination">
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
  letter-spacing: -0.03em;
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

.company-cell {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 180px;
}

.company-avatar {
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

.company-cell strong,
.company-cell div > span,
.contact-cell a,
.contact-cell span,
.contact-cell small {
  display: block;
}

.company-cell strong {
  color: var(--color-primary);
  font-size: 0.85rem;
}

.company-cell div > span,
.contact-cell small {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.contact-cell {
  min-width: 190px;
}

.contact-cell a,
.contact-cell > span {
  font-size: 0.8rem;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  min-width: 210px;
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