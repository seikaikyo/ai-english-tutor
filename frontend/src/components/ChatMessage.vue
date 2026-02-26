<script setup lang="ts">
import type { ChatMessage } from '../composables/useChat'

const props = defineProps<{
  message: ChatMessage
}>()

const emit = defineEmits<{
  speak: [text: string]
}>()

const isUser = props.message.role === 'user'
</script>

<template>
  <div class="chat-message" :class="{ user: isUser, assistant: !isUser }">
    <div class="bubble">
      <p>{{ message.content }}</p>
      <button
        v-if="!isUser"
        class="speak-btn"
        title="Read aloud"
        @click="emit('speak', message.content)"
      >
        <i class="pi pi-volume-up" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  display: flex;
  margin-bottom: 12px;
  padding: 0 16px;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: var(--radius-bubble);
  line-height: 1.5;
  font-size: 15px;
  position: relative;
}

.user .bubble {
  background: var(--color-user-bubble);
  color: var(--color-user-text);
  border-bottom-right-radius: 4px;
}

.assistant .bubble {
  background: var(--color-ai-bubble);
  color: var(--color-ai-text);
  border-bottom-left-radius: 4px;
}

.bubble p {
  margin: 0;
}

.speak-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--color-surface);
  color: var(--color-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  opacity: 0;
  transition: opacity 0.2s;
}

.bubble:hover .speak-btn {
  opacity: 1;
}

.speak-btn:hover {
  color: var(--color-user-bubble);
}
</style>
