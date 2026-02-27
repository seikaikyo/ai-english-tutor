---
title: AI English Tutor MVP
type: feature
status: in-progress
created: 2026-02-26
---

# AI English Tutor MVP

## 背景
用戶即將參加 Mercor AI Red Teamer 的線上面試（英文），需要一個對話練習工具來降低緊張感。

## 變更內容
建立一個 AI 英文對話練習系統，支援語音輸入/輸出，可模擬面試情境。

### 核心功能
1. **語音輸入**: 使用 Web Speech API (STT) 將用戶語音轉文字
2. **AI 對話**: 使用 Claude API 產生自然的英文對話回應
3. **語音輸出**: 使用 Web Speech Synthesis (TTS) 朗讀 AI 回應
4. **情境模式**: 預設「Mercor 面試」情境，模擬 Zelinda 的角色
5. **對話紀錄**: 顯示完整對話歷史，方便複習

### 技術選型
| 元件 | 技術 |
|------|------|
| 前端 | Vite + Vue 3 + TypeScript |
| UI | PrimeVue (Aura theme) |
| 語音輸入 | Web Speech API (SpeechRecognition) |
| 語音輸出 | Web Speech Synthesis API |
| AI 對話 | Claude API (Anthropic SDK) |
| 部署 | Vercel |

### MVP 畫面
- 單頁應用，中間是對話紀錄區
- 底部是錄音按鈕（按住說話 or 點擊切換）
- 頂部是情境選擇（面試/日常對話/自由聊天）
- 每則 AI 回應旁有播放按鈕

## 影響範圍
- 全新專案，不影響其他專案
- `frontend/` - Vue 3 前端
- `backend/` - API 代理（保護 API Key）

## UI/UX 規格
- 色彩: PrimeVue Aura 預設主題
- 間距: 4px 基數
- 響應式: 以 mobile 為主（手機練習）
- 互動: 錄音按鈕需明顯的狀態回饋（錄音中/處理中/播放中）

## 測試計畫
1. Web Speech API 在 Chrome/Safari 上正常運作
2. Claude API 回應正確且自然
3. TTS 朗讀流暢
4. 對話紀錄正確顯示
5. Mobile 版面正常

## Checklist
- [ ] 前端 Vite + Vue 3 + PrimeVue 專案初始化
- [ ] Web Speech API 語音輸入元件
- [ ] Claude API 對話串接
- [ ] Web Speech Synthesis 語音輸出
- [ ] 面試情境 prompt 設計
- [ ] 對話紀錄 UI
- [ ] Vercel 部署
