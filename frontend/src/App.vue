<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import ChatHistory from './components/ChatHistory.vue'
import VoiceButton from './components/VoiceButton.vue'
import PhraseHelper from './components/PhraseHelper.vue'
import { useChat } from './composables/useChat'
import { useSpeechRecognition } from './composables/useSpeechRecognition'
import { useSpeechSynthesis } from './composables/useSpeechSynthesis'

const toast = useToast()
const chat = useChat()
const stt = useSpeechRecognition()
const tts = useSpeechSynthesis()

const textInput = ref('')

// 語音按鈕四態
const voiceState = computed<'idle' | 'listening' | 'processing' | 'speaking'>(() => {
  if (tts.isSpeaking.value) return 'speaking'
  if (chat.isLoading.value) return 'processing'
  if (stt.isListening.value) return 'listening'
  return 'idle'
})

// 場景選項
const scenarioOptions = chat.scenarios.map(s => ({
  label: s.label,
  value: s.id,
}))

// 語音辨識完成 → 自動送出
watch(stt.transcript, async (text) => {
  if (!text) return
  const reply = await chat.sendMessage(text)
  if (reply) {
    await tts.speak(reply)
  }
})

// 文字送出
async function handleSend() {
  const text = textInput.value.trim()
  if (!text) return
  textInput.value = ''
  const reply = await chat.sendMessage(text)
  if (reply) {
    await tts.speak(reply)
  }
}

// 快捷片語
async function handlePhrase(phrase: string) {
  const reply = await chat.sendMessage(phrase)
  if (reply) {
    await tts.speak(reply)
  }
}

// 麥克風切換
function toggleVoice() {
  if (stt.isListening.value) {
    stt.stop()
  } else if (tts.isSpeaking.value) {
    tts.stop()
  } else {
    stt.start()
  }
}

// 朗讀指定訊息
async function handleSpeak(text: string) {
  await tts.speak(text)
}

// 場景切換
function handleScenarioChange(event: any) {
  chat.switchScenario(event.value)
  toast.add({
    severity: 'info',
    summary: 'Scenario changed',
    life: 2000,
  })
}
</script>

<template>
  <Toast />
  <div class="app-container">
    <!-- 頂部列 -->
    <header class="app-header">
      <h1>English Tutor</h1>
      <div class="header-actions">
        <Select
          :modelValue="chat.currentScenarioId.value"
          :options="scenarioOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Scenario"
          class="scenario-select"
          @update:modelValue="handleScenarioChange"
        />
        <Button
          icon="pi pi-trash"
          severity="secondary"
          text
          rounded
          title="Clear history"
          @click="chat.clearHistory()"
        />
      </div>
    </header>

    <!-- 對話區 -->
    <ChatHistory
      :messages="chat.messages.value"
      :isLoading="chat.isLoading.value"
      @speak="handleSpeak"
    />

    <!-- 即時辨識文字 -->
    <div v-if="stt.interimTranscript.value" class="interim-text">
      {{ stt.interimTranscript.value }}
    </div>

    <!-- 快捷片語 -->
    <PhraseHelper
      :phrases="chat.currentScenario.value.phrases"
      @select="handlePhrase"
    />

    <!-- 底部控制區 -->
    <footer class="app-footer">
      <div class="input-row">
        <InputText
          v-model="textInput"
          placeholder="Type a message..."
          class="text-input"
          @keyup.enter="handleSend"
        />
        <Button
          icon="pi pi-send"
          :disabled="!textInput.trim() || chat.isLoading.value"
          @click="handleSend"
        />
      </div>
      <VoiceButton
        :state="voiceState"
        :supported="stt.isSupported.value"
        @toggle="toggleVoice"
      />
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  max-width: 640px;
  margin: 0 auto;
  background: var(--color-surface);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.app-header h1 {
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.scenario-select {
  width: 180px;
}

.interim-text {
  padding: 4px 32px;
  font-size: 14px;
  color: var(--color-muted);
  font-style: italic;
}

.app-footer {
  padding: 12px 16px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.input-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.text-input {
  flex: 1;
}

@media (max-width: 640px) {
  .app-container {
    max-width: 100%;
  }
}
</style>
