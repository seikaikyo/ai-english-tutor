import { ref, computed } from 'vue'
import { API_BASE } from '../config/api'
import { scenarios, type Scenario } from '../config/scenarios'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  grammarNote?: string
  translation?: string
}

const GRAMMAR_PROMPT_SUFFIX = `
---GRAMMAR_MODE---
After your normal response, add a grammar correction section.
Use the separator "---GRAMMAR---" on its own line.
In the grammar section:
1. Quote incorrect or unnatural phrases from the user's latest message
2. Provide the corrected version
3. Explain briefly in Traditional Chinese (zh-TW)
4. If no errors, briefly note in Traditional Chinese
Keep corrections concise.`

const TRANSLATION_PROMPT_SUFFIX = `
---TRANSLATION_MODE---
After your normal response (and after the grammar section if present), add a translation section.
Use the separator "---TRANSLATION---" on its own line.
In the translation section:
- Translate your English response into natural Traditional Chinese (zh-TW)
- Keep the translation concise and natural, matching the tone of the original
- Do NOT translate the grammar notes, only the main conversational response`

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const grammarMode = ref(false)
  const translationMode = ref(true)
  const currentScenarioId = ref(scenarios[0]!.id)

  // API key 管理
  const apiEnabled = ref(localStorage.getItem('apiEnabled') === 'true')
  const apiKey = ref(localStorage.getItem('apiKey') || '')

  function setApiEnabled(value: boolean) {
    apiEnabled.value = value
    localStorage.setItem('apiEnabled', String(value))
  }

  function setApiKey(key: string) {
    apiKey.value = key
    localStorage.setItem('apiKey', key)
  }

  const currentScenario = computed<Scenario>(
    () => scenarios.find(s => s.id === currentScenarioId.value) ?? scenarios[0]!
  )

  function switchScenario(id: string) {
    currentScenarioId.value = id
    messages.value = []
    addGreeting()
  }

  function addGreeting() {
    const scenario = currentScenario.value
    if (scenario.greeting) {
      messages.value.push({
        role: 'assistant',
        content: scenario.greeting,
        timestamp: Date.now(),
        ...(translationMode.value && scenario.greetingZh
          ? { translation: scenario.greetingZh }
          : {}),
      })
    }
  }

  async function sendMessage(text: string): Promise<string | null> {
    if (!text.trim() || isLoading.value) return null

    messages.value.push({
      role: 'user',
      content: text.trim(),
      timestamp: Date.now(),
    })

    isLoading.value = true

    try {
      const apiMessages = messages.value.map(m => ({
        role: m.role,
        content: m.content,
      }))

      let systemPrompt = currentScenario.value.systemPrompt
      if (grammarMode.value) systemPrompt += GRAMMAR_PROMPT_SUFFIX
      if (translationMode.value) systemPrompt += TRANSLATION_PROMPT_SUFFIX

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (apiEnabled.value && apiKey.value) {
        headers['X-Api-Key'] = apiKey.value
      }

      let maxTokens = 300
      if (grammarMode.value && translationMode.value) maxTokens = 1000
      else if (translationMode.value) maxTokens = 800
      else if (grammarMode.value) maxTokens = 600

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          messages: apiMessages,
          system_prompt: systemPrompt,
          max_tokens: maxTokens,
        }),
      })

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`)
      }

      const data = await res.json()
      let reply = data.reply as string
      let grammarNote: string | undefined
      let translation: string | undefined

      // 先拆翻譯（在最後面）
      if (translationMode.value && reply.includes('---TRANSLATION---')) {
        const parts = reply.split('---TRANSLATION---')
        reply = (parts[0] ?? '').trim()
        translation = (parts[1] ?? '').trim()
      }

      // 再拆文法（在中間）
      if (grammarMode.value && reply.includes('---GRAMMAR---')) {
        const parts = reply.split('---GRAMMAR---')
        reply = (parts[0] ?? '').trim()
        grammarNote = (parts[1] ?? '').trim()
      }

      messages.value.push({
        role: 'assistant',
        content: reply,
        timestamp: Date.now(),
        ...(grammarNote ? { grammarNote } : {}),
        ...(translation ? { translation } : {}),
      })

      return reply
    } catch (err) {
      console.error('Chat error:', err)
      messages.value.push({
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: Date.now(),
      })
      return null
    } finally {
      isLoading.value = false
    }
  }

  function clearHistory() {
    messages.value = []
    addGreeting()
  }

  // 初始化招呼語
  addGreeting()

  return {
    messages,
    isLoading,
    grammarMode,
    translationMode,
    apiEnabled,
    apiKey,
    setApiEnabled,
    setApiKey,
    currentScenario,
    currentScenarioId,
    scenarios,
    switchScenario,
    sendMessage,
    clearHistory,
  }
}
