"""
stages/qualification.py — Stage 2: Lead qualification.

Asks the customer 3 structured questions to qualify them as a lead.
Stores answers and produces a qualification summary.

Questions asked:
  Q1. What treatment are you interested in?
  Q2. Have you had this treatment before?
  Q3. When are you looking to book? (urgency signal)
"""

import json
import anthropic

QUALIFICATION_QUESTIONS = [
    "Which of our treatments are you most interested in — Botox, Fillers, or a free consultation first?",
    "Have you had this type of treatment before, or would this be your first time?",
    "When are you looking to book — are you flexible, or do you have a specific timeframe in mind?",
]

SUMMARY_SYSTEM_PROMPT = """You are a lead qualification assistant for Bloom Aesthetics Clinic.

Given the answers to 3 qualification questions, produce a structured lead summary in JSON.

RESPONSE FORMAT — valid JSON only, no extra text:
{
  "treatment_interest": "<treatment they mentioned>",
  "experience_level": "first_time" or "returning",
  "booking_urgency": "urgent" or "flexible" or "unknown",
  "lead_quality": "hot" or "warm" or "cold",
  "recommended_action": "<one sentence: what the clinic should do next>"
}

Lead quality guide:
- hot: specific treatment + wants to book soon
- warm: specific treatment but flexible timeline
- cold: vague interest or no clear treatment preference"""


def get_qualification_questions() -> list:
    return QUALIFICATION_QUESTIONS


def build_qualification_summary(answers: dict, client: anthropic.Anthropic) -> dict:
    """
    Given {question: answer} pairs, ask Claude to produce a structured lead summary.
    """
    answers_text = "\n".join(
        f"Q: {q}\nA: {a}" for q, a in answers.items()
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=SUMMARY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here are the qualification answers:\n\n{answers_text}\n\nProduce the lead summary."
            }
        ],
    )

    raw = response.content[0].text.strip()
    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "treatment_interest": "unknown",
            "experience_level": "unknown",
            "booking_urgency": "unknown",
            "lead_quality": "cold",
            "recommended_action": raw,
        }
