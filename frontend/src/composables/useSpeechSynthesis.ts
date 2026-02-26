import { ref } from 'vue'

export function useSpeechSynthesis() {
  const isSpeaking = ref(false)
  const isSupported = ref('speechSynthesis' in window)

  let currentUtterance: SpeechSynthesisUtterance | null = null

  function getPreferredVoice(): SpeechSynthesisVoice | null {
    const voices = speechSynthesis.getVoices()
    // 偏好自然度高的英語語音
    const preferred = [
      'Samantha', 'Karen', 'Daniel',  // macOS
      'Google US English', 'Google UK English Female',  // Chrome
    ]

    for (const name of preferred) {
      const voice = voices.find(v => v.name.includes(name) && v.lang.startsWith('en'))
      if (voice) return voice
    }

    // fallback: 第一個英語語音
    return voices.find(v => v.lang.startsWith('en')) || null
  }

  function speak(text: string): Promise<void> {
    return new Promise((resolve) => {
      if (!isSupported.value) {
        resolve()
        return
      }

      stop()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.pitch = 1.0

      const voice = getPreferredVoice()
      if (voice) {
        utterance.voice = voice
      }

      utterance.onstart = () => {
        isSpeaking.value = true
      }

      utterance.onend = () => {
        isSpeaking.value = false
        currentUtterance = null
        resolve()
      }

      utterance.onerror = () => {
        isSpeaking.value = false
        currentUtterance = null
        resolve()
      }

      currentUtterance = utterance
      speechSynthesis.speak(utterance)
    })
  }

  function stop() {
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel()
    }
    isSpeaking.value = false
    currentUtterance = null
  }

  // 預載語音清單（某些瀏覽器需要）
  if (isSupported.value) {
    speechSynthesis.getVoices()
    speechSynthesis.onvoiceschanged = () => {
      speechSynthesis.getVoices()
    }
  }

  return {
    isSpeaking,
    isSupported,
    speak,
    stop,
  }
}
