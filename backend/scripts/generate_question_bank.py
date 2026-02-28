#!/usr/bin/env python3
"""AI English Tutor 題庫生成器

用 Claude API 批次生成練習題和預建回應。

用法：
  python scripts/generate_question_bank.py              # 生成全部
  python scripts/generate_question_bank.py --mode drills       # 只生成練習題
  python scripts/generate_question_bank.py --mode responses    # 只生成預建回應
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

# 載入環境變數
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
DATA_DIR = Path(__file__).parent.parent / 'data' / 'question_bank'

DRILL_TYPES = [
    ('grammar_fill', 30, 'grammar fill-in-the-blank'),
    ('vocabulary', 30, 'vocabulary multiple choice'),
    ('situational', 30, 'situational response'),
    ('pronunciation', 30, 'pronunciation practice'),
]

SCENARIOS = [
    ('interview-prep', 20, 'generic job interview preparation'),
    ('free-chat', 20, 'casual free conversation'),
]


def generate_drills(drill_type: str, count: int, desc: str) -> list[dict]:
    """生成練習題"""
    if drill_type == 'grammar_fill':
        format_spec = '''[
  {
    "id": "grammar_fill_001",
    "sentence": "She _____ to the store if she had known it was closed.",
    "options": ["wouldn't have gone", "won't go", "didn't go", "hasn't gone"],
    "answer": "wouldn't have gone",
    "response": "Let's practice grammar! Fill in the blank:\\n\\nShe _____ to the store if she had known it was closed.\\n\\n1. wouldn't have gone\\n2. won't go\\n3. didn't go\\n4. hasn't gone\\n\\n(The correct answer is: wouldn't have gone - This is the third conditional, used for unreal past situations.)"
  }
]'''
    elif drill_type == 'vocabulary':
        format_spec = '''[
  {
    "id": "vocabulary_001",
    "prompt": "Choose the word that best completes the sentence: The scientist's findings were _____ by multiple independent studies.",
    "options": ["corroborated", "fabricated", "diminished", "extricated"],
    "answer": "corroborated",
    "response": "Vocabulary check!\\n\\nChoose the word that best completes the sentence: The scientist's findings were _____ by multiple independent studies.\\n\\n1. corroborated\\n2. fabricated\\n3. diminished\\n4. extricated\\n\\n(The correct answer is: corroborated - meaning to confirm or support with evidence.)"
  }
]'''
    elif drill_type == 'situational':
        format_spec = '''[
  {
    "id": "situational_001",
    "situation": "Your colleague just gave a presentation and asks for your feedback. You think it was good but the pacing was too fast.",
    "example_response": "Great job on the presentation! The content was really solid. One thing I'd suggest is slowing down a bit - some of the key points went by quickly, and I think the audience would benefit from having a moment to absorb them.",
    "response": "Situational response practice:\\n\\nSituation: Your colleague just gave a presentation and asks for your feedback. You think it was good but the pacing was too fast.\\n\\nHow would you respond?\\n\\nExample answer: Great job on the presentation! The content was really solid. One thing I'd suggest is slowing down a bit - some of the key points went by quickly, and I think the audience would benefit from having a moment to absorb them."
  }
]'''
    elif drill_type == 'pronunciation':
        format_spec = '''[
  {
    "id": "pronunciation_001",
    "word": "thoroughly /THUR-oh-lee/",
    "tip": "The 'th' is voiced (like 'the'), not voiceless (like 'think'). The 'ough' sounds like 'uh'. Stress is on the first syllable.",
    "response": "Pronunciation practice:\\n\\nWord: thoroughly /THUR-oh-lee/\\n\\nTip: The 'th' is voiced (like 'the'), not voiceless (like 'think'). The 'ough' sounds like 'uh'. Stress is on the first syllable."
  }
]'''
    else:
        return []

    prompt = f"""Generate {count} {desc} exercises for an English learner.
Level: intermediate to advanced (B2-C1).
Topics: professional communication, daily life, academic, technology.

Format as JSON array (no markdown code block):

{format_spec}

Generate exactly {count} items. IDs should be {drill_type}_001 through {drill_type}_{count:03d}.
Each "response" field should be a complete, self-contained reply text that includes the exercise AND the answer.
Vary difficulty and topics across the {count} items."""

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4096 * 3,
        system='You are an English language exercise generator. Output only valid JSON, no other text.',
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

    try:
        questions = json.loads(text)
        print(f'  {drill_type}: {len(questions)} 題')
        return questions
    except json.JSONDecodeError:
        try:
            start = text.index('[')
            end = text.rindex(']') + 1
            questions = json.loads(text[start:end])
            print(f'  {drill_type}: 修復後取得 {len(questions)} 題')
            return questions
        except (ValueError, json.JSONDecodeError):
            print(f'  {drill_type}: JSON 解析失敗，跳過')
            return []


def generate_fallback_responses(scenario: str, count: int, desc: str) -> list[dict]:
    """生成預建回應"""
    prompt = f"""Generate {count} Q&A pairs for an English tutoring chatbot in the following scenario:
{desc}

Each pair should have:
1. A list of keywords that would trigger this response
2. The chatbot's response (2-3 sentences, friendly and natural)

Format as JSON array (no markdown code block):

[
  {{
    "id": "{scenario}_001",
    "keywords": ["tell me about", "what is", "describe"],
    "user_example": "Can you tell me about the role?",
    "response": "This role involves working closely with the team to tackle key challenges in our domain. You'd be collaborating across functions and contributing to impactful projects. It's a great fit for someone who enjoys problem-solving and continuous learning!"
  }}
]

Generate exactly {count} items covering common questions and conversation starters for this scenario.
Keywords should be lowercase phrases that commonly appear in user messages.
Responses should sound natural, friendly, and conversational (2-3 sentences)."""

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4096 * 2,
        system='You are an English tutoring response generator. Output only valid JSON, no other text.',
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

    try:
        responses = json.loads(text)
        print(f'  {scenario}: {len(responses)} 組')
        return responses
    except json.JSONDecodeError:
        try:
            start = text.index('[')
            end = text.rindex(']') + 1
            responses = json.loads(text[start:end])
            print(f'  {scenario}: 修復後取得 {len(responses)} 組')
            return responses
        except (ValueError, json.JSONDecodeError):
            print(f'  {scenario}: JSON 解析失敗，跳過')
            return []


def run_drills():
    """生成所有練習題"""
    drills_dir = DATA_DIR / 'drills'
    drills_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for drill_type, count, desc in DRILL_TYPES:
        out_file = drills_dir / f'{drill_type}.json'

        if out_file.exists():
            existing = json.loads(out_file.read_text(encoding='utf-8'))
            c = len(existing) if isinstance(existing, list) else 0
            print(f'  {drill_type}: 已存在 ({c} 題)，跳過')
            total += c
            continue

        print(f'  生成 {desc} ({drill_type})...')
        questions = generate_drills(drill_type, count, desc)
        if questions:
            out_file.write_text(
                json.dumps(questions, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            total += len(questions)

        time.sleep(1)

    print(f'練習題完成: {total} 題')
    return total


def run_responses():
    """生成預建回應"""
    resp_dir = DATA_DIR / 'fallback_responses'
    resp_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for scenario, count, desc in SCENARIOS:
        out_file = resp_dir / f'{scenario}.json'

        if out_file.exists():
            existing = json.loads(out_file.read_text(encoding='utf-8'))
            c = len(existing) if isinstance(existing, list) else 0
            print(f'  {scenario}: 已存在 ({c} 組)，跳過')
            total += c
            continue

        print(f'  生成 {desc} ({scenario})...')
        responses = generate_fallback_responses(scenario, count, desc)
        if responses:
            out_file.write_text(
                json.dumps(responses, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            total += len(responses)

        time.sleep(1)

    print(f'預建回應完成: {total} 組')
    return total


def save_metadata(stats: dict):
    """儲存統計資訊"""
    from datetime import datetime
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'model': 'claude-sonnet-4-20250514',
        'stats': stats,
    }
    meta_file = DATA_DIR / 'metadata.json'
    meta_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'metadata 已寫入: {meta_file}')


def main():
    parser = argparse.ArgumentParser(description='AI English Tutor 題庫生成器')
    parser.add_argument(
        '--mode',
        choices=['drills', 'responses', 'all'],
        default='all',
        help='生成模式 (預設: all)',
    )
    args = parser.parse_args()

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('錯誤: 未設定 ANTHROPIC_API_KEY')
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stats = {}

    print('=== AI English Tutor 題庫生成器 ===\n')

    if args.mode in ('drills', 'all'):
        print('[練習題] 生成練習題...')
        stats['drills'] = run_drills()
        print()

    if args.mode in ('responses', 'all'):
        print('[預建回應] 生成預建回應...')
        stats['responses'] = run_responses()
        print()

    save_metadata(stats)
    print('\n完成!')


if __name__ == '__main__':
    main()
