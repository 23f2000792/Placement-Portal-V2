<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const applicationId = route.params.id

const loading = ref(true)
const error = ref('')
const processingAction = ref(false)
const scheduling = ref(false)
const showScheduleModal = ref(false)

const application = ref({})
const companyProfile = ref({})

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
  if (!value) return 'Not available'

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

const fetchApplicationDetails = async () => {
  loading.value = true
  error.value = ''

  try {
    const [applicationResponse, profileResponse] =
      await Promise.all([
        companyAPI.getApplication(applicationId),
        companyAPI.getProfile(),
      ])

    application.value =
      applicationResponse.data.application || {}

    companyProfile.value =
      profileResponse.data.profile || {}
  } catch (requestError) {
    console.error(
      'Unable to load application details:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load application details.'
  } finally {
    loading.value = false
  }
}

const shortlistApplication = async () => {
  if (!canManage.value) return

  processingAction.value = true

  try {
    await companyAPI.shortlistApplication(applicationId)

    messageStore.updateSuccessMessages(
      'Candidate shortlisted successfully.',
    )

    await fetchApplicationDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to shortlist the candidate.',
    )
  } finally {
    processingAction.value = false
  }
}

const selectApplication = async () => {
  if (!canManage.value) return

  const confirmed = window.confirm(
    `Mark ${application.value.student_name} as selected?`,
  )

  if (!confirmed) return

  processingAction.value = true

  try {
    await companyAPI.selectApplication(applicationId)

    messageStore.updateSuccessMessages(
      'Candidate selected successfully.',
    )

    await fetchApplicationDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to select the candidate.',
    )
  } finally {
    processingAction.value = false
  }
}

const rejectApplication = async () => {
  if (!canManage.value) return

  const reason = window.prompt('Enter the rejection reason:')

  if (!reason?.trim()) return

  processingAction.value = true

  try {
    await companyAPI.rejectApplication(applicationId, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages(
      'Application rejected successfully.',
    )

    await fetchApplicationDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the application.',
    )
  } finally {
    processingAction.value = false
  }
}

const openScheduleModal = () => {
  if (!canManage.value) return

  interviewData.interview_date = ''
  interviewData.notes = application.value.interview_notes || ''
  showScheduleModal.value = true
}

const closeScheduleModal = () => {
  if (scheduling.value) return

  showScheduleModal.value = false
}

const scheduleInterview = async () => {
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
    await companyAPI.scheduleInterview(applicationId, {
      interview_date: interviewData.interview_date,
      notes: interviewData.notes.trim(),
    })

    messageStore.updateSuccessMessages(
      'Interview scheduled successfully.',
    )

    showScheduleModal.value = false

    await fetchApplicationDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to schedule the interview.',
    )
  } finally {
    scheduling.value = false
  }
}

const goBack = () => {
  router.push('/company/applications')
}

const downloadResume = async () => {
  try {
    await companyAPI.downloadStudentResume(
      application.value.student_id,
      `${application.value.student_name || 'student'}_resume.pdf`,
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to download the student resume.',
    )
  }
}

onMounted(fetchApplicationDetails)
</script>

<template>
  <div class="application-detail-page fade-in">
    <header class="page-header">
      <div>
        <button
          type="button"
          class="back-link"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Applications
        </button>

        <div class="title-row">
          <h1 class="dashboard-title">
            {{ application.student_name || 'Application' }}
          </h1>

          <span
            v-if="!loading"
            class="badge"
            :class="getStatusClass(application.status)"
          >
            {{ formatStatus(application.status) }}
          </span>
        </div>

        <p class="page-subtitle">
          Review candidate and recruitment information.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading"
        @click="fetchApplicationDetails"
      >
        <i class="bi bi-arrow-clockwise"></i>
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
          Loading application details
        </span>
      </div>

      <span>Loading application details...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Application could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchApplicationDetails"
      >
        Retry
      </button>
    </div>

    <template v-else>
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
            Application details remain visible, but recruitment
            decisions are currently disabled.
          </p>
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <article class="card">
            <div class="card-header">
              <div>
                <h2>Candidate information</h2>
                <p>Student profile attached to this application.</p>
              </div>
            </div>

            <div class="card-body candidate-profile">
              <div class="candidate-heading">
                <span class="candidate-avatar">
                  {{
                    application.student_name
                      ?.charAt(0)
                      .toUpperCase() || 'S'
                  }}
                </span>

                <div>
                  <h3>{{ application.student_name }}</h3>
                  <p>
                    {{
                      application.student_roll ||
                      'Roll number unavailable'
                    }}
                  </p>
                </div>
              </div>

              <div class="candidate-grid">
                <div>
                  <span>Branch</span>
                  <strong>
                    {{
                      application.student_branch ||
                      'Not provided'
                    }}
                  </strong>
                </div>

                <div>
                  <span>CGPA</span>
                  <strong>
                    {{
                      application.student_cgpa !== null &&
                      application.student_cgpa !== undefined
                        ? Number(
                            application.student_cgpa,
                          ).toFixed(2)
                        : 'Not provided'
                    }}
                  </strong>
                </div>

                <div>
                  <span>Email</span>
                  <strong>
                    {{ application.student_email }}
                  </strong>
                </div>

                <div>
                  <span>Phone</span>
                  <strong>
                    {{
                      application.student_phone ||
                      'Not provided'
                    }}
                  </strong>
                </div>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <div>
                <h2>Placement drive</h2>
                <p>Role and eligibility information.</p>
              </div>

              <button
                type="button"
                class="section-link"
                @click="
                  router.push(
                    `/company/drives/${application.drive_id}`,
                  )
                "
              >
                View drive
              </button>
            </div>

            <div class="card-body">
              <div class="drive-heading">
                <h3>{{ application.drive_name }}</h3>
                <p>{{ application.job_title }}</p>
              </div>

              <div class="description-section">
                <span>Job description</span>

                <p>
                  {{
                    application.job_description ||
                    'No job description provided.'
                  }}
                </p>
              </div>

              <div class="eligibility-grid">
                <div>
                  <span>Minimum CGPA</span>

                  <strong>
                    {{
                      application.min_cgpa !== null &&
                      application.min_cgpa !== undefined
                        ? Number(
                            application.min_cgpa,
                          ).toFixed(2)
                        : 'No restriction'
                    }}
                  </strong>
                </div>

                <div>
                  <span>Allowed branches</span>

                  <strong>
                    {{
                      application.allowed_branches ||
                      'All branches'
                    }}
                  </strong>
                </div>
              </div>

              <div class="description-section">
                <span>Additional eligibility criteria</span>

                <p>
                  {{
                    application.eligibility_criteria ||
                    'No additional eligibility criteria.'
                  }}
                </p>
              </div>
            </div>
          </article>

          <article
            v-if="application.interview_date"
            class="card"
          >
            <div class="card-header">
              <div>
                <h2>Interview</h2>
                <p>Scheduled interview information.</p>
              </div>

              <button
                v-if="
                  canManage &&
                  application.status === 'shortlisted'
                "
                type="button"
                class="section-link"
                @click="openScheduleModal"
              >
                Reschedule
              </button>
            </div>

            <div class="card-body interview-content">
              <div>
                <span>Date and time</span>
                <strong>
                  {{
                    formatDateTime(application.interview_date)
                  }}
                </strong>
              </div>

              <div>
                <span>Instructions</span>
                <strong>
                  {{
                    application.interview_notes ||
                    'No additional instructions'
                  }}
                </strong>
              </div>
            </div>
          </article>

          <article
            v-if="
              application.status === 'rejected' &&
              application.rejection_reason
            "
            class="rejection-card"
          >
            <i class="bi bi-x-circle"></i>

            <div>
              <strong>Rejection reason</strong>
              <p>{{ application.rejection_reason }}</p>
            </div>
          </article>
        </div>

        <aside class="side-column">
          <article class="card">
            <div class="card-header">
              <h2>Application details</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row">
                <span>Application ID</span>
                <strong>#{{ application.id }}</strong>
              </div>

              <div class="detail-row">
                <span>Status</span>

                <span
                  class="badge"
                  :class="getStatusClass(application.status)"
                >
                  {{ formatStatus(application.status) }}
                </span>
              </div>

              <div class="detail-row stacked-row">
                <span>Applied on</span>

                <strong>
                  {{ formatDateTime(application.applied_at) }}
                </strong>
              </div>

              <div
                v-if="application.shortlisted_at"
                class="detail-row stacked-row"
              >
                <span>Shortlisted on</span>

                <strong>
                  {{
                    formatDateTime(application.shortlisted_at)
                  }}
                </strong>
              </div>

              <div
                v-if="application.selected_at"
                class="detail-row stacked-row"
              >
                <span>Selected on</span>

                <strong>
                  {{ formatDateTime(application.selected_at) }}
                </strong>
              </div>

              <div
                v-if="application.rejected_at"
                class="detail-row stacked-row"
              >
                <span>Rejected on</span>

                <strong>
                  {{ formatDateTime(application.rejected_at) }}
                </strong>
              </div>

              <div class="detail-row">
                <span>Resume</span>
                
                <button
                  v-if="application.has_resume"
                  type="button"
                  class="btn btn-outline-primary btn-sm"
                  @click="downloadResume"
                >
                  <i class="bi bi-download"></i>
                    View resume
                </button>

                <strong v-else>Not uploaded</strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Drive schedule</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row stacked-row">
                <span>Application deadline</span>

                <strong>
                  {{
                    formatDateTime(
                      application.application_deadline,
                    )
                  }}
                </strong>
              </div>

              <div class="detail-row stacked-row">
                <span>Drive date</span>

                <strong>
                  {{ formatDateTime(application.drive_date) }}
                </strong>
              </div>

              <div class="detail-row">
                <span>Drive status</span>

                <strong>
                  {{ formatStatus(application.drive_status) }}
                </strong>
              </div>
            </div>
          </article>

          <article
            v-if="canManage"
            class="action-card"
          >
            <span>Recruitment decision</span>

            <template v-if="application.status === 'applied'">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="processingAction"
                @click="shortlistApplication"
              >
                Shortlist candidate
              </button>

              <button
                type="button"
                class="btn btn-outline-danger"
                :disabled="processingAction"
                @click="rejectApplication"
              >
                Reject application
              </button>
            </template>

            <template
              v-else-if="application.status === 'shortlisted'"
            >
              <button
                type="button"
                class="btn btn-primary"
                :disabled="processingAction"
                @click="selectApplication"
              >
                Select candidate
              </button>

              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="processingAction"
                @click="openScheduleModal"
              >
                {{
                  application.interview_date
                    ? 'Reschedule interview'
                    : 'Schedule interview'
                }}
              </button>

              <button
                type="button"
                class="btn btn-outline-danger"
                :disabled="processingAction"
                @click="rejectApplication"
              >
                Reject application
              </button>
            </template>

            <div
              v-else-if="application.status === 'selected'"
              class="decision-state"
            >
              <i class="bi bi-check-circle"></i>

              <div>
                <strong>Candidate selected</strong>
                <p>The final selection result has been recorded.</p>
              </div>
            </div>

            <div
              v-else-if="application.status === 'rejected'"
              class="decision-state rejected"
            >
              <i class="bi bi-x-circle"></i>

              <div>
                <strong>Application rejected</strong>
                <p>This application has been marked as rejected.</p>
              </div>
            </div>
          </article>
        </aside>
      </section>
    </template>

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
            <h2 id="scheduleTitle">
              Schedule interview
            </h2>

            <p>{{ application.student_name }}</p>
          </div>

          <button
            type="button"
            class="dialog-close"
            aria-label="Close interview dialog"
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
              placeholder="Meeting link, venue or interview instructions"
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
            @click="scheduleInterview"
          >
            <span
              v-if="scheduling"
              class="spinner-border spinner-border-sm"
              aria-hidden="true"
            ></span>

            {{
              scheduling
                ? 'Scheduling...'
                : 'Save interview'
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

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dashboard-title {
  margin-bottom: 0;
}

.page-header > .btn {
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

.access-notice strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.access-notice p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.76rem;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.6fr);
  gap: 20px;
  align-items: start;
}

.main-column,
.side-column {
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 650;
}

.card-header p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 400;
}

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.candidate-profile {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.candidate-heading {
  display: flex;
  align-items: center;
  gap: 13px;
}

.candidate-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 10px;
  font-weight: 700;
}

.candidate-heading h3,
.drive-heading h3 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1rem;
  font-weight: 650;
}

.candidate-heading p,
.drive-heading p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.76rem;
}

.candidate-grid,
.eligibility-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.candidate-grid > div,
.eligibility-grid > div,
.interview-content > div {
  padding: 14px;
  background: var(--color-surface-muted);
  border-radius: var(--border-radius-sm);
}

.candidate-grid span,
.eligibility-grid span,
.interview-content span,
.description-section > span {
  display: block;
  margin-bottom: 5px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.candidate-grid strong,
.eligibility-grid strong,
.interview-content strong {
  overflow-wrap: anywhere;
  color: var(--color-text);
  font-size: 0.8rem;
  font-weight: 600;
}

.description-section {
  margin-top: 22px;
}

.description-section p {
  margin: 0;
  color: var(--color-text);
  font-size: 0.82rem;
  line-height: 1.7;
  white-space: pre-line;
}

.eligibility-grid {
  margin-top: 22px;
}

.interview-content {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 14px;
}

.rejection-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 17px;
  background: #fff1f0;
  border: 1px solid #f5cfcc;
  border-radius: var(--border-radius);
}

.rejection-card > i,
.rejection-card strong {
  color: var(--color-danger);
}

.rejection-card strong {
  font-size: 0.82rem;
}

.rejection-card p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.76rem;
  line-height: 1.6;
}

.detail-list {
  padding-top: 7px;
  padding-bottom: 7px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-child {
  border-bottom: 0;
}

.detail-row > span:first-child {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.detail-row strong {
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
  text-align: right;
}

.stacked-row {
  flex-direction: column;
  gap: 5px;
}

.stacked-row strong {
  text-align: left;
}

.action-card {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 18px;
  background: var(--color-primary);
  border-radius: var(--border-radius);
}

.action-card > span {
  margin-bottom: 5px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
}

.action-card .btn {
  width: 100%;
}

.decision-state {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #ffffff;
}

.decision-state > i {
  margin-top: 2px;
}

.decision-state strong {
  font-size: 0.82rem;
}

.decision-state p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.72rem;
  line-height: 1.5;
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

@media (max-width: 991.98px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .action-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .candidate-grid,
  .eligibility-grid,
  .interview-content,
  .side-column {
    grid-template-columns: 1fr;
  }
}
</style>