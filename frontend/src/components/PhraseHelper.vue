<script setup lang="ts">
defineProps<{
  phrases: string[]
}>()

const emit = defineEmits<{
  select: [phrase: string]
}>()
</script>

<template>
  <div class="phrase-helper">
    <div class="phrase-scroll">
      <button
        v-for="phrase in phrases"
        :key="phrase"
        class="phrase-chip"
        @click="emit('select', phrase)"
      >
        {{ phrase }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.phrase-helper {
  padding: 8px 0;
  border-top: 1px solid #e2e8f0;
}

.phrase-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 16px;
  scrollbar-width: none;
}

.phrase-scroll::-webkit-scrollbar {
  display: none;
}

.phrase-chip {
  flex-shrink: 0;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: var(--color-surface);
  color: #475569;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s, border-color 0.2s;
}

.phrase-chip:hover {
  background: #f1f5f9;
  border-color: var(--color-user-bubble);
  color: var(--color-user-bubble);
}
</style>
