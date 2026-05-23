# Closira AI Agent

An AI-powered customer support workflow for Bloom Aesthetics Clinic, built with Python and the Anthropic Claude API. Handles customer conversations end-to-end across four stages: FAQ answering, lead qualification, escalation detection, and conversation summary.

---

## Setup and Run

### Prerequisites

- Python 3.10 or higher
- An Anthropic API key 

### Installation

```bash
git clone <repo-url>
cd closira-ai-agent

pip install -r requirements.txt
```

### Configure your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your-api-key-here` with your actual Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### Run the agent

```bash
python main.py
```

---

## How to Use

Once running, type your message and press Enter. The agent responds as Bloom, the clinic's virtual assistant.

### Available commands

| Command | What it does |
|---|---|
| `/qualify` | Start the lead qualification stage (3 structured questions) |
| `/summary` | Generate a structured session summary and exit |
| `/exit` | End the session |
| `/help` | Show available commands |

### Typical session flow

1. Start the script : Bloom greets you
2. Ask questions about the clinic (FAQ stage)
3. Type `/qualify` when ready : Bloom asks 3 qualification questions
4. Type `/summary` to generate and save the end-of-session report

---

## The Four Stages

### Stage 1 : FAQ Answering
Answers customer questions strictly from the SOP data in `sop.py`. Returns a structured JSON response with `can_answer`, `confidence`, `escalate`, and `sop_gap` fields. The AI is explicitly instructed not to answer anything outside the SOP.

### Stage 2 : Lead Qualification
Asks 3 structured questions: treatment interest, prior experience, and booking timeline. Produces a lead summary with quality classification (`hot / warm / cold`) and a recommended next action.

### Stage 3 : Escalation Detection
Escalation is triggered by:
- Out-of-scope question (model sets `escalate: true`)
- Angry/frustrated sentiment (keyword detection + model detection)
- Explicit escalation request ("speak to a manager", "talk to a human")
- Medical question (always escalated, never answered by AI)
- Pricing negotiation attempt
- More than 2 unanswered questions in a row

All escalations are logged with reason, trigger message, and stage at the time of escalation.

### Stage 4 : Conversation Summary
Generates a structured JSON summary covering:
- Customer intent
- Key details collected
- SOP gaps identified (questions the AI could not answer)
- Whether the session was escalated and why
- Lead quality assessment
- Recommended next action for the human team

---

## Project Structure

```
closira-ai-agent/
├── main.py                        # CLI entry point
├── workflow.py                    # 4-stage orchestration logic (state machine)
├── sop.py                         # SOP data — the AI's only knowledge source
├── logger.py                      # Structured JSON event logger
├── stages/
│   ├── faq.py                     # Stage 1: SOP-grounded FAQ answering
│   ├── qualification.py           # Stage 2: Lead qualification questions + summary
│   ├── escalation.py              # Stage 3: Escalation triggers and handler
│   └── summary.py                 # Stage 4: Conversation summary generator
├── test_transcripts/
│   ├── 01_in_sop_question.md      # Test: in-SOP question answered correctly
│   ├── 02_out_of_scope.md         # Test: out-of-scope question escalated
│   ├── 03_escalation_trigger.md   # Test: angry sentiment detected and escalated
│   ├── 04_lead_qualification.md   # Test: full qualification flow
│   └── 05_conversation_summary.md # Test: end-of-session summary generated
├── prompt_design.md               # Full prompt design document
├── .env.example                   # API key template
├── .gitignore
└── requirements.txt
```

---

## SOP Data

The AI operates exclusively on the SOP defined in `sop.py` for **Bloom Aesthetics Clinic**:

- **Services:** Botox (from £200), Fillers (from £250), Free Consultations
- **Hours:** Mon–Sat, 9 AM – 7 PM
- **Booking:** WhatsApp or website, 24hr cancellation required
- **Always escalate:** medical questions, complaints, pricing negotiation, > 2 unanswered questions

To use a different business, replace the `SOP_TEXT` in `sop.py`. No other changes needed.

---

## Logging

All key events are logged to `closira_session.log` in JSON format:

```json
{"timestamp": "2026-05-23T09:00:00+00:00", "event": "FAQ_RESPONSE", "detail": "can_answer=true", "confidence": "HIGH", "escalate": false}
{"timestamp": "2026-05-23T09:01:00+00:00", "event": "ESCALATION_TRIGGERED", "reason": "sentiment", "trigger": "I am disgusted..."}
```

The log file is reset at the start of each new session.

---

## Model

All API calls use `claude-haiku-4-5-20251001`  the fastest and most cost-efficient Claude model. It is sufficient for structured JSON extraction, classification, and short-form summarisation. Token usage per session is minimal (typically under 2,000 tokens total).

---

## Trade-offs and Known Limitations

1. **No persistent memory** : conversation history lives in RAM only. Restarting the script clears all context.
2. **Keyword escalation is simple** : negated phrases ("I am NOT angry") could falsely trigger escalation. A production system would use the LLM for all sentiment decisions.
3. **Qualification is fixed-order** : questions are asked in sequence regardless of what the customer has already said. A smarter system would skip already-answered questions.
4. **No streaming** : responses appear all at once. Streaming would improve perceived responsiveness in a real chat interface.
5. **English only** : the SOP and prompts are in English. Multi-language support would require prompt translation or a multilingual SOP.
6. **Follow-ups not scheduled** : the qualification summary recommends a next action but does not trigger any automated follow-up. This would require integration with a CRM or messaging platform.
