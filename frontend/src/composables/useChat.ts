import { ref, computed } from 'vue'
import { API_BASE } from '../config/api'
import { scenarios, type Scenario } from '../config/scenarios'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
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

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          system_prompt: currentScenario.value.systemPrompt,
        }),
      })

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`)
      }

      const data = await res.json()
      const reply = data.reply as string

      messages.value.push({
        role: 'assistant',
        content: reply,
        timestamp: Date.now(),
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
    currentScenario,
    currentScenarioId,
    scenarios,
    switchScenario,
    sendMessage,
    clearHistory,
  }
}
