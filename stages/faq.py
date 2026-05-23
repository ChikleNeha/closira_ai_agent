"""
stages/faq.py — Stage 1: SOP-grounded FAQ answering.

The AI answers customer questions strictly from the SOP.
Returns a structured response that includes:
- the answer text
- a confidence flag (HIGH / LOW)
- an escalation flag if the question is out of scope
"""

import json
import anthropic
from sop import get_sop

SYSTEM_PROMPT = """You are Bloom, a friendly and professional customer support assistant for Bloom Aesthetics Clinic in London.

Your ONLY source of information is the SOP data provided below. You must follow these rules without exception:

RULES:
1. Answer ONLY from the SOP data. If the answer is not in the SOP, do NOT guess or make up information.
2. If you cannot answer from the SOP, set "can_answer" to false and "escalate" to true.
3. Never mention specific staff names, medical advice, treatment guarantees, or contraindications.
4. Keep responses warm, concise, and professional — suitable for a WhatsApp or website chat.
5. Never apologise excessively. One brief acknowledgement is enough.
6. If a customer sounds angry, frustrated, or makes a complaint, set "escalate" to true with reason "sentiment".

RESPONSE FORMAT — always respond with valid JSON only, no extra text:
{
  "answer": "<your response to the customer>",
  "can_answer": true or false,
  "confidence": "HIGH" or "LOW",
  "escalate": true or false,
  "escalate_reason": "<reason if escalate is true, else null>",
  "sop_gap": "<describe what info was missing from SOP if can_answer is false, else null>"
}

SOP DATA:
---
{sop}
---"""


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.replace("{sop}", get_sop())


def answer_faq(user_message: str, conversation_history: list, client: anthropic.Anthropic) -> dict:
    """
    Send user message to Claude with SOP-grounded system prompt.
    Returns parsed structured response dict.
    """
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Cheapest Claude model — sufficient for structured FAQ
        max_tokens=512,
        system=build_system_prompt(),
        messages=messages,
    )

    raw = response.content[0].text.strip()

    try:
        # Strip markdown code fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: treat as plain answer, flag for review
        result = {
            "answer": raw,
            "can_answer": True,
            "confidence": "LOW",
            "escalate": False,
            "escalate_reason": None,
            "sop_gap": None,
        }

    return result
