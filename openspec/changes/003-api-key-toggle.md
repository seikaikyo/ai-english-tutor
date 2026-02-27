---
title: API Key 開關 + 自訂輸入
type: feature
status: in-progress
created: 2026-02-27
---

# API Key 開關 + 自訂輸入

## 變更內容

讓用戶可以在前端切換 API 模式（線上/離線）並輸入自己的 API key。

## 架構

```
前端 localStorage 儲存 key（不上傳伺服器）
  ↓
每次 API 請求帶 X-Api-Key header
  ↓
後端優先用 request key → 退回 env key → 無 key 走 fallback
```

## 影響範圍

### 前端 (2 檔案)
- `App.vue` - 新增設定區塊（開關 + key 輸入框）
- `composables/useChat.ts` - 請求帶 header

### 後端 (1 檔案)
- `main.py` - 從 header 讀 key，動態建 client

## 測試計畫
1. 無 key → 離線練習
2. 輸入 key → 切換為 AI 互動
3. 關閉 API 開關 → 強制離線
4. 錯誤的 key → 自動 fallback + 提示
