"""題庫 + Fallback 服務

離線時轉為「結構化練習模式」：
- 文法填空
- 詞彙選擇 (4 選 1)
- 情境回應
- 發音練習

以及預建回應（keyword 匹配）。
"""

import json
import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / 'data' / 'question_bank'


class QuestionBankService:
    """英語題庫與 fallback 回應服務"""

    # TOEIC drill types 對應的 scenario ID
    TOEIC_SCENARIO_MAP = {
        'toeic-part5': 'toeic_part5',
        'toeic-part6': 'toeic_part6',
        'toeic-part7': 'toeic_part7',
        'toeic-mixed': None,  # 從所有 toeic_ drills 隨機選
    }

    def __init__(self):
        self._drills: dict[str, list[dict]] = {
            'grammar_fill': [],
            'vocabulary': [],
            'situational': [],
            'pronunciation': [],
            'toeic_part5': [],
            'toeic_part6': [],
            'toeic_part7': [],
        }
        self._fallback_responses: dict[str, list[dict]] = {}
        self._used_drill_ids: set[str] = set()
        self._loaded = False

    def load(self):
        """載入所有題庫和預建回應"""
        # 載入練習題
        drills_dir = DATA_DIR / 'drills'
        if drills_dir.exists():
            for drill_type in self._drills:
                f = drills_dir / f'{drill_type}.json'
                if f.exists():
                    try:
                        data = json.loads(f.read_text(encoding='utf-8'))
                        if isinstance(data, list):
                            self._drills[drill_type] = data
                        elif isinstance(data, dict) and 'questions' in data:
                            self._drills[drill_type] = data['questions']
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error('載入 %s 失敗: %s', f.name, e)

        # 載入預建回應
        responses_dir = DATA_DIR / 'fallback_responses'
        if responses_dir.exists():
            for f in responses_dir.glob('*.json'):
                try:
                    data = json.loads(f.read_text(encoding='utf-8'))
                    scenario_name = f.stem  # 例如 mercor-interview, free-chat
                    if isinstance(data, list):
                        self._fallback_responses[scenario_name] = data
                    elif isinstance(data, dict) and 'responses' in data:
                        self._fallback_responses[scenario_name] = data['responses']
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error('載入 fallback 回應失敗 %s: %s', f.name, e)

        self._loaded = True
        drill_total = sum(len(d) for d in self._drills.values())
        resp_total = sum(len(r) for r in self._fallback_responses.values())
        logger.info(
            '題庫載入完成: drills=%d, fallback_responses=%d',
            drill_total, resp_total,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def detect_scenario(self, system_prompt: str) -> str | None:
        """從 system_prompt 偵測場景"""
        prompt_lower = system_prompt.lower()
        if 'mercor' in prompt_lower or 'santiago' in prompt_lower:
            return 'mercor-interview'
        if 'free chat' in prompt_lower or 'conversation partner' in prompt_lower:
            return 'free-chat'
        # TOEIC 場景偵測
        if 'toeic' in prompt_lower:
            if 'part 5' in prompt_lower or 'incomplete sentences' in prompt_lower:
                return 'toeic-part5'
            if 'part 6' in prompt_lower or 'text completion' in prompt_lower:
                return 'toeic-part6'
            if 'part 7' in prompt_lower or 'reading comprehension' in prompt_lower:
                return 'toeic-part7'
            return 'toeic-mixed'
        return None

    def find_fallback_response(self, scenario: str, user_message: str) -> str | None:
        """用 keyword 匹配預建回應"""
        responses = self._fallback_responses.get(scenario, [])
        if not responses:
            return None

        msg_lower = user_message.lower().strip()

        # 嘗試 keyword 匹配
        for entry in responses:
            keywords = entry.get('keywords', [])
            if any(kw.lower() in msg_lower for kw in keywords):
                return entry.get('response', '')

        # 匹配不到就回 None
        return None

    def get_random_drill(self) -> str:
        """隨機取得一題練習題，格式化為回覆文字"""
        available_types = [t for t, qs in self._drills.items() if qs]
        if not available_types:
            return (
                "I'm currently in offline mode and don't have practice exercises available. "
                "Please try again later when the AI service is back online."
            )

        drill_type = random.choice(available_types)
        questions = self._drills[drill_type]

        # 過濾已出過的
        unused = [q for q in questions if q.get('id') not in self._used_drill_ids]
        if not unused:
            self._used_drill_ids = set()
            unused = questions.copy()

        question = random.choice(unused)
        if question.get('id'):
            self._used_drill_ids.add(question['id'])

        return question.get('response', self._format_drill(question, drill_type))

    def _format_drill(self, question: dict, drill_type: str) -> str:
        """格式化練習題為回覆文字"""
        if drill_type == 'grammar_fill':
            sentence = question.get('sentence', '')
            options = question.get('options', [])
            answer = question.get('answer', '')
            opts_text = '\n'.join(f'{i+1}. {o}' for i, o in enumerate(options))
            return (
                f"Let's practice grammar! Fill in the blank:\n\n"
                f"{sentence}\n\n{opts_text}\n\n"
                f"(The correct answer is: {answer})"
            )
        elif drill_type == 'vocabulary':
            prompt_text = question.get('prompt', '')
            options = question.get('options', [])
            answer = question.get('answer', '')
            opts_text = '\n'.join(f'{i+1}. {o}' for i, o in enumerate(options))
            return (
                f"Vocabulary check!\n\n{prompt_text}\n\n{opts_text}\n\n"
                f"(The correct answer is: {answer})"
            )
        elif drill_type == 'situational':
            situation = question.get('situation', '')
            example = question.get('example_response', '')
            return (
                f"Situational response practice:\n\n"
                f"Situation: {situation}\n\n"
                f"How would you respond?\n\n"
                f"Example answer: {example}"
            )
        elif drill_type == 'pronunciation':
            word = question.get('word', '')
            tip = question.get('tip', '')
            return (
                f"Pronunciation practice:\n\n"
                f"Word: {word}\n\n"
                f"Tip: {tip}"
            )
        return question.get('response', 'Practice question not available.')

    def get_toeic_drill(self, scenario: str) -> str:
        """取得 TOEIC 題目"""
        drill_type = self.TOEIC_SCENARIO_MAP.get(scenario)

        if drill_type is None:
            # toeic-mixed: 從所有 toeic_ drills 隨機選
            toeic_types = [t for t in self._drills if t.startswith('toeic_') and self._drills[t]]
            if not toeic_types:
                return "No TOEIC questions available. Please try again later."
            drill_type = random.choice(toeic_types)

        questions = self._drills.get(drill_type, [])
        if not questions:
            return f"No {drill_type} questions available. Please try again later."

        unused = [q for q in questions if q.get('id') not in self._used_drill_ids]
        if not unused:
            # 該類型用完就重置
            for q in questions:
                self._used_drill_ids.discard(q.get('id', ''))
            unused = questions.copy()

        question = random.choice(unused)
        if question.get('id'):
            self._used_drill_ids.add(question['id'])

        return question.get('response', 'Question not available.')

    def get_fallback_reply(self, system_prompt: str, user_message: str) -> str:
        """取得 fallback 回覆（主要入口）

        1. 偵測場景
        2. TOEIC 場景 → 直接出 TOEIC 題
        3. 其他場景 → keyword 匹配預建回應
        4. 都沒匹配 → 出一般練習題
        """
        scenario = self.detect_scenario(system_prompt)

        # TOEIC 場景直接出題
        if scenario and scenario.startswith('toeic'):
            return self.get_toeic_drill(scenario)

        if scenario:
            matched = self.find_fallback_response(scenario, user_message)
            if matched:
                return matched

        return self.get_random_drill()

    def get_status(self) -> dict:
        """回傳題庫狀態"""
        return {
            'loaded': self._loaded,
            'drills': {
                dtype: len(questions)
                for dtype, questions in self._drills.items()
            },
            'fallback_responses': {
                scenario: len(responses)
                for scenario, responses in self._fallback_responses.items()
            },
            'total_drills': sum(len(d) for d in self._drills.values()),
            'total_responses': sum(len(r) for r in self._fallback_responses.values()),
        }


# 全域單例
question_bank = QuestionBankService()
