<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage as ChatMsg } from '../composables/useChat'
import ChatMessage from './ChatMessage.vue'

const props = defineProps<{
  messages: ChatMsg[]
  isLoading: boolean
}>()

const emit = defineEmits<{
  speak: [text: string]
}>()

const scrollContainer = ref<HTMLElement | null>(null)

watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  }
)
</script>

<template>
  <div ref="scrollContainer" class="chat-history">
    <ChatMessage
      v-for="msg in messages"
      :key="msg.timestamp"
      :message="msg"
      @speak="emit('speak', $event)"
    />
    <div v-if="isLoading" class="typing-indicator">
      <span /><span /><span />
    </div>
  </div>
</template>

<style scoped>
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  scroll-behavior: smooth;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 32px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-muted);
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.32s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
