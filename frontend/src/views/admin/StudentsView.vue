<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loading = ref(true)
const error = ref('')
const students = ref([])
const processingId = ref(null)

const filters = reactive({
  branch: '',
  year: '',
  status: '',
  search: '',
})

const currentPage = ref(1)
const perPage = 10

const branches = computed(() => {
  return [
    ...new Set(
      students.value
        .map((student) => student.branch)
        .filter(Boolean),
    ),
  ].sort()
})

const graduationYears = computed(() => {
  return [
    ...new Set(
      students.value
        .map((student) => student.graduation_year)
        .filter(Boolean),
    ),
  ].sort((a, b) => Number(a) - Number(b))
})

const filteredStudents = computed(() => {
  const search = filters.search.trim().toLowerCase()

  return students.value.filter((student) => {
    const matchesBranch =
      !filters.branch || student.branch === filters.branch

    const matchesYear =
      !filters.year ||
      String(student.graduation_year) === String(filters.year)

    let matchesStatus = true

    if (filters.status === 'active') {
      matchesStatus =
        !student.is_blacklisted && !student.is_placed
    } else if (filters.status === 'blacklisted') {
      matchesStatus = Boolean(student.is_blacklisted)
    } else if (filters.status === 'placed') {
      matchesStatus = Boolean(student.is_placed)
    }

    const matchesSearch =
      !search ||
      student.name?.toLowerCase().includes(search) ||
      student.roll_number?.toLowerCase().includes(search) ||
      student.email?.toLowerCase().includes(search)

    return (
      matchesBranch &&
      matchesYear &&
      matchesStatus &&
      matchesSearch
    )
  })
})

const totalCount = computed(() => students.value.length)

const activeCount = computed(() =>
  students.value.filter(
    (student) =>
      !student.is_blacklisted && !student.is_placed,
  ).length,
)

const blacklistedCount = computed(() =>
  students.value.filter((student) => student.is_blacklisted).length,
)

const placedCount = computed(() =>
  students.value.filter((student) => student.is_placed).length,
)

const totalPages = computed(() =>
  Math.max(
    1,
    Math.ceil(filteredStudents.value.length / perPage),
  ),
)

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * perPage

  return filteredStudents.value.slice(start, start + perPage)
})

const rangeStart = computed(() => {
  if (!filteredStudents.value.length) return 0

  return (currentPage.value - 1) * perPage + 1
})

const rangeEnd = computed(() =>
  Math.min(
    currentPage.value * perPage,
    filteredStudents.value.length,
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
    label: 'Total students',
    value: totalCount.value,
    icon: 'bi-people',
  },
  {
    label: 'Active',
    value: activeCount.value,
    icon: 'bi-person-check',
  },
  {
    label: 'Placed',
    value: placedCount.value,
    icon: 'bi-briefcase',
  },
  {
    label: 'Blacklisted',
    value: blacklistedCount.value,
    icon: 'bi-slash-circle',
  },
])

const getDisplayStatus = (student) => {
  if (student.is_blacklisted) return 'Blacklisted'
  if (student.is_placed) return 'Placed'
  return 'Active'
}

const getStatusClass = (student) => {
  if (student.is_blacklisted) return 'bg-secondary'
  if (student.is_placed) return 'bg-primary'

  return 'bg-success'
}

const fetchStudents = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminAPI.getStudents()

    students.value = response.data.students || []
  } catch (requestError) {
    console.error('Unable to load students:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load student records.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.branch = ''
  filters.year = ''
  filters.status = ''
  filters.search = ''
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return

  currentPage.value = page
}

const blacklistStudent = async (id) => {
  const reason = window.prompt('Enter the blacklist reason:')

  if (!reason?.trim()) return

  processingId.value = id

  try {
    await adminAPI.blacklistStudent(id, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages(
      'Student blacklisted successfully.',
    )

    await fetchStudents()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to blacklist the student.',
    )
  } finally {
    processingId.value = null
  }
}

const activateStudent = async (id) => {
  if (!window.confirm('Reactivate this student account?')) return

  processingId.value = id

  try {
    await adminAPI.activateStudent(id)

    messageStore.updateSuccessMessages(
      'Student account reactivated.',
    )

    await fetchStudents()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reactivate the student.',
    )
  } finally {
    processingId.value = null
  }
}

const viewDetails = (id) => {
  router.push(`/admin/students/${id}`)
}

watch(
  () => [
    filters.branch,
    filters.year,
    filters.status,
    filters.search,
  ],
  () => {
    currentPage.value = 1
  },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(fetchStudents)
</script>

<template>
  <div class="students-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Students</h1>

        <p class="page-subtitle">
          Search student records and manage placement portal access.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading"
        @click="fetchStudents"
      >
        <i class="bi bi-arrow-clockwise"></i>
        Refresh
      </button>
    </header>

    <section
      class="summary-grid"
      aria-label="Student statistics"
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
          <h2>Student records</h2>

          <p>
            {{ filteredStudents.length }}
            {{
              filteredStudents.length === 1
                ? 'student'
                : 'students'
            }}
            found
          </p>
        </div>

        <div class="filters">
          <select
            v-model="filters.branch"
            class="form-select"
            aria-label="Filter students by branch"
          >
            <option value="">All branches</option>

            <option
              v-for="branch in branches"
              :key="branch"
              :value="branch"
            >
              {{ branch }}
            </option>
          </select>

          <select
            v-model="filters.year"
            class="form-select year-filter"
            aria-label="Filter students by graduation year"
          >
            <option value="">All years</option>

            <option
              v-for="year in graduationYears"
              :key="year"
              :value="year"
            >
              {{ year }}
            </option>
          </select>

          <select
            v-model="filters.status"
            class="form-select status-filter"
            aria-label="Filter students by status"
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="placed">Placed</option>
            <option value="blacklisted">Blacklisted</option>
          </select>

          <div class="search-field">
            <i class="bi bi-search"></i>

            <input
              v-model="filters.search"
              type="search"
              class="form-control"
              placeholder="Search name, roll number or email"
              aria-label="Search students"
            />
          </div>

          <button
            v-if="
              filters.branch ||
              filters.year ||
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
            Loading students
          </span>
        </div>

        <span>Loading student records...</span>
      </div>

      <div
        v-else-if="error"
        class="page-state error-state"
      >
        <i class="bi bi-exclamation-circle"></i>

        <div>
          <strong>Student records could not be loaded</strong>
          <p>{{ error }}</p>
        </div>

        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="fetchStudents"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="paginatedStudents.length === 0"
        class="empty-state"
      >
        <i class="bi bi-people"></i>
        <strong>No students found</strong>

        <span>
          Try changing the current search or filters.
        </span>
      </div>

      <template v-else>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Roll number</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Graduation</th>
                <th>Contact</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="student in paginatedStudents"
                :key="student.id"
              >
                <td>
                  <div class="student-cell">
                    <span class="student-avatar">
                      {{
                        student.name?.charAt(0).toUpperCase() ||
                        'S'
                      }}
                    </span>

                    <div>
                      <strong>{{ student.name }}</strong>
                      <span>Student #{{ student.id }}</span>
                    </div>
                  </div>
                </td>

                <td>
                  {{ student.roll_number || 'Not provided' }}
                </td>

                <td>
                  {{ student.branch || 'Not provided' }}
                </td>

                <td>
                  <span class="cgpa-value">
                    {{
                      student.cgpa !== null &&
                      student.cgpa !== undefined
                        ? Number(student.cgpa).toFixed(2)
                        : '—'
                    }}
                  </span>
                </td>

                <td>
                  {{ student.graduation_year || '—' }}
                </td>

                <td>
                  <div class="contact-cell">
                    <a
                      v-if="student.email"
                      :href="`mailto:${student.email}`"
                    >
                      {{ student.email }}
                    </a>

                    <span v-else>Not provided</span>

                    <small>
                      {{ student.phone || 'No phone number' }}
                    </small>
                  </div>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="getStatusClass(student)"
                  >
                    {{ getDisplayStatus(student) }}
                  </span>
                </td>

                <td>
                  <div class="action-group">
                    <button
                      v-if="!student.is_blacklisted"
                      type="button"
                      class="btn btn-outline-secondary btn-sm"
                      :disabled="processingId === student.id"
                      @click="blacklistStudent(student.id)"
                    >
                      Blacklist
                    </button>

                    <button
                      v-else
                      type="button"
                      class="btn btn-outline-primary btn-sm"
                      :disabled="processingId === student.id"
                      @click="activateStudent(student.id)"
                    >
                      Reactivate
                    </button>

                    <button
                      type="button"
                      class="btn btn-outline-secondary btn-sm icon-button"
                      title="View student details"
                      aria-label="View student details"
                      @click="viewDetails(student.id)"
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
          v-if="filteredStudents.length > perPage"
          class="records-footer"
        >
          <span>
            Showing {{ rangeStart }}–{{ rangeEnd }} of
            {{ filteredStudents.length }}
          </span>

          <nav aria-label="Student pagination">
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
  width: 170px;
}

.filters .year-filter {
  width: 125px;
}

.filters .status-filter {
  width: 140px;
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
  width: 270px;
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
  gap: 11px;
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
.student-cell div > span,
.contact-cell a,
.contact-cell span,
.contact-cell small {
  display: block;
}

.student-cell strong {
  color: var(--color-primary);
  font-size: 0.85rem;
}

.student-cell div > span,
.contact-cell small {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.cgpa-value {
  color: var(--color-text);
  font-size: 0.825rem;
  font-weight: 600;
}

.contact-cell {
  min-width: 210px;
}

.contact-cell a,
.contact-cell > span {
  font-size: 0.8rem;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  min-width: 155px;
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
  .filters .year-filter,
  .filters .status-filter,
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