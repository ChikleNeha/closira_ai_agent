"""
stages/escalation.py — Stage 3: Escalation detection.

Defines all escalation triggers and the escalation handler.
Escalation can be triggered by:
  1. FAQ stage returning escalate=True (out-of-scope or low confidence)
  2. Sentiment detection (anger, complaint, frustration)
  3. Explicit customer request ("speak to a human", "manager", etc.)
  4. Unanswered question count exceeding threshold (>2)
  5. Pricing negotiation attempt

This module also handles the escalation response to the customer
and logs the event with a structured reason.
"""

import anthropic
from logger import log_escalation

# Keywords that trigger immediate escalation regardless of stage
EXPLICIT_ESCALATION_KEYWORDS = [
    "speak to a human", "talk to a person", "real person",
    "manager", "supervisor", "speak to someone",
    "human agent", "escalate", "i want to complain",
    "this is unacceptable", "legal action", "sue",
]

SENTIMENT_KEYWORDS = [
    "angry", "furious", "disgusted", "terrible", "awful",
    "worst", "horrible", "hate", "useless", "incompetent",
    "waste of time", "scam", "fraud", "ridiculous",
]

PRICING_NEGOTIATION_KEYWORDS = [
    "discount", "cheaper", "negotiate", "lower the price",
    "can you do better", "too expensive", "best price",
    "match the price", "price match",
]

ESCALATION_MESSAGES = {
    "out_of_scope": (
        "That's a great question, but it falls outside what I'm able to help with directly. "
        "I'm connecting you with one of our team members who will have the answer. "
        "You'll hear from us shortly — thank you for your patience! 🌸"
    ),
    "sentiment": (
        "I'm really sorry to hear you're feeling this way — that's not the experience we want for you at all. "
        "I'm escalating this to a senior team member right now so we can make this right. "
        "Someone will be in touch with you very shortly. 🌸"
    ),
    "explicit_request": (
        "Of course! I'm connecting you with one of our team members right away. "
        "Please hold on — someone will be with you shortly. 🌸"
    ),
    "pricing_negotiation": (
        "I understand you'd like to discuss pricing — that's something our team handles directly. "
        "I'm passing you over to them now so they can help you further. 🌸"
    ),
    "unanswered_limit": (
        "I've reached the limit of what I can help with on this topic. "
        "I'm bringing in one of our team members who will be better placed to assist you. 🌸"
    ),
    "medical": (
        "Medical questions are really important to us, and I want to make sure you get accurate advice. "
        "I'm connecting you with our clinical team right away. 🌸"
    ),
}


def check_explicit_escalation(message: str) -> tuple[bool, str]:
    """Check if message contains explicit escalation or sentiment triggers."""
    lower = message.lower()

    for kw in EXPLICIT_ESCALATION_KEYWORDS:
        if kw in lower:
            return True, "explicit_request"

    for kw in SENTIMENT_KEYWORDS:
        if kw in lower:
            return True, "sentiment"

    for kw in PRICING_NEGOTIATION_KEYWORDS:
        if kw in lower:
            return True, "pricing_negotiation"

    return False, ""


def handle_escalation(
    reason: str,
    trigger: str,
    conversation_history: list,
    unanswered_count: int = 0,
) -> str:
    """
    Log escalation event and return the appropriate message to show the customer.
    """
    log_escalation(
        reason=reason,
        trigger=trigger,
        conversation_snapshot=conversation_history,
    )

    return ESCALATION_MESSAGES.get(reason, ESCALATION_MESSAGES["out_of_scope"])


def check_medical_question(message: str) -> bool:
    """Detect medical questions that must always be escalated."""
    medical_keywords = [
        "allerg", "pregnant", "pregnancy", "medication", "side effect",
        "reaction", "contraindic", "safe for", "health condition",
        "medical", "doctor", "nerve", "bruising", "swelling", "pain",
    ]
    lower = message.lower()
    return any(kw in lower for kw in medical_keywords)
