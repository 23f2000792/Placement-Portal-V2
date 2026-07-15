<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { studentAPI } from '@/services/api'
import { useMessageStore } from '@/stores/message'

const messageStore = useMessageStore()

const loading = ref(true)
const refreshing = ref(false)
const saving = ref(false)
const editing = ref(false)
const uploadingResume = ref(false)
const resumeInput = ref(null)
const error = ref('')

const profile = ref({})

const form = reactive({
  phone: '',
  alternate_email: '',
})

const initials = computed(() => {
  const name = profile.value.name?.trim()

  if (!name) return 'S'

  return name
    .split(/\s+/)
    .map((part) => part.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const cgpa = computed(() => {
  if (
    profile.value.cgpa === null ||
    profile.value.cgpa === undefined
  ) {
    return '—'
  }

  return Number(profile.value.cgpa).toFixed(2)
})

const syncForm = () => {
  form.phone = profile.value.phone || ''
  form.alternate_email =
    profile.value.alternate_email || ''
}

const fetchProfile = async (isRefresh = false) => {
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  error.value = ''

  try {
    const response = await studentAPI.getProfile()

    profile.value = response.data.profile || {}
    syncForm()
  } catch (requestError) {
    console.error(
      'Unable to load student profile:',
      requestError,
    )

    error.value =
      requestError.response?.data?.message ||
      'Unable to load your profile.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const startEditing = () => {
  syncForm()
  editing.value = true
}

const cancelEditing = () => {
  syncForm()
  editing.value = false
}

const saveProfile = async () => {
  if (saving.value) return

  saving.value = true

  try {
    const response = await studentAPI.updateProfile({
      phone: form.phone.trim(),
      alternate_email: form.alternate_email.trim(),
    })

    profile.value =
      response.data.profile || profile.value

    syncForm()
    editing.value = false

    messageStore.updateSuccessMessages(
      'Profile updated successfully.',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to update your profile.',
    )
  } finally {
    saving.value = false
  }
}

const selectResume = () => {
  resumeInput.value?.click()
}

const uploadResume = async (event) => {
  const file = event.target.files?.[0]

  if (!file) return

  if (file.type !== 'application/pdf') {
    messageStore.updateErrorMessages(
      'Please select a PDF resume.',
    )

    event.target.value = ''
    return
  }

  uploadingResume.value = true

  try {
    const response = await studentAPI.uploadResume(file)

    profile.value =
      response.data.profile || profile.value

    messageStore.updateSuccessMessages(
      'Resume uploaded successfully.',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to upload resume.',
    )
  } finally {
    uploadingResume.value = false
    event.target.value = ''
  }
}

const downloadResume = async () => {
  try {
    await studentAPI.downloadResume(
      profile.value.resume_filename || 'resume.pdf',
    )
  } catch (requestError) {
    messageStore.updateErrorMessages(
      requestError.response?.data?.message ||
        'Unable to download resume.',
    )
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<template>
  <div class="student-profile-page fade-in">
    <header class="page-header">
      <div>
        <h1 class="dashboard-title">My profile</h1>

        <p class="page-subtitle">
          Review your academic details and manage contact information.
        </p>
      </div>

      <div class="header-actions">
        <button
          type="button"
          class="btn btn-outline-secondary"
          :disabled="loading || refreshing"
          @click="fetchProfile(true)"
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

        <button
          v-if="!editing"
          type="button"
          class="btn btn-primary"
          :disabled="loading"
          @click="startEditing"
        >
          <i class="bi bi-pencil"></i>
          Edit contact details
        </button>
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
          Loading student profile
        </span>
      </div>

      <span>Loading your profile...</span>
    </div>

    <div
      v-else-if="error"
      class="page-state error-state"
    >
      <i class="bi bi-exclamation-circle"></i>

      <div>
        <strong>Profile could not be loaded</strong>
        <p>{{ error }}</p>
      </div>

      <button
        type="button"
        class="btn btn-outline-secondary btn-sm"
        @click="fetchProfile()"
      >
        Retry
      </button>
    </div>

    <template v-else>
      <section class="profile-grid">
        <aside class="side-column">
          <article class="identity-card">
            <span class="profile-avatar">
              {{ initials }}
            </span>

            <h2>{{ profile.name }}</h2>

            <p>{{ profile.roll_number }}</p>

            <div class="identity-meta">
              <div>
                <span>Branch</span>
                <strong>
                  {{ profile.branch || 'Not provided' }}
                </strong>
              </div>

              <div>
                <span>CGPA</span>
                <strong>{{ cgpa }}</strong>
              </div>
            </div>

            <div class="graduation-year">
              <i class="bi bi-mortarboard"></i>

              <span>
                Class of
                {{ profile.graduation_year || '—' }}
              </span>
            </div>
          </article>

          <article class="card">
            <div class="card-header">
              <h2>Resume</h2>
            </div>
            
            <div class="card-body resume-status">
              <span
                class="resume-icon"
                :class="{
                  'resume-available': profile.has_resume,
                }"
              >
                <i
                  :class="[
                    'bi',
                    profile.has_resume
                      ? 'bi-file-earmark-check'
                      : 'bi-file-earmark',
                  ]"
                ></i>
              </span>
              
              <div class="resume-content">
                <strong>
                  {{
                    profile.has_resume
                      ? profile.resume_filename
                    : 'No resume uploaded'
                  }}
                </strong>
                
                <p>
                  {{
                    profile.has_resume
                      ? 'Your resume is available to placement administrators and companies you apply to.'
                      : 'Upload your resume as a PDF file.'
                  }}
                </p>
                
                <input
                  ref="resumeInput"
                  type="file"
                  accept=".pdf,application/pdf"
                  class="d-none"
                  @change="uploadResume"
                />
                
                <div class="d-flex flex-wrap gap-2 mt-3">
                  <button
                    type="button"
                    class="btn btn-primary btn-sm"
                    :disabled="uploadingResume"
                    @click="selectResume"
                  >

                   <span
                    v-if="uploadingResume"
                   class="spinner-border spinner-border-sm"
                   ></span>

                   <i
                   v-else
                     class="bi bi-upload"
                   ></i>

                   {{
                     uploadingResume
                     ? 'Uploading...'
                     : profile.has_resume
                       ? 'Replace resume'
                       : 'Upload resume'
                   }}
                  </button>

                  <button
                    v-if="profile.has_resume"
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    @click="downloadResume"
                  >
                    <i class="bi bi-download"></i>
                      Download
                  </button>
                </div>
              </div>
            </div>
          </article>
        </aside>

        <main class="main-column">
          <article class="card">
            <div class="card-header section-header">
              <div>
                <h2>Student information</h2>

                <p>
                  Institute and academic information associated with
                  your account.
                </p>
              </div>

              <span class="readonly-label">
                <i class="bi bi-lock"></i>
                Institute managed
              </span>
            </div>

            <div class="card-body details-grid">
              <div class="detail-item">
                <span>Full name</span>
                <strong>{{ profile.name }}</strong>
              </div>

              <div class="detail-item">
                <span>Roll number</span>
                <strong>{{ profile.roll_number }}</strong>
              </div>

              <div class="detail-item">
                <span>Primary email</span>
                <strong>{{ profile.email }}</strong>
              </div>

              <div class="detail-item">
                <span>Branch</span>
                <strong>{{ profile.branch }}</strong>
              </div>

              <div class="detail-item">
                <span>CGPA</span>
                <strong>{{ cgpa }}</strong>
              </div>

              <div class="detail-item">
                <span>Graduation year</span>
                <strong>
                  {{ profile.graduation_year || '—' }}
                </strong>
              </div>
            </div>
          </article>

          <article class="card">
            <div class="card-header section-header">
              <div>
                <h2>Contact information</h2>

                <p>
                  Contact details used for placement communication.
                </p>
              </div>

              <button
                v-if="!editing"
                type="button"
                class="section-link"
                @click="startEditing"
              >
                Edit
              </button>
            </div>

            <div
              v-if="!editing"
              class="card-body details-grid contact-grid"
            >
              <div class="detail-item">
                <span>Phone number</span>

                <strong>
                  {{ profile.phone || 'Not provided' }}
                </strong>
              </div>

              <div class="detail-item">
                <span>Alternate email</span>

                <strong>
                  {{
                    profile.alternate_email ||
                    'Not provided'
                  }}
                </strong>
              </div>
            </div>

            <form
              v-else
              class="card-body"
              @submit.prevent="saveProfile"
            >
              <div class="form-grid">
                <div>
                  <label
                    for="student-phone"
                    class="form-label"
                  >
                    Phone number
                  </label>

                  <input
                    id="student-phone"
                    v-model="form.phone"
                    type="tel"
                    class="form-control"
                    maxlength="20"
                    placeholder="Enter phone number"
                  />
                </div>

                <div>
                  <label
                    for="student-alternate-email"
                    class="form-label"
                  >
                    Alternate email
                  </label>

                  <input
                    id="student-alternate-email"
                    v-model="form.alternate_email"
                    type="email"
                    class="form-control"
                    maxlength="255"
                    placeholder="Enter alternate email"
                  />
                </div>
              </div>

              <div class="form-actions">
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  :disabled="saving"
                  @click="cancelEditing"
                >
                  Cancel
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
                      ? 'Saving...'
                      : 'Save changes'
                  }}
                </button>
              </div>
            </form>
          </article>

          <article class="info-card">
            <i class="bi bi-info-circle"></i>

            <div>
              <strong>Academic profile changes</strong>

              <p>
                Name, roll number, branch, CGPA and graduation year
                are currently read-only because the profile API only
                permits contact information updates.
              </p>
            </div>
          </article>
        </main>
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

.dashboard-title {
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions .btn,
.form-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.profile-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.55fr) minmax(0, 1.45fr);
  gap: 20px;
  align-items: start;
}

.side-column,
.main-column {
  min-width: 0;
}

.identity-card {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 28px 20px 20px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: var(--border-radius);
  text-align: center;
}

.profile-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 15px;
  color: var(--color-primary);
  background: #ffffff;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 700;
}

.identity-card h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 650;
}

.identity-card > p {
  margin: 5px 0 20px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.73rem;
}

.identity-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.identity-meta > div {
  padding: 14px 8px;
}

.identity-meta > div + div {
  border-left: 1px solid rgba(255, 255, 255, 0.12);
}

.identity-meta span,
.identity-meta strong {
  display: block;
}

.identity-meta span {
  color: rgba(255, 255, 255, 0.48);
  font-size: 0.66rem;
}

.identity-meta strong {
  margin-top: 4px;
  color: #ffffff;
  font-size: 0.75rem;
}

.graduation-year {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 17px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.72rem;
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

.readonly-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  padding-top: 7px;
  padding-bottom: 7px;
}

.detail-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
}

.detail-item:nth-child(odd) {
  padding-right: 18px;
}

.detail-item:nth-child(even) {
  padding-left: 18px;
}

.detail-item span,
.detail-item strong {
  display: block;
}

.detail-item span {
  color: var(--color-text-muted);
  font-size: 0.68rem;
}

.detail-item strong {
  overflow-wrap: anywhere;
  margin-top: 5px;
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 600;
}

.contact-grid .detail-item {
  border-bottom: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.form-label {
  color: var(--color-text);
  font-size: 0.75rem;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid var(--color-border);
}

.resume-status {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.resume-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  color: var(--color-text-muted);
  background: var(--color-surface-muted);
  border-radius: 8px;
}

.resume-available {
  color: #23633c;
  background: #e7f4ec;
}

.resume-status strong {
  color: var(--color-primary);
  font-size: 0.8rem;
}

.resume-status p {
  margin: 5px 0 0;
  color: var(--color-text-muted);
  font-size: 0.72rem;
  line-height: 1.55;
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
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .identity-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 767.98px) {
  .page-header,
  .header-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .header-actions .btn {
    width: 100%;
  }

  .details-grid,
  .form-grid,
  .side-column {
    grid-template-columns: 1fr;
  }

  .detail-item:nth-child(odd),
  .detail-item:nth-child(even) {
    padding-right: 0;
    padding-left: 0;
  }

  .identity-card {
    grid-column: auto;
  }
}
</style>