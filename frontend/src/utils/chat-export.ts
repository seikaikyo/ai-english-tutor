import type { ChatMessage } from '../composables/useChat'

function formatTime(ts: number): string {
  const d = new Date(ts)
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

function formatDate(ts: number): string {
  const d = new Date(ts)
  return d.toISOString().slice(0, 16).replace('T', ' ')
}

export function exportChat(messages: ChatMessage[], scenarioLabel: string) {
  if (messages.length === 0) return

  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10)

  const lines: string[] = [
    `# English Tutor - ${scenarioLabel}`,
    '',
    `Date: ${formatDate(now.getTime())}`,
    '',
    '---',
  ]

  for (const msg of messages) {
    const time = formatTime(msg.timestamp)
    const speaker = msg.role === 'user' ? 'You' : 'AI'

    lines.push('')
    lines.push(`**${speaker}** (${time})`)
    lines.push('')
    lines.push(msg.content)

    if (msg.grammarNote) {
      lines.push('')
      lines.push('> **Grammar Note**')
      for (const line of msg.grammarNote.split('\n')) {
        lines.push(`> ${line}`)
      }
    }

    lines.push('')
    lines.push('---')
  }

  const content = lines.join('\n')
  const slug = scenarioLabel.toLowerCase().replace(/\s+/g, '-')
  const filename = `chat-${slug}-${dateStr}.md`

  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
