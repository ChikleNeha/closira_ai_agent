# Test Transcript 2 — Out-of-Scope Question

**Scenario:** Customer asks something not covered in the SOP. AI must acknowledge the gap and escalate rather than guessing.

**Expected behaviour:** `can_answer: false`, escalation triggered with reason `out_of_scope`.

---

**Bloom:** Hello! Welcome to Bloom Aesthetics Clinic 🌸

I'm Bloom, your virtual assistant. I can help you with information about our services, pricing, and bookings. How can I help you today?

**Customer:** Do you offer lip flip treatments?

**Bloom:** That's a great question, but it falls outside what I'm able to help with directly. I'm connecting you with one of our team members who will have the answer. You'll hear from us shortly — thank you for your patience! 🌸

---

**Result:** ✅ PASS

**Notes:**
- "Lip flip" is not listed in the SOP (only Botox, Fillers, and Consultations are listed)
- AI did not guess or say "yes we do lip flips" — it acknowledged the gap
- Escalation triggered cleanly with reason `out_of_scope`
- SOP gap logged: "Customer asked about lip flip treatments — not in SOP"
- `can_answer: false`, `escalate: true`, `escalate_reason: "out_of_scope"`
- Recommended follow-up: Add lip flip to SOP or train AI on expanded service list
