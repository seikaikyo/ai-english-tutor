---
title: TOEIC 多益練習模式
type: feature
status: in-progress
created: 2026-02-27
---

# TOEIC 多益練習模式

## 變更內容

在 ai-english-tutor 加入 TOEIC 多益練習場景。利用現有 scenario 架構，新增 TOEIC 題型練習。

## 設計決策

### TOEIC 題型對應

只做閱讀部分（Part 5-7），聽力部分用文字模擬：

| TOEIC Part | 題型 | App 中的實作 |
|-----------|------|------------|
| Part 5 | Incomplete Sentences | 文法/詞彙填空（4 選 1） |
| Part 6 | Text Completion | 段落填空（4 選 1） |
| Part 7 | Reading Comprehension | 閱讀理解（單篇/雙篇） |
| Part 1-4 | Listening | 文字呈現對話 + TTS 朗讀 |

### Scenario 架構（零後端改動）

ai-english-tutor 是 scenario-driven 架構。加 TOEIC 只需：
1. `scenarios.ts` 新增場景物件
2. 題庫加 TOEIC fallback 內容

前端 Select 自動出現新選項，不需改 UI 元件。

## 影響範圍

### 前端 (1 檔案修改)

| 檔案 | 修改內容 |
|------|---------|
| `frontend/src/config/scenarios.ts` | 新增 4 個 TOEIC scenario |

### 後端 (0 檔案修改)

現有架構已支援任意 scenario。Fallback 題庫自動載入。

### 題庫 (新增)

```
backend/data/question_bank/
├── drills/
│   ├── toeic_part5.json      # 30 題 Incomplete Sentences
│   ├── toeic_part6.json      # 15 題 Text Completion
│   └── toeic_part7.json      # 15 題 Reading Comprehension
└── fallback_responses/
    ├── toeic-part5.json      # Part 5 預建回應
    ├── toeic-part6.json      # Part 6 預建回應
    └── toeic-part7.json      # Part 7 預建回應
```

### Scenario 設計

```typescript
// 4 個 TOEIC 場景
{
  id: 'toeic-part5',
  label: 'TOEIC Part 5 - Incomplete Sentences',
  systemPrompt: `You are a TOEIC instructor...`,
  greeting: 'Welcome to TOEIC Part 5 practice!...',
  phrases: ['Next question', 'Explain the answer', ...]
}
// toeic-part6, toeic-part7, toeic-mixed
```

## 實作順序

1. 在 `scenarios.ts` 新增 4 個 TOEIC scenario
2. 生成 TOEIC 題庫 JSON（Part 5/6/7）
3. 修改 `question_bank_service.py` 識別 toeic scenario
4. 測試有 API / 無 API 兩種模式

## 測試計畫

1. 選 TOEIC Part 5 → 確認出 Incomplete Sentences 題
2. 選 TOEIC Part 7 → 確認出 Reading Comprehension 題
3. Grammar mode ON → 確認文法回饋正常
4. 無 API → 確認 fallback 出題正常
5. 切換 scenario → 確認對話清空、greeting 正確

## Checklist

- [ ] scenarios.ts 新增 TOEIC scenarios
- [ ] TOEIC Part 5 題庫 (30 題)
- [ ] TOEIC Part 6 題庫 (15 題)
- [ ] TOEIC Part 7 題庫 (15 題)
- [ ] question_bank_service 識別 toeic
- [ ] Fallback 回應
- [ ] 測試全部 TOEIC 場景
