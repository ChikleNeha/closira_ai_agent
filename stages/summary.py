"""
stages/summary.py — Stage 4: Conversation summary generator.

At session end, produces a structured summary covering:
  - Customer intent
  - Key details collected
  - SOP gaps identified during the conversation
  - Recommended next action for the human team
"""

import json
import anthropic

SUMMARY_SYSTEM_PROMPT = """You are a conversation analyst for Bloom Aesthetics Clinic.

Given a full conversation transcript and any qualification data collected, produce a structured session summary for the clinic team.

RESPONSE FORMAT — valid JSON only, no extra text:
{
  "customer_intent": "<one sentence describing what the customer wanted>",
  "key_details_collected": [
    "<detail 1>",
    "<detail 2>"
  ],
  "sop_gaps_identified": [
    "<any question the AI could not answer from the SOP — or 'None' if all questions were covered>"
  ],
  "escalated": true or false,
  "escalation_reason": "<reason if escalated, else null>",
  "lead_quality": "hot" or "warm" or "cold" or "not_assessed",
  "recommended_next_action": "<clear, specific action for the human team to take>"
}"""


def generate_summary(
    conversation_history: list,
    qualification_data: dict,
    escalation_log: list,
    client: anthropic.Anthropic,
) -> dict:
    """
    Generate a structured end-of-session summary.
    conversation_history: list of {role, content} dicts
    qualification_data: dict from Stage 2, or empty {}
    escalation_log: list of escalation event dicts
    """

    # Format transcript for the prompt
    transcript = "\n".join(
        f"{'Customer' if m['role'] == 'user' else 'Bloom AI'}: {m['content']}"
        for m in conversation_history
    )

    context = f"""CONVERSATION TRANSCRIPT:
{transcript}

QUALIFICATION DATA COLLECTED:
{json.dumps(qualification_data, indent=2) if qualification_data else "Not collected"}

ESCALATION EVENTS:
{json.dumps(escalation_log, indent=2) if escalation_log else "None"}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SUMMARY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{context}\n\nGenerate the session summary."
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
            "customer_intent": "Could not parse",
            "key_details_collected": [],
            "sop_gaps_identified": [],
            "escalated": bool(escalation_log),
            "escalation_reason": None,
            "lead_quality": "not_assessed",
            "recommended_next_action": raw,
        }
