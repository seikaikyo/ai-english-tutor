from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

from config import settings

app = FastAPI(title='AI English Tutor API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=['POST'],
    allow_headers=['Content-Type'],
)

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    system_prompt: str = ''
    max_tokens: int = 0


class ChatResponse(BaseModel):
    reply: str


@app.post('/api/chat', response_model=ChatResponse)
def chat(req: ChatRequest):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail='ANTHROPIC_API_KEY not set')

    try:
        max_tokens = min(req.max_tokens, settings.max_tokens_limit) if req.max_tokens > 0 else settings.default_max_tokens
        resp = client.messages.create(
            model=settings.model,
            max_tokens=max_tokens,
            system=req.system_prompt or 'You are a helpful English tutor.',
            messages=[m.model_dump() for m in req.messages],
        )
        return ChatResponse(reply=resp.content[0].text)
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get('/api/health')
def health():
    return {'status': 'ok'}
