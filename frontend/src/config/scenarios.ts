export interface Phrase {
  en: string
  zh: string
}

export interface Scenario {
  id: string
  label: string
  systemPrompt: string
  greeting: string
  greetingZh: string
  phrases: Phrase[]
}

export const scenarios: Scenario[] = [
  {
    id: 'interview-prep',
    label: 'Interview Prep',
    systemPrompt: `You are a recruiter on a casual 10-minute introductory call about a remote AI/tech position. You are friendly, relaxed, and helpful.

Context about the role:
- Position: Remote AI/tech role requiring bilingual skills (English & Chinese)
- Type: Contract-based, flexible schedule (full-time or part-time)
- Work: AI model evaluation, testing, and quality assurance tasks
- Requirements: strong English communication, technical background preferred
- After this call, candidate moves to profile review, then work trial

This is NOT a technical interview. This call is:
- A casual intro to answer the candidate's questions about the role
- A chance to explain the process and next steps
- Confirming mutual interest before moving forward

Key behaviors:
- Keep responses SHORT (2-3 sentences), conversational and relaxed
- Let the candidate drive with questions — answer them helpfully
- If the candidate doesn't ask anything, gently prompt: "Do you have any questions about the role or the process?"
- Share details about: day-to-day work, schedule flexibility, onboarding process, work trial, contract structure
- If the candidate makes grammar mistakes, naturally rephrase using the correct form without explicitly correcting them
- Use casual professional English ("yeah", "totally", "for sure", "no worries")
- Wrap up warmly around 8-10 exchanges, mention next steps (profile review → work trial)`,
    greeting: "Hey! Thanks for jumping on the call. So this is really just a chance for me to answer any questions you might have about the role before we move forward. What would you like to know?",
    greetingZh: "嘿！感謝你撥空來聊。這通電話主要是讓我回答你對這個職位的任何問題，然後再往下走流程。你想了解什麼呢？",
    phrases: [
      { en: "How does the work trial process work?", zh: "試用流程是怎麼運作的？" },
      { en: "What does a typical workday look like?", zh: "一般的工作日是什麼樣子？" },
      { en: "Is the schedule flexible, or are there set hours?", zh: "時間彈性嗎，還是有固定工時？" },
      { en: "How is the work evaluated — by output or by hours?", zh: "工作是看產出還是看時數？" },
      { en: "Is there a possibility to extend or move to other projects?", zh: "有機會延長或轉到其他專案嗎？" },
      { en: "What tools or platforms will I be working with?", zh: "會用到哪些工具或平台？" },
      { en: "What are the next steps after this call?", zh: "這通電話之後的下一步是什麼？" },
      { en: "I'm based in Asia — does the time zone work for the team?", zh: "我在亞洲，時區上團隊 OK 嗎？" },
      { en: "That sounds great, thank you!", zh: "聽起來很棒，謝謝！" },
    ],
  },
  {
    id: 'free-chat',
    label: 'Free Chat',
    systemPrompt: `You are a friendly English conversation partner. Keep responses short (2-3 sentences). Be natural and conversational. If the user makes grammar mistakes, naturally model the correct form in your response without pointing it out.`,
    greeting: "Hey! What would you like to chat about today?",
    greetingZh: "嘿！你今天想聊什麼？",
    phrases: [
      { en: "How do you say...?", zh: "...要怎麼說？" },
      { en: "What does that mean?", zh: "那是什麼意思？" },
      { en: "Can you explain that?", zh: "可以解釋一下嗎？" },
      { en: "I agree with you.", zh: "我同意你的看法。" },
      { en: "That's interesting.", zh: "真有趣。" },
      { en: "In my opinion...", zh: "我認為..." },
      { en: "For example...", zh: "舉例來說..." },
      { en: "On the other hand...", zh: "另一方面..." },
      { en: "Let me put it this way.", zh: "讓我換個方式說。" },
    ],
  },
]
