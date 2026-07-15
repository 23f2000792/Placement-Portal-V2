<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { companyAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const profile = ref({})

const form = reactive({
  company_name: '',
  hr_contact: '',
  website: '',
  industry: '',
  location: '',
  description: '',
})

const approvalStatus = computed(
  () => profile.value.approval_status || 'pending',
)

const isBlacklisted = computed(
  () => Boolean(profile.value.is_blacklisted),
)

const formatStatus = (status) => {
  if (!status) return 'Unknown'

  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (status) => {
  const classes = {
    approved: 'bg-success',
    pending: 'bg-warning',
    rejected: 'bg-danger',
  }

  return classes[status] || 'bg-secondary'
}

const populateForm = () => {
  form.company_name = profile.value.company_name || ''
  form.hr_contact = profile.value.hr_contact || ''
  form.website = profile.value.website || ''
  form.industry = profile.value.industry || ''
  form.location = profile.value.location || ''
  form.description = profile.value.description || ''
}

const fetchProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await companyAPI.getProfile()

    profile.value = response.data.profile || {}
    populateForm()
  } catch (requestError) {
    console.error('Unable to load company profile:', requestError)

    error.value =
      requestError.response?.data?.message ||
      'Unable to load company profile.'
  } finally {
    loading.value = false
  }
}

const normalizeWebsite = (value) => {
  const website = value.trim()

  if (!website) return ''

  if (
    website.startsWith('http://') ||
    website.startsWith('https://')
  ) {
    return website
  }

  return `https://${website}`
}

const validateForm = () => {
  if (!form.company_name.trim()) {
    return 'Company name is required.'
  }

  if (!form.hr_contact.trim()) {
    return 'HR contact is required.'
  }

  if (form.website.trim()) {
    try {
      const url = new URL(normalizeWebsite(form.website))

      if (!['http:', 'https:'].includes(url.protocol)) {
        return 'Enter a valid company website.'
      }
    } catch {
      return 'Enter a valid company website.'
    }
  }

  return ''
}

const saveProfile = async () => {
  const validationError = validateForm()

  if (validationError) {
    messageStore.updateErrorMessages(validationError)
    return
  }

  saving.value = true

  try {
    const payload = {
      company_name: form.company_name.trim(),
      hr_contact: form.hr_contact.trim(),
      website: normalizeWebsite(form.website),
      industry: form.industry.trim(),
      location: form.location.trim(),
      description: form.description.trim(),
    }

    const response = await companyAPI.updateProfile(payload)

    profile.value = response.data.profile || {
      ...profile.value,
      ...payload,
    }

    populateForm()

    messageStore.updateSuccessMessages(
      'Company profile updated successfully.',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to update company profile.',
    )
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  populateForm()
}

onMounted(fetchProfile)
</script>

<template>
  <div class="company-profile-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">Company profile</h1>

        <p class="page-subtitle">
          Manage your organisation and placement contact details.
        </p>
      </div>

      <div
        v-if="!loading"
        class="status-summary"
      >
        <span>Approval status</span>

        <span
          class="badge"
          :class="getStatusClass(approvalStatus)"
        >
          {{ formatStatus(approvalStatus) }}
        </span>
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
        <span class="visually-hidden">
          Loading company profile
        </span>
      </div>

      <span>Loading company profile...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Company profile could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchProfile"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section
        v-if="isBlacklisted"
        class="account-notice danger-notice"
      >
        <i class="bi bi-slash-circle"></i>

        <div>
          <strong>Company account blacklisted</strong>

          <p>
            Recruitment actions are restricted for this company
            account. Contact the institute placement cell for further
            information.
          </p>
        </div>
      </section>

      <section
        v-else-if="approvalStatus !== 'approved'"
        class="account-notice"
        :class="{
          'danger-notice': approvalStatus === 'rejected',
        }"
      >
        <i
          :class="[
            'bi',
            approvalStatus === 'rejected'
              ? 'bi-x-circle'
              : 'bi-clock',
          ]"
        ></i>

        <div>
          <strong>
            {{
              approvalStatus === 'rejected'
                ? 'Company registration rejected'
                : 'Company approval pending'
            }}
          </strong>

          <p>
            {{
              approvalStatus === 'rejected'
                ? 'Your company is not currently approved to conduct placement drives.'
                : 'Your company profile is awaiting review by the institute placement cell.'
            }}
          </p>
        </div>
      </section>

      <form
        class="profile-layout"
        @submit.prevent="saveProfile"
      >
        <div class="main-column">
          <section class="card">
            <div class="card-header">
              <div>
                <h2>Organisation details</h2>

                <p>
                  Information displayed across placement records.
                </p>
              </div>
            </div>

            <div class="card-body form-section">
              <div class="field-group">
                <label
                  for="companyName"
                  class="form-label"
                >
                  Company name
                  <span aria-hidden="true">*</span>
                </label>

                <input
                  id="companyName"
                  v-model="form.company_name"
                  type="text"
                  class="form-control"
                  maxlength="255"
                  autocomplete="organization"
                  required
                />
              </div>

              <div class="field-grid">
                <div class="field-group">
                  <label
                    for="industry"
                    class="form-label"
                  >
                    Industry
                  </label>

                  <input
                    id="industry"
                    v-model="form.industry"
                    type="text"
                    class="form-control"
                    maxlength="255"
                    placeholder="Example: Information Technology"
                    autocomplete="organization-title"
                  />
                </div>

                <div class="field-group">
                  <label
                    for="location"
                    class="form-label"
                  >
                    Location
                  </label>

                  <input
                    id="location"
                    v-model="form.location"
                    type="text"
                    class="form-control"
                    maxlength="255"
                    placeholder="Example: Bengaluru, Karnataka"
                    autocomplete="address-level2"
                  />
                </div>
              </div>

              <div class="field-group">
                <label
                  for="website"
                  class="form-label"
                >
                  Company website
                </label>

                <input
                  id="website"
                  v-model="form.website"
                  type="text"
                  class="form-control"
                  maxlength="500"
                  placeholder="www.example.com"
                  autocomplete="url"
                />

                <small class="field-help">
                  HTTPS is added automatically when the protocol is
                  omitted.
                </small>
              </div>

              <div class="field-group">
                <label
                  for="description"
                  class="form-label"
                >
                  Company description
                </label>

                <textarea
                  id="description"
                  v-model="form.description"
                  class="form-control"
                  rows="7"
                  placeholder="Briefly describe the organisation and its work."
                ></textarea>
              </div>
            </div>
          </section>

          <section class="card">
            <div class="card-header">
              <div>
                <h2>Placement contact</h2>

                <p>
                  Primary HR contact for recruitment coordination.
                </p>
              </div>
            </div>

            <div class="card-body form-section">
              <div class="field-group">
                <label
                  for="hrContact"
                  class="form-label"
                >
                  HR contact
                  <span aria-hidden="true">*</span>
                </label>

                <input
                  id="hrContact"
                  v-model="form.hr_contact"
                  type="text"
                  class="form-control"
                  maxlength="255"
                  placeholder="Name, email or phone number"
                  required
                />

                <small class="field-help">
                  Use the primary contact the placement cell should
                  reach for drive coordination.
                </small>
              </div>
            </div>
          </section>

          <div class="form-actions">
            <button
              type="button"
              class="btn btn-outline-secondary"
              :disabled="saving"
              @click="resetForm"
            >
              Reset changes
            </button>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="saving"
            >
              <span
                v-if="saving"
                class="spinner-border spinner-border-sm"
                aria-hidden="true"
              ></span>

              <i
                v-else
                class="bi bi-check-lg"
              ></i>

              {{
                saving
                  ? 'Saving profile...'
                  : 'Save changes'
              }}
            </button>
          </div>
        </div>

        <aside class="side-column">
          <section class="company-card">
            <span class="company-avatar">
              {{
                profile.company_name
                  ?.charAt(0)
                  .toUpperCase() || 'C'
              }}
            </span>

            <h2>
              {{ profile.company_name || 'Company profile' }}
            </h2>

            <p>
              {{ profile.industry || 'Industry not provided' }}
            </p>

            <span
              class="badge"
              :class="getStatusClass(approvalStatus)"
            >
              {{ formatStatus(approvalStatus) }}
            </span>
          </section>

          <section class="card">
            <div class="card-header">
              <h2>Account information</h2>
            </div>

            <div class="card-body detail-list">
              <div class="detail-row">
                <span>Company ID</span>

                <strong>
                  #{{ profile.id || profile.company_id }}
                </strong>
              </div>

              <div class="detail-row">
                <span>Approval</span>

                <strong>
                  {{ formatStatus(approvalStatus) }}
                </strong>
              </div>

              <div class="detail-row">
                <span>Account status</span>

                <strong>
                  {{ isBlacklisted ? 'Restricted' : 'Active' }}
                </strong>
              </div>

              <div
                v-if="profile.approved_at"
                class="detail-row"
              >
                <span>Approved on</span>

                <strong>
                  {{
                    new Date(
                      profile.approved_at,
                    ).toLocaleDateString('en-IN')
                  }}
                </strong>
              </div>
            </div>
          </section>

          <section class="info-card">
            <i class="bi bi-info-circle"></i>

            <div>
              <strong>Profile review</strong>

              <p>
                Changes to company details are visible to the
                placement cell and may be used during recruitment
                coordination.
              </p>
            </div>
          </section>
        </aside>
      </form>
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

.status-summary {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.status-summary > span:first-child {
  color: var(--color-text-muted);
  font-size: 0.75rem;
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

.account-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  padding: 15px 17px;
  background: #fff9e8;
  border: 1px solid #eadcae;
  border-radius: var(--border-radius);
}

.account-notice.danger-notice {
  background: #fff1f0;
  border-color: #f5cfcc;
}

.account-notice > i {
  color: var(--color-primary);
}

.danger-notice > i {
  color: var(--color-danger);
}

.account-notice strong {
  color: var(--color-primary);
  font-size: 0.84rem;
}

.account-notice p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.76rem;
  line-height: 1.55;
}

.profile-layout {
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

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field-group {
  min-width: 0;
}

.form-label {
  margin-bottom: 7px;
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
}

.form-label span {
  color: var(--color-danger);
}

.field-help {
  display: block;
  margin-top: 6px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
  line-height: 1.5;
}

textarea.form-control {
  resize: vertical;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.form-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
}

.company-card {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 28px 20px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: var(--border-radius);
  text-align: center;
}

.company-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  margin-bottom: 15px;
  color: var(--color-primary);
  background: #ffffff;
  border-radius: 12px;
  font-size: 1.15rem;
  font-weight: 700;
}

.company-card h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 650;
}

.company-card p {
  margin: 6px 0 14px;
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.75rem;
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

.detail-row span {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.detail-row strong {
  color: var(--color-text);
  font-size: 0.78rem;
  font-weight: 600;
  text-align: right;
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
  .profile-layout {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .company-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 767.98px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .field-grid,
  .side-column {
    grid-template-columns: 1fr;
  }

  .form-actions {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>