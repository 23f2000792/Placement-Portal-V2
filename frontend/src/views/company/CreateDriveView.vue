<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { companyAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const messageStore = useMessageStore()

const loadingProfile = ref(true)
const profileError = ref('')
const submitting = ref(false)
const companyProfile = ref({})

const form = reactive({
  drive_name: '',
  job_title: '',
  job_description: '',
  eligibility_criteria: '',
  min_cgpa: '',
  allowed_branches: '',
  application_deadline: '',
  drive_date: '',
})

const canCreateDrive = computed(
  () =>
    companyProfile.value.approval_status === 'approved' &&
    !companyProfile.value.is_blacklisted,
)

const accessTitle = computed(() => {
  if (companyProfile.value.is_blacklisted) {
    return 'Company account blacklisted'
  }

  if (companyProfile.value.approval_status === 'rejected') {
    return 'Company registration rejected'
  }

  return 'Company approval pending'
})

const accessMessage = computed(() => {
  if (companyProfile.value.is_blacklisted) {
    return 'Your company cannot create placement drives while the account is blacklisted.'
  }

  if (companyProfile.value.approval_status === 'rejected') {
    return 'Your company registration has not been approved by the institute placement cell.'
  }

  return 'The institute placement cell must approve your company before you can create placement drives.'
})

const minimumDeadline = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())

  return now.toISOString().slice(0, 16)
})

const minimumDriveDate = computed(
  () => form.application_deadline || minimumDeadline.value,
)

const fetchCompanyProfile = async () => {
  loadingProfile.value = true
  profileError.value = ''

  try {
    const response = await companyAPI.getProfile()
    companyProfile.value = response.data.profile || {}
  } catch (requestError) {
    console.error('Unable to load company profile:', requestError)

    profileError.value =
      requestError.response?.data?.message ||
      'Unable to verify company account status.'
  } finally {
    loadingProfile.value = false
  }
}

const validateForm = () => {
  if (!form.drive_name.trim()) {
    return 'Drive name is required.'
  }

  if (!form.job_title.trim()) {
    return 'Job title is required.'
  }

  if (!form.job_description.trim()) {
    return 'Job description is required.'
  }

  if (!form.application_deadline) {
    return 'Application deadline is required.'
  }

  const deadline = new Date(form.application_deadline)

  if (deadline <= new Date()) {
    return 'Application deadline must be in the future.'
  }

  if (
    form.min_cgpa !== '' &&
    (Number(form.min_cgpa) < 0 || Number(form.min_cgpa) > 10)
  ) {
    return 'Minimum CGPA must be between 0 and 10.'
  }

  if (
    form.drive_date &&
    new Date(form.drive_date) < deadline
  ) {
    return 'Drive date cannot be before the application deadline.'
  }

  return ''
}

const buildPayload = () => ({
  drive_name: form.drive_name.trim(),
  job_title: form.job_title.trim(),
  job_description: form.job_description.trim(),
  eligibility_criteria: form.eligibility_criteria.trim(),
  min_cgpa:
    form.min_cgpa === '' ? null : Number(form.min_cgpa),
  allowed_branches: form.allowed_branches
    .split(',')
    .map((branch) => branch.trim())
    .filter(Boolean)
    .join(', '),
  application_deadline: form.application_deadline,
  drive_date: form.drive_date || null,
})

const submitForm = async () => {
  if (!canCreateDrive.value) {
    messageStore.updateErrorMessages(
      'Your company cannot create placement drives at this time.',
    )

    return
  }

  const validationError = validateForm()

  if (validationError) {
    messageStore.updateErrorMessages(validationError)
    return
  }

  submitting.value = true

  try {
    await companyAPI.createDrive(buildPayload())

    messageStore.updateSuccessMessages(
      'Placement drive created and sent for admin approval.',
    )

    router.push('/company/drives')
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to create the placement drive.',
    )
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/company/drives')
}

onMounted(fetchCompanyProfile)
</script>

<template>
  <div class="create-drive-page fade-in">
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

        <h1 class="dashboard-title">Create placement drive</h1>

        <p class="page-subtitle">
          Add a recruitment opportunity for institute review.
        </p>
      </div>
    </header>

    <div
      v-if="loadingProfile"
      class="page-state"
      aria-live="polite"
    >
      <div
        class="spinner-border spinner-border-sm"
        role="status"
      >
        <span class="visually-hidden">
          Checking company status
        </span>
      </div>

      <span>Checking company account status...</span>
    </div>

    <div
      v-else-if="profileError"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Company status could not be verified</strong>
        <p>{{ profileError }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchCompanyProfile"
      >
        Retry
      </button>
    </div>

    <section
      v-else-if="!canCreateDrive"
      class="access-state"
    >
      <span class="access-icon">
        <i
          :class="[
            'bi',
            companyProfile.is_blacklisted
              ? 'bi-slash-circle'
              : companyProfile.approval_status === 'rejected'
                ? 'bi-x-circle'
                : 'bi-clock',
          ]"
        ></i>
      </span>

      <h2>{{ accessTitle }}</h2>
      <p>{{ accessMessage }}</p>

      <button
        type="button"
        class="btn btn-primary"
        @click="router.push('/company/dashboard')"
      >
        Return to dashboard
      </button>
    </section>

    <form
      v-else
      class="form-layout"
      @submit.prevent="submitForm"
    >
      <div class="form-column">
        <section class="card">
          <div class="card-header">
            <div>
              <h2>Role information</h2>
              <p>Describe the recruitment opportunity.</p>
            </div>
          </div>

          <div class="card-body form-section">
            <div class="field-group">
              <label
                for="driveName"
                class="form-label"
              >
                Drive name
                <span aria-hidden="true">*</span>
              </label>

              <input
                id="driveName"
                v-model.trim="form.drive_name"
                type="text"
                class="form-control"
                maxlength="255"
                placeholder="Example: Graduate Hiring 2027"
                autocomplete="off"
                required
              />
            </div>

            <div class="field-group">
              <label
                for="jobTitle"
                class="form-label"
              >
                Job title
                <span aria-hidden="true">*</span>
              </label>

              <input
                id="jobTitle"
                v-model.trim="form.job_title"
                type="text"
                class="form-control"
                maxlength="255"
                placeholder="Example: Data Analyst"
                autocomplete="off"
                required
              />
            </div>

            <div class="field-group">
              <label
                for="jobDescription"
                class="form-label"
              >
                Job description
                <span aria-hidden="true">*</span>
              </label>

              <textarea
                id="jobDescription"
                v-model="form.job_description"
                class="form-control"
                rows="7"
                placeholder="Describe the role, responsibilities and recruitment process."
                required
              ></textarea>

              <small class="field-help">
                Include enough information for students to evaluate the role.
              </small>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-header">
            <div>
              <h2>Eligibility</h2>
              <p>Define who can apply to this drive.</p>
            </div>
          </div>

          <div class="card-body form-section">
            <div class="field-grid">
              <div class="field-group">
                <label
                  for="minCgpa"
                  class="form-label"
                >
                  Minimum CGPA
                </label>

                <input
                  id="minCgpa"
                  v-model="form.min_cgpa"
                  type="number"
                  class="form-control"
                  min="0"
                  max="10"
                  step="0.01"
                  placeholder="Example: 7.50"
                />

                <small class="field-help">
                  Leave blank if there is no CGPA restriction.
                </small>
              </div>

              <div class="field-group">
                <label
                  for="allowedBranches"
                  class="form-label"
                >
                  Allowed branches
                </label>

                <input
                  id="allowedBranches"
                  v-model="form.allowed_branches"
                  type="text"
                  class="form-control"
                  maxlength="500"
                  placeholder="CSE, ECE, EE"
                  autocomplete="off"
                />

                <small class="field-help">
                  Enter comma-separated branch names.
                </small>
              </div>
            </div>

            <div class="field-group">
              <label
                for="eligibilityCriteria"
                class="form-label"
              >
                Additional eligibility criteria
              </label>

              <textarea
                id="eligibilityCriteria"
                v-model="form.eligibility_criteria"
                class="form-control"
                rows="4"
                placeholder="Example: No active backlogs. Graduating batch of 2027."
              ></textarea>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-header">
            <div>
              <h2>Schedule</h2>
              <p>Set the application deadline and planned drive date.</p>
            </div>
          </div>

          <div class="card-body form-section">
            <div class="field-grid">
              <div class="field-group">
                <label
                  for="applicationDeadline"
                  class="form-label"
                >
                  Application deadline
                  <span aria-hidden="true">*</span>
                </label>

                <input
                  id="applicationDeadline"
                  v-model="form.application_deadline"
                  type="datetime-local"
                  class="form-control"
                  :min="minimumDeadline"
                  required
                />
              </div>

              <div class="field-group">
                <label
                  for="driveDate"
                  class="form-label"
                >
                  Drive date
                </label>

                <input
                  id="driveDate"
                  v-model="form.drive_date"
                  type="datetime-local"
                  class="form-control"
                  :min="minimumDriveDate"
                />

                <small class="field-help">
                  Optional. It must be after the application deadline.
                </small>
              </div>
            </div>
          </div>
        </section>

        <div class="form-actions">
          <button
            type="button"
            class="btn btn-outline-secondary"
            :disabled="submitting"
            @click="goBack"
          >
            Cancel
          </button>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="submitting"
          >
            <span
              v-if="submitting"
              class="spinner-border spinner-border-sm"
              aria-hidden="true"
            ></span>

            <i
              v-else
              class="bi bi-arrow-right"
            ></i>

            {{
              submitting
                ? 'Creating drive...'
                : 'Submit for approval'
            }}
          </button>
        </div>
      </div>

      <aside class="form-sidebar">
        <section class="guidance-card">
          <span class="guidance-label">Approval process</span>

          <h2>What happens next?</h2>

          <ol>
            <li>
              <span>1</span>
              <p>The placement drive is submitted as pending.</p>
            </li>

            <li>
              <span>2</span>
              <p>The institute placement cell reviews the drive.</p>
            </li>

            <li>
              <span>3</span>
              <p>Approved drives become visible to eligible students.</p>
            </li>
          </ol>
        </section>

        <section class="note-card">
          <i class="bi bi-info-circle"></i>

          <div>
            <strong>Before submitting</strong>

            <p>
              Check the deadline, CGPA requirement and branch names carefully.
              Pending drives can be edited before approval.
            </p>
          </div>
        </section>
      </aside>
    </form>
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

.access-state {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  min-height: 430px;
  padding: 40px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  text-align: center;
}

.access-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-bottom: 18px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 12px;
  font-size: 1.25rem;
}

.access-state h2 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1.15rem;
  font-weight: 650;
}

.access-state p {
  max-width: 500px;
  margin: 9px 0 22px;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  line-height: 1.65;
}

.form-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(270px, 0.55fr);
  gap: 20px;
  align-items: start;
}

.form-column,
.form-sidebar {
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

.guidance-card {
  padding: 22px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: var(--border-radius);
}

.guidance-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
}

.guidance-card h2 {
  margin: 7px 0 20px;
  font-size: 1.05rem;
  font-weight: 650;
}

.guidance-card ol {
  display: flex;
  flex-direction: column;
  gap: 17px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.guidance-card li {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.guidance-card li > span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 25px;
  width: 25px;
  height: 25px;
  color: var(--color-primary);
  background: #ffffff;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: 700;
}

.guidance-card p {
  margin: 2px 0 0;
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.76rem;
  line-height: 1.55;
}

.note-card {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  margin-top: 20px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.note-card > i {
  color: var(--color-accent);
}

.note-card strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.note-card p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
  line-height: 1.55;
}

@media (max-width: 991.98px) {
  .form-layout {
    grid-template-columns: 1fr;
  }

  .form-sidebar {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .note-card {
    margin-top: 0;
  }
}

@media (max-width: 767.98px) {
  .field-grid,
  .form-sidebar {
    grid-template-columns: 1fr;
  }

  .form-actions {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>