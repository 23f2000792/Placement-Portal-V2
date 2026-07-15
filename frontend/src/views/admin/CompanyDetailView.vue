<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { adminAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const companyId = route.params.id

const loading = ref(true)
const error = ref('')
const processingAction = ref(false)
const company = ref({})
const drives = ref([])

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

const getCompanyStatus = () => {
  if (company.value.is_blacklisted) return 'Blacklisted'
  return formatStatus(company.value.approval_status)
}

const getCompanyStatusClass = () => {
  if (company.value.is_blacklisted) return 'bg-secondary'

  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
  }

  return classes[company.value.approval_status] || 'bg-secondary'
}

const getDriveStatusClass = (status) => {
  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
    closed: 'bg-secondary',
  }

  return classes[status] || 'bg-secondary'
}

const fetchCompanyDetails = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await adminAPI.getCompanyDetails(companyId)

    company.value = response.data.company || {}
    drives.value = response.data.drives || []
  } catch (requestError) {
    console.error('Unable to load company details:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load company details.'
  } finally {
    loading.value = false
  }
}

const approveCompany = async () => {
  if (!window.confirm('Approve this company registration?')) return

  processingAction.value = true

  try {
    await adminAPI.approveCompany(companyId)
    messageStore.updateSuccessMessages('Company approved successfully.')
    await fetchCompanyDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to approve the company.',
    )
  } finally {
    processingAction.value = false
  }
}

const rejectCompany = async () => {
  const reason = window.prompt('Enter the rejection reason:')

  if (!reason?.trim()) return

  processingAction.value = true

  try {
    await adminAPI.rejectCompany(companyId, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages('Company registration rejected.')
    await fetchCompanyDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reject the company.',
    )
  } finally {
    processingAction.value = false
  }
}

const blacklistCompany = async () => {
  const reason = window.prompt('Enter the blacklist reason:')

  if (!reason?.trim()) return

  processingAction.value = true

  try {
    await adminAPI.blacklistCompany(companyId, {
      reason: reason.trim(),
    })

    messageStore.updateSuccessMessages('Company blacklisted successfully.')
    await fetchCompanyDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to blacklist the company.',
    )
  } finally {
    processingAction.value = false
  }
}

const activateCompany = async () => {
  if (!window.confirm('Reactivate this company account?')) return

  processingAction.value = true

  try {
    await adminAPI.activateCompany(companyId)
    messageStore.updateSuccessMessages('Company account reactivated.')
    await fetchCompanyDetails()
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to reactivate the company.',
    )
  } finally {
    processingAction.value = false
  }
}

const viewDrive = (driveId) => {
  router.push(`/admin/drives/${driveId}`)
}

const goBack = () => {
  router.push('/admin/companies')
}

onMounted(fetchCompanyDetails)
</script>

<template>
  <div class="company-detail-page fade-in">
    <header class="page-header">
      <div>
        <button
          type="button"
          class="back-link"
          @click="goBack"
        >
          <i class="bi bi-arrow-left"></i>
          Companies
        </button>

        <h1 class="dashboard-title">Company details</h1>

        <p class="page-subtitle">
          Review company information, account status and placement drives.
        </p>
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
        <span class="visually-hidden">Loading company details</span>
      </div>

      <span>Loading company details...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Company details could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchCompanyDetails"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section class="company-overview">
        <article class="company-identity">
          <span class="company-avatar">
            {{ company.company_name?.charAt(0).toUpperCase() || 'C' }}
          </span>

          <div class="identity-copy">
            <div class="company-title-row">
              <h2>{{ company.company_name }}</h2>

              <span
                class="badge"
                :class="getCompanyStatusClass()"
              >
                {{ getCompanyStatus() }}
              </span>
            </div>

            <p>
              {{ company.industry || 'Industry not provided' }}
              <span class="separator">·</span>
              {{ company.location || 'Location not provided' }}
            </p>

            <span class="company-id">
              Company ID #{{ company.id }}
            </span>
          </div>

          <div class="company-actions">
            <template v-if="company.approval_status === 'pending'">
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="processingAction"
                @click="rejectCompany"
              >
                Reject
              </button>

              <button
                type="button"
                class="btn btn-primary"
                :disabled="processingAction"
                @click="approveCompany"
              >
                <span
                  v-if="processingAction"
                  class="spinner-border spinner-border-sm"
                  aria-hidden="true"
                ></span>

                Approve company
              </button>
            </template>

            <button
              v-else-if="
                company.approval_status === 'approved' &&
                !company.is_blacklisted
              "
              type="button"
              class="btn btn-outline-secondary"
              :disabled="processingAction"
              @click="blacklistCompany"
            >
              <i class="bi bi-slash-circle"></i>
              Blacklist company
            </button>

            <button
              v-else-if="company.is_blacklisted"
              type="button"
              class="btn btn-outline-primary"
              :disabled="processingAction"
              @click="activateCompany"
            >
              <i class="bi bi-arrow-counterclockwise"></i>
              Reactivate company
            </button>
          </div>
        </article>
      </section>

      <section class="details-grid">
        <article class="card">
          <div class="card-header">
            <h2>Company information</h2>
          </div>

          <div class="card-body details-list">
            <div class="detail-row">
              <span>Industry</span>
              <strong>{{ company.industry || 'Not provided' }}</strong>
            </div>

            <div class="detail-row">
              <span>Location</span>
              <strong>{{ company.location || 'Not provided' }}</strong>
            </div>

            <div class="detail-row">
              <span>Website</span>

              <a
                v-if="company.website"
                :href="company.website"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ company.website }}
                <i class="bi bi-box-arrow-up-right"></i>
              </a>

              <strong v-else>Not provided</strong>
            </div>

            <div class="detail-row">
              <span>Registered</span>
              <strong>{{ formatDate(company.created_at) }}</strong>
            </div>
          </div>
        </article>

        <article class="card">
          <div class="card-header">
            <h2>HR contact</h2>
          </div>

          <div class="card-body details-list">
            <div class="detail-row">
              <span>Name</span>
              <strong>{{ company.hr_name || 'Not provided' }}</strong>
            </div>

            <div class="detail-row">
              <span>Email</span>

              <a
                v-if="company.hr_email"
                :href="`mailto:${company.hr_email}`"
              >
                {{ company.hr_email }}
              </a>

              <strong v-else>Not provided</strong>
            </div>

            <div class="detail-row">
              <span>Phone</span>
              <strong>{{ company.hr_phone || 'Not provided' }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="card description-card">
        <div class="card-header">
          <h2>Company description</h2>
        </div>

        <div class="card-body">
          <p>
            {{
              company.company_description ||
              company.description ||
              'No company description has been provided.'
            }}
          </p>
        </div>
      </section>

      <section class="card drives-card">
        <div class="card-header section-header">
          <div>
            <div class="section-title-row">
              <h2>Placement drives</h2>

              <span class="badge bg-primary">
                {{ drives.length }}
              </span>
            </div>

            <p>Recruitment drives created by this company.</p>
          </div>
        </div>

        <div
          v-if="drives.length === 0"
          class="empty-state"
        >
          <i class="bi bi-briefcase"></i>
          <strong>No placement drives</strong>
          <span>This company has not created a drive yet.</span>
        </div>

        <div
          v-else
          class="table-responsive"
        >
          <table class="table">
            <thead>
              <tr>
                <th>Drive</th>
                <th>Job title</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Applications</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="drive in drives"
                :key="drive.id"
              >
                <td class="primary-cell">
                  {{ drive.drive_name }}
                </td>

                <td>{{ drive.job_title }}</td>
                <td>{{ formatDate(drive.application_deadline) }}</td>

                <td>
                  <span
                    class="badge"
                    :class="getDriveStatusClass(drive.status)"
                  >
                    {{ formatStatus(drive.status) }}
                  </span>
                </td>

                <td>
                  {{ Number(drive.application_count || 0).toLocaleString('en-IN') }}
                </td>

                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    @click="viewDrive(drive.id)"
                  >
                    View drive
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

.company-overview {
  margin-bottom: 20px;
}

.company-identity {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.company-avatar {
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

.company-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.company-title-row h2 {
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

.company-id {
  color: var(--color-text-muted);
  font-size: 0.72rem;
}

.company-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.company-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
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

.description-card p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  line-height: 1.7;
  white-space: pre-line;
}

.drives-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
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

.primary-cell {
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
  .details-grid {
    grid-template-columns: 1fr;
  }

  .company-identity {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .company-actions {
    width: 100%;
    margin-left: 82px;
  }
}

@media (max-width: 575.98px) {
  .company-identity {
    padding: 20px;
  }

  .company-avatar {
    width: 52px;
    height: 52px;
    flex-basis: 52px;
  }

  .company-title-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .company-actions {
    align-items: stretch;
    flex-direction: column;
    margin-left: 0;
  }

  .company-actions .btn {
    justify-content: center;
  }

  .detail-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>