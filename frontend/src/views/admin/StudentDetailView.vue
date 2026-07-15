<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const studentId = route.params.id

const loading = ref(true)
const refreshing = ref(false)
const processingAction = ref(false)
const error = ref('')

const student = ref({})
const applications = ref([])

const applicationStats = computed(() => {
  const stats = {
    total: applications.value.length,
    shortlisted: 0,
    selected: 0,
    rejected: 0,
  }

  applications.value.forEach((application) => {
    const status = application.status?.toLowerCase()

    if (status === 'shortlisted') stats.shortlisted += 1
    if (status === 'selected') stats.selected += 1
    if (status === 'rejected') stats.rejected += 1
  })

  return stats
})

const summaryCards = computed(() => [
  {
    label: 'Applications',
    value: applicationStats.value.total,
    icon: 'bi-inbox-fill',
  },
  {
    label: 'Shortlisted',
    value: applicationStats.value.shortlisted,
    icon: 'bi-hourglass-split',
  },
  {
    label: 'Selected',
    value: applicationStats.value.selected,
    icon: 'bi-check-circle-fill',
  },
  {
    label: 'Rejected',
    value: applicationStats.value.rejected,
    icon: 'bi-x-circle-fill',
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

const getStudentStatus = () => {
  if (student.value.is_blacklisted) return 'Blacklisted'
  if (student.value.is_placed) return 'Placed'

  return 'Active'
}

const getStudentStatusClass = () => {
  if (student.value.is_blacklisted) return 'bg-secondary'
  if (student.value.is_placed) return 'bg-primary'

  return 'bg-success'
}

const getApplicationStatusClass = (status) => {
  const classes = {
    applied: 'bg-primary',
    shortlisted: 'bg-info',
    selected: 'bg-success',
    rejected: 'bg-danger',
  }

  return classes[status?.toLowerCase()] || 'bg-secondary'
}

const fetchStudentDetails = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await adminAPI.getStudentDetails(studentId)

    student.value = response.data.student || {}
    applications.value = response.data.applications || []
  } catch (requestError) {
    console.error('Unable to load student details:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load student details.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const blacklistStudent = async () => {
  const reason = window.prompt('Enter the blacklist reason:')

  if (!reason?.trim()) return

  processingAction.value = true

  try {
    await adminAPI.blacklistStudent(studentId, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages(
      'Student blacklisted successfully.',
    )

    await fetchStudentDetails(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to blacklist the student.',
    )
  } finally {
    processingAction.value = false
  }
}

const activateStudent = async () => {
  if (!window.confirm('Reactivate this student account?')) return

  processingAction.value = true

  try {
    await adminAPI.activateStudent(studentId)

    messageStore.updateSuccessMessages(
      'Student account reactivated.',
    )

    await fetchStudentDetails(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reactivate the student.',
    )
  } finally {
    processingAction.value = false
  }
}

const goBack = () => {
  router.push('/admin/students')
}

const viewApplication = (applicationId) => {
  router.push({
    path: '/admin/applications',
    query: {
      application: applicationId,
    },
  })
}

const downloadResume = async () => {
  try {
    await adminAPI.downloadStudentResume(
      studentId,
      student.value.resume_filename || 'resume.pdf',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to download the student resume.',
    )
  }
}

onMounted(() => {
  fetchStudentDetails()
})
</script>

<template>
  <div class="student-detail-page fade-in">
    <header class="page-header">
      <div>
        <button
          type="button"
          class="back-link"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Students
        </button>

        <h1 class="dashboard-title">Student details</h1>

        <p class="page-subtitle">
          Review academic information and placement application history.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary refresh-button"
        :disabled="refreshing || loading"
        @click="fetchStudentDetails(true)"
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
    >
      <div
        class="spinner-border spinner-border-sm"
        role="status"
      >
        <span class="visually-hidden">
          Loading student details
        </span>
      </div>

      <span>Loading student details...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Student details could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchStudentDetails()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section class="student-overview">
        <div class="student-identity">
          <span class="student-avatar">
            {{ student.name?.charAt(0).toUpperCase() || 'S' }}
          </span>

          <div class="identity-copy">
            <div class="student-title-row">
              <h2>{{ student.name }}</h2>

              <span
                class="badge"
                :class="getStudentStatusClass()"
              >
                {{ getStudentStatus() }}
              </span>
            </div>

            <p>
              {{ student.roll_number || 'Roll number not provided' }}
              <span class="separator">·</span>
              {{ student.branch || 'Branch not provided' }}
            </p>

            <span class="student-id">
              Student ID #{{ student.id }}
            </span>
          </div>

          <div class="student-actions">
            <button
              v-if="!student.is_blacklisted"
              type="button"
              class="btn btn-outline-secondary"
              :disabled="processingAction"
              @click="blacklistStudent"
            >
              <i class="bi bi-slash-circle"></i>
              Blacklist student
            </button>

            <button
              v-else
              type="button"
              class="btn btn-outline-primary"
              :disabled="processingAction"
              @click="activateStudent"
            >
              <i class="bi bi-arrow-counterclockwise"></i>
              Reactivate student
            </button>
          </div>
        </div>
      </section>

      <section
        class="summary-grid"
        aria-label="Student application statistics"
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
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </div>
        </article>
      </section>

      <section class="details-grid">
        <article class="card">
          <div class="card-header">
            <h2>Academic information</h2>
          </div>

          <div class="card-body details-list">
            <div class="detail-row">
              <span>Roll number</span>
              <strong>
                {{ student.roll_number || 'Not provided' }}
              </strong>
            </div>

            <div class="detail-row">
              <span>Branch</span>
              <strong>
                {{ student.branch || 'Not provided' }}
              </strong>
            </div>

            <div class="detail-row">
              <span>CGPA</span>

              <strong>
                {{
                  student.cgpa !== null &&
                  student.cgpa !== undefined
                    ? Number(student.cgpa).toFixed(2)
                    : 'Not provided'
                }}
              </strong>
            </div>

            <div class="detail-row">
              <span>Graduation year</span>

              <strong>
                {{ student.graduation_year || 'Not provided' }}
              </strong>
            </div>

            <div class="detail-row">
              <span>Placement status</span>

              <strong>
                {{ student.is_placed ? 'Placed' : 'Not placed' }}
              </strong>
            </div>
          </div>
        </article>

        <article class="card">
          <div class="card-header">
            <h2>Contact information</h2>
          </div>

          <div class="card-body details-list">
            <div class="detail-row">
              <span>Email</span>

              <a
                v-if="student.email"
                :href="`mailto:${student.email}`"
              >
                {{ student.email }}
              </a>

              <strong v-else>Not provided</strong>
            </div>

            <div class="detail-row">
              <span>Phone</span>

              <strong>
                {{ student.phone || 'Not provided' }}
              </strong>
            </div>

            <div class="detail-row">
              <span>Resume</span>
              
              <button
                v-if="student.has_resume"
                type="button"
                class="btn btn-outline-primary btn-sm"
                @click="downloadResume"
              >
                <i class="bi bi-download"></i>
                  View / download resume
              </button>

              <strong v-else>Not uploaded</strong>
            </div>

            <div class="detail-row">
              <span>Registered</span>

              <strong>
                {{ formatDate(student.created_at) }}
              </strong>
            </div>

            <div
              v-if="student.is_blacklisted"
              class="detail-row"
            >
              <span>Account status</span>
              <strong>Blacklisted</strong>
            </div>

            <div
              v-if="
                student.is_blacklisted &&
                student.blacklist_reason
              "
              class="detail-row"
            >
              <span>Blacklist reason</span>

              <strong>
                {{ student.blacklist_reason }}
              </strong>
            </div>
          </div>
        </article>
      </section>

      <section class="card applications-card">
        <div class="card-header section-header">
          <div>
            <div class="section-title-row">
              <h2>Placement history</h2>

              <span class="badge bg-primary">
                {{ applications.length }}
              </span>
            </div>

            <p>
              Complete application history for this student.
            </p>
          </div>
        </div>

        <div
          v-if="applications.length === 0"
          class="empty-state"
        >
          <i class="bi bi-inbox"></i>
          <strong>No placement applications</strong>

          <span>
            This student has not applied to a placement drive.
          </span>
        </div>

        <div
          v-else
          class="table-responsive"
        >
          <table class="table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Drive</th>
                <th>Job title</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Interview</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="application in applications"
                :key="application.id"
              >
                <td>
                  <RouterLink
                    v-if="application.company_id"
                    :to="`/admin/companies/${application.company_id}`"
                    class="primary-link"
                  >
                    {{ application.company_name }}
                  </RouterLink>

                  <span v-else>
                    {{ application.company_name || 'Not available' }}
                  </span>
                </td>

                <td>
                  <RouterLink
                    v-if="application.drive_id"
                    :to="`/admin/drives/${application.drive_id}`"
                    class="primary-link"
                  >
                    {{ application.drive_name }}
                  </RouterLink>

                  <span v-else>
                    {{ application.drive_name || 'Not available' }}
                  </span>
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
                    :class="
                      getApplicationStatusClass(application.status)
                    "
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

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 18px;
  padding: 0;
  color: var(--color-text-muted);
  background: transparent;
  border: 0;
  font-size: 0.8rem;
  font-weight: 600;
}

.back-link:hover {
  color: var(--color-primary);
}

.dashboard-title {
  margin-bottom: 0;
}

.refresh-button,
.student-actions .btn {
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

.student-overview {
  margin-bottom: 20px;
}

.student-identity {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.student-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 64px;
  width: 64px;
  height: 64px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 12px;
  font-size: 1.4rem;
  font-weight: 700;
}

.identity-copy {
  min-width: 0;
}

.student-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.student-title-row h2 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 650;
  letter-spacing: -0.03em;
}

.identity-copy p {
  margin: 6px 0 3px;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.separator {
  margin: 0 5px;
}

.student-id {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.student-actions {
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

.summary-icon i,
.summary-icon .bi {
  display: block;
  width: auto;
  height: auto;
  margin: 0;
  padding: 0;
  color: inherit !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  font-size: inherit;
  line-height: 1;
  box-shadow: none !important;
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

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.details-grid .card {
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.details-list {
  padding-top: 8px;
  padding-bottom: 8px;
}

.detail-row {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 20px;
  padding: 13px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-row > span {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.detail-row strong,
.detail-row a {
  overflow-wrap: anywhere;
  color: var(--color-text);
  font-size: 0.825rem;
  font-weight: 600;
}

.detail-row a {
  color: var(--color-accent);
}

.applications-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.section-header p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.primary-link {
  color: var(--color-primary);
  font-weight: 600;
}

.empty-state {
  min-height: 260px;
}

.empty-state strong {
  color: var(--color-primary);
  font-size: 0.9rem;
}

.empty-state span {
  font-size: 0.8rem;
}

@media (max-width: 991.98px) {
  .summary-grid,
  .details-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .student-identity {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .student-actions {
    width: 100%;
    margin-left: 82px;
  }
}

@media (max-width: 767.98px) {
  .page-header {
    flex-direction: column;
  }

  .summary-grid,
  .details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 575.98px) {
  .student-identity {
    padding: 20px;
  }

  .student-avatar {
    width: 52px;
    height: 52px;
    flex-basis: 52px;
  }

  .student-title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .student-actions {
    width: 100%;
    margin-left: 0;
  }

  .student-actions .btn {
    justify-content: center;
    width: 100%;
  }

  .detail-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>