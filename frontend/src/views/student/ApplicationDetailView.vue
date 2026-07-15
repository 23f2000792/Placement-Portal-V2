<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()

const applicationId = route.params.id

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const application = ref({})

const drive = computed(() => application.value.drive || {})
const interview = computed(
  () => application.value.interview || null,
)

const timeline = computed(() => {
  const items = [
    {
      label: 'Application submitted',
      date: application.value.applied_at,
      icon: 'bi-send',
      state: 'complete',
    },
  ]

  if (application.value.status === 'shortlisted') {
    items.push({
      label: 'Shortlisted',
      date: application.value.updated_at,
      icon: 'bi-person-check',
      state: 'complete',
    })
  }

  if (interview.value) {
    items.push({
      label: 'Interview scheduled',
      date: interview.value.date,
      icon: 'bi-calendar-event',
      state: 'interview',
    })
  }

  if (application.value.status === 'selected') {
    items.push({
      label: 'Selected',
      date: application.value.updated_at,
      icon: 'bi-check-circle',
      state: 'selected',
    })
  }

  if (application.value.status === 'rejected') {
    items.push({
      label: 'Application rejected',
      date: application.value.updated_at,
      icon: 'bi-x-circle',
      state: 'rejected',
    })
  }

  return items
})

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

const getStatusContent = (status) => {
  const content = {
    applied: {
      title: 'Application under review',
      message:
        'Your application has been submitted and is awaiting review by the company.',
      icon: 'bi-clock',
    },
    shortlisted: {
      title: 'You have been shortlisted',
      message:
        'The company has shortlisted your application for the next recruitment stage.',
      icon: 'bi-person-check',
    },
    selected: {
      title: 'You have been selected',
      message:
        'The company has recorded a successful final selection for this application.',
      icon: 'bi-check-circle',
    },
    rejected: {
      title: 'Application not selected',
      message:
        'The company has closed this application with a rejected status.',
      icon: 'bi-x-circle',
    },
  }

  return (
    content[status] || {
      title: 'Application status',
      message: 'Review the latest application information below.',
      icon: 'bi-file-earmark-text',
    }
  )
}

const getInterviewCountdown = (value) => {
  if (!value) return ''

  const difference =
    new Date(value).getTime() - new Date().getTime()

  if (difference <= 0) {
    return 'Interview time has passed'
  }

  const totalMinutes = Math.floor(
    difference / (1000 * 60),
  )

  const days = Math.floor(totalMinutes / (60 * 24))
  const hours = Math.floor(
    (totalMinutes % (60 * 24)) / 60,
  )
  const minutes = totalMinutes % 60

  if (days > 0) {
    return `${days} day${days === 1 ? '' : 's'} and ${hours} hour${
      hours === 1 ? '' : 's'
    } remaining`
  }

  if (hours > 0) {
    return `${hours} hour${hours === 1 ? '' : 's'} and ${minutes} minute${
      minutes === 1 ? '' : 's'
    } remaining`
  }

  return `${minutes} minute${
    minutes === 1 ? '' : 's'
  } remaining`
}

const fetchApplication = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await studentAPI.getApplication(
      applicationId,
    )

    application.value =
      response.data.application || {}
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
    refreshing.value = false
  }
}

const goBack = () => {
  router.push('/student/applications')
}

const viewDrive = () => {
  if (!drive.value.id) return

  router.push(`/student/drives/${drive.value.id}`)
}

onMounted(() => {
  fetchApplication()
})
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
          My applications
        </button>

        <div class="title-row">
          <h1 class="dashboard-title">
            Application #{{ application.id || applicationId }}
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
          Track your recruitment progress and interview details.
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading || refreshing"
        @click="fetchApplication(true)"
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
        @click="fetchApplication()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        class="status-banner"
        :class="`status-${application.status}`"
      >
        <span class="status-icon">
          <i
            :class="[
              'bi',
              getStatusContent(application.status).icon,
            ]"
          ></i>
        </span>

        <div>
          <strong>
            {{ getStatusContent(application.status).title }}
          </strong>

          <p>
            {{ getStatusContent(application.status).message }}
          </p>
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <article class="card">
            <div class="card-header section-header">
              <div>
                <h2>Placement application</h2>

                <p>
                  Role and company associated with this application.
                </p>
              </div>

              <button
                type="button"
                class="section-link"
                @click="viewDrive"
              >
                View drive
              </button>
            </div>

            <div class="card-body">
              <div class="company-heading">
                <span class="company-avatar">
                  {{
                    drive.company_name
                      ?.charAt(0)
                      .toUpperCase() || 'C'
                  }}
                </span>

                <div>
                  <span>Recruiting company</span>
                  <h3>{{ drive.company_name }}</h3>
                </div>
              </div>

              <div class="role-section">
                <span>Placement drive</span>
                <strong>{{ drive.drive_name }}</strong>
              </div>

              <div class="role-section">
                <span>Job title</span>
                <strong>{{ drive.job_title }}</strong>
              </div>
            </div>
          </article>

          <article
            v-if="interview"
            class="card interview-card"
          >
            <div class="card-header">
              <div>
                <h2>Interview details</h2>

                <p>
                  Schedule and instructions provided by the company.
                </p>
              </div>
            </div>

            <div class="card-body">
              <div class="interview-date">
                <span class="interview-icon">
                  <i class="bi bi-calendar-event"></i>
                </span>

                <div>
                  <span>Date and time</span>

                  <strong>
                    {{ formatDateTime(interview.date) }}
                  </strong>
                </div>
              </div>

              <div class="countdown-box">
                <span>Interview countdown</span>

                <strong>
                  {{ getInterviewCountdown(interview.date) }}
                </strong>
              </div>

              <div class="instructions">
                <span>Instructions</span>

                <p>
                  {{
                    interview.notes ||
                    'No additional interview instructions have been provided.'
                  }}
                </p>
              </div>
            </div>
          </article>

          <article
            v-else-if="application.status === 'shortlisted'"
            class="info-card"
          >
            <i class="bi bi-calendar-event"></i>

            <div>
              <strong>Interview not scheduled yet</strong>

              <p>
                You have been shortlisted. Interview information will
                appear here after the company schedules it.
              </p>
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

              <div class="detail-row stacked-row">
                <span>Last updated</span>

                <strong>
                  {{ formatDateTime(application.updated_at) }}
                </strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Application timeline</h2>
            </div>

            <div class="card-body timeline">
              <div
                v-for="(item, index) in timeline"
                :key="`${item.label}-${index}`"
                class="timeline-item"
                :class="`timeline-${item.state}`"
              >
                <span class="timeline-marker">
                  <i :class="['bi', item.icon]"></i>
                </span>

                <div>
                  <strong>{{ item.label }}</strong>

                  <span>{{ formatDateTime(item.date) }}</span>
                </div>
              </div>
            </div>
          </article>

          <article class="info-card">
            <i class="bi bi-info-circle"></i>

            <div>
              <strong>Status updates</strong>

              <p>
                Application decisions and interview schedules are
                updated by the recruiting company.
              </p>
            </div>
          </article>
        </aside>
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

.status-banner {
  display: flex;
  align-items: center;
  gap: 13px;
  margin-bottom: 20px;
  padding: 16px 18px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border-radius: 8px;
}

.status-banner strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.status-banner p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.status-applied {
  background: #eef3fa;
  border-color: #d3dfef;
}

.status-applied .status-icon {
  color: #314c77;
  background: #dfe8f4;
}

.status-shortlisted {
  background: #eef7f8;
  border-color: #d2e7e9;
}

.status-shortlisted .status-icon {
  color: #27616a;
  background: #dceff1;
}

.status-selected {
  background: #edf8f1;
  border-color: #cbe7d5;
}

.status-selected .status-icon {
  color: #23633c;
  background: #dcefe3;
}

.status-rejected {
  background: #fff5f4;
  border-color: #f1d5d2;
}

.status-rejected .status-icon {
  color: var(--color-danger);
  background: #f8dfdc;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.6fr);
  gap: 20px;
  align-items: start;
}

.main-column,
.side-column {
  min-width: 0;
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

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.section-link {
  padding: 0;
  color: var(--color-accent);
  background: transparent;
  border: 0;
  font-size: 0.78rem;
  font-weight: 600;
}

.company-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.company-avatar {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;

  flex: 0 0 38px;
  width: 38px;
  height: 38px;

  padding: 0 !important;
  margin: 0;

  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;

  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1;

  text-align: center;
}

.company-heading span,
.role-section > span,
.interview-date div > span,
.countdown-box > span,
.instructions > span {
  display: block;
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.company-heading h3 {
  margin: 4px 0 0;
  color: var(--color-primary);
  font-size: 1rem;
  font-weight: 650;
}

.role-section {
  margin-top: 20px;
}

.role-section strong {
  display: block;
  margin-top: 5px;
  color: var(--color-text);
  font-size: 0.84rem;
  font-weight: 600;
}

.interview-date {
  display: flex;
  align-items: center;
  gap: 12px;
}

.interview-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 9px;
}

.interview-date strong {
  display: block;
  margin-top: 4px;
  color: var(--color-primary);
  font-size: 0.86rem;
}

.countdown-box {
  margin-top: 20px;
  padding: 14px;
  background: var(--color-surface-muted);
  border-radius: var(--border-radius-sm);
}

.countdown-box strong {
  display: block;
  margin-top: 5px;
  color: var(--color-primary);
  font-size: 0.8rem;
}

.instructions {
  margin-top: 20px;
}

.instructions p {
  margin: 5px 0 0;
  color: var(--color-text);
  font-size: 0.8rem;
  line-height: 1.7;
  white-space: pre-line;
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
  font-size: 0.72rem;
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

.timeline {
  padding-top: 18px;
  padding-bottom: 18px;
}

.timeline-item {
  position: relative;
  display: flex;
  gap: 11px;
  padding-bottom: 22px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item:not(:last-child)::before {
  position: absolute;
  top: 28px;
  bottom: 4px;
  left: 13px;
  width: 1px;
  background: var(--color-border);
  content: '';
}

.timeline-marker {
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 27px;
  width: 27px;
  height: 27px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 7px;
  font-size: 0.7rem;
}

.timeline-item strong,
.timeline-item div > span {
  display: block;
}

.timeline-item strong {
  color: var(--color-primary);
  font-size: 0.76rem;
}

.timeline-item div > span {
  margin-top: 4px;
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.timeline-selected .timeline-marker,
.timeline-complete .timeline-marker {
  color: #23633c;
  background: #dcefe3;
}

.timeline-interview .timeline-marker {
  color: #314c77;
  background: #dfe8f4;
}

.timeline-rejected .timeline-marker {
  color: var(--color-danger);
  background: #f8dfdc;
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.info-card > i {
  color: var(--color-accent);
}

.info-card strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.info-card p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
  line-height: 1.55;
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

  .info-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .side-column {
    grid-template-columns: 1fr;
  }

  .info-card {
    grid-column: auto;
  }
}
</style>