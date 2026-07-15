<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },

  value: {
    type: [String, Number],
    default: 0,
  },

  icon: {
    type: String,
    default: 'bi-bar-chart',
  },

  description: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <article class="stat-card">
    <div class="stat-content">
      <span class="stat-title">
        {{ title }}
      </span>

      <strong class="stat-value">
        {{
          typeof value === 'number'
            ? value.toLocaleString('en-IN')
            : value
        }}
      </strong>

      <span
        v-if="description"
        class="stat-description"
      >
        {{ description }}
      </span>
    </div>

    <span class="stat-icon">
      <i :class="['bi', icon]"></i>
    </span>
  </article>
</template>

<style scoped>
.stat-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  min-height: 132px;
  padding: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.stat-content {
  min-width: 0;
}

.stat-title,
.stat-value,
.stat-description {
  display: block;
}

.stat-title {
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-weight: 500;
}

.stat-value {
  margin-top: 9px;
  color: var(--color-primary);
  font-size: 1.65rem;
  font-weight: 650;
  letter-spacing: -0.04em;
  line-height: 1;
}

.stat-description {
  margin-top: 10px;
  color: var(--color-text-muted);
  font-size: 0.68rem;
  line-height: 1.45;
}

.stat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  color: var(--color-primary);
  background: var(--color-surface-muted);
  border-radius: 9px;
  font-size: 0.95rem;
}
</style>