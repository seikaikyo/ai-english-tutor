<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import ToggleSwitch from 'primevue/toggleswitch'
import ChatHistory from './components/ChatHistory.vue'
import VoiceButton from './components/VoiceButton.vue'
import PhraseHelper from './components/PhraseHelper.vue'
import { useChat } from './composables/useChat'
import { useSpeechRecognition } from './composables/useSpeechRecognition'
import { useSpeechSynthesis } from './composables/useSpeechSynthesis'
import { exportChat } from './utils/chat-export'

const toast = useToast()
const chat = useChat()
const stt = useSpeechRecognition()
const tts = useSpeechSynthesis()

const textInput = ref('')
const showSettings = ref(false)

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

// 匯出對話紀錄
function handleExport() {
  exportChat(chat.messages.value, chat.currentScenario.value.label)
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
        <div class="grammar-toggle">
          <label for="grammar-mode">Grammar</label>
          <ToggleSwitch v-model="chat.grammarMode.value" inputId="grammar-mode" />
        </div>
        <Button
          icon="pi pi-download"
          severity="secondary"
          text
          rounded
          title="Export chat"
          :disabled="chat.messages.value.length === 0"
          @click="handleExport"
        />
        <Button
          icon="pi pi-trash"
          severity="secondary"
          text
          rounded
          title="Clear history"
          @click="chat.clearHistory()"
        />
        <Button
          icon="pi pi-cog"
          severity="secondary"
          text
          rounded
          title="Settings"
          @click="showSettings = !showSettings"
        />
      </div>
    </header>

    <!-- 設定面板 -->
    <div v-if="showSettings" class="settings-panel">
      <div class="setting-row">
        <label for="api-toggle">AI Mode</label>
        <ToggleSwitch
          :modelValue="chat.apiEnabled.value"
          inputId="api-toggle"
          @update:modelValue="chat.setApiEnabled($event)"
        />
        <span class="setting-hint">{{ chat.apiEnabled.value ? 'ON' : 'OFF (offline)' }}</span>
      </div>
      <div v-if="chat.apiEnabled.value" class="setting-row">
        <label for="api-key">API Key</label>
        <Password
          :modelValue="chat.apiKey.value"
          inputId="api-key"
          placeholder="sk-ant-..."
          :feedback="false"
          toggleMask
          class="api-key-input"
          @update:modelValue="chat.setApiKey($event)"
        />
      </div>
      <p class="setting-hint">
        {{ chat.apiEnabled.value && chat.apiKey.value ? 'AI interactive mode' : 'Practice with question bank (no API needed)' }}
      </p>
    </div>

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

.grammar-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-muted);
  white-space: nowrap;
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

.settings-panel {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-row label {
  font-size: 13px;
  font-weight: 500;
  min-width: 64px;
}

.setting-hint {
  font-size: 12px;
  color: var(--color-muted);
}

.api-key-input {
  flex: 1;
  max-width: 280px;
}

@media (max-width: 640px) {
  .app-container {
    max-width: 100%;
  }
}
</style>
