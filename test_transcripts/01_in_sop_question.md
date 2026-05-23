# Test Transcript 1 — In-SOP Question

**Scenario:** Customer asks about Botox pricing — a question directly answerable from the SOP.

**Expected behaviour:** AI answers accurately from SOP only, no hallucination.

---

**Bloom:** Hello! Welcome to Bloom Aesthetics Clinic 🌸

I'm Bloom, your virtual assistant. I can help you with information about our services, pricing, and bookings. How can I help you today?

**Customer:** What are your Botox prices?

**Bloom:** Our Botox treatments start from £200 per area. If you'd like to know exactly what's included or discuss which areas you're interested in, a free consultation would be a great first step — no obligation at all!

Would you like to book a consultation, or do you have any other questions? 😊

---

**Result:** ✅ PASS

**Notes:**
- Answer sourced directly from SOP ("Botox: from £200")
- No fabricated details (no mention of specific clinicians, session durations, or guarantees)
- Offered free consultation as a natural next step (present in SOP)
- `can_answer: true`, `confidence: HIGH`, `escalate: false`
