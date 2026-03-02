<script setup lang="ts">
import type { Phrase } from '../config/scenarios'

defineProps<{
  phrases: Phrase[]
  showZh?: boolean
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
        :key="phrase.en"
        class="phrase-chip"
        :title="phrase.zh"
        @click="emit('select', phrase.en)"
      >
        <span class="phrase-en">{{ phrase.en }}</span>
        <span v-if="showZh" class="phrase-zh">{{ phrase.zh }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.phrase-helper {
  padding: 8px 0;
  border-top: 1px solid #e2e8f0;
  overflow: hidden;
}

.phrase-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 16px;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.phrase-chip:hover {
  background: #f1f5f9;
  border-color: var(--color-user-bubble);
  color: var(--color-user-bubble);
}

.phrase-zh {
  font-size: 11px;
  color: #9ca3af;
}

.phrase-chip:hover .phrase-zh {
  color: var(--color-user-bubble);
  opacity: 0.7;
}
</style>
