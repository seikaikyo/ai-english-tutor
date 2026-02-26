import { ref, onUnmounted } from 'vue'

// 擴展 Window 型別
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

export function useSpeechRecognition() {
  const isListening = ref(false)
  const transcript = ref('')
  const interimTranscript = ref('')
  const isSupported = ref(false)

  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

  isSupported.value = !!SpeechRecognition

  let recognition: any = null

  if (SpeechRecognition) {
    recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = true
    recognition.continuous = false

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          final += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }

      if (final) {
        transcript.value = final
      }
      interimTranscript.value = interim
    }

    recognition.onend = () => {
      isListening.value = false
      interimTranscript.value = ''
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      isListening.value = false
      interimTranscript.value = ''
    }
  }

  function start() {
    if (!recognition || isListening.value) return
    transcript.value = ''
    interimTranscript.value = ''
    recognition.start()
    isListening.value = true
  }

  function stop() {
    if (!recognition || !isListening.value) return
    recognition.stop()
  }

  onUnmounted(() => {
    if (recognition && isListening.value) {
      recognition.abort()
    }
  })

  return {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    start,
    stop,
  }
}
