# Prompt Design Document — Closira AI Agent

## Overview

This document explains every prompt design decision made in this project: what was chosen, why, and what alternatives were considered. The goal is to demonstrate that the AI behaviour is intentional and reasoned, not accidental.

---

## 1. System Prompt (Stage 1 — FAQ Answering)

```
You are Bloom, a friendly and professional customer support assistant for Bloom Aesthetics Clinic in London.

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
[SOP injected here at runtime]
---
```

### Design Decisions

**Why JSON output format?**

Forcing structured JSON output turns the LLM into a deterministic component in a pipeline rather than a freeform chatbot. This means:
- Escalation decisions are machine-readable and loggable, not buried in prose
- `can_answer` and `confidence` fields decouple *what the AI says* from *what the system does next*
- The workflow layer can act on `escalate: true` without parsing natural language

Alternatives considered: asking the model to return `[ESCALATE]` as a prefix, or using a confidence score (0–1). JSON was chosen because it is more extensible and easier to parse reliably.

**Why "ONLY source of information" phrasing?**

Weak phrasing like "try to use the SOP" leaves the model room to fill gaps with training data. "ONLY" and "do NOT guess" are explicit prohibitions. The word "ONLY" appears in caps to increase instruction salience — research on LLM instruction following shows that emphasis and placement affect compliance.

**Why is the SOP injected at runtime rather than hardcoded in the prompt?**

This makes the system SOP-agnostic. Any business could replace `sop.py` with their own data and the AI behaviour would update automatically. It also makes the SOP visible and auditable in one place.

---

## 2. Hallucination Prevention

Three layers are used:

### Layer 1 — Explicit instruction in the system prompt
```
Answer ONLY from the SOP data. If the answer is not in the SOP, do NOT guess or make up information.
```
This is the primary guardrail. The model is told what to do when it doesn't know — return `can_answer: false` — rather than being left to decide on its own.

### Layer 2 — Structured output with `can_answer` field
The `can_answer: false` path forces the model to admit a knowledge gap rather than generate a plausible-sounding but fabricated answer. This is preferable to a confidence score because it is binary and unambiguous — there is no threshold to tune.

### Layer 3 — Unanswered question counter in the workflow
Even if the model incorrectly sets `can_answer: true` for an out-of-scope question, the workflow tracks how many consecutive unanswered or low-confidence responses have occurred. After 2, it escalates regardless of what the model says (`UNANSWERED_THRESHOLD = 2` in `workflow.py`). This is a non-AI safety net that does not rely on the model's self-assessment.

### Why not use a retrieval system (RAG)?
For a 5-field SOP that fits comfortably in a single prompt, RAG adds complexity without benefit. The entire SOP is injected into the context window. RAG would be appropriate if the SOP were hundreds of pages long.

---

## 3. Confidence-Based Escalation

Escalation is triggered by a layered decision tree, not a single mechanism:

| Trigger | Where detected | How |
|---|---|---|
| Out-of-scope question | Stage 1 (FAQ) | Model sets `escalate: true`, `can_answer: false` |
| Low confidence | Stage 1 (FAQ) | Model sets `confidence: "LOW"` |
| Angry sentiment | Stage 1 (FAQ) | Model sets `escalate: true`, `escalate_reason: "sentiment"` |
| Explicit escalation request | `escalation.py` (pre-model) | Keyword matching before API call |
| Medical question | `escalation.py` (pre-model) | Keyword matching before API call |
| Pricing negotiation | `escalation.py` (pre-model) | Keyword matching before API call |
| Unanswered question threshold | `workflow.py` | Counter ≥ 2 triggers escalation |

**Why keyword matching for some triggers instead of relying on the model?**

Keywords are deterministic — they never miss a trigger due to model variability. For high-stakes triggers like medical questions or explicit escalation requests, deterministic matching is safer than LLM judgement. The model handles nuanced cases (sentiment, ambiguous out-of-scope questions); keywords handle clear-cut cases.

**Why log escalation reason?**

The human agent receiving the escalation needs context immediately. A structured log with `reason`, `trigger_message`, and `stage_at_escalation` means the agent does not have to re-read the full conversation to understand why the handoff occurred.

---

## 4. Tone and Persona

**Persona name:** Bloom — matches the clinic brand (Bloom Aesthetics), making the AI feel native to the business rather than generic.

**Tone guidelines in the prompt:**
- "warm, concise, and professional"
- "suitable for a WhatsApp or website chat" — this anchors the response length and register. WhatsApp messages are short; the model should not write paragraphs.
- "Never apologise excessively" — over-apologising erodes customer confidence. One acknowledgement is enough.

**Emoji use:** A single 🌸 in escalation messages adds warmth without being unprofessional. It is consistent with how aesthetic clinics communicate on social media and WhatsApp.

**Why not a more formal tone?**

Bloom Aesthetics serves SMB clients who interact via WhatsApp. Formal, corporate language would feel out of place. The persona is calibrated to match the channel and the industry — beauty, aesthetics, wellness — where warmth and approachability are expected.

---

## 5. Lead Qualification Design

Three questions were chosen rather than the maximum allowed (2–3) to collect the minimum viable data for a lead record:

| Question | What it reveals |
|---|---|
| Treatment interest | Which service to prepare for; informs booking type |
| Prior experience | First-time vs returning; informs consultation need |
| Timeline | Booking urgency; informs follow-up priority |

The qualification summary uses a separate Claude call with a focused system prompt that maps answers to `lead_quality: hot / warm / cold`. This separation keeps Stage 2 clean — the qualification *asking* logic is stateless, and the *summarisation* is a one-shot classification task.

---

## 6. Conversation Summary Design

The summary prompt instructs the model to produce five fields:
- `customer_intent` — a single sentence synthesising what the customer wanted
- `key_details_collected` — a list of concrete facts gathered
- `sop_gaps_identified` — what the AI could not answer (directly actionable for the SOP owner)
- `escalated` + `escalation_reason` — for audit and handoff quality tracking
- `recommended_next_action` — one specific, actionable instruction for the human team

**Why include `sop_gaps_identified`?**

This is the most operationally valuable output for a real business. Every gap is a signal that the SOP needs to be updated. Over time, reviewing session summaries tells the clinic owner exactly what customers ask that the AI cannot answer — allowing continuous SOP improvement.

---

## 7. Model Choice

**Model used:** `claude-haiku-4-5-20251001`

Haiku was chosen over Sonnet or Opus for three reasons:
1. The tasks are structured and well-constrained — JSON extraction, keyword classification, short summaries. These do not require frontier model capability.
2. Lower latency — Haiku responds faster, which matters in a chat context.
3. Lower cost — appropriate for a prototype where volume could be high.

In production, Sonnet would be appropriate for the summary stage where nuanced synthesis matters more.

---

## 8. Known Limitations

1. **No memory across sessions** — conversation history is held in memory only. Restarting the script clears all context.
2. **Keyword escalation is brittle** — "I am not angry" would still match the "angry" keyword. A production system would use the LLM for sentiment classification throughout, not just in-SOP questions.
3. **Qualification is linear** — questions are asked in fixed order regardless of what the customer has already said. A smarter system would skip questions already answered in the FAQ stage.
4. **No streaming** — responses appear all at once. For a real WhatsApp integration, streaming would improve perceived responsiveness.
5. **Single-language only** — the system prompt and SOP are in English only.
