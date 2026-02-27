# AI English Tutor

Voice-first English speaking practice tool built for interview preparation. Simulates real conversation scenarios with AI, supports speech input/output, and provides grammar feedback on demand.

Built this to prep for a remote AI Red Teamer position -- needed a way to rehearse English interview conversations with instant feedback on grammar mistakes.

## What it does

- **Scenario simulation** -- practice with pre-configured conversation contexts (e.g. recruiter intro call) or free chat
- **Voice input/output** -- Web Speech API for recognition, browser TTS for playback
- **Grammar correction mode** -- toggle on to get per-message grammar notes in Traditional Chinese, displayed below the AI response without interrupting conversation flow
- **Quick phrases** -- tap common phrases to keep the conversation moving when you're stuck
- **Chat export** -- download the full conversation as Markdown, grammar notes included

## Architecture

```
frontend/                    backend/
Vue 3 + TypeScript + PrimeVue    FastAPI + Anthropic SDK
                 |                        |
                 +--- POST /api/chat -----+
                                          |
                                   Claude API (Sonnet)
```

The grammar correction works by appending instructions to the system prompt when enabled. Claude returns the normal response and grammar notes separated by a delimiter (`---GRAMMAR---`). The frontend splits the response and renders them separately -- TTS only reads the conversational part.

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | Vue 3.5, TypeScript 5.9, Vite 7, PrimeVue 4 |
| Backend | FastAPI, Pydantic, Anthropic Python SDK |
| AI | Claude Sonnet |
| Speech | Web Speech API (recognition + synthesis) |

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

uvicorn main:app --port 8004
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5172`.

## Project structure

```
backend/
  main.py              # FastAPI app, single /api/chat endpoint
  config.py            # Settings (model, token limits, CORS)

frontend/src/
  composables/
    useChat.ts          # Chat state, grammar mode, message splitting
    useSpeechRecognition.ts
    useSpeechSynthesis.ts
  components/
    ChatMessage.vue     # Message bubble + grammar note block
    ChatHistory.vue     # Scrollable message list
    VoiceButton.vue     # 4-state mic button (idle/listening/processing/speaking)
    PhraseHelper.vue    # Quick phrase chips
  config/
    scenarios.ts        # Conversation scenarios with system prompts
  utils/
    chat-export.ts      # Markdown export with Blob download
  App.vue               # Layout, wiring, header controls
```

## License

MIT
