<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { studentAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

const loading = ref(true)
const refreshing = ref(false)
const applying = ref(false)
const error = ref('')

const drive = ref({})
const application = ref(null)
const studentProfile = ref({})

const company = computed(() => drive.value.company || {})
const eligibility = computed(
  () => drive.value.eligibility || {},
)

const alreadyApplied = computed(
  () =>
    Boolean(application.value) ||
    Boolean(eligibility.value.already_applied),
)

const canApply = computed(
  () =>
    !alreadyApplied.value &&
    Boolean(eligibility.value.is_eligible),
)

const applicationState = computed(() => {
  if (alreadyApplied.value) {
    return {
      label: 'Application submitted',
      message:
        'You have already applied to this placement drive.',
      icon: 'bi-check-circle',
      className: 'state-applied',
    }
  }

  if (!eligibility.value.deadline_active) {
    return {
      label: 'Applications closed',
      message:
        'The application deadline for this placement drive has passed.',
      icon: 'bi-clock-history',
      className: 'state-closed',
    }
  }

  if (!eligibility.value.cgpa_eligible) {
    return {
      label: 'CGPA requirement not met',
      message:
        'Your current CGPA is below the minimum requirement for this drive.',
      icon: 'bi-lock',
      className: 'state-ineligible',
    }
  }

  if (!eligibility.value.branch_eligible) {
    return {
      label: 'Branch not eligible',
      message:
        'Your branch is not included in the eligible branches for this drive.',
      icon: 'bi-lock',
      className: 'state-ineligible',
    }
  }

  return {
    label: 'Eligible to apply',
    message:
      'Your profile meets the current eligibility requirements.',
    icon: 'bi-check-circle',
    className: 'state-eligible',
  }
})

const formatDateTime = (value) => {
  if (!value) return 'To be announced'

  return new Date(value).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getDaysLeft = (deadline) => {
  if (!deadline) return 'No deadline'

  const difference =
    new Date(deadline).getTime() - new Date().getTime()

  const days = Math.ceil(
    difference / (1000 * 60 * 60 * 24),
  )

  if (days < 0) return 'Closed'
  if (days === 0) return 'Today'
  if (days === 1) return '1 day left'

  return `${days} days left`
}

const normalizeWebsite = (website) => {
  if (!website) return ''

  if (
    website.startsWith('http://') ||
    website.startsWith('https://')
  ) {
    return website
  }

  return `https://${website}`
}

const fetchData = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const [driveResponse, profileResponse] =
      await Promise.all([
        studentAPI.getDrive(driveId),
        studentAPI.getProfile(),
      ])

    drive.value = driveResponse.data.drive || {}
    application.value =
      driveResponse.data.application || null
    studentProfile.value =
      profileResponse.data.profile || {}
  } catch (requestError) {
    console.error(
      'Unable to load placement drive:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load placement drive details.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const applyToDrive = async () => {
  if (!canApply.value || applying.value) return

  const confirmed = window.confirm(
    `Apply to ${drive.value.drive_name} at ${company.value.name}?`,
  )

  if (!confirmed) return

  applying.value = true

  try {
    await studentAPI.applyToDrive(driveId)

    messageStore.updateSuccessMessages(
      'Application submitted successfully.',
    )

    await fetchData(true)
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to submit your application.',
    )
  } finally {
    applying.value = false
  }
}

const viewApplication = () => {
  if (!application.value?.id) return

  router.push(
    `/student/applications/${application.value.id}`,
  )
}

const goBack = () => {
  router.push('/student/drives')
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="drive-detail-page fade-in">
    <header class="page-header">
      <div>
        <button
          type="button"
          class="back-link"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Placement drives
        </button>

        <h1 class="dashboard-title">
          {{ drive.drive_name || 'Placement drive' }}
        </h1>

        <p class="page-subtitle">
          {{ drive.job_title || 'Recruitment opportunity' }}
        </p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary"
        :disabled="loading || refreshing"
        @click="fetchData(true)"
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
          Loading placement drive
        </span>
      </div>

      <span>Loading placement drive...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Placement drive could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchData()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        class="eligibility-banner"
        :class="applicationState.className"
      >
        <span class="banner-icon">
          <i
            :class="[
              'bi',
              applicationState.icon,
            ]"
          ></i>
        </span>

        <div>
          <strong>{{ applicationState.label }}</strong>
          <p>{{ applicationState.message }}</p>
        </div>

        <button
          v-if="canApply"
          type="button"
          class="btn btn-primary"
          :disabled="applying"
          @click="applyToDrive"
        >
          <span
            v-if="applying"
            class="spinner-border spinner-border-sm"
            aria-hidden="true"
          ></span>

          <i
            v-else
            class="bi bi-send"
          ></i>

          {{
            applying
              ? 'Applying...'
              : 'Apply now'
          }}
        </button>

        <button
          v-else-if="application?.id"
          type="button"
          class="btn btn-outline-secondary"
          @click="viewApplication"
        >
          View application
        </button>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <article class="card">
            <div class="card-header">
              <div>
                <h2>Role information</h2>
                <p>
                  Position and recruitment opportunity details.
                </p>
              </div>
            </div>

            <div class="card-body">
              <div class="role-heading">
                <span>Job title</span>
                <h3>{{ drive.job_title }}</h3>
              </div>

              <div class="description-section">
                <span>Job description</span>

                <p>
                  {{
                    drive.job_description ||
                    'No job description has been provided.'
                  }}
                </p>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <div>
                <h2>Eligibility criteria</h2>
                <p>
                  Requirements evaluated against your student profile.
                </p>
              </div>
            </div>

            <div class="card-body">
              <div class="eligibility-grid">
                <article class="eligibility-item">
                  <div>
                    <span>CGPA requirement</span>

                    <strong>
                      {{
                        drive.min_cgpa !== null &&
                        drive.min_cgpa !== undefined
                          ? `Minimum ${Number(
                              drive.min_cgpa,
                            ).toFixed(2)}`
                          : 'No minimum'
                      }}
                    </strong>
                  </div>

                  <span
                    class="eligibility-result"
                    :class="{
                      eligible:
                        eligibility.cgpa_eligible,
                      ineligible:
                        !eligibility.cgpa_eligible,
                    }"
                  >
                    <i
                      :class="[
                        'bi',
                        eligibility.cgpa_eligible
                          ? 'bi-check-circle'
                          : 'bi-x-circle',
                      ]"
                    ></i>

                    {{
                      eligibility.cgpa_eligible
                        ? 'Eligible'
                        : 'Not eligible'
                    }}
                  </span>
                </article>

                <article class="eligibility-item">
                  <div>
                    <span>Your CGPA</span>

                    <strong>
                      {{
                        studentProfile.cgpa !== null &&
                        studentProfile.cgpa !== undefined
                          ? Number(
                              studentProfile.cgpa,
                            ).toFixed(2)
                          : 'Not provided'
                      }}
                    </strong>
                  </div>
                </article>

                <article class="eligibility-item">
                  <div>
                    <span>Branch requirement</span>

                    <strong>
                      {{
                        drive.allowed_branches ||
                        'All branches'
                      }}
                    </strong>
                  </div>

                  <span
                    class="eligibility-result"
                    :class="{
                      eligible:
                        eligibility.branch_eligible,
                      ineligible:
                        !eligibility.branch_eligible,
                    }"
                  >
                    <i
                      :class="[
                        'bi',
                        eligibility.branch_eligible
                          ? 'bi-check-circle'
                          : 'bi-x-circle',
                      ]"
                    ></i>

                    {{
                      eligibility.branch_eligible
                        ? 'Eligible'
                        : 'Not eligible'
                    }}
                  </span>
                </article>

                <article class="eligibility-item">
                  <div>
                    <span>Your branch</span>

                    <strong>
                      {{
                        studentProfile.branch ||
                        'Not provided'
                      }}
                    </strong>
                  </div>
                </article>
              </div>

              <div class="criteria-section">
                <span>Additional eligibility criteria</span>

                <p>
                  {{
                    drive.eligibility_criteria ||
                    'No additional eligibility criteria have been specified.'
                  }}
                </p>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <div>
                <h2>About the company</h2>
                <p>
                  Organisation conducting this placement drive.
                </p>
              </div>
            </div>

            <div class="card-body company-content">
              <div class="company-heading">
                <span class="company-avatar">
                  {{
                    company.name
                      ?.charAt(0)
                      .toUpperCase() || 'C'
                  }}
                </span>

                <div>
                  <h3>{{ company.name }}</h3>

                  <p>
                    {{
                      company.industry ||
                      'Industry not provided'
                    }}
                  </p>
                </div>
              </div>

              <p class="company-description">
                {{
                  company.description ||
                  'No company description has been provided.'
                }}
              </p>

              <div class="company-meta">
                <div>
                  <i class="bi bi-geo-alt"></i>

                  <span>
                    {{
                      company.location ||
                      'Location not provided'
                    }}
                  </span>
                </div>

                <a
                  v-if="company.website"
                  :href="normalizeWebsite(company.website)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i class="bi bi-globe"></i>
                  Visit company website
                </a>
              </div>
            </div>
          </article>
        </div>

        <aside class="side-column">
          <article class="company-summary">
            <span class="summary-avatar">
              {{
                company.name
                  ?.charAt(0)
                  .toUpperCase() || 'C'
              }}
            </span>

            <span class="summary-label">
              Recruiting company
            </span>

            <h2>{{ company.name }}</h2>

            <p>{{ company.industry || 'Placement partner' }}</p>
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
                      drive.application_deadline,
                    )
                  }}
                </strong>

                <small>
                  {{
                    getDaysLeft(
                      drive.application_deadline,
                    )
                  }}
                </small>
              </div>

              <div class="detail-row stacked-row">
                <span>Drive date</span>

                <strong>
                  {{ formatDateTime(drive.drive_date) }}
                </strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Eligibility status</h2>
            </div>

            <div class="card-body status-list">
              <div>
                <span>CGPA</span>

                <strong
                  :class="{
                    eligible:
                      eligibility.cgpa_eligible,
                    ineligible:
                      !eligibility.cgpa_eligible,
                  }"
                >
                  {{
                    eligibility.cgpa_eligible
                      ? 'Eligible'
                      : 'Not eligible'
                  }}
                </strong>
              </div>

              <div>
                <span>Branch</span>

                <strong
                  :class="{
                    eligible:
                      eligibility.branch_eligible,
                    ineligible:
                      !eligibility.branch_eligible,
                  }"
                >
                  {{
                    eligibility.branch_eligible
                      ? 'Eligible'
                      : 'Not eligible'
                  }}
                </strong>
              </div>

              <div>
                <span>Deadline</span>

                <strong
                  :class="{
                    eligible:
                      eligibility.deadline_active,
                    ineligible:
                      !eligibility.deadline_active,
                  }"
                >
                  {{
                    eligibility.deadline_active
                      ? 'Active'
                      : 'Closed'
                  }}
                </strong>
              </div>
            </div>
          </article>

          <article class="info-card">
            <i class="bi bi-info-circle"></i>

            <div>
              <strong>Eligibility validation</strong>

              <p>
                Eligibility is validated again by the server when an
                application is submitted.
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

.dashboard-title {
  margin-bottom: 0;
}

.page-header .btn,
.eligibility-banner .btn {
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

.eligibility-banner {
  display: flex;
  align-items: center;
  gap: 13px;
  margin-bottom: 20px;
  padding: 16px 18px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.eligibility-banner > div {
  flex: 1;
}

.banner-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border-radius: 8px;
}

.eligibility-banner strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.eligibility-banner p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.state-eligible {
  background: #edf8f1;
  border-color: #cbe7d5;
}

.state-eligible .banner-icon {
  color: #23633c;
  background: #dcefe3;
}

.state-applied {
  background: #eef3fa;
  border-color: #d3dfef;
}

.state-applied .banner-icon {
  color: #314c77;
  background: #dfe8f4;
}

.state-ineligible,
.state-closed {
  background: #fff5f4;
  border-color: #f1d5d2;
}

.state-ineligible .banner-icon,
.state-closed .banner-icon {
  color: var(--color-danger);
  background: #f8dfdc;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.55fr);
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

.role-heading > span,
.description-section > span,
.criteria-section > span {
  display: block;
  margin-bottom: 5px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.role-heading h3 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1.15rem;
  font-weight: 650;
}

.description-section {
  margin-top: 22px;
}

.description-section p,
.criteria-section p,
.company-description {
  margin: 0;
  color: var(--color-text);
  font-size: 0.82rem;
  line-height: 1.75;
  white-space: pre-line;
}

.eligibility-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.eligibility-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
  background: var(--color-surface-muted);
  border-radius: var(--border-radius-sm);
}

.eligibility-item span,
.eligibility-item strong {
  display: block;
}

.eligibility-item div > span {
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.eligibility-item div > strong {
  overflow-wrap: anywhere;
  margin-top: 4px;
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
}

.eligibility-result {
  display: inline-flex !important;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
  font-size: 0.68rem;
  font-weight: 650;
}

.eligible {
  color: #23633c !important;
}

.ineligible {
  color: var(--color-danger) !important;
}

.criteria-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.company-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.company-heading {
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-avatar,
.summary-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  background: #eef0f4;
  font-weight: 700;
}

.company-avatar {
  width: 42px;
  height: 42px;
  border-radius: 9px;
}

.company-heading h3 {
  margin: 0;
  color: var(--color-primary);
  font-size: 0.95rem;
  font-weight: 650;
}

.company-heading p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.company-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.company-meta div,
.company-meta a {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.company-meta a {
  color: var(--color-accent);
  text-decoration: none;
}

.company-summary {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 25px 20px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: var(--border-radius);
  text-align: center;
}

.summary-avatar {
  width: 52px;
  height: 52px;
  margin-bottom: 13px;
  background: #ffffff;
  border-radius: 12px;
}

.summary-label {
  color: rgba(255, 255, 255, 0.48);
  font-size: 0.66rem;
}

.company-summary h2 {
  margin: 5px 0 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 650;
}

.company-summary p {
  margin: 5px 0 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.72rem;
}

.detail-list,
.status-list {
  padding-top: 7px;
  padding-bottom: 7px;
}

.detail-row {
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-row:last-child {
  border-bottom: 0;
}

.stacked-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-row span,
.status-list span {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.detail-row strong {
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
}

.detail-row small {
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.status-list > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 11px 0;
  border-bottom: 1px solid var(--color-border);
}

.status-list > div:last-child {
  border-bottom: 0;
}

.status-list strong {
  font-size: 0.72rem;
  font-weight: 650;
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

  .company-summary {
    grid-column: 1 / -1;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .eligibility-banner {
    align-items: stretch;
    flex-direction: column;
  }

  .eligibility-grid,
  .side-column {
    grid-template-columns: 1fr;
  }

  .company-meta {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>