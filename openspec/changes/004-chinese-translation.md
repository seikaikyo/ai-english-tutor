---
title: AI 回覆加上正體中文翻譯
type: feature
status: in-progress
created: 2026-03-02
---

# AI 回覆加上正體中文翻譯

## 變更內容
在 AI 的英文回覆下方顯示正體中文翻譯，讓使用者可以參考理解。

## 實作方式
- 修改 system prompt，要求 Claude 在回覆時附帶中文翻譯
- 使用 `---TRANSLATION---` 分隔符號（類似現有的 `---GRAMMAR---` 機制）
- 前端拆分並以摺疊/展開方式顯示翻譯區塊
- Quick phrases 加上靜態中文翻譯

## 影響範圍
- `frontend/src/composables/useChat.ts` - 新增翻譯分隔邏輯
- `frontend/src/components/ChatMessage.vue` - 顯示翻譯區塊
- `frontend/src/config/scenarios.ts` - quick phrases 加中文
- `frontend/src/App.vue` - 翻譯開關 toggle
- `frontend/src/utils/chat-export.ts` - 匯出包含翻譯

## UI/UX 規格
- 翻譯區塊在 AI 回覆氣泡下方，可點擊展開/收合
- 背景色: 淺綠 (#f0fdf4)，邊框: 綠色 (#22c55e)
- 預設收合，點擊「顯示翻譯」展開
- 間距遵循 4px 倍數系統

## 測試計畫
1. 開啟翻譯模式，AI 回覆下方出現翻譯區塊
2. 點擊可展開/收合翻譯
3. Grammar mode + Translation mode 同時開啟時兩個區塊都正常顯示
4. 匯出 Markdown 包含翻譯內容
5. Quick phrases 顯示中文翻譯

## Checklist
- [ ] useChat.ts 加入翻譯解析邏輯
- [ ] ChatMessage.vue 加入翻譯顯示區塊
- [ ] App.vue 加入翻譯 toggle
- [ ] scenarios.ts quick phrases 加中文
- [ ] chat-export.ts 支援翻譯匯出
