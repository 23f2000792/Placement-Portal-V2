<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const role = ref('student')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMessage = ref('')

const studentProfile = ref({
  name: '',
  roll_number: '',
  branch: '',
  cgpa: '',
  graduation_year: '',
  phone: '',
})

const companyProfile = ref({
  company_name: '',
  hr_name: '',
  hr_email: '',
  hr_phone: '',
  website: '',
  industry: '',
  location: '',
  description: '',
})

const handleRegister = async () => {
  errorMessage.value = ''

  const registrationData = {
    email: email.value.trim(),
    password: password.value,
    profile:
      role.value === 'student'
        ? { ...studentProfile.value }
        : { ...companyProfile.value },
  }

  const result =
    role.value === 'student'
      ? await authStore.registerStudent(registrationData)
      : await authStore.registerCompany(registrationData)

  if (!result.success) {
    errorMessage.value =
      result.error || 'Unable to create account.'

    return
  }

  await router.push({
    path: '/login',
    query: {
      registered: role.value,
    },
  })
}
</script>

<template>
  <main class="registration-page">
    <section class="registration-shell">
      <header class="page-header">
        <RouterLink
          to="/login"
          class="brand"
        >
          <span class="brand-mark">P</span>

          <span>
            <span class="brand-name">Placement Portal</span>
            <span class="brand-description">Institute Placement Cell</span>
          </span>
        </RouterLink>

        <RouterLink
          to="/login"
          class="sign-in-link"
        >
          Already registered? Sign in
        </RouterLink>
      </header>

      <div class="registration-content">
        <div class="registration-heading">
          <span class="eyebrow">Create account</span>

          <h1>Join the placement portal</h1>

          <p>
            Select your account type and provide the required profile
            information.
          </p>
        </div>

        <div
          v-if="errorMessage"
          class="alert alert-danger"
          role="alert"
        >
          {{ errorMessage }}
        </div>

        <div
          class="role-selector"
          role="group"
          aria-label="Account type"
        >
          <button
            type="button"
            class="role-option"
            :class="{ active: role === 'student' }"
            @click="role = 'student'"
          >
            <span class="role-icon">
              <i class="bi bi-mortarboard"></i>
            </span>

            <span>
              <strong>Student</strong>
              <small>Apply to placement drives</small>
            </span>
          </button>

          <button
            type="button"
            class="role-option"
            :class="{ active: role === 'company' }"
            @click="role = 'company'"
          >
            <span class="role-icon">
              <i class="bi bi-building"></i>
            </span>

            <span>
              <strong>Company</strong>
              <small>Conduct recruitment drives</small>
            </span>
          </button>
        </div>

        <form @submit.prevent="handleRegister">
          <section class="form-section">
            <div class="section-heading">
              <h2>Account details</h2>
              <p>Credentials used to sign in to the portal.</p>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label
                  for="email"
                  class="form-label"
                >
                  Email address
                </label>

                <input
                  id="email"
                  v-model="email"
                  type="email"
                  class="form-control"
                  placeholder="name@example.com"
                  autocomplete="email"
                  required
                  :disabled="authStore.loading"
                />
              </div>

              <div class="col-md-6">
                <label
                  for="password"
                  class="form-label"
                >
                  Password
                </label>

                <div class="password-field">
                  <input
                    id="password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="Create a password"
                    autocomplete="new-password"
                    minlength="8"
                    required
                    :disabled="authStore.loading"
                  />

                  <button
                    type="button"
                    class="password-toggle"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                    @click="showPassword = !showPassword"
                  >
                    <i
                      class="bi"
                      :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"
                    ></i>
                  </button>
                </div>

                <div class="form-text">
                  Minimum 8 characters. Use uppercase, lowercase and a number.
                </div>
              </div>
            </div>
          </section>

          <section
            v-if="role === 'student'"
            class="form-section"
          >
            <div class="section-heading">
              <h2>Student profile</h2>
              <p>Academic details used for drive eligibility checks.</p>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label
                  for="student-name"
                  class="form-label"
                >
                  Full name
                </label>

                <input
                  id="student-name"
                  v-model.trim="studentProfile.name"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label
                  for="roll-number"
                  class="form-label"
                >
                  Roll number
                </label>

                <input
                  id="roll-number"
                  v-model.trim="studentProfile.roll_number"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-4">
                <label
                  for="branch"
                  class="form-label"
                >
                  Branch
                </label>

                <select
                  id="branch"
                  v-model="studentProfile.branch"
                  class="form-select"
                  required
                >
                  <option value="" disabled>Select branch</option>
                  <option value="Computer Science">Computer Science</option>
                  <option value="Information Technology">
                    Information Technology
                  </option>
                  <option value="Electronics">Electronics</option>
                  <option value="Mechanical">Mechanical</option>
                  <option value="Civil">Civil</option>
                </select>
              </div>

              <div class="col-md-4">
                <label
                  for="cgpa"
                  class="form-label"
                >
                  CGPA
                </label>

                <input
                  id="cgpa"
                  v-model.number="studentProfile.cgpa"
                  type="number"
                  class="form-control"
                  min="0"
                  max="10"
                  step="0.01"
                  placeholder="0.00"
                  required
                />
              </div>

              <div class="col-md-4">
                <label
                  for="graduation-year"
                  class="form-label"
                >
                  Graduation year
                </label>

                <input
                  id="graduation-year"
                  v-model.number="studentProfile.graduation_year"
                  type="number"
                  class="form-control"
                  min="2025"
                  max="2035"
                  placeholder="2027"
                  required
                />
              </div>

              <div class="col-md-6">
                <label
                  for="student-phone"
                  class="form-label"
                >
                  Phone number
                  <span class="optional">Optional</span>
                </label>

                <input
                  id="student-phone"
                  v-model.trim="studentProfile.phone"
                  type="tel"
                  class="form-control"
                  placeholder="+91 98765 43210"
                />
              </div>
            </div>
          </section>

          <section
            v-else
            class="form-section"
          >
            <div class="section-heading">
              <h2>Company profile</h2>
              <p>
                Company registrations are reviewed by the institute before
                placement drives can be created.
              </p>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label
                  for="company-name"
                  class="form-label"
                >
                  Company name
                </label>

                <input
                  id="company-name"
                  v-model.trim="companyProfile.company_name"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label
                  for="industry"
                  class="form-label"
                >
                  Industry
                  <span class="optional">Optional</span>
                </label>

                <input
                  id="industry"
                  v-model.trim="companyProfile.industry"
                  type="text"
                  class="form-control"
                  placeholder="Technology"
                />
              </div>

              <div class="col-md-6">
                <label
                  for="hr-name"
                  class="form-label"
                >
                  HR contact name
                </label>

                <input
                  id="hr-name"
                  v-model.trim="companyProfile.hr_name"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label
                  for="hr-email"
                  class="form-label"
                >
                  HR contact email
                </label>

                <input
                  id="hr-email"
                  v-model.trim="companyProfile.hr_email"
                  type="email"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label
                  for="hr-phone"
                  class="form-label"
                >
                  HR phone
                  <span class="optional">Optional</span>
                </label>

                <input
                  id="hr-phone"
                  v-model.trim="companyProfile.hr_phone"
                  type="tel"
                  class="form-control"
                />
              </div>

              <div class="col-md-6">
                <label
                  for="website"
                  class="form-label"
                >
                  Website
                  <span class="optional">Optional</span>
                </label>

                <input
                  id="website"
                  v-model.trim="companyProfile.website"
                  type="url"
                  class="form-control"
                  placeholder="https://example.com"
                />
              </div>

              <div class="col-md-6">
                <label
                  for="location"
                  class="form-label"
                >
                  Location
                  <span class="optional">Optional</span>
                </label>

                <input
                  id="location"
                  v-model.trim="companyProfile.location"
                  type="text"
                  class="form-control"
                  placeholder="Bengaluru, India"
                />
              </div>

              <div class="col-12">
                <label
                  for="description"
                  class="form-label"
                >
                  Company description
                  <span class="optional">Optional</span>
                </label>

                <textarea
                  id="description"
                  v-model.trim="companyProfile.description"
                  class="form-control"
                  rows="4"
                  placeholder="Briefly describe the company and its work."
                ></textarea>
              </div>
            </div>
          </section>

          <div class="form-actions">
            <p>
              By creating an account, you confirm that the information provided
              is accurate.
            </p>

            <button
              type="submit"
              class="btn btn-primary create-button"
              :disabled="authStore.loading"
            >
              <span
                v-if="authStore.loading"
                class="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>

              <span>
                {{ authStore.loading ? 'Creating account...' : 'Create account' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
.registration-page {
  min-height: 100vh;
  padding: 32px;
  background: var(--color-background);
}

.registration-shell {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 54px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  color: inherit;
}

.brand:hover {
  color: inherit;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: #ffffff;
  background: var(--color-primary);
  border-radius: 8px;
  font-weight: 700;
}

.brand > span:last-child {
  display: flex;
  flex-direction: column;
}

.brand-name {
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 650;
}

.brand-description {
  margin-top: 2px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

.sign-in-link {
  font-size: 0.825rem;
  font-weight: 600;
}

.registration-content {
  max-width: 900px;
  margin: 0 auto;
}

.registration-heading {
  margin-bottom: 30px;
}

.eyebrow {
  color: var(--color-accent);
  font-size: 0.7rem;
  font-weight: 650;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.registration-heading h1 {
  margin: 8px 0;
  font-size: 2rem;
  font-weight: 650;
  letter-spacing: -0.04em;
}

.registration-heading p,
.section-heading p {
  color: var(--color-text-muted);
}

.role-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  color: var(--color-text);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  text-align: left;
  transition:
    border-color var(--transition),
    box-shadow var(--transition);
}

.role-option:hover {
  border-color: #bdc6d4;
}

.role-option.active {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(49, 94, 251, 0.1);
}

.role-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  color: var(--color-primary);
  background: #eef0f4;
  border-radius: 8px;
}

.role-option strong,
.role-option small {
  display: block;
}

.role-option strong {
  font-size: 0.875rem;
  font-weight: 650;
}

.role-option small {
  margin-top: 3px;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.form-section {
  margin-bottom: 20px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
}

.section-heading {
  margin-bottom: 22px;
}

.section-heading h2 {
  margin-bottom: 5px;
  font-size: 1rem;
  font-weight: 650;
}

.section-heading p {
  margin: 0;
  font-size: 0.8rem;
}

.optional {
  margin-left: 4px;
  color: var(--color-text-muted);
  font-size: 0.7rem;
  font-weight: 400;
}

.password-field {
  position: relative;
}

.password-field .form-control {
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0;
  color: var(--color-text-muted);
  background: transparent;
  border: 0;
  transform: translateY(-50%);
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 4px 0 40px;
}

.form-actions p {
  max-width: 500px;
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

.create-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-width: 170px;
  min-height: 42px;
}

@media (max-width: 767.98px) {
  .registration-page {
    padding: 24px 18px;
  }

  .page-header {
    margin-bottom: 42px;
  }

  .sign-in-link {
    font-size: 0.75rem;
  }

  .role-selector {
    grid-template-columns: 1fr;
  }

  .form-section {
    padding: 20px;
  }

  .form-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .create-button {
    width: 100%;
  }
}

@media (max-width: 575.98px) {
  .brand-description {
    display: none;
  }

  .registration-heading h1 {
    font-size: 1.7rem;
  }
}
</style>