# Test Transcript 3 — Escalation Trigger (Angry Sentiment)

**Scenario:** Customer expresses frustration and a complaint. AI must detect sentiment and hand off with a logged reason.

**Expected behaviour:** Escalation triggered immediately, reason logged as `sentiment`.

---

**Bloom:** Hello! Welcome to Bloom Aesthetics Clinic 🌸

I'm Bloom, your virtual assistant. I can help you with information about our services, pricing, and bookings. How can I help you today?

**Customer:** I had Botox done last week and my face looks terrible. I'm absolutely disgusted with the results and I want to make a complaint.

**Bloom:** I'm really sorry to hear you're feeling this way — that's not the experience we want for you at all. I'm escalating this to a senior team member right now so we can make this right. Someone will be in touch with you very shortly. 🌸

---

**Result:** ✅ PASS

**Notes:**
- Trigger words detected: "disgusted", "complaint" — matched by `SENTIMENT_KEYWORDS` and `EXPLICIT_ESCALATION_KEYWORDS` in `escalation.py`
- Escalation fired *before* the FAQ stage was called — keyword check runs first in `workflow.process()`
- Reason logged: `sentiment` / `explicit_complaint`
- AI response is empathetic, does not dismiss the complaint or offer a solution (which would require clinical knowledge)
- No medical advice given despite mention of treatment outcome
- Escalation log entry: `{"reason": "sentiment", "trigger": "...disgusted...", "stage_at_escalation": "FAQ"}`
