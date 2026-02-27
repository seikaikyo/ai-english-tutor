import { ref, computed } from 'vue'
import { API_BASE } from '../config/api'
import { scenarios, type Scenario } from '../config/scenarios'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  grammarNote?: string
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

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const grammarMode = ref(false)
  const currentScenarioId = ref(scenarios[0].id)

  const currentScenario = computed<Scenario>(
    () => scenarios.find(s => s.id === currentScenarioId.value) || scenarios[0]
  )

  function switchScenario(id: string) {
    currentScenarioId.value = id
    messages.value = []
    addGreeting()
  }

  function addGreeting() {
    const greeting = currentScenario.value.greeting
    if (greeting) {
      messages.value.push({
        role: 'assistant',
        content: greeting,
        timestamp: Date.now(),
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

      const systemPrompt = grammarMode.value
        ? currentScenario.value.systemPrompt + GRAMMAR_PROMPT_SUFFIX
        : currentScenario.value.systemPrompt

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          system_prompt: systemPrompt,
          max_tokens: grammarMode.value ? 600 : 300,
        }),
      })

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`)
      }

      const data = await res.json()
      let reply = data.reply as string
      let grammarNote: string | undefined

      if (grammarMode.value && reply.includes('---GRAMMAR---')) {
        const [main, note] = reply.split('---GRAMMAR---')
        reply = main.trim()
        grammarNote = note.trim()
      }

      messages.value.push({
        role: 'assistant',
        content: reply,
        timestamp: Date.now(),
        ...(grammarNote ? { grammarNote } : {}),
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
    currentScenario,
    currentScenarioId,
    scenarios,
    switchScenario,
    sendMessage,
    clearHistory,
  }
}
