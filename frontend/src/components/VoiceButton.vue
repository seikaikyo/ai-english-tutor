<script setup lang="ts">
defineProps<{
  state: 'idle' | 'listening' | 'processing' | 'speaking'
  supported: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const stateConfig = {
  idle: { icon: 'pi-microphone', label: 'Tap to speak' },
  listening: { icon: 'pi-microphone', label: 'Listening...' },
  processing: { icon: 'pi-spin pi-spinner', label: 'Thinking...' },
  speaking: { icon: 'pi-volume-up', label: 'Speaking...' },
}
</script>

<template>
  <div class="voice-button-wrapper">
    <button
      class="voice-button"
      :class="state"
      :disabled="!supported || state === 'processing'"
      @click="emit('toggle')"
    >
      <i class="pi" :class="stateConfig[state].icon" />
    </button>
    <span class="voice-label">{{ supported ? stateConfig[state].label : 'Voice not supported' }}</span>
  </div>
</template>

<style scoped>
.voice-button-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.voice-button {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: none;
  background: var(--color-user-bubble);
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.voice-button:hover:not(:disabled) {
  transform: scale(1.05);
}

.voice-button:active:not(:disabled) {
  transform: scale(0.95);
}

.voice-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.voice-button.listening {
  background: #ef4444;
  animation: pulse 1.5s infinite;
}

.voice-button.processing {
  background: #f59e0b;
}

.voice-button.speaking {
  background: #10b981;
  animation: pulse 2s infinite;
}

.voice-label {
  font-size: 13px;
  color: var(--color-muted);
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 16px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
</style>
