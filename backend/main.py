import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

from config import settings
from services.api_health import api_health
from services.question_bank_service import question_bank

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 載入題庫
    question_bank.load()
    logger.info('題庫狀態: %s', question_bank.get_status())

    # 設定 API key 狀態（env 層級）
    api_health.set_has_api_key(bool(settings.anthropic_api_key))

    yield


app = FastAPI(title='AI English Tutor API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=['POST', 'GET'],
    allow_headers=['Content-Type', 'X-Api-Key'],
)

# 預設 client（用 env key）
_default_client = None
if settings.anthropic_api_key:
    _default_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _get_client(request_api_key: str | None) -> anthropic.Anthropic | None:
    """取得 Anthropic client：request key > env key > None"""
    if request_api_key:
        return anthropic.Anthropic(api_key=request_api_key)
    return _default_client


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
def chat(req: ChatRequest, request: Request):
    system_prompt = req.system_prompt or 'You are a helpful English tutor.'
    user_message = req.messages[-1].content if req.messages else ''

    # 從 header 取得 API key
    request_api_key = request.headers.get('X-Api-Key')
    client = _get_client(request_api_key)
    has_key = client is not None

    # 判斷是否嘗試 API
    should_try = has_key and (request_api_key or api_health.should_try_api)

    if should_try:
        try:
            max_tokens = (
                min(req.max_tokens, settings.max_tokens_limit)
                if req.max_tokens > 0
                else settings.default_max_tokens
            )
            resp = client.messages.create(
                model=settings.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[m.model_dump() for m in req.messages],
            )
            if not request_api_key:
                api_health.mark_success()
            return ChatResponse(reply=resp.content[0].text)
        except anthropic.APIError as e:
            logger.warning('Claude API 失敗: %s', e)
            if not request_api_key:
                api_health.mark_failure()
        except Exception as e:
            logger.warning('Claude API 未預期錯誤: %s', e)
            if not request_api_key:
                api_health.mark_failure()

    # Fallback 到題庫
    reply = question_bank.get_fallback_reply(system_prompt, user_message)
    return ChatResponse(reply=reply)


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api/status')
def status():
    """系統狀態（API + 題庫）"""
    return {
        'api': api_health.get_status(),
        'question_bank': question_bank.get_status(),
    }
